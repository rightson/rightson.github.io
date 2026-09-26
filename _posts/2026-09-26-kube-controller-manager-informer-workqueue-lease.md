---
layout: post
title: "kube-controller-manager 把事件洪流壓成可重算的 Key：Shared Informer、Workqueue 與 Lease 如何維持控制面收斂"
date: 2026-09-26 08:01:20 +0800
domain: distributed-systems
categories: distributed-systems
description: "幾十個 controller 若各自掃描 API、同步處理每個 event，再靠單一 active replica 維持一致，控制面很快會被自己的觀察成本拖垮。kube-controller-manager 透過 shared informer、local cache、workqueue 與 Lease，把全域狀態變成可重算、可合併、可接手的局部工作。"
---

[上一篇](/distributed-systems/2026/09/25/etcd-kubernetes-mvcc-watch-quorum.html)停在一個很自然的問題：etcd 已經把 cluster mutation 排成可排序、可追蹤的歷史，但「歷史存在」還不等於「有人能有效把它轉成動作」。

如果每個 controller 都自己對 API server 做高頻 LIST、每收到一個 watch event 就同步執行完整修復、而且把 event queue 當成不能遺失的工作紀錄，那麼 object 數量與 controller 數量一上去，control plane 會先被自己的觀察成本和重試風暴拖垮。Kubernetes 的做法是把問題拆開：**觀察共享、事件只負責提示、工作單位縮成 object key、正確性仍由最新 state 重算；HA 則另外用 Lease 決定哪一個 controller-manager replica 目前負責執行。**

這幾個機制合在一起，才形成 kube-controller-manager 真正有價值的工程形狀。

官方把 kube-controller-manager 定義成「內含 Kubernetes 核心 control loops 的 daemon」。邏輯上，每個 controller 是獨立控制迴路；實作上，為了降低部署與管理複雜度，許多 built-in controllers 被打包進同一個 binary/process。[kube-controller-manager reference](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-controller-manager/) 現行 v1.37 文件列出的 controller 已經包含 Deployment、ReplicaSet、StatefulSet、Job、namespace、HPA、persistent volume、resource claim、EndpointSlice 等數十種；這些 controller 並不共享同一套業務邏輯，只共享一部分 observation、client 與 lifecycle infrastructure。

<figure>
  <img src="/images/distributed-systems/2026-09-26/kcm-control-loop-fanout.svg" alt="kube-controller-manager 內多個 controller 共用 API observation infrastructure，再各自維持不同資源的 desired state" style="max-width:100%;height:auto;">
  <figcaption>圖 1｜kube-controller-manager 把許多獨立 control loop 放進同一個 process，並透過 shared informer infrastructure 共用部分 API observation。依據 <a href="https://kubernetes.io/docs/reference/command-line-tools-reference/kube-controller-manager/">kube-controller-manager reference</a> 與 <a href="https://github.com/kubernetes/kubernetes/blob/master/cmd/kube-controller-manager/app/controllermanager.go">controllermanager.go</a> 整理／重繪。</figcaption>
</figure>

## 有了 Watch，為什麼還需要 Shared Informer

先從最直接的成本開始。

假設 cluster 有 200,000 個 Pod，平均每個序列化後約 3 KiB；有 10 個 controller 都需要知道 Pod 狀態。如果每個 controller 都自己建立一份完整 local snapshot，光原始 payload 的量級就是：

<pre><code>200,000 × 3 KiB × 10
≈ 5.7 GiB
</code></pre>

這還沒算 Go object、map、index、GC metadata，也沒有算第一次 LIST 對 API server 的 decode、network 與 etcd/read cache 壓力。這個算例不是 Kubernetes 官方 benchmark，只是把「重複 observation」的量級攤開。

Kubernetes client-go 的 SharedInformer 正是為了把這種重複成本合併。它維護一份 local cache，client 從 cache 讀物件，並對 cache update 註冊 handler。原始碼把語義寫得很精確：SharedInformer 的 local cache 對 authoritative state 是 **eventually consistent**；對同一個 object，cache 中看到的狀態會保持順序，但中間某些狀態可以完全不出現；不同 object 之間則沒有全域排序保證。[SharedInformer source](https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/client-go/tools/cache/shared_informer.go)

