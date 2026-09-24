---
layout: post
title: "kube-apiserver 為什麼必須成為共同入口：大型叢集先統一『誰能改變事實』，才談得上可靠控制"
date: 2026-09-24 08:02:03 +0800
domain: eda
categories: eda
description: "kube-apiserver 的價值不是收 YAML，而是把身份、授權、admission、版本衝突、watch 與 persistence 收斂成一套共同 mutation contract。這篇從 request path、resourceVersion、watch cache、APF，一路推到 AI/EDA/HPC control plane 為何需要共同的 policy boundary，但不該把 RDMA、NFS/SAN 或 LSF data path 硬塞進 Kubernetes。"
---

一個大型叢集最危險的狀況，往往不是 scheduler 選錯 node，而是**很多元件都能直接改變「系統現在是什麼」**。

想像一個半導體設計平台：工程師從 portal 提交 APR，flow controller 依 project policy 補上 queue 與 license class；capacity controller 因機台壓力改資源需求；storage controller 建立 scratch volume；另一個 operator 因 node 維護把 workload 移走。若每個元件都能直接改 LSF job、資料庫、volume metadata 或某個共享狀態表，而沒有一個共同的版本、授權與驗證邊界，問題很快不再是「哪個 component 寫錯」，而是**你無法證明目前狀態到底是由哪一條合法決策路徑產生的**。

