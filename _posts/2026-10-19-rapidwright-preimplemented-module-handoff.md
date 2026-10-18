---
layout: post
title: "RapidWright 讓 FPGA 實體模組成為可重用的交付物"
date: 2026-10-19 06:04:03 +0800
domain: ic-design-platform
categories: ic-design-platform
series: sota-r2g-cad
permalink: /ic-design-platform/2026/10/19/rapidwright-preimplemented-module-handoff.html
description: "AMD Research 的 RapidWright 以 checkpoint 重用局部佈局與佈線，把建庫和系統整合分開；模組重複、介面穩定時能攤提實作成本，頻繁改動或全域連線主導時則可能失去優勢。"
takeaways:
  - who: "FPGA 整合工程師"
    value: "FPGA 整合工程師可透過 RapidWright 重用已完成局部佈局與佈線的模組，讓後續迭代集中於組合和全域連線，但必須預先固定介面、時脈及可用的實體位置，並保留最後一輪工具檢查。"
  - who: "IP 與實體設計團隊"
    value: "IP 與實體設計團隊承擔多種模組實作的建庫、相容性及維護成本，重用次數增加後才有機會回收投入；若 RTL 或裝置條件經常變動，重建成本會抵銷省下的工作時數。"
  - who: "AMD Research"
    value: "AMD Research 提供的 RapidWright 公開方法把實體 checkpoint 變成可程式化的組合材料，使工程師能保存局部高品質解，也讓設計流程持續依賴 Vivado 的最終全域實作與裝置資料。"
  - who: "CAD 平台負責人"
    value: "CAD 平台負責人應同時計入冷啟動建庫與暖啟動整合，並與完整重跑及固定 shell 比較；假設算例到第十二版才開始省時，說明穩定重用的壽命比單次拼接速度更能左右導入結果。"
---

一個 FPGA 系統若含有數百個相似運算單元，每次修改頂層連線都重新解整顆設計，會重複支付大量局部實作成本。完整重跑仍有合理性：工具能一起調整邏輯、位置與線路，跨模組路徑也能獲得較多最佳化自由。但當功能單元已經穩定、變動主要出現在組合方式，保存局部實體結果就形成另一條工程路線。

