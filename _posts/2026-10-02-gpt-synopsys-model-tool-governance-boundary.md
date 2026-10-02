---
layout: post
title: "GPT-Synopsys 讓模型直接操作 EDA 工具，平台團隊最先省下的是工具轉譯成本"
date: 2026-10-02 05:57:51 +0800
domain: ic-design-platform
categories: ic-design-platform
series: agentic-design-radar
permalink: /ic-design-platform/2026/10/02/gpt-synopsys-model-tool-governance-boundary.html
description: "OpenAI 與 Synopsys 把專用模型接上 Synopsys 工具與 Autopilot。第一年最可能省下的是各團隊自建 prompt adapter 與報告解讀的人力；時程與 PPA 收益要等同條件 benchmark。"
summary:
  - "GPT-Synopsys 讓專用模型直接操作 Synopsys EDA 工具，預定跑在 OpenAI 的基礎設施上"
  - "第一年最可能省下的是各團隊自建工具轉譯的人力，例如 prompt adapter 與報告解讀"
  - "時程與 PPA 收益目前沒有公開數據，GA 日期與支援工具清單也還沒公布"
  - "客戶保留目標、晉級條件與放行權，才能接進現有 flow 而不被單一廠商綁住"
  - "第一個 PoC 適合選固定條件下的約束診斷或 regression triage，並保留人工 baseline"
---

OpenAI 與 Synopsys 在 2026 年 9 月 30 日宣布共同開發 GPT-Synopsys：專用模型直接操作 Synopsys EDA 工具，目標涵蓋 PPA optimization、timing closure 與 verification closure。服務預定運行於 OpenAI-hosted infrastructure，整合 Synopsys.ai 與 Autopilot，並可接入客戶自己的 agent harness。[Synopsys／OpenAI 聯合公告](https://news.synopsys.com/2026-09-30-OpenAI-and-Synopsys-Announce-GPT-Synopsys-Frontier-Intelligence-to-Revolutionize-Chip-Design)

對 IC 設計平台團隊來說，這項合作第一年最可能帶來的收益是降低工具轉譯成本：各團隊今天自己維護的 prompt adapter、Tcl 產生規則與報告解讀，會有一部分改由工具供應商提供。縮短 tapeout 時程或改善 PPA 則要等同條件的 benchmark。雙方目前公布的是多年合作協議、共同研發與 go-to-market，以及已有 early technology engagements。

<figure>
  <a href="/images/ic-design-platform/2026-10-02/gpt-synopsys-service-boundary.svg"><img src="/images/ic-design-platform/2026-10-02/gpt-synopsys-service-boundary.svg" alt="客戶的目標、政策與 agent harness 進入 GPT-Synopsys；專用模型透過 Autopilot 操作 EDA 工具，產生帶版本的設計產物與工具報告，再由工程師審查與放行。" width="900" height="660" loading="lazy"></a>
  <figcaption>圖一：依據 <a href="https://news.synopsys.com/2026-09-30-OpenAI-and-Synopsys-Announce-GPT-Synopsys-Frontier-Intelligence-to-Revolutionize-Chip-Design">共同公告</a>與 <a href="https://news.synopsys.com/2026-09-28-Synopsys-Powers-Autonomous-Engineering-with-a-Broad-Portfolio-of-Long-Horizon-Agents-and-Autopilot-Platform">Autopilot 官方說明</a>整理。圖中的版本化設計狀態、Evidence gate 與失敗處理路徑屬參考設計，尚非已公開的產品實作。</figcaption>
</figure>

## 專用模型省下哪三種轉譯

今天稍早整理的 [Jalapeño／XLS 案例](/ic-design-platform/2026/10/02/jalapeno-llm-xls-eda-design.html) 走的是另一條路：通用模型提出候選修改，XLS compiler、驗證與標準 EDA flow 判定候選能否採用。GPT-Synopsys 則讓模型學會使用特定工具、解讀輸出並連續修改設計。前者把領域知識放在編譯器與 flow，後者放進模型與工具介面。

| 路線 | 領域知識放在哪 | 平台團隊要維護 | 主要風險 |
| --- | --- | --- | --- |
| 通用模型＋編譯器／EDA 判定（Jalapeño） | XLS compiler、驗證與 EDA flow | 候選格式、判定流程 | 候選淘汰率決定 tool-hours |
| 專用模型直接操作工具（GPT-Synopsys） | 模型與廠商提供的 action surface | 目標、晉級條件、artifact 版本 | 工具與模型綁同一廠商，換供應商成本高 |

專用模型有機會省下三種轉譯成本。

第一是指令與語意。模型理解工具 command、report 與錯誤訊息，各團隊不必再為每套工具維護 prompt adapter 與報告解析，也不必在每次工具改版時跟著調整。

第二是長程狀態。Autopilot 提供 orchestration、skills、persistent memory、telemetry 與 governance，長程工作因此是有狀態的工作流程，而非一串互不相關的 API 呼叫。[Synopsys Autopilot 公告](https://news.synopsys.com/2026-09-28-Synopsys-Powers-Autonomous-Engineering-with-a-Broad-Portfolio-of-Long-Horizon-Agents-and-Autopilot-Platform)

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

第一個 PoC 適合選可回退、結果明確的閉環，例如固定 RTL、SDC 與 tool build 下的 constraint diagnosis 或 regression triage，同時保留人工或 script baseline。每次實驗量測 accepted outcomes、工程師審查時間、tool-hours、license 等待、token／compute 成本、重試次數與結果不一致次數，比較的是同條件下的產出，而非 agent 完成了多少步。

本文的判斷是：GPT-Synopsys 第一年對平台團隊的主要價值在工具轉譯人力，tapeout 時程的改善要更晚才會出現。若早期客戶公布在固定 RTL、SDC 與工具版本下，timing closure 迭代次數或工程師審查時間明顯下降，這個判斷就要往前修正；若公開資料只有探索次數增加、沒有 artifact lineage，更多自動化會先放大工具費用與錯誤交付風險。

## 證據範圍

- 公告沒有提供 GA 日期、支援工具與版本清單、客戶 benchmark、可自主運作的最長工作範圍，也沒有說明失敗後如何恢復。文中對時程與 PPA 的判斷是推論，不是已公布的結果。
- 資料治理尚未公開資料駐留、跨客戶隔離、export-control policy、模型更新對重現性的影響，以及跨 customer harness 的 audit schema。
- 圖一的版本化設計狀態、Evidence gate 與失敗處理路徑是參考設計，用來說明客戶端需要保留的控制點。

## References

- [OpenAI and Synopsys Announce GPT-Synopsys，2026-09-30](https://news.synopsys.com/2026-09-30-OpenAI-and-Synopsys-Announce-GPT-Synopsys-Frontier-Intelligence-to-Revolutionize-Chip-Design)
- [Synopsys AgentEngineer and Autopilot Platform，2026-09-28](https://news.synopsys.com/2026-09-28-Synopsys-Powers-Autonomous-Engineering-with-a-Broad-Portfolio-of-Long-Horizon-Agents-and-Autopilot-Platform)
