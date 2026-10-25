---
layout: post
title: "Marvell 把 3DIC signoff 延伸到 die、封裝與完整堆疊"
date: 2026-10-26 06:03:58 +0800
domain: ic-design-platform
categories: ic-design-platform
series: sota-r2g-cad
permalink: /ic-design-platform/2026/10/26/marvell-3dic-physical-signoff-handoff.html
description: "Marvell 的公開 3DIC 方法先分別檢查 die、interposer 與 substrate，再以 3Dblox 和系統 netlist 組裝跨 die 連接與 ESD 路徑；它能提早暴露對位、連接及電阻問題，代價是新增一層系統描述、規則維護與高成本 P2P 工作。"
takeaways:
  - who: "Marvell 實體驗證團隊"
    value: "Marvell 實體驗證團隊把單顆 die、interposer、substrate 與完整 stack 分成可追溯的檢查層級，再以 3Dblox 和系統 netlist 串接幾何與邏輯關係，使跨 die 的 opens、shorts、對位和 ESD 路徑能在 tapeout 前被定位。"
  - who: "Chiplet 整合負責人"
    value: "Chiplet 整合負責人需維護 die 方向、介面、hybrid bond、TSV、BGA 與 power clamp 的共同描述；這份資料若與各 die 的 P&R 版本分離，完整 stack 即使通過工具，也可能檢查到錯誤組合。"
  - who: "CAD 平台團隊"
    value: "CAD 平台團隊可以把 TOPO、LDL、CD 與 P2P 排成不同頻率，讓早期迭代先處理拓樸與邏輯連接；Marvell 公開數據顯示 P2P 佔 Tier1 KGS 案例約八成 core-hours，因此完整工作仍應保留在重要里程碑。"
  - who: "EDA 工具供應商"
    value: "Siemens 與 Synopsys 的工具需把不同製程、foundry 與封裝格式轉成一致的跨層連接模型；3Dblox 標準化能降低轉譯摩擦，但規則 deck、電阻限制與 ESD 元件辨識仍依賴製程及專案資料。"
---

一顆 3DIC 可以讓每個 die 各自通過 DRC、LVS 與 ESD 檢查，組裝後仍留下錯誤。原因很具體：兩顆 die 的 hybrid bond pads 可能沒有對齊，彼此對應的 net 名稱可能不一致，從 package BGA 經 TSV 到上層 power clamp 的電阻也可能超過規則。單顆 die 的綠燈只覆蓋局部設計，無法描述跨越封裝的完整導電路徑。