AMD Research 的 [RapidWright](https://www.rapidwright.io/docs/Introduction.html) 提供可讀寫 Vivado design checkpoint 的 Java 設計介面，讓工程師操作邏輯及實體 netlist。這篇聚焦它公開的預先實作模組方法：先付費找到可重用的局部解，再把整合工作縮小到選擇模組版本、安排位置和連接模組。研究主體是公司研究團隊公開的 CAD 方法與 Vivado 交接，官方程式碼則讓這條方法可以逐步檢查。

<figure>
<a href="/images/ic-design-platform/2026-10-19/rapidwright-module-handoff.svg"><img src="/images/ic-design-platform/2026-10-19/rapidwright-module-handoff.svg" alt="設計團隊固定 RTL、裝置與時脈條件，Vivado 先建立局部實作，RapidWright 重用並拼接模組，再交回 Vivado 完成全域路由與整合檢查。" width="640" height="910"></a>
<figcaption>圖一：依據 <a href="https://www.rapidwright.io/docs/PreImplemented_Module_Flow.html#high-performance-flow">RapidWright 預先實作流程</a>整理。圖中的功能需求與系統行為檢查是整合責任；箭頭表示交付順序，沒有表示速度比例。</figcaption>
</figure>

沿圖往下看，兩次 Vivado 工作處理不同規模的問題。第一次針對模組建立實體版本，第二次解決組合後才存在的全域路徑。減少重做的工程，來自這個分工。

## 一份 DCP 同時帶著邏輯與實體狀態

RTL 描述電路行為，綜合後的 netlist 描述元件及連接；完成實作後，還多出元件放在哪個位置、net 使用哪些路由資源。RapidWright 操作的 DCP 是設計快照，依產生階段可包含 netlist、constraints、placement 與 routing。模組交出去的材料因此超過一份可重新綜合的 RTL。[Design Checkpoints 文件](https://www.rapidwright.io/docs/Design_Checkpoints.html)

這會改變 IP 團隊和整合團隊的工作分配。IP 團隊除了提供接埠及功能，還要選出足以重用的實體配置；整合團隊則拿這些配置安排整個系統。一次已投入的實體最佳化可以跨多個實例及版本攤提，代價是部分局部決策提前固定。

完整路徑可以具體列成下表。前兩列是設計團隊在採用此方法前仍需完成的工程責任，後面才進入公開示範的實體組合流程。

| 階段 | 輸入與可改變內容 | 交付物與接收工作 |
| --- | --- | --- |
| 設計需求與 IP 整合 | 功能、吞吐量、latency、時脈、裝置及板級 I/O | 固定 RTL、XDC 和介面規格；接收方確認 pipeline 與 reset 語意 |
| 功能驗證與必要形式檢查 | RTL、測試、協定及跨時脈假設 | 功能結果與版本；模組新增一拍須同步修改系統預期 |
| 模組 OOC 實作 | 綜合 netlist、pblock、時脈目標與工具選項 | 局部 placed-and-routed DCP、接埠資料及報告 |
| 模組庫與系統組合 | 模組實體版本、合法位置、頂層連接 | RapidWright 輸出的組合 DCP；保留局部實體結果 |
| 全域完成與板級交付 | 系統 DCP、全域 clocks、跨模組 net、I/O 條件 | 完整 routing、timing、DRC，再依專案要求產生 bitstream 與做板測 |

FPGA 應用在此交付的是已製造晶片的配置。ASIC R2G 的 standard-cell library、製程 SDC、DFT 插入、APR、GDS signoff 和封裝設計，屬於另一條矽晶片製造交付鏈；兩者可比較交接方式，輸出形式及責任仍各自成立。若用 FPGA 驗證 SoC，DFT 及封裝需求要留在 ASIC 計畫中，板級原型只覆蓋選定的功能與系統情境。

## 同一份電路要有不同的實體版本

可重用的實體模組需要符合目標 FPGA 的資源排列。FPGA 內部的邏輯、BRAM、DSP 與特殊區域有固定位置，矩形尺寸相同只解決幾何外形；移動模組還要找到能容納其元件與路由的相容位置。

[官方 PicoBlaze 教學第一部分](https://www.rapidwright.io/docs/PreImplemented_Modules_Part_I.html)提供一個直覺例子：目標是 VU3P 裝置上的小型微控制器，理論資源下限可估出十五個 slice，但三欄乘五列的緊密配置失敗，四欄乘五列才取得可用結果；流程另用 `CONTAIN_ROUTING` 約束局部路由。局部面積壓得越緊，搜尋與佈線越容易受限制，最小資源數因此只是起點。

由此可推得一項平台設計原則：模組庫應保存同一電路的幾種可用實體形狀，讓整合工程師依位置選擇。省去整顆設計的重跑後，工程努力會轉向「哪些形狀能反覆使用」。如果每次都為新的位置製作唯一形狀，資料庫雖持續膨脹，實際攤提次數卻很低。

目前 [PicoBlazeArray.java](https://github.com/Xilinx/RapidWright/blob/adcd4c7cdfc9aeec3ce4e0025e0a35f15af0fa6a/src/com/xilinx/rapidwright/examples/PicoBlazeArray.java) 把這個交接寫得很具體。程式讀取多份 `pblock*.dcp` 及 metadata，把 BRAM 當模組 anchor，逐一檢查候選位置，選擇可用實作，再建立實例及其接埠連接；它也略過上下方 clock-region 區域以避開特殊資源情境。範例含一般 module 與多實作版本兩條程式路徑。

程式中的「同一種電路、多個實體版本」可以避免為每個實例各做一次搜尋，卻增加版本配對工作。參考設計可以把一個模組項目索引到 RTL／netlist digest、part 與 speed grade、工具 build、XDC、接埠及各實作的 pblock；系統組合另記錄每個 instance 選了哪個版本、放在哪裡。這是團隊可加上的資料設計，官方 metadata 格式與這份索引分開維護。

以模組名稱作唯一索引會留下風險。工程師即使保留相同 module name，也可能更換 BRAM 模式或 reset 行為；若仍取回舊 DCP，最後產物就含有舊功能。索引內容應先決定可重用範圍，檔名只提供查找入口。相反地，僅更改 instance 名稱時，局部電路和實體條件可能完全相同，過度保守的重建又會吃掉收益。

推論到資源安排，緊密包裝和容易搬移還會產生競爭。多留一圈路由空間，可能讓單一模組比較容易閉合，卻降低整顆裝置可容納的實例數；為每個位置增加一種版本，又會拉高探索與維護成本。實體設計團隊應同時記錄每種形狀的資源占用、合法位置數及實際使用次數，讓庫的成長跟隨已發生的需求。

這也影響工作優先順序。一個只使用一次的特殊模組，即使局部搜尋很成功，也可能排在可服務數十個實例的共用模組之後。整合計畫先固定常用介面，實體團隊才容易集中改善少數高重用版本；若前端持續改規格，後端建庫會變成追趕需求的額外工序。

## 把搜尋成本移到可重複使用的階段

第二個機制是改變計算工作的時點。單次專案可以承受一次完整探索，多次迭代則有機會共用探索結果。[預先實作流程文件](https://www.rapidwright.io/docs/PreImplemented_Module_Flow.html#module-cache)描述，Vivado 先對每種 IP 做 OOC 綜合與實作；RapidWright 的模組資料包含實體資料、共用的壓縮 EDIF 與介面 metadata。BlockStitcher 依頂層連接組合模組，最後由 Vivado 完成全域路由。

這項分工帶來兩種時間。建庫的冷啟動可能很慢，已有合用模組時的暖啟動才會快。對每天只有一個新電路、很少重用的團隊，冷啟動接近常態；對同一組功能單元反覆改系統組合的團隊，暖啟動占比才有機會提高。導入決策因此應按實際版本序列計帳，包含失敗搜尋與被淘汰的模組。

時脈也是建庫與整合間的重要相依。局部路徑表現很好，跨模組長線仍可能成為 critical path。設計若允許額外 latency，可以在模組間增加 pipeline，換取較短的組合路徑；但資料、valid、ready、reset 和控制資訊都要保持對齊。只替資料加暫存器而沿用原控制協定，可能讓頻率改善伴隨功能錯誤。

同樣地，高複製次數通常有利於攤提，但高度密集的全對全通訊會把成本推回頂層路由。整合者應分開觀察「模組內部路徑」與「跨模組路徑」的惡化程度。若後者已支配設計，繼續提高模組庫的局部品質，改善空間就會縮小；需要回到連線拓樸、位置安排或系統 pipeline。

## 從三種 PicoBlaze 實作走到整個陣列

[官方教學第二部分](https://www.rapidwright.io/docs/PreImplemented_Modules_Part_II.html)在三個 pblock 上組合兩種 placer directive、兩種 router directive 和十五個 clock-uncertainty 設定，共一百八十次候選實作；再把選出的局部實作組成三百九十六個 PicoBlaze。這是指定 VU3P 教學的流程與規模，讀者可以順著參數和產物重建操作。

完整案例的輸入包括微控制器 netlist、三種區域配置、時脈目標與候選工具設定。探索階段先比較每種區域可取得的局部解；陣列建立階段則安排 instance，把相鄰單元的八位元接埠連起來，補上系統 clock、reset 及頂層 I/O，再輸出 DCP。接收工程師得到的是一份含既有局部路由的系統設計，仍要處理新增的全域關係。[範例連接程式](https://github.com/Xilinx/RapidWright/blob/adcd4c7cdfc9aeec3ce4e0025e0a35f15af0fa6a/src/com/xilinx/rapidwright/examples/PicoBlazeArray.java)

教學接著明列 `update_clock_routing`、`route_design` 和 `report_timing_summary`；其範例報告給出約 365 MHz 的時脈能力。這個結果伴隨模組建庫、裝置和連線條件，適合用來理解完整交接，不能拆成「拼接後自然保有原頻率」的保證。[陣列全域完成步驟](https://www.rapidwright.io/docs/PreImplemented_Modules_Part_II.html)

若重跑此案例，建議固定一組 Vivado 與 RapidWright 版本，保留每個候選的實際輸入及 timing report，再記錄陣列建立前後的 clock 與 constraint。檢查至少應覆蓋 setup、hold、未受約束的路徑、route status 及 DRC；最後再以功能測試核對系統連接。零退出碼只描述程序結束，工程師仍需閱讀哪些路徑被計入分析。

這條流程最有意思的分工，是 IP 團隊可以提供「已找到的一小組好解」，整合者再決定哪些解值得組合。若局部選擇導致全域失敗，應保留那份組合 DCP 和報告，換一種模組配置或安排後再完成全域實作；若發現模組本身功能變動，則回到建庫階段。兩種失敗的重跑範圍不同。

## 十二次迭代才回收的假設成本

把官方的一百八十次搜尋作為工作數量，另假設每次花十五分鐘，建庫就需要 `180 × 0.25 = 45` 工作小時。再假設完整重跑每版六小時，已有模組庫後，拼接、全域路由與共同檢查合計每版兩小時。這些時間全部是明示假設，以下程式實跑的是成本模型。

設版本數為 N，完整重跑成本是 `6N`，重用成本是 `45 + 2N`，單位皆為 implementation-job hours，也就是各工具工作時數加總。故 `45 + 2N < 6N` 要求 `N > 11.25`，第十二版才開始節省。兩條路線應包含相同必要檢查，避免讓完整重跑負擔較嚴格的流程。

| 版本數 | 完整重跑 | 建庫加重用 | 重用節省 |
| --- | --- | --- | --- |
| 1 | 6 h | 47 h | −41 h |
| 5 | 30 h | 55 h | −25 h |
| 12 | 72 h | 69 h | 3 h |
| 20 | 120 h | 85 h | 35 h |

<figure>
<a href="/images/ic-design-platform/2026-10-19/rapidwright-reuse-amortization.svg"><img src="/images/ic-design-platform/2026-10-19/rapidwright-reuse-amortization.svg" alt="假設建庫需要四十五工作小時，每版由六小時降到兩小時，到第十二版才回本；二十版可省三十五小時，但每十版重建一次會反而多花十小時。" width="640" height="880" loading="lazy"></a>
<figcaption>圖二：假設算例，數值由<a href="https://github.com/rightson/rightson.github.io/blob/main/scripts/experiments/rapidwright_reuse_cost.py">成本模型程式</a>產生；不是 Vivado 或 RapidWright 的效能量測。</figcaption>
</figure>

若每十版就因介面或實體條件變更而完整重建，二十版要支付兩次建庫，成本變成 `2 × 45 + 20 × 2 = 130 h`，比完整重跑的一百二十小時多十小時。同一套暖啟動數字，足以支持相反的導入結果；造成差異的是模組庫可用多久。

[實跑結果檔](https://github.com/rightson/rightson.github.io/blob/main/scripts/experiments/rapidwright_reuse_cost.results.json)保存四組穩定重用情境、十版重建情境及假設。程式可用 `python3 scripts/experiments/rapidwright_reuse_cost.py` 重跑，另以逐版累加核對重建發生在第一版與第十一版。這個測試檢查計帳及臨界值，FPGA placement、routing 和 PPA 均未執行。

工作時數和日曆時間還要分開。如果有十二個可同時工作的槽位，四十五工作小時的理想計算下限是 3.75 小時，另加啟動、等待與最慢候選的影響；共享資源緊張時，建庫可能跨越更久。若不同階段使用不同核心數或授權 token，還應分別換算 CPU-hours 與 license-hours。CAD 團隊維護模組庫、除錯及審查的人工成本，也應列在同一份導入評估。

## 完整重跑與固定 shell 都是合理選擇

完整實作保有最多全域最佳化自由，也省下自訂模組庫的維護。當模組變動頻繁、設計較小或跨模組路徑主導時，它是有力的比較基準。選用 RapidWright 之前，應先確認現有工具流程已正常設定，避免把錯誤 baseline 的耗時算成重用收益。

另一條路是固定系統 shell，只替換少量變動邏輯。[RapidWright 的 timing-closed shell 教學](https://www.rapidwright.io/docs/ReusingTimingClosedLogicAsAShell.html)從完整實作移除動態模組，保留靜態邏輯，再把新內容放回原介面；它使用保留介面與鎖定實體路由的步驟。這種重用固定平台的位置，與搬動數百個模組的工作形狀不同。

| 路線 | 適合的變動形狀 | 主要代價 |
| --- | --- | --- |
| 完整 Vivado 實作 | 大量 RTL 或全域架構一起改動 | 每版支付較多實作時間，保留較大最佳化自由 |
| RapidWright 預先實作模組 | 穩定單元大量複製，組合經常調整 | 建庫與合法位置管理，局部固定後犧牲部分全域自由 |
| 固定 timing-closed shell | 靜態平台穩定，只有局部內容更換 | 介面與周邊資源限制，新增內容仍須完成整合實作 |

shell 做法也會反過來影響功能分工。保留的介面越穩定，平台重用越容易；若應用需要新增 clock、增加外部頻寬或大改 reset，既有 shell 的維護範圍就會擴大。模組重定位、固定 shell 以及裝置執行時的動態部分重配置，各自處理不同階段的問題，團隊應先明確選定要縮短哪一段迭代。

## 三家公司把重用放在不同交接點

跨公司比較應看實際交付物。[NVIDIA NVDLA 整合手冊](https://nvdla.org/hw/v2/integration_guide.html#synthesis)提供配置後 RTL、製程相關 cell 替換及綜合輸入輸出的接點；[Arm Neoverse CSS](https://www.arm.com/products/cloud-datacenter/neoverse-compute-subsystems)則以已驗證、針對目標製程最佳化的運算子系統，替合作夥伴承擔部分非差異化整合工作。這兩者分別反映公開參考 IP 流程及商用子系統交付。

RapidWright 的公開方法再把重用推到 FPGA 的局部 placed-and-routed 狀態。三者都能減少下一個團隊需要重做的工作，限制則隨交付深度增加：RTL 接收者有較多重新實作自由，實體模組接收者要遵守更具體的裝置與位置條件。這是依交付物作出的工程比較，沒有對三家公司做速度排名。

[Xilinx Research Labs 的 Chris Lavin 在 2018 年 FCCM 的原始論文](https://www.rapidwright.io/docs/_downloads/ba6c3a2f111b835c0e91e90884c0d55e/FCCM18-RapidWright.pdf)已把局部實作重用與模組複製列為設計策略，並區分單純 RTL 重整與預先實作的結果。這個有日期的前例提醒我們，效益可能同時來自架構重整和實體重用；比較時應保留「原始設計、重整後完整實作、重整後模組重用」三組結果，才看得出哪一筆投入產生改善。

從團隊分工推論，長期資產會由單一專案的 Tcl recipe，延伸到有明確適用條件的實體模組庫。工具工作可能減少，IP 團隊的維護及整合溝通卻會增加；依賴也持續集中在裝置資料、DCP 相容性與 Vivado 完成流程。若 library owner 沒有資源維護版本，整合工程師就得自行承擔相容性調查，節省的運算成本可能換成更多人力。

未來三個月，團隊可選一個具有重複單元的公開設計，固定工具與裝置，對十次真實的設計變更同時跑完整實作、模組重用與固定 shell。逐版保存冷暖成本、人工介入時間、跨模組關鍵路徑和最終 timing；若只有暖啟動變快、累積成本及品質反而惡化，導入範圍就應縮小。若跨多次變更仍能維持相同功能及時脈要求，再增加模組庫覆蓋。

[前一篇 NVDLA 文章](/eda/2026/09/30/nvidia-nvdla-config-to-synthesis-handoff.html)停在生成 RTL、製程相關 views 與綜合資料的交接；RapidWright 補上保存局部實體結果再整合的一段。穩定介面、大量重複且全域連線可控制的設計，最有機會用前期建庫換取較短迭代；下一個實驗應直接量出模組庫在需求變動下的有效壽命。

## 證據範圍

RapidWright 文件此次頁首為 2026.1.1-beta，PicoBlaze 教學未提供可據以推定所有範例數字更新日期的版本記錄；因此本文把數字標成官方教學結果，不稱為 2026 年重新量測。原始論文是 2018 年 Xilinx Research Labs 研究，現行文件將 RapidWright 列為 AMD Research 提供的框架；這些資料不足以證明 AMD 內部 ASIC 量產平台採用同一流程。

本文讀取官方程式碼 commit `adcd4c7cdfc9aeec3ce4e0025e0a35f15af0fa6a` 作為介面對照，沒有執行 Vivado、RapidWright 或 FPGA 板測。約 365 MHz 僅是官方指定陣列案例數字；一百八十次搜尋沒有搭配可直接引用到本文成本模型的實測工時。程式輸出全部是合成成本試算，沒有量測 PPA、功耗、license 消耗或真實開發時程。

DCP 文件明示加密設計與跨工具版本相容性的限制；checkpoint reader/writer 的 API library 另有修改版 Xilinx 授權條款。公開預先實作流程也註明其 RapidWright router 當前停用，本文因此把最終全域路由交回 Vivado。公司比較只涵蓋各自已公開的交付位置，不推定完整內部 CAD 架構，也不外推到商用先進製程 signoff。

## 參考資料

- [RapidWright Introduction](https://www.rapidwright.io/docs/Introduction.html)及[Design Checkpoints](https://www.rapidwright.io/docs/Design_Checkpoints.html)，AMD Research 公開文件，頁首版本 2026.1.1-beta。
- [A Pre-implemented Module Flow](https://www.rapidwright.io/docs/PreImplemented_Module_Flow.html)，模組庫、BlockStitcher、Vivado 交接及流程限制。
- [Pre-implemented Modules Part I](https://www.rapidwright.io/docs/PreImplemented_Modules_Part_I.html)與[Part II](https://www.rapidwright.io/docs/PreImplemented_Modules_Part_II.html)，VU3P PicoBlaze 教學。
- [Reusing Timing-closed Logic as a Shell](https://www.rapidwright.io/docs/ReusingTimingClosedLogicAsAShell.html)，固定實體平台的互補方法。
- Chris Lavin／Xilinx Research Labs，[RapidWright: Enabling Custom Crafted Implementations for FPGAs](https://www.rapidwright.io/docs/_downloads/ba6c3a2f111b835c0e91e90884c0d55e/FCCM18-RapidWright.pdf)，FCCM 2018。
- [PicoBlazeArray.java 固定版本](https://github.com/Xilinx/RapidWright/blob/adcd4c7cdfc9aeec3ce4e0025e0a35f15af0fa6a/src/com/xilinx/rapidwright/examples/PicoBlazeArray.java)，模組載入、位置判定、接埠連接與 DCP 輸出。
- [NVDLA Integrator’s Manual](https://nvdla.org/hw/v2/integration_guide.html)及[Arm Neoverse CSS](https://www.arm.com/products/cloud-datacenter/neoverse-compute-subsystems)，用於交付物比較。

