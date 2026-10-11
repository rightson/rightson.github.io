---
layout: essay
title: "當基金被迫縮短持有期限，長期資金如何捕捉市場錯價"
date: 2026-10-11 12:27:33 +0800
permalink: /essays/time-horizon-arbitrage/
description: "Bill Ackman 用指數化、多策略基金風控與短天期選擇權解釋股價跳空；結合 IBM 2026 年暴跌、資金去槓桿研究及估值算例，分析時間期限錯配何時能形成低吸優勢。"
takeaways:
  - who: "Millennium 與 Citadel"
    value: "Ackman 指出，多策略基金把交易交給受短期風控與績效制度約束的 Pod；當類似部位同時接近風險限額，減碼需求可能放大財報事件後的價格變動，但個別公司的賣壓來源仍需驗證。"
  - who: "指數型基金"
    value: "被動持有人較少因單季財報主動調整配置，讓當下願意成交的邊際買賣方更值得研究；這項結構性變化可能增加價格對資金流的敏感度，但不能把指數持股直接視為市場流通股消失。"
  - who: "Pershing Square"
    value: "Ackman 強調長期且穩定的資金基礎，使投資組合能承受價格先跌、價值後實現的時間落差；這種優勢來自負債與資產期限匹配，並以選對企業及避免永久損失為先決條件。"
  - who: "IBM"
    value: "IBM 2026 年第二季預告的營收年增僅 1%、基礎架構營收減少 7%，引發 7 月 14 日約四分之一市值的單日跌幅；事件既可能包含訂單流放大效果，也顯示 AI 支出轉向造成的基本面修正不能忽略。"
---

