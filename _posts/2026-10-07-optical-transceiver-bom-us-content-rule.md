---
layout: post
title: "800G 光模組的成本集中在哪裡，65% 美國含量傳聞可能如何改變採購"
date: 2026-10-07 19:04:48 +0800
domain: ai-industry
categories: ai-industry
description: "800G EML 模組的雷射、DSP 與類比晶片占據主要材料成本；供應商能留下多少利潤，還要看認證、良率與採購條件。以訊號路徑、BOM 算例與正式政策文件，釐清 65% 美國含量傳聞如何影響零件替換與供應鏈分工。"
takeaways:
  - who: "Lumentum 與 Coherent"
    value: "Lumentum 與 Coherent 在高速光源與磷化銦製造上的能力，讓它們進入 EML、矽光與 CPO 的採購路徑；能否持續取得議價力，要看新產能的良品交付與雷射價格，而政策傳聞目前只提供額外情境。"
  - who: "Marvell"
    value: "Marvell 已公開量產的 3 奈米 1.6T Ara DSP，又把產品延伸到部分重定時架構；線性光學會改變模組內的晶片內容，營收走向仍須同時觀察出貨量、每顆售價與新產品收入。"
  - who: "中際旭創"
    value: "中際旭創的供應鏈調整涉及零件來源、產品認證與製造分工；若未來政策採 BOM 含量門檻，替換雷射或 DSP 會改變合規空間，但實際效果須依適用世代、認定方式與成本分母重算。"
  - who: "達發與聯亞"
    value: "達發已有官方公開的 800G DSP 方案，聯亞則有矽光 CW 雷射與磊晶產品；台廠的成長要從具體產品、量產份額與良率追到營收和現金，會員名單、送樣或擴產宣告各只回答其中一段。"
  - who: "雲端資料中心業者"
    value: "雲端資料中心業者以模組採購、耗電與維護支出支付互連成本；LPO 與 CPO 可減少部分模組負擔，同時增加主機協同設計與光電封裝要求，採購選擇會把利潤移向能交付完整鏈路的供應商。"
---

光模組把交換器與伺服器的電訊號轉成光，讓資料跨越機櫃。AI 叢集擴大後，採購端同時面對更高頻寬、有限電力與交付時程；模組內的高速晶片、雷射與光學組裝因此各有不同的議價條件。理解這些分工，才能判斷哪一筆新增採購會成為哪家公司的收入，以及供應吃緊時誰能留下利潤。

2026 年 10 月的市場討論，又加上「光模組須有至少 65% 美國含量」的政策情境。這個數字目前屬研究機構推估與市場轉述。正式規則、立法提案與預期中的新措施有不同適用範圍，後面的成本計算會逐一說明。

先沿著一顆 **800G、8×100G、EML、DR8、可插拔且含 DSP** 的模組看訊號路徑。這組限定很重要：改用矽光、線性光學或不同傳輸距離，零件數量與成本就會變。圖左沿發射方向讀，圖右沿接收方向讀；主機與模組各自處理哪些工作，會直接影響可替換的晶片。

<div role="region" aria-label="800G EML DR8 主機到光纖的 TX 與 RX 路徑，對應 315 美元假設 BOM、支援材料、公司產品和公開階段；替代矽光與 CPO 角色另列，可橫向捲動" tabindex="0" style="overflow-x: auto; margin: 1.5rem 0;">
  <a href="/images/ai-industry/2026-10-07/optical-module-bom-role-map.svg" aria-label="開啟完整圖">
    <img src="/images/ai-industry/2026-10-07/optical-module-bom-role-map.svg" alt="800G EML DR8 主機到光纖的 TX 與 RX 路徑，對應 315 美元假設 BOM、支援材料、公司產品和公開階段；替代矽光與 CPO 角色另列" style="width: 100%; min-width: 1200px; max-width: none; height: auto;" />
  </a>
</div>

[開啟完整圖，可放大閱讀](/images/ai-industry/2026-10-07/optical-module-bom-role-map.svg)

