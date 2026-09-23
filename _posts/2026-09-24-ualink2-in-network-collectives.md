---
layout: post
title: "UALink 2.0 的分水嶺：Scale-up Switch 開始執行 Collective，而不只是搬資料"
date: 2026-09-24 06:06:45 +0800
author: Scott Yo-Ru Chen
domain: networking
categories: networking ualink
description: "UALink 2.0 最重要的改變不是再提高 lane rate，而是把 collective 的一部分搬進 fabric。這會同時改寫頻寬效率、switch microarchitecture、correctness、security 與管理邊界。"
---

作者：Scott Yo-Ru Chen

我認為 UALink 2.0 最值得注意的地方，不是又多了一個「開放版 NVLink」，也不是單純把 scale-up bandwidth 繼續往上推。真正的分水嶺，是 **switch 開始理解 collective，並在資料還在 fabric 裡流動時就參與計算**。

這件事看起來只是把 reduce、all-reduce、broadcast、reduce-scatter 從 accelerator software 往 switch 下推，但系統含義遠比「省一點頻寬」大。當 fabric 從 passive transport 變成 collective execution layer，switch 便開始承擔 operation state、datatype、ordering、completion、failure isolation，甚至 security context。從這一刻起，AI scale-up network 不再只是高速 I/O，而是一個受限、可驗證、可管理的 distributed computer。

