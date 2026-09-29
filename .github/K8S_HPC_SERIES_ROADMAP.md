# Kubernetes / HPC Systems：從入門到 production architecture

本檔是 `rightson/rightson.github.io` 這個系列唯一的選題、前置依賴與完成狀態來源。公開文章遵守 repo 最新 `AGENTS.md`；本檔只管課程，不作公開文章。每三天於 Asia/Taipei 08:00 啟動一次寫作與發布流程；啟動時間不是文章的建立或上線時間。

## 目前狀態與接續規則

- **新課程從 K001 開始，全部未完成。** 舊系列 #001–#005 曾在 `_posts/`，#006 曾在 `_drafts/`；六篇及其本地 SVG 已移至 `_archive/k8s-hpc/`，不屬於新課程的已完成篇目，不提供公開先修連結。
- 若前一篇已有提交而 Pages／正式頁尚未驗證，先完成驗證或修復；不得跳到下一篇。若已提交同一篇，先比對 source、build、deploy、public content，不建立副本。
- 依下列順序選第一個前置知識已教完的未完成篇目。篇號是穩定 ID；插入必需先修時使用新 ID，明示其前置關係，不重新編號既有篇目。
- `[x]` 的唯一條件：文章、圖檔已在預設分支；Pages build 與 deploy 成功；正式 URL 的標題與正文已核對。各篇完成時在該行補 `_posts/...` 和實際 public URL。未全數驗證只記錄精確狀態，不打勾。
- 每次執行先讀最新 `AGENTS.md`、本檔、`_config.yml`、最近同系列及相關 `_posts/`，核對遠端 head、同日／同篇／同 slug 與既有草稿。寫入前重新取得目標 blob SHA，保留並行修改；不 force-push。

## 教學契約

讀者只需一般軟體工程背景。新概念第一次出現，先給可用的 mental model、具體例子和邊界；後續再揭開實作。不能把「最後會學到 kernel／RDMA」當作第一篇就使用其術語的理由。必要時說「此處先視為 X，後文再拆」；模型可簡化，事實不能錯。

每篇只打通當前的一個問題：**具體矛盾 → 直覺 → 最小模型 → 當前深度的機制 → 完整例子 → 模型邊界 → 下一個自然問題**。這是編輯檢查，不作固定小標，也不在正文提寫作法。前十篇優先建立系統全貌及元件關係；不要求讀者已知 namespace、cgroup、Raft、NUMA、RDMA。

| 階段 | 主要能力 | 正文參考長度與例子 |
| --- | --- | --- |
| 入門 K001–K013 | 直覺、基本名詞、單機與叢集模型 | 約 3,000–5,000 中文字；至少一個從起點走到終點的例子 |
| 中階 K014–K031 | YAML 到 process、狀態轉移、API 與實作的關係 | 約 4,000–6,000 字；至少兩個例子與一個具體故障 |
| 進階 K032–K064 | kernel、queue、資料路徑、拓撲與可量化效能 | 約 5,000–8,000 字，深題可更長；至少兩個例子 |
| 精通 K065–K081 | workload 到硬體的跨層正確性、性能與運維取捨 | 依問題所需；比較合理方案、失效恢復、成本與可驗證指標 |

長度是參考，不為湊字數引入尚未具備先修的概念。入門文也要準確；進階文不能省掉已建立的關鍵前提。每篇原則上有 2–5 張服務當前理解的技術圖（入門可用 lifecycle／system overview；後期用 packet、I/O、queue、topology、failure timeline）。每圖有 alt、caption、來源；自繪標「依據 XXX 整理／重繪」並附一手連結。不得把未渲染 Mermaid 當圖。正文重要技術事實就近引官方文件、原始論文或規格；區分官方事實、論文／廠商結果、假設算例及作者推導。發布前核對會變動的版本與 API。

### Phase 0 — 一台電腦如何執行程式

完成後能說出 process、CPU、memory、file、socket 為何是後續容器與叢集的基本單位。只教理解 Kubernetes 必需的 OS 基礎。

