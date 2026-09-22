---
layout: post
title: "Kubernetes 創始篇：它不是更好的 Batch Scheduler，而是一個把 Desired State 變成 Cluster Reality 的 Control Plane"
date: 2026-09-22 13:40:00 +0800
author: Scott Yo-Ru Chen
domain: eda
categories: eda
description: "理解 Kubernetes 的第一步不是背 Pod、Service、Deployment，而是看懂它把『我要什麼』與『機器現在是什麼』分離，透過 API、controller、scheduler、kubelet 與 Linux kernel 持續 reconciliation。對 AI、EDA、IC design、Foundry/HPC，真正的問題也因此不是要不要用 K8s，而是 K8s 應該控制到哪一層、哪些 data path 必須直接尊重 kernel、RDMA、SAN/NFS 與硬體拓撲。"
---

如果把 Kubernetes 理解成「可以取代 LSF / Slurm 的 container scheduler」，後面幾乎所有技術判斷都會偏掉。

**Kubernetes 最核心的發明不是 Pod，也不是 scheduler，而是把整個 cluster 變成一個持續 reconciliation 的 distributed control plane。** 使用者宣告 desired state；API server 把它變成可被觀察、版本化的 cluster state；controllers 不斷比較 desired state 與 current state；scheduler 只負責其中一個問題——「這個 Pod 應該去哪一台 node」；真正讓 process 跑起來、限制 CPU/memory、建立 network namespace、掛載 storage 的，最後仍然是 kubelet、container runtime 與 Linux kernel。

這件事對一般 web service 已經重要，對 AI、EDA、IC design、Foundry/HPC 更重要，因為這些工作負載會直接碰到 Kubernetes 抽象層的邊界：CPU pinning、NUMA、GPU/NIC locality、RDMA、MPI collective、license token、NFS metadata storm、SAN queue depth、local NVMe scratch、page cache、memory bandwidth、gang scheduling、checkpoint/restart。**Kubernetes 可以描述與協調這些條件，但不能把物理限制抽象掉。**

本系列因此不從「如何寫 Deployment YAML」開始，而從 Kubernetes 到底在控制什麼開始。

<figure>
  <img src="https://kubernetes.io/images/docs/components-of-kubernetes.svg" alt="Kubernetes 官方 cluster components 架構圖" style="max-width:100%;height:auto;">
  <figcaption>圖 1｜Kubernetes 官方 cluster components：control plane 由 API server、etcd、scheduler、controller manager 等元件組成；worker node 上由 kubelet、container runtime 等把宣告轉成實際 workload。來源：<a href="https://kubernetes.io/docs/concepts/overview/components/">Kubernetes Documentation — Kubernetes Components</a>。</figcaption>
</figure>

## 第一個關鍵：Scheduler 不是 Kubernetes 的中心

傳統 HPC 使用者很自然會先看 scheduler，因為在 LSF / Slurm 世界裡，最明顯的操作界面就是 submit job、排隊、分配資源、啟動程式。

