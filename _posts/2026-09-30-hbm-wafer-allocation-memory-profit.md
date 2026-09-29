---
layout: post
title: "HBM 吃掉三成 DRAM 晶圓，記憶體利潤開始按每片晶圓重新分配"
date: 2026-09-30 07:19:40 +0800
domain: ai-industry
categories: ai-industry
description: "HBM 的產能占比上升，會同時擠壓一般型 DRAM，卻不保證每片 HBM 晶圓更賺錢。下一輪記憶體獲利要看規格、良率、合約價與資本支出能否一起改善。"
---

HBM 正把記憶體產業從「賣出多少 bit」改造成「有限晶圓該交給哪一種產品」。三星主管在 9 月 29 日表示，HBM 明年可能占全球 DRAM 晶圓產能近 30%，高於目前約 20%。這十個百分點會同時作用在兩邊：HBM 與一般型 DRAM 共用前段產能，同樣容量的 HBM 又需要更多晶圓，所以 AI 的需求會推高 HBM 用量，也會壓縮 DDR5 等產品的供給。

我比較在意的是這個配置決策如何改變獲利。當 HBM 合約價追不上 DDR5、先進封裝良率還在爬坡，原廠增加 HBM 並不一定能提高每片晶圓的利潤；當供應吃緊迫使客戶縮減每顆加速器的記憶體容量，需求仍然很強，也不代表原定規格可以照單全收。HBM4 良率、base die、堆疊封裝與合約重議，會比產能宣告更早決定這批投資能不能留下獲利。

## 三成晶圓只換到一成多的 bit