Marvell 在 2025 年 WISH 發表的[完整論文](https://designthesolution.org/wp-content/uploads/2025/09/navigating-the-challenges-of-physical-verification-in-3dics-from-2d-to-3d-solutions-qi-mohannad-jeanne-abhijat-mike.pdf)，提供一個少見的具名公司案例：流程先完成各 die、interposer 與 substrate 的檢查，再組裝 3D layout 與系統 netlist，最後執行跨 die 連接、對位和六類 ESD 路徑檢查。公開簡報另列出工作時間、核心數、超過 24,000 條 die-to-die signal nets，以及 Tier1、Tier2 各九個 power domains，足以把方法轉成可計帳的平台交接。

<figure>
<a href="/images/ic-design-platform/2026-10-26/marvell-3dic-signoff-flow.svg"><img src="/images/ic-design-platform/2026-10-26/marvell-3dic-signoff-flow.svg" alt="Marvell 3DIC 實體 signoff 先分別檢查 SoC、HBM、interposer 與 substrate，再以 3Dblox 和系統 netlist 組裝，最後執行幾何、連接與 ESD 跨層檢查。" width="640" height="900"></a>
<figcaption>圖一：依據 Marvell <a href="https://www.gsaglobal.org/events/wp-content/uploads/sites/10/2024/12/process-3v2-qi-wang-wish25_navigating_challenges_pv_v3.pdf">WISH 2025 簡報</a>與<a href="https://designthesolution.org/wp-content/uploads/2025/09/navigating-the-challenges-of-physical-verification-in-3dics-from-2d-to-3d-solutions-qi-mohannad-jeanne-abhijat-mike.pdf">論文</a>重繪。流程方塊表示交付順序，沒有表示組織架構或 runtime 比例。</figcaption>
</figure>

沿圖往下看，3DIC signoff 多出的工作並非把多份 DRC 報告放在一起。它需要一個系統層描述，把各自正確的 die、封裝連接與保護元件組成同一張可檢查的圖。

## 三個局部結果要組成同一份系統狀態

Marvell 方法的第一層仍是熟悉的單體流程。SoC chiplets、HBM 和 dummy dies 各自執行 multi-DRC、antenna、LVS 與 ESD；interposer 和 substrate 則檢查其 routing、bump 與封裝規則。這些結果讓各團隊能在自己的設計資料上收斂，也保留不同 node、foundry 與工具所需的規則 deck。

第二層才建立完整 stack。論文寫明，layout assembly 使用 3Dblox 表達 die、interposer 與 substrate 的位置和介面，logical inter-die connectivity 則轉成可供比較的系統 netlist。IEEE P3537 將 3Dblox 定義為描述 chiplets、interposers、substrates 及其 connectivity 的模組化階層語言；標準化的用途，是讓不同工具交換同一份高階組裝意圖。[IEEE P3537 scope](https://standards.ieee.org/ieee/3537/11871/)

這個交接需要同時固定幾何與邏輯。幾何資料回答 die 的尺寸、方向、厚度、介面區域和相對位置；邏輯資料回答每一個 hybrid bond、micro-bump、C4 與 BGA 最終接到哪一條 net。完整 layout 抽出的連接若與 top-level system netlist 不一致，3DSTACK 類工具便可找出 open、short、缺失 label 或錯位的 bump。[Siemens Calibre 3DStack](https://www.siemens.com/en-us/products/ic/calibre-design/calibre-3d-ic/3dstack/)

因此 artifact 的責任可以分成四份：

| 交付層級 | 主要輸入 | 可變內容 | 接收端需要的結果 |
| --- | --- | --- | --- |
| 單顆 die | layout、netlist、製程 deck、bump 與 clamp 資料 | P&R 幾何、局部 routing、保護元件 | DRC／LVS／antenna／die ESD 結果與版本 |
| Interposer／substrate | package layout、RDL、C4、BGA、封裝規則 | 封裝走線、escape、尺寸與材料堆疊 | interposer 和 substrate 的連接及規則結果 |
| Assembly | 3Dblox、die transforms、介面對應、system netlist | die 放置、方向、連接映射 | 可抽取的完整 3D layout 與跨 die netlist |
| Stack signoff | 組裝 layout、系統 netlist、ESD 規則及各層結果 | waiver、規則設定、修正後的幾何與 routing | alignment、stack LVS、TOPO、P2P、CD 報告 |

版本關係是平台必須補上的部分。只用檔名連接這四層，會允許新 die layout 搭配舊 3Dblox，或讓 clamp library 更新後仍沿用舊 P2P 結果。參考設計可把每次 stack run 綁定 die layout digest、netlist digest、process deck revision、assembly description、tool build 和 waiver set；接收方看到 pass 時，也能知道它屬於哪一組實體輸入。

[前一篇 RapidWright 文章](/ic-design-platform/2026/10/19/rapidwright-preimplemented-module-handoff.html)保存局部 placed-and-routed module，讓全域整合者重用實體結果。Marvell 案例處理更晚的交接點：每個 die 已有自己的實體結果，平台還要證明完整封裝中的幾何、電氣連接與保護路徑一致。兩者共同之處是局部成功仍要經過系統層重新組合。

## Seal ring 進場後，P&R 看不到的幾何也要被檢查

第一個關鍵機制出現在 hybrid bonding 的 seal ring。Marvell 論文說明，seal ring 在 die assembly 之後依晶片尺寸加入，用來提供切割時的機械保護和環境隔離。它位於 P&R 工具之外，原本的 P&R 環境看不到新增區域，因此也無法替 seal ring 周邊安排 dummy hybrid bond pads。

Marvell 的做法是由插入流程自動產生符合 DRC 的 dummy HBPs，再把 Tier1 與 Tier2 的 projected pad locations 放入 floorplanning 對位檢查。這處理的是跨工具可見性：P&R 完成時的合法 layout，在 assembly 階段加入 seal ring 後多了新幾何；若平台沒有把新增物件送回檢查路徑，局部完成狀態便無法直接沿用。

同一份論文把多種 die-level checks 合併成單一 runset，包含 logic、SoIC TSV、backside metal、hybrid bond 與 micro-bump，並提供可在 floorplan 階段開啟的規則模式。早期模式用來發現介面對位、尺寸與重疊問題，最終模式則使用完整資料執行 signoff。兩者共享規則來源時，工程師能在幾何仍容易移動的階段收到回饋。

早期檢查節省的是昂貴重跑之前的修改成本。若錯位要等到完整 stack LVS 才出現，修正會穿過 assembly、layout extraction、netlist comparison 與相關 signoff 工作；在 floorplan 時發現，改動通常仍侷限於 die transform、pad planning 或 interface region。公開資料沒有提供迭代次數下降的量化結果，因此效益應以專案內的「首次發現階段、修正影響檔案數、重跑 core-hours」來量。

這套方法也增加維護面。Foundry rule、seal ring generator、dummy HBP 規則與 3Dblox 介面描述要一起升版。若自動產生器和 signoff deck 對同一個 enclosure 使用不同 revision，早期通過的 geometry 仍可能在最後被拒絕。平台應讓規則 revision 成為 run identity 的一部分，而非只保存工具 command line。

## ESD 要沿 BGA、TSV 與 hybrid bond 走完整條路

第二個機制是把 ESD 檢查從單顆 die 擴展成整個導電網路。Marvell 公開案例包含 top die 與 bottom die，兩者可由不同 node 製造，透過 hybrid bond pads 通訊；外部 I/O 從 BGA、substrate、C4 或 micro-bump 進入，再經 bottom die 的 TSV 到達上層 GPIO ESD cell 或 power clamp。

論文列出六種路徑，涵蓋面對面的 hybrid bonds、die-to-die signal pads、直接進入 Tier2 GPIO 的訊號，以及 power／ground 分別連到 Tier1、Tier2 或兩層 clamps 的組合。工具工作再拆成三類：

1. **TOPO** 找出保護元件與合法拓樸，回答每個入口是否有可達的 ESD 元件。
2. **P2P** 沿實際導體量測 BGA 或 bump 到 clamp 的點對點電阻。
3. **CD** 檢查金屬寬度和 current density，確認路徑可承受規則指定的電流。

這三項不能用單一 connectivity pass 取代。Netlist 連得上，只表示存在路徑；路徑若太長、太窄或跨越錯誤 clamp，ESD 電流仍可能造成損壞。Marvell 例子將一條 resistance rule 設為低於 0.1 Ω，工具回報 pad 與 clamp 間的實測電阻，工程師再依違例位置修 routing。這個數值屬於該案例規則，不是所有 3DIC 的通用上限。

完整路徑還揭示不同團隊的相依。Die team 擁有 clamp cell、TSV 與內部 routing，package team 擁有 BGA、C4、interposer 和 substrate，system signoff team 才看得到兩者串起來的電阻及分流。任何一方只交付 pass／fail 摘要，都不足以重建跨層問題；接收端至少需要 pin mapping、保護元件類型、抽取 connectivity、規則值與可定位的 violation path。

Siemens 2026 年的產品說明也把這條資料鏈分成相似的工具責任：Innovator3D IC 準備組裝與 netlists，Calibre 3DStack 建立完整 multi-die connectivity，Calibre 3DPERC 再執行 ESD path、point-to-point resistance 與 current density checks。[Calibre 3D IC solution](https://blogs.sw.siemens.com/calibre/2026/05/14/the-calibre-3d-ic-solution-mastering-the-complexities-of-advanced-3d-ic-chip-design/) 這能交叉確認機制方向，Marvell 的實際 runset 和內部自動化仍以其論文揭露為準。

## P2P 讓 signoff 預算集中在少數工作

Marvell 的公開 runtime 表讓資源安排可以量化。Tier2 top die 案例有九個 power domains、一個 ground 和超過 24,000 條 D2D signal nets；Tier1 bottom die 也有相同的 power-domain 數量與超過 24,000 條 D2D nets，另有超過 100 條 I/O signal nets。簡報列出的 job 時間與 cores 如表：

| 公開工作 | Tier2 runtime／cores | Tier1 KGS runtime／cores |
| --- | ---: | ---: |
| TOPO | 1.5 h／48 | 2.9 h／48 |
| LDL | 1.6 h／48 | 2.5 h／48 |
| CD | 1.8 h／48 | 6.2 h／16 |
| P2P | 41 h／240 | 6.5 h／240 |

將每項的 wall-clock hours 乘上 cores，可得到工作量近似值。Tier2 四項合計約 10,075.2 core-hours，其中 P2P 為 9,840 core-hours，占 97.7%；Tier1 KGS 合計約 1,918.4 core-hours，P2P 為 1,560 core-hours，占 81.3%。不同 tier 和模式的設計內容不相同，兩欄不適合被當成工具速度比較；它們共同指出 P2P 會支配計算預算。

<figure>
<a href="/images/ic-design-platform/2026-10-26/marvell-3dic-resource-budget.svg"><img src="/images/ic-design-platform/2026-10-26/marvell-3dic-resource-budget.svg" alt="Marvell Tier1 KGS 公開工作中 P2P 為 1560 core-hours，佔總量 81.3%；五次迭代的假設中，每次完整執行為 9592 core-hours，四次只跑 TOPO 與 LDL 再做一次完整工作為 2955.2 core-hours。" width="640" height="900" loading="lazy"></a>
<figcaption>圖二：上半部依據 Marvell WISH 2025 公開 runtime 與 cores 換算；下半部是五次迭代的假設算例。<a href="https://github.com/rightson/rightson.github.io/blob/main/scripts/experiments/marvell_3dic_signoff_budget.py">計帳程式</a>與<a href="https://github.com/rightson/rightson.github.io/blob/main/scripts/experiments/marvell_3dic_signoff_budget.results.json">結果檔</a>可重跑。</figcaption>
</figure>

假設同一個 Tier1 KGS stack 連續整合五次，每次都執行 TOPO、LDL、CD 與 P2P，總量是 5 × 1,918.4 = 9,592 core-hours。若前四次只跑 TOPO 和 LDL，最後一次再執行完整工作，算例變成 4 × 259.2 + 1,918.4 = 2,955.2 core-hours，下降 69.2%。這是排程模型，沒有宣稱輕量工作可以取代 CD 與 P2P。

可借鏡的實驗應把同一批真實 design changes 分成兩組。A 組每次跑完整工作；B 組讓 floorplan 和初期 assembly 只跑 geometry、TOPO 與 LDL，在里程碑補齊 CD、P2P 和完整 stack LVS。兩組都保存首次發現的 violation、重跑次數、core-hours、license-hours、人工除錯時間，以及最終完整工作找到的新增問題。若 B 組延後發現的高嚴重度問題抵銷計算節省，頻率就要提高。

排程還要分開 core-hours 與日曆時間。兩百四十 cores 跑 6.5 小時是 1,560 core-hours；若共享叢集只能短暫提供八十 cores，工具擴展性與排隊時間都可能改變完成時點。公司需要量到自己的 license 限額、記憶體峰值、I/O 和 parallel efficiency，Marvell 表格只能提供量級和工作組成。

## 三種流程處理不同的變動形狀

Marvell 方法適合 die、封裝和 stack 由不同資料與團隊維護的情境。標準化 assembly description 把跨層連接變成共同輸入，multi-level checks 則讓局部與系統結果有明確接續。它的代價是多一份必須同步的 system description、跨 foundry 規則整合，以及昂貴的 full-stack extraction 和 P2P。

另一條路是讓單一 EDA 平台保有組裝、物理實作與 signoff 的共同資料庫。這可以減少格式轉換及版本對接，工具供應商也能把 in-design checking 接到修正介面；團隊換來較深的產品依賴，既有腳本和不同供應商的 die data 仍要轉入共同模型。Synopsys 的 [Multi-Die System](https://www.synopsys.com/solutions/multi-die-design.html)屬於這類整合路線的公開產品說明。

第三條路是只在最終階段做 assembly verification。它對變動少、介面成熟的專案維護成本最低，卻把錯位、名稱對接與跨層保護問題留到修改代價較高的階段。若專案只有兩顆高度固定的 die，完整 flow automation 的投入可能難以攤提；若 chiplets、foundries、package variants 與 derivative products 持續增加，共同描述和早期檢查的回收機會會上升。

TSMC 在 2023 年公布 [3Dblox 2.0](https://pr.tsmc.com/english/news/3070)，把 early 3D IC design 和跨生態系工具交換列為重點；Marvell 2025 年案例新增的理解，是將 seal ring 後處理、dummy HBPs、multi-level DRC 和跨 package ESD 電阻放進同一條具名公司流程。方法演進的方向，從「能描述多顆 die」走向「每個新增物件都能回到系統連接與可靠度規則」。

未來六個月，最值得測的是同一份 assembly intent 能否驅動早期分析與 final signoff，且在 die revision、package variant 和 tool version 改變時保持一致。可觀察三個訊號：跨工具轉譯後的 net count 是否穩定、早期 run 找到的違例有多少會在完整工作重現、final P2P 新增問題的比例是否下降。若版本同步成本持續高於省下的重跑，人力和時程改善就不成立。

Marvell 的公開案例補齊了 R2G 後段一個常被省略的交接：GDS、netlist 與單顆 die 報告交出去後，chiplet 系統仍需要自己的 design intent、layout assembly、系統 connectivity 和 ESD path results。流程能改善時程與 tool-hours 的條件，是介面資料可重用、早期檢查能實際攔下後期問題，且高成本 P2P 工作按風險安排頻率；代價落在共同模型、規則 deck、版本治理與 full-stack 計算。

## 證據範圍

本文主要依據 Marvell 於 WISH 2025 發表的八頁論文與二十頁簡報。論文支持 multi-level DRC、3Dblox assembly、LVS connectivity、六類 ESD 路徑及 0.1 Ω 案例規則；簡報支持公開 runtime、cores、power domains 與 signal-net 規模。資料沒有提供 tapeout 名稱、量產狀態、導入前後迭代數、缺陷逃逸率或人力節省。

2026 DAC 議程另列 Marvell 的 stacked 3D chiplet SIP flow 和 physical signoff 報告，但目前公開頁面多為摘要；本文沒有用摘要補造論文未揭露的內部介面。Marvell 論文提到 Siemens Calibre PERC 與 Synopsys IC Validator，沒有揭露每項工作使用的完整版本、runset 或分配比例。

Core-hour 數字由公開 wall-clock hours 乘 cores，適合比較該表內工作量級，不表示工具的 CPU 使用率、license 費用或叢集效率。五次迭代模型是明示假設，沒有執行 EDA 工具、3D extraction 或實際 layout；0.1 Ω 僅屬論文案例規則。

## 參考資料

- Qi Wang 等，Marvell，[Navigating the Challenges of Physical Verification in 3DICs](https://designthesolution.org/wp-content/uploads/2025/09/navigating-the-challenges-of-physical-verification-in-3dics-from-2d-to-3d-solutions-qi-mohannad-jeanne-abhijat-mike.pdf)，WISH 2025，2025-09-05。
- Marvell，[WISH 2025 presentation](https://www.gsaglobal.org/events/wp-content/uploads/sites/10/2024/12/process-3v2-qi-wang-wish25_navigating_challenges_pv_v3.pdf)，完整流程、runtime 與資源表。
- IEEE Standards Association，[P3537 Draft Standard for 3Dblox](https://standards.ieee.org/ieee/3537/11871/)，3Dblox language scope。
- Siemens EDA，[Calibre 3DStack](https://www.siemens.com/en-us/products/ic/calibre-design/calibre-3d-ic/3dstack/)及[Calibre 3D IC solution](https://blogs.sw.siemens.com/calibre/2026/05/14/the-calibre-3d-ic-solution-mastering-the-complexities-of-advanced-3d-ic-chip-design/)，assembly connectivity 與 3DPERC 工作。
- Marvell，[DAC 2026 presentations](https://www.marvell.com/company/events/dac-2026.html)，後續 SIP flow、physical signoff 和 3Dblox 議程。
- Synopsys，[Multi-Die System](https://www.synopsys.com/solutions/multi-die-design.html)，整合式 exploration-to-signoff 替代方案。
