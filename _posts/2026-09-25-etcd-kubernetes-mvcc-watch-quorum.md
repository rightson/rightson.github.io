---
layout: post
title: "etcd 把 Kubernetes 狀態變成可排序歷史：MVCC、Watch 與 Quorum 如何決定 Control Plane 的極限"
date: 2026-09-25 08:02:46 +0800
domain: distributed-systems
categories: distributed-systems
description: "kube-apiserver 統一了誰能改變叢集狀態，etcd 則負責讓這些改變有可恢復、可排序、可追蹤的歷史。從 revision、MVCC、watch、compaction、quorum 到 WAL fsync，可以直接看見 Kubernetes control plane 為什麼最後仍受磁碟與網路延遲約束。"
---

[上一篇](/eda/2026/09/24/kube-apiserver-policy-serialization-boundary.html)把問題停在一個很關鍵的位置：kube-apiserver 可以統一 authentication、authorization、admission 與 mutation contract，但 API server 本身不是永久狀態。它可以重啟、被替換，甚至同時有多個 replica。那麼下一個必然問題就是：**當很多 API server、controller 與 scheduler 同時讀寫 cluster state 時，誰來保證「哪個狀態先發生、現在最新的是哪一版、故障後要從哪裡接回去」？**

Kubernetes 把這件事交給 etcd。

