---
author: Scott Yo-Ru Chen
layout: post
title: "NVLink 6 真正的突破不是 3.6 TB/s，而是把故障恢復做成跨層控制迴路"
date: 2026-09-23 05:30:00 +0800
categories: networking nvlink resiliency distributed-systems
---

作者：Scott Yo-Ru Chen

我認為 NVLink 6 這一代最重要的變化，不是把 GPU-to-GPU bandwidth 從 1.8 TB/s 拉到 3.6 TB/s，而是 NVIDIA 開始把「故障恢復」視為一條從 PHY 一路延伸到 distributed runtime 的控制迴路。這個方向比單純增加頻寬更值得注意，因為當 72、數百甚至上千顆 accelerator 被綁成一個 scale-up domain，真正限制 goodput 的往往不再是 peak bandwidth，而是 rare error 被放大成 collective stall、process abort、model reload 甚至整個 rack drain 的機率。

9 月 15 日 NVIDIA 公布 NVLink 6 的 multi-layer resiliency 細節：PHY 端用 lightweight FEC、Physical Layer Retry（PLR）與 UPHY recovery，把大多數錯誤壓在 sub-millisecond；link layer 用 credit-based flow control（CBFC）避免 buffer overflow 後才補救；control plane 用 NMX 的 contain-and-drain 與 HA 隔離故障；再往上，NCCL elasticity、Dynamo Shadow Engine 與 CUDA checkpoint 處理已經穿透硬體邊界的 failure。[NVIDIA 的原始技術說明](https://developer.nvidia.com/blog/how-nvidia-nvlink-6-delivers-multi-layer-resiliency-for-ai-factories/)把這些機制放在同一張 recovery-time stack 裡。

真正值得研究的問題是：**當 interconnect 快到足以把數十顆 GPU 當成一顆邏輯 accelerator 時，network reliability 也必須跟著變成 compute semantics 的一部分。**

![NVLink 6 多層故障恢復時間尺度](/images/networking/2026-09-23/nvlink6-resiliency-stack.svg)

圖：作者整理；資料來源：[NVIDIA — How NVLink 6 Delivers Multi-Layer Resiliency for AI Factories](https://developer.nvidia.com/blog/how-nvidia-nvlink-6-delivers-multi-layer-resiliency-for-ai-factories/)

## 問題已經不是 BER，而是錯誤會被放大多少層

高速 SerDes 永遠不可能做到 bit error probability 為零。lane rate 提高、package trace 變長、connector 數量增加、熱梯度變大，signal margin 只會更難做。單一 bit error 本身通常不昂貴；昂貴的是它逃過最靠近 source 的修復層，最後變成 software-visible failure。

這裡可以用一個很簡單的模型理解：

`Expected lost work ≈ fault rate × failure amplification × recovery time`

傳統網路設計常把這三項拆開：PHY team 管 BER，switch team 管 packet，runtime team 管 process，scheduler 再處理 node failure。但在 tensor parallel、expert parallel 或頻繁 collective 的 workload 裡，這種分層邊界沒有真的消失。一次 link retrain 若讓 NCCL communicator 失效，後果可能不是幾個 microseconds 的 link interruption，而是幾分鐘的 model reload。

這正是 NVLink 6 的設計重點：把 recovery 放在**最便宜、最局部、最短時間尺度**的 layer 完成，只有該層真的無法處理，才向上升級。

NVIDIA 公開規格顯示，第六代 NVLink 在 Vera Rubin 上提供每顆 GPU 3.6 TB/s bidirectional bandwidth，NVL72 rack 合計 260 TB/s；NVLink Switch 還加入 130 TFLOPS 等級的 in-network compute，服務 reduction 與 multicast。[NVLink scale-up architecture](https://developer.nvidia.com/blog/nvidia-nvlink-the-scale-up-network-for-ai-factories/)同時把 rack-scale goodput 與 resiliency 放在同一個評估框架裡。這個連結很重要：頻寬愈高、同步愈緊，fault amplification 其實愈嚴重。

## 為什麼規模一上去，rare error 會變成常態

scale-up domain 的可靠度有一個很反直覺的地方：單一 link 可以非常可靠，但整個 domain 仍然可能很常看到事件。

如果把每條 link 的可見故障率粗略寫成 `λ`，同時存在 `N` 條獨立 link，而且任何一條故障都可能讓 workload stall，那麼 domain-level hazard rate 會近似隨 `N × λ` 增長。真實系統當然不是完全獨立：同一顆 retimer、switch tray、power rail、clock domain 或 thermal event 會造成 correlated failure，使情況更糟。這也是為什麼大型 AI system 不可能只靠提高單一元件 MTBF 解決問題。

真正有效的方法是降低 **failure amplification factor**。

假設一個 transient bit error 被 FEC 修掉，對 workload 的 cost 幾乎為零；同樣的 physical disturbance 若造成 link down，但由 PLR/UPHY 在 1 ms 內恢復，代價仍然只是短暫 latency bubble；若進一步使 communicator abort，cost 立刻跳到 seconds 或 minutes。換句話說，同一個 physical root cause，因為 containment layer 不同，經濟成本可能跨越六個數量級。

這也是我認為「recovery hierarchy」比單純 BER 更重要的原因。未來評估 SerDes 或 optical engine，不應只問 pre-FEC/post-FEC BER，而要問：

- error burst 超過 FEC capability 後，會不會在 local replay buffer 被消化？
- retrain 時 routing 是否能繞過 degraded lane？
- replay 是否維持 transaction ordering？
- link flap 是否會 invalidate GPU memory operation 或 communicator？
- 上層能否辨識 temporary degradation 和 permanent failure？

這些問題已經跨過傳統 PHY spec 的邊界。

## 第一層：FEC、PLR、UPHY recovery 的目的不是「完全沒有錯」

NVLink 6 的 PHY strategy 很值得拆開看。

第一道是 lightweight FEC。NVIDIA 的說法是，因為後面還有 PLR，所以不必把所有錯誤都交給更重、更高 latency 的 FEC 去消化。FEC 先 inline 修掉可修復 bit errors；如果 burst error 超過 correction capability，就由 PLR 在 physical layer 重送 packet；若再嚴重到 link down，UPHY recovery 重新校準 link，而 packet 暫存在 replay buffer 中。

這是一個典型的 cross-layer latency trade-off：**不要用最昂貴的機制處理所有錯誤，而是建立多段 protection envelope。**

假設 FEC coding gain 做得更強，可能降低 post-FEC BER，但會付出更多 coding latency、power 與 silicon area。反過來，如果 FEC 太輕，就會把過多事件推給 replay，造成 tail latency。最適點不是「BER 最低」，而是讓整體 expected recovery cost 最小。

NVIDIA 宣稱 PLR + UPHY recovery 可以把許多 physical fault 壓在 1 ms 以下，且 FEC correction 接近即時。[官方說明](https://developer.nvidia.com/blog/how-nvidia-nvlink-6-delivers-multi-layer-resiliency-for-ai-factories/)沒有公開完整 FEC code、raw/post-FEC BER curve、replay-buffer depth、channel loss budget 或不同溫度下的 retry distribution，因此目前能確認的是 architecture，而不能從公開資料獨立驗證其實際 error envelope。

這是 vendor claim 必須保留的界線。

## 第二層：CBFC 真正做的是把 congestion 從「錯誤事件」變成 admission control

NVLink 6 link layer 採 credit-based flow control。sender 只有在知道 next hop 有足夠 buffer credit 時才允許送出資料。換句話說，它不是等 queue 爆掉之後再要求對端減速，而是在 packet injection 前就做 admission control。

這和常見 RoCE/PFC 的思路不同。PFC 的本質是 queue pressure 已經出現，再透過 pause frame 反應；大型 lossless fabric 因而可能出現 head-of-line blocking、pause propagation 甚至 deadlock。這不是單純理論問題。USENIX ATC 2025 的 [FLB 研究](https://www.usenix.org/conference/atc25/presentation/hu-jinbin)就量測到 PFC 與 fine-grained rerouting 交互作用時，反而可能把 congestion 擴散到更多 path，加劇 HoL blocking。

但這裡不能把問題簡化成「credit 好、Ethernet 壞」。

2026 年 7 月更新的 [Ultra Ethernet 1.0.3](https://ultraethernet.org/specification-history/)已經不是舊式 RoCEv2 + PFC 的單一模型。UET 定義 Network-signal Congestion Control、Receiver-credit Congestion Control 與 Transport Flow Control 等不同機制，並支援 loss recovery、multipathing 與新的 transport semantics。也就是說，NVIDIA 對「off-the-shelf Ethernet」的比較不能直接外推成對所有 modern Ethernet fabric 的結論。

真正的差異在 control scope。NVLink 可以假設一個更封閉、拓撲受控、hop 數少、硬體高度一致的 scale-up domain，因此 hop-by-hop credit 的 state cost 與 buffer coupling 可以接受；Ethernet scale-out 要跨越數萬到數十萬 endpoint、多 vendor switch 與更複雜路徑，設計空間不同。

## lossless 不代表沒有 congestion，也不代表天然 deadlock-free

credit-based flow control 很容易被一句「不掉包」過度簡化。真正的問題是：當多個 traffic class、virtual channel 或 routing dependency 同時存在時，credit dependency 本身可能形成 cycle。任何 lossless fabric 要避免 deadlock，都必須在 routing、virtual channel、buffer partition 或 escape path 上建立額外 invariant。

NVLink 公開資料目前強調 CBFC 能避免 buffer overflow 與 PFC pause storm，但沒有公開足夠細節讓外部完整分析其 channel dependency graph。因此，對「mathematically eliminate packet drops」可以接受，但不能進一步推成「所有 congestion pathology 都被消除」。

反過來，Ethernet 也不再只有 PFC。UEC 的 Receiver-credit Congestion Control 與 Transport Flow Control 已經把 receiver-side credit 引入 transport，並保留 ECN/latency signal 與 selective retransmission。這其實顯示兩個世界正在靠近：專用 scale-up fabric 開始增加 network-style manageability；Ethernet 則開始吸收更強的 credit、loss recovery 與 accelerator-aware semantics。

差別最後可能不是「credit vs packet loss」，而是誰能把 control loop 做得更短、state scope 更小、implementation complexity 更可控。

## 第三層：contain-and-drain 把 link failure 變成局部拓撲重組

當 fault 已經嚴重到需要 software-visible intervention，NVLink 6 的 NMX Controller 會把 affected link 放進 contain-and-drain state：先阻止新 traffic 進入，再讓既有 transaction drain，之後 retrain link。

這裡的價值不在「有 SDN controller」，而是 control plane 和 data plane 的 failure domain 被刻意拆開。

根據 NVIDIA 說明，NMX control function 可以在 switch tray 之間做 HA migration；switch management CPU 或 NVOS reboot 時，data plane 仍持續 forwarding。這是成熟 switch architecture 常見的 principle，但把它搬進 rack-scale accelerator fabric 後，意義更大：GPU collective 不應因為管理面重啟而被迫 abort。

另一方面，NVLink 也允許 partially populated rack 與 switch tray hot-swap。NCCL 可以根據退化後的 topology 重建 collective ring/tree。這代表「拓撲」不再只是 boot-time 靜態資訊，而是 runtime recovery input。

![NVLink 6 故障放大與局部封鎖路徑](/images/networking/2026-09-23/failure-containment-path.svg)

圖：作者整理；資料來源：[NVIDIA NVLink resiliency](https://developer.nvidia.com/blog/how-nvidia-nvlink-6-delivers-multi-layer-resiliency-for-ai-factories/)、[NCCL 2.24 RAS](https://developer.nvidia.com/blog/networking-reliability-and-observability-at-scale-with-nccl-2-24/)

## Serviceability 才是 rack-scale 系統是否能進 production 的分水嶺

很多 interconnect benchmark 只量 microbenchmark latency 與 bandwidth，但 production system 最終還是由 maintenance policy 決定可用度。若更換一個 switch tray 必須先 drain 整個 72-GPU domain，等於把單一 FRU 的維修成本放大成整個 rack 的 lost capacity；若還牽動上層 data parallel group，影響甚至會跨 rack。

因此 hot-swap、partial population、in-service software update 看似「系統管理」功能，其實直接影響 accelerator economics。對一個高利用率 inference cluster 而言，可以在 workload 持續跑的狀態下替換 switch tray，代表 maintenance window 從 capacity outage 變成 topology degradation。

這裡可以把 availability 寫成一個更接近工程現實的式子：

`Useful compute = peak compute × scheduling efficiency × communication efficiency × availability`

前兩項常被模型、kernel 與 scheduler 團隊優化，communication efficiency 則由 fabric 決定；但當設備數量大到一定程度，availability 會開始主導。若 72 顆 GPU 必須同生共死，任何單點維修都會讓 availability 急遽惡化；如果 fabric 能 graceful degradation，則系統可以把「故障」降級成「暫時少一點 bandwidth」。

這也是 NVLink 6 可以運作 partially populated rack 的意義。它不是為了讓客戶少裝幾顆 GPU，而是讓 topology 本身成為可變狀態。對 control plane 而言，rack 不再只有 healthy/unhealthy，而有一個連續的 degraded operating region。

對未來 CPO 更是如此。pluggable optics 壞掉可以抽換 module；CPO 把 optical engine 拉近 switch ASIC 後，功耗與 electrical reach 變好，但 service unit 可能變大。若 optical engine、laser source、fiber attach 的維修需要更換整個 switch tray，network resiliency 與 mechanical serviceability 就必須共同設計。這是下一代 102.4T/204.8T fabric 很容易被忽略的 cross-layer trade-off。

## 第四層：真正昂貴的不是 link reset，而是 communicator state

硬體把大部分錯誤擋住之後，剩下最麻煩的是 process-level failure。

NCCL communicator 不是一個可以任意 hot-swap 的抽象。它和參與 process、GPU topology、transport path 綁得很深。當 communicator 所在 process crash，傳統 recovery 往往意味著重新啟 engine：weight 從 storage 搬回 HBM、kernel compile、CUDA graph recapture、communicator rebuild。

NVIDIA Dynamo 的 Shadow Engine 做法很直接：在 primary engine 旁邊維持一個已經初始化、但 idle 的 replica。它事先建立自己的 NCCL/NIXL communicator，也已經把 model state 準備好。primary 掛掉時，不是「重新建立一個 process」，而是把 traffic 切到已經活著的 process。

NVIDIA 在 B200 的 benchmark 中，對一個 two-worker inference setup 模擬失去其中一個 worker，cold restart 恢復 serving capacity 要 283 秒，Shadow Engine 是 7.3 秒，約 39 倍差異。[原始 benchmark 與架構說明](https://developer.nvidia.com/blog/how-nvidia-nvlink-6-delivers-multi-layer-resiliency-for-ai-factories/)來自 NVIDIA 自身，公開資料沒有提供完整 model size、storage hierarchy、cache 狀態與多種 failure pattern，因此這個數字應理解成「證明 warm redundancy 可以把 recovery order 從 minutes 壓到 seconds」，而不是所有 deployment 都會固定得到 39x。

代價也很清楚：shadow engine 不是免費。它佔 GPU memory、process slot、network state，也可能降低有效資源利用率。這是一個 reliability-versus-capacity 的經典取捨。只有當 downtime cost 高於 standby cost，它才成立。

## 下一步會是 fault-aware scheduling，而不只是 fault recovery

目前多數 scheduler 看到的是 node health、GPU health、job state，network telemetry 往往只在 observability 系統裡供人排查。這在 scale-up fabric 裡很浪費，因為 PHY 和 switch 其實比 scheduler 更早知道某條 lane 正在惡化：FEC corrected error count 上升、PLR 次數增加、retrain 變頻繁、eye margin 下降、某個 trunk link 被 rebalanced。

如果這些訊號只用來告警，系統會等到 failure 發生才行動；如果它們可以變成 scheduler input，就能做 predictive containment。

例如一組 tensor-parallel worker 正跑在一個逐漸惡化的 link domain，scheduler 可以先停止把新 request 放進去，將 decode traffic 移到健康 replica，待 queue drain 後再做 maintenance。training job 則可在 checkpoint 邊界前主動重建 communicator，而不是等 link hard-down。

這會把 network telemetry 從「觀測資料」提升成「control signal」。

但風險也很明顯。過度敏感的 predictor 會造成不必要 migration，反而降低 utilization；不同 layer 對 degradation 的定義也可能衝突。PHY 看到 corrected BER 上升，不代表 application throughput 一定受影響。真正需要的是跨層 policy：什麼 signal 只做 logging，什麼 signal 觸發 routing change，什麼 signal 需要 communicator shrink，什麼程度才值得移動 workload。

這個問題很接近現代 storage 的 predictive failure management，也接近 distributed database 的 replica health scoring。AI fabric 最後可能走到同樣方向：不是追求「永不故障」，而是讓 failure 在真正影響 service-level objective 之前就被隔離。

## 第五層：checkpoint 仍然是最後一道保險，但不該是第一反應

當 fault 已經跨過 link、switch、process，最後才輪到 checkpoint/restore。

NVLink 6 文章提到 NCCL 對 `cuda-checkpoint` 的 prototype support，目標是讓 multi-node checkpoint 可以在 communicator 與 CUDA graph 建立之後仍捕捉更多 startup state。這一點很關鍵，因為傳統 checkpoint 通常只保 application data，真正 restart 時還是要重走大量 initialization。

如果未來 communicator state、GPU memory state、graph state 都能更完整地被 snapshot，distributed inference 的 recovery unit 就會從「整個 job」逐漸縮小到「故障 process / worker group」。

這和 database recovery 很像：不是每次出錯都 full restore，而是靠多層 write-ahead / retry / replica / checkpoint 把 recovery scope 壓小。

## In-network compute 會讓 reliability 問題更難，而不是更簡單

NVLink 6 Switch 的 SHARP engine，以及 UALink 2.0 新增的 In-Network Compute，都代表 collective 不再只是端點之間的 byte movement。switch 本身開始持有 computation state：partial reduction、multicast replication、collective epoch、participant membership。

這會改變 failure semantics。

假設一個 AllReduce 已經有 31 個 participant 的 partial sum 進入 switch，第 32 個 participant 在 link retry 期間重送資料。switch 必須知道這是同一個 contribution 的 replay，還是一個新的 operation；否則就可能 double-count。再假設 switch tray 在 operation 中途被 contain-and-drain，runtime 必須知道目前 collective 是否可以安全 retry、是否要換 topology 重做、或者必須 abort 整個 communicator。

因此 in-network compute 真正困難的地方，不只是算力，而是 **failure atomicity**。

傳統 packet switch 可以把 packet 視為近似 stateless forwarding；帶 reduction engine 的 switch 更像 distributed system 裡的一個 stateful participant。它需要 operation identifier、epoch、replay/duplicate suppression、timeout 與 membership change semantics。這些資訊若只藏在 vendor firmware 裡，上層 runtime 很難做 portable recovery；若要標準化，又會增加 protocol surface。

這是我認為 UALink 2.0 後續最值得追的部分。規格已經把 In-Network Compute 與 manageability 拉進來，但真正 production-ready 的判準應該是：在 link flap、switch failover、partial participant failure 下，collective state 是否仍有明確、可測試、跨 vendor 的 semantics。

## 從 PHY 到 distributed runtime，這其實是一條控制迴路

把 NVLink 6 拆完後，我會把它畫成下面這條鏈：

`BER → FEC/PLR → link health → routing/credit → communicator health → engine health → workload goodput`

每一層都在做三件事：detect、contain、recover。差別只在時間尺度與 state 範圍。

這對 future interconnect 的影響比單一 protocol 更大。因為當 scale-up domain 擴到數百 accelerator，PHY reliability、switch topology、collective library 和 scheduler 會被迫共享更多 failure semantics。單純做到「link up」已經不夠，IP 必須能 expose telemetry、degradation state、retry counters、fault locality，讓上層知道什麼時候重排 traffic、什麼時候縮 communicator、什麼時候真的該 checkpoint restore。

這也是為什麼 UALink 2.0 值得一起看。UALink 在 2026 年 4 月加入 In-Network Compute、centralized manageability，以及和 UCIe 3.0 相容的 chiplet 定義，管理面採 gNMI、YANG、SAI、Redfish。[UALink 2.0 公告](https://ualinkconsortium.org/wp-content/uploads/2026/04/UALink-2.0-Specification-PR_FINAL.pdf)反映同一件事：scale-up interconnect 已經不是只有 PHY + packet format，而是在變成完整 system substrate。

NVLink 的優勢是 extreme co-design；UALink 的目標是 multi-vendor interoperability。這兩條路真正競爭的，不只是 bandwidth，而是誰能更快建立跨 PHY、switch、manageability、runtime 的可靠度 contract。

## 真正需要的是一份 cross-layer fault budget

如果把這套設計轉成工程方法，我會要求每一層都回答同一組問題：可偵測的 fault class 是什麼、偵測 latency 多久、可以 local recovery 的比例是多少、向上層暴露什麼 state、失敗後最多放大多少 workload cost。

PHY 的 budget 可能以 BER、FEC margin、retrain time 表示；link layer 看 replay rate、credit starvation 與 route convergence；runtime 看 communicator rebuild 與 replica failover；service layer 最後看 token loss、request error rate、job completion time。只有把這些 budget 串起來，才能真正回答「一個 lane margin 下降 3 dB，最後會不會變成使用者看到的 SLA violation」。

這也是未來 observability 最需要改變的地方。現在很多 telemetry 仍以 layer 為中心：SerDes counter 在 BMC，switch counter 在 NOS，NCCL trace 在 job log，serving latency 在 application dashboard。若沒有共同的 fault identity 和 timestamp correlation，就很難知道同一個 transient event 穿過了幾層。

對 AI factory 而言，最有價值的不是更多 counter，而是能建立因果鏈：哪一個 physical event，透過哪一條 routing path，影響哪一個 communicator，最後造成多少 lost tokens。這才是 cross-layer resiliency 真正成熟的樣子。

## 我目前的判斷

第一，**AI interconnect 的 KPI 應該從 peak bandwidth 轉成 sustained goodput。** 3.6 TB/s 很重要，但如果 fault recovery 仍是 minutes 級，實際 token throughput 會被 availability 吃掉。未來 benchmark 應該同時量 bandwidth、tail latency、fault injection 下的 recovery time，以及 workload-level goodput。

第二，**scale-up fabric 正在向 memory system 靠攏，而不是向傳統 packet network 靠攏。** direct load/store、atomics、credit、ordered operation、replay、coherence-like semantics 都使它更像延伸的 memory fabric。可靠度也因此必須在更低層處理，不能等 TCP/RDMA timeout 才反應。

第三，**真正的 moat 可能不是 SerDes，而是 failure semantics 的垂直整合。** SerDes、switch、NIC、runtime 都可以被單點追上；難的是把錯誤從 physical signal 一路映射成可預期的 application recovery。這需要多代硬體、driver、collective library、scheduler 與操作經驗共同收斂。

第四，**開放標準最大的挑戰不是功能表，而是跨 vendor fault behavior 是否真的可組合。** UALink 可以規範 protocol、manageability 與 chiplet interface，但 production-grade resiliency 要驗證的是：A vendor accelerator、B vendor switch、C vendor retimer、D vendor runtime 在 partial failure 時，是否還能維持同一套 recovery contract。這會比 link interoperability 難很多。

## 接下來真正值得追的問題

我會持續看四件事。

一是 NVLink 6 是否會公開更完整的 FEC/PLR error statistics、lane degradation threshold 與 CPO 版本的 fault model。當 scale-up 從 copper 拉到 CPO，laser、fiber attach、optical engine 會引入完全不同的 failure distribution。

二是 UALink 2.0 的 In-Network Compute 與 manageability 是否能在 2026–2027 的實際 silicon 上做到 multi-vendor fault injection interoperability，而不只是 link bring-up。

三是 Ultra Ethernet 從 scale-out 往 scale-up transport 延伸時，是否會採更多 credit-based semantics，還是維持 end-to-end loss recovery 與 receiver-credit 的混合模式。[UEC 1.0.3](https://ultraethernet.org/specification-history/)已經展示出 transport 與 congestion control 正在快速演化。

四是 distributed runtime 是否會真正開始「吃」fabric health telemetry。當 scheduler、NCCL、Dynamo 能直接知道某一條 lane 或 switch tray 正在 degradation，而不是等 operation timeout，AI cluster 才算真正進入 fault-aware scheduling。

這可能是 NVLink 6 最重要的訊號：**下一代 network 不只是搬資料，而是要把故障控制在不值得讓上層知道的地方。**

## References

1. [How NVIDIA NVLink 6 Delivers Multi-Layer Resiliency for AI Factories](https://developer.nvidia.com/blog/how-nvidia-nvlink-6-delivers-multi-layer-resiliency-for-ai-factories/) — NVIDIA Technical Blog, 2026.
2. [NVIDIA NVLink: The Scale-Up Network for AI Factories](https://developer.nvidia.com/blog/nvidia-nvlink-the-scale-up-network-for-ai-factories/) — NVIDIA Technical Blog, 2026.
3. [NVLink & NVLink Switch Specifications](https://www.nvidia.com/en-eu/data-center/nvlink/) — NVIDIA, 2026.
4. [Networking Reliability and Observability at Scale with NCCL 2.24](https://developer.nvidia.com/blog/networking-reliability-and-observability-at-scale-with-nccl-2-24/) — NVIDIA Technical Blog, 2025.
5. [FLB: Fine-grained Load Balancing for Lossless Datacenter Networks](https://www.usenix.org/conference/atc25/presentation/hu-jinbin) — USENIX ATC, 2025.
6. [Ultra Ethernet Specification History — 1.0.3](https://ultraethernet.org/specification-history/) — Ultra Ethernet Consortium, 2026.
7. [Ultra Ethernet Consortium Specification 1.0](https://ultraethernet.org/ultra-ethernet-consortium-uec-launches-specification-1-0-transforming-ethernet-for-ai-and-hpc-at-scale/) — Ultra Ethernet Consortium, 2025.
8. [UALink 2.0 Specification Update](https://ualinkconsortium.org/wp-content/uploads/2026/04/UALink-2.0-Specification-PR_FINAL.pdf) — UALink Consortium, 2026.
9. [UALink Specifications](https://ualinkconsortium.org/specification/) — UALink Consortium, 2026.
