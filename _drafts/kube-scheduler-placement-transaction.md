---
layout: post
title: "kube-scheduler 只承諾 Node Placement：Filter、Score、Reserve、Permit 到 Bind 的完整決策鏈"
date: 2026-09-28 08:00:00 +0800
domain: distributed-systems
categories: distributed-systems
description: "scheduler 對 Pod 做的是可行性判斷、偏好排序與 Node 綁定承諾；CPU pinning、NUMA、NIC 與 storage locality 要到 node-local mechanism 才真正落實。從 queue、Filter、Score、Assume、Reserve、Permit 到 Bind，可以看見 Kubernetes placement 的能力邊界。"
---

[上一篇](/distributed-systems/2026/09/26/kube-controller-manager-informer-workqueue-lease.html)停在一個很具體的位置：controller 已把 desired state 推進成一個尚未綁定 Node 的 Pod。接下來如果有 5,000 台機器，scheduler 要回答的並不是「哪台最快」，而是更窄、也更難的一個問題：**在目前能觀察到的 cluster state 與 policy 下，哪一台 Node 可以合法承接這個 Pod，而且這個決定不能和下一個 scheduling decision 互相踩掉。**

對 web service 來說，`requests.cpu: 4`、`requests.memory: 8Gi` 配合 topology spread，通常已足以建立合理 placement；但對 APR、STA、MPI 或多 GPU training，Node 上「還有 32 CPU」並不代表有 32 個可預測的 physical cores，也不代表 256 GiB memory 都在同一個 NUMA node，更不代表 GPU 與 400 Gb/s RNIC 掛在同一個 PCIe root complex。若 scheduler 假設 API resource 已完整描述 hardware reality，它會做出語義正確、性能卻很差的 placement。

