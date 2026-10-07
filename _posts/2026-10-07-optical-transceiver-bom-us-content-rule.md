---
layout: post
title: "800G 光模組近七成成本落在美系晶片，65% 美國含量門檻鎖住的是中國的國產替代"
date: 2026-10-07 19:04:48 +0800
domain: ai-industry
categories: ai-industry
description: "一顆 800G EML 光收發模組約 315 美元成本中，雷射、DSP、Driver 與 TIA 約占七成且以美系為主。傳聞中的 65% 美國 BOM 門檻因此幾乎不影響現有出貨，卻讓中國模組廠難以換用自家晶片降本。"
takeaways:
  - who: "Lumentum"
    value: "EML 產能已排到 2028 年，又握有約一半的全球 EML 出貨量；只要光模組必須維持 65% 美國含量，模組廠換掉它的雷射就會直接跌破門檻，議價力因此延續到 3.2T 世代。"
  - who: "Marvell"
    value: "800G DSP 單顆約占模組成本 28%，又跟 GPU 搶台積電 3 奈米產能；缺貨讓它在 2026 年 9 月傳出漲價 15% 至 20%，LPO 與 CPO 放量前，這筆收入難以被替代。"
  - who: "中際旭創"
    value: "全球市占約三分之一、毛利率 46.6%，靠的是組裝規模而非晶片；若門檻落地，它用中國雷射或 DSP 降本的路會被封住，成本結構只能繼續綁在美系晶片上。"
  - who: "聯亞"
    value: "以磷化銦磊晶與 CW 雷射代工切入矽光模組，8 月營收年增 181%；它的機會來自美系廠分散供應來源，台灣零件在門檻計算中不算美國含量，所以要靠產能與良率取得訂單。"
  - who: "雲端資料中心業者"
    value: "Google、Meta、AWS 每年採購數千萬顆光模組，原本期待每年降價 15% 至 20%；晶片缺貨加上地緣政治門檻，讓 800G 與 1.6T 的單價停止下滑，這筆成本最後由它們承擔。"
---