- [ ] K001. 啟動一個程式之後，作業系統建立了什麼？process、thread、生命週期與最小 trace。
- [ ] K002. 一顆 CPU 為什麼能輪流執行許多 process？core、時間片與 scheduler 的初步直覺。
- [ ] K003. 程式讀寫的記憶體與檔案各在哪裡？address space、RAM、filesystem 的可用模型。
- [ ] K004. 兩個程式怎麼傳訊息？同機 process、socket、跨機網路與隔離需求。

### Phase 1 — Kubernetes 解的叢集問題

先看懂整台機器；遇到 kernel 或共識細節只指出邊界，不展開。

- [ ] K005. 一台機器用指令能跑，幾百台為什麼不能只靠 SSH 與 script？失敗、重試與人力成本。
- [ ] K006. 從「執行命令」到「描述期望」：desired state、observed state 與收斂。
- [ ] K007. Pod、Node、Deployment、Service 各代表什麼？以一個小服務的整體生命週期建立模型。
- [ ] K008. Control plane 與 Node 如何分工？API server、狀態儲存、controller、scheduler、kubelet 的第一張全貌圖。
- [ ] K009. 一台 Node 故障時，誰發現、誰補救、哪些事情 Kubernetes 不能保證？回看宣告式模型的邊界。

### Phase 2 — 一份 YAML 如何成為 Running Pod

逐層追同一個最小範例；每篇回答「上一層已完成，下一層為什麼還沒發生」。不要一次講完所有內部實作。

- [ ] K010. `kubectl apply` 到底送出了什麼？YAML、API object、spec、status、基本驗證。
- [ ] K011. API server 接受 object 後存在哪裡？持久狀態與 etcd 的初階模型；Raft 延後。
- [ ] K012. Deployment 為什麼會產生 Pod？controller 讀狀態與反覆收斂。
- [ ] K013. 誰決定 Pod 去哪個 Node？request、可行性、選擇與 bind 的入門模型。
- [ ] K014. Node 收到 Pod 後，誰真正啟動它？kubelet、CRI、runtime 的責任邊界。
- [ ] K015. 從 YAML 到 Running：沿同一個 Pod 追 API、儲存、controller、scheduler、kubelet、process；用事件與狀態診斷卡住的位置。

### Phase 3 — Container 是 Linux process

前提：K014–K015。先介紹共享 kernel，再拆單一隔離機制；不把 container 當 VM。

- [ ] K016. Container 與 VM 各隔離什麼？image、runtime、OCI 與 Linux process。
- [ ] K017. 兩個 container 為何看到不同的 process tree？PID namespace、init、signal。
- [ ] K018. 為何看到不同檔案樹？mount namespace、rootfs、image layers、overlayfs。
- [ ] K019. 為何有不同網路視角？network namespace、interface 與路由的初階模型。
- [ ] K020. 誰限制一組 process 的資源？cgroup v2 hierarchy 與 Pod/container 邊界。
- [ ] K021. `kubectl exec`、container exit、Pod restart 是哪些 process 與狀態變化？以可觀察 trace 收束。

### Phase 4 — CPU 與 memory 從承諾到硬體

前提：process、scheduler、cgroup。此階段才解釋「4 CPU」與 physical core 的差距。

- [ ] K022. CPU request/limit 在 scheduler 與 Node 各代表什麼？以 YAML → accounting → cgroup 為例。
- [ ] K023. `cpu.weight`、`cpu.max`、throttling：份額與上限為何產生不同延遲。
- [ ] K024. core、logical CPU、SMT 與 runqueue：Linux CFS/EEVDF 怎麼分配可執行時間。
- [ ] K025. CPU affinity、cpuset、CPU Manager：何時能要求專用邏輯 CPU，何時仍有干擾。
- [ ] K026. NUMA：CPU socket、local/remote memory 與 locality 的第一個量化例子。
- [ ] K027. virtual memory、page table、TLB、page fault：程式存取位址如何落到實體記憶體。
- [ ] K028. memory request/limit、cgroup reclaim、OOM：排程允諾與實際記憶體壓力。
- [ ] K029. THP、hugepages 與 memory bandwidth：吞吐與尾延遲的取捨。
- [ ] K030. page cache：讀檔為什麼常先碰 RAM；它如何計入記憶體壓力。
- [ ] K031. 從 CPU／memory 指標診斷同一工作在兩台 Node 時間不同；建立 topology 與 contention 邊界。

