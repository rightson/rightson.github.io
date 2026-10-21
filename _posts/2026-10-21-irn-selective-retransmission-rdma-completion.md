---
layout: post
title: "IRN 讓失序封包先落地，補齊缺口後才宣告 RDMA 完成"
date: 2026-10-21 19:08:00 +0800
domain: networking
categories: networking
series: networking-deep-dive
permalink: /networking/2026/10/21/irn-selective-retransmission-rdma-completion.html
description: "IRN 以選擇性重傳、BDP 在途上限與 completion gating，把丟包代價限制在缺失封包，同時維持 RDMA Write、Read、Send 與 Atomic 的完成順序。"
takeaways:
  - who: "IRN requester"
    value: "IRN requester 以累積 ACK、選擇性 ACK bitmap 與 recovery sequence 找出缺失 PSN；一次視窗有多個丟包時只補缺口，避免 go-back-N 把已送達資料重新灌回壅塞點。"
  - who: "IRN responder"
    value: "IRN responder 把失序資料直接 DMA 到最終應用程式位址，並以 arrival bitmap 追蹤缺口與尾包；尾包先到時先保存 completion metadata，連續前綴完整後才更新 MSN、釋放 WQE 與交付 CQE。"
  - who: "RNIC 設計團隊"
    value: "RNIC 設計團隊用 BDP-FC 限定每個 QP 的在途封包，也同時限定 SACK 與 arrival bitmap 長度；鏈路升到 400 或 800 Gb/s 後，RTT、MTU 與 QP 規模會直接決定片上狀態成本。"
  - who: "RDMA 應用程式"
    value: "RDMA 應用程式仍應依 Write-with-Immediate、後續 Send、Atomic 或 CQE 判斷完成；直接輪詢遠端 buffer 的尾端內容，遇到失序 placement 時會把部分寫入誤判成完整 operation。"
---

RDMA 把資料搬移交給 RNIC，application 只要張貼 WQE，稍後從 completion queue 取得結果。這個介面看似以 operation 為單位，線上傳送卻由多個帶 packet sequence number（PSN）的封包完成。只要其中一包遺失，transport 就必須回答兩個問題：要重送多少資料，以及 application 何時能相信整個 operation 已經完成。

