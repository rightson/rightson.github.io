---
layout: post
title: "Kubernetes 創始篇：它不是更好的 Batch Scheduler，而是一個把 Desired State 變成 Cluster Reality 的 Control Plane"
date: 2026-09-22 13:40:00 +0800
author: Scott Yo-Ru Chen
domain: eda
categories: eda
description: "理解 Kubernetes 的起點，不是 Pod、Service 或 YAML，而是大規模系統為什麼需要把『想要什麼』與『現在是什麼』分離，再透過持續 reconciliation 把兩者拉近。從這個問題出發，才能看懂 API server、etcd、controller、scheduler、kubelet，以及它們與 Linux kernel、NUMA、RDMA、NFS/SAN 和 HPC workload 的真正邊界。"
---

如果今天有人問我：「EDA farm 要不要從 LSF 換成 Kubernetes？」我會先把這個問題拆掉。

因為 **Kubernetes 最值得理解的地方，從來不是它能不能啟動 container，而是它重新定義了大型運算平台如何控制一個永遠在變動的系統。**

一個數千台甚至數萬台機器的 cluster，不可能長時間維持靜止。Node 會掛、process 會 crash、network 會 partition、disk 會變慢、image 會拉取失敗、GPU 會 unhealthy、工程師會同時提交新工作，controller 自己也可能 restart。只要規模夠大，「異常」就不再是例外，而是正常工作狀態的一部分。

如果平台的基本模型仍然是：

`收到命令 → 執行一串步驟 → 希望最後成功`

那麼每一次中途失敗，都會逼系統回答一個很麻煩的問題：**到底執行到哪裡？哪些動作已經成功？哪些可以重做？哪些重做會造成重複副作用？**

規模越大，這種 procedural automation 越容易變成由大量 retry、cleanup、repair scripts 拼起來的狀態機。

Kubernetes 選擇從另一個方向解決問題：不要把「如何一步一步做到」當成唯一真相，而是先把「系統應該長成什麼樣子」保存下來，然後讓很多小型 control loops 不斷觀察現況，持續把 current state 拉向 desired state。

這個差異，比 container 本身重要得多。

也正因如此，理解 Kubernetes 的正確路徑，不應該是先背 Pod、Deployment、Service，而是先回答：

**一個大規模運算系統，為什麼最後會需要 desired state、reconciliation、shared state 與分散式 controllers？**

<figure>
  <img src="https://kubernetes.io/images/docs/components-of-kubernetes.svg" alt="Kubernetes 官方 cluster components 架構圖" style="max-width:100%;height:auto;">
  <figcaption>圖 1｜Kubernetes 官方 cluster components。Control plane 由 API server、etcd、scheduler、controller manager 等元件構成；worker node 上由 kubelet 與 container runtime 將宣告轉成實際 workload。來源：<a href="https://kubernetes.io/docs/concepts/overview/components/">Kubernetes Documentation — Kubernetes Components</a>。</figcaption>
</figure>

## 當失敗變成常態，命令就不再足以描述系統

先想一個最簡單的例子。

假設我們需要四個完全相同的服務 instance。傳統 script 可以寫：

`create instance 1 → create instance 2 → create instance 3 → create instance 4`

但如果第三台建立完之後 machine crash 呢？

script 重跑時，前兩個 instance 是否還存在？第三個是否已經建立成功但 response 丟失？第四個根本沒開始？如果直接重跑全部步驟，會不會變成六個 instance？

真正困難的不是「create」這個 API，而是**失敗發生後，如何重新知道事實。**

因此，大規模控制系統需要的第一個性質不是更複雜的 workflow engine，而是一個可持久化、可觀察的 system state。

如果目標只寫成：

`replicas = 4`

那麼 controller 不需要知道昨天發生過哪些命令，只需要知道：

`desired = 4`
`current = 3`

差值就是下一步行動。

如果 current 變成 5，就刪掉一個；如果 node 壞掉後 current 變成 3，就補一個。controller crash 之後重新啟動，也不需要恢復一條極長的 program counter，只要重新讀 state，再算一次差值。

這就是 Kubernetes controller 模型最根本的價值。

