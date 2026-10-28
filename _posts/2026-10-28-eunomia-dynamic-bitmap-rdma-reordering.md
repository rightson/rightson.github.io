---
layout: post
title: "Eunomia 讓 RDMA 用動態 bitmap 承受常態多路徑失序"
date: 2026-10-28 19:08:18 +0800
permalink: /networking/2026/10/28/eunomia-dynamic-bitmap-rdma-reordering.html
domain: networking
categories: networking
description: "Eunomia 只在連線真的失序時配置可擴張 bitmap，讓 packet spraying 與不等長路徑不再反覆觸發 RDMA 丟包處理；片上記憶體、ACK 流量與 WRITE 完成延遲則成為新的成本。"
takeaways:
  - who: "Eunomia receiver"
    value: "第一個失序封包才觸發 bitmap block 配置，circular 與 linear 兩段追蹤缺口；連續前綴前進後再合併區段，避開擴張 circular bitmap 時重排全部 bit 的成本。"
  - who: "RNIC 設計團隊"
    value: "罕見失序連線的常駐狀態可降到一個 4-byte 位址，高失序連線再依需求取得更多 block；若多數連線長期失序，48-byte metadata 與配置器會吃掉動態配置優勢。"
  - who: "RDMA fabric 營運團隊"
    value: "端點能區分重排與遺失後，packet spraying、deflection 與不規則拓樸成為可測試選項；論文的最高 FCT 改善來自 100 Gb/s ns-3 模擬，仍需在目標 RNIC 與流量上重建。"
  - who: "RDMA WRITE 應用程式"
    value: "依賴末包旗標時，Eunomia 先在 sender 等到前段已連續確認再送末包，因此增加一個 RTT；若改由 receiver 暫存末包，代價會移到 PCIe 搬移與 RNIC 資料路徑。"
series: networking-deep-dive
---

大型 RDMA fabric 一直有一個互相牽制的選擇。ECMP 把一條 flow 固定在一條路徑上，封包大致有序，RNIC 容易維持零複製與低延遲；但粗粒度雜湊遇到 elephant flow 或路徑不等長時，仍可能讓一條 uplink 壅塞、另一條閒置。Packet spraying 把每個封包分散到不同路徑，可以更快填平流量，代價是 receiver 看見的 packet sequence number（PSN）不再連續。

傳統 lossless RDMA 常把 PSN 缺口當成遺失。若 receiver 收到 8、10、11，卻還沒看到 9，它可能丟棄後續封包，sender 再以 go-back-N 從 9 開始重傳。這個機制面對偶發掉包尚可理解；當失序本身就是負載平衡的正常結果時，卻會把已經抵達的資料反覆丟棄，讓頻寬、尾延遲與 PFC 壓力一起惡化。