圖：一般 retimed EML 模組的功能與成本對應。BOM 為[公開個人拆解](https://caifuhao.eastmoney.com/news/20260411230337084311740)的假設算例；功能依據 [IEEE 架構討論](https://www.ieee802.org/3/df/public/22_02/lu_3df_01b_220215.pdf)。公司例子依據 [Marvell 產品資料](https://www.marvell.com/products/pam-dsp.html)、[達發方案](https://www.airoha.com/group-news/09joI74gjH0LOMIF)、[Lumentum 100G EML](https://www.lumentum.com/en/products/eml-100g-pam4-cwdm-laser)與 [ELSFP-350](https://www.lumentum.com/products/external-laser-source-els-module-ultra-high-power-laser)、[Coherent 2024 年報](https://www.coherent.com/content/dam/coherent/site/en/documents/investors/annual-filings/2024/coherent-annual-report-2024.pdf)、[聯亞年報](https://www.lmoc.com.tw/index.php?i=1&id=391&lang=en&option=module&task=dfile)與 [NVIDIA 量產分工](https://blogs.nvidia.com/blog/nvidia-gtc-taipei-computex-2026-news/)整理。公司對應其公開能力，成本對應元件類別；實際算例的供應商與料號待查。

## 一顆模組把高速電路接到精密光學

800G 表示模組的總傳輸速率。在這個例子裡，八條約 100G 的通道共同提供 800G；PAM4 用四個振幅層級表示每個符號，增加傳輸密度，也提高電路對雜訊、失真與時序的要求。[IEEE 802.3df 的介紹](https://standards.ieee.org/beyond-standards/ethernets-next-bar/)說明 800GbE 的平行八通道結構。

發射端的電訊號先經模組 DSP 做等化與重定時，再由 Driver 提供調變器所需的驅動訊號。EML 把雷射與電吸收調變器結合，產生隨資料變化的光；透鏡與光纖陣列 FA 將光耦合進光纖。接收端由 PD 把光變成電流，TIA 把小電流轉成可處理的電壓，DSP 再整理訊號送回主機。DR8 使用八條平行發射光路與八條接收光路；光路對準與測試也需要製程能力。

FEC 是用冗餘資訊修正錯誤，與等化、重定時分屬不同功能。一般 Ethernet 鏈路的 PCS／FEC 在主機端；更高速的設計可能再加入分段或串接 FEC。[IEEE 2022 年的架構討論](https://www.ieee802.org/3/df/public/22_02/lu_3df_01b_220215.pdf)列出不同分工，所以「DSP 一律負責全部糾錯」會把不同架構混在一起。

這條路徑上至少有兩種稀缺能力。高速電路要在功耗限制內處理失真的訊號；光學製造要把多條光路對準，並在溫度、壽命與大量生產條件下保持良率。前者形成 IC 設計與產品認證的門檻，後者形成製程、設備與交付的門檻。光學組裝的商業模式也可能包含設計、測試與品質責任，只有外殼與焊接的代工費用，無法代表整家模組公司的價值。

### 功能位置能對到成本，晶片整合與交付範圍仍須展開

省去細節會影響 BOM 的適用性與加總方式。功能圖描述每個工作的位置，一個工作可以由獨立晶片完成，也可以整合在另一個採購項目中。例如，[Marvell Perseus 官方產品資料](https://www.marvell.com/products/pam-dsp.html)列出整合 TIA 與雷射 Driver；[達發 AN8928／AN8924](https://www.airoha.com/group-news/09joI74gjH0LOMIF)也列出內建 Driver。拿這些方案重算成本，要以該整合晶片的採購價取代被它涵蓋的各列。

| 圖裡省略的細節 | 如何影響這份 800G 算例 | 重算時需要的資料 |
| --- | --- | --- |
| DSP、Driver、TIA 的晶片整合 | 分開畫的是功能；整合產品可合併採購，88 與 38 美元須重列 | 料號、功能範圍、裸晶／封裝價格；38 美元的分拆尚無資料 |
| 光源、調變器與接收器的整合 | 本例限定八條 EML 發射通道；矽光改列 CW、PIC 與分光，PD 也可能在 PIC 內 | 光功率、通道數、雷射數、PIC 內容與耦合損耗 |
| 發射與接收的耦合件 | 圖有兩個方向，但被動光學 29 美元只計一次 | 透鏡、FA／FAU、連接器的實際數量及報價 |
| MCU、監控、時脈與溫控 | 原資料未逐項交代，9 美元支援材料的涵蓋範圍也待查 | 每項材料及是否已包含在其他採購件 |
| 封裝、測試、良率與保固 | 材料價與合格模組銷貨成本有差距，6 美元餘額保持未解 | 報價交付範圍、製造費、測試費、良率與保固準備 |

因此，315 美元算例可教成本結構和敏感度；驗證某個實際產品，需要再接上料號級清單。加入細節可能把兩列合成一列、把一列拆成多項，或新增支出。光引擎與 ELS 分攤則屬另一份成本模型。管理、時脈與散熱雖未出現在資料串列中，仍需出現在完整採購清單。

## 315 美元拆解能教成本結構，尚不足以代表實際採購

原先流傳的 [2026 年 4 月 800G EML 拆解](https://caifuhao.eastmoney.com/news/20260411230337084311740)列出約 315 美元 BOM 與 380–400 美元售價。這是個人撰稿資料，以下將金額視為**假設算例**，用來觀察成本敏感度。BOM 是材料清單及其成本；ASP 是平均售價，兩者需要分開。

上方整合圖把訊號路徑與成本放在一起：DSP 與 EML 各有金額；Driver／TIA 和雙向被動光學各只有一筆合計。下表保留完整數字方便核算。原始分項合計 309 美元，與 315 美元總額之間的 6 美元獨立列出。

| 成本項目 | 算例金額（美元／顆模組） | 占 315 美元比例 | 成本會因什麼改變 |
| --- | ---: | ---: | --- |
| EML 雷射 | 92 | 29.2% | 通道數、每通道速率、採購價格與光源架構 |
| DSP | 88 | 27.9% | 製程、通道配置、內建功能與採購條件 |
| Driver 與 TIA | 38 | 12.1% | 線性度要求、封裝與功能整合 |
| 被動光學 | 29 | 9.2% | 光路、耦合方式與製造良率 |
| PD | 24 | 7.6% | 接收器架構、材料與整合方式 |
| PCB／陶瓷基板 | 14.5 | 4.6% | 電氣損耗、層數與設計 |
| 外殼／散熱／連接器 | 14.5 | 4.6% | 封裝尺寸與散熱需求 |
| 電容／電阻／電源等 | 9 | 2.9% | 供電與監控設計 |
| 原文未分列 | 6 | 1.9% | 保留為未解釋差額 |

EML、DSP、Driver 與 TIA 加總為 218 美元，218÷315＝69.2%。這是四類元件的成本占比。EML 有美日等不同來源，DSP 也有台灣方案；將各項占比乘上實際符合認定的採購比例，才得到特定模組的含量。

對零件廠，單項金額大提供較大的收入池；對模組廠，同一項也是最大的成本壓力。假設 DSP 原價 88 美元，漲價 20% 會增加 17.6 美元材料成本；以 400 美元售價且其他條件固定計算，毛利空間減少 4.4 個百分點。若售價同步上調，買方承擔更多；若長約鎖住售價，模組廠先吸收。這個試算顯示漲價如何傳導，漲幅與轉嫁程度仍應逐家公司查證。

更高速的產品會重寫這張表。[Marvell 2024 年 12 月公布的 Ara](https://www.marvell.com/company/newsroom/marvell-unveils-industrys-first-3nm-1-6tbps-pam4-interconnect-platform.html)使用 3 奈米、八條 200G 電氣與光學通道，並整合雷射 Driver。產品升級時，原本分開採購的功能可能合在一起；比較新舊 BOM 要先防止重複計價。

## 用同一口徑算毛利，才能看見誰留下利潤

將前面的材料算例接到售價，有一個必須解決的算術問題：

- 售價 380 美元、BOM 315 美元：扣材料後剩 65 美元，比例為 17.1%。
- 售價 400 美元、BOM 315 美元：扣材料後剩 85 美元，比例為 21.3%。

若 315 美元是完整材料成本，製造、折舊、測試及保固等另計支出還會壓低毛利。若產品毛利率為 46.6%，售價 400 美元對應的全部銷貨成本應為 213.6 美元。兩組數字之間相差逾 100 美元，必須回頭確認產品、期間、客戶長約與成本範圍。這份材料拆解適合教計算，不適合直接帶入公司獲利預測。

同樣地，公司整體毛利率、產品毛利率與代工毛利率需要分欄。以下保留兩家可直接查到財報的例子，以及原文的模組資料，讓口徑一眼可辨：

| 對象與期間 | 數字 | 計算範圍 | 可以回答什麼 |
| --- | --- | --- | --- |
| Lumentum FQ4 FY2026，季末 6/27 | GAAP 47.4%；非 GAAP 50.4% | 公司合併，含不同產品 | 整體產品組合與成本改善 |
| Fabrinet FQ4 FY2026，季末 6/26 | GAAP 12.0%；非 GAAP 12.2% | 公司合併，製造服務 | 該公司代工模式的毛利與費用結構 |
| 中際旭創 2026 上半年光模組，原文媒體轉述 | 46.6% | 產品類別，待核對原始財報 | 保留為待核對項，與單顆 BOM 分開 |

來源：[Lumentum 財報](https://investor.lumentum.com/financial-news-releases/news-details/2026/Lumentum-Announces-Fourth-Quarter-and-Full-Fiscal-Year-2026-Results/default.aspx)、[Fabrinet 財報的 GAAP／非 GAAP 調節表](https://www.sec.gov/Archives/edgar/data/1408710/000140871026000026/fn-2026811xex991q426.htm)、[中際旭創與新易盛媒體資料](https://stock.10jqka.com.cn/20260901/c679463474.shtml)。

推論：具有難以替換的產品、良率與認證，供應商更有機會保住價格；模組整合商也能靠設計與規模取得利潤。判斷持續性時，要觀察同一家公司的毛利額、營業利益與現金流連續變化。較高的合併毛利率本身，仍留有產品組合與會計差異。

## 光源、訊號處理與封裝位置，要分三次選

EML、矽光、LPO 與 CPO 回答的是不同問題。把它們排成單一接班序列，會讓供應商分析失去準確性。

| 設計維度 | 選項 | 採購上改變的內容 |
| --- | --- | --- |
| 光如何產生與調變 | EML；CW 雷射＋矽調變器；VCSEL 等 | 雷射數量、材料、調變器與耦合 |
| 電訊號在哪裡整理 | 雙向 retimed；LPO；部分重定時 | 模組 DSP、類比晶片及主機 SerDes 分工 |
| 光電轉換放在哪裡 | 面板可插拔；CPO 等 | 電氣路徑長度、封裝、光纖配線與維修 |

EML 把光源與調變結合；矽光可由 CW 雷射提供連續光，再由矽光晶片上的調變器寫入資料。矽光改變光源與調變的配置，模組仍可使用 DSP。光纖陣列 FA／FAU 負責耦合與連接，需求要依每台設備的光引擎數、通道數與封裝設計計算。[Coherent 的 InP 製程說明](https://www.coherent.com/news/press-releases/worlds-first-6-inch-inp-scalable-wafer-fabs-paving-the-way-for-the-next-generation-of-lasers-for-ai-transceivers-and-6g-wireless-networks)列出 EML、高速光偵測器與矽光 CW 雷射等產品，說明同一材料平台如何跨不同光學設計。

下圖先分開三個選擇，再組成五種具體配置。沿每一列比較零件如何改變，最後讀組合表；光源、處理方式與封裝可以搭配，但每種搭配都要滿足相同鏈路的電氣、光學與維修要求。

<div role="region" aria-label="三次選型圖，分別比較 EML、CW 加矽光和 VCSEL，雙向 retimed、TRO 和 LPO，以及可插拔和 CPO；下方列出五種具體組合與成本變化，可橫向捲動" tabindex="0" style="overflow-x: auto; margin: 1.5rem 0;">
  <a href="/images/ai-industry/2026-10-07/optical-three-design-choices.svg" aria-label="開啟完整圖">
    <img src="/images/ai-industry/2026-10-07/optical-three-design-choices.svg" alt="三次選型圖，分別比較 EML、CW 加矽光和 VCSEL，雙向 retimed、TRO 和 LPO，以及可插拔和 CPO；下方列出五種具體組合與成本變化" style="width: 100%; min-width: 1200px; max-width: none; height: auto;" />
  </a>
</div>

[開啟完整圖，可放大閱讀](/images/ai-industry/2026-10-07/optical-three-design-choices.svg)

圖：功能比較示意，依據 [Coherent 2024 年報的光源與距離說明](https://www.coherent.com/content/dam/coherent/site/en/documents/investors/annual-filings/2024/coherent-annual-report-2024.pdf)、[2026 年 OFC 多技術展示](https://www.coherent.com/news/press-releases/coherent-demonstrates-next-gen-pluggable-transceiver-ofc-2026)、[LPO MSA 規範](https://www.lpo-msa.org/files/live/sites/lpomsa/files/specs/LPO_MSA_Specification_v1p2_final.pdf)、[Marvell Ara T 公告](https://www.marvell.com/company/newsroom/marvell-1-6t-optical-dsp-ai-data-center-connectivity.html)與 [NVIDIA CPO 技術說明](https://developer.nvidia.com/blog/how-industry-collaboration-fosters-nvidia-co-packaged-optics/)整理。產品例子對應公開技術路徑，A 的 315 美元為獨立假設。

例如，從配置 A 的 EML retimed 可插拔改成 B 的矽光 retimed 可插拔，DSP 可以保留，光學材料則重列。從 B 改成 LPO，是省去模組內數位處理並重估線性電路與主機通道；再改成 CPO，還會搬動光引擎和供光位置。TRO 居於雙向 retimed 與全線性之間：發射端留重定時，接收端回到主機協同。Ara T 在 2026 年第一季起送樣，與原版 Ara 已量產的階段分開。

### LPO 節省模組處理，主機與整條鏈路共同承擔品質

LPO 移除模組內的數位處理，留下線性光電轉換，依靠主機端處理鏈路。[LPO MSA 規範第 5.6 節](https://www.lpo-msa.org/files/live/sites/lpomsa/files/specs/LPO_MSA_Specification_v1p2_final.pdf)明定主機執行 RS(544,514) FEC；同一份規範也列出主機、模組與光纖的測試點。它覆蓋 100G/lane、最高 800G 的組合，外推到 200G/lane 應另讀對應規格。

拿掉算例中 88 美元 DSP，只能先得到移除項目的金額。新的線性 Driver／TIA、PCB 損耗控制、主機 SerDes 能力、互通測試與維護，也有成本。假設新增支出為 20 美元，材料淨節省才是 68 美元；20 美元是用來說明方法的假設。

功耗也要量整套系統。假設某方案每顆模組淨省 3W、部署 10 萬顆，全年連續運作可省 2.628GWh；電價 0.10 美元／kWh 時約為 26.28 萬美元，尚未計 PUE 或主機端功耗差。對雲端業者，釋出的電力能否轉成更多可用算力，以及故障處理是否更快，可能比模組折價更有意義。

Marvell 的產品反應已經出現：[官方產品公告](https://investor.marvell.com/news-events/press-releases/detail/1013/marvell-ushers-in-the-1-6t-era-with-expanded-optical-dsp-platform-portfolio-redefining-ai-data-center-end-to-end-connectivity)列出量產 Ara、發射端重定時 Ara T 與其他配置。這支持的產業走向是產品分化：完整 DSP、部分重定時與線性方案，分別競爭不同鏈路。

### CPO 把光電整合移近交換晶片，採購單位跟著改變

CPO 將光引擎移近交換 ASIC，縮短高速電氣路徑，再以光纖連到遠端。[NVIDIA 技術說明](https://developer.nvidia.com/blog/scaling-ai-factories-with-co-packaged-optics-for-better-power-efficiency/)展示光引擎、外部光源與封裝的分工。維修、更換、光纖管理與可靠性設計會進入系統採購，成本應以「同樣總頻寬、距離、可靠性與交付範圍」比較。

為了只比較封裝位置，以下前後兩邊均固定使用 CW 雷射與矽光 PIC。上半部的模組含 DSP、EIC 與 PIC；下半部採外部 ELS 供光的 CPO。藍線表示高速電訊號，橘線表示已承載資料的光，綠色虛線表示尚未調變的 CW 供光。收發方向以雙向箭頭合併呈現，實體 TX／RX 光纖仍分開。

<div role="region" aria-label="矽光 retimed 可插拔改成外部 ELS 供光 CPO 的 before after 架構，標示 ASIC 與共同封裝、DSP、EIC Driver TIA、PIC 調變器和 PD、面板光纖介面，以及電訊號、資料光、CW 供光三種路徑，可橫向捲動" tabindex="0" style="overflow-x: auto; margin: 1.5rem 0;">
  <a href="/images/ai-industry/2026-10-07/optical-cpo-before-after.svg" aria-label="開啟完整圖">
    <img src="/images/ai-industry/2026-10-07/optical-cpo-before-after.svg" alt="矽光 retimed 可插拔改成外部 ELS 供光 CPO 的 before after 架構，標示 ASIC 與共同封裝、DSP、EIC Driver TIA、PIC 調變器和 PD、面板光纖介面，以及電訊號、資料光、CW 供光三種路徑" style="width: 100%; min-width: 1200px; max-width: none; height: auto;" />
  </a>
</div>

[開啟完整圖，可放大閱讀](/images/ai-industry/2026-10-07/optical-cpo-before-after.svg)

圖：依據 [NVIDIA 2025 年 CPO 技術說明](https://developer.nvidia.com/blog/how-industry-collaboration-fosters-nvidia-co-packaged-optics/)、[2026 年 Spectrum-X 技術更新](https://developer.nvidia.com/blog/scaling-power-efficient-ai-factories-with-nvidia-spectrum-x-ethernet-photonics)與 [2026 年量產分工](https://blogs.nvidia.com/blog/nvidia-gtc-taipei-computex-2026-news/)整理的功能配置比較，非晶粒 floorplan；省略通道複製、管理匯流排與冷卻管線。圖內的 NVIDIA 配置數另依產品資料列出；800G EML 的金額只用在前面的 BOM 算例。

EIC 是承接高速電介面的電子晶片，PIC 是處理光的積體電路。這類 CPO 方案省去面板上的獨立模組 DSP，Driver、TIA、調變器與 PD 的工作持續存在，並透過短電氣距離和共同設計管理訊號品質。CW 雷射位於 ASIC 封裝外，送出的供光進入 PIC 後才寫入資料；外部光源與面板資料光纖是兩條不同路徑。

NVIDIA 公開的 Spectrum-X 單 ASIC 封裝例子含 32 個光引擎，每引擎 16 條 TX 與 16 條 RX、200G/lane。以單方向速率計，每引擎 3.2Tb/s、單 ASIC 102.4Tb/s；四 ASIC 系統合計 409.6Tb/s。光引擎數與外部雷射模組數按各型號核對，採購模型也要區分光引擎、ELS 分攤與整機。

假設 10 萬條鏈路兩端均用可插拔光模組，就是 20 萬顆；若交換器端改成 CPO，交換器端的光學功能轉入光引擎，另一端仍可能保留可插拔。只追可插拔顆數會漏掉轉移出去的內容。應把每端架構分開，再計算每條鏈路的光源、DSP、光引擎與連接成本。

NVIDIA 在 [2026 年 6 月 1 日的官方更新](https://blogs.nvidia.com/blog/nvidia-gtc-taipei-computex-2026-news/)已將 Spectrum-X Ethernet Photonics 標為量產，並列出 TSMC、SPIL 與 Foxconn 的分工。量產代表產品階段已前進，全球採用比例則要另以客戶部署和收入追蹤。站內的 [AI collective 光路成本分析]({% post_url 2026-09-30-collective-optical-reconfiguration-cost-boundary %})也說明，系統成本需要把資料路徑與等待一起計入。

## 磷化銦與先進 DSP 的供給，要看良品交付

磷化銦 InP 用在高速雷射與部分光偵測器。產業鏈由基板、磊晶、元件製造再走到封裝測試；各階段良率相乘，公告的晶圓產能與能交給客戶的零件數之間，還有製程與認證距離。

2025 年 6 月 11 日，[AXT 的 8-K](https://www.sec.gov/Archives/edgar/data/1051627/000143774925020087/axti20250611_8k.htm)披露取得向部分歐洲與日本客戶出口 InP 的許可。這個前例說明供應變化要追到材料品項、目的地與許可進度。上游受到限制，即使元件需求旺盛，下游也可能先遇到交付壓力。

供給改善的路徑包括更大晶圓與製程爬坡。[Coherent 2026 年 6 月的公告](https://coherent.gcs-web.com/news-releases/news-release-details/coherent-announces-chips-letter-intent-50-million-expand-world)說明 Sherman 的 6 吋 InP 量產平台與擴產計畫。若新平台提高每片晶圓的良品數，雷射缺貨溢價可能收斂；認證、設備與良率爬坡則決定這個效果何時進入交付。

DSP 要分製程世代與產品。Ara 的 3 奈米是官方可確認的能力；更高需求對先進製程配置形成壓力，仍須取得具體投片、交期與價格資料，才有足夠資訊估算短缺量。站內 [HBM 晶圓配置分析]({% post_url 2026-09-30-hbm-wafer-allocation-memory-profit %})提供類似思路：以有限投入追到合格產出與利潤，避免只看擴產金額。

## 65% 傳聞與兩條正式政策路徑分開讀

「65%」「中國製」「美國公司」「美國製造」各自有不同法律與供應鏈意義。以 2026 年 10 月 7 日取得的文件來看，至少要分開以下三種資訊：

| 文件或訊息 | 階段與範圍 | 與光模組採購相關的內容 |
| --- | --- | --- |
| FCC 26-50 的正式規則，9/11 刊登 | 規則已公布，10/13 生效；設備授權 | 在特定條件下限制 Covered List 業者生產的具數位邏輯硬體元件 |
| S.5548，9/24 提出 | 參議院提案；聯邦採購 | 列出特定光模組廠及關係企業，提案設立法後五年生效安排 |
| 65% 含量、可能由 3.2T 開始 | 研究機構推估與市場轉述 | 等待正式適用產品、計算方法、豁免與時程 |

來源：[Federal Register 正式規則](https://www.govinfo.gov/content/pkg/FR-2026-09-11/html/2026-18535.htm)、[S.5548 提案全文](https://www.govinfo.gov/content/pkg/BILLS-119s5548is/xhtml/BILLS-119s5548is.html)；65% 情境的市場討論見 [股癌 EP702 原集](https://player.soundon.fm/p/954689a5-3096-43a4-a80b-7810b219cef3/episodes/42301381-6003-4b54-a28d-290a3fd2e258)，摩根士丹利原報告仍待核對。

FCC 正式規則討論 Covered List 元件，純機械與被動元件有不同處理。S.5548 則在提案中點名中際旭創、新易盛及相關企業，並涵蓋特定零件、韌體與軟體來源。它們的文字與 BOM 比例情境各有不同作用，閱讀時要先定位到適用採購與產品。

推論：若未來規則真的按零件價值比例認定，採購可能向符合條件的高價元件集中；若按製造主體、控制關係或個別元件限制，海外組裝與高比例美系材料可能仍有其他合規要求。這兩種走向會形成不同的台灣訂單。

### 用兩個變數計算含量，再看替換空間

假設未來規則採零件價值口徑，含量可寫成：

**符合認定的零件金額 ÷ 規則指定的成本分母。**

供應商國籍、製造地、控制權與代工來源如何認定，由條文決定。以下只演示「218 美元全部符合、其餘 97 美元全部不符合、分母為 315 美元」的算術；每項替換都同步更新分子與分母。

| 假設替換 | 符合金額（美元） | 總成本（美元） | 假設含量 |
| --- | ---: | ---: | ---: |
| 基準 | 218 | 315 | 69.2% |
| EML 改為等價非符合零件，成本仍 92 | 126 | 315 | 40.0% |
| EML 改為非符合零件，成本降至 60 | 126 | 283 | 44.5% |
| DSP 改為等價非符合零件，成本仍 88 | 130 | 315 | 41.3% |
| 只把原本符合的 10 美元零件等價替換 | 208 | 315 | 66.0% |

在等價替換條件下，65% 需要至少 204.75 美元符合內容，基準只有 13.25 美元餘裕。這說明門檻一旦採用，會對哪些替換形成較大限制；也說明規則未定義前，單憑供應商所在地無法宣布某家公司已合規。

如果改成 CW 雷射與矽光晶片，甚至 3.2T 的新配置，應重新列出所有零件與價格，再重新認定。800G 的 69.2% 是教算式的例子，3.2T 政策效果需使用相應產品的資料。

## 台廠要從產品位置追到可認列收入

台廠可透過產品替換、供應來源分散與 CPO 新分工取得訂單，三條路徑的時間與金額不同。先縮到有具體公開資料的公司，再逐格追蹤：

| 公司 | 可確認的產品或角色 | 公開階段 | 財務上接著要查 |
| --- | --- | --- | --- |
| 達發 | AN8928／AN8924，106Gbps ×8／×4 PAM4 DSP，列出 800G／400G 應用 | 2026/3/17 官方方案展示 | 該產品量產時間、客戶份額、DSP 收入與毛利 |
| 聯亞 | 磊晶及矽光 CW 雷射產品 | 公司年報與營收揭露 | CW／磊晶的出貨組合、良率、毛利與擴產現金 |
| 台積電 | 矽光製造 | NVIDIA 量產平台列出的合作分工 | 光學製造內容與營收貢獻 |
| 日月光旗下 SPIL | 光電元件封裝、組裝與測試 | 同一量產平台的合作分工 | 封裝產能利用率、良率與收入 |
| 鴻海 | CPO 交換器系統組裝 | 同一量產平台的合作分工 | 系統單價、訂單量與可保留的毛利 |

來源：[達發官方方案](https://www.airoha.com/group-news/09joI74gjH0LOMIF)、[聯亞年報](https://www.lmoc.com.tw/index.php?i=1&id=391&lang=en&option=module&task=dfile)、[聯亞營收頁](https://www.lmoc.com.tw/index.php?lang=en&temp=investment)、[NVIDIA 公開分工](https://blogs.nvidia.com/blog/nvidia-gtc-taipei-computex-2026-news/)。公司合作角色與該產品的營收貢獻，分別列在不同欄。

聯亞營收頁列出的 2026 年 9 月營收為 5.40492 億元、8 月為 5.20469 億元，月增約 3.8%。這可確認公司收入增加；個別光源產品的貢獻，還要接到產品組合。送樣、認證、首次量產與重複採購各回答不同的商業進度，分析時保留其名稱。

零件與代工的計價單位也要確認。若磊晶廠按晶圓賣，收入模型應以晶圓片數及每片價格建立；若按雷射良品交貨，才用零件顆數。FAU 要看每個光引擎的組數，系統組裝則看每台交換器內容。上下游金額屬於不同公司的收入，估整體市場時需避免將同一批材料反覆加總。

![假設零件廠從客戶設備出貨量、每台用量、供應份額與售價推到營收，再扣銷貨成本、營業費用和營運資金推到現金](/images/ai-industry/2026-10-07/optical-order-to-cash.svg)

圖：假設算例，單位為美元。由訂單到現金的計算示意，用來區分出貨、獲利與收款；非任何公司的預測。

例如某零件廠服務的設備年出貨 100 萬台，每台用兩個零件、取得 20% 份額、每顆售價 10 美元，對應營收為 **100萬×2×20%×10＝400 萬美元**。以 40% 毛利率計，毛利 160 萬；新增營業費用 60 萬，新增營業利益為 100 萬。若有效稅率假設 20%，稅後營業利益為 80 萬；再加折舊 20 萬、減資本支出 100 萬及淨營運資金增加 50 萬，近似新增自由現金流為負 50 萬美元。

這個例子說明設備擴產能讓營收與利益先上升，現金則可能先流出。估算供應能力時，還要拿 40 萬顆的需求與良品產能比較；若以投入量報產能，先扣製程良率與認證後可交付比例。只把客戶的全部需求當成自家出貨，會高估收入。

## 2027 年的利潤要用價格、出貨與現金一起驗證

推論：未來四季，高速光源、成熟 DSP 與已通過客戶認證的光電製造，仍有機會在升速過程中取得較好的訂單條件；可插拔、部分重定時與 CPO 會依客戶及鏈路分化。新產能的交付速度與替代方案的採用比例，將決定稀缺溢價能維持多久。

這個走向有兩個合理的相反情境。第一，InP 良率、新供應商認證與零件擴產比需求更快，採購端取得更多選擇，價格先鬆動。第二，更多系統改用線性光學或 CPO，傳統模組 DSP 的每條鏈路內容減少，但新光引擎與封裝收入增加。前者主要改變價格，後者主要改變內容；兩者可以同時發生。

接著以同一產品、同一客戶與同一期間追蹤以下組合。月營收按月檢查，毛利與現金按季檢查，政策則在正式文件出現時更新。

| 看到的變化 | 必須一起查 | 對產業判斷的作用 |
| --- | --- | --- |
| DSP／雷射報價下降 | 出貨量、交期、合約、替代方案比例 | 區分擴產、需求轉弱與產品替換 |
| 雷射交期縮短 | 良品產能、ASP、庫存與客戶拉貨 | 區分供給改善與訂單消化 |
| 台廠營收快速增加 | 產品組合、毛利額、應收款與營運現金流 | 區分可持續出貨、低毛利擴量與提前備貨 |
| CPO 客戶部署增加 | 交換器台數、光引擎內容、遠端模組與產品收入 | 重算每條鏈路的收入分配 |
| 65% 或其他限制正式公布 | 適用產品、認定方式、分母、豁免及生效日 | 重算需調整的採購，而非沿用傳聞 |
| 擴產設備到位 | 良率、認證、利用率與折舊 | 檢查新增產能何時形成毛利與現金 |

價格停止上漲可能是交付改善；只有出貨、交期或架構採用提供相應變化，才足以把它連到替代。相反地，需求仍成長但單位內容與 ASP 下降，公司收入也可能低於原先假設。

光模組的收入池沿著訊號處理、光源、耦合與系統整合分配。短期價格由可交付供應決定，長期分配由架構與替換成本改變。把採購單位、量、價格、良率與現金接起來，才能分辨誰正在獲得持續的利潤，以及下一份公告會改變哪個假設。

## 證據範圍

- 315 美元 BOM 來自個人文章，原始分項與合計有 6 美元差額，且同文售價、BOM 與毛利率互不相容。本文只用它作假設算例，不採信其未經核對的市占、客戶採購比例與缺口數字。
- 截至 2026 年 10 月 7 日，本文取得的一手文件，未提供上述 65%／3.2T 情境的正式條文。摩根士丹利原報告未取得；美國公司、美國製造、盟國來源、價值分母與外包製程認定均待確認。本文未將任何台廠判為合規或排除。
- FCC 26-50、S.5548 與尚待公布的光模組措施不可互相替代。S.5548 引用的是 9 月 24 日提出版本，不代表法案已通過；適用細節仍須依最後條文核對。
- 詳細拆解圖的公司是公開能力例子，未確認為假設算例的實際供應商；價格亦未確認對應圖列產品。通道數與裸晶數、合併報價與分項金額分開。訊號路徑是一般功能圖；模組 FEC、Driver 整合、光源數量與熱管理依產品而異。原先引用的 2022 年 IEEE 功耗比例屬不同光學配置，本次移除其對所有 800G DR8 模組的外推。
- CPO 前後圖固定矽光，比較外部 ELS 供光配置；其他 CPO 光源位置與介面仍依設計。圖示功能框分開展示 EIC 與 PIC，實際可垂直堆疊；面板光纖介面與 ELS 可抽換性分別確認。
- LPO 規範引用 100G/lane 版本；CPO 與部分重定時的產品公告支持各自公布的能力與階段，不提供全球採用比例。圖中尺寸與光路不按比例。
- 公司毛利率區分 GAAP／非 GAAP、期間與產品範圍；中際旭創 46.6% 保留為原文二手資料待核對項，不作單顆模組預測。聯亞營收是公司整體，未假設全部來自 CW 雷射。
- 營收、功耗、含量與現金流試算均明示假設，未加入任何公司目標價、個人持倉或進退場建議。

## 來源

- [IEEE — Ethernet’s Next Bar is Now – 800 Gb/s!](https://standards.ieee.org/beyond-standards/ethernets-next-bar/)
- [IEEE — DSP and FEC considerations for 800GbE and 1.6TbE，2022-02-15](https://www.ieee802.org/3/df/public/22_02/lu_3df_01b_220215.pdf)
- [LPO MSA — 100G-DR-LPO specification，第 5.6 節及鏈路測試](https://www.lpo-msa.org/files/live/sites/lpomsa/files/specs/LPO_MSA_Specification_v1p2_final.pdf)
- [Marvell — 3nm 1.6T Ara 平台，2024-12-03](https://www.marvell.com/company/newsroom/marvell-unveils-industrys-first-3nm-1-6tbps-pam4-interconnect-platform.html)
- [Marvell — Expanded 1.6T optical DSP portfolio，量產與部分重定時產品](https://investor.marvell.com/news-events/press-releases/detail/1013/marvell-ushers-in-the-1-6t-era-with-expanded-optical-dsp-platform-portfolio-redefining-ai-data-center-end-to-end-connectivity)
- [NVIDIA — Scaling AI Factories with Co-Packaged Optics](https://developer.nvidia.com/blog/scaling-ai-factories-with-co-packaged-optics-for-better-power-efficiency/)
- [NVIDIA — COMPUTEX 2026 更新，6/1 Spectrum-X Photonics 量產與合作分工](https://blogs.nvidia.com/blog/nvidia-gtc-taipei-computex-2026-news/)
- [Coherent — 6 吋 InP 製程與產品範圍](https://www.coherent.com/news/press-releases/worlds-first-6-inch-inp-scalable-wafer-fabs-paving-the-way-for-the-next-generation-of-lasers-for-ai-transceivers-and-6g-wireless-networks)
- [Coherent — Sherman 擴產與 CHIPS 意向書，2026-06-16](https://coherent.gcs-web.com/news-releases/news-release-details/coherent-announces-chips-letter-intent-50-million-expand-world)
- [AXT — InP 出口許可 8-K，2025-06-11](https://www.sec.gov/Archives/edgar/data/1051627/000143774925020087/axti20250611_8k.htm)
- [Federal Register — FCC 26-50 正式規則，2026-09-11](https://www.govinfo.gov/content/pkg/FR-2026-09-11/html/2026-18535.htm)
- [GovInfo — S.5548 提案全文，2026-09-24](https://www.govinfo.gov/content/pkg/BILLS-119s5548is/xhtml/BILLS-119s5548is.html)
- [Lumentum — FQ4 FY2026 財報，2026-08-11](https://investor.lumentum.com/financial-news-releases/news-details/2026/Lumentum-Announces-Fourth-Quarter-and-Full-Fiscal-Year-2026-Results/default.aspx)
- [Fabrinet — FQ4 FY2026 財報及會計調節表](https://www.sec.gov/Archives/edgar/data/1408710/000140871026000026/fn-2026811xex991q426.htm)
- [達發 — AN8928／AN8924 PAM4 DSP，2026-03-17](https://www.airoha.com/group-news/09joI74gjH0LOMIF)
- [聯亞 — 公司年報](https://www.lmoc.com.tw/index.php?i=1&id=391&lang=en&option=module&task=dfile)；[2026 年營收資料](https://www.lmoc.com.tw/index.php?lang=en&temp=investment)
- [東方財富個人文章 — 800G EML 成本拆解，2026-04-11，本文僅作算例](https://caifuhao.eastmoney.com/news/20260411230337084311740)
- [同花順 — 模組廠上半年數字，二手資料待核對](https://stock.10jqka.com.cn/20260901/c679463474.shtml)
- [股癌 EP702 原集，2026-10-03](https://player.soundon.fm/p/954689a5-3096-43a4-a80b-7810b219cef3/episodes/42301381-6003-4b54-a28d-290a3fd2e258)

- [Marvell — PAM4 DSP 產品資料，Spica、Perseus 與類比整合](https://www.marvell.com/products/pam-dsp.html)
- [Marvell — Ara T 等產品於 Q1 2026 起送樣，2026-03-12](https://www.marvell.com/company/newsroom/marvell-1-6t-optical-dsp-ai-data-center-connectivity.html)
- [Lumentum — 100G EML 官方產品與 800G 升級路徑](https://www.lumentum.com/en/products/eml-100g-pam4-cwdm-laser)
- [Lumentum — ELSFP-350 外部雷射模組](https://www.lumentum.com/products/external-laser-source-els-module-ultra-high-power-laser)
- [Coherent — 2024 年報，800G DR8 與不同光源](https://www.coherent.com/content/dam/coherent/site/en/documents/investors/annual-filings/2024/coherent-annual-report-2024.pdf)
- [Coherent — OFC 多種 1.6T 光學技術展示，2026-03-17](https://www.coherent.com/news/press-releases/coherent-demonstrates-next-gen-pluggable-transceiver-ofc-2026)
- [NVIDIA — CPO 光引擎、外部供光與封裝，2025-08-26](https://developer.nvidia.com/blog/how-industry-collaboration-fosters-nvidia-co-packaged-optics/)
- [NVIDIA — Spectrum-X Ethernet Photonics 技術更新，2026-01-06](https://developer.nvidia.com/blog/scaling-power-efficient-ai-factories-with-nvidia-spectrum-x-ethernet-photonics)
