---
layout: post
title: "GPT-Synopsys 把 EDA 授權、模型與算力打包販售，Synopsys 把 AI agent 變成續約籌碼"
date: 2026-10-02 05:57:51 +0800
domain: ic-design-platform
categories: ic-design-platform
series: agentic-design-radar
permalink: /ic-design-platform/2026/10/02/gpt-synopsys-model-tool-governance-boundary.html
description: "OpenAI 取得 Synopsys 工具授權開發專用模型，雙方分潤，並把算力、模型與授權打包銷售。晶片公司省下工具轉譯人力，換來對兩家供應商的同時依賴。"
lede: "OpenAI 取得 Synopsys 的 EDA 工具授權來開發專用模型，雙方分潤，再把算力、模型與授權包成一項服務賣給晶片公司。最懂 EDA 的 agent 從此以 Synopsys 工具為母語，晶片公司日後想改用 Cadence，得連 agent 流程一起搬；OpenAI 則借 Synopsys 的業務敲開半導體客戶。沒有 CAD 平台團隊的中型設計公司最快用得上，大型公司省下的主要是整合人力，卻要把設計資料送進 OpenAI 的雲。公告沒有寫排他條款，若 OpenAI 轉頭與 Cadence 簽約，主導權就會換手。"
---

OpenAI 與 Synopsys 在 2026 年 9 月 30 日宣布共同開發 GPT-Synopsys：專用模型直接操作 Synopsys EDA 工具，目標涵蓋 PPA optimization、timing closure 與 verification closure。OpenAI 取得 Synopsys EDA 工具授權，用來開發這個模型；雙方簽訂多年合作，包含分潤與共同 go-to-market，對客戶提供「算力、模型與授權」打包的聯合服務。服務預定運行於 OpenAI-hosted infrastructure，整合 Synopsys.ai 與 Autopilot，並可接入客戶自己的 agent harness。[Synopsys／OpenAI 聯合公告](https://news.synopsys.com/2026-09-30-OpenAI-and-Synopsys-Announce-GPT-Synopsys-Frontier-Intelligence-to-Revolutionize-Chip-Design)

這筆交易讓 Synopsys 把「最懂 EDA 的模型」做成以自家工具為母語，並把模型收入接進自己的授權生意。對 IC 設計平台團隊來說，第一年最可能看到的是工具轉譯成本下降：各團隊自己維護的 prompt adapter、Tcl 產生規則與報告解讀，會有一部分改由供應商提供。縮短 tapeout 時程或改善 PPA，要等同條件的 benchmark。目前公布的是合作架構與 early technology engagements，沒有客戶名單與量化結果。

<figure>
  <a href="/images/ic-design-platform/2026-10-02/gpt-synopsys-service-boundary.svg"><img src="/images/ic-design-platform/2026-10-02/gpt-synopsys-service-boundary.svg" alt="客戶的目標、政策與 agent harness 進入 GPT-Synopsys；專用模型透過 Autopilot 操作 EDA 工具，產生帶版本的設計產物與工具報告，再由工程師審查與放行。" width="900" height="660" loading="lazy"></a>
  <figcaption>圖一：依據 <a href="https://news.synopsys.com/2026-09-30-OpenAI-and-Synopsys-Announce-GPT-Synopsys-Frontier-Intelligence-to-Revolutionize-Chip-Design">共同公告</a>與 <a href="https://news.synopsys.com/2026-09-28-Synopsys-Powers-Autonomous-Engineering-with-a-Broad-Portfolio-of-Long-Horizon-Agents-and-Autopilot-Platform">Autopilot 官方說明</a>整理。圖中的版本化設計狀態、Evidence gate 與失敗處理路徑屬參考設計，尚非已公開的產品實作。</figcaption>
</figure>

## 專用模型省下哪三種轉譯

今天稍早整理的 [Jalapeño／XLS 案例](/ic-design-platform/2026/10/02/jalapeno-llm-xls-eda-design.html) 走的是另一條路：通用模型提出候選修改，XLS compiler、驗證與標準 EDA flow 判定候選能否採用。GPT-Synopsys 則讓模型學會使用特定工具、解讀輸出並連續修改設計。前者把領域知識放在編譯器與 flow，後者放進模型與工具介面。

| 路線 | 領域知識放在哪 | 平台團隊要維護 | 主要風險 |
| --- | --- | --- | --- |
| 通用模型＋編譯器／EDA 判定（Jalapeño） | XLS compiler、驗證與 EDA flow | 候選格式、判定流程 | 候選淘汰率決定 tool-hours |
| 專用模型直接操作工具（GPT-Synopsys） | 模型與廠商提供的 action surface | 目標、晉級條件、artifact 版本 | 工具與模型綁同一組供應商，換廠成本高 |

專用模型有機會省下三種轉譯成本。

第一是指令與語意。模型理解工具 command、report 與錯誤訊息，各團隊不必再為每套工具維護 prompt adapter 與報告解析，也不必在每次工具改版時跟著調整。

第二是長程狀態。Autopilot 提供 orchestration、skills、persistent memory、telemetry 與 governance，長程工作因此是有狀態的工作流程，各步驟之間保留上下文。[Synopsys Autopilot 公告](https://news.synopsys.com/2026-09-28-Synopsys-Powers-Autonomous-Engineering-with-a-Broad-Portfolio-of-Long-Horizon-Agents-and-Autopilot-Platform)

第三是合法動作。工具供應商可以把允許的操作與執行語意放進受控介面，模型呼叫的是定義好的動作，避免任意產生 shell 或 Tcl。

這三項節省的都是平台團隊的整合人力。設計品質仍由 timing、power 與 equivalence 的結果決定，而這些結果只對特定版本的 netlist、SDC、library、corner、tool build 與 options 成立。模型在下一輪改動約束或設計，前一輪的 WNS 與 power 結論就要重算。因此平台仍要把每次決策綁到 input digest、tool／model 版本、授權身分、動作、輸出 artifact 與判定結果，才能重建模型選擇某個候選的理由。

## 客戶 harness 要保留三項決定權

公告寫明 GPT-Synopsys 可與 customer agent harness 互通。客戶因此可以保留既有 flow owner、artifact store、policy engine 與放行流程。較穩健的切法，是由 GPT-Synopsys 負責工具操作與領域推理，客戶 harness 保留三項決定權：

1. **目標與可改範圍**：哪些 RTL、SDC、UPF 或 waiver 可讀、可改，或只能提出建議。
2. **晉級條件**：simulation、formal、LEC、STA、DRC、LVS 各需要哪些固定條件，什麼結果才進入下一階段。
3. **發布與回退**：哪個 checkpoint 可以交付下一階段，誰能撤銷、回退或要求重跑。

跨供應商整合靠的是機器可讀的執行紀錄。每個 agent 至少要輸出 run identity、input／output digests、結果類型、有效範圍與失敗狀態；只回傳自然語言摘要，另一個工具就無從判斷讀到的是哪一版 artifact。模型負責解釋結果，工具產物與晉級紀錄才是後續自動化的依據。

## 長程執行出錯時，留下的是工程狀態

假設 agent 為修正 setup violation，先調整 synthesis options，再啟動 APR 與 STA。APR 在 license server 暫時失聯後 timeout；agent 重試時讀到舊 checkpoint，卻把新一輪 STA report 登記成目前候選。使用者看到 WNS 改善，但 report、netlist 與寄生參數分屬不同 run。

處理方式是先確認狀態，再決定重跑範圍。平台要判斷先前 job 是否仍在執行、scratch 與 license 是否殘留、checkpoint 是否完整，再以 idempotency key 對應 workflow step。任何 input digest 改變，下游結果一律作廢。狀態無法確認時，隔離該候選並從最近一個已驗證的 checkpoint 重跑。

資料治理方面，Synopsys 表示客戶資料不用於模型訓練，提供傳輸與靜態加密，以及 retention、audit 與 permission controls。這回答了企業採用的第一道門檻。[GPT-Synopsys 資料治理說明](https://news.synopsys.com/2026-09-30-OpenAI-and-Synopsys-Announce-GPT-Synopsys-Frontier-Intelligence-to-Revolutionize-Chip-Design)

## 第一個 PoC 選什麼、量什麼

第一個 PoC 適合選可回退、結果明確的閉環，例如固定 RTL、SDC 與 tool build 下的 constraint diagnosis 或 regression triage，同時保留人工或 script baseline。每次實驗量測 accepted outcomes、工程師審查時間、tool-hours、license 等待、token／compute 成本、重試次數與結果不一致次數。比較基準是同條件下被採用的產出，agent 執行了多少步只是過程指標。

## 授權、分潤與打包，讓 Synopsys 從模型用量抽成

Synopsys 從這筆交易拿到三樣東西。模型用 Synopsys 工具開發，工具的指令、報告與錯誤語意變成模型能力，晶片公司日後要比較 Cadence，比的是整套 agent 流程。打包銷售把採購從「買工具 seat」擴大成「買算力、模型與授權」，Synopsys 在同一家客戶身上的收入面變大，分潤再讓它從模型用量抽成。最後是防守：通用 agent 普及之後，EDA 工具有被當成可互換後端的風險，Synopsys 先把 agent 綁在自家工具上，把這個風險轉成護城河。

OpenAI 拿到的是另一種資產。EDA 工具產出的 timing、LEC、DRC 結果可以自動判定對錯，這種場景很適合用來改進模型；OpenAI 透過授權取得它，再經由 Synopsys 的業務接觸全球晶片公司，以分潤取得營收。OpenAI 也在與 Broadcom 開發自家晶片（見 [Jalapeño 一文](/ic-design-platform/2026/10/02/jalapeno-llm-xls-eda-design.html)），自己就是這套工具的潛在大客戶。

帳單則落在晶片公司身上：打包服務涵蓋算力、模型與授權，價格尚未公布，收入由 Synopsys 與 OpenAI 依分潤分配。拿到好處的兩家廠商和付錢的晶片公司分屬兩邊，導入前要先把這筆帳算清楚。

## 中型設計公司先用上，大型公司要多算資料與依賴的帳

沒有 CAD 平台團隊的中型設計公司，原本沒有人力自建 agent、工具轉譯層與長程執行管理，買打包服務就能取得接近大公司的自動化，收益最直接。大型設計公司已有平台團隊，省下的主要是轉譯人力，邊際收益小得多，要付出的卻一樣。

那筆代價有四個部分。工具綁 Synopsys，模型與算力綁 OpenAI，任一方調價或改版都會直接傳到設計流程。服務跑在 OpenAI 的基礎設施上，公告沒有提到 VPC 或地端選項；同樣在開發 AI 加速器的公司，等於把設計資料送進一個也在做晶片的對手的雲，受出口管制限制的客戶也會卡在同一關。模型版本更新會改變 agent 的決策，同一個設計兩次執行的結果可能不同。按用量計費則讓 EDA 支出從固定授權變成浮動支出，探索越多、帳單越高。

## 膠水層搬進供應商的產品之後

過去，把 EDA 工具接成自動化流程的那層膠水程式碼，握在晶片公司自己的 CAD 團隊手上；要換供應商，重寫膠水層就好。打包服務把這一層搬進供應商的產品裡，轉換成本跟著上升。續約時，Synopsys 可以把工具、模型與算力一起報價，客戶很難拆開比價。前面提到客戶 harness 要保留的三項決定權，正是晶片公司守住談判位置的最後一道防線。

被壓縮的工作有三類：晶片公司內部的 prompt adapter 與報告解析；以 LLM 包裝原廠 EDA 工具為主要賣點的 AI-EDA 新創，因為原廠同時握有工具介面與授權；以及初階工程師看守 run、整理報告的部分日常。

## FlexEDA 與 Copilot 留下的線索

打包算力與授權並不新。2022 年起，Synopsys Cloud 的 FlexEDA 就提供託管算力加按分鐘計費的授權。[Synopsys：What is FlexEDA](https://www.synopsys.com/blogs/chip-design/what-is-flexeda.html) 這次多出來的是模型，以及資料改流向 OpenAI 的基礎設施；大型設計公司過去對託管 EDA 的接受程度，大致就是 GPT-Synopsys 的天花板。

GitHub Copilot 提供了另一條線索。它起初只用 OpenAI 的模型，2024 年 10 月 29 日加入 Anthropic 的 Claude 3.5 Sonnet 與 Google 的 Gemini 1.5 Pro。[GitHub Blog](https://github.blog/news-insights/product-news/bringing-developer-choice-to-copilot/) 掌握使用介面與通路的一方，最後把模型變成可替換的零件。GPT-Synopsys 的公告同樣沒有排他條款。

照這兩條線索往下推，2027 年底前，Cadence 或 Siemens EDA 很可能宣布與前沿模型公司的同等級合作，或推出與自家授權打包的自研模型。GA 前後，Synopsys 也大概需要補上客戶雲或地端部署；如果首批具名客戶以中型公司為主、看不到大型 AI 晶片開發商，就表示資料流向確實是採用的瓶頸。

## 如果 OpenAI 也找上 Cadence

另一種走向是主導權最後落到 OpenAI。OpenAI 握有模型、算力，以及 agent 這個直接面對工程師的介面，又透過授權學會 EDA 工具的用法；公告沒有排他條款，一旦模型的 EDA 能力可以遷移到其他廠商的工具，OpenAI 大可再與 Cadence 合作，Synopsys 就從平台退成後端之一。客戶 harness 可互通、客戶資料不用於訓練，也讓晶片公司保有替換模型的空間。

這個走向要成真，需要 OpenAI 與其他 EDA 廠商簽下類似協議，或模型在不同廠商工具之間的表現差距很小。在那之前，主導權仍在 Synopsys：agent 執行任何操作都需要 Synopsys 的授權，工具的內部語意與產品路線圖在它手上，晶圓廠認證的 signoff 流程短期內也難以替換，分潤還讓它隨模型用量收費。OpenAI 與 Cadence 的合作公告一旦出現，這個排序就要倒過來。

## 證據範圍

- 公告沒有提供 GA 日期、支援工具與版本清單、價格、客戶名單、benchmark、可自主運作的最長工作範圍，也沒有說明失敗後如何恢復。文中對時程、PPA 與主導權歸屬的判斷是推論。
- 公告寫明 OpenAI 取得授權「用於開發專用模型」，沒有說明是否以工具結果作為訓練訊號；「適合用來改進模型」是推論。
- OpenAI 與 Broadcom 開發晶片的資訊來自前文引用的訪談；OpenAI 是否會使用 GPT-Synopsys，公告沒有提及。
- 公告沒有寫明是否排他，也沒有提到 VPC 或地端部署；對 2027 年與 GA 前後的推估都以此為前提。
- 資料治理尚未公開資料駐留、跨客戶隔離、export-control policy、模型更新對重現性的影響，以及跨 customer harness 的 audit schema。
- 圖一的版本化設計狀態、Evidence gate 與失敗處理路徑是參考設計，用來說明客戶端需要保留的控制點。

## References

- [OpenAI and Synopsys Announce GPT-Synopsys，2026-09-30](https://news.synopsys.com/2026-09-30-OpenAI-and-Synopsys-Announce-GPT-Synopsys-Frontier-Intelligence-to-Revolutionize-Chip-Design)
- [Synopsys AgentEngineer and Autopilot Platform，2026-09-28](https://news.synopsys.com/2026-09-28-Synopsys-Powers-Autonomous-Engineering-with-a-Broad-Portfolio-of-Long-Horizon-Agents-and-Autopilot-Platform)
- [Synopsys：What is FlexEDA](https://www.synopsys.com/blogs/chip-design/what-is-flexeda.html)
- [GitHub：Bringing developer choice to Copilot，2024-10-29](https://github.blog/news-insights/product-news/bringing-developer-choice-to-copilot/)