這句話決定了 controller 的設計方式。

如果一個 Pod 在極短時間內從 revision A → B → C，而 informer 只讓某個 consumer 實際看到 A 與 C，controller 仍然必須正確。因為 controller 的責任不是逐條重播 B 發生過什麼，而是拿「現在的 C」重新判斷還需要做什麼。

kube-controller-manager 自己也把這個共享層做得很具體。現行 source 的 <code>CreateControllerContext()</code> 會建立名為 <code>shared-informers</code> 的 client，再建立 SharedInformerFactory；同一段程式還對 cache object 做 transform，把 <code>managedFields</code> 清掉來降低 memory footprint。[kube-controller-manager source](https://github.com/kubernetes/kubernetes/blob/master/cmd/kube-controller-manager/app/controllermanager.go)

這個小細節很值得看。當 object 數量只有幾百時，省掉一段 metadata 沒什麼感覺；當同一 process 的 informer cache 長期持有幾十萬個 object，控制面是否能活著，往往就是被這些「每個 object 多幾百 bytes」的成本決定。

<figure>
  <img src="/images/distributed-systems/2026-09-26/informer-cache-pipeline.svg" alt="API server 經 List Watch Reflector 進入 local store，再由 event handler 將 object key 推入 workqueue" style="max-width:100%;height:auto;">
  <figcaption>圖 2｜Shared Informer 把 API observation 與 controller work 分離：Reflector 維持 LIST/WATCH，local Store/Indexer 保存近期狀態，handler 只把需要處理的 key 交給後續 workqueue。依據 <a href="https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/client-go/tools/cache/shared_informer.go">client-go SharedInformer</a> 與 Kubernetes 2026 年的 <a href="https://kubernetes.io/blog/2026/07/29/controller-runtime-cache-explained/">controller-runtime cache 解說</a> 整理／重繪。</figcaption>
</figure>

## Event 不適合直接變成工作，因為 event rate 可以比修復速度快很多

有了 local cache，下一個問題才浮出來：event 到底應該代表什麼？

假設 Deployment controller 正在處理 <code>default/web</code>，一次 reconcile 需要 200 ms。這 200 ms 裡，Pod status、ReplicaSet status、owner reference 等相關物件可能連續產生數十個 update。如果每個 update 都變成一個獨立「必須執行一次」的 task，queue growth 很快就會和 state change rate 綁死。

Kubernetes workqueue 採取不同語義：queue 裡通常放的是 key，例如：

<pre><code>default/web
kube-system/coredns
project-a/apr-run-1731
</code></pre>

key 的含義是「這個 object 值得重新檢查」，不是「請重播某一條 event」。

client-go workqueue 的 source 有兩個很重要的 set：<code>dirty</code> 與 <code>processing</code>。item 被 <code>Get()</code> 取出後進入 processing；若處理期間同一 key 又被 <code>Add()</code>，它會再次被標成 dirty；等 worker <code>Done()</code> 時，如果 dirty 仍存在，key 才重新進 queue。[client-go workqueue source](https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/client-go/util/workqueue/queue.go)

因此，假設同一 object 在一次 200 ms reconcile 期間收到 100 個 update，queue 不必保存 100 份事件紀錄。只要知道「處理完之後還要再看一次」即可。

這不是單純的效能技巧，而是 correctness model 的延伸：

<pre><code>Event:
  "something may have changed"

Queue key:
  "re-evaluate this object"

Reconcile:
  read latest cached / authoritative state
  compute required delta
  perform bounded action
</code></pre>

只要 reconcile 是 level-triggered、idempotent，而且真正的 intent/status 保存在 API state，event coalescing 就不會把 correctness 一起丟掉。

反過來，如果你需要「每一筆 event 都必須恰好處理一次」，那就已經是在做 durable event processing，應該使用具有 durable log / offset / acknowledgement 語義的系統；不能把 Kubernetes informer handler 當 Kafka consumer 來想。

<figure>
  <img src="/images/distributed-systems/2026-09-26/workqueue-dirty-processing.svg" alt="client-go workqueue 透過 dirty 與 processing 集合合併同一 key 的大量重複事件" style="max-width:100%;height:auto;">
  <figcaption>圖 3｜workqueue 用 dirty / processing 狀態把同一 key 的重複 event 合併成「至少再 reconcile 一次」。這是 state-based controller 能承受 event burst 的關鍵。依據 <a href="https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/client-go/util/workqueue/queue.go">client-go workqueue source</a> 重繪。</figcaption>
</figure>

## Local cache 的代價是：你必須接受「讀到稍舊的世界」

Shared Informer 降低 API 壓力，也帶來一個不能忽略的 trade-off：cache 不是 authoritative storage。

如果 controller 從 lister 讀到 Pod 還存在，實際 API state 可能已經往前走；如果 controller 同時根據兩種 resource 做判斷，也不能假設兩份 local cache 來自同一個 etcd revision。SharedInformer 的 contract 明確只保證對單一 object 的狀態順序，不提供不同 object 間的全域一致 snapshot。

這就是為什麼 Kubernetes controller 常把 cache read 用於「找出下一步可能需要做什麼」，而在 mutation 時再依賴 API server 的 resourceVersion / conflict semantics 阻止 stale write。

可以把它理解成兩層：

<pre><code>local cache:
  cheap, scalable, eventually consistent
  適合 observation / candidate selection

API mutation:
  authoritative serialization boundary
  適合 commit state transition
</code></pre>

前兩篇談到的 kube-apiserver 與 etcd，在這裡重新接回來。Informer 並沒有取代它們；它只是把「每個 controller 都直接讀 authoritative store」轉成「大多數 read 在 local cache 完成，必要 mutation 再回 authoritative boundary」。

對大型 AI/HPC control plane 來說，這個差異直接影響 API 設計。如果每一張 GPU 的 temperature、NIC queue depth、RDMA counter、每秒 I/O bytes 都被做成高頻 Kubernetes object update，controller-manager 的 shared cache 也救不了你。這些 high-rate telemetry 適合留在 metrics / streaming system；Kubernetes API 應該保存較低頻、需要被協調與承諾的 state，例如 device allocation、health condition、admission result 或 workload intent。

control plane 並不是資料越多越好。要能重建決策的 state 放進來；純觀測 telemetry 留在更適合高吞吐的 data path。

## 多個 Controller 放在同一個 process，不代表它們變成一個大 state machine

kube-controller-manager 目前把數十個 built-in controllers 放進同一個 daemon，但 Deployment、ReplicaSet、namespace、Job、HPA、PV binder 等 controller 的 ownership 仍然不同。[kube-controller-manager reference](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-controller-manager/) 的 <code>--controllers</code> flag 甚至允許個別啟停 controller，預設 <code>*</code> 啟用所有 on-by-default controllers。

這個架構有一個重要好處：**複雜流程不需要一個 controller 同時理解所有狀態。**

例如使用者更新 Deployment：

<pre><code>Deployment spec
   ↓
Deployment controller
   ↓
ReplicaSet desired state
   ↓
ReplicaSet controller
   ↓
Pod objects
   ↓
Scheduler（下一篇）
   ↓
Pod.spec.nodeName
   ↓
kubelet
</code></pre>

每一層都只處理自己擁有的 state transition。Deployment controller 不需要知道 Linux cgroup；ReplicaSet controller 不需要知道哪顆 CPU 空閒；scheduler 不負責確保 replica 數量；kubelet 也不決定 Deployment rollout strategy。

這種分工看起來繞路，卻讓 failure localization 變得可行。某個 controller crash，其他 loop 可以繼續；某個 transition 暫時失敗，object state 仍保留，下一次 reconcile 能重新算。

但把很多 controllers 放在同一 process 也有 blast radius。process crash 會讓同一個 kube-controller-manager replica 裡的 controllers 一起停；shared informer memory pressure 也會是 process-wide 問題。Kubernetes 用 HA replica + leader election 來補 process availability，並沒有因此把所有 controller 變成獨立 microservice。

這是一個很務實的 trade-off：邏輯上解耦，營運上合併。

## HA 需要 Leader Election，但 Lease 只解決「誰應該工作」

如果 kube-controller-manager 只有一份，process 或 node 掛掉時所有 built-in control loops 都一起停止。生產 cluster 通常會跑多個 control-plane instance，因此需要從多個 kube-controller-manager replica 中選出 active leader。

現行 kube-controller-manager 預設開啟 <code>--leader-elect</code>；預設 resource lock 是 <code>leases</code>，LeaseDuration 15 秒、RenewDeadline 10 秒、RetryPeriod 2 秒。[kube-controller-manager reference](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-controller-manager/) [Lease documentation](https://kubernetes.io/docs/concepts/architecture/leases/)

典型路徑可以簡化成：

<pre><code>replica A acquires Lease
        ↓
A starts controller loops
        ↓
A periodically renews Lease
        ↓
A fails / cannot renew
        ↓
renew deadline exceeded
        ↓
other replicas observe expired leadership
        ↓
one replica wins update conflict
        ↓
new leader starts loops
</code></pre>

到了 Kubernetes 1.37，Coordinated Leader Election 已是 Beta、預設仍停用；啟用後 kube-controller-manager 與 kube-scheduler 可使用 LeaseCandidate + Lease，並以 deterministic policy 處理版本升級期間的 leader 選擇。[Coordinated Leader Election](https://kubernetes.io/docs/concepts/cluster-administration/coordinated-leader-election/)

這裡最容易被高估的是「leader」二字。

client-go leader election source 的 package comment 直接提醒：這個 implementation **不保證只有一個 client 在現實世界中同時 acting as leader，也就是不提供 fencing**。[client-go leader election source](https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/client-go/tools/leaderelection/leaderelection.go)

原因並不神祕。Lease 能決定誰目前有權繼續扮演 leader，但舊 leader 曾經啟動的 external side effect 不會因 Lease ownership 改變就自動停止。

<figure>
  <img src="/images/distributed-systems/2026-09-26/lease-failover-no-fencing.svg" alt="kube-controller-manager leader lease failover 與 external side effect 未被自動 fencing 的界線" style="max-width:100%;height:auto;">
  <figcaption>圖 4｜Lease 解決 active controller-manager 的協調與 failover；它不會自動 fence 已經送往外部系統的 side effect。圖中的 15s / 10s / 2s 是 kube-controller-manager 現行預設值。依據 <a href="https://kubernetes.io/docs/reference/command-line-tools-reference/kube-controller-manager/">kube-controller-manager flags</a>、<a href="https://kubernetes.io/docs/concepts/architecture/leases/">Lease docs</a> 與 <a href="https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/client-go/tools/leaderelection/leaderelection.go">client-go leader election source</a> 整理／重繪。</figcaption>
</figure>

## 一個 API latency spike，會把 Leader Election 的 trade-off 全部暴露出來

假設 controller-manager leader 本身沒有 crash，但 API server 因 etcd fsync latency、network congestion 或 overload，讓 Lease renewal 在 10 秒 RenewDeadline 內一直失敗。

acting leader 會放棄 leadership。其他 replica 則依 Lease 狀態嘗試接手。把 LeaseDuration 設得更短，故障接手可以更快，但暫時 API latency spike 也更容易造成 leader churn；設得更長，false failover 下降，真正故障後的 takeover 也會更慢。

client-go source 甚至明確提醒，大型 cluster 若 API latency SLA 比較寬鬆，就應把這點納入 RetryPeriod / LeaseDuration 調校，並監控 leader transition rate。

這裡可以看到 control-plane latency 如何一路往上傳：

<pre><code>etcd / network latency
      ↓
API mutation latency
      ↓
Lease renew latency
      ↓
leader stability
      ↓
controller reconciliation continuity
      ↓
Pod / volume / endpoint / job state convergence
</code></pre>

因此，前一篇談 etcd WAL 與 quorum 並不是底層背景知識而已。它會直接改變 controller-manager 的 availability。

## EDA/HPC 平台最危險的誤用：把 Lease 當成外部 Job 的 exactly-once 保證

把同一個 pattern 放到 IC design platform 會更清楚。

假設我們定義一個 <code>AprRun</code> object：

<pre><code>spec:
  backend: lsf
  tool: innovus
  cpu: 32
  memory: 256Gi
status:
  backendJobId: "..."
  phase: Running
</code></pre>

自訂 controller 看到新的 <code>AprRun</code>，準備向 LSF submit 一個 APR job。此時 controller replica A 持有 Lease。

可能發生下面這條 failure path：

<pre><code>A: submit job to LSF
        ↓
LSF accepted job
        ↓
A loses API connectivity before status write
        ↓
A cannot renew Lease
        ↓
B becomes leader
        ↓
B sees AprRun still has no backendJobId
        ↓
B submits again
</code></pre>

如果 external submit 沒有 idempotency key，現在有兩個 Innovus job，同時吃 license、CPU、NFS scratch，甚至都可能往同一 output path 寫檔。

Lease 沒有做錯任何事。它只保證 B 在符合 election protocol 後可以開始工作，並沒有證明 A 先前送出去的 LSF job 已經被取消。

這種 workload 的 controller 至少需要另一層 external ownership contract。例如把 <code>AprRun.metadata.uid</code> 映射成 deterministic backend key：

<pre><code>externalKey =
  "apr-" + AprRun.metadata.uid
</code></pre>

submit 前先查 backend 是否已存在同 key job；或由一個具 conditional create / compare-and-set 能力的 execution gateway 原子登記 ownership，再送 LSF。即使 controller crash、leader failover、watch event 重送，新的 controller 都能從 shared state + external state 重建「這個 intent 是否已經 materialize」。

這才是 state-based controller 可以管理 LSF/Slurm 的必要條件。

相同邏輯也適用於 volume attach、license reservation、artifact promotion、foundry simulation reservation。只要 side effect 落在 Kubernetes API 之外，Lease election 就不能被當成 fencing token。

## Shared Informer 也不適合裝 EDA report 本體

另一個常見錯誤是覺得「既然 controller 靠 cache 工作，就把 report 也塞成 Kubernetes object」。

一個 APR / STA run 可能產生 MB 到 GB 等級的 log、timing report、congestion map、checkpoint；shared informer 的價值是讓 controller 快速觀察 **control metadata**，不是複製 heavy artifact。

比較合理的切割是：

<pre><code>Kubernetes object:
  run identity
  desired stage
  tool/version
  resource request
  artifact URI + digest
  summarized conditions
  policy / ownership

Artifact storage:
  Tcl / log / report
  netlist / checkpoint
  timing details
  congestion / waveform
  large diagnostic payload
</code></pre>

controller cache 裡保存「去哪裡找 artifact、它是哪一版、是否完成驗證」，而不是把整份 report 放進 etcd → apiserver → watch → informer cache。

這個切割同時保護 API server、etcd 與 controller-manager memory，也讓 NFS/SAN/object store 繼續做它們擅長的 bulk data path。

對 AI training 也一樣：checkpoint 不應進 Kubernetes API；control plane 記錄 checkpoint identity、location、generation 與 readiness，真正數百 GB / TB 的 bytes 留給 parallel filesystem 或 object storage。

## Workqueue 並不需要 durable，因為真正 durable 的是 state

這裡可以回頭回答一個容易困惑的問題：如果 workqueue 在 memory，controller process crash 後 queue 全消失，為什麼不會漏工作？

因為 queue 從來不應該是 correctness 的唯一來源。

新 leader / 新 process 啟動後，informer 先做 initial LIST，把目前存在的 object 放進 local cache；handler 或 controller startup path 再讓需要處理的 object 進 queue。即使 crash 前某一條 event 永遠遺失，只要 API state 仍然顯示 desired/current 不一致，下一輪 reconcile 就能重新發現工作。

這就是 command queue 與 reconciliation queue 最根本的差異。

如果設計一個 EDA flow controller，卻把「下一步應該跑 route」只保存在 Redis queue 裡，API object 本身無法推導，queue 丟失就是 correctness 丟失。反過來，如果 object state 能表示：

<pre><code>desiredStage: Route
completedStage: Place
inputArtifact: sha256:...
</code></pre>

那麼 queue 可以消失，controller 重啟後仍知道下一步是 route。

因此 workqueue 可以 aggressively deduplicate，也可以 retry/backoff；它是 throughput / fairness / retry 的執行工具，不是 business truth。

## 這套機制的邊界也很清楚

Shared Informer、workqueue、Lease 合起來能解三類問題：

| 問題 | Kubernetes 機制 | 保證邊界 |
| --- | --- | --- |
| 很多 controller 重複讀 API | Shared informer / local cache | cache eventually consistent |
| 同一 object event burst | key-based workqueue | 合併提示，不保存完整 event history |
| controller-manager replica 故障 | Lease leader election | 協調 active replica，不提供 external fencing |

這三個邊界如果搞混，就會產生三種典型 bug：

第一，假設 cache 永遠最新，做出基於 stale multi-object snapshot 的危險決策。

第二，把每個 watch event 當不可丟失的 transaction，最後在 event backlog 裡重播過期動作。

第三，把 leader election 當 exactly-once execution，結果在 failover 時重複 submit 外部 job。

kube-controller-manager 的設計其實一直在做相反的事：**盡量不要求一次性事件可靠，不要求 local read 強一致，也不把 leader 身分當外部世界的 fencing；它把 correctness 放回 authoritative state 與可重算的 reconciliation。**

## 下一個問題：Controller 已經決定「需要一個 Pod」，誰決定它該去哪裡

到這裡，control plane 的責任已經逐漸拆清楚。

kube-apiserver 提供 mutation boundary；etcd 保存有序 durable state；kube-controller-manager 持續把高階 object intent 展開成下一層 desired state，並用 informer/workqueue 把 observation 成本與修復成本控制在可接受範圍。

但 controller 產生 Pod 之後，仍然沒有回答一個 HPC 最敏感的問題：

<pre><code>這個 Pod 應該放在哪一台 node？
</code></pre>

一般 web service 可能只在意「有足夠 CPU/memory」；AI training 開始在意 GPU/NIC topology；APR 開始在意 NUMA、memory capacity、local scratch、license adjacency；MPI workload 則可能要求一整組 node 同時可用。

因此下一篇進入 <code>kube-scheduler</code>：從 queue、filter、score、reserve、permit 到 bind，拆解「找到一台能跑的 node」與「找到一個不會把 distributed workload 跑慢數倍的位置」到底差在哪裡。

## References

1. [kube-controller-manager Reference](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-controller-manager/) — Kubernetes v1.37 command reference。
2. [kube-controller-manager source: controllermanager.go](https://github.com/kubernetes/kubernetes/blob/master/cmd/kube-controller-manager/app/controllermanager.go) — Kubernetes upstream source。
3. [client-go SharedInformer source](https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/client-go/tools/cache/shared_informer.go) — eventual-consistency、cache 與 handler contract。
4. [client-go Workqueue source](https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/client-go/util/workqueue/queue.go) — dirty / processing semantics。
5. [Kubernetes: How the controller-runtime Cache Actually Works](https://kubernetes.io/blog/2026/07/29/controller-runtime-cache-explained/) — Kubernetes Blog, 2026-07-29。
6. [Kubernetes Lease](https://kubernetes.io/docs/concepts/architecture/leases/) — component leader election 與 Lease semantics。
7. [client-go leader election source](https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/client-go/tools/leaderelection/leaderelection.go) — LeaseDuration / RenewDeadline / retry 與 fencing limitation。
8. [client-go LeaseLock source](https://github.com/kubernetes/kubernetes/blob/master/staging/src/k8s.io/client-go/tools/leaderelection/resourcelock/leaselock.go) — Lease read/create/update implementation。
9. [Coordinated Leader Election](https://kubernetes.io/docs/concepts/cluster-administration/coordinated-leader-election/) — Kubernetes 1.37 Beta feature，預設停用。