官方文件把 controller 描述成持續運作的 control loop：觀察 cluster state，然後讓 current state 靠近 desired state；API object 的 `spec` 通常就是 desired state 的表示。[Kubernetes Controllers](https://kubernetes.io/docs/concepts/architecture/controller/)

例如：

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 4
```

真正的語義不是：

> 現在幫我 create 四個 Pod。

而是：

> 從現在開始，只要這個 Deployment 還存在，就持續讓系統接近四個可用 replica。

這兩句話表面上只差一點點，系統架構卻完全不同。

前者是一個 command；後者是一個長期 invariant。

## 一旦接受「狀態比命令重要」，Kubernetes 的架構就幾乎被推導出來了

如果 desired state 必須在 controller crash 後仍然存在，那它不能只存在某個 process memory。

所以需要 durable state。

如果很多 controller 都要讀寫同一組 cluster objects，就需要共同的 API contract。

如果每個 controller 都自己直接修改 etcd schema，整個系統很快就無法治理，所以必須有統一的 API server 做 validation、admission、authorization、versioning 與 concurrency control。

如果 controller 要在幾萬甚至幾十萬個 objects 中持續找出變化，又不能每秒 full scan 一次整個 cluster，就需要 watch / resourceVersion / cache 這類增量觀察機制。

如果不同 controller 各自管理 Deployment、Job、Node、Endpoint、Volume 等不同部分，它們又必須允許獨立 failure，就不能把所有邏輯塞進單一 central brain。

從這些限制出發，Kubernetes 的主要形狀自然出現：

`API server → durable state → watch → independent reconcile loops`

<figure>
  <img src="/assets/images/k8s/k8s-reconciliation-path.svg" alt="Kubernetes desired state 到 Linux execution substrate 的 reconciliation path" style="max-width:100%;height:auto;">
  <figcaption>圖 2｜Kubernetes reconciliation path。使用者寫入 desired state 後，API/etcd 保存 cluster state；controllers 與 scheduler 產生後續決策；kubelet 最後把 node state 向目標收斂。依據 <a href="https://kubernetes.io/docs/concepts/architecture/controller/">Kubernetes Controllers</a>、<a href="https://kubernetes.io/docs/concepts/overview/components/">Kubernetes Components</a> 與 <a href="https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/">Scheduling Framework</a> 重繪整理。</figcaption>
</figure>

這張圖真正值得看的不是元件名稱，而是箭頭方向。

Kubernetes 沒有一個元件從頭到尾「執行整個 Deployment」。Deployment controller 看到缺 Pod，只負責建立 Pod object；scheduler 看到未綁定的 Pod，只負責決定 node；kubelet 看到屬於自己的 Pod，只負責讓 node 上的 runtime state 接近 Pod spec。

每一個元件只掌握足夠完成自己責任的資訊。

這樣做的代價是 eventual consistency：某一瞬間 cluster 可能永遠不是完全一致的。但換來的是 fault isolation、retryability 與可水平演化的控制面。

在大規模系統裡，這通常比「所有事情必須在一次 transaction 中完成」更實際。

## 所以 scheduler 並不是 Kubernetes 的中心

這裡是從 HPC 世界切進 Kubernetes 最容易誤判的地方。

LSF、Slurm 這類 workload manager 的日常介面高度圍繞 job queue 與 resource allocation，所以工程師自然把 scheduler 視為核心。Slurm 官方就明確把三項主要功能定義為：分配 compute resources、啟動與監控 parallel work，以及仲裁 pending jobs 對資源的競爭；它也具備 reservation、backfill、gang scheduling、topology-aware placement 等典型 HPC 機制。[Slurm Overview](https://slurm.schedmd.com/overview.html)

Kubernetes scheduler 做的事情其實更窄。

它面對的是一個已經存在於 API 中、尚未綁定 node 的 Pod，然後經過 queue、filter、score、reserve、permit、bind 等階段，把：

`pod-123`

轉成：

`pod-123 → node-42`

[Kubernetes Scheduling Framework](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/)

到這裡為止，container 甚至還沒有真的被建立。

更重要的是，即使 scheduler 暫時停掉，Kubernetes 很多核心語義仍存在：

- 已經執行中的 Pod 不會因 scheduler 掛掉立即停止；
- Deployment controller 仍然知道 desired replica 數量；
- kubelet 仍然管理 node 上已綁定的 Pods；
- API server / etcd 仍然保存 cluster state；
- scheduler 恢復之後，可以重新處理那些尚未 placement 的 Pods。

這揭露了兩個系統的不同重心。

Slurm 的第一級 abstraction 是 **job/resource allocation**。

Kubernetes 的第一級 abstraction 是 **persistent API state + reconciliation**。

兩者有重疊，但不是同一類問題的不同品牌實作。

## 為什麼 Kubernetes 要拆成很多 control loops，而不是一顆超級 scheduler？

因為大型平台的決策根本不在同一個時間尺度。

一個 Pod placement 可能需要毫秒到秒。

Node failure detection 可能是數秒到數十秒。

Deployment rollout 可能持續幾分鐘。

HPC admission queue 可能讓一個 256-GPU job 等幾十分鐘甚至幾小時。

容量規畫則可能是幾週到幾季。

如果把這些 decision loops 全部塞進單一 scheduler，它必須同時理解：

- immediate feasibility；
- global fairness；
- topology；
- capacity reservation；
- hardware health；
- application lifecycle；
- storage attachment；
- network identity；
- retry；
- external cloud / storage / accelerator APIs。

它很快就不再是一個 scheduler，而是一個無法拆解的 monolith。

Kubernetes 選擇讓不同 controllers 各自維護局部 invariant，再透過 API objects 交換 state。這讓系統可以新增新的 CRD/controller，而不必修改所有既有元件。

這也是 Kubernetes 為什麼後來能從「container orchestration」擴展成 infrastructure control plane。

只要某個外部資源具有三件事：

1. 可以描述 desired state；
2. 可以觀察 current state；
3. 可以透過 API 或 driver 改變它；

理論上就能包進 reconciliation loop。

Volume、LoadBalancer、GPU、NIC、certificate、database cluster 可以如此；EDA flow execution、license pool、artifact lineage、甚至外部 LSF backend 也可以如此。

這並不表示「全部都應該 Kubernetes 化」，而是表示它的控制模型具有很強的可組合性。

## API server 與 etcd 的角色，不只是「放 YAML 的資料庫」

一旦所有 controllers 都靠 shared state 協作，shared state 就變成控制面的核心基礎設施。

Kubernetes 官方把 kube-apiserver 定義為 control plane front end，而 etcd 是保存 API server data 的 consistent、highly available key-value store。[Kubernetes Components](https://kubernetes.io/docs/concepts/overview/components/)

但如果只把 etcd 想成 database，仍然低估了整個系統。

controller 面臨的真正問題是：**如何持續知道哪些 objects 變了。**

最直覺的方法是 polling：

`LIST all Pods → compare → sleep → LIST again`

假設 cluster 有 100,000 Pods、數百個 controllers，每個 controller 都頻繁 full scan，API server 和 etcd 很快就會被讀取流量淹沒。

因此 Kubernetes 大量依賴 LIST + WATCH 模型。

controller 先取得一個 snapshot 與 resourceVersion，之後接收增量事件，再把有變化的 object key 放進 workqueue。

典型邏輯更接近：

`watch event`
→ `enqueue key`
→ `read latest object`
→ `compare desired/current`
→ `act`
→ `update status`
→ `retry when necessary`

事件本身不是唯一真相。

即使同一事件重複送達，或 controller 在處理一半時 crash，重新起來仍然可以讀「最新 state」再算一次。只要 reconcile logic 具有 idempotency，整個系統就不必依賴一條完美、exactly-once 的事件歷史。

這也是 Kubernetes 很重要的一個 distributed-systems 取捨：**盡量把 correctness 建立在可重新讀取的 state，而不是建立在永遠不丟失、永遠不重複的 event sequence。**

後面談 informer、workqueue、controller-runtime、etcd MVCC 時，這個觀念會一直出現。

## 到 scheduler bind 為止，其實都還只是「決定」

接下來才是很多平台文章容易跳過的部分。

假設 scheduler 完成：

`pod-123 → node-42`

這只是在 API state 中確定 placement。

node-42 上的 kubelet 觀察到這個 Pod 屬於自己之後，才開始把 declarative spec 轉成 machine reality。

Kubernetes 使用 CRI 作為 kubelet 與 container runtime 之間的主要介面；今天常見 runtime 是 containerd 或 CRI-O。[Kubernetes Container Runtime Interface](https://kubernetes.io/docs/concepts/containers/cri/)

再往下，OCI runtime 需要建立真正的 Linux process isolation：

- PID namespace 決定 process tree 看見什麼；
- mount namespace 決定 filesystem view；
- network namespace 決定 interface、route、socket namespace；
- cgroup 決定 CPU、memory、I/O 等 resource control；
- capabilities / seccomp / LSM 決定 process 可以做什麼；
- overlayfs 或其他 snapshotter 決定 image root filesystem 如何被組合。

也就是說，**Kubernetes 沒有發明 container isolation；它是在大規模 cluster 上協調 Linux 已經存在的 kernel mechanisms。**

這個邊界非常重要。

因為所有抽象在最後都會落到 kernel，而效能與隔離的真實行為也在那裡決定。

## 「4 CPU」到底是什麼？這就是抽象開始漏出物理世界的地方

看一段非常普通的 spec：

```yaml
resources:
  requests:
    cpu: "4"
  limits:
    cpu: "4"
```

從 API 層看，這只是一個 resource quantity。

但如果我們問一個 HPC engineer 真正在意的問題：

**這是不是代表我的 APR job 得到四顆專屬 physical cores？**

答案不是。

一般 Kubernetes CPU request 主要影響 scheduling 與 CPU share；CPU limit 最後會落到 Linux cgroup 的 CPU bandwidth control。cgroup v2 提供 `cpu.weight`、`cpu.max` 等介面，kubelet/runtime 透過 cgroup hierarchy 把上層 resource semantics 映射到 kernel。[Linux cgroup v2](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)｜[Kubernetes cgroup v2](https://kubernetes.io/docs/concepts/architecture/cgroups/)

但 kernel 還有更多實體問題：

- 這四個 logical CPUs 是否共享 SMT sibling？
- process 是否會在 cores 間 migrate？
- LLC 是否與其他 workload 共享？
- memory allocation 在本地 NUMA node 還是 remote socket？
- NIC / GPU 掛在哪個 PCIe root complex？
- memory bandwidth 是否已被鄰居飽和？

因此：

`4 vCPU-equivalent entitlement ≠ 4 isolated physical cores with local memory`

如果要提高 determinism，就要再進一步使用 CPU Manager static policy、cpuset、Topology Manager、NUMA-aware device placement 等機制。

這也說明為什麼 Kubernetes 的 abstraction 本身不是問題，**真正的問題是平台是否知道 abstraction 在哪裡開始不夠精確。**

對微服務來說，平均 CPU capacity 可能已足夠。

對 Innovus、Fusion Compiler、STA、OPC、TCAD、MPI 或 latency-sensitive inference，cache locality、NUMA 與 memory bandwidth 可能比「CPU 數量」更重要。

## 這也是為什麼 HPC 的 performance truth 往往不在 control plane

再看另一個例子。

一個 distributed training Pod 被 scheduler 放到「有 GPU、有 RDMA NIC」的 node 上，不代表它就會快。

真實資料可能走：

`GPU HBM`
→ `NVLink / NVSwitch`
→ `PCIe`
→ `NIC DMA`
→ `RoCE / InfiniBand fabric`
→ `remote NIC`
→ `remote GPU`

如果 GPU 與 NIC 不在同一個 NUMA / PCIe locality，資料可能先跨 socket interconnect。

如果 SR-IOV VF 配錯 NUMA node，CPU polling thread 可能跑在另一顆 socket。

如果 RoCE fabric 出現 congestion，PFC / ECN / congestion-control 行為會直接影響 collective tail latency。

如果 fallback 成 TCP，整條 data path 的 CPU involvement、copy 與 latency 特性又不同。

scheduler 可以選 node，但它不能取消 PCIe topology，也不能讓網路 queueing 不存在。

EDA storage 也是同樣道理。

假設一個 APR flow 掛載 NFS，storage vendor 告訴你 aggregate bandwidth 有 100 GB/s。

這不代表 flow 一定快。

如果 workload 是數百萬個小檔案：

`open → lookup → getattr → close`

真正瓶頸可能在 metadata operations、directory lookup、NFS RPC latency、server-side lock / inode pressure，而不是 bulk throughput。

另一種 workload 可能大量 mmap 大檔，瓶頸變成 page fault、page cache reclaim、writeback。

如果 backend 是 SAN block device，再加上 XFS/ext4，問題又轉成 block queue、multipath、filesystem metadata 與 page cache。

所以一句「我們 storage 很快」沒有意義。

必須問：**哪一條 I/O path？哪一種 operation mix？哪一層正在排隊？**

<figure>
  <img src="/assets/images/k8s/k8s-hpc-control-data-boundary.svg" alt="Kubernetes control plane 與 HPC node/kernel/data path 的分界" style="max-width:100%;height:auto;">
  <figcaption>圖 3｜Kubernetes 可以控制 placement、lifecycle 與 policy，但 HPC throughput / jitter 多數在 kernel 與 hardware data path 中形成。依據 <a href="https://kubernetes.io/docs/concepts/overview/components/">Kubernetes Components</a>、<a href="https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html">Linux cgroup v2</a>、<a href="https://slurm.schedmd.com/overview.html">Slurm architecture</a> 的責任邊界重繪整理。</figcaption>
</figure>

這張圖其實可以用一句話概括：

**Control plane 決定「應該怎麼安排」，data plane 決定「實際跑得多快」。**

一個成熟的 HPC platform 必須同時理解兩者。

## 所以「Kubernetes 能不能跑 HPC」本身就是錯的問題

幾乎所有 HPC workload 都可以被包進 container，也幾乎都可以想辦法被 Kubernetes 啟動。

但這沒有回答真正的工程問題。

更好的問題是：

**Kubernetes 能不能在不破壞 workload 最重要的 resource semantics 之下，帶來更高的 control-plane leverage？**

對不同 workload，答案完全不同。

| Workload | 真正稀缺資源 | 關鍵約束 | Kubernetes 單靠 Pod 是否足夠？ |
| --- | --- | --- | --- |
| Web service | CPU / memory / replica | availability、autoscaling | 通常接近足夠 |
| GPU inference | GPU、HBM、latency | batching、GPU partition、NUMA/NIC | 需要 device/topology awareness |
| Large training | GPU + NIC + topology | gang start、NCCL/RDMA、checkpoint | 不夠，需要 workload-aware scheduling |
| SYN / STA | CPU、memory、license | license token、shared FS、runtime variance | 不夠 |
| APR | memory、CPU locality、I/O | NUMA、scratch、metadata、license | 明顯不夠 |
| Foundry simulation | CPU/GPU cluster、fabric、storage | MPI/RDMA、parallel FS、deadline | 需要 HPC semantics |

這也是為什麼 Kubernetes 與 Slurm / LSF 的關係，不應被簡化成 replacement。

在很多 semiconductor environment，更實際的架構可能是：

`domain control plane / API / policy / artifact lineage`
→ `admission / dependency / desired state`
→ `execution backend`

而 execution backend 可以同時存在：

`Kubernetes Job | LSF | Slurm | bare metal | specialized appliance`

這時 Kubernetes 式架構的價值不是「把所有東西變成 Pod」，而是建立一個一致的 control model。

## 為什麼 AI 比 EDA 更容易先走到這一步？

因為兩者的歷史包袱不同。

近代 AI infrastructure 大量是在 GPU cluster 成長過程中重新建置。GPU、checkpoint、dataset、serving endpoint、autoscaling、job admission，本來就適合 API-driven orchestration。

雖然 large-scale training 會遇到非常傳統的 HPC 問題——gang scheduling、RDMA、topology、checkpoint、straggler——但平台本身可以從一開始就把 container、Kubernetes、GPU operator、CNI、CSI、Kueue / workload APIs 一起設計。

EDA 則不一樣。

很多 production environment 已經有成熟路徑：

`Tcl / Perl / Makefile`
→ `LSF / batch farm`
→ `NFS / SAN`
→ `EDA executable`
→ `license server`
→ `reports / GDS / netlist / artifacts`

這條 path 可能運作了十年以上。

工具對 hostname、UID/GID、filesystem path、symlink、fork/exec、mmap、shared library、kernel version、license checkout、interactive GUI、local scratch 都可能存在隱含假設。

因此「containerize 成功」不等於「production migration 成功」。

真正值得做的是先找 control plane 能創造價值、但不需要立刻重寫 data plane 的位置。

例如：

- flow dependency 與 desired/current state；
- job intent 與 priority；
- artifact lineage；
- retry / recovery policy；
- heterogeneous execution backend；
- observability；
- resource / license admission；
- deadline-aware orchestration。

然後逐步決定哪些 workload 適合直接 Kubernetes native，哪些仍留在 LSF / Slurm。

## 2026 的 Kubernetes 正在證明：原始 Pod scheduling 模型確實不夠描述 HPC

這不是抽象推論。

Kubernetes v1.37 的 Workload-Aware Scheduling 已經把 Workload / PodGroup、gang scheduling 與 workload-aware preemption 推進到 Beta；對更複雜的多層 topology，還引入 CompositePodGroup。這些能力就是在回答 AI/ML 與複雜 batch workload「一個 Pod 一個 placement decision」不夠用的問題。[Kubernetes v1.37 Workload-Aware Scheduling](https://kubernetes.io/blog/2026/09/08/kubernetes-v1-37-advancing-workload-aware-scheduling/)

同一個版本中，Dynamic Resource Allocation 持續擴展對 GPU、NIC 等裝置的表達能力，DRA extended-resource support 已進入 GA。[Kubernetes v1.37 DRA Updates](https://kubernetes.io/blog/2026/09/03/kubernetes-v1-37-dra-updates/)

這些變化很有意思。

它們不是讓 Kubernetes「變得更 cloud native」，而是在讓它更懂 physical resources、group scheduling 與 topology。

換句話說，Kubernetes 越往 AI/HPC 深處走，就越必須重新面對 HPC 世界早已熟悉的問題。

Slurm 有 gang scheduling、backfill、topology-aware resource selection、task affinity；Kubernetes 現在也逐步補上 workload group、topology-aware scheduling、device allocation。

兩條路正在靠近，但它們仍從不同 abstraction 起點出發。

## 真正值得研究的是：Control plane 應該停在哪裡？

到這裡，Kubernetes 的核心輪廓就清楚很多了。

它不是神奇地把 hardware heterogeneity 消失。

它也不是比 LSF / Slurm 更聰明的一顆 scheduler。

它真正強的地方，是提供一套可以持久化 intent、觀察 current state、讓多個 controllers 持續收斂、並且可以被擴充的 control-plane substrate。

但一旦 workload 真正開始執行，世界立刻回到物理限制：

`CPU scheduler`
`NUMA`
`cache`
`page fault`
`block queue`
`NFS RPC`
`SAN path`
`TCP congestion`
`RDMA queue pair`
`NIC IRQ`
`PCIe topology`

成熟的平台不是想辦法把這些細節藏掉，而是知道**哪些細節可以抽象，哪些必須被提升成 scheduler 與 control-plane 可理解的 constraint。**

這也是這個系列接下來要一路回答的問題。

我們會沿著真正的 execution path 往下：

`Pod YAML`
→ `API server`
→ `etcd / watch`
→ `controller / scheduler`
→ `kubelet`
→ `CRI / containerd / runc`
→ `namespace / cgroup`
→ `Linux scheduler / NUMA / VM`
→ `VFS / page cache / block layer`
→ `TCP / eBPF / RDMA / NIC`
→ `NFS / SAN / NVMe / parallel filesystem`
→ `AI / EDA / Foundry distributed workload`

下一篇會選擇最直接的一條路：**一份 Pod YAML 到底如何變成 Linux 上真正存在的一群 processes。**

我們會從 API request 開始，依序追過 etcd state、scheduler binding、kubelet sync loop、CRI、containerd、OCI runtime，最後看到 namespace、cgroup 與 process 是怎麼真的出現在 kernel 裡。

走完這條 path 之後，Kubernetes 就不再是「一組雲端名詞」，而是一個可以從 API 一路 debug 到 kernel 的系統。