[三星主管的說法](https://www.reuters.com/world/asia-pacific/samsung-electronics-says-hbm-account-nearly-30-industry-dram-capacity-next-year-2026-09-29/)是 HBM 明年占 DRAM 晶圓產能近 30%。TrendForce 今年 6 月的推估更能說明物理成本：2027 年前三大供應商約 30% 的 DRAM wafer input，對應的 HBM bit supply 只有約 13%。HBM die 較大，還要經過 TSV、薄化、堆疊與封裝；[SK hynix 6 月 29 日的說明](https://news.skhynix.com/en/fact-05/)也明確指出，同樣記憶體容量下，HBM 能從一片晶圓取得的可用 die 較少。

這組比例不適合直接拿來算營收，卻揭露了供給彈性的方向。HBM 投片占比從 20% 升到 30%，相對增幅是 50%，有效 HBM bit 卻不會同步增加 50%；良率、堆疊層數與封裝產能都會形成第二道限制。一般型 DRAM 也因此得到間接受益：原廠把先進製程移給 HBM，server DDR5、PC 與手機記憶體能分到的產能就變少。

但「被排擠」不等於所有 DRAM 都有同樣定價權。三星在 7 月 31 日公布第二季結果時，確認伺服器產品營收占比創高、HBM4 銷售擴大，並預期下半年 HBM、server DRAM 與企業級 SSD 需求加速；同一份資料也說行動裝置與 PC 需求趨緩。[三星第二季營運績效](https://news.samsung.com/tw/%E4%B8%89%E6%98%9F%E9%9B%BB%E5%AD%90%E5%85%AC%E5%B8%832026%E5%B9%B4%E7%AC%AC%E4%BA%8C%E5%AD%A3%E7%87%9F%E9%81%8B%E7%B8%BE%E6%95%88)支持的是產品組合向伺服器移動，不足以證明低階消費性 DRAM 可以無限漲價。

## 客戶開始用規格換取供應

供應吃緊已經影響加速器設計。[TrendForce 9 月 29 日的研究](https://www.trendforce.com/presscenter/news/20260929-13255.html)指出，部分 GPU 與 ASIC 業者正在評估以 8-Hi 取代原先的 12-Hi HBM。每個 stack 的容量下降，可以讓相同 HBM bit 供應支撐更多加速器，也降低單顆晶片的材料成本；代價是 base die 成本分攤到更少容量，TrendForce 預估 2027 年 8-Hi 每 Gb 價格反而可能比 12-Hi 高 10% 至 20%。

這代表 HBM 需求不能只看「每顆 GPU 配多少 GB」。若客戶從 12-Hi 改為 8-Hi，單顆容量可能下降，stack 數、base die 與封裝步驟未必同比例減少。對供應商而言，規格變更可以緩解單機成本，也可能讓系統廠把昂貴記憶體用得更精準；對軟體與模型服務商而言，較小的 memory capacity 則可能提高跨卡通訊、KV cache 分層或模型切分的成本。最後誰承擔這筆效率損失，還要回到整機效能與每 token 成本。

## HBM 漲價是在修復每片晶圓的報酬

HBM 的售價高，不代表先前合約一直比 DDR5 好賺。TrendForce 6 月 2 日曾估算，受年度合約定價與一般型 DRAM 上漲影響，2026 年第一季 HBM 的每片晶圓營收與獲利已低於 64GB DDR5 RDIMM。到了 9 月 29 日，TrendForce 把 2027 年 HBM blended ASP 年增預估上修至 121%，理由包括供應受限、HBM4 占比提高及 HBM4E 下半年爬坡。這是第三方預測，不是已簽合約；但它說明原廠為何需要大幅重議價格，才能讓有限晶圓繼續流向 HBM。

公司層級需要拿合格產出和現金檢查產能宣告。Micron 在 6 月 24 日確認 HBM4 已對首位客戶大量出貨，並送樣給多家終端客戶；同季淨資本支出約 71 億美元、調整後自由現金流約 183 億美元。[Micron 第三季資料](https://investors.micron.com/news/press-release/2026/Micron-Technology-Inc--Reports-Record-Results-for-the-Third-Quarter-of-Fiscal-2026/default.aspx)至少證明當時擴產沒有吃掉全部現金，但即將公布的第四季結果仍要重新檢查 ASP、毛利、CapEx 與 HBM 客戶數。三星則同時握有 DRAM、4 奈米 base die 與封裝能力，整合範圍較廣；能否轉成更高報酬，仍取決於客戶認證與良率。

我的判斷是，記憶體景氣已由單一產品短缺，進入跨產品爭奪同一片晶圓的階段。直接受益者會是能把 HBM4 合格率、base die 與封裝交付一起拉高，並在重議合約後保住每片晶圓利潤的供應商；一般型 DRAM 則透過排擠效應取得第二層價格支撐。這個方向值得研究，不等於三星、SK hynix 或 Micron 在目前價格就便宜；我手上沒有一致的即時估值與共識修正資料，不會把供給吃緊直接翻成買進結論。

最強的反證有三個：8-Hi 普及使單顆加速器 HBM 容量下降，HBM4 良率與新廠爬坡快於預期，以及 PC、手機需求弱到足以抵銷產能排擠。接下來兩季，我會把 HBM wafer input 與 bit share 放在一起看，再核對 8-Hi／12-Hi mix、一般型 DRAM 合約價，以及三家原廠的 CapEx 與自由現金流。只看到晶圓占比上升，還不能證明每股價值跟著上升。

## 來源

- [Reuters：Samsung Electronics says HBM to account for nearly 30% of industry DRAM capacity next year，2026-09-29](https://www.reuters.com/world/asia-pacific/samsung-electronics-says-hbm-account-nearly-30-industry-dram-capacity-next-year-2026-09-29/)
- [TrendForce：HBM Supply Constraints Persist，2026-09-29](https://www.trendforce.com/presscenter/news/20260929-13255.html)
- [TrendForce：Tight DRAM Supply Gives Suppliers Greater Pricing Power in HBM，2026-06-02](https://www.trendforce.com/presscenter/news/20260602-13074.html)
- [SK hynix：Mid-to-Long-Term Investment Strategy，2026-06-29](https://news.skhynix.com/en/fact-05/)
- [Samsung Electronics：2026 年第二季營運績效，2026-07-31](https://news.samsung.com/tw/%E4%B8%89%E6%98%9F%E9%9B%BB%E5%AD%90%E5%85%AC%E5%B8%832026%E5%B9%B4%E7%AC%AC%E4%BA%8C%E5%AD%A3%E7%87%9F%E9%81%8B%E7%B8%BE%E6%95%88)
- [Micron：Fiscal 2026 Third Quarter Results，2026-06-24](https://investors.micron.com/news/press-release/2026/Micron-Technology-Inc--Reports-Record-Results-for-the-Third-Quarter-of-Fiscal-2026/default.aspx)