### Phase 5 — Networking：從 Pod 到 NIC

前提：socket、network namespace。由一次 `send()` 逐步向下走，直到能解釋 100 GbE 與應用吞吐的落差。

- [ ] K032. 兩個 Pod 怎麼互送資料？Pod IP、Service、DNS 與基本封包路徑。
- [ ] K033. socket、TCP/IP、封包與連線：`send()` 到對端 `recv()` 的最小模型。
- [ ] K034. veth、bridge、路由與 CNI：Pod 網卡如何接上 Node 網路。
- [ ] K035. Service 轉送與 NAT：iptables／IPVS 的差異及 conntrack 邊界。
- [ ] K036. overlay、underlay 與 MTU：跨 Node 路徑的額外封裝成本。
- [ ] K037. eBPF、XDP、tc：替代資料路徑的 hook、map 與可驗證限制。
- [ ] K038. NAPI、softirq、NIC queue、RSS/RPS/XPS：封包進出時 CPU 在做什麼。
- [ ] K039. TCP buffer、BDP、congestion control、ECN：高速網路的端到端吞吐與延遲。
- [ ] K040. SR-IOV、DPDK 與 passthrough：省掉哪些路徑，換來哪些隔離與操作代價。
- [ ] K041. RDMA／RoCE：QP、CQ、MR、loss/congestion 與 TCP 路徑的適用邊界。

### Phase 6 — Storage：從 file 到共享資料

前提：file、memory 與基本 network。先讀懂單機 `read()`，才談 CSI、SAN、NFS 與平行檔案系統。

- [ ] K042. file descriptor、VFS、dentry、inode：程式打開檔案時查找了什麼。
- [ ] K043. page cache、buffered I/O、writeback、`fsync()`：快與持久性的分界。
- [ ] K044. filesystem、block layer、blk-mq、NVMe queue：一次 I/O 如何到本地裝置。
- [ ] K045. Kubernetes volume、PVC、CSI 與 topology binding：資料生命週期和 Pod 生命週期如何分開。
- [ ] K046. NFS：RPC、metadata、client cache、lock 與共享 POSIX 工作負載。
- [ ] K047. SAN、iSCSI、Fibre Channel、multipath：遠端 block 裝置的路徑與失效。
- [ ] K048. NVMe-oF over TCP／RDMA：裝置協定、fabric 與 queue 的界線。
- [ ] K049. Ceph、Lustre、Spectrum Scale／GPFS、BeeGFS：metadata 與資料平行化的不同設計。
- [ ] K050. small files／metadata storm：頻寬充足時大量 EDA 檔案仍慢的原因。
- [ ] K051. local NVMe scratch、shared storage、checkpoint：容量、再現性與恢復成本。

### Phase 7 — Distributed systems 與 Kubernetes 的失效模型

前提：已追過單 Node 和 API 到 process。通用理論可連至獨立 Distributed Systems 系列；此處聚焦 Kubernetes/etcd 行為。

- [ ] K052. state、identity、duplicate event 與 idempotency：reconcile 為何能安全重試。
- [ ] K053. watch、cache、backoff、workqueue：觀測與執行之間的延遲和壓力。
- [ ] K054. lease、leader election、fencing：誰能動作及舊 leader 的殘留風險。
- [ ] K055. etcd MVCC、Raft、quorum、compaction：持久化順序與故障恢復。
- [ ] K056. consistency、eventual convergence 與 status：使用者讀到的進度代表什麼。
- [ ] K057. checkpoint、backpressure、partition 與復原：重新回看整條控制鏈。

### Phase 8 — Scheduling：從 placement 到 HPC 作業

前提：resource model、topology 與叢集失效。用工作意圖推導，而非功能清單。