因此 kube-scheduler 需要的是一條有清楚 rollback 邊界的決策鏈：**Queue 決定誰先被考慮；Filter 排除不可能的 Node；Score 比較剩下候選；Assume 先在 scheduler cache 中占住資源；Reserve／Permit 讓 plugin 建立或延後額外承諾；最後 Bind 才把 Node 選擇寫回 API。** Kubernetes v1.37 的 scheduler source 仍沿著這條主幹執行，而 Workload-Aware Scheduling 又把相同概念擴到 PodGroup，但後者是另一個更高層的問題。[Scheduling Framework](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/)｜[kube-scheduler v1.37.0 source](https://github.com/kubernetes/kubernetes/blob/v1.37.0/pkg/scheduler/schedule_one.go)

<figure>
  <img src="/images/distributed-systems/2026-09-27/scheduler-pipeline.svg" alt="kube-scheduler 從 scheduling queue 經 Filter、Score、Assume、Reserve、Permit 到 Bind 的完整決策鏈" style="max-width:100%;height:auto;">
  <figcaption>圖 1｜一個 Pod 的 placement 是 scheduling cycle 與 binding cycle 串成的決策路徑。Filter／Score 產生候選與排名；Assume 先占 scheduler cache；Reserve／Permit 提供 plugin 的承諾與等待點；Bind 才把 Node 決定寫入 API。依據 <a href="https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/">Scheduling Framework</a> 與 <a href="https://github.com/kubernetes/kubernetes/blob/v1.37.0/pkg/scheduler/schedule_one.go">Kubernetes v1.37.0 schedule_one.go</a> 整理／重繪。</figcaption>
</figure>

## 先把「能不能放」和「比較想放哪裡」拆開

假設一個 APR Pod 宣告：

```yaml
resources:
  requests:
    cpu: "32"
    memory: 256Gi
nodeSelector:
  eda-class: highmem
```

如果 cluster 有 5,000 個 Node，最直接的寫法是對每一台都算一次完整 objective function，再挑最高分。但這會把 scheduler latency 與 cluster size 幾乎直接綁在一起，而且很多 Node 其實一開始就不可能承接 workload：記憶體不足、taint 不允許、volume topology 不合、node affinity 不符、port 衝突，或者 required anti-affinity 已經排除它。

Scheduling Framework 因此先用 PreFilter／Filter 解 feasibility，再用 PreScore／Score 做 preference。Filter plugin 對每個 Node 回答的是硬條件：「可不可以」；Score plugin 對可行 Node 回傳分數，scheduler 再依 plugin weight 合成總分。[Scheduling Framework](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/)

這個拆分不是程式碼潔癖，而是兩種錯誤的代價不同。memory request 256 GiB、Node 只剩 192 GiB，把它排進去代表 admission accounting 已違反；這是 feasibility error。Node A 和 Node B 都合法，只是 A 的 topology spread 較好、B 的 bin-packing 較佳，選錯只是 optimization loss。把 hard constraint 和 soft preference 混在一起，就很容易讓「分數很高」掩蓋「根本不能執行」的條件。

可以用一個假設算例看 Score 如何運作。假設兩個 plugin 都把結果正規化到 0–100：

| Node | NodeResourcesFit | NodeAffinity | 權重後總分 |
| --- | ---: | ---: | ---: |
| A | 80 | 20 | `80×2 + 20×1 = 180` |
| B | 60 | 90 | `60×2 + 90×1 = 210` |

若 `NodeResourcesFit` weight=2、`NodeAffinity` weight=1，B 勝出。這是示意計算，不是 Kubernetes 預設設定；真正 profile 由 `KubeSchedulerConfiguration` 決定，而且不同 scheduling profile 可以有不同 plugin 與 weight。[Scheduler Configuration](https://kubernetes.io/docs/reference/scheduling/config/)

scheduler 沒有一個宇宙通用的「最佳 Node」。你給它什麼 state、constraint 與 objective，它只能在那個模型裡求解。EDA 想追求 license locality、NFS path、NUMA memory；AI 想追求 GPU/NIC/NVLink topology；一般服務則可能更重視 spreading 與 availability。這些目標衝突時，policy 就是 architecture，不是 tuning 細節。

## 5,000 台 Node 不需要每次都完整 Score

大型 cluster 的下一個矛盾是：即使 Filter 可以平行執行，也沒有必要每次都把所有 Node 送進 Score。

Kubernetes 的 scheduler performance tuning 允許用 `percentageOfNodesToScore` 控制候選集合。現行文件描述的自動比例會隨 cluster 變大下降：100 台 Node 約 50%，5,000 台約 10%，並有 5% 下限；scheduler source 同時保留「至少找到 100 個 feasible nodes」的門檻。達到需要的可行節點數後，Filter 可以提早停止，再只對這批候選做 Score。[Scheduler Performance Tuning](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduler-perf-tuning/)｜[schedule_one.go v1.37.0](https://github.com/kubernetes/kubernetes/blob/v1.37.0/pkg/scheduler/schedule_one.go)

以 5,000-node cluster 的預設比例示例，目標候選大約是 500 個。這不表示只檢查 500 台就一定找到 500 台 feasible nodes；若很多 Node 被 Filter 排除，實際檢查數會更高。但一旦已取得足夠候選，後續 Score 的候選集合可以從 5,000 縮到約 500，量級上少 10 倍。

這是一個清楚的 latency-versus-optimality trade-off。若每次都檢查所有 Node，placement 有機會更接近全域最高分，但 scheduler throughput 下降；若只取較小候選集，提交尖峰時吞吐較好，但某台尚未被掃到的 Node 可能其實更理想。Kubernetes 用輪替起始 index 讓不同 scheduling cycle 不會永遠從同一批 Node 開始，降低長期偏斜；它仍沒有把「每次一定找到全域最優」當 correctness contract。[schedule_one.go](https://github.com/kubernetes/kubernetes/blob/v1.37.0/pkg/scheduler/schedule_one.go)

對 tape-out 前的大量 STA／APR submission，這個 trade-off 很現實。你可能寧願快速讓大量 job 都取得「夠好」的 placement，也不願 scheduler 花更久替每一個 job 找理論最高分 Node。相反地，若單一 distributed training job 占掉數百顆 GPU，錯一次 topology placement 的成本可能遠高於多花一些 scheduling time 做更完整搜尋。同一個 framework 可以承載兩種 policy，但不代表同一組參數適合所有 workload。

## 選出 Node 之後還不能直接 Bind

到這裡有一個容易忽略的 race。

假設 Node-7 有 64 CPU request capacity。Pod A 要 32 CPU，scheduler 選中 Node-7；如果它必須同步呼叫 API server 完成 Bind，等 informer 再把已綁定 Pod 回傳到 scheduler cache，才開始排 Pod B，correctness 很簡單，但 throughput 會被 API round trip 與 cache propagation latency 限制。

如果反過來，scheduler 一選完 Node-7 就立即開始排 Pod B，卻沒有先把 Pod A 算進 Node-7 的已用資源，Pod B 也可能看到 64 CPU available，再選同一台 Node。兩個合法 decision 因為觀察到同一份 stale snapshot 而重複承諾 capacity。

Kubernetes 的答案是 **Assume**。

v1.37 `scheduleOnePod()` 先同步跑 scheduling cycle；成功後 `prepareForBindingCycle()` 會呼叫 `assumeAndReserve()`。source comment 寫得很直接：即使 Pod 還沒有真正 Bind，scheduler cache 先假設它已在選定 Node 上執行，讓 scheduler 不必等待 binding 完成就能繼續。之後 binding cycle 才以 goroutine 非同步執行。[schedule_one.go — assumeAndReserve](https://github.com/kubernetes/kubernetes/blob/v1.37.0/pkg/scheduler/schedule_one.go)

這裡的 pattern 很接近 optimistic transaction：

```text
read snapshot
  → choose Node
  → assume resource in local state
  → reserve plugin state
  → commit binding through API
  → observe committed object later
```

它不是資料庫 transaction，因為 scheduler cache、plugin reservation 與 API object 不是同一個 atomic store；所以 failure path 必須明確。Reserve plugin 若失敗，framework 會呼叫 Unreserve 並 Forget assumed Pod；Permit 若 deny，也走同樣 rollback；PreBind 或 Bind 失敗後，`handleBindingCycleError()` 再執行 Unreserve／Forget，讓其他 Pod 因資源釋放事件重新被考慮。[Scheduling Framework — Reserve/Permit](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/)｜[schedule_one.go — binding failure](https://github.com/kubernetes/kubernetes/blob/v1.37.0/pkg/scheduler/schedule_one.go)

這個 rollback contract 不能省。最麻煩的狀態是「scheduler 以為資源占住，API 卻沒承認」或「plugin 外部資源已保留，scheduler 卻重試另一台」。前者造成 ghost capacity，後者造成 double reservation。Scheduling Framework 明確要求 Unreserve 必須 idempotent，而且不能失敗，就是因為它負責清理 speculative state。[Scheduling Framework](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/)

## Reserve 與 Permit 解的是承諾時機

Reserve 常被誤讀成「把 Node 的 CPU 真正保留起來」。它不是。

Reserve extension point 讓 plugin 在 Bind 前建立自己的 state，例如某個 scarce resource、volume 或其他 placement-dependent state；如果後面失敗，對應 Unreserve 負責清理。Permit 則可以 approve、deny 或 wait；wait 最長 timeout 由 framework 限制，v1.37 source 的上限是 15 分鐘。[Scheduling Framework](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/)｜[framework.go v1.37.0](https://github.com/kubernetes/kubernetes/blob/v1.37.0/pkg/scheduler/framework/runtime/framework.go)

這對 gang-like semantics 很關鍵，但不能延伸成「單 Pod scheduler 已自然具備完整 HPC gang scheduling」。Kubernetes v1.37 把 Workload-Aware Scheduling 推到 Beta，加入 `PodGroup` 與同批 admission／placement 的能力；但 `GenericWorkload` feature gate 預設仍停用，官方也明確把傳統逐 Pod scheduling 造成 distributed workload partial start / deadlock 當成這項功能要解的問題。[Kubernetes v1.37 Workload-Aware Scheduling](https://kubernetes.io/blog/2026/09/08/kubernetes-v1-37-advancing-workload-aware-scheduling/)｜[Scheduling Groups](https://kubernetes.io/docs/concepts/workloads/pods/scheduling-group/)

因此本篇只處理單一 placement 的 transaction boundary；PodGroup、gang scheduling、backfill 與 Slurm/LSF 的 queue semantics 留到後面的 scheduling phase 再完整比較。

## Bind 只把 Pod → Node 寫成 cluster fact

當 Bind plugin 成功時，scheduler 完成的是一個 control-plane state transition：Pod 已被指定到某個 Node。它沒有呼叫 `clone()`、沒有建立 cgroup，也沒有設定 CPU affinity。

真正的 execution 邊界在 kubelet。

kubelet 看到 `spec.nodeName` 指向自己的 Pod 後，才經 CRI 要求 runtime 建 sandbox／container；OCI runtime 再透過 namespace、mount、cgroup 等 Linux mechanism 建立 process state。這也是 scheduler 與 kernel 之間必須保留層次的原因：scheduler 做 cluster-wide placement，node agent 做 node-local realization。

考慮這個 Pod：

```yaml
resources:
  requests:
    cpu: "32"
    memory: 256Gi
  limits:
    cpu: "32"
    memory: 256Gi
```

scheduler 在 placement 時主要看 request accounting：Node allocatable 是否還容得下 32 CPU 與 256 GiB，而不是 32 顆 physical cores 是否連續或同一個 socket。Kubernetes 官方資源管理文件明確說明 scheduler 依 request 做 placement；實際 CPU／memory enforcement 則由 kubelet、runtime 與 Linux cgroups 落實。[Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)

在 cgroup v2，CPU control 最終會落到 `cpu.weight`、`cpu.max` 等 kernel interface；要取得更強的 CPU locality，還需要 CPU Manager。預設 `none` policy 允許 workload 在可用 CPU 間移動；`static` policy 才會對符合條件的 Guaranteed Pod、整數 CPU request 配置 exclusive CPUs，並透過 cpuset／runtime affinity 落實。[Linux cgroup v2](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)｜[Control CPU Management Policies on the Node](https://kubernetes.io/docs/tasks/administer-cluster/cpu-management-policies/)

<figure>
  <img src="/images/distributed-systems/2026-09-27/node-vs-numa-boundary.svg" alt="Kubernetes Pod 的 CPU memory request 經 scheduler placement、kubelet CRI 到 Linux cgroup 與 cpuset，並受 NUMA PCIe locality 制約" style="max-width:100%;height:auto;">
  <figcaption>圖 4｜Node placement 與實際執行是兩層不同承諾。scheduler 用 API-visible request／constraint 選 Node；kubelet／runtime 再把資源語義映射到 cgroup、cpuset 與 process。即使兩台 Node 都通過 Filter，NUMA、PCIe、NIC/storage path 的 locality 仍可能不同。Kubernetes 部分依據 <a href="https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/">Resource Management</a>、<a href="https://kubernetes.io/docs/tasks/administer-cluster/cpu-management-policies/">CPU Manager</a> 與 <a href="https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html">Linux cgroup v2</a>；右側 topology mapping 為作者整理。</figcaption>
</figure>

這就回答了「為什麼 32 CPU 不等於 32 個可預測 physical cores」。API 裡的 CPU request 首先是一個 scheduler accounting quantity；它能阻止 scheduler 在 allocatable 上明顯超賣，但 deterministic execution 要再依賴 CPU Manager、Topology Manager、NUMA placement、SMT policy 與實際硬體拓樸。這些 mechanism 不會因為 Score 階段選到高分 Node 就自動成立。

## Scheduler 看的是 snapshot，不是即時硬體真相

scheduler 並不是每次判斷都直接向每一台 kubelet 詢問「現在還剩多少資源」。那樣做會讓一次 placement 變成跨數千台 Node 的分散式 RPC，任何慢 Node、網路抖動或 kubelet timeout 都可能拖住 scheduling path。

scheduler 維護自己的 cache，並在 scheduling cycle 開始時把 cache 更新成可供演算法查詢的 snapshot。v1.37 `schedulingCycle()` 一開始就呼叫 `Cache.UpdateSnapshot()`，後續 PreFilter、Filter、Score 都以這個本地 view 工作。[schedule_one.go](https://github.com/kubernetes/kubernetes/blob/v1.37.0/pkg/scheduler/schedule_one.go)

代價是 snapshot 可能落後。Node-7 上一個 Pod 正在 termination，kubelet 已開始釋放 process，但 API 狀態尚未讓 scheduler cache 看見，scheduler 可能暫時低估可用資源；反過來，如果某個 external device 已失效，但 Node condition、ResourceClaim 或 plugin state 還沒更新，scheduler 也可能短暫高估那台機器的可行性。

Kubernetes 沒有試圖用同步鎖把所有 Node 變成一個原子 snapshot，而是用收斂、版本化 state 與失敗重試承受時間差。scheduler correctness 更接近四個條件：已知 hard constraint 不應故意違反；自己剛做出的 speculative placement 必須立即反映在 cache；API state 改變後，事件必須有機會喚醒受影響 workload；Bind 前後條件改變時必須能 rollback。

對 HPC platform，這也提醒一件事：不要把微秒到毫秒級 telemetry 直接當 scheduler correctness input。NIC queue depth、GPU utilization、memory bandwidth、filesystem latency 都比 scheduling cycle 變化得更快。若每個瞬時值都同步進 API 再驅動 placement，決策可能永遠追著噪音跑。較穩定的做法是把低頻、可治理的 capacity／health／topology state 送進 scheduler，高頻 telemetry 留給 observability、autoscaling 或 runtime policy；只有當 telemetry 穩定地代表結構性狀態改變，才提升成 placement constraint。

## 「資源足夠」首先是 admission accounting

再看 `requests.cpu: 32`。scheduler 判斷 Node 是否能容納 Pod 時，看的不是 `/proc/stat` 當下 CPU idle 百分比，而是已配置 request 的總和與 Node allocatable。瞬時 CPU usage 可能一秒內大幅改變，若 placement 依賴即時 utilization，Pod 在建立與真正開始執行之間的延遲就足以讓判斷過期。[Resource Management](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/)

所以 Node 明明「現在 CPU 只有 10% 使用率」，scheduler 仍可能拒絕一個 32-CPU Pod，因為既有 workload 已宣告足夠多的 CPU request。反過來，Node 當下 CPU 很忙，只要 request accounting 還有空間，Pod 仍可能被視為 feasible。這個 model 偏向 admission capacity，而不是即時 performance prediction。

對 EDA farm，這很容易踩坑。傳統 LSF queue 常把 host load、resource string、license、project quota 和 dispatch policy 混在同一個 operational model；工程師看到的是「現在這台 host 很忙，所以先不要派」。Kubernetes 預設 scheduler 更傾向依宣告 request 與穩定 constraint 做決策。如果把原本依賴 host load 的 flow 直接改成 Pod，但 request 全部寫得過小，scheduler 會合法地 overpack，最後在 kernel runqueue、memory bandwidth 或 page cache 上互相干擾。

反過來，如果每個 APR job 都把 request 寫成整台機器的 peak requirement，又會降低 utilization。假設一台 64-core host 上，APR job 平均用 20 cores、短時間 peak 32 cores：

```text
方案 A：每 job request = 20 CPU
  scheduler 可同時放 3 個 job（60/64）
  平均 utilization 較高；peak 時可能 96 runnable CPU 競爭 64 cores

方案 B：每 job request = 32 CPU
  scheduler 只放 2 個 job（64/64）
  peak contention 較少；平均可能留下不少 idle capacity
```

這是作者算例，不是官方 benchmark。它顯示 request 是 capacity contract，不會自動從應用 profile 推導出最有效率的數字。對 deadline-driven signoff，方案 B 可能更合理；對大量可平行、可容忍 variance 的 regression，方案 A 可能得到更高 cluster throughput。

## 多目標 Score 沒有免費午餐

當 hard constraint 都滿足後，真正困難的是決定哪些目標值得被換成同一個 scalar score。

一個 AI training worker 的候選 Node，可能同時存在這些取捨：Node A 的 GPU/NIC locality 最好但留下碎片；Node B 的 bin packing 最好但 GPU 到 RNIC 跨 PCIe switch；Node C topology 普通但位於同一 rack；Node D 離 checkpoint storage 路徑較近。只要最後仍是一組加權分數，所有目標都要被壓成「一分值多少」。

weight 代表 operator policy，不是物理定律。`NodeResourcesFit` weight 變大，可能讓 cluster 更緊密 packing，也可能加劇熱點。某些條件則根本不該被 score 補償：需要 RDMA 的 workload 若沒有可用 RNIC，通常是 Filter 問題，不應因 CPU 很空就得到高分抵消。更麻煩的是某些 topology 只在多 Pod 一起看時才有意義；單 Pod 的局部最高分不一定能組成整個 job 的全域好 placement。

這正是 v1.37 Workload-Aware Scheduling 的背景之一。PodGroup／gang scheduling要處理的，是「多個 Pod 必須一起成立」的 workload semantics，而不是再替單 Pod 多加幾個 Score plugin。[Kubernetes v1.37 Workload-Aware Scheduling](https://kubernetes.io/blog/2026/09/08/kubernetes-v1-37-advancing-workload-aware-scheduling/) v1.37 queue source也已把 scheduling entity 抽象成 Pod 或 PodGroup；但 feature maturity 與 production adoption 必須分開看，不能因 API 出現就假設它已取代 Slurm 的 gang/backfill 生態。[scheduling_queue.go v1.37.0](https://github.com/kubernetes/kubernetes/blob/v1.37.0/pkg/scheduler/backend/queue/scheduling_queue.go)

## 一條 APR placement path：哪些承諾在哪一層成立

把抽象收斂成完整路徑。假設 APR workload 需要 32 CPU、256 GiB memory、local NVMe scratch，並要求 `eda-highmem` pool。

第一層，API server 接受 Job/Pod intent；controller 建出 pending Pod。第二層，scheduler queue 讓它進 active path。第三層，Filter 檢查 pool label、resource request、taint/toleration、volume 等硬條件。第四層，Score 在可行 Node 中依 profile 排序。第五層，Assume 先把 32 CPU / 256 GiB 記入 scheduler cache，Reserve／Permit 完成需要的 plugin state，Bind 把 Pod 指到 Node-7。

到這裡，Kubernetes 只建立了「Node-7 承接這個 Pod」的 cluster fact。

第六層，Node-7 kubelet 觀察到 Pod 後才開始 image、volume、network、CRI runtime 流程。第七層，runtime／kernel 建 cgroup，CPU limit 可能落到 `cpu.max`，CPU request 影響 weight；若 node 啟用 CPU Manager static 且 Pod 滿足 Guaranteed + integer CPU 條件，才有機會得到 exclusive cpuset。第八層，即使 CPU 已 pin，同一個 cpuset 對應哪個 NUMA node、memory 是否 local、NVMe 是否在同 socket、IRQ 與 storage queue 是否互相競爭，仍是下一層 topology／kernel mechanism。

這條 path 能幫我們判斷 bug 應該在哪一層找：

- Pod 一直 Pending、`0/200 nodes are available`：先查 scheduler Filter diagnosis，不是 Linux CPU utilization。
- Pod 已 Bound 但 ContainerCreating 很久：scheduler 已完成，查 kubelet、image、CSI/CNI/runtime。
- Pod Running 但 APR wall time 比 bare metal 慢很多：查 cgroup throttling、CPU affinity、NUMA、page cache、scratch I/O；「選到 highmem node」不是性能證明。
- 分散式 job 只有部分 rank Running、其餘 Pending：問題可能在 gang semantics，不是單 Pod Score。

可診斷的 HPC platform 最後要能把 `Pod UID → scheduling attempt → selected Node → kubelet realization → cgroup/cpuset → NUMA/device/storage path` 串起來。只看 wall time，無法知道慢在 placement、node realization 還是 data path；只看 scheduler event，也無法證明 kernel 執行符合性能意圖。

## Queue 不能靠無條件重試撐 correctness

v1.37 scheduling queue 不只有一個 FIFO。source 明確維護 `activeQ`、`backoffQ` 與 `unschedulableEntities`：正在被考慮的 entity 在 activeQ；暫時退避的放 backoffQ；已判定目前不可排的留在 unschedulable set。預設 initial backoff 1 秒、max backoff 10 秒；不可排 entity 最長停留預設 5 分鐘，之後會重新被移動。[scheduling_queue.go v1.37.0](https://github.com/kubernetes/kubernetes/blob/v1.37.0/pkg/scheduler/backend/queue/scheduling_queue.go)


<figure>
  <img src="/images/distributed-systems/2026-09-27/scheduler-queue-state.svg" alt="kube-scheduler activeQ、unschedulable 與 backoffQ 的狀態轉移" style="max-width:100%;height:auto;">
  <figcaption>圖 2｜Scheduling Queue 不是單純 FIFO。Filter／Permit 失敗後，entity 可能進入 unschedulable 或 backoff；只有相關 cluster event、QueueingHint 或 retry timer 改變條件時才值得重新進 activeQ。v1.37 queue 也能在 Workload-Aware Scheduling 啟用時承載 PodGroup。依據 <a href="https://github.com/kubernetes/kubernetes/blob/v1.37.0/pkg/scheduler/backend/queue/scheduling_queue.go">Kubernetes v1.37.0 scheduling queue source</a> 整理／重繪。</figcaption>
</figure>

為什麼不能每秒把所有 unschedulable Pods 全部重跑？假設 10,000 個 Pod 同時因「GPU 不足」失敗，如果每秒無條件再試一次，一分鐘就是 600,000 次 scheduling attempts。這是透明算例，不是 Kubernetes benchmark；它只說明無效 retry 本身就可能和真正可排 workload 競爭 scheduler CPU。

因此 scheduler 需要根據 cluster event 與 plugin queueing hint 判斷哪些 workload 值得被喚醒。Node 新增、assigned Pod 刪除、PVC／resource claim 狀態改變，真正受事件影響的 entity 才應推回 active/backoff path。hint 太窄，可能漏掉已變得可排的 Pod；太寬，又退回 retry storm。最大 unschedulable duration提供保底進展，backoff 抑制失敗條件的快速重複。

failure recovery 因而形成閉環：

```text
Filter 無可行 Node
  → unschedulable
  → relevant cluster event / timeout
  → active or backoff queue
  → 重新 Filter / Score

Assume / Reserve 成功但 Bind 失敗
  → Unreserve
  → Forget assumed Pod
  → backoff
  → 下一次重新做完整 placement decision
```

scheduler 不需要保證每次 attempt 都成功；它必須保證失敗後 speculative resource 不會永遠留在 cache，也不把仍可能成功的 workload 永遠遺失。

## 什麼情況下不應讓 Kubernetes scheduler 接管 placement

有了 plugin framework，很容易產生誘惑：任何特殊需求都寫一個 scheduler plugin，最後把 LSF/Slurm 全部換掉。這個推論太快。

若 workload 主要是獨立 Pod、resource contract 可由 API 清楚表達、失敗可重試，而且平台重視統一 API、policy、device allocation 與 multi-tenant governance，Kubernetes scheduler 很有吸引力。GPU inference、一般 batch、部分 embarrassingly parallel regression 都可能符合。

但若 workload 依賴成熟 backfill、複雜 license token、跨數千 rank 的 coordinated start、長時間 reservation、特殊拓樸或 site-specific fair-share，現有 Slurm/LSF policy 可能已把很多 operational knowledge 編碼進 scheduler。此時較合理的架構可能是 Kubernetes 做 submission / policy control plane，執行仍交給 LSF/Slurm；或者只遷移 resource semantics 能被 Kubernetes 精確表達的 workload。

deterministic performance 也需要算成本。Kubernetes 可以透過 CPU Manager、Topology Manager、DRA、SR-IOV 等機制逐步把更多硬體 constraint 暴露出來，但每增加一個維度，就增加 state、plugin coupling、failure mode 與運維成本。若 dedicated bare-metal partition 已能用簡單規則提供穩定 wall time，為了統一平台再疊多層 abstraction 未必划算。

真正的判斷標準是：**決定 workload 成功與完成時間的 constraint，有多少能被 scheduler model 完整表達、驗證並在失敗時恢復。**模型之外的東西，最後都會以 performance variance、人工例外或 hidden scheduler rule 的形式回來。

## Placement 之後，Node 上才開始真正執行

到這裡，Pod 已從 abstract desired state 走到一個具體 Node：Queue 管等待，Filter 管 feasibility，Score 管 preference，Assume 避免非同步 Bind 造成重複資源承諾，Reserve／Permit 管 plugin-level commitment，Bind 把 Node assignment 寫回 Kubernetes API。

但 Linux 上甚至可能還沒有新的 workload process。

真正把這個承諾變成可執行狀態的是 kubelet：它要觀察被指派給自己的 Pod，和 container runtime 對話，準備 volume、network、cgroup、namespace，最後才讓 process 出現。當 kubelet crash、runtime 卡住、image 拉不下來、volume mount 失敗，scheduler 的 placement 已經成功，workload 卻仍然無法 Running。

下一篇會沿著這條界線進入 **kubelet：cluster-level declarative intent 如何被翻譯成 node-local process state**。到那裡，`Pod.spec.nodeName` 才會真正落到 CRI、OCI runtime 與 Linux kernel。

## References

1. [Kubernetes Scheduling Framework](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/) — scheduling / binding cycles 與 extension points。
2. [Kubernetes v1.37.0 `schedule_one.go`](https://github.com/kubernetes/kubernetes/blob/v1.37.0/pkg/scheduler/schedule_one.go) — ScheduleOne、Filter/Score、Assume、Reserve、Permit、Bind 與 rollback path。
3. [Kubernetes v1.37.0 scheduling queue source](https://github.com/kubernetes/kubernetes/blob/v1.37.0/pkg/scheduler/backend/queue/scheduling_queue.go) — activeQ、backoffQ、unschedulable entities 與 backoff defaults。
4. [Kubernetes v1.37.0 Scheduling Framework runtime](https://github.com/kubernetes/kubernetes/blob/v1.37.0/pkg/scheduler/framework/runtime/framework.go) — plugin extension points 與 Permit timeout 上限。
5. [Scheduler Configuration](https://kubernetes.io/docs/reference/scheduling/config/) — profiles、plugins 與 Score weight。
6. [Scheduler Performance Tuning](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduler-perf-tuning/) — `percentageOfNodesToScore` 與 scheduling latency / placement quality trade-off。
7. [Resource Management for Pods and Containers](https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/) — requests、limits 與 scheduler / kubelet resource semantics。
8. [Control CPU Management Policies on the Node](https://kubernetes.io/docs/tasks/administer-cluster/cpu-management-policies/) — CPU Manager none/static policy 與 exclusive CPU 條件。
9. [Linux cgroup v2 documentation](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html) — `cpu.weight`、`cpu.max` 等 kernel resource-control interface。
10. [Kubernetes v1.37: Advancing Workload-Aware Scheduling](https://kubernetes.io/blog/2026/09/08/kubernetes-v1-37-advancing-workload-aware-scheduling/) — PodGroup / gang scheduling Beta 與傳統逐 Pod scheduling 的限制。
11. [Scheduling Groups](https://kubernetes.io/docs/concepts/workloads/pods/scheduling-group/) — `PodGroup` 與 gang scheduling policy。
12. [Node-resource bin packing](https://kubernetes.io/docs/concepts/scheduling-eviction/resource-bin-packing/) — `NodeResourcesFit` scoring strategy 與 resource weights。


## 補充：Node 選擇的「正確」與「快」必須分開量

評估 scheduler 時，只有平均 scheduling latency 不夠。至少要把三類量分開：第一是 queueing latency，也就是 workload 從進入 queue 到真正開始 scheduling 的時間；第二是一次 scheduling attempt 的演算法成本，包括 Filter、Score 與 plugin 呼叫；第三是 placement quality，例如 fragmentation、跨 NUMA／rack traffic、後續 preemption 或因 locality 不佳造成的 wall-time 損失。

這三者可能彼此交換。把候選 Node 比例降得很低，一次 scheduling 會更快，卻可能讓資源碎片逐步累積；過度追求 bin packing，又可能讓少數 Node 熱點化，增加 memory bandwidth、NIC 與 storage queue 競爭。增加 topology-aware plugin 能改善 placement，但也會增加 snapshot state 與計算成本。對 HPC/EDA，比較 scheduler policy 時應同時看「提交到開始執行」與「開始執行到工作完成」，因為前者變快但後者因干擾變慢，整體 throughput 未必改善。

這也解釋為什麼 scheduler throughput 不是最終北極星。真正昂貴的是 scarce expert-hour、license-hour、GPU-hour 與 tape-out deadline。若多花一些 scheduling computation 能避免數小時的跨 NUMA 或 network locality 損失，值得；若 workload 本身只有幾秒，為每個 Pod 做複雜全域最佳化就可能得不償失。平台必須把成本放回 workload economics，而不是只追 kube-scheduler 自身的 benchmark。


## 再往下一層：scheduler 無法替你消除 queueing 與 hardware contention

把 placement 視為一次「Pod 找 Node」很容易忽略兩種完全不同的排隊。第一種在 control plane：Pod 還沒得到 Node，等待的是 scheduler queue、可行資源、priority 或 preemption。第二種在 Node 內：Pod 已經 Running，process 卻在 Linux runqueue、memory controller、block queue、NIC queue 或 shared filesystem 上排隊。兩者在使用者眼中都可能只是「job 變慢」，但修法完全不同。

例如一個 32-CPU APR Pod 已成功 Bind 到 64-core Node，而且沒有其他 Pod 的 declared request 讓 Node 超載。若 CPU Manager 使用預設 none policy，32 CPU 仍不是 32 個 exclusive cores；Linux scheduler 會在允許的 CPU 上排 runnable threads。若同機其他 workload 也大量 runnable，cgroup weight 決定的是競爭時的相對份額，不是每一個 thread 永遠獨占 core。若又跨兩個 NUMA node 配 memory，CPU placement 看起來正確，memory access 仍可能走 remote interconnect。此時增加 kube-scheduler Score plugin 並不一定能修好，因為真正的 queue 已經在 kernel。

反過來，若 workload 長時間卡在 Pending，先調 `cpu.max` 或 IRQ affinity 也沒有意義。Filter diagnosis 若顯示「insufficient memory」或 node affinity 不滿足，問題還停留在 cluster placement；要處理的是 request、capacity、label、taint、volume topology 或 device availability。這種分層診斷是大型平台最需要保留的能力：同一個「慢」字，必須能映射到不同 queue 與不同 owner。

對 AI training 更明顯。四個 worker 都 Running 不代表 collective path 已最佳化。scheduler 可能只知道每個 Pod 要 8 GPU；真正的 NCCL ring、GPU-to-NIC PCIe path、跨 rack oversubscription、RoCE congestion、IRQ affinity 要在更低層才能證明。若 topology 沒有被 API/DRA/plugin 暴露，scheduler 沒有資訊可以最佳化。若資訊被暴露，但單 Pod Score 無法表達「四個 worker 必須共同落在一組拓樸」，就需要 PodGroup 或更高層的 workload placement，而不是在單 Pod plugin 裡偷偷保存全域狀態。

同一原則也適用 storage。APR Pod 的 PVC 若只代表「可掛載的 shared filesystem」，Filter 能回答 volume topology 是否合法，卻無法保證這個 job 開始後不會遇到 metadata storm。NFS bandwidth 即使足夠，數十萬個小檔的 lookup/create/unlink 仍可能把 metadata service 壓垮。這種 bottleneck 要靠 storage architecture、local scratch、artifact staging 或 I/O-aware admission 解，而不是假設 Node placement 一次就把整條 data path 最佳化。

因此 scheduler 的好設計反而要求它承認邊界。它應該把能穩定描述、能驗證、能在失敗後 rollback 的 placement state 納入決策；對於比 scheduling state 變化更快、或只能在 execution time 才知道的訊號，應交給 node-local policy、runtime feedback 或下一層 control loop。把所有東西都拉進 scheduler，最後通常得到一個狀態巨大、耦合極高、每個 failure 都很難重現的中央最佳化器。

## EDA 的 license constraint 為什麼也不能只塞進 Node Score

EDA 還有一個 Kubernetes 原生資源模型沒有直接覆蓋的 scarce resource：commercial tool license。假設有 200 台 high-memory host，但 Innovus token 只剩 8 個。單看 Node resource，可能有 100 個 APR Pod 都能通過 Filter；若全部先 Bind，再讓 application 啟動後向 license server 排隊，就會出現大量 Running Pod 實際上只是在等待 token，占住 CPU、memory 與 scratch。

可以把 license availability 做成 scheduler plugin，但這立即產生 distributed-state 問題。license token 不屬於某一個 Node；Reserve 成功到 application 真正 checkout token 之間有時間窗；Bind 失敗要歸還 reservation；controller crash 或 network partition 不能留下永久 token leak。若 license server 本身仍是 authoritative owner，scheduler plugin 就必須和它建立可回滾的 reservation contract，而不是只把「目前剩 8 個」做成一個 Score。

另一種設計是把 license admission 放在 scheduler 之前，例如由 queue/admission controller 只放 8 個 APR workload 進入可排狀態，再讓 kube-scheduler 專注 Node placement。這比較接近 Kueue 或傳統 batch scheduler 的 admission-before-placement 思維。哪種方式比較好，取決於 license reservation 能否可靠地被建模，以及是否希望沒有 token 的 workload 占據 Node resource。

這個例子說明 scheduler plugin extension point 很強，但 extension point 不是架構答案。每一個 scarce resource 都要先問 ownership、commit point、rollback、failure detection；只有這些 contract 清楚，才知道它應該落在 Filter、Reserve、Permit、外部 admission，還是根本留在 LSF/Slurm。否則只是把原本 hidden shell script 的 race condition 搬進 scheduler process。


## 一個容易被忽略的驗證點：placement policy 也是 run environment

對可重現性要求高的 EDA／HPC，scheduler configuration 本身應被視為 execution environment 的一部分。若同一批長時間 run 在不同日期由不同 scheduling profile、不同 Score weight、不同 Node label 或不同 topology policy 排入 cluster，後續 wall time 變化不能只歸因於 tool binary、RTL 或 SDC。placement policy 已經改變了 CPU／NUMA／device／storage path 的候選集合。

因此 production platform 至少應能回查：這次 scheduling attempt 使用哪個 profile、主要 Filter rejection 原因、最後選中的 Node、當時的 resource class／topology label，以及 node-local CPU/NUMA policy。這不是要把所有 scheduler internal state永久保存，而是保留足以重建「為什麼這個 workload 被放在這裡」的 evidence。對 regression、tape-out signoff 或昂貴 AI training，沒有這條 evidence chain，就很難區分 workload regression 與 infrastructure placement regression。