UALink Consortium 在 2026 年 4 月發布 Common Specification 2.0，正式加入 In-Network Compute；同一批 specification 還拆出 200G Data Link/Physical Layer 2.0、Manageability 1.0 與 Chiplet 1.0。[UALink 官方發布](https://ualinkconsortium.org/wp-content/uploads/2026/04/UALink-2.0-Specification-PR_FINAL.pdf)把這四件事放在一起，其實已經透露設計方向：未來 scale-up fabric 的瓶頸不再只在 PHY，而在「資料搬移、集體同步與系統控制」能否一起被處理。

![Endpoint-only collective 與 in-network reduction 的差異](/images/networking/2026-09-24/ualink-inc-cut.svg)

圖：作者整理；資料來源：[UALink — Exploring In-Network Compute](https://ualinkconsortium.org/blog/exploring-in-network-compute-how-ualink-is-redefining-ai-scale-up-architecture-1509/)、[Synopsys — Four Ways UALink 2.0 Advances AI Scale Up](https://www.synopsys.com/blogs/chip-design/4-ways-ualink-2-0-advances-ai-scale-up.html)

## 200G/lane 解決的是 link rate，但 collective 的問題是重複搬資料

UALink 1.0 已經不是一條慢的 interconnect。官方 white paper 定義最高 200 GT/s data rate per lane，實際 signaling rate 212.5 GT/s，用來吸收 Ethernet Layer 1 的 FEC 與 encoding overhead；四條 lane 組成一個 Station，可提供 800 Gbps TX 與 800 Gbps RX。目標 scale 是最多 1,024 個 accelerator，request-response RTT 目標低於 1 µs。[UALink 200G 1.0 White Paper](https://ualinkconsortium.org/wp-content/uploads/2025/04/UALink-1.0-White_Paper_v3.pdf)

也就是說，UALink 2.0 加 In-Network Compute 的原因，不是因為 1.0 bandwidth 不夠快，而是因為 collective 的成本不是單純的 `bytes / link_rate`。

以 data parallel training 的 gradient all-reduce 為例，每顆 accelerator 都持有一份 partial gradient。傳統做法由 communication library 把 collective 拆成 point-to-point transfers，endpoint 需要收資料、做 reduction，再把 partial result 往下一段送。即使每條 lane 再快一倍，資料仍然會在多個 endpoint 與 fabric cut 之間重複經過。

最簡單的模型，是看一個 fan-in 為 `k` 的 switch cut。假設每個 endpoint 都有同一個 tensor block，大小為 `B` bytes：

`passive forwarding traffic across uplink ≈ k × B`

如果 switch 能在本地把 `k` 份相同 position 的 block 先做 partial reduction，則跨越上行 cut 的資料可以近似變成：

`in-network reduced traffic across uplink ≈ B`

這不是說整個 all-reduce 流量會神奇地變成原來的 `1/k`。最後的結果仍要向下 dissemination，而且實際 collective 會 chunk、pipeline、striping，甚至跨多 plane。但在**會聚 cut** 上，能不能先 combine 再送，會直接決定 fabric 內部是否需要為大量重複 intermediate data 付出 bandwidth。

這也是 UALink 官方在介紹 In-Network Compute 時反覆強調的核心：reduction、aggregation、synchronization、collective primitive、部分 data transformation 與 scheduling optimization，都可以在資料「in flight」時進行，而不是等資料抵達 endpoint 後才開始處理。[UALink In-Network Compute 技術說明](https://ualinkconsortium.org/blog/exploring-in-network-compute-how-ualink-is-redefining-ai-scale-up-architecture-1509/)

## 真正困難的不是 ALU，而是 collective state

如果只從 hardware block diagram 看，In-Network Compute 很容易被誤解成「在 switch 裡塞幾個 adder」。那不是難點。

真正困難的是：switch 必須知道這一批資料屬於哪個 collective、哪一個 virtual pod、哪個 tensor block、什麼 datatype、什麼 operation，以及什麼時候可以宣告完成。

Synopsys 對 UALink 2.0 的技術說明提到，specification 定義了 collective primitives 與 block collectives，涵蓋 operation establishment、data flow 與 completion tracking；switch 只保存執行 collective 所需的最小狀態。[Synopsys 技術說明](https://www.synopsys.com/blogs/chip-design/4-ways-ualink-2-0-advances-ai-scale-up.html)

這個「最小狀態」是關鍵。state 太少，switch 無法知道來自不同 source 的 block 是否可以 combine，也無法可靠追蹤 completion；state 太多，switch SRAM、lookup、scheduler 與 recovery complexity 會迅速膨脹。

一個實際 collective-aware switch 至少要面對幾種 state dimension：

- collective/group identity：這批資料屬於哪一組 participant；
- operation：sum、max、min、broadcast 或其他 primitive；
- datatype：FP32、FP16、BF16、integer，甚至不同 block format；
- sequence/chunk identity：哪個 tensor slice 正在處理；
- arrival bitmap 或等價狀態：還缺哪些 participant；
- destination/distribution rule：結果送去哪裡；
- completion/error state：何時可以 safe completion，何時必須 abort。

這裡的設計壓力不像一般 packet switch。傳統 switch 的核心工作是 lookup、queue、schedule、forward；collective-aware switch 則多了一個「資料語意相同才能合併」的條件。它不能因為兩個 packet 都要走同一個 output port，就任意把 payload 做加法。

![Collective-aware switch 的最小執行狀態](/images/networking/2026-09-24/ualink-inc-state.svg)

圖：作者整理；資料來源：[Synopsys — UALink 2.0 Collectives](https://www.synopsys.com/blogs/chip-design/4-ways-ualink-2-0-advances-ai-scale-up.html)、[UALink Common 2.0](https://ualinkconsortium.org/specification/ualink-common-2-0-specification/)

## throughput 上限取決於「每秒要合併多少元素」，不是只有 port bandwidth

In-Network Compute 會帶來另一個容易被忽略的 bottleneck：switch arithmetic throughput。

假設一個 switch 的 aggregate payload arrival rate 是 `R` bit/s，而 reduction datatype width 是 `w` bits。若每個到達元素都需要至少一次 combine，則 reduction datapath 的最低 element rate 大約是：

`combine_rate ≈ R / w`

例如只做一個量級估算：若某個 fabric slice 實際承接 51.2 Tb/s payload，datatype 是 16-bit，那就是約 3.2 trillion elements/s 的 arrival rate。這不是在說某顆 UALink switch 公開規格就是 51.2 Tb/s，也不是說每個 bit 都會進 reduction engine；它只是顯示一件事：**當 network compute 真正要 line-rate 化，ALU、accumulator、SRAM banking、crossbar 與 scheduler 必須一起按 network throughput 設計。**

這和 GPU 裡的 tensor core 完全不同。switch 不需要做複雜 matrix multiply，但它的 arithmetic 必須極度 predictable，不能讓某一種 collective 把 forwarding pipeline 卡死。

因此比較兩個 in-network collective design 時，我不會先看「支援幾種 operation」，而會看下面幾個數字：

1. 每個 port、每個 switch 的 sustained reduction throughput；
2. 可同時存在多少 collective context；
3. 每個 context 支援多少 participant / tensor block；
4. small-message setup latency 與 large-message steady-state bandwidth；
5. collective traffic 與普通 load/store traffic 同時存在時，是否互相 starvation；
6. failure/retry 發生後，context 是否能局部恢復，而不是整個 pod reset。

目前公開的 UALink 2.0 資料足以確認 architecture direction，但沒有公開足夠的 commercial silicon benchmark，可以回答上述問題。這個界線必須保留。

## floating point reduction 讓「結果相同」比「封包送到」困難

network engineer 很容易把 correctness 想成 packet correctness：CRC 正確、ordering 正確、沒有 duplicate，事情就結束。但 reduction 進入 switch 之後，數值語意也變成 fabric contract。

浮點加法不是 associative：

`(a + b) + c ≠ a + (b + c)`

原因是每一次 addition 都可能 rounding。當 collective topology 改變，reduction tree 的 combine order 也可能改變，最後 bitwise result 便可能和 endpoint-only algorithm 不同。

這不一定是錯。大多數 AI training 可以接受合理範圍內的 floating-point nondeterminism；問題在於 software stack 必須知道自己接受的是什麼 contract。

還有更多 corner cases：

- NaN 如何 propagate；
- overflow / underflow 如何處理；
- FP16/BF16 是否用較寬 accumulator；
- mixed precision 是否允許；
- 某一個 participant timeout 時，已經形成的 partial sum 怎麼處理；
- retry packet 是否可能被重複 reduce；
- multi-path reroute 後如何避免 duplicate contribution。

最後一點特別重要。一般 reliable transport 遇到 timeout 可以 retransmit；但如果 switch 已經把某個 packet 的 payload 納入 accumulator，再收到 retry copy，就不能再加一次。也就是說，reliability state 與 collective state 必須有一致的 idempotency / deduplication 邊界。

這也是為什麼「switch 裡多幾個 ALU」是錯的抽象。真正的問題是：**fabric 要開始對 computation correctness 負責。**

## security 邊界也被一起往 switch 推

UALink 2.0 的 collective-aware fabric 還有一個直接後果：switch 進入 trusted computing base。

UALink 1.0 已經有 end-to-end encryption / authentication 的設計方向；2.0 進一步面對 multi-tenant、virtual pod 與 collective offload。Synopsys 的說明指出，UALink 2.0 對 virtual pod 提供各自的 security context、keying / rotation，collective traffic 若需要 switch 處理，switch 必須在被允許的 trust boundary 內解密、計算，再重新保護資料。[Synopsys — Security in UALink 2.0](https://www.synopsys.com/blogs/chip-design/4-ways-ualink-2-0-advances-ai-scale-up.html)

這裡存在很現實的 architecture trade-off。

如果 switch 永遠看不到 plaintext，in-network reduction 很難做；如果 switch 可以看到 tenant tensor，switch 的 firmware、key management、attestation、debug interface 與 telemetry 都變成 security surface。

所以未來 hyperscaler 真正會問的，不會只是「有沒有 encryption」，而是：

- collective engine 是否和 forwarding path 有明確 privilege boundary；
- 不同 virtual pod 的 state 是否硬體隔離；
- crash dump / telemetry 會不會洩漏 payload 或 key-related state；
- switch reset 後 collective context 與 key context 如何同步恢復；
- firmware upgrade 能否不破壞 tenant trust chain。

In-Network Compute 帶來的 latency benefit，最後必須和更大的 TCB 一起算。

## UALink 2.0 把 protocol、PHY、chiplet、management 拆開，是比 200G 更重要的工程決策

這次 specification suite 另一個值得注意的地方，是 UALink Consortium 把 Common 2.0、200G DL/PL 2.0、Manageability 1.0、Chiplet 1.0 分離。[UALink specification suite](https://ualinkconsortium.org/specification/)

這不是文件整理而已，而是把 evolution cadence 拆開。

PHY / SerDes 會跟著 200G、400G、optical I/O 的進度快速演進；collective semantics、security model 與 pod control plane 不應該每次換 PHY 就全部重寫。相反地，collective operation 也可以新增，而不必等下一代 electrical signaling。

Chiplet 端則和 UCIe 3.0 對齊。UALink Chiplet specification 定義 interface、form factor、flow control 與 management，官方說明其與 UCIe 3.0 完整相容。[UCIe 3.0](https://www.uciexpress.org/specifications)目前已支援 48/64 GT/s、extended sideband、runtime recalibration 與更完整的 manageability。這讓 accelerator vendor 可以把 UALink controller / PHY / security block 視為一個可整合的 I/O subsystem，而不是每顆 accelerator 都重新發明 die-to-die glue。

Manageability 也同樣被獨立出來。UALink Manageability 1.0 採 gNMI、YANG、SAI、Redfish 等既有管理介面，表示 rack-scale scale-up fabric 開始被當成「需要 topology discovery、partition、health、lifecycle control 的系統」，而不只是板子上的高速連線。[UALink 2.0 官方發布](https://ualinkconsortium.org/wp-content/uploads/2026/04/UALink-2.0-Specification-PR_FINAL.pdf)

![UALink 2.0 specification suite 的解耦方向](/images/networking/2026-09-24/ualink2-spec-split.svg)

圖：作者整理；資料來源：[UALink Specifications](https://ualinkconsortium.org/specification/)、[UCIe 3.0 Specifications](https://www.uciexpress.org/specifications)

## Helios 證明 hardware ecosystem 正在形成，但還不能證明 UALink 2.0 collective 的實際效能

2026 年真正讓 UALink 從 specification 走向 system reality 的，是 AMD Helios。

AMD 公開的 Helios rackscale design 有 72 顆 MI455X GPU，使用 UALink over Ethernet（UALoE）做 scale-up，官方規格列出最高 260 TB/s aggregate scale-up bandwidth；scale-out 則使用 Pensando Ethernet。AMD 也公開四個 scale-up cartridge，並描述每個 switch tray 的 UALoE switching silicon。[AMD Helios 官方規格](https://www.amd.com/en/products/rackscale-solutions/helios.html)

另外 AMD 與 Celestica 在 2026 年 3 月宣布合作開發 Helios scale-up switch，並預計 2026 年底開始交付。[AMD / Celestica 公告](https://newsroom.amd.com/news/amd-and-celestica-announce-collaboration-to-a/)

這些資料證明的是三件事：

第一，UALink/UALoE 已經不只是 consortium slide，實際 rack、switch、GPU、manufacturing ecosystem 正在落地。

第二，200G-class scale-up fabric 已經被設計進 72-GPU rack，而不是停留在小型 demo。

第三，open scale-up fabric 會和 scale-out Ethernet 並存，而不是互相取代。

但目前公開資料**不能**直接證明另一件事：Helios shipping configuration 是否完整實作 UALink Common 2.0 的 In-Network Collectives，以及它的 reduction throughput、latency、failure semantics 是否優於 NVLink 6 或其他 proprietary fabric。

這是 vendor claim 最需要避免越界的地方。`260 TB/s aggregate scale-up bandwidth` 是 endpoint aggregate bandwidth，不是 all-reduce goodput，也不是 bisection bandwidth，更不是 collective completion time。

真正能比較的 benchmark 應至少固定：

- accelerator count；
- topology；
- tensor size / datatype；
- collective operation；
- number of concurrent collectives；
- computation/communication overlap；
- link failure / degraded path 條件；
- software library version；
- measured p50/p99 completion latency 與 sustained goodput。

在這些資料公開以前，「UALink 2.0 比 NVLink 更快」或反過來都不是嚴謹結論。

## 我的判斷：scale-up fabric 下一階段競爭的是 execution semantics

我目前的判斷有三點。

第一，單純提高 lane rate 的邊際效益會下降。當 200G/lane、下一代 400G/lane、CPO 或 optical I/O 繼續拉高 raw bandwidth，AI communication 的瓶頸會更集中到 synchronization、collective scheduling、tail latency 與 failure handling。這也是為什麼 UALink 2.0 和 NVLink 6 都開始把「network participates in computation」放到核心位置。

第二，In-Network Compute 最難建立的 moat 不是 arithmetic IP，而是 software / protocol / observability 的完整 contract。能不能讓 NCCL/RCCL 類 runtime、switch silicon、pod controller、security 與 telemetry 對同一個 collective state 有一致理解，會比「支援 reduce」四個字更重要。

第三，open standard 的真正驗收點不是 spec 公開，而是 interoperability。UALink Consortium 在 2026 年 4 月仍明確表示後續會建立 interoperability 與 compliance program。[官方發布](https://ualinkconsortium.org/wp-content/uploads/2026/04/UALink-2.0-Specification-PR_FINAL.pdf) 在兩家獨立 accelerator、兩家 switch、不同 controller/IP 能通過同一套 collective correctness、security、recovery test 之前，「multi-vendor fabric」仍然是一個正在形成的能力，不是已經被充分驗證的事實。

## 接下來真正值得追的問題

接下來我會看四件事。

一是 UALink INC 的 operation coverage 與 datatype coverage，尤其 FP8/FP16/BF16/FP32 mixed precision reduction 到底如何定義 accumulator semantics。

二是 commercial switch silicon 的 collective context capacity、line-rate reduction throughput 與 small-message latency。這會決定 INC 是少數大 tensor 的 accelerator，還是能進入普遍 runtime path。

三是 failure semantics。partial reduction 已發生後，如果 link flap、switch reset 或 participant timeout，系統如何保證不重複計算、不交付半完成結果，而且能局部恢復。

四是 compliance。真正重要的不是第一顆 UALink switch 出貨，而是不同 vendor 的 accelerator / switch / IP 能不能在 collective、security、management、recovery 上互通。

如果這四件事能被證明，UALink 2.0 的價值就不只是「又一個高速 interconnect 標準」。它會讓 open scale-up fabric 第一次真正具備 execution semantics。

## References

1. [UALink Consortium — UALink 2.0 Specification Suite Release, 2026-04-07](https://ualinkconsortium.org/wp-content/uploads/2026/04/UALink-2.0-Specification-PR_FINAL.pdf)
2. [UALink Consortium — Exploring In-Network Compute: How UALink Is Redefining AI Scale-Up Architecture, 2026-06-24](https://ualinkconsortium.org/blog/exploring-in-network-compute-how-ualink-is-redefining-ai-scale-up-architecture-1509/)
3. [UALink Consortium — Introducing UALink 200G 1.0 Specification](https://ualinkconsortium.org/wp-content/uploads/2025/04/UALink-1.0-White_Paper_v3.pdf)
4. [UALink Consortium — Specifications](https://ualinkconsortium.org/specification/)
5. [Synopsys — Four Ways UALink 2.0 Advances AI Scale Up](https://www.synopsys.com/blogs/chip-design/4-ways-ualink-2-0-advances-ai-scale-up.html)
6. [AMD — Helios Rackscale Solution](https://www.amd.com/en/products/rackscale-solutions/helios.html)
7. [AMD / Celestica — Collaboration on Helios Rackscale AI Platform, 2026-03-16](https://newsroom.amd.com/news/amd-and-celestica-announce-collaboration-to-a/)
8. [UCIe Consortium — UCIe 3.0 Specifications](https://www.uciexpress.org/specifications)
