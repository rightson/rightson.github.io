---
layout: post
title: "CSIG 用 4/8-byte L2 Tag 回報 Bottleneck：μs 級 Network State 如何驅動 Transport"
date: 2026-09-25 06:15:02 +0800
domain: networking
categories: networking congestion-control
description: "SIGCOMM 2026 的 CSIG 用固定長度 L2 tag 在每個封包上累積 bottleneck state，讓 sender 約一個 RTT 內取得可直接控制的 available bandwidth、delay 與 locator；Google 報告 Fast Ramp-Up 在 production 將 median RPC latency 降低 20%、unclaimed bandwidth 降低 60%。"
---

作者：Scott Yo-Ru Chen

CSIG（Congestion Signaling）把 datacenter transport 最缺的資訊壓成一個固定長度的 bottleneck summary：封包穿過 fabric 時，switch 只在自己的狀態更差時覆寫 tag，receiver 再把結果反射回 sender。這個設計刻意犧牲完整 per-hop trace，換來每包可用、固定 4/8-byte、可以在 line rate 執行的 control signal。Google 在 SIGCOMM 2026 公開的結果顯示，Fast Ramp-Up 利用這類訊號後，production 的 median RPC latency 降低 20%，unclaimed bandwidth 降低 60%；團隊也驗證到五代 commodity switch、最高 102.4 Tbps、四代 NIC 與五種 transport stack。[Google Research](https://research.google/pubs/csig-congestion-signaling-for-datacenter-transports/)

這個工作最值得研究的地方，是它對 telemetry 做了非常強的資訊壓縮：不把整條 path 的狀態搬回 host，只保留「目前最限制這個 packet 的 hop」以及它的 signal value。對 congestion control 而言，這個資訊往往比一整串 switch counters 更可操作；代價則是 sender 永遠只看到經過壓縮後的 path state。

~~~text
Forward path
Sender             Switch A              Switch B              Receiver
S = max   ------>  local=0.78  ------>   local=0.41  ------>   extract
                    S=0.78                S=0.41, LM=B

Reverse reflection
Sender  <----------------------------------------------------- Receiver
        bottleneck=0.41, locator=Switch B / topology stage
~~~


圖：作者整理；資料來源：[Google — CSIG: Congestion Signaling for Datacenter Transports](https://research.google/pubs/csig-congestion-signaling-for-datacenter-transports/)、[IETF Internet-Draft draft-ravi-ippm-csig-01](https://datatracker.ietf.org/doc/html/draft-ravi-ippm-csig-01)

## ECN 能指出壅塞，fast ramp-up 還需要更直接的 headroom

DCTCP、DCQCN 這類 congestion control 可以利用 ECN 判斷 queue 是否越過 threshold；Swift 則從 RTT / delay 推導 congestion。這些訊號都很實用，但 sender 在「網路其實還有多少容量可以拿」這件事上仍要靠 heuristic。

這個盲點在 burst-heavy datacenter traffic 特別明顯。短 RPC、新啟動的大 flow、collective phase transition、storage / KV-cache transfer 都可能突然需要大量頻寬。sender 太保守，link 留下 idle capacity；sender 太激進，queue、RTT、drop 或 ECN marking 立刻上升。早期 CSIG Internet-Draft 把問題寫得很直接：CCA 對 slow-down 已經有很多成熟訊號，對 starting rate 與 ramp-up rate 卻缺乏 bottleneck 明示資訊。[IETF CSIG draft](https://datatracker.ietf.org/doc/html/draft-ravi-ippm-csig-01)

這裡可以做一個簡單量級估算。假設一條 800 Gb/s bottleneck 在 100 μs 內仍有 40% capacity 沒被使用：

`unused_bytes = 800 Gb/s × 0.4 × 100 μs ÷ 8 ≈ 4 MB`

100 μs 看起來極短，但高速 fabric 的成本已經大到足以讓這 4 MB 成為可觀的 idle capacity。對短生命週期 flow 而言，等到多個 RTT 後才逐步探測到可用頻寬，可能等於 transfer 已經接近結束。

ECN 的優勢是語意簡單、部署成熟；完整 INT 的優勢是資訊豐富。問題在於 INT header 會隨 hop 數與 metric 數增加。CSIG draft 估計常見 INT variant 的 per-packet overhead 約從 20B 到 100B 以上，而且 header 長度可變，會增加 MTU 與 parser 複雜度。[IETF CSIG draft, Introduction](https://datatracker.ietf.org/doc/html/draft-ravi-ippm-csig-01)

CSIG 選的是第三條路：讓 switch 計算 path reduction，只把 reduction result 留在 packet 裡。

## Compare-and-replace 讓 path telemetry 變成 associative reduction

CSIG 的 forward path 可以抽象成一個很小的 reduction operator。sender 先放入初始 signal，packet 經過每個 switch 時，switch 量出自己的 local state，只有在 local value 比 tag 內目前的 bottleneck 更差時才 overwrite。

以 minimum available bandwidth 為例：

`S_out = min(S_in, ABW_local)`

以 maximum per-hop delay 為例：

`S_out = max(S_in, PD_local)`

當 overwrite 發生，switch 同時更新 locator metadata，receiver 最後拿到的就是這個 packet 經過 path 上的 worst hop。receiver 再透過 transport option 或 payload，把 signal 反射到 reverse path；sender 因此大約在一個 RTT 內取得 forward-path bottleneck state。[IETF CSIG operation](https://datatracker.ietf.org/doc/html/draft-ravi-ippm-csig-01)

這個設計能在 line rate 成立，關鍵在 operator 很小，而且是 associative 的 min/max reduction。switch 不必保存每個 flow 的完整 path history，也不必把每一跳的 telemetry append 到 packet。data plane 只做：

`measure → compare → optional replace`

因此 topology 從 3 hops 擴到 7 hops，CSIG header 本身不會跟著長大。

但資訊量也被嚴格限制。早期 draft 定義一個 packet 同時只攜帶一種 signal；如果 sender 同時想要 available bandwidth、utilization 與 per-hop delay，可以在不同 packets 間輪替 signal type。這種做法把「每一包知道全部」改成「一條 flow 持續 sample 幾種 path property」，更接近 control-loop 真正需要的資料率。

## 4-byte compact 與 8-byte wide 的差異在 quantization budget

CSIG 的早期公開協定文件定義 compact 4-byte 與 expanded 8-byte 格式；2025 年 UEC 對 IEEE 802.1 的 liaison 也描述 4-byte compact 與 8-byte wide tag，並說明兩者使用不同 EtherType。[UEC / IEEE 802.1 liaison](https://www.ieee802.org/1/files/public/docs2025/liaison-UEC-CongestionSignalingCSIG-1125.pdf)

~~~text
4-byte Compact
+------------------+-----+---+----------------+--------------------+
| TPID / EtherType | T   | R | Signal value   | Locator metadata   |
| 16 bits          | 3b  |1b | 5 bits / 32桶  | 7 bits             |
+------------------+-----+---+----------------+--------------------+

8-byte Expanded / UEC Wide
+------------------+------------------+------+----------------+------+
| TPID / EtherType | Locator metadata | T    | Signal value   | R    |
| 16 bits          | 16 bits          | 4b   | 20 bits        | 8b   |
+------------------+------------------+------+----------------+------+
~~~


圖：作者依據 [IETF CSIG draft](https://datatracker.ietf.org/doc/html/draft-ravi-ippm-csig-01) 與 [UEC / IEEE 802.1 liaison](https://www.ieee802.org/1/files/public/docs2025/liaison-UEC-CongestionSignalingCSIG-1125.pdf) 重繪。

compact format 的資料欄位只有 16 bits：3-bit signal type、1-bit reserved、5-bit signal value、7-bit locator metadata。5-bit signal value 意味著只有 32 個 bucket。這不是單純的解析度不足，而是 control design 的一部分：bucket 應該把解析度集中在「控制決策最敏感」的區間。例如 0 與 1 Gb/s available bandwidth 的差異通常比 399 與 400 Gb/s 更重要。

expanded / wide format 把 signal value 拉到 20 bits，locator metadata 到 16 bits，也提供更大的 signal type / metadata 空間。早期 draft 舉例，若 available-bandwidth quantum 設成 8 Mb/s，20-bit value 可以涵蓋到 Tb/s 級 link；per-hop delay 若用 128 ns quantum，則可表示到毫秒以上尺度。這些是 encoding 範例，不代表所有 implementation 必須使用相同 quantum。[IETF CSIG Appendix A](https://datatracker.ietf.org/doc/html/draft-ravi-ippm-csig-01)

這裡存在一個容易被忽略的 trade-off：量化解析度越高，不代表 control loop 一定越好。network signal 本身有 measurement noise、queue dynamics 與 feedback delay。當 controller 的 resolution 遠高於可穩定估計的 physical state，更多 bits 只會把 noise 帶進 rate update。

## Google 的 production 結果證明 deployability，但不能直接外推所有 workload

SIGCOMM 2026 的 CSIG paper 目前最強的公開證據，是它已經離開單一 prototype。Google 的摘要報告：

- Fast Ramp-Up 將 median RPC latency 降低 20%；
- unclaimed bandwidth 降低 60%；
- CSIG 驗證過五代 commodity switch，最高到 102.4 Tbps；
- 涵蓋四代 NIC 與五種 transport stack。[Google Research](https://research.google/pubs/csig-congestion-signaling-for-datacenter-transports/)

這組結果對架構判斷很重要，因為 CSIG 的主要風險一直不是 min/max 這個演算法本身，而是能不能跨 parser、switch generation、NIC、host stack 與 transport 真正部署。五代 switch 與多 transport 的結果顯示，固定 L2 tag 的 portability 有實際價值。

但 20% 與 60% 不應被當成「開 CSIG 就會得到的固定收益」。Fast Ramp-Up 的收益高度依賴 workload 是否經常留下可被快速 reclaim 的 headroom。如果 network 已長時間接近 saturation，available bandwidth 本來就接近零，直接知道 bottleneck state 也不會創造新的 capacity。若 workload 的 tail 主要卡在 incast queue、receiver bottleneck、application pacing 或 storage stall，ramp-up 的影響也可能很小。

因此比較 CSIG-based CCA 時，至少要固定 flow-size distribution、RTT、offered load、incast pattern、path diversity、ECN/AQM 設定、NIC pacing 與 sender algorithm。production median improvement 很有說服力，但它回答的是 deployability 與 fleet-level usefulness，沒有替所有 topology / CCA 給出 universal speedup。

## L2 placement 解的是部署邊界，也降低 transport 耦合

把 CSIG 放在 L2 有三個工程上的理由。

第一，tag 可以位在固定 parser region，不必深入理解 TCP、RDMA、Falcon 或其他 L4+ transport。Google 的 SIGCOMM 摘要也特別強調 transport-agnostic deployability。[SIGCOMM 2026 program](https://conferences.sigcomm.org/sigcomm/2026/program/papers/)

第二，L2 tag 可以留在 operator-controlled domain。UEC 對 IEEE 的 liaison 描述 LLDP capability negotiation：如果下一跳不支援 CSIG，switch 應在 egress strip 掉 tag，避免 tag 離開支援的 network domain。[UEC / IEEE 802.1 liaison](https://www.ieee802.org/1/files/public/docs2025/liaison-UEC-CongestionSignalingCSIG-1125.pdf)

第三，tunnel 與 encryption 比較容易處理。早期 draft 的設計目標包括 IP-in-IP、VXLAN、Geneve 以及不同加密邊界；CSIG 放在 L2，使 transit switch 不必依賴 inner L3/L4 header 才能讀寫 signal。[IETF CSIG design rationale](https://datatracker.ietf.org/doc/html/draft-ravi-ippm-csig-01)

這也解釋了為什麼 CSIG 的進展不能只看 paper。OCP SAI 1.18.1 release notes 已列出 UEC CSIG protocol enhancement；目前 `saitam.h` 也可以看到 CSIG EtherType、signal type、bandwidth computation interval、quantization bands 等 API 欄位。[SAI 1.18.1 Release Notes](https://github.com/opencomputeproject/SAI/blob/master/doc/SAI_1.18.1_ReleaseNotes.md)、[SAI TAM API](https://github.com/opencomputeproject/SAI/blob/master/inc/saitam.h)

Linux Plumbers Conference 2025 也已有把 CSIG 接進 Linux TCP 的提案：L2 收包處理、GRO / hardware-software interaction、TCP handshake negotiation，以及透過 ACK TCP option 做 reflection。[Linux Plumbers Conference 2025](https://lpc.events/event/19/contributions/2272/)

這些材料還不等於「CSIG 已成為 Linux/UEC 的普遍預設能力」。它們比較準確地說明：switch API、host stack 與 standards coordination 已經開始形成同一條 implementation path。

## Fixed bottleneck summary 的代價：第二壞的 hop 被丟掉

CSIG 最漂亮的地方也是它最大的限制：path 被壓成一個 bottleneck。

| 維度 | ECN | CSIG | Per-hop INT |
| --- | --- | --- | --- |
| Packet overhead | IP header bits，固定 | 4 B / 8 B，固定 | 約 20 B 到 100 B+，依 hop / metric 成長 |
| Congestion state | threshold / marking | multi-bit bottleneck + locator | per-hop metrics |
| Path detail | 低 | principal bottleneck | 完整 per-hop detail |
| 適合用途 | 簡潔壅塞訊號 | transport control input | fine-grained telemetry / debug |

圖：作者整理；資料來源：[RFC 3168 ECN](https://www.rfc-editor.org/rfc/rfc3168)、[IETF CSIG draft](https://datatracker.ietf.org/doc/html/draft-ravi-ippm-csig-01)、[P4 INT v2.1](https://p4.org/p4-spec/docs/INT_v2_1.pdf)

如果 path 上同時存在兩個接近的 bottleneck，CSIG 只留下更差的一個。當第一 bottleneck 在下一個 RTT 消失，sender 不一定知道第二 bottleneck 已經接手限制。這會讓 controller 面對「compressed state switching」：observed bottleneck 可以在不同 hop 間跳動。

multipath 會再加一層複雜度。若 packets 被 spraying 到不同 paths，每一包得到的是各自 path 的 bottleneck summary。這對 per-packet path selection 很有價值，但如果 sender 把不同 path 的 sample 混成單一 flow estimate，signal variance 可能會明顯增加。

另一個 failure mode 是 stale signal。switch 量測的是過去一小段 window，packet 走到 receiver，再 reflection 回 sender，又經過約一個 RTT。高速 link 在這段時間可以搬很多資料。以 800 Gb/s 為例，50 μs 就相當於 5 MB serialization budget；若在這 50 μs 內大量 senders 同時看到「有 headroom」並加速，舊的 available-bandwidth estimate 很快失效。

因此 CSIG 適合成為 control input，不適合成為無條件的 rate oracle。實際 CCA 仍需要 pacing、increase gain、queue/delay guardrail、ECN 或 loss fallback 來維持 stability。

## Brownfield 最難的是「沒有訊號」的語意

partial deployment 會產生一個很實際的 correctness 問題：sender 收不到 CSIG 時，究竟代表 network 很空，還是 path 中有一段根本不支援 CSIG？

這兩種情況的控制動作完全相反。

早期 draft 把 device capability 分成 discard、pass-through、complete support，並定義 egress stripping；UEC 後續也用 LLDP capability negotiation 處理 supported domain。[IETF incremental deployment](https://datatracker.ietf.org/doc/html/draft-ravi-ippm-csig-01)、[UEC / IEEE liaison](https://www.ieee802.org/1/files/public/docs2025/liaison-UEC-CongestionSignalingCSIG-1125.pdf)

因此 transport 端必須把「valid signal」與「signal absent」分開建模。最危險的實作，是把 absence 解讀成 maximum headroom，然後 aggressive ramp-up。brownfield CCA 比較安全的策略，是只有在 capability negotiation 與完整 path support 都成立時才啟用 CSIG-specific fast path；其他 traffic 回到既有 ECN / RTT / loss semantics。

security 也有同樣問題。CSIG 是 sender 會直接拿來改 transmission rate 的 control input，若不受信任的 host 或 transit device 可以偽造 available bandwidth，就能誘導 sender 過度加速或刻意降速。早期 draft 因此把 CSIG-domain 定義成可信任的 network domain，boundary stripping 不是 optional hygiene，而是控制迴路的一部分。

## 我的判斷：telemetry 正在變成 transport 的 hardware API

我目前有三個判斷。

第一，CSIG 的價值主要來自 bounded information。完整 telemetry 看起來資訊最多，但 transport control 不需要重建整張 network map；它需要的是能快速回答下一個 rate update 的最小 state。fixed-size bottleneck reduction 讓 switch hardware 成本、packet overhead 與 host parsing 都有明確上限。

第二，400G/800G 世代會讓 fast ramp-up 變得更重要。link rate愈高，同樣 10–100 μs 的保守探測就代表更多未利用 bytes；AI/HPC flow 又常有 phase synchronization，使 capacity availability 變化更陡。這使「知道何時該減速」之外，「知道現在安全地能加多少」變成同等重要的 transport 問題。

第三，值得追的是 ecosystem convergence。SIGCOMM paper 證明 Google production deployability；UEC 與 IEEE liaison 處理 tag / EtherType / capability negotiation；SAI 暴露 switch implementation API；Linux 社群開始討論 TCP reflection。這四條線若收斂成一致的 wire format、switch semantics 與 host API，CSIG 才可能從 hyperscaler-specific telemetry primitive 變成 broader Ethernet transport primitive。

## 接下來要驗證的問題

第一個問題是 control stability。不同 CCA 同時消費 min(ABW)、min(ABW/C) 或 max(PD) 時，gain、measurement window、feedback delay 應如何配合，才不會讓大量 senders 同步 overshoot？

第二個問題是 UEC 最終 wire contract。2025 IEEE liaison 描述的 compact / wide tag 已經很具體，但 EtherType、negotiation、wide-format semantics 與 compliance 還要看後續公開規格如何收斂。UEC 目前公開的 Ultra Ethernet Specification 最新版本是 1.0.3（2026-07-16）；CSIG 的演進應該以 UEC / IEEE 後續正式材料，而不是已過期的 2024 IETF draft 作為最終依據。[UEC Specification History](https://ultraethernet.org/specification-history/)

第三個問題是 RoCE / UET / TCP / proprietary transport 對 CSIG 的 rate update 是否能共存。wire signal 可以 transport-agnostic，但 control law 不是。相同 bottleneck signal 餵給不同 CCA，可能得到完全不同的 fairness 與 tail behavior。

第四個問題是 observability 能否和 control 共用同一個 signal contract。Google paper 強調每個 packet 都能帶 flow-contextual bottleneck location；若這些資料同時進 transport loop 與 fleet telemetry，就有機會把「事後 join counters 找 root cause」縮短成直接問：哪些 flows、在哪個 topology tier、被哪種 bottleneck 限制。這會是 CSIG 在 congestion control 之外更長期的價值。

## References

1. [Abhiram Ravi et al., “CSIG: Congestion Signaling for Datacenter Transports” — ACM SIGCOMM 2026 / Google Research](https://research.google/pubs/csig-congestion-signaling-for-datacenter-transports/)
2. [ACM SIGCOMM 2026 — Program: CSIG](https://conferences.sigcomm.org/sigcomm/2026/program/papers/)
3. [Ravi et al., “Congestion Signaling (CSIG)” — IETF Internet-Draft, 2024-02-02, expired work in progress](https://datatracker.ietf.org/doc/html/draft-ravi-ippm-csig-01)
4. [Ultra Ethernet Consortium → IEEE 802.1 Liaison: Congestion Signaling (CSIG), 2025-11](https://www.ieee802.org/1/files/public/docs2025/liaison-UEC-CongestionSignalingCSIG-1125.pdf)
5. [Ultra Ethernet Consortium — Specification History](https://ultraethernet.org/specification-history/)
6. [Open Compute Project SAI 1.18.1 Release Notes](https://github.com/opencomputeproject/SAI/blob/master/doc/SAI_1.18.1_ReleaseNotes.md)
7. [Open Compute Project SAI — TAM / CSIG API](https://github.com/opencomputeproject/SAI/blob/master/inc/saitam.h)
8. [Linux Plumbers Conference 2025 — Congestion Signaling for Linux TCP Data Center Networking](https://lpc.events/event/19/contributions/2272/)
9. [RFC 3168 — Explicit Congestion Notification (ECN)](https://www.rfc-editor.org/rfc/rfc3168)
10. [P4.org — In-band Network Telemetry (INT) v2.1](https://p4.org/p4-spec/docs/INT_v2_1.pdf)
11. [Gautam Kumar et al., “Swift: Delay is Simple and Effective for Congestion Control in the Datacenter” — SIGCOMM 2020](https://research.google/pubs/swift-delay-is-simple-and-effective-for-congestion-control-in-the-datacenter/)
12. [Weitao Wang et al., “Poseidon: An Efficient Congestion Control using Deployable INT for Data Center Networks” — NSDI 2023](https://research.google/pubs/poseidon-an-efficient-congestion-control-using-deployable-int-for-data-center-networks/)