AI 叢集把數萬顆 GPU 串成一台機器，交換器每一個 800G 連接埠都要插一顆光收發模組，把電訊號轉成光送進光纖。2026 年 10 月 3 日，謝孟恭在 Podcast《股癌》[EP702〈抽不到Radiohead與光模組禁令〉](https://whatmkreallysaid.com/episode.html?file=EP702)拆解了一顆 800G 光模組的內部結構，並評論摩根士丹利在 10 月 1 日流傳的研究：美國可能要求光模組 BOM 至少 65% 來自美國公司，才能繼續出貨。他的結論是這條規則近乎「原狀重申」。本篇沿著同一顆模組，把技術路徑、成本拆解、上游材料與廠商毛利放在一起，計算這個門檻究竟卡住誰。

光模組的價值分配跟它的訊號路徑一一對應。模組內每一段轉換都由一類晶片或元件負責，誰掌握難以替代的那一段，誰就拿走大部分利潤。先看訊號怎麼走。

![800G 光收發模組的訊號路徑：主機電訊號經 DSP、Driver、EML 雷射與光學次組件轉成光；回程經光學次組件、PD、TIA 回到 DSP](/images/ai-industry/2026-10-07/optical-module-signal-path.svg)

圖：800G 光收發模組的兩條訊號路徑。依據[股癌 EP702](https://whatmkreallysaid.com/episode.html?file=EP702) 口述與 [NADDOD 800G OSFP 規格說明](https://www.naddod.com/es/blog/800g-osfp-optical-transceivers-evolution-and-innovation)重繪，不按比例。

## 一顆 800G 模組裡，電和光各走一段

發射端從交換器送出的電訊號先進 DSP。DSP 對 PAM4 訊號做等化、重定時與前向糾錯，再交給 Driver 放大到足以驅動雷射。以中際旭創的 800G EML DR8 為例，8 顆 EML（電吸收調變雷射）各自把一路 100G 電訊號調變成光，經透鏡、隔離器與光纖陣列（FA）耦合進 8 對平行單模光纖，傳 500 公尺。接收端反過來：光經 FA 與透鏡進入 PD（光偵測器）轉成電流，TIA（轉阻放大器）放大成電壓，再回到同一顆 DSP。謝孟恭在節目中的口訣是「出去是 Driver，回來是 TIA，都要經過 DSP」。

這條路徑上有兩處決定成本與良率。第一是 DSP。速率在 100G 以下時模組可以不放 DSP，400G 以後普遍採用 PAM4，每個符號帶 2 bit，雜訊容忍度變小，800G 幾乎都要放，1.6T 則是必需。代價是功耗：[IEEE 802.3df 工作小組 2022 年 11 月的資料](https://grouper.ieee.org/groups/802/3/df/public/22_11/chang_3df_01a_2211.pdf)顯示，一顆 11 到 12W 的 800G 模組中，DSP 約占 65% 的功耗，雷射約 12%，TEC 與 TIA 各約 10%。第二是光的對準。把 8 道光同時精準耦合進光纖，需要主動對位設備與製程經驗，謝孟恭以大立光切入 FA 為例，指出「把光對準本身就是不容易的」。

這兩處各自對應一群供應商：DSP 集中在少數美系 IC 設計公司，對準與被動光學則由大量台、日、中廠商分擔。下一步把它們換算成金額。

## 315 美元的成本有七成落在四類晶片

公開的拆解數字來自中國財經平台東方財富的一篇[個人撰稿文章（2026 年 4 月）](https://caifuhao.eastmoney.com/news/20260411230337084311740)，並非券商正式報告，適合當量級參考。它把 800G EML 模組的成本列為約 315 美元，對應售價約 380 至 400 美元；節目中把 315 美元稱為 ASP，金額與此拆解的成本相同，較合理的解讀是成本。

![800G EML 光收發模組 BOM 成本拆解，EML 92 美元、DSP 88 美元、Driver 與 TIA 38 美元、被動光學 29 美元、PD 24 美元，其餘為 PCB、外殼與被動元件](/images/ai-industry/2026-10-07/optical-module-bom-800g.svg)

圖：800G EML 模組 BOM。依據[東方財富財富號 2026 年 4 月拆解](https://caifuhao.eastmoney.com/news/20260411230337084311740)整理；原文各項加總 309 美元，與其標示的合計 315 美元差約 6 美元，以「原文未分列」呈現。

| 成本項目 | 數量 × 單價 | 金額（美元） | 占比 | 主要供應來源 |
| --- | --- | --- | --- | --- |
| EML 雷射 | 8 × 11.5 | 92 | 29.2% | Lumentum、Coherent、Broadcom、三菱電機、住友電工 |
| DSP | 1 × 88 | 88 | 27.9% | Marvell、Broadcom、MaxLinear、達發 |
| Driver 與 TIA | 4 × 9.5 | 38 | 12.1% | Semtech、MACOM、Broadcom、Marvell |
| 被動光學 | 隔離器、FA、透鏡、耦合器 | 29 | 9.2% | 天孚通信、上詮、波若威及日系廠 |
| PD | 8 × 3.0 | 24 | 7.6% | 美、日、台、中皆有 |
| 高速 PCB 與陶瓷基板 | — | 14.5 | 4.6% | 台、日、中 |
| 外殼、散熱、連接器 | — | 14.5 | 4.6% | 台、中 |
| 被動元件與 PMIC | — | 9 | 2.9% | 多國 |
| 原文未分列 | 可能為 TEC、MCU 或組裝 | 6 | 1.9% | — |

EML、DSP、Driver 與 TIA 合計 218 美元，約 69%，正好落在節目引述摩根士丹利「60 幾 % 本來就是美國元件」的區間。剩下約三成由被動光學、PCB、外殼與被動元件構成，供應商數量多、單項金額小。另一組券商通用的口徑是「光晶片及組件約 50%、電晶片約 15%」（[財聯社](https://www.cls.cn/detail/1426329)），切法不同，量級一致。

DSP 的單價波動最大。[鉅亨網 2026 年的整理](https://hao.cnyes.com/post/269937)顯示 800G DSP 長約價約 45 至 70 美元，現貨再溢價 10% 至 20%；較早的報導中 Marvell 報價曾達 90 至 100 美元。謝孟恭在 [EP699](https://whatmkreallysaid.com/episode.html?file=EP699)（2026 年 9 月 23 日）提到美系 DSP 廠傳出漲價 15% 至 20%，大客戶漲幅較小。

矽光路線會重寫這張表。[PhotonCap 2026 年 3 月的分析](https://photoncap.net/p/the-silicon-photonics-light-source)指出，矽光模組用 1 至 4 顆 CW 雷射搭配矽調變器取代 8 顆 EML，雷射總成本由 80 至 100 美元以上降到 20 至 40 美元；但這個優勢只在 DR8 這類平行單模規格成立，2×FR4 需要 4 個波長，EML 仍是主流。1.6T 方面，[野村 2026 年 9 月 23 日的專家會議紀要](https://www.stockfeel.com.tw/?p=277131)轉述 3 奈米 DSP 約 130 至 180 美元、模組成本約 450 至 550 美元，DSP 占比與 800G 相當或更高。

## 晶片廠的毛利率比模組廠高出一截

成本結構決定了利潤怎麼分。把供應鏈上各環節 2026 年的財報毛利率排在一起，晶片與組裝之間的差距一目了然。

![光通訊供應鏈各環節毛利率，源杰 80.4%、光聖 62.5%、Lumentum 50.4%、新易盛 48.5%、中際旭創 46.6%、Fabrinet 12.2%](/images/ai-industry/2026-10-07/optical-chain-gross-margin.svg)

圖：各環節毛利率。依據[源杰 2026 上半年](https://stock.10jqka.com.cn/20260722/c678335504.shtml)、[光聖 2026 年第二季](https://www.moneyweekly.com.tw/_Article?AID=246935)、[Lumentum FQ4'26](https://investor.lumentum.com/financial-news-releases/news-details/2026/Lumentum-Announces-Fourth-Quarter-and-Full-Fiscal-Year-2026-Results/default.aspx)、[中際旭創與新易盛 2026 上半年](https://stock.10jqka.com.cn/20260901/c679463474.shtml)、[Fabrinet FQ4'26](https://www.sec.gov/Archives/edgar/data/0001408710/000140871026000026/fn-2026811xex991q426.htm)財報整理。

中國雷射晶片廠源杰 2026 上半年毛利率 80.4%，營收年增 351%；Lumentum 非 GAAP 毛利率 50.4%。模組廠中際旭創的光模組毛利率 46.6%、新易盛 48.5%，已比去年同期的四成上下明顯擴張，原因是缺料讓 800G 停止年年降價。AAOI 財務長在 [2026 年 3 月](https://www.marketbeat.com/instant-alerts/applied-optoelectronics-cfo-flags-laser-bottleneck-as-hyperscalers-push-800g-and-16t-optics-2026-03-03/)表示，800G 與 1.6T 約每 Gbps 0.5 美元，往年每年 15% 至 20% 的降價「目前不太可能」。代工的 Fabrinet 毛利率只有 12.2%，台灣閒置 SMT 廠承接 ShuffleBox 等光通代工時，謝孟恭在 EP652 估計毛利約一成上下。

毛利擴張的成本由採購端承擔。[TrendForce 與 LightCounting](https://www.telecomtv.com/content/access-evolution/global-ai-optical-transceiver-market-to-reach-26bn-in-2026-says-trendforce-55327/) 估計 AI 光模組市場由 2025 年約 165 億美元成長到 2026 年約 260 億美元，需求超出供給約 30%。用量隨網路架構變化：[FiberMall 的試算](https://www.fibermall.com/blog/a100-h100-gh200-cluster.htm)顯示 H100 三層 fat-tree 每顆 GPU 約配 2.5 顆 800G 模組，兩層約 1.5 顆；GB200 NVL72 的 scale-out 網路仍是每顆 GPU 一張 400G 或 800G 網卡，每顆 GPU 對應的光模組數量沒有減少。[TrendForce 2026 年 2 月](https://www.trendforce.com/presscenter/news/20260210-12919.html)另估 Google 今年近 400 萬顆 TPU 會帶動 800G 以上模組逾 600 萬顆。採購量以千萬顆計，又失去年年降價，雲端業者每年多付的金額直接轉成晶片廠與模組廠的毛利。

光聖是一個例外。它做 MPO 連接器、高芯數光纖與跳線，2026 年第二季毛利率 62.5%，高於模組廠。這說明「三成低毛利」是整體平均，掌握高密度光纖或 Google 等單一大客戶認證的利基廠，在缺貨期一樣能拿到晶片級的毛利。

## 換一種模組規格，就換一批供應商

光模組有多種規格，每一種用到的零件組合不同，這決定了哪家供應商吃到哪一塊。

| 產品 | 光源 | DSP | Driver 與 TIA | 隔離器與 TEC | FA／FAU | 光纖與距離 |
| --- | --- | --- | --- | --- | --- | --- |
| 800G DR8（EML） | 8 顆 EML，長在磷化銦上 | 有 | 有 | 有 | 有 | 平行單模，500 公尺 |
| 800G DR8（矽光） | 1 至 4 顆 CW 雷射加矽調變器 | 有 | 有 | 部分 | 有 | 平行單模，500 公尺 |
| 800G 2×FR4 | 8 顆 EML，4 波長 × 2 | 有 | 有 | 有 | 部分 | 雙工單模，2 公里 |
| 800G SR8 | 8 顆 VCSEL，長在砷化鎵上 | 有 | 有 | 無 | 部分 | 多模，50 至 100 公尺 |
| LPO | 同上任一 | 拿掉 | 改為線性設計 | 依光源 | 有 | 短距，靠交換器端 SerDes |
| AEC 銅纜 | 無雷射 | 兩端 Retimer | 無 | 無 | 無 | 機櫃內 7 公尺以下 |
| CPO | 外部光源，約 400mW CW | 拿掉 | 整合進光引擎 | 無 | 大量 | 光引擎與交換晶片共同封裝 |

依據 [NADDOD](https://www.naddod.com/es/blog/800g-osfp-optical-transceivers-evolution-and-innovation)、[Semtech 線性光學晶片組](https://www.semtech.com/company/press/semtech-launches-224-gbps-ic-family-for-linear-optics-era)與 [PhotonCap](https://photoncap.net/p/the-silicon-photonics-light-source) 整理。

這張表裡有兩個方向相反的力量。LPO 與 CPO 拿掉 DSP，直接削掉約 28% 的 BOM 與六成以上的功耗，對 Marvell、Broadcom 的 DSP 事業是長期壓力。另一方面，FA／FAU 在每一種光路線都需要，到 CPO 用量更大，是少數不論路線如何演變都會增加的環節。

CPO 的成本會集中到光引擎與封裝。一份 [2026 年 7 月的產業估算](https://www.moneyweekly.com.tw/_Article?AID=236750)把一台 1.6T CPO 交換器的 BOM 列為約 75,803 美元：72 個光引擎約 32,400 美元（約 43%），單模光纖約 12,343 美元（16%），交換 ASIC 約 12,000 美元（16%），外部光源約 7,200 美元，MPO 與線材約 5,760 美元，FAU 約 3,600 美元，shuffle box 約 2,500 美元。與可插拔模組相比，DSP 與模組外殼消失，雷射從每通道一顆變成少數高功率外部光源，價值移向台積電 COUPE 這類矽光封裝、光纖與 FAU。

謝孟恭在 EP699 提醒，市場容易把這看成零和：CPO 起來、DSP 就要死。他的觀察是被認為會被取代的產品常常持續放量，賺得比預期更久，DSP 廠也可能把功能做成 chiplet 或以 SerDes IP 形式繼續取得價值。[NVIDIA 在 2026 年 5 月底宣布](https://nand-research.com/nvidia-is-rewiring-the-data-center-with-light/) Quantum-X 與 Spectrum-X Photonics 進入量產，[Broadcom 的 Tomahawk 6 Davisson](https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-tomahawkr-6-davisson-industrys-first-1024) 也已出貨；業界普遍估計大規模放量在 2027 至 2028 年，在那之前 800G 與 1.6T 可插拔模組仍是出貨主力。本站先前分析 [AI collective 改接光路的成本]({% post_url 2026-09-30-collective-optical-reconfiguration-cost-boundary %})時也指出，光互連的架構選擇要把切換與等待成本一起算，速度更快的方案未必立刻勝出。

## 磷化銦基板與 3 奈米產能是兩個最緊的上游

EML、CW 雷射與 PD 都長在磷化銦（InP）基板上，VCSEL 則長在砷化鎵上。磊晶廠在基板上一層層長出三五族化合物，讓材料能發光，謝孟恭在 EP619 用「千層派」比喻這道製程。

基板高度集中：[Kitco 2026 年 6 月的報導](https://www.kitco.com/news/off-the-wire/2026-06-11/chinas-control-over-indium-phosphide-exports-threatens-ai-data-centre)指出，AXT（北京通美）與住友電工合計約占 80%，JX 約 10%，6 吋 InP 晶圓價格漲了約 250%，達每片約 5,000 美元。原料端更集中。2025 年 2 月 4 日，中國把銦納入出口管制，AXT 到 2025 年 6 月才拿到第一張出口許可（[AXT 8-K](https://www.sec.gov/Archives/edgar/data/1051627/000143774925020087/axti20250611_8k.htm)）；[TrendForce 2026 年 8 月的研究](https://trendforce.com/news/2026/08/06/news-inp-shortage-emerges-as-ai-optical-interconnect-bottleneck/)指出中國占全球精煉銦約 70%。這個前例說明材料管制會直接傳導到雷射產能：同一時期，Lumentum 表示 EML 產能已售到 2028 年。謝孟恭在 EP686 說磷化銦基板是「市場上可能最缺乏的東西」，台美公司都說對原料有信心，但財報數字看得出仍在缺料。

擴產已經啟動。[JX 計畫到 2030 財年投資 1,200 億日圓](https://www.trendforce.com/news/2026/06/16/news-jx-advanced-metals-to-invest-jpy-120b-through-fy2030-expand-inp-capacity-up-to-10x-as-cpo-demand-accelerates/)，產能最多擴大 10 倍；住友電工到 2028 財年產能提高到 2024 財年的 3.1 倍；Coherent 德州 Sherman 的 6 吋 InP 產線在 2026 年產能翻倍。新產能多數在 2027 年後才開出。

第二個瓶頸是 DSP 的晶圓產能。最先進的 1.6T DSP 用台積電 3 奈米製造，跟 GPU 搶同一批產能。鉅亨網的整理估計 1.6T DSP 在 2026 年缺 300 萬至 400 萬顆，2027 年缺口逾 2,000 萬顆。這與本站分析 [HBM 搶 DRAM 晶圓]({% post_url 2026-09-30-hbm-wafer-allocation-memory-profit %})的邏輯相同：AI 晶片吃掉先進製程產能後，周邊晶片的供給彈性跟著下降，價格因此上漲。中國 DSP 廠有設計能力，卻拿不到 3 奈米或 5 奈米產能，這是它們追不上 1.6T 的主因。

## 65% 門檻正好卡在美系晶片的現有占比

[404K Research 在 2026 年 10 月 1 日整理](https://404kresearch.substack.com/p/fcc-optical-transceiver-restrictions)的摩根士丹利觀點有三點：美國聯邦通訊委員會（FCC）若出手，可能從中國製 3.2T 模組開始限制；800G 與 1.6T 預計不受影響；BOM 價值中至少 65% 來自美國公司的模組可以豁免。3.2T 預計 2028 年起量、2029 年放量。截至 10 月 5 日，FCC 尚未公告正式條文，報告原文也未公開。

用前面的 BOM 表計算，門檻的作用就很清楚。一顆模組若 EML、DSP、Driver 與 TIA 全用美系，美國含量約 218／315，也就是 69%，剛好跨過 65%。中國模組廠只要把 EML 換成源杰的雷射，美國含量就掉到約 40%；換掉 DSP 也是約 41%。這條規則對組裝地點幾乎沒有限制，限制的是中國廠用自家晶片取代美系晶片。謝孟恭的判讀相同：美國把毛利高、有核心技術的環節留在自己手上，組裝讓外面做也可以。

這也解釋了為何門檻不會很快收緊。[Cignal AI 的資料](https://cignal.ai/2026/08/fcc-ban-on-new-chinese-optical-modules/)顯示 2026 年第一季全球光模組市場 77 億美元，中國廠合計約 60%，中際旭創一家約 34%。中際旭創與新易盛出貨北美走泰國、馬來西亞的海外廠（EP685），若直接封殺中國模組，美國資料中心的建置會先受傷；上游的銦又在中國手上，逼得太緊會招來反制。

門檻還有一個較少被討論的作用：價格保護。海外研調擔心中國大規模擴產光通零組件，會像過去那樣把價格壓垮。只要美國市場要求 65% 美國含量，中國零組件廠就只能在中國與其他市場競爭，美系與非中系廠的報價較不受衝擊。

## 台灣廠商落在去中化的第二輪訂單

台灣零件在 65% 計算中不算美國含量，因此台廠的機會來自美系廠分散供應來源，而且要靠產能與良率取得。依環節排列：

| 環節 | 台灣廠商 | 公開資料 |
| --- | --- | --- |
| DSP | 達發 | 400G 與 800G PAM4 DSP，全球前五大模組廠試用中，市占個位數 |
| 磊晶與雷射 | 聯亞、全新、英特磊 | 聯亞 Datacom 占營收 80% 至 85%，與住友簽 5 年 InP 供貨合約；全新 MOCVD 由 5 台增至 7 台 |
| 雷射封裝 | 華星光、眾達 | 華星光 CW 雷射月產能擴至 2027 年 600 萬顆以上；眾達與 Broadcom 合作雷射光學封裝 |
| 三五族代工 | 穩懋、宏捷科 | 被列入 3.2T 去中化供應名單 |
| FA、連接器、光纖 | 上詮、波若威、大立光、光聖 | 上詮參與台積電矽光聯盟；波若威為 NVIDIA CPO 夥伴；大立光 9 月建置 FA 試產線 |
| 矽光封裝與 CPO 系統 | 台積電、日月光（矽品）、鴻海、台達電 | 台積電 COUPE 獲 NVIDIA、Broadcom 採用；台達電為 Broadcom CPO 交換器製造夥伴 |

依據 [TechNews 2026 年 3 月](https://technews.tw/2026/03/17/taiwan-epi-wafers-and-optical-communication/)、[優分析](https://uanalyze.com.tw/articles/3704954732)、[NAND Research](https://nand-research.com/nvidia-is-rewiring-the-data-center-with-light/)、[TrendForce 2026 年 7 月](https://www.trendforce.com/presscenter/news/20260727-13151.html)與[股癌 EP702](https://whatmkreallysaid.com/episode.html?file=EP702) 整理。

謝孟恭在節目中把台廠的機會分成三種：美系廠擔心夜長夢多，把機構件、光學件甚至組裝移到台灣，EML 也可能找台廠封裝；美系找 second source 時，從中國改找台灣；中國去美化時，透過第三方找台積電投片，或在禁令前提前拉貨。他特別指出達發目前鎖定 400G，到 3.2T 還有幾個世代，不會是第一波。台廠的位置偏向 Tier 2、Tier 3 與可插拔產品，離 GPU 核心較遠；台積電與先進封裝是例外。

## 接下來兩年會看到的三組數字

照前述機制推演，2027 年底前光模組的利潤仍會集中在 EML 與 DSP 兩端。InP 新產能要到 2027 年後才開出，3 奈米 DSP 缺口在 2027 年擴大，兩者都讓 800G 與 1.6T 的售價維持在每 Gbps 0.5 美元附近，模組廠毛利率維持四成以上。CPO 在 2028 年之前占交換器出貨的比重仍低，可插拔模組不會被快速取代。

三組數字可以驗證或推翻這個推演。第一是 Lumentum 與 Coherent 的 EML、CW 雷射產能與訂單能見度；若 2027 年上半年出現價格鬆動，代表 InP 瓶頸比預期更早解除。第二是 Marvell、Broadcom 的 DSP 報價與台積電 3 奈米產能分配；若 DSP 停止漲價，LPO 與 CPO 的替代壓力就提前到來。第三是 FCC 是否在 2026 年底前發布正式條文，以及門檻適用的速率；若從 1.6T 甚至 800G 開始適用，中國模組廠的海外產能也會被迫重組。

最強的反向情境是中國廠繞過門檻。中國擁有銦原料與大量組裝產能，若源杰、光迅等廠把 200G EML 與 CW 雷射良率做上來，再透過海外子公司與非美市場消化產能，價格戰可能從 2027 年開始外溢到美國以外的資料中心，壓縮全球模組廠與非美零件廠的毛利。目前維持原推演的理由是：美國以外的 AI 資本支出規模較小，而 3 奈米 DSP 產能仍掌握在台積電與美系客戶手上。

## 證據範圍

- 800G BOM 拆解、ASP 與 2026 年各客戶需求量來自個人撰稿文章與調研紀要轉述，非券商正式報告，適合作為量級參考；原文各項加總與合計相差約 6 美元。
- 摩根士丹利報告原文與確切發布日未公開，65% 門檻、3.2T 起始世代等內容取自研究機構與媒體轉述；截至 2026 年 10 月 5 日 FCC 尚未公告。
- 雷射、DSP、VCSEL 市占與 DSP 缺口數字多來自研調摘要或媒體轉述，口徑可能不同；VCSEL 市占可能包含 3D 感測應用。
- 毛利率取自各公司公開財報，期間不完全一致（上半年、單季、非 GAAP）。
- 節目內容依據逐字稿網站整理，語音轉文字可能有誤差，以原始音檔為準。
- CPO 交換器 BOM 來自未具名機構的產業估算，規格推定接近 NVIDIA Quantum-X Photonics，未經廠商確認。

## 來源

- [股癌 EP702〈抽不到Radiohead與光模組禁令〉逐字稿，2026-10-03](https://whatmkreallysaid.com/episode.html?file=EP702)；[原集音檔（SoundOn）](https://player.soundon.fm/p/954689a5-3096-43a4-a80b-7810b219cef3/episodes/42301381-6003-4b54-a28d-290a3fd2e258)
- [股癌 EP699〈小學生棒球課與DSP漲價〉逐字稿，2026-09-23](https://whatmkreallysaid.com/episode.html?file=EP699)
- [東方財富財富號：800G 光模組 BOM 拆解，2026-04](https://caifuhao.eastmoney.com/news/20260411230337084311740)
- [財聯社：光模組成本結構](https://www.cls.cn/detail/1426329)
- [IEEE 802.3df：chang_3df_01a_2211，2022-11](https://grouper.ieee.org/groups/802/3/df/public/22_11/chang_3df_01a_2211.pdf)
- [NADDOD：800G OSFP 光模組演進](https://www.naddod.com/es/blog/800g-osfp-optical-transceivers-evolution-and-innovation)
- [鉅亨網：DSP 價格與缺口](https://hao.cnyes.com/post/269937)
- [PhotonCap：矽光光源，2026-03-20](https://photoncap.net/p/the-silicon-photonics-light-source)
- [StockFeel：野村專家會議紀要，2026-09-23](https://www.stockfeel.com.tw/?p=277131)
- [MarketBeat：AAOI 財務長談雷射瓶頸，2026-03-03](https://www.marketbeat.com/instant-alerts/applied-optoelectronics-cfo-flags-laser-bottleneck-as-hyperscalers-push-800g-and-16t-optics-2026-03-03/)
- [同花順：源杰科技 2026 上半年](https://stock.10jqka.com.cn/20260722/c678335504.shtml)
- [同花順：中際旭創與新易盛 2026 上半年](https://stock.10jqka.com.cn/20260901/c679463474.shtml)
- [Lumentum FQ4'26 財報](https://investor.lumentum.com/financial-news-releases/news-details/2026/Lumentum-Announces-Fourth-Quarter-and-Full-Fiscal-Year-2026-Results/default.aspx)
- [Fabrinet FQ4'26 8-K](https://www.sec.gov/Archives/edgar/data/0001408710/000140871026000026/fn-2026811xex991q426.htm)
- [MoneyWeekly：光聖 2026 年第二季](https://www.moneyweekly.com.tw/_Article?AID=246935)
- [MoneyWeekly：CPO 交換器 BOM 估算，2026-07-13](https://www.moneyweekly.com.tw/_Article?AID=236750)
- [Semtech：224G 線性光學晶片組](https://www.semtech.com/company/press/semtech-launches-224-gbps-ic-family-for-linear-optics-era)
- [NAND Research：NVIDIA 以光重構資料中心](https://nand-research.com/nvidia-is-rewiring-the-data-center-with-light/)
- [Broadcom：Tomahawk 6 Davisson](https://investors.broadcom.com/news-releases/news-release-details/broadcom-announces-tomahawkr-6-davisson-industrys-first-1024)
- [Kitco：中國控制 InP 出口，2026-06-11](https://www.kitco.com/news/off-the-wire/2026-06-11/chinas-control-over-indium-phosphide-exports-threatens-ai-data-centre)
- [AXT 8-K，2025-06-11](https://www.sec.gov/Archives/edgar/data/1051627/000143774925020087/axti20250611_8k.htm)
- [TrendForce：InP 短缺成 AI 光互連瓶頸，2026-08-06](https://trendforce.com/news/2026/08/06/news-inp-shortage-emerges-as-ai-optical-interconnect-bottleneck/)
- [TrendForce：JX 擴產 InP，2026-06-16](https://www.trendforce.com/news/2026/06/16/news-jx-advanced-metals-to-invest-jpy-120b-through-fy2030-expand-inp-capacity-up-to-10x-as-cpo-demand-accelerates/)
- [404K Research：FCC 光模組限制，2026-10-01](https://404kresearch.substack.com/p/fcc-optical-transceiver-restrictions)
- [Cignal AI：FCC 對中國光模組，2026-08](https://cignal.ai/2026/08/fcc-ban-on-new-chinese-optical-modules/)
- [TechNews：台灣磊晶與光通訊，2026-03-17](https://technews.tw/2026/03/17/taiwan-epi-wafers-and-optical-communication/)
- [優分析：聯亞](https://uanalyze.com.tw/articles/3704954732)
- [TelecomTV／TrendForce：AI 光模組市場 2026 年達 260 億美元](https://www.telecomtv.com/content/access-evolution/global-ai-optical-transceiver-market-to-reach-26bn-in-2026-says-trendforce-55327/)
- [FiberMall：GPU 叢集光模組比例](https://www.fibermall.com/blog/a100-h100-gh200-cluster.htm)
- [TrendForce：Google TPU 與光模組，2026-02-10](https://www.trendforce.com/presscenter/news/20260210-12919.html)
- [TrendForce：CPO 交換器，2026-07-27](https://www.trendforce.com/presscenter/news/20260727-13151.html)