Kubernetes 對這個問題的選擇很強硬：cluster state 的正常變更都必須經過 API。官方文件直接把 REST API 稱為 Kubernetes 的 fundamental fabric；component 之間與外部命令的操作都由 API server 處理，持久狀態再以 API resource 的形式寫入 etcd。[Kubernetes API Overview](https://kubernetes.io/docs/reference/using-api/)

因此，kube-apiserver 的角色不能簡化成「YAML endpoint」。它更像 cluster 的 **commit boundary**：誰提出 mutation、誰有權做、物件是否符合政策、是不是基於過期版本、要以什麼形式持久化、後續 controller 要從哪個版本開始觀察，全部在這個邊界上被統一。

這個「共同入口」是邏輯上的，不代表只能跑一個 process。Kubernetes 明確設計 kube-apiserver 可以 horizontal scale，部署多個 instance 並由 load balancer 分流；一致的 durable state 則由 etcd backing store 提供。[Kubernetes Cluster Architecture](https://kubernetes.io/docs/concepts/architecture/)

所以真正值得理解的是：**多個 API server instance 為什麼仍能呈現一套共同的 cluster truth？**

## 如果所有 controller 都直接寫 backend，reconciliation 也救不了你

上一篇談 reconciliation：controller 不依賴「曾經執行過什麼」，而是反覆比較 desired state 與 observed state，重新推導下一步。這個模型有一個隱含前提：所有 controller 對「desired state 現在是什麼」必須有共同答案。

如果 controller A 讀 Kubernetes object，controller B 卻直接改 etcd，controller C 再把外部資料庫當 source of truth，reconcile loop 只會更快地把不同真相互相覆蓋。

要讓多個 control loop 可以安全共存，至少需要四個條件：

- mutation 必須先被識別：誰在改、改哪個 resource、做哪個 verb；
- mutation 必須先過 policy：這個 actor 是否有權改，物件內容是否允許；
- mutation 必須帶版本語義：避免慢半拍的 controller 把較新的狀態覆蓋掉；
- mutation 之後必須可被其他 controller 有序觀察：否則每個人看到的世界不同步。

kube-apiserver 就是把這四件事綁成一個 contract。

官方的 API access-control path 顯示，request 進入 API 後先經過 authentication，再做 authorization；寫入類 request 接著進 admission control，通過後再做 object validation 並寫入 object store。Admission controller 可以 mutate 或 reject create/update/delete 等 request，但單純的 GET/LIST/WATCH read 不走 admission mutation path。[Controlling Access to the Kubernetes API](https://kubernetes.io/docs/concepts/security/controlling-access/)｜[Admission Control](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/)

<figure>
  <img src="/assets/images/k8s/2026-09-24/apiserver-request-pipeline.svg" alt="kube-apiserver request logical pipeline" style="max-width:100%;height:auto;">
  <figcaption>圖 1｜kube-apiserver 的邏輯責任鏈：authentication、authorization、admission、object validation 與 persistence 共同形成 mutation boundary；讀取則有不同資料路徑。API Priority and Fairness 用來避免 overload 時低價值流量壓垮 control plane。依據 <a href="https://kubernetes.io/docs/concepts/security/controlling-access/">Controlling Access to the Kubernetes API</a>、<a href="https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/">Admission Control</a> 與 <a href="https://kubernetes.io/docs/concepts/cluster-administration/flow-control/">API Priority and Fairness</a> 重繪整理；圖示表達邏輯責任，不代表內部所有 filter 的逐函式呼叫順序。</figcaption>
</figure>

這條路徑看起來像一般企業 API gateway，但差異在於它不是只保護 API；**它保護的是 control plane 的 state transition。**

RBAC 只回答「這個 identity 能不能 update 這種 resource」。Admission 則可以看 object 內容，例如禁止某 namespace 的 workload 申請不允許的 runtime、要求特定 label、限制 privileged setting，或修改預設值。Kubernetes v1.30 起，ValidatingAdmissionPolicy 已 stable，可以直接用 CEL 在 API server 內宣告 validation，而不一定要把每個規則都做成外部 webhook。[Validating Admission Policy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/)

對 EDA 平台來說，這個差異非常實際。假設未來定義一個 `AprRun` CRD：

```yaml
apiVersion: r2g.example.com/v1
kind: AprRun
metadata:
  name: top-a-route-147
spec:
  design: top_a
  tool: innovus-26.1
  backend: lsf
  resources:
    cpu: 32
    memoryGi: 512
  licenseClass: innovus
  scratchClass: nvme-local
```

如果 policy 規定某類 project 不得使用超過 1 TiB DRAM，或只有特定 flow identity 能指定 `tapeout-critical` priority，最好的 enforcement point 不是等 job 進 LSF 後再靠 script 猜，而是在 intent 被接受成 cluster state 之前就拒絕不合法 mutation。

這就是 API boundary 相對於「共用一套 library」更強的地方。library 只能保證願意使用它的 client；API admission 保護的是所有走正常 API path 的 client。

Kubernetes 官方甚至另外列出 API server bypass risk：直接存取 kubelet 等旁路介面，可能繞過 admission 與 Kubernetes audit，這正反映了「共同入口」不是美學選擇，而是安全與一致性邊界。[Kubernetes API Server Bypass Risks](https://kubernetes.io/docs/concepts/security/api-server-bypass-risks/)

## 真正困難的不是阻止非法寫入，而是阻止「合法但過期」的寫入

身份與 policy 解決後，distributed control plane 還有更棘手的問題：兩個 actor 都合法，而且都基於自己當下看到的正確狀態做決策，最後仍然可能互相覆蓋。

假設 `AprRun` 目前 `resourceVersion=100`。

flow controller A 讀到它，準備把 `status.backendJobId` 寫成 LSF job 8451932；同時 capacity controller B 也讀到同一版，準備把某個 scheduling hint 更新。A 先寫成功後，物件已經進入下一版本。如果 B 還把自己手上的整份舊 object 用 PUT 覆蓋回去，就可能把 A 剛寫入的資料一起抹掉。

Kubernetes 不靠 distributed lock 解這個問題。對 PUT update，client 必須帶它所讀到的 `resourceVersion`；若 server 發現版本已經落後，會回 `409 Conflict`，要求 client 重新讀取、merge，再 retry。[Kubernetes API Concepts — Updates to existing resources](https://kubernetes.io/docs/reference/using-api/api-concepts/)

<figure>
  <img src="/assets/images/k8s/2026-09-24/apiserver-resourceversion-conflict.svg" alt="Kubernetes resourceVersion optimistic concurrency conflict" style="max-width:100%;height:auto;">
  <figcaption>圖 2｜兩個 controller 同時基於 `resourceVersion=100` 決策時，先提交者成功後會產生新版本；後提交的 stale PUT 會收到 `409 Conflict`，避免 lost update。依據 <a href="https://kubernetes.io/docs/reference/using-api/api-concepts/">Kubernetes API Concepts</a> 重繪整理。</figcaption>
</figure>

這個設計非常適合 controller architecture，因為 reconcile 本來就預期可以 retry。與其先拿全域 lock、長時間持有，再冒 deadlock 或 lock holder failure 的風險，不如允許 actor 樂觀地工作，只在 commit 發現 collision 時重算。

這裡也可以看出 `resourceVersion` 與一般「修改時間」完全不同。它不是給 UI 顯示用的 timestamp，而是 API consistency protocol 的一部分。Kubernetes 1.37 的 API Concepts 進一步規定，對 conformant 1.35+ API server，內建型別與 CRD 的 resourceVersion 在同一 API resource type 內必須可視為單調增加的十進位整數；但 client 仍應依 API 規則使用，而不是把它當全域 transaction ID。[Kubernetes API Concepts — Resource versions](https://kubernetes.io/docs/reference/using-api/api-concepts/)

對 EDA/AI control plane，這個機制帶來一個重要設計原則：**不要讓多個 controller 共享可變 row，然後靠「大家應該不會同時寫」維持安全。** 如果 ownership 可以切成不同 field，Server-Side Apply / managed fields 會比整份 object replacement 更適合；若某個 mutation 真正依賴舊值，就讓它帶版本條件，衝突時重算，而不是假裝 concurrency 不存在。

## API server 既然是共同入口，為什麼不會自己變成大瓶頸？

答案不是「它很快」，而是 Kubernetes 刻意讓讀取與變更通知不要全部落到 durable store。

在大型 cluster，scheduler、controller-manager、operator、CSI controller、CNI controller、autoscaler、監控與大量 custom controller 都會讀 API。如果每一個 LIST/WATCH 都直接做 etcd quorum read，etcd 很快會從 reliable backing store 變成整個 control plane 的 read fan-out engine。

Kubernetes 的解法是 watch cache。API server 維持一份反映 etcd state 的 in-memory cache，讓大量 GET/LIST/WATCH 可以從 cache 取得資料；client 再用 `resourceVersion` 銜接初始 snapshot 與後續 watch stream。API Concepts 對 watch 的語義要求是：client 可以先 list/get 取得版本，再從該 resourceVersion 之後接收 change stream；歷史版本已被 compact 時，client 需要處理 `410 Gone` 並重新建立狀態。[Kubernetes API Concepts — Efficient detection of changes](https://kubernetes.io/docs/reference/using-api/api-concepts/)

在 Kubernetes 1.37，`Most Recent` get/list 已可透過 watch cache 搭配 etcd progress notification 維持一致性，而不是每一次都直接做 etcd quorum read；官方文件明確把這件事描述為降低 etcd load 的 scalability 改進。[Kubernetes API Concepts — get/list semantics](https://kubernetes.io/docs/reference/using-api/api-concepts/)

<figure>
  <img src="/assets/images/k8s/2026-09-24/apiserver-watch-cache.svg" alt="kube-apiserver watch cache scaling read path" style="max-width:100%;height:auto;">
  <figcaption>圖 3｜kube-apiserver 透過 watch cache 把 durable persistence 與大規模 read/watch fan-out 分離。Kubernetes 1.37 對 most-recent read 的 cache consistency 有更完整支援。依據 <a href="https://kubernetes.io/docs/reference/using-api/api-concepts/">Kubernetes API Concepts</a> 重繪整理。</figcaption>
</figure>

這裡有一個很容易被忽略的系統設計：**etcd 是 source of truth，不代表每次讀取都必須直接讀 etcd。**

只要 API server 能維持明確 consistency semantics，就可以用 memory cache 承擔高頻 read path，把 etcd 留給 durable ordering 與 persistence。這和 HPC storage 很像：metadata durability 在 shared filesystem，不代表每次 `stat()` 都應穿透到最慢的 durable media；cache 是否安全，取決於 coherence contract，而不是「有沒有 cache」。

對未來半導體 design platform 也一樣。若 platform object 有幾十萬個 run、artifact、resource claim，而 agent/controller 全靠輪詢 PostgreSQL 主庫，最後一定會把 source of truth 當 message bus 使用。更可擴展的設計通常是：durable state 保持權威性，但 read model、watch stream、cache 與 queue 承擔 fan-out。

## 共同入口也會形成 queue；過載時必須決定誰先活下來

API server 把所有 control-plane mutation 集中到共同 contract，必然產生另一個問題：如果所有 actor 同時湧入，這個入口本身會排隊。

例如 5,000-node cluster 發生網路抖動，大量 node status、controller retry、operator reconcile 同時回來；另外還有 CI 系統批量 submit 10,000 個 Job。若 API server 只做單純 FIFO，一個 noisy client 就可能把 leader-election、node heartbeat 或 system controller 的關鍵 request 卡在後面，進一步造成更多 controller restart 與 retry，形成 overload feedback loop。

Kubernetes 的 API Priority and Fairness（APF）就是為這個 failure mode 設計。它會把 request 分類到不同 priority level，為各 level 分配 concurrency，並在同一 priority 內做 fair queuing；官方文件特別指出，其目的之一就是避免 poorly-behaved client 阻塞其他 controller，並保護像 leader election 這種關鍵流量。[API Priority and Fairness](https://kubernetes.io/docs/concepts/cluster-administration/flow-control/)

這個機制對 HPC/EDA 比 web cluster 更有意義，因為 submission traffic 常是 bursty 的。

Tape-out 前一天，幾百個 block 同時重跑 STA/APR；或 AI 平台一次提交數百個 worker 的 distributed job。這些 workload intent 都重要，但它們不應該有能力餓死 node health、storage attach、scheduler binding 或 control-plane leader election。

換句話說，**API fairness 其實是 control-plane admission scheduling。** 它排的不是 CPU core 或 GPU，而是「哪些 state transition request 可以先消耗 API server 的有限 concurrency」。這和後面真正的 workload scheduler 是不同層次的 scheduling problem。

## 對 AI / EDA / Foundry，API server 最有價值的不是「都改成 Pod」

走到這裡，就可以重新看一個常見爭論：既有 LSF/Slurm + NFS/SAN 的 EDA farm，要不要全部 Kubernetes 化？

如果把 Kubernetes 的價值等同於 Pod runtime，答案很容易變成二選一：不是把 job 全部 containerize，就是繼續留在 LSF。

但 kube-apiserver 提供的其實是另一個更有價值的切入點：**先統一 intent 與 policy mutation boundary，再決定 execution backend 要不要換。**

例如 `AprRun` 被 API 接受之後，controller 可以根據 policy 選擇：

`Kubernetes Job | LSF | Slurm | bare metal reservation`

storage 也可以是：

`local NVMe scratch | NFS | SAN | Lustre / BeeGFS`

network data path 更可能完全不經 Kubernetes overlay，而是 SR-IOV、InfiniBand、RoCE 或 dedicated fabric。

API server 不需要成為這些 data path 的代理。它只需要保存「這次 run 被允許使用哪個 backend、哪個 storage class、哪種 topology、哪個 priority，以及現在執行到哪裡」。

<figure>
  <img src="/assets/images/k8s/2026-09-24/apiserver-hpc-policy-boundary.svg" alt="kube-apiserver as AI EDA HPC policy boundary" style="max-width:100%;height:auto;">
  <figcaption>圖 4｜作者推論：在 AI / EDA / Foundry 平台中，kube-apiserver 最值得複用的是共同的 identity、policy、versioning、audit 與 watch contract；execution/data path 可繼續使用 LSF/Slurm、NFS/SAN、TCP/RDMA 等最適機制。Kubernetes API boundary 部分依據 <a href="https://kubernetes.io/docs/reference/using-api/">Kubernetes API Overview</a>、<a href="https://kubernetes.io/docs/concepts/security/controlling-access/">API Access Control</a> 與 <a href="https://kubernetes.io/docs/reference/using-api/api-concepts/">API Concepts</a> 重繪；HPC/EDA mapping 為作者推論。</figcaption>
</figure>

這樣做有一個很具體的好處：flow owner 不再需要知道每個 backend 的 mutation 細節。

他只宣告：`AprRun.spec.priority=tapeout-critical`。Admission 決定這個 identity 能不能這樣要求；scheduler/control-plane controller 再把這個 intent 映射成 LSF queue、Kubernetes PriorityClass 或 dedicated reservation。未來 backend 從 LSF 換成 Slurm，甚至某些 stage 搬到 Kubernetes，flow intent 不必跟著重寫。

這種 abstraction 才有平台價值：**把 organization policy 與 backend implementation 分開，但又保留可以向下追到真實 execution 的 evidence。**

反過來，如果平台只是包一層 REST API，背後仍允許每個 flow script 直接 `bsub`、直接 mount 任意 NFS、直接改資料庫 row，那就沒有真正形成 control plane。它只有 portal，沒有 authority boundary。

## kube-apiserver 的限制也很清楚：它只能治理被表達成 API state 的東西

共同入口很強，但不能神化。

kube-apiserver 能保證的是 API object mutation 的 policy、versioning 與 observation contract。它不會讓 512 GiB APR job 自動得到 NUMA-local memory；不會因為 PVC 建立成功，就保證 NFS metadata latency 足夠；也不會因為 RDMA device 已被分配，就保證 PFC/ECN、NIC queue、IRQ affinity 與 PCIe locality 正確。

換句話說，API server 可以把「我要 32 CPU、512 GiB、某種 storage/network capability」寫成可治理的 intent，但**真正的 performance correctness 最後仍然落在 kubelet、cgroup、Linux scheduler、NUMA、VFS、block layer、TCP/RDMA、NIC 與 storage fabric。**

這也是為什麼這個系列不能停在 CRD/operator。

我們先建立了 reconciliation：系統為什麼要從 state difference 重算，而不是相信 command history。現在再建立 API boundary：多個 control loop 為什麼需要一套共同、可版本化、可驗證的 cluster truth。

下一個問題就避不掉了：如果 durable truth 最後存在 etcd，**etcd 到底如何讓多個 API server 在 machine failure、network delay、leader change 下仍對寫入順序有共同答案？**

下一篇會進入 Raft、quorum、MVCC、revision、linearizable read、watch 與 compaction。到那時，`resourceVersion` 背後那個真正負責「哪一個 state transition 先發生」的分散式系統才會浮出來。

## References

1. [Kubernetes API Overview](https://kubernetes.io/docs/reference/using-api/) — Kubernetes Documentation, v1.37.
2. [The Kubernetes API](https://kubernetes.io/docs/concepts/overview/kubernetes-api/) — Kubernetes Documentation.
3. [Kubernetes API Concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/) — Kubernetes Documentation, including update conflicts, resourceVersion, watch and read consistency semantics.
4. [Controlling Access to the Kubernetes API](https://kubernetes.io/docs/concepts/security/controlling-access/) — Kubernetes Documentation.
5. [Admission Control in Kubernetes](https://kubernetes.io/docs/reference/access-authn-authz/admission-controllers/) — Kubernetes Documentation.
6. [Validating Admission Policy](https://kubernetes.io/docs/reference/access-authn-authz/validating-admission-policy/) — Kubernetes Documentation.
7. [API Priority and Fairness](https://kubernetes.io/docs/concepts/cluster-administration/flow-control/) — Kubernetes Documentation.
8. [Cluster Architecture](https://kubernetes.io/docs/concepts/architecture/) — Kubernetes Documentation.
9. [kube-apiserver command reference](https://kubernetes.io/docs/reference/command-line-tools-reference/kube-apiserver/) — Kubernetes Documentation.
10. [Kubernetes API Server Bypass Risks](https://kubernetes.io/docs/concepts/security/api-server-bypass-risks/) — Kubernetes Documentation.