傳統 RoCE 的可靠連線遇到失序封包時會丟棄它，sender 收到 NACK 後從最後一個連續確認點重新傳送。這個 go-back-N 作法適合幾乎不丟包的 fabric；若交換器開始丟包，一個缺口會讓後面已經跨過網路的封包失去價值。2018 年 Radhika Mittal 等人提出 [IRN](https://arxiv.org/abs/1806.08159)，把 selective retransmission 與 BDP-based flow control 加進 RoCE endpoint，讓 fabric 可以承受丟包而不必用 PFC 保證每一包都留下。

這篇接續 [RoCE 用 PFC 接住在途資料，用 ECN 降低持續進入的流量]({% post_url 2026-10-14-roce-pfc-ecn-feedback-buffer-budget %})。上一篇從 queue 與控制延遲解釋 PFC 為何會暫停其他 flow；這一篇沿著丟包後的 PSN、memory placement、WQE 與 CQE 前進，說清 RNIC 如何只補缺口，同時維持 operation completion。

先沿下圖的藍色路徑看一遍：requester 從 Request WQE 取得位址與長度，切成 PSN 連續的封包；fabric 可以丟失或重排；responder 把先到資料直接 DMA 到最終位址。橘色路徑負責補洞。arrival bitmap 已經看見尾包，也要等較早 PSN 補齊，才把 completion 交給 application。

![IRN requester 將 WQE 分段，封包經 lossy fabric 後由 responder 直接 DMA 並以 bitmap 等待缺口，連續前綴完整後交付 CQE](/images/networking/2026-10-21/irn-end-to-end-path.svg)

圖一：依據 [IRN extended paper §3、§5](https://arxiv.org/abs/1806.08159) 整理。資料 placement 與 completion notification 是兩條相關但分開推進的狀態路徑。

## Go-back-N 把一個缺口放大成整段重送

假設一個 QP 已送出 PSN 0–63，PSN 7 與 29 在 fabric 內暫時性遺失。傳統 receiver 收到 PSN 8 時，因為期待值仍是 7，便丟棄 8 以及後續失序封包並回 NACK。sender 從 PSN 7 起重送到 63，共 57 包；其中只有 7 與 29 原本缺失，另外 55 包曾經成功越過網路，卻因 receiver 沒有保留而再走一次。

IRN receiver 收到失序封包時不丟棄資料。NACK 同時帶回 cumulative ACK，也就是目前第一個缺口，以及觸發 NACK 的較高 PSN，形成簡化的 SACK。sender 以 bitmap 記錄哪些 PSN 已被累積或選擇性確認，進入 loss-recovery mode 後先補累積 ACK 指向的缺口；較高 PSN 已有選擇性確認時，bitmap 內的零才代表另一個需要重送的位置。[IRN §3.1](https://arxiv.org/abs/1806.08159) 還用 recovery sequence 記住進入修補前最後一次正常送出的 PSN；累積 ACK 越過它之後，sender 才離開修補模式。

![同一個64包視窗遺失PSN 7與29，go-back-N從7起重送57包，IRN只補2包](/images/networking/2026-10-21/irn-retransmission-timeline.svg)

圖二：假設算例。丟包視為暫時事件，重送成功；總傳送量由 121 包降到 66 包。這是 packet accounting，沒有代入 queue、RTT、RTO 或 congestion control。

這個差異會在 congestion 時自我強化。go-back-N 增加的 55 包與新流量共用同一個瓶頸，延長 queue 並創造更多丟包機會。selective retransmission 只補兩個缺口，把重傳負擔限制在出錯 flow 與出錯 PSN。IRN 論文的 factor analysis 也測過「選擇性重傳但沒有 SACK」：遇到同一視窗內多個缺口時，需要用多個 RTT 逐次發現，與 SACK 版本相比，平均 flow completion time 在不同情境下惡化不到 1% 到 75%。同一分析把 SACK 換回 go-back-N，搭配 Timely 時平均 FCT 差距仍有 20%–50%。

SACK bitmap 不是讓 sender 立刻相信所有較高 PSN 永久安全。它是在一個受限制的在途範圍內記錄 receiver 已看到的 PSN，sender 仍保存可重傳資料；cumulative ACK 往前推，才代表連續區段完成。這個區分也解釋 IRN 為何要把 selective retransmission 與 BDP-FC 成對設計。

## BDP-FC 同時限制 queue 壓力與追蹤狀態

若 sender 可以無限增加在途封包，receiver 的失序集合也可能無限增長。IRN 以 bandwidth-delay product 設定靜態 packet cap：

~~~text
BDP_bytes = link_rate_bytes_per_second × path_RTT_seconds
BDP_packets = ceil(BDP_bytes / MTU_bytes)
in_flight_packets < BDP_packets
~~~

sender 只有在目前 PSN 與最後確認 PSN 的差小於 cap 時，才送新封包。[IRN §3.2](https://arxiv.org/abs/1806.08159) 使用已知 datacenter topology 最長路徑的 BDP，並容許適度高估。cap 太小會讓長路徑鏈路等不到下一批資料；cap 太大仍能傳滿鏈路，卻增加 queue 與 bitmap 狀態。

論文的預設網路是 40 Gb/s、最長六 hop、每 hop 傳播延遲 2 μs，給出 120 kB BDP，約 110 個 1 kB MTU 封包。原文的 FPGA resource 試算將 bitmap 向上取成 128 bits。IRN 共使用五張 BDP-sized bitmap：responder 兩張追蹤到達與尾包事件，requester 一張追蹤 Read response，兩端各一張追蹤 selective ACK。原文在 128-bit 假設下得到每 QP 640 bits bitmap，另外增加 160 bits per-QP state 與每個 WQE 3 bytes context。

同一公式套到更高速鏈路，狀態量會跟著 BDP 增加。下面的試算固定 1 KiB MTU，採十進位 Gb/s 與 bytes；「每 QP bytes」只計五張 bitmap，未納入 alignment、cache、timer、WQE 及 allocator overhead。

| 鏈路與 RTT | BDP | packet cap | 五張 bitmap |
| --- | ---: | ---: | ---: |
| 40 Gb/s、24 μs | 120,000 bytes | 118 包 | 74 bytes/QP |
| 100 Gb/s、24 μs | 300,000 bytes | 293 包 | 184 bytes/QP |
| 200 Gb/s、12 μs | 300,000 bytes | 293 包 | 184 bytes/QP |
| 400 Gb/s、12 μs | 600,000 bytes | 586 包 | 367 bytes/QP |
| 800 Gb/s、12 μs | 1,200,000 bytes | 1,172 包 | 733 bytes/QP |

![BDP packet cap與五張bitmap的每QP狀態隨鏈路速率增加](/images/networking/2026-10-21/irn-bdp-bitmap-scaling.svg)

圖三：假設算例，以 [可重跑腳本](https://github.com/rightson/rightson.github.io/blob/main/scripts/experiments/irn_selective_retransmission.py) 產生；紫色 800 Gb/s bar 提醒高速下 RTT 仍主導狀態。數值不是現代 RNIC 的實測資源。

以 400 Gb/s、12 μs 為例，五張 bitmap 的純資料量是 367 bytes/QP。若設計目標是 100 萬個同時駐留的 QP，單純相乘約 367 MB；實作通常會把熱門 QP context 放片上 cache，冷 context 放較慢層級，packet-rate、cache miss 與 PCIe 往返因而成為另一組問題。縮短 RTT 可等比例縮小 cap；把 MTU 從 1 KiB 增加到 4 KiB 可把 bitmap 位元數約降為四分之一，但大封包在丟失時也多重送資料，並改變小訊息 latency 與 serialization。

另一個可行方向是 dynamic window，由 congestion control 依狀態縮放在途量。它能在低負載提高彈性，也把 transport state 與速率控制綁得更緊。IRN 刻意選擇固定 BDP cap，把「可安全追蹤多少封包」與「目前應該多快送」拆開：前者限制 state，後者仍可交給 DCQCN、Timely 或其他演算法。

## 失序資料可以先寫入，完成通知必須等待連續前綴

把 OOO 封包全放 RNIC SRAM 最直觀，也最昂貴。論文用 110 包/QP、1 kB/包估算，一千個 flow 就需要 110 MB packet buffer。IRN 的替代做法是把封包直接 DMA 到 application 指定的最終位址，只在 NIC 保留 bitmap。這個轉換將每個失序封包約 1 kB 的 packet storage，縮成一或數個追蹤 bit，但它也打破「最後一包到達等於整個 message 完成」的直覺。

考慮 12 包 RDMA operation。PSN 0、1、3…11 都已抵達，PSN 2 遺失。尾包 PSN 11 帶來 operation 的末端資訊，payload 也已放進 memory；連續前綴仍只有 0、1。若 RNIC 此時釋放 WQE 或產生可見 CQE，application 會讀到中間缺一段的 buffer。

IRN responder 使用兩類資訊把這兩件事拆開：arrival bitmap 表示各 PSN 是否到達，另一個 bit 標示哪些 PSN 是會觸發 MSN 更新、Receive WQE expiration 或 CQE 的最後一包。尾包先到時，RNIC 可以先建立 premature CQE 並把 metadata 放到 main memory；只有 bitmap 的連續前綴越過該尾包，才把 CQE 交給 application。[IRN §5.3.3](https://arxiv.org/abs/1806.08159) 以這個順序維持 Write、Send 與 Write-with-Immediate 的完成語意。

![尾包PSN 11先到但PSN 2缺失，completion被保留；PSN 2補齊後才交付CQE](/images/networking/2026-10-21/irn-completion-gate.svg)

圖四：假設算例。綠格已 DMA，紅格是缺口，紫格為尾包；completion event 在第 12 次抵達，也就是 PSN 2 修補後才變成可見。

這裡的關鍵不在「資料能否先落地」，而在「哪一個事件授權 application 使用資料」。[IRN Appendix B.1](https://arxiv.org/abs/1806.08159) 引用 InfiniBand Write completion 條件：Write-with-Immediate 的末包完成、後續 Send 完成，或後續 Atomic 更新，才能讓 responder application 依序使用先前 Write 的內容。IRN 讓這些後續事件都等到較早 PSN 連續完成，因此即使物理抵達順序改變，operation 可見順序仍維持。

## 四種 RDMA operation 需要不同的失序補強

Write 的第一包帶有 RETH，包含 remote address 與長度。後續封包若早到，只有 PSN 仍不足以算出 placement；IRN 因此要求每一包都攜帶 RETH。每包還要能推導相對 offset，responder 才能直接 DMA 到正確位置。這增加 header bytes，換來免存整包的 OOO placement。

Send 與 Write-with-Immediate 會消耗 responder 預先張貼的 Receive WQE，而且 WQE 必須依張貼順序配對。in-order transport 可以靠隱含游標前進；OOO transport 要在 Request WQE 與 Receive WQE 都維護 recv_WQE_SN，封包也攜帶這個編號。Send packet 還要帶相對 PSN offset，才能把資料寫進該 Receive WQE 指向的 buffer。

Read 的方向容易混淆。requester 發出 Read request，responder 反而成為資料來源；現有 RoCE requester 對 Read response 沒有逐包 ACK。IRN 為 Read response 新增 read (N)ACK opcode，requester 每收到一包 response 就回覆，responder 也要有 timeout。Read/Atomic request 本身若失序到達，必須在 responder 的 Read WQE buffer 等較早 request；read_WQE_SN 用來定位正確 slot。Atomic 是單包 operation，處理方式接近單包 Read。

這些補強可整理成一個順序：

1. packet arrival 先依 operation metadata 找到最終位址或 WQE slot；
2. payload DMA 完成後設定 arrival bit；
3. NACK/SACK 告訴 sender 哪些 PSN 已見、哪個連續缺口仍在；
4. last-packet metadata 可以先保存；
5. contiguous prefix 跨過 operation 尾端後，才更新 MSN、釋放 WQE 並提交 CQE。

Shared Receive Queue 另有一個細節。receive WQE 由多個 QP 共用時，recv_WQE_SN 在 WQE 從 SRQ dequeue 時配置。若較高序號 Send 先到，RNIC 要依序 dequeue 足夠的 WQE，讓該封包配到對應 slot；如果 responder 沒有 credit，某些失序 probe 必須直接丟棄，等正常 loss recovery 重新送到。[IRN Appendix B.2–B.4](https://arxiv.org/abs/1806.08159) 把 receiver-not-ready 等錯誤 NACK 與一般失序 NACK 分開，前者仍可能啟動 go-back-N 式處理。

## Timeout 補上沒有較高 PSN 可報告的丟包

SACK 需要較高 PSN 抵達，receiver 才能指出前面有洞。單包 RPC 整包遺失時，沒有後續封包觸發 NACK；message 尾端遺失也可能缺少足夠的新到達。sender 仍要靠 timeout。

IRN 使用兩個固定值。當在途封包數不超過 N 時，用較短的 `RTO_low`，降低單包訊息尾端等待；在途較多時改用 `RTO_high`，減少 queue variation 引起的 spurious retransmission。論文預設 N=3、`RTO_low`=100 μs、`RTO_high`=320 μs，並在模擬中把 `RTO_high` 放大至四倍、N 提高到 10 或 15，主要結果只有小幅差異。這些是 40 Gb/s 模擬參數，部署時要以實際 path RTT、queue delay 與 timer granularity重新選擇。

另一種方案是像 TCP 一樣動態估計 RTO。原文表示其實驗版本增加了複雜度，初始 timeout 的影響仍主導短訊息，因此沒有帶來改善。今天若 NIC 已有更細的 telemetry 與 timer wheel，dynamic RTO 可能重新變得有吸引力；代價是每 QP 估計狀態、更新頻率及 clock domain 會進入 packet-processing critical path。

## 原始結果支持 endpoint 處理丟包，部署條件已經改變

IRN 論文使用商用 NIC vendor 提供、擴充自 INET/OMNeT++ 的 RoCE simulator。預設是 54 台 server 的三層 fat-tree、40 Gb/s link、每 hop 2 μs propagation、70% network load；50% flow 是 32 bytes–1 kB 單包訊息，15% flow 為 200 kB–3 MB 大流量。論文報告 IRN 不開 PFC，相對 RoCE 加 PFC，在不同 topology、bandwidth、buffer、workload 與 congestion-control 情境改善 6%–83%。預設無 explicit congestion control 時，IRN 遭遇 8.5% packet drop，仍因 selective recovery 與無 pause spreading 得到較好的 network-wide 結果。

這組結果的意思是 endpoint loss recovery 足以改變 PFC 的必要性，並非「丟包越多越好」。論文同時顯示 BDP-FC 減少多餘 queue，SACK-based recovery 的影響又比 BDP-FC 更大；兩者一起才形成完整設計。搭配 Timely 或 DCQCN 後，IRN 開關 PFC 的差異縮小，因為 explicit congestion control 同時減少 drop 與 pause。

硬體部分以 Xilinx Kintex UltraScale KU060、Vivado HLS 2017.2 合成四個簡化模組。論文報告 receiveData、txFree、receiveAck 與 timeout 合計使用 1.35% FF、4.01% LUT，最慢模組 throughput 為 45.45 Mpps；bitmap 增大到支援 100 Gb/s 時，合計為 2.66% FF、9.5% LUT。這些模組接收已解析的 packet metadata 與 QP context，沒有包含完整 RNIC datapath。FPGA、HLS、40/100 Gb/s 與 2017 年工具結果只能說明增量邏輯可合成，不能直接當作現代 400/800 Gb/s ASIC 的面積與功耗。

相反方向的方案也合理。PFC 配合嚴格 traffic engineering，可以讓現有 go-back-N RNIC 在可控 fabric 內維持低 drop，且不改 endpoint packet format；代價是逐跳 buffer、priority mapping、watchdog 與 pause spreading 管理。iWARP 直接沿用 TCP reliability，能在一般 IP 網路上處理丟包；代價是 byte stream 與 RDMA segment 間的轉換，以及更完整的 transport state。IRN 選在兩者中間：保留 RDMA segment 與 operation 語意，只加入 packet-level SACK、有限在途與 OOO placement。

未來 24 個月內，若新一代 RNIC 或 scale-out transport 公開 per-packet SACK、OOO direct placement 與 completion gating 的資源數字，最值得比較的是 400/800 Gb/s 下每 QP bitmap cache miss、最大 resident QP 數及小訊息 loss tail。若業界仍普遍要求無丟包 fabric，而且 endpoint 沒有公開承擔這些狀態，IRN 的論點會繼續停留在架構參考；若 endpoint 能在不犧牲 message rate 的條件下吸收偶發 drop，PFC 的角色就可能縮到特定 traffic class 或最後一道保護。

## 一個缺口牽動 packet、memory 與 application 三層狀態

IRN 的 selective retransmission 解決 bandwidth 浪費，BDP-FC 把失序集合限制在固定範圍，completion gating 則把「資料已落地」和「operation 可使用」重新接起來。少任何一層都會留下問題：只有 SACK 而沒有 cap，bitmap 可能隨在途量膨脹；只有 OOO DMA 而沒有 completion gate，application 會看見部分結果；只有 cap 而保留 go-back-N，丟包仍會重送整段資料。

64 包的假設案例把差距縮成可檢查的數字：兩個缺口時，go-back-N 送 121 包，selective retransmission 送 66 包。12 包 completion 案例也給出清楚條件：尾包已到仍停在連續前綴 2，補上 PSN 2 後才交付 CQE。這兩個結果由 [腳本](https://github.com/rightson/rightson.github.io/blob/main/scripts/experiments/irn_selective_retransmission.py) 與 [結果檔](https://github.com/rightson/rightson.github.io/blob/main/scripts/experiments/irn_selective_retransmission.results.json) 固定保存，方便改動 window、loss pattern、link rate、RTT 與 MTU 後重新核對。

## 證據範圍

本文的 IRN transport、operation-specific header、bitmap、WQE/CQE ordering、模擬與 FPGA synthesis 數字，來自 2018 年 extended paper。假設算例只檢查 packet 數量、連續前綴與 BDP 公式，沒有重跑作者的 OMNeT++ simulator、FPGA RTL、商用 RNIC firmware 或實體 lossy fabric。

BDP 表採固定 RTT 與 MTU，沒有加入 protocol headers、ACK traffic、path asymmetry、timer wheel、context cache、alignment 及 memory hierarchy。每 QP 狀態相乘用來展示量級，不表示任何現有產品的實際容量。文章沒有宣稱 IRN 已成為 RoCE 標準，也沒有把論文的 40/100 Gb/s resource result 外推成 400/800 Gb/s ASIC 結果。

## References

- Radhika Mittal et al., [Revisiting Network Support for RDMA](https://arxiv.org/abs/1806.08159), extended version of ACM SIGCOMM 2018, 2018-06-21。
- Renato Recio et al., [A Remote Direct Memory Access Protocol Specification](https://www.rfc-editor.org/rfc/rfc5040), RFC 5040, 2007-10。
- Hemal Shah et al., [Direct Data Placement over Reliable Transports](https://www.rfc-editor.org/rfc/rfc5041), RFC 5041, 2007-10。
- Yibo Zhu et al., [Congestion Control for Large-Scale RDMA Deployments](https://conferences.sigcomm.org/sigcomm/2015/pdf/papers/p523.pdf), ACM SIGCOMM 2015。