把 etcd 理解成一個「存 YAML 的 key-value database」會低估它的角色。對 Kubernetes 而言，etcd 更像是一個把所有 control-plane mutation 排成單一邏輯時間軸的 durable state machine。每次 key space 改變都會得到新的 cluster-wide revision；watcher 可以沿著 revision 往前追；controller crash 後可以從曾經看過的位置繼續；而當多個 writer 同時修改同一個 object 時，revision 又成為 optimistic concurrency 的基礎。[etcd v3 API](https://etcd.io/docs/v3.6/learning/api/) 對 revision、MVCC 與 watch 的定義正是這套機制的底層。

這也意味著 Kubernetes control plane 有一個很現實的下限：**再漂亮的 declarative API，最後仍要等多數 etcd member 把狀態可靠地落到 storage。** 如果 WAL fsync 太慢、peer network 抖動、leader churn，scheduler 並不會因為演算法還能算出最佳 node 就繼續前進。它必須先把 binding 變成可被整個叢集承認的事實。

<figure>
  <img src="/images/distributed-systems/2026-09-25/etcd-write-quorum.svg" alt="etcd leader 將 mutation 複寫到多數 member，寫入 WAL 後才形成 committed revision" style="max-width:100%;height:auto;">
  <figcaption>圖 1｜一個 control-plane mutation 必須穿過 leader、Raft replication 與多數 member 的 durable write，才成為 committed revision。依據 <a href="https://etcd.io/docs/v3.6/learning/api/">etcd v3 API</a>、<a href="https://etcd.io/docs/v3.6/op-guide/hardware/">etcd Hardware Recommendations</a> 整理／重繪。</figcaption>
</figure>

## 共享狀態如果沒有全域順序，reconciliation 很快就會失去意義

假設 scheduler 看見一個 Pending Pod，決定把它放到 node-A；同一時間，另一個 controller 因為 maintenance policy 正準備把 node-A 標成不可接受新的 workload。兩邊都可能在幾毫秒內完成自己的計算。

問題不在誰比較聰明，而在於：**兩個決策最後必須落進同一個可排序的 cluster history。**

如果底層 storage 只提供最後寫入者獲勝而沒有可驗證的版本關係，controller 很難知道自己剛剛基於哪一版世界做了決策。它也無法可靠區分：我讀到的是最新狀態；我讀到的是稍舊但仍可接受的 snapshot；我在寫入前，別人已經先修改了同一個 object；或我斷線期間漏掉了哪些變化。

etcd v3 為整個 key space 維護一個 64-bit cluster-wide revision。每次 key space 發生 mutation，store revision 就往前推進。這個 revision 不是 wall-clock time，而是 logical clock；它的價值在於提供一個可比較的先後。

<pre><code>revision 4201 : Pod/foo created
revision 4202 : Node/A condition changed
revision 4203 : Pod/foo spec.nodeName = node-A
revision 4204 : Pod/foo status updated</code></pre>

這四件事不需要發生在同一台 API server，也不需要依賴每台機器時鐘完全同步。只要它們被 etcd commit，就能落在一條共同排序的歷史上。

這就是 Kubernetes <code>resourceVersion</code> 能成立的基礎。Kubernetes 官方 API 文件說明，每個 object 都帶有 <code>resourceVersion</code>，client 可以用它來追蹤自某一版本之後的變化；對 client 而言 resourceVersion 應視為 opaque value，不應自行解析其數值語義。[Kubernetes API Concepts](https://kubernetes.io/docs/reference/using-api/api-concepts)

## Quorum 把一致性直接換成延遲成本

從 API server 送出一個 mutation 到 etcd，大致可以抽象成：

<pre><code>API server
   ↓
etcd leader
   ↓
append proposal
   ↓
replicate to followers
   ↓
majority persists WAL
   ↓
commit
   ↓
apply to MVCC backend
   ↓
response</code></pre>

write latency 不是 leader 本機 memory access 的延遲，而是多數 replica 完成必要持久化與 consensus path 的延遲。

三個 member 的 etcd cluster，需要至少兩個 member 同意；五個 member，需要至少三個。

<pre><code>3 members → quorum 2 → tolerate 1 member failure
5 members → quorum 3 → tolerate 2 member failures</code></pre>

多兩台不是免費得到更高 throughput。member 數量增加主要是提高 failure tolerance，而不是橫向擴充寫入能力；production 應維持奇數 member。[Kubernetes: Operating etcd clusters](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/)

這也解釋了為什麼把 etcd 拉到更多 zone 不是單純的 HA 加法。quorum path 變長，network RTT 與尾端 latency 會直接進入每次 durable mutation 的成本。etcd 的 tuning 文件把 heartbeat interval 與 election timeout 綁在 peer RTT 上；跨高延遲網路部署時，failure detection 必須變慢，否則短暫抖動就容易被誤判為 leader failure。[etcd Tuning](https://etcd.io/docs/v3.6/tuning/)

## MVCC 讓讀、寫、watch 共享同一個歷史座標

etcd 的 Multi-Version Concurrency Control 會保留 key 的歷史 revision，而不是每次 update 就把舊值完全覆蓋掉。

<pre><code>rev 500  /pods/foo = Pending
rev 540  /pods/foo = Running
rev 610  /pods/foo = Succeeded</code></pre>

client 可以要求在某個 revision 看 key space 的 snapshot，也可以從某個 revision 開始 watch 後續事件。這讓「先取得目前世界，再追蹤之後變化」成為可能。

<figure>
  <img src="/images/distributed-systems/2026-09-25/etcd-mvcc-watch.svg" alt="etcd MVCC revision timeline 與多個 watcher 從不同 revision 持續接收更新" style="max-width:100%;height:auto;">
  <figcaption>圖 2｜MVCC 把 key space 變成 revision-indexed history；watcher 可以從已知 revision 接續，而不是每次重新掃描全量狀態。依據 <a href="https://etcd.io/docs/v3.6/learning/api/">etcd v3 API</a> 與 <a href="https://kubernetes.io/docs/reference/using-api/api-concepts">Kubernetes API Concepts</a> 整理／重繪。</figcaption>
</figure>

對 Kubernetes controller 而言，這比資料庫支援 transaction 更直接。controller 通常需要的是：先建立某類 object 的 local cache；記住自己同步到哪個 resourceVersion；持續接收後續變化；crash 或 connection reset 之後，不要默默漏事件。

這也是 [前一篇 reconciliation loop](/eda/2026/09/23/kubernetes-reconciliation-control-loop.html) 裡 list/watch 模式能成立的 storage 前提。

多 writer 衝突也能透過 revision 做 compare-and-swap 類型的保護。etcd transaction 可以先比較 key 的 modification revision，再決定是否執行 mutation。Kubernetes API 的 optimistic concurrency 最後就是建立在這種「我寫入時，前提版本仍然有效嗎？」的能力上。

## Watch 不是無限保留的 event log

如果 controller 每秒都重新 LIST 全部 Pods、Nodes、Jobs，cluster 規模上去後，API server 與 etcd 很快就會被重複讀取壓垮。watch 的價值就是把 polling 轉成 incremental change stream。

<pre><code>LIST current objects
→ remember resourceVersion
→ WATCH from that resourceVersion
→ apply incremental changes to local cache</code></pre>

但歷史不能無限保留。

etcd 的 MVCC history 會持續成長。若每一次 update 的舊 revision 永遠存在，backend database 只會越來越大；watcher 數量也會佔用記憶體。etcd 官方 hardware guide 指出，除了 cache key-value data 外，大量記憶體會用在追蹤 watcher；數千 watcher、數百萬 keys 的重負載部署需要顯著更多 RAM。[etcd Hardware Recommendations](https://etcd.io/docs/v3.6/op-guide/hardware/)

所以 etcd 必須 compaction：把某個 revision 以前的歷史宣告為不再可讀。

假設 controller 最後看見 revision 9000，然後斷線很久；回來時 etcd 已 compact 到 revision 12000。它不能假裝從 9001 繼續，因為中間歷史已經不存在。

Kubernetes API 對這種情況的語義很明確：client 可能收到 HTTP <code>410 Gone</code>，接著必須丟棄過舊 cache、重新 LIST，取得新的 resourceVersion，再重新 WATCH。[Kubernetes API Concepts](https://kubernetes.io/docs/reference/using-api/api-concepts)

<figure>
  <img src="/images/distributed-systems/2026-09-25/etcd-compaction-relist.svg" alt="watcher 落後於 compaction revision 後必須重新 LIST 再重新建立 WATCH" style="max-width:100%;height:auto;">
  <figcaption>圖 3｜當 watcher 落後到 compaction window 之外，系統不能補出已刪除歷史；正確恢復方式是重新建立 snapshot，再接新的 watch。依據 <a href="https://etcd.io/docs/v3.6/op-guide/maintenance/">etcd Maintenance</a> 與 <a href="https://kubernetes.io/docs/reference/using-api/api-concepts">Kubernetes API Concepts</a> 整理／重繪。</figcaption>
</figure>

這裡要分清兩個不同動作：compaction 移除舊 revision 的歷史可見性；defragmentation 則把 backend 已經空出的內部空間真正還給 filesystem。

刪除歷史不代表磁碟檔案立即縮小。etcd maintenance guide 指出，compaction 之後 backend 可能留下 internal fragmentation；defrag 才會回收 filesystem space，而且對 live member 執行 defrag 時會阻塞該 member 的讀寫，因此必須有操作節奏。[etcd Maintenance](https://etcd.io/docs/v3.6/op-guide/maintenance/)

## 幾毫秒的 storage tail latency，可以放大成整個 control plane 的停滯

etcd 的寫入路徑會碰 durable log，所以它對 disk write latency 非常敏感。

官方 hardware guide 把 fast disk 列為 etcd performance 與 stability 最重要的因素之一：多數 member 必須把 request 寫入持久化 log；如果 disk write 太慢，heartbeat 可能 timeout，接著觸發 election。[etcd Hardware Recommendations](https://etcd.io/docs/v3.6/op-guide/hardware/)

<pre><code>shared disk / slow fsync
        ↓
Raft WAL persistence delayed
        ↓
heartbeat / replication response delayed
        ↓
follower suspects leader
        ↓
leader election
        ↓
mutating request stalls or times out
        ↓
scheduler/controller cannot commit new state</code></pre>

<figure>
  <img src="/images/distributed-systems/2026-09-25/etcd-io-failure-chain.svg" alt="從 WAL fsync latency 到 leader election，再到 Kubernetes control-plane mutation 停滯的 failure chain" style="max-width:100%;height:auto;">
  <figcaption>圖 4｜etcd 把 storage tail latency 放進 consensus critical path；磁碟抖動可能一路放大成 leader election 與 control-plane mutation stall。依據 <a href="https://etcd.io/docs/v3.6/tuning/">etcd Tuning</a>、<a href="https://etcd.io/docs/v3.6/metrics/">etcd Metrics</a> 與 <a href="https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/">Kubernetes etcd Operations</a> 整理／重繪。</figcaption>
</figure>

對 HPC/EDA 環境，這個問題尤其容易被低估，因為大家直覺會把 storage performance 想成 job 的 NFS / SAN throughput。但 control plane storage 是另一條完全不同的路徑。

假設一台 control-plane host 同時承受大量 log write、image unpack、backup、monitoring I/O，甚至把 etcd data 放在高 contention 的 shared virtual disk。即使 compute node 的 NFS/SAN 很快，etcd 的 WAL fsync 仍可能抖動。結果不是某個 APR job 讀檔變慢，而是新的 Job、Pod binding、Lease、status update 都開始累積 latency。

更微妙的是：**已經在 worker node 上執行的 process 可能完全沒事。**

Kubernetes 官方 etcd 操作文件指出，etcd 失去可用 quorum 時，cluster 無法改變 current state；已經排程的 Pod 仍可能繼續執行，但新的 Pod 無法正常被排程。這正好說明 control plane 與 execution data plane 的分界。[Operating etcd clusters for Kubernetes](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/)

所以在 EDA farm 裡，control plane 掛掉不等於 Innovus process 立刻被 kill；但新的 flow stage、reschedule、volume mutation、queue admission 可能全部卡住。對長時間 tape-out workload，這種 failure semantics 比單純 service down 更需要被設計清楚。

## etcd 適合存 cluster truth，不適合存 EDA artifact、telemetry 或大物件

etcd 的 system limits 文件指出，預設單一 request 最大約 1.5 MiB；預設 backend storage quota 為 2 GiB，正常環境建議上限約 8 GiB。[etcd System Limits](https://etcd.io/docs/v3.6/dev-guide/limit/)

這些數字已經透露它的設計位置：**etcd 是 metadata store，不是 artifact store。**

| 類型 | 適合放哪裡 | 原因 |
| --- | --- | --- |
| desired state、policy、job identity、artifact reference、小型 status | Kubernetes API / etcd | 需要一致、可 watch、可重建控制狀態 |
| netlist、DEF/GDS、checkpoint、tool report、waveform、大型 log | NFS / SAN / parallel FS / object store | 大容量、吞吐與 POSIX/object semantics 才是主需求 |
| 高頻 metrics、trace、event telemetry | TSDB / log / observability pipeline | 高寫入率與 retention query 不應拖累 consensus store |

例如 APR stage 完成後，control plane 應該記 artifact URI、hash、stage、tool version 與 state，而不是把數百 MB checkpoint 本身塞進 CRD。

這個切割的理由不只是容量，而是 failure isolation。大型 artifact I/O、metrics burst、log retention 不應該競爭 control-plane consensus 的 disk latency budget。

## 3-member 或 5-member，是可容忍故障數與 commit path 成本的交換

三個 etcd member 的 quorum 是 2，可以容忍一個 member failure；五個 member 的 quorum 是 3，可以容忍兩個 member failure。Kubernetes 官方操作文件建議 production 使用 odd number members，並以 five-member cluster 作為 production recommendation；真正部署時仍要看 failure domain、RTT 與 storage quality，而不是把 member 數當成越多越好。[Operating etcd clusters for Kubernetes](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/)

對同一個 datacenter 裡的 on-prem HPC cluster，我會先問三個更底層的問題：

- 三台或五台 member 是否真的落在獨立 failure domain？
- member 間 RTT 與 tail latency 是否穩定？
- 每台 member 的 persistent storage 是否足夠隔離 noisy neighbor？

如果五個 member 全部共享同一個 storage array、同一個 top-of-rack failure domain，數字上的 quorum 可能比實際的 fault isolation 好看很多。

## 對 AI / EDA / Foundry 平台，etcd 的價值是把控制狀態縮到足夠小、足夠可靠

在半導體或 AI HPC 場景，Kubernetes 常被拿來和 LSF、Slurm 比 scheduler feature。從 etcd 這一層往下看，會發現更早的設計問題：**哪些東西值得成為整個平台必須一致承認的 state？**

以 EDA flow control plane 為例，可以把 etcd 留給 FlowRun desired state、stage dependency、execution backend choice、license/policy decision reference、artifact identity、retry/checkpoint pointer 與 observed stage state。

實際 execution 可以仍然在 LSF；大型 checkpoint 可以仍然在 NFS/SAN；compute node 可以有 local NVMe scratch。Kubernetes control plane 的價值不是把所有 data path 都收進 etcd，而是讓不同 backend 的狀態有共同、可 watch、可恢復的表示。

這也會反過來影響 CRD 設計：如果一個 CRD status 每秒更新數十次，或者把完整 tool report 塞進 object，問題不只是 API 太肥，而是把高頻、低價值資料推進 consensus write path。

設計 control plane 時，一個很實用的判準是：

<pre><code>這個狀態如果晚 5 秒看到，會不會破壞 correctness？</code></pre>

如果答案是否定的，它可能不需要成為 etcd 的高頻 mutation。

## etcd 的邊界，最後把問題推向 controller 本身

走到這裡，Kubernetes 的前三層已經接起來了。

kube-apiserver 統一誰有資格提出 mutation；etcd 統一哪些 mutation 已經成為 cluster history；watch 又把這段歷史送回每個 controller。

下一個問題因此不再是 storage：**controller 收到同一條可排序的變化之後，要如何在重複 event、process crash、leader failover 與 stale cache 下，仍然安全地計算下一個動作？**

這會進到下一篇的 kube-controller-manager：built-in controllers、shared informer、workqueue、Lease-based leader election，以及為什麼 Kubernetes 可以讓 controller 重啟很多次，卻仍然要求 reconcile 結果收斂。

## References

1. [etcd v3 API — revisions, MVCC, watch and transactions](https://etcd.io/docs/v3.6/learning/api/)
2. [etcd Hardware Recommendations](https://etcd.io/docs/v3.6/op-guide/hardware/)
3. [etcd Maintenance — compaction, defragmentation and quotas](https://etcd.io/docs/v3.6/op-guide/maintenance/)
4. [etcd Tuning — heartbeat, election timeout, disk and network latency](https://etcd.io/docs/v3.6/tuning/)
5. [etcd System Limits](https://etcd.io/docs/v3.6/dev-guide/limit/)
6. [etcd Metrics](https://etcd.io/docs/v3.6/metrics/)
7. [Kubernetes API Concepts — resourceVersion, list/watch and 410 Gone](https://kubernetes.io/docs/reference/using-api/api-concepts)
8. [Kubernetes — Operating etcd clusters](https://kubernetes.io/docs/tasks/administer-cluster/configure-upgrade-etcd/)