- [ ] K058. Node selection、Filter、Score、bind：scheduler 做了哪個承諾。
- [ ] K059. affinity、taint、topology spread、priority、preemption：可行性與偏好。
- [ ] K060. quota、fair-share、queues、admission：多團隊如何分配稀缺資源。
- [ ] K061. gang scheduling、PodGroup、Kueue、Volcano：多 Pod 同時起跑的條件。
- [ ] K062. backfill、reservation、license-aware scheduling：昂貴 HPC／EDA 資源的等待成本。
- [ ] K063. CPU／GPU／NIC locality 與跨 Node fabric topology：選對 Node 仍可能變慢。
- [ ] K064. Slurm、LSF、Kubernetes 對 batch 與 service 的責任邊界；比較可重現情境。

### Phase 9 — AI／GPU systems

前提：NUMA、NIC、RDMA、storage、gang scheduling。以一個 training job 的完整生命週期串接。

- [ ] K065. training job 從提交、admission 到 GPU allocation 的控制鏈。
- [ ] K066. PCIe、NVLink、GPU/NIC affinity 與 NUMA：裝置拓撲如何改變訓練時間。
- [ ] K067. NCCL、collectives、RDMA 與 network topology：同步成本與故障傳播。
- [ ] K068. data／tensor／pipeline／expert parallel：對排程與網路需求的不同形狀。
- [ ] K069. checkpoint/restart 與 storage path：算力利用率、可靠性與 I/O 成本。
- [ ] K070. inference serving：prefill/decode、併發、隔離、延遲與 GPU sharing。

### Phase 10 — EDA／IC design／Foundry HPC

前提：前述 CPU、network、storage、distributed systems、scheduling。公開案例不包含任何私有 PDK、RTL、log、客戶或未公開架構。

- [ ] K071. synthesis、APR、STA、DFT、simulation、regression、signoff 的工作形狀與產物。
- [ ] K072. Tcl／Perl／Makefile、RTL／netlist／SDC／UPF、report／log 如何形成可追溯 execution DAG。
- [ ] K073. license server、queue、huge-memory host 與 deadline：一個 APR job 的完整路徑。
- [ ] K074. NFS／SAN／local scratch 的 metadata、checkpoint 與 artifact lineage 取捨。
- [ ] K075. Foundry OPC／TCAD／extraction 與 IC design 負載何處能共享平台、何處需要隔離。
- [ ] K076. Kubernetes、Slurm、LSF、VM、bare metal 各管理哪一層？從明確約束推導 hybrid 或單一方案。

### Phase 11 — Production-scale architecture 與整體設計

前提：K001–K076 的模型能沿 execution path 連通。最後的文章以 production 故障、容量與成本檢驗設計。

- [ ] K077. control plane／data plane 分離、multi-cluster 與 failure domain。
- [ ] K078. topology-aware／workload-aware scheduling 與可重現 performance SLO。
- [ ] K079. observability：從 API、queue、kubelet、cgroup、NIC 到 storage 定位瓶頸。
- [ ] K080. reliability、security、capacity planning 與 operational cost 的共同約束。
- [ ] K081. 從零設計 semiconductor／AI／HPC production system：job submission → placement → execution → artifact → recovery 的完整設計與反證。

## 發文與回報

使用符合最新 `AGENTS.md` 的 front matter、單一 `domain: distributed-systems` 和 `categories: distributed-systems`；新文不公開署名。檔名 `_posts/YYYY-MM-DD-english-kebab-slug.md`，`date` 是 Markdown 首次實際寫入時間（Asia/Taipei）；引用與圖在同 commit。對變動中的 Kubernetes release、scheduler、DRA、CNI/CSI 或 Linux 行為，發文前查官方最新資料。先檢查標題骨架和近文去重，能 build 時本地 build；提交後回讀遠端 source、檢查 Pages build/deploy 與實頁標題／正文。失敗只修復，不跳題、不空 commit。

每次回報：篇號、標題、Phase、核心 mental model、repo path、commit SHA、正式 URL、deploy／正文驗證狀態、下一題及其新增的一層理解。若缺任一驗證項，只報已完成到哪一步。