2026 年 9 月，Bill Ackman 在 [The Holy Grail of Investing 訪談（38:20–41:44）](https://singjupost.com/transcript-of-bill-ackman-interview-holy-grail-of-investing-podcast/)提出一個市場結構問題：企業價值往往需要數年實現，部分主導交易的機構資金卻受到每天的風控、每季的績效與年底的報酬結算約束。兩種時間尺度開始分離。

這個差異會讓投資人面對同一家公司，卻做出表面矛盾的選擇。經理人可以相信企業兩年後會變得更值錢，同時仍在今天賣出，因為眼前的回撤、槓桿限制或績效考核不允許繼續持有。對能穩定持有多年的資金而言，這種被動賣壓可能帶來超額報酬的機會。

整套推論的前提是：**市場成交價受當下買賣盤決定，企業長期價值則受未來能產生多少現金流決定。** 當兩者短期偏離，需要分辨價格變化有多少來自新的基本面資訊，又有多少來自誰必須立刻交易。

![指數化、Pod 風控與選擇權避險如何影響財報事件的訂單流，以及跌價後的短期錯價與價值陷阱兩種情境](/images/essays/2026-10-11/forced-selling-horizon-gap.svg)

[開啟完整流程圖，可放大閱讀](/images/essays/2026-10-11/forced-selling-horizon-gap.svg)

圖：投資期限錯配與價格形成的概念示意，屬**參考設計與假設算例**。結構取自 [Ackman 2026 年訪談](https://singjupost.com/transcript-of-bill-ackman-interview-holy-grail-of-investing-podcast/)；箭頭表示可能的因果路徑，非 IBM 當日交易流的實測結果。

## 大型企業一天跌四分之一，必須同時檢查價值與賣壓

2026 年 7 月 14 日，IBM 發布第二季初步財報：[營收 172 億美元、年增 1%，軟體營收年增 5%，基礎架構營收年減 7%](https://newsroom.ibm.com/2026-07-14-Arvind-Krishnas-Letter-to-IBM-Investors)。IBM 說明，部分企業客戶正在將預算轉往 AI 伺服器、記憶體等基礎設施。IBM 股價當日[下跌約 25%](https://www.investing.com/news/stock-market-news/ibm-expects-secondquarter-revenue-below-estimates-4790496)，創紀錄的跌幅成為 Ackman 訪談中的例子。

這個事件有兩個必須分開處理的問題。

首先，IBM 的長期獲利能力是否已改變？企業 IT 支出轉向 AI 可能只是訂單遞延，也可能使既有軟硬體組合失去原本的成長速度。後者會同時影響未來營收、毛利與估值倍數。IBM 在 [7 月 22 日正式第二季財報](https://newsroom.ibm.com/2026-07-22-IBM-RELEASES-SECOND-QUARTER-RESULTS)確認了收入與獲利壓力；以「只錯過一季」解讀這場下跌，仍然太快。

其次，為什麼市場選擇在極短的時間完成這麼大的重新定價？原本由不同投資人分散承受的風險，若在財報公布後被同時壓縮，市場需要找到願意立即接手的反向交易者。大型公司也可能出現報價跳空；即使總交易量很高，特定價位之間仍未必有足夠深度。

**價格暴跌是需要解釋的現象；基本面惡化與被迫減碼是兩個待檢驗的來源。** 把所有跌幅都解讀成機構錯殺，會把最重要的估值判斷省略。

## 指數化改變誰在持有，Pod 風控改變誰必須賣出

Ackman 描述了三種資金行為，合在一起可形成市場短期化的假說。

指數基金依成分股、權重及資金申贖配置，不會像主動基金那樣，因每家公司財報失望而完整重做持股判斷。長期被動持股比重提高後，**邊際交易者**的行為可能更直接影響短期價格。這不等於指數基金持股被鎖死，也不等於被動資金一定製造更大波動。指數再平衡與 ETF 申贖本身仍會帶來大量交易。

[Xavier Gabaix 與 Ralph Koijen 2021 年的 Inelastic Markets Hypothesis](https://www.nber.org/papers/w28967)提供一套可檢驗的機制：當市場股票需求對價格不夠敏感，資金流的價格影響可能遠大於流入或流出的金額。論文研究的是整體股市的資金流與價格彈性，不能直接拿其中的乘數估算單一公司財報日跌幅。

第二種力量是 Pod 型多策略避險基金。Millennium、Citadel 的交易團隊可能有分散的投資主題，卻共用對回撤與風險的強約束。用一個假設算例說明：某 Pod 自有資本 1 億美元，多空部位絕對值合計 5 億美元；即使淨市場曝險很低，單一持股若快速下跌，仍可能消耗風險預算。管理人為了使風險回到額度內，可以在仍看好長期價值時先減碼。

這條價格回饋路徑很清楚：

> 財報不如預期 → 價格下跌 → 回撤與風險額度收緊 → 多個持有相似部位的團隊同時降低曝險 → 賣壓再度衝擊價格。

上述金額是**假設算例**，不是 Millennium、Citadel 的實際帳戶資料。更重要的是，Pod 經理人也可能利用下跌建立反向部位；沒有持倉與訂單流資訊，無法把整體賣壓歸因於特定機構。

## 短天期選擇權讓對沖更快，方向未必一致

Ackman 另外提到 0DTE（當日到期）選擇權與短期投機。選擇權造市商會隨標的價格改變而調整 Delta hedge；他們持有的 Gamma 方向，決定避險單會傾向跟隨行情，還是逆向吸收行情。

- **Short Gamma：** 標的上漲可能需要買入、下跌可能需要賣出，形成追價與追跌。
- **Long Gamma：** 標的上漲可能賣出、下跌可能買入，形成相反的穩定力量。

[Cboe 2025 年的 SPX 0DTE 研究](https://www.cboe.com/insights/posts/0-dt-es-decoded-positioning-trends-and-market-impact)估計，當時造市商的淨 Gamma 避險流量規模相對 SPX 每日流動性很小；[Adams 等人的研究（2025，2026 年修訂）](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5641974)甚至發現樣本期間的平均效果偏向**降低**指數波動。

所以，選擇權交易量變大，並不能直接推出股票更容易暴跌。特別是 IBM 單一個股事件，SPX 0DTE 的研究只提供市場機制參照，不能當作 IBM 當日價格的成因證據。

## 被迫賣出確實存在，2020 年的去槓桿提供了前例

2020 年 3 月市場劇烈震盪時，槓桿與補繳保證金迫使部分機構同時降低部位。[美國聯準會 2020 年金融穩定報告](https://www.federalreserve.gov/publications/2020-may-financial-stability-report-asset-valuation.htm)指出，槓桿型基金被迫出售資產、擁擠交易同時調整，可能加劇市場流動性壓力。

更具體的[聯準會 2021 年研究](https://www.federalreserve.gov/econres/notes/feds-notes/sizing-hedge-funds-treasury-market-activities-and-holdings-20211006.html)估計，避險基金於 2020 年 3 月持有的美國公債減少約 1,410 億美元、相當於前月估計部位的 13%。這是**美國公債市場**的壓力案例，足以說明去槓桿如何放大市場失序，不能直接推論每次股票財報暴跌都屬同一機制。

這類事件的共同條件是：賣方承受短期資金或風險約束、不同機構持有相似部位，而反向資金當下不足。當市場恢復吸收能力，價格與價值的落差才有機會縮小。

## 從 100 美元跌到 75 美元，低吸可能賺 26.7%，也可能再賠 20%

假設一家公司財報前股價為 100 美元，發布不利消息後跌到 75 美元。以下全部是**假設算例**，無關 IBM 的合理股價：

| | 短期錯價 | 價值陷阱 |
| --- | ---: | ---: |
| 原股價 | $100 | $100 |
| 財報後市場價格 | $75 | $75 |
| 重估後長期內在價值 | $95 | $60 |
| 現價回到內在價值的空間 | **+26.7%** | **−20.0%** |
| 關鍵差異 | 市價跌幅超過內在價值損失 | 市價尚未反映長期惡化 |

第一個情境，若正常化的營收、毛利與自由現金流大致維持，25% 的價格下跌可能主要反映急迫賣壓。第二個情境，若 AI 或其他技術變化正在永久壓縮產品需求與獲利能力，跌掉四分之一仍可能偏貴。

這使低吸策略的問題變得精確：**估計企業價值改變多少，才能知道價格是否超跌。** 股價跌幅是尋找研究標的的起點，無法充當安全邊際本身。

例如本站的[HBM 晶圓產能與記憶體利潤分析](/ai-industry/2026/09/30/hbm-wafer-allocation-memory-profit.html)，就是從產能排擠、良率、合約價與現金流拆解企業獲利來源。只有先回答這類問題，才知道價格事件究竟改變了多少未來價值。

## 穩定資本是優勢，但估值能力決定它能否轉成報酬

Ackman 在同一場訪談的 [14:14–18:45](https://singjupost.com/transcript-of-bill-ackman-interview-holy-grail-of-investing-podcast/)談到 Pershing Square 的資本結構：透過長期、較穩定的資本來源，降低投資人短期贖回迫使經理人賣出的可能。他將這件事描述成資產與負債的期限匹配。

這可以套用到個人投資者。若資金不需要在接下來一年用於生活開銷、抵押品補繳或其他承諾，投資人便能把決策期限延伸到企業價值真正發生改變的時間。相反地，即使原先研究判斷正確，槓桿與現金需求也可能使投資人賣在下跌最嚴重的時刻。

實務上可以依序檢查五件事：

| 判斷環節 | 應取得的具體資訊 | 容易犯的錯 |
| --- | --- | --- |
| 基本面 | 正常化自由現金流、競爭地位、需求是否永久轉向 | 把結構衰退當季節性遞延 |
| 市場供給 | 大成交量、持股集中度、融資與基金去槓桿線索 | 單憑暴跌就宣稱「主力被迫賣」 |
| 估值 | 保守與悲觀情境下的價值區間 | 用暴跌前股價取代內在價值 |
| 資金期限 | 未來 12–24 個月現金需求、槓桿與持股集中度 | 自己反而成為下一個被迫賣方 |
| 驗證與退出 | 後續訂單、毛利、指引、分析師預估與競爭變化 | 將「長期持有」當作拒絕修正錯誤 |

到 **2027–2028 年**，可用事件研究檢驗這套方法：將大型公司財報後單日跌幅達一定幅度的事件分組，比較未來數季獲利預估修正幅度、股票相對報酬，以及機構持股集中或市場流動性指標。如果暴跌後基本面預估保持穩定的一組，扣除風險與交易成本後仍持續優於對照組，時間期限錯配才更接近一個可實證的投資優勢。反之，若獲利預估持續下修且價格沒有均值回歸，逢低買進就可能只是接住價值下修的股票。

## 結語

Ackman 這段話把投資競爭分成兩個時間尺度：一邊的資金追求短期績效並受即時風控限制；另一邊的資金可以等待公司經營成果逐步反映。

**耐心的經濟價值，來自於不必在別人被迫交易的同一天做出相同交易。** 但這項優勢要先付出研究成本、估值錯誤的風險、機會成本，以及可能長時間落後市場的壓力。

能否從這種不對稱獲利，最後仍回到一個可以驗證的問題：**市場正在出售的是一段不受歡迎的時間，還是一家已經失去未來的公司？**

## 證據範圍

- Ackman 對指數化、Pod 與股價跳空的關係屬[訪談中的市場結構判斷](https://singjupost.com/transcript-of-bill-ackman-interview-holy-grail-of-investing-podcast/)，並非 IBM 個股賣方的逐筆交易歸因。訪談中提到 Vanguard、State Street、Northern Trust 合計持有約四分之一美國企業股權，未附統計口徑，本文不採用該比例作為已核實數據。
- [Gabaix 與 Koijen（2021）](https://www.nber.org/papers/w28967)支持資金流與價格彈性的研究框架；[Cboe（2025）](https://www.cboe.com/insights/posts/0-dt-es-decoded-positioning-trends-and-market-impact)與[Adams 等人（2025／2026）](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5641974)顯示 0DTE 對波動的方向依部位與樣本而異。這些研究都沒有直接估計 IBM 2026 年 7 月 14 日的機構交易構成。
- [IBM 7 月 14 日初步公告](https://newsroom.ibm.com/2026-07-14-Arvind-Krishnas-Letter-to-IBM-Investors)與[7 月 22 日正式財報](https://newsroom.ibm.com/2026-07-22-IBM-RELEASES-SECOND-QUARTER-RESULTS)提供企業基本面；[Reuters 7 月 14 日報導](https://www.investing.com/news/stock-market-news/ibm-expects-secondquarter-revenue-below-estimates-4790496)提供股價事件。$100／$75 與 $95／$60 全為假設算例，並非投資建議或個股目標價。

## 參考資料

1. [Bill Ackman, *The Holy Grail of Investing* podcast 訪談逐字稿（2026-09-08 首播，09-30 逐字稿刊出）](https://singjupost.com/transcript-of-bill-ackman-interview-holy-grail-of-investing-podcast/)
2. [IBM, *Arvind Krishna's Letter to IBM Investors*, 2026-07-14](https://newsroom.ibm.com/2026-07-14-Arvind-Krishnas-Letter-to-IBM-Investors)
3. [IBM, *Second-Quarter Results*, 2026-07-22](https://newsroom.ibm.com/2026-07-22-IBM-RELEASES-SECOND-QUARTER-RESULTS)
4. [Gabaix & Koijen, *In Search of the Origins of Financial Fluctuations*, NBER, 2021](https://www.nber.org/papers/w28967)
5. [Federal Reserve, *Financial Stability Report*, 2020 年 5 月](https://www.federalreserve.gov/publications/2020-may-financial-stability-report-asset-valuation.htm)
6. [Federal Reserve, *Sizing Hedge Funds' Treasury Market Activities*, 2021-10-06](https://www.federalreserve.gov/econres/notes/feds-notes/sizing-hedge-funds-treasury-market-activities-and-holdings-20211006.html)
7. [Cboe, *0DTEs Decoded*, 2025-05-02](https://www.cboe.com/insights/posts/0-dt-es-decoded-positioning-trends-and-market-impact)
8. [Adams et al., *Do S&P500 Options Increase Market Volatility?*, 2025／2026 修訂](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5641974)