Slurm 官方把自己的核心功能描述得很直接：分配 compute resource、啟動與監控 parallel job，以及仲裁 pending work 的資源競爭；它還有 reservation、backfill、topology-aware placement、gang scheduling 與 accounting 等典型 HPC 能力。[Slurm 官方 Overview](https://slurm.schedmd.com/overview.html)

Kubernetes scheduler 的責任其實窄很多。官方 Scheduling Framework 將一次 Pod placement 拆成 scheduling cycle 與 binding cycle：前者選 node，後者把決策寫回 cluster；中間可以經過 filter、score、reserve、permit、pre-bind、bind 等 extension points。[Kubernetes Scheduling Framework](https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/)

真正不同之處是：**即使 scheduler 完全停止，Kubernetes 仍然有一大半核心語義存在。**

已經跑著的 Pod 不會因 scheduler 停止就立刻消失；Deployment controller 仍然可以觀察 replica 是否不足；kubelet 仍然可以維持 node 上既有 workload；API server 與 etcd 仍然保存 cluster desired/current state。scheduler 是 control plane 的一個 controller-like decision maker，而不是整個系統的唯一大腦。

這種切割很重要，因為大規模平台最後一定會遇到「不同決策有不同時間尺度」：

- scheduler：毫秒到秒，決定 Pod 放哪裡；
- controller：秒到分鐘，確保 replica、Job、Node、Volume 等狀態收斂；
- autoscaler：分鐘級，決定是否增減 node；
- HPC queue/admission：可能是分鐘到小時，決定昂貴資源何時允許工作進場；
- capacity planner：週到季，決定機房、GPU、storage、network 是否要擴容。

把所有邏輯塞進單一 scheduler，規模一大就會變成無法演化的 central brain。Kubernetes 反而把「決策」拆成很多可重試、可獨立失敗、靠共享 API state 協調的 control loops。

## Desired state 與 current state 才是核心抽象

Kubernetes 官方對 controller 的定義很清楚：controller 是持續運作的 control loop，觀察 cluster state，並讓 current state 朝 desired state 靠近；API object 的 `spec` 通常描述 desired state。[Kubernetes Controllers](https://kubernetes.io/docs/concepts/architecture/controller/)

例如你宣告：

```yaml
apiVersion: apps/v1
kind: Deployment
spec:
  replicas: 4
```

重點不是「執行 create 4 pods 這個命令」。

真正的語義是：**從現在開始，系統應該持續維持 4 個符合條件的 replica。**

如果某台 node 掛掉、Pod 被 kill、container crash，系統不是回頭重播一串 shell commands；controller 重新觀察現況，只看到 `desired=4, current=3`，於是再次產生一個 Pod。這就是 level-triggered reconciliation。

這與許多傳統 flow automation 的差異很大。Makefile、Tcl、Perl、shell script 通常描述「現在執行哪些步驟」；Kubernetes object 更接近描述「系統最終應維持什麼狀態」。

<figure>
  <img src="/assets/images/k8s/k8s-reconciliation-path.svg" alt="Kubernetes desired state 到 Linux execution substrate 的 reconciliation path" style="max-width:100%;height:auto;">
  <figcaption>圖 2｜Kubernetes reconciliation path。使用者寫入 desired state 後，API/etcd 保存 cluster state；controllers 與 scheduler 產生後續決策；kubelet 最後把 node state 向目標收斂。依據 <a href="https://kubernetes.io/docs/concepts/architecture/controller/">Kubernetes Controllers</a>、<a href="https://kubernetes.io/docs/concepts/overview/components/">Kubernetes Components</a> 與 <a href="https://kubernetes.io/docs/concepts/scheduling-eviction/scheduling-framework/">Scheduling Framework</a> 重繪整理。</figcaption>
</figure>

這也解釋了 Kubernetes 為什麼特別適合做「platform control plane」：只要某個外部系統可以被觀察、被驅動、狀態可以回報，就能被包進 reconciliation loop。cloud load balancer、volume、network attachment、GPU allocation，甚至未來 EDA flow、license pool、artifact execution backend，都可以用類似模式整合，而不要求所有東西都變成 container。

## API server 與 etcd：不是資料庫 CRUD，而是整個控制面的共享事實

Kubernetes control plane 幾乎所有元件都繞著 kube-apiserver 運作。官方架構把 API server 定義為 control plane 的 front end，而 etcd 是保存所有 API server data 的 consistent、highly available key-value store。[Kubernetes Components](https://kubernetes.io/docs/concepts/overview/components/)

這裡最容易低估的是 watch。

如果每一個 controller 都每秒掃描整個 cluster：

`LIST all Pods → compare → sleep → LIST again`

規模一大，API server、etcd 與 controller 自己都會被 polling 壓垮。Kubernetes 使用 resourceVersion、watch、informer/cache 等機制，把大量 controller 變成「先取得 snapshot，再接收增量變化」。

因此一個成熟 controller 的運作模型通常是：

`watch event → enqueue key → read desired/current state → reconcile → update status → retry if needed`

這不是 message queue 驅動的 one-shot workflow；event 只是提醒「某個 object 可能需要重新檢查」。真正的 source of truth 仍然是 API state。即使 event 重複、順序不理想、controller crash 後重啟，只要 reconcile 是 idempotent，就能重新從 state 推導下一步。

這是 Kubernetes 能承受 component restart、network glitch 與 transient failure 的核心原因之一。

## Scheduler 做完決策後，真正的世界才開始

假設 scheduler 最後決定：

`pod-123 → node-42`

這只是一筆 control-plane decision。

node-42 上的 kubelet 看到 Pod 已經被綁定到自己後，才透過 CRI 與 container runtime 溝通。Kubernetes 官方定義 CRI 為 kubelet 與 runtime 間的主要 gRPC protocol；目前 Kubernetes 需要相容的 CRI runtime，例如 containerd 或 CRI-O。[Kubernetes CRI](https://kubernetes.io/docs/concepts/containers/cri/)

runtime 再往下透過 OCI runtime 等機制建立 Linux process isolation。到了 kernel 層，所謂「container CPU limit」最終不是 Kubernetes 特有技術，而是 cgroup；network isolation 依靠 network namespace；filesystem view 依靠 mount namespace；process view 依靠 PID namespace。

以 CPU limit 為例，Pod YAML 裡可能只寫：

```yaml
resources:
  limits:
    cpu: "4"
```

但 Linux 最後需要的是 cgroup scheduler 可以執行的控制值。cgroup v2 用 `cpu.max` 等介面限制 CPU bandwidth；Kubernetes kubelet 與 runtime 必須正確建立 cgroup hierarchy 才能落實 Pod/container resource control。[Linux Kernel cgroup v2](https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html)｜[Kubernetes cgroup v2](https://kubernetes.io/docs/concepts/architecture/cgroups/)

這裡就是整套系列後面會一路往下鑽的地方：

`resources.cpu → cgroup → Linux scheduler → runqueue → physical core → shared cache → NUMA memory`

所以「Pod request 4 CPU」與「程式得到 4 顆沒有干擾、memory-local 的 physical cores」完全不是同一件事。

對 web service，也許平均 throughput 還能接受；對 Innovus、Fusion Compiler、STA、OPC simulation、MPI 或 GPU training，這種差異可能直接變成 20%、50%，甚至數倍的 runtime variance。

## Kubernetes 無法抽象掉 HPC 的 data path

HPC workload 的效能通常不由 control plane 決定，而由資料真正怎麼走決定。

例如一個 distributed training job：

`GPU HBM → NVLink/NVSwitch → PCIe → NIC → RDMA/RoCE fabric → remote GPU`

一個大型 APR job 可能主要在：

`CPU → LLC → NUMA DRAM → page cache → NFS/SAN → shared filesystem metadata`

scheduler 可以盡量把 GPU、NIC、CPU 放在正確 node；Topology Manager 可以協助 NUMA alignment；Multus/SR-IOV 可以提供更直接的 NIC access；CSI 可以幫你 mount NFS/SAN volume。

但 Kubernetes 並不會因此讓 NFS metadata latency 消失，也不會幫 RoCE fabric 自動消除 congestion，更不會讓一個跨 socket 的 memory access 變成本地 DRAM。

<figure>
  <img src="/assets/images/k8s/k8s-hpc-control-data-boundary.svg" alt="Kubernetes control plane 與 HPC node/kernel/data path 的分界" style="max-width:100%;height:auto;">
  <figcaption>圖 3｜Kubernetes 決定 placement、lifecycle 與 policy；實際 HPC throughput/jitter 多數發生在 kernel 與 hardware data path。依據 <a href="https://kubernetes.io/docs/concepts/overview/components/">Kubernetes Components</a>、<a href="https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html">Linux cgroup v2</a>、<a href="https://slurm.schedmd.com/overview.html">Slurm architecture</a> 的責任邊界重繪整理。</figcaption>
</figure>

這就是我認為評估 Kubernetes 是否適合 EDA / Foundry 時最重要的判準：

**不要問「Kubernetes 能不能跑這個 workload」；幾乎都能。應該問「它能不能在不破壞 workload 最重要的 locality、I/O、license、queueing、failure semantics 之下，提供更好的 control-plane leverage」。**

## 為什麼 AI 比 EDA 更早大規模接受 Kubernetes

這裡有一個很值得觀察的結構差異。

AI platform 天生比較容易拆成 API-driven resource orchestration：GPU、Job、checkpoint、dataset、service endpoint、autoscaling。雖然 distributed training 對 RDMA/topology 很敏感，但大量 AI infrastructure 本來就是近年重建，可以直接讓 container、Kubernetes、GPU operator、DRA、Kueue 等能力一起成長。

EDA / IC design 的 installed base 不同。

很多 production flow 已經在：

`Tcl / Perl / Makefile → LSF → NFS / SAN → commercial EDA tools → license server`

上面累積十幾二十年。工具對 hostname、filesystem path、shared cache、license checkout、process tree、interactive GUI、local scratch、fork/exec 行為甚至 kernel version 都可能有隱含假設。

所以 EDA 的最佳遷移路徑不一定是「把 LSF 全部換成 Kubernetes」。

更合理的架構可能是：

`Kubernetes / domain control plane → policy / dependency / artifact / desired state`

然後 execution backend 仍可以是：

`LSF | Slurm | Kubernetes Job | bare metal | specialized farm`

也就是讓 Kubernetes 式的 control-plane semantics 管「要完成什麼、依賴什麼、目前做到哪裡、失敗後如何恢復」，而不是強迫所有 execution data plane 立刻改成 Pod。

這也是本系列最後會回到 R2G / semiconductor compute platform 的地方。

## 2026 的 Kubernetes 正在往 HPC workload semantics 靠近

截至 2026 年 9 月，Kubernetes v1.37 已把 Workload-Aware Scheduling 的多個能力往前推，包括 PodGroup / gang scheduling、workload-aware preemption，以及針對複雜 heterogeneous workload 的 CompositePodGroup 等方向；DRA 也持續擴充 GPU、NIC 等非傳統 CPU/memory resource 的表達能力。[Kubernetes v1.37 Workload-Aware Scheduling](https://kubernetes.io/blog/2026/09/08/kubernetes-v1-37-advancing-workload-aware-scheduling/)｜[Kubernetes v1.37 DRA](https://kubernetes.io/blog/2026/09/03/kubernetes-v1-37-dra-updates/)

這說明一件事：Kubernetes 原始的「一個 Pod 一個 placement decision」模型，本來就不完整描述大型 AI/HPC job。當 workload 需要 256 個 GPU、32 台 node、特定 NVLink/RDMA topology，而且任何一部分沒到齊整個 job 都不能有效開始時，scheduler 必須理解「workload group」而不是只理解個別 Pod。

換句話說，Kubernetes 並沒有消滅 HPC scheduler 的問題；它正在逐步吸收那些問題。

## 這個系列真正要回答的問題

後續不會把 Kubernetes 當成抽象名詞堆疊。

我們會沿著真正的 execution path 往下：

`Pod YAML`
→ `API server / etcd / controller`
→ `scheduler`
→ `kubelet / CRI / containerd / runc`
→ `namespace / cgroup`
→ `Linux scheduler / NUMA / VM / page cache`
→ `VFS / block layer / NVMe / NFS / SAN / Lustre`
→ `TCP / eBPF / SR-IOV / RDMA / NIC queues`
→ `rack / fabric / cluster`
→ `AI / EDA / Foundry distributed workload`

每一層都要回答同一件事：**上層 abstraction 最後落到哪個 kernel/hardware mechanism？那個 mechanism 的限制又如何反過來約束上層 control plane？**

下一篇會直接走完整條 Pod creation path：從一份 YAML 寫進 API server 開始，經過 etcd watch、scheduler binding、kubelet SyncPod、CRI，到 container runtime 最後呼叫 OCI runtime，在 Linux 上真正建立 process、namespace 與 cgroup。等這條路走完，Kubernetes 才不再是一堆名詞，而會變成一個可以逐層 debug 的系統。