[Eunomia](https://arxiv.org/abs/2412.08540) 的提案不是消除失序，而是在 RNIC 收到資料、送進 host memory 前先記住哪些 PSN 已經到達。它的核心取捨很精確：不替每條 queue pair（QP）常駐配置足以覆蓋最壞失序範圍的 bitmap，只在真的發生失序時，向共享片上記憶體逐塊索取空間。這使 packet spraying、deflection routing 與不規則拓樸有機會成為日常工具，而不是只有應急時才敢啟用的功能。

2018 年的 [MP-RDMA](https://www.usenix.org/conference/nsdi18/presentation/lu) 已經用端點 bitmap 與選擇性確認承受多路徑失序；2023 年的 [ConWeave](https://conferences.sigcomm.org/sigcomm/2023/program.html) 則把 reorder queue 放到目的端 ToR。Eunomia 的新問題是：當資料中心有數十萬到百萬條 QP，而且每條連線的失序跨度差異很大，能否讓片上 SRAM 成本跟「當下真的失序」的連線數量與跨度一起伸縮？

![Eunomia 的端到端資料路徑](/images/networking/2026-10-28/eunomia-end-to-end-path.svg)

## 多路徑把偶發失序改成持續工作負載

先區分三種看似相近、實際代價不同的情況。

第一種是封包遺失。PSN 9 沒有抵達，receiver 永遠看不到它，最後必須由 timeout、NACK 或 selective repeat 觸發重傳。第二種是短暫重排。PSN 10 先到，9 稍後抵達；receiver 只要暫時保留 10 的到達狀態，就能避免重傳。第三種是大範圍失序。Packet spraying 讓 20、33、17、41 交錯抵達，缺口不只一個，而且最大 PSN 與目前連續前綴之間可能持續擴張。

固定大小 bitmap 的索引很簡單：PSN 減去 Head，或直接做模數映射。困難是尺寸。若 bitmap 太小，跨越視窗的封包仍需丟棄；若為每條 QP 都按最壞情況配置，幾乎從不失序的連線也會吃掉 SRAM。以論文比較口徑，100 Gb/s、8 微秒 RTT、100 個封包的 bandwidth-delay product 下，IRN 每條連線需要 125 bytes bitmap 加約 20 bytes metadata。把 145 bytes 乘上一百萬條 QP，就是約 145 MB；這遠高於一般 RNIC 願意留給 reorder state 的片上容量。

Eunomia 把接收工作分成三層。Packet driver 先辨識 Head、Last 與 PSN；Hybrid Dynamic（HD）bitmap 記錄已到達的序號；memory controller 管理所有連線共用的 2-byte blocks、metadata 與空閒表。資料本體仍可依原有 DMA 路徑寫入 host memory，Eunomia 主要保存「到達與否」，不是複製整個 payload。

Sender 需為每個 message 增加 33 bits：32-bit Head 指出訊息的第一個 PSN，1-bit Last 標示最後一包。這個開銷不能只報一個百分比，因為它依 payload 大小而變。若 payload 為 256 bytes，33 bits 約占 1.61%；1 KiB 時約 0.40%；4 KiB 時約 0.10%。計算與假設已放在[可重現腳本](/scripts/experiments/eunomia_bitmap_budget.py)與[輸出結果](/scripts/experiments/eunomia_bitmap_budget.results.json)。

## Circular 與 linear 區段讓 bitmap 擴張時免搬舊狀態

純 circular bitmap 容易回收。假設視窗有 8 bits，Head 是 0，已收到 0、1、2、4、6；當 3 抵達後，連續前綴可以推進到 5，前四個位置就能循環使用。問題出在擴張：如果新封包 PSN 15 抵達，8-bit 視窗容納不了。直接把 circular bitmap 從 8 擴到 16 bits，既要配置新區域，也可能要搬移與重新映射原有 bits，資料路徑硬體會變複雜。

Eunomia 將 bitmap 分成 circular portion 與 linear portion。第一個區段維持既有索引與回收；失序跨度超過容量時，memory controller 在尾端配置一個 linear block，讓新 PSN 先落在不會改變舊映射的位置。後續若又超過，再繼續接 block。等 circular 區段的缺口補齊、Head 前進並釋放舊區段後，linear portion 才合併成新的 circular portion。

![Hybrid Dynamic bitmap 的擴張與合併](/images/networking/2026-10-28/eunomia-hybrid-bitmap.svg)

用一個完整例子看資料流。QP 收到 message 的 Head=100、Last=115。100 到達時仍是 in-order，不需配置 bitmap；101、102 依序抵達也一樣。接著 108 先到，receiver 發現 103–107 是缺口，才配置第一個 16-bit block與 metadata，將相對位置 8 標成 1。112 到達時仍在同一 block；若 120 屬於下一個 message，就由新的 Head 隔離，不得誤用前一個 message 的窗口。

現在 103、104、105 陸續抵達。Head 可以前進，但 106、107 還沒到，所以 108 之後的 bits 仍保留。若 115 到達並帶 Last=1，receiver 已知道 message 的上界，仍不能提前完成；要等 106、107、109–111、113、114 全部補齊，bitmap 顯示從 Head 到 Last 連續，才把 completion 交給應用程式。若缺口長時間不補，timeout 仍回到既有 go-back-N 或 selective repeat，而不是假裝所有缺口都是重排。

這個機制同時處理兩個尺度。快路徑只做 bit set、Head 推進與 ACK/SACK；慢一點的配置路徑才處理 block 尋找、metadata 更新、區段合併。論文原型的 master memory array 以 2-byte block 管理，共示範 1024 個 blocks；每條連線保留 4-byte HD bitmap address。當連線第一次失序，controller 尋找 24 個連續 blocks 建立 48-byte metadata。作者也明列限制：若找不到連續 metadata 空間，非連續 linked metadata 還是後續工作。

## 記憶體節省來自只替失序連線付 metadata

Eunomia 的節省不是「每條連線的 bitmap 永遠更小」，而是把常駐成本變成共享池。沒有失序的 QP 只保留 4-byte 位址；active QP 才付 48-byte metadata 與實際 bitmap blocks。論文表格報告 Eunomia 每連線約 4–82 bytes，範圍取決於是否 active 與 bitmap 擴張程度。

要判斷何時划算，可以先做一個清楚的假設模型。以下不是論文的硬體量測，而是以一百萬條 QP、固定方案每條 32-byte bitmap 加 9-byte metadata、Eunomia 每條 4-byte base state、active QP 另付 48-byte metadata，加上每 16 PSN 使用 2 bytes block，計算共享池需求。

當 active QP 平均需要 64 bits bitmap 時，固定方案為 41 MB。若 5% QP 失序，動態方案約 6.8 MB；20% 時 15.2 MB；60% 時 37.6 MB；100% 時反而升到 60 MB。兩者交會約在 active ratio 66.1%。平均跨度只有 16 bits 時，交會點約 74%；跨度 256 bits 時，交會點降到約 46.3%。

![一百萬條 QP 的記憶體預算假設](/images/networking/2026-10-28/eunomia-memory-budget.svg)

這個計算揭露三個部署問題。第一，active ratio 比峰值 reorder depth 更重要；少數很深的失序可能仍比多數輕微失序便宜。第二，metadata 是固定稅。bitmap 很小時，48-byte metadata 甚至比 bits 本身大。第三，共享池需要公平性。若少數長 flow 無上限擴張，它們會耗盡 blocks，使新失序連線拿不到狀態。Eunomia 因此允許設定每連線上限；達上限後的新封包必須被丟棄或交回原有 loss recovery。

論文也展示這個反轉：在 20 條連線的 microbenchmark 中，隨失序連線比例上升，動態配置一開始省記憶體；超過約六成後，metadata 與配置成本可能讓總量高於固定配置。這不是設計失敗，而是動態配置的適用邊界。部署前要量測的是「同時 active 的失序 QP 分布」，而不是只看平均 packet reordering rate。

## 配置器必須在封包時間內回答三個問題

共享狀態省下容量後，控制器必須回答三個原本不存在的問題：誰先取得 block、何時歸還、拿不到時怎麼退回。第一個問題是 admission。假設 100 Gb/s port 收到 1,500-byte packets，線速約每 120 奈秒出現一包；即使硬體平行處理，第一次 OOO 同時觸發 metadata 建立與 block 搜尋，也不能讓單一 allocator 鎖住所有 queue。實作上需要把 free-block bitmap 分 bank、把 QP hash 到不同 allocation queue，或為每個 ingress pipeline 預留小型 local cache。否則 Eunomia 雖減少 SRAM，卻可能把突發失序轉成 controller head-of-line blocking。

第二個問題是 reclamation。bitmap 的 bit 可以隨 Head 前進而清除，metadata 卻不能因暫時沒有缺口就立刻釋放。若釋放門檻太積極，同一條多路徑連線下一個 burst 又要重新配置，allocator traffic 會振盪；若保留太久，已回復有序的 QP 仍占著 48-byte metadata。可行策略是加 idle epoch：連續若干 RTT 沒有 OOO，才把 block 歸還共享池。以 8 微秒 RTT、保留 32 RTT 為例，狀態至少留 256 微秒，能吸收微突發，又不至於在流結束後停留數秒。這個數字應由 trace 中的 reorder burst gap 校準，不能只憑平均流長設定。

第三個問題是 exhaustion。當 free blocks 低於保留水位，控制器可依序採取四級動作：停止替既有 QP 擴張、拒絕新 metadata、對越界 PSN 回 NACK、最後退回既有 go-back-N。這條 failure path 必須明確，因為「失序支援暫時退化」比「部分 QP 永遠等不到 completion」更容易營運。遙測至少要提供 pool occupancy、allocation latency、allocation miss、每 QP cap hit、bitmap merge 次數與 fallback 次數；若只能看到整體 FCT，事故發生時無法分辨是 fabric 壅塞、真正掉包，還是 reorder state 被耗盡。

### 一次 256-PSN 失序如何消耗共享池

沿用 16-bit、2-byte block。QP 首次看到超前封包時，配置 48-byte metadata 與一個 2-byte block；若最遠 PSN 距 Head 為 255，需要 16 個 blocks，也就是 32 bytes bitmap。加上 metadata，這條 active QP 使用 80 bytes，再加每 QP 原有的 4-byte address，共 84 bytes。這與論文表中的 4–82 bytes 只差口徑：表格把常駐 address 與 active 結構分開表達；本文預算圖則把兩者都算進全系統總量。

如果同一百萬 QP 中只有一萬條出現這種最深跨度，額外 active state 約 0.8 MB，加上所有 QP 的 4 MB base address，仍遠低於每條固定配置 41 bytes 的 41 MB。若六十萬條都達到 256-PSN 跨度，active state 就約 48 MB，再加 base 4 MB，已超過固定方案。這也說明 active ratio 與 span 必須聯合觀察：只報「最大失序 256 包」會高估容量，只報「平均失序連線 5%」又可能漏掉少數連線持續占滿 pool。

Block size 也不是越小越好。2-byte block 的內部浪費低，卻增加鏈接、allocation 與 merge 次數；64-byte block 更容易以 SRAM row 讀寫，但只有幾個 OOO packets 時會浪費大部分 bits。產品化時可採兩級 slab：常見小跨度先拿小 block，超過門檻後換成大 block；代價是 controller 還要處理兩種 free list 與遷移。Eunomia 論文選擇固定 2-byte block，先證明資料結構可擴張，沒有宣稱已找到所有 RNIC 的最佳粒度。

### 連線與裝置故障不能留下幽靈狀態

正常 close 時，QP context 可以帶著 bitmap 一起回收；異常情況更麻煩。若 receiver reset，sender 仍可能重送舊 PSN，新建立的 QP 必須用 generation 或 connection identity 隔離舊封包，否則過期封包可能把新 bitmap 的 bit 設成 1。若 memory controller 更新 metadata 到一半發生錯誤，Head、Tail 與 block owner 也要能以一致順序重建，不能讓同一 block 同時屬於兩條 QP。

一個保守的寫入次序是先標記 block owner，再更新相對地址，最後才公布新的 Tail；回收則先讓 QP 不再引用 block，再清 owner。任何中途失敗都偏向暫時洩漏容量，而不是錯把別人的到達狀態當成自己的資料。洩漏可由背景 scrubber 依 owner 與 QP generation 回收；跨連線錯配則可能直接破壞 RDMA 的資料正確性。這些 recovery 行為尚未在論文的單 FPGA packet driver 中完整驗證，卻是從研究原型走向 NIC firmware 時最先要補的項目。

實際驗收還應把這些計數器與 flow completion 串在一起。當 p99 上升時，若 allocation miss 先升、PFC pause 沒升，問題更可能在端點狀態；若 pause 與 queue depth 同時升，則應先處理 fabric hotspot。這種可觀測性可避免把所有尾延遲都歸咎於 packet spraying。

## SACK 阻止正常重排觸發丟包修補

只記 bitmap 還不夠，sender 必須知道缺口附近哪些封包已經到達。Eunomia 的 ordering feedback 與 congestion feedback 分開：ACK 表示新的連續前綴，SACK 表示超前抵達的 PSN，NACK 表示 receiver 無法處理或視窗越界。論文模擬中，ordering ACK 流量約帶來 5% 額外負載；壅塞控制仍由 DCQCN 等既有機制負責。

分離兩種回饋很重要。若把 SACK 視為壅塞訊號，packet spraying 造成的路徑延遲差會讓 sender 無謂降速；若把所有缺口都視為重排，真正遺失又會拖到 timeout。Eunomia 的判斷是先保留 OOO 到達狀態，讓短暫缺口有時間補齊；既有 timeout 與 recovery 邏輯仍負責證明「不是只晚到，而是需要重傳」。

這也解釋為什麼 Eunomia 與 [上一篇 IRN 深度文](/networking/2026/10/21/irn-selective-retransmission-rdma-completion.html)互補。IRN 用 BDP 大小的固定 bitmap 與 selective retransmission，目標是讓有損網路不必依賴 PFC；Eunomia 把 bitmap 改成依失序需求擴張，目標是承受 packet spraying 的更大 reorder window。兩者都避免 go-back-N 浪費，但容量模型與首要故障不同。

在作者的 ns-3 設定中，網路是 8×8 Clos、128 hosts、100 Gb/s links、1 微秒 propagation delay、1:2 oversubscription、9 MB shared switch buffer，並開啟 PFC 與 DCQCN。以 AliStorage 工作負載比較時，細粒度負載平衡加 Eunomia 相對 ECMP 的平均 FCT 最多降低 85%、尾端最多 91%；相對 ConWeave 最高約降低 53% 與 55%。作者也報告 PFC pause 最多下降約 99%，原因是 packet spraying 先降低 hotspot，再由 endpoint 吸收重排。

這些數字證明的是「在該模擬環境裡，端點可承受失序後，細粒度負載平衡的上限很高」，不是所有 fabric 都會得到相同幅度。工作負載、oversubscription、buffer、ECMP entropy、路徑延遲差與 RNIC implementation 都會改變結果。更保守的驗證方式，是先重播自己的 flow size distribution 與 path delay trace，再比較 p50/p99 FCT、pause duration、SACK bandwidth、bitmap occupancy 與 block allocation failure。

## 完成語意使 SEND 與 WRITE 付出不同代價

RDMA 的困難不只在封包是否到齊，也在何時可以對應用程式宣告完成。SEND/RECV 比較直觀：receiver 已知道 message boundary，可以讓 OOO data 寫入預定位置，但 completion queue entry 必須等 Head 到 Last 全部連續。Eunomia 的 Last bit 讓 RNIC 知道最後一個 PSN，不會因較後封包先到就過早完成。

RDMA WRITE 更敏感。遠端 CPU 通常不參與，而且應用程式可能把最後一筆 write 或 immediate data 當成「前面的內容都可讀」的信號。若末包先經較快路徑抵達，單靠 receiver bitmap 雖知道還有缺口，卻可能已把完成可見性暴露給軟體。

Eunomia 的主要方案在 sender 端延後末包：先送前面所有 packets，等到它們都被連續確認，再送 Last packet。這維持既有 receiver completion 語意，但為 WRITE 多付一個 RTT。若 RTT 為 8 微秒，短 message 的完成時間可能直接增加約 8 微秒；長 flow 已經跨越多個 RTT 時，相對比例較小。

替代方案是 receiver 暫存末包，直到 bitmap 連續後才 DMA。它省掉 sender 額外 RTT，卻要讓 RNIC 保存 payload 或額外做一次 PCIe 搬移，並處理暫存空間耗盡。這是典型的端到端取捨：等待放在 sender，成本是 latency；等待放在 receiver，成本是 buffer、PCIe traffic 與更複雜的完成閘門。

## 三個方案把等待與狀態放在不同位置

![端點與交換器重排方案的取捨](/images/networking/2026-10-28/eunomia-design-tradeoffs.svg)

第一個替代方案是 IRN 類固定 BDP bitmap。它的優點是索引、時序與容量上界清楚，且 selective retransmission 已直接對準 loss recovery。若 fabric 的最大 reorder depth 本來就小於 BDP，而且 QP 數量可控，固定配置可能比共享 allocator 更容易驗證。它的弱點是每條 QP 都付最壞狀態，在百萬 QP 或高度稀疏失序時浪費 SRAM。

第二個替代方案是 ConWeave 類 in-network reordering。目的端 ToR 能在封包進 RNIC 前恢復順序，因此 commodity RNIC 不需修改；代價是交換器要保存 flowlet／route state 與 reorder queue，且 failure、路由狀態回收與跨 ToR 部署成為新的控制面問題。論文的 failure simulation 甚至觀察到 ConWeave 在超過 2% link failure 後無 flow 完成，作者歸因於 route-state 問題；這是特定模擬結果，不宜外推成所有實作的定論。

第三個替代方案是限制 packet spraying，只在 elephant flows 或遙測顯示 hotspot 時啟用。這能把 reorder state 壓到小範圍，也降低 ACK 流量；但需要準確分類 flow、快速偵測 congestion，切換期間仍會遇到 reorder。對短流占比高、路徑相近的 fabric，這可能比全流量 spraying 更務實。

Eunomia 的 FPGA prototype 以 SystemVerilog 實作於 AMD Kintex UltraScale+ XCKU5P KCU116，使用 Vivado 2022.2。整體約 82,201 LUT、3,434 registers；memory controller 約 81,029 LUT，是主要成本，HD bitmap 模組約 2,180 LUT。這個原型證明資料結構能進硬體，但沒有等同商用 RNIC tape-out：LUT 與 ASIC SRAM/logic 面積不能直接換算，單 packet driver 也還未覆蓋多 port、完整 transport pipeline、PCIe contention 與 firmware recovery。

未來 12 個月若要把 Eunomia 方向帶進產品，最值得先做三件事。其一，從 production trace 建立每毫秒 active OOO QP、reorder span 與持續時間的聯合分布，據此決定 block size、metadata pool 與 per-QP cap。其二，把 allocation miss、SACK bandwidth 與 WRITE extra RTT 放進 SLO，而不只看平均 FCT。其三，做故障注入：link flap、route change、receiver restart、metadata corruption 與 block exhaustion 時，確保系統能退回既有 recovery，不會把缺口永久卡在完成閘門。

Eunomia 最有價值的地方不是宣稱 packet spraying 已經沒有代價，而是把代價從「所有 QP 都先付固定 bitmap」改成「真的失序時，按跨度租用共享狀態」。只要 active ratio、allocator 延遲與 completion 語意都被量測，這個設計能讓負載平衡從 flow-level hash 進一步走向 packet-level。反過來，若大多數 QP 長期失序、metadata 連續空間不足，或 WRITE 的額外 RTT 無法接受，固定端點狀態或目的端 ToR 重排仍可能是更穩健的選擇。

## 證據範圍

本文的機制、資源數字與效能結果以 2024-12-11 發布的 [Eunomia 論文](https://arxiv.org/abs/2412.08540)及 [APNet 2025 官方議程](https://conferences.sigcomm.org/events/apnet2025/apnetprogram.php)為主。效能來自 ns-3 模擬，硬體成本來自單一 FPGA prototype，尚不是商用 RNIC 的實測結果。文中的一百萬 QP 記憶體圖是明示假設的重算，用來找動態與固定配置交會點，不是作者量測；完整數值可由附帶腳本重建。

## 參考資料

- Sana Mahmood、Jinqi Lu、Soudeh Ghorbani，〈[Eunomia: Enabling General and Efficient Packet Reordering Support for RDMA](https://arxiv.org/abs/2412.08540)〉，2024-12-11。
- APNet 2025，〈[Reinventing RDMA session](https://conferences.sigcomm.org/events/apnet2025/apnetprogram.php)〉，2025-08-07。
- Yiwen Lu 等，〈[Multi-Path Transport for RDMA in Datacenters](https://www.usenix.org/conference/nsdi18/presentation/lu)〉，NSDI 2018。
- Jiaqi Gao 等，〈[ConWeave: Reimagining Congestion Control in Lossless Ethernet](https://conferences.sigcomm.org/sigcomm/2023/program.html)〉，SIGCOMM 2023。
- Inho Cho 等，〈[Breaking the Transience-Equilibrium Nexus: A New Approach to Datacenter Packet Transport](https://arxiv.org/abs/1806.08159)〉，IRN，2018。
