---
layout: post
title: "GPT-Synopsys 把專用模型、EDA 執行與企業治理綁成一項服務"
date: 2026-10-02 05:57:51 +0800
domain: ic-design-platform
categories: ic-design-platform
series: agentic-design-radar
permalink: /ic-design-platform/2026/10/02/gpt-synopsys-model-tool-governance-boundary.html
description: "OpenAI 與 Synopsys 將專用模型、EDA 工具、Autopilot 及客戶 agent harness 接成共同服務；模型能否進入正式流程，取決於版本化證據、恢復邊界與資料治理。"
---

OpenAI 與 Synopsys 在 2026 年 9 月 30 日宣布共同開發 GPT-Synopsys，讓專用模型直接操作 Synopsys EDA 工具，涵蓋 PPA optimization、timing closure 與 verification closure。這項合作把模型、工具執行、授權與企業治理放進同一項服務：GPT-Synopsys 預定運行於 OpenAI-hosted infrastructure，整合 Synopsys.ai 與 Autopilot，也要能接入客戶自己的 agent harness。[Synopsys／OpenAI 聯合公告](https://news.synopsys.com/2026-09-30-OpenAI-and-Synopsys-Announce-GPT-Synopsys-Frontier-Intelligence-to-Revolutionize-Chip-Design)

目前可確認的是多年合作協議、共同研發與 go-to-market，以及已有 early technology engagements。公告沒有提供 GA 日期、支援工具與版本清單、客戶 benchmark、可自主運作的最長工作範圍，或失敗後如何恢復。因此這是一個值得納入平台規劃的新架構方向，還不是已證實能自行完成 signoff 的量產能力。

<figure>
  <a href="/images/ic-design-platform/2026-10-02/gpt-synopsys-service-boundary.svg"><img src="/images/ic-design-platform/2026-10-02/gpt-synopsys-service-boundary.svg" alt="客戶的目標、政策與 agent harness 進入 GPT-Synopsys；專用模型透過 Autopilot 操作 EDA 工具，產生帶版本的設計產物與工具證據，再由工程師審查與放行。" width="900" height="660" loading="lazy"></a>
  <figcaption>圖一：依據 <a href="https://news.synopsys.com/2026-09-30-OpenAI-and-Synopsys-Announce-GPT-Synopsys-Frontier-Intelligence-to-Revolutionize-Chip-Design">共同公告</a>與 <a href="https://news.synopsys.com/2026-09-28-Synopsys-Powers-Autonomous-Engineering-with-a-Broad-Portfolio-of-Long-Horizon-Agents-and-Autopilot-Platform">Autopilot 官方說明</a>整理。版本 manifest、證據閘門與恢復路徑是作者提出的導入要求，不代表已公開的產品實作。</figcaption>
</figure>

## 專用模型改變的是工具操作層

今天稍早整理的 [Jalapeño／XLS 案例](/ic-design-platform/2026/10/02/jalapeno-llm-xls-eda-design.html) 顯示另一條路徑：通用模型提出候選修改，XLS compiler、驗證與標準 EDA flow 接手判定候選是否可用。GPT-Synopsys 的公開方向則是讓模型學會使用特定工具、解讀輸出並持續修改設計。兩者都把工具結果當回饋，但責任邊界不同。

專用模型有機會減少三種轉譯成本。第一，模型可以理解工具 command、report 與錯誤語意，不必每個團隊重新建立大量 prompt adapter。第二，Autopilot 提供 orchestration、skills、persistent memory、telemetry 與 governance，使長程工作不只是一串無狀態 API 呼叫。第三，工具供應商可以把合法的 action surface 與執行語意放進受控介面，而非讓模型任意產生 shell 或 Tcl。[Synopsys Autopilot 公告](https://news.synopsys.com/2026-09-28-Synopsys-Powers-Autonomous-Engineering-with-a-Broad-Portfolio-of-Long-Horizon-Agents-and-Autopilot-Platform)

這些能力仍不能把 EDA exit code 直接升格為交付證據。一次 timing run 成功，只表示指定版本的 netlist、SDC、library、corner、tool build 與 options 產生了一份結果。模型若在下一輪改動約束或設計，前一輪的 WNS、power 與 equivalence 結論可能全部失效。平台需要把每次決策綁到 immutable input digest、tool／model version、授權身分、action、output artifact 與 acceptance result；缺一項，就無法重建模型為何選擇這個候選。

## 客戶 harness 需要保有驗收主權

公告特別寫明 GPT-Synopsys 將與 customer agent harness interoperable。這表示客戶不必把既有 flow owner、artifact store、policy engine 與放行流程全部交給單一 vendor platform。較穩健的切法，是由 GPT-Synopsys 提供受控的工具操作與領域推理，客戶 harness 保留三項權力：

1. **目標與禁止變更範圍**：哪些 RTL、SDC、UPF 或 waiver 可讀、可改或只能提出建議。
2. **證據閘門**：simulation、formal、LEC、STA、DRC、LVS 需要哪些固定條件，何種結果才能晉級。
3. **發布與回復**：哪個 checkpoint 可以交付下一階段，誰能撤銷、回退或重新驗證。

這個邊界也決定跨供應商整合是否成立。若每個 agent 只回傳自然語言摘要，客戶 harness 無法判斷另一個工具讀到的是哪一版 artifact。介面至少要輸出 machine-readable run identity、input／output digests、evidence type、validity scope 與 failure status。模型可以解釋結果，工具產物與驗收紀錄才是後續自動化可依賴的契約。

## 長程執行的失敗會留下工程狀態

假設 agent 為修正 setup violation，先調整 synthesis options，再啟動 APR 與 STA。APR 在 license server 暫時失聯後 timeout；agent 重試時讀到舊 checkpoint，卻把新一輪 STA report 登記成目前候選。使用者看到 WNS 改善，但 report、netlist 與寄生參數並不屬於同一個 run。

恢復不能只重送最後一個 command。平台要先判斷先前 job 是否仍在執行、scratch 與 license 是否殘留、checkpoint 是否完整，再以 idempotency key 對應 workflow step；任何 input digest 改變，都應使 downstream evidence 失效。若無法證明狀態一致，安全結果是隔離該候選並從最近的 verified checkpoint 重跑，而不是沿用看似成功的局部報告。

Synopsys 公告稱客戶資料不會用於模型訓練，並提供傳輸與靜態加密，以及 retention、audit、permission controls。這回答部分企業採用門檻，但尚未公開資料駐留、不同客戶隔離、export-control policy、模型更新對重現性的影響，以及跨 customer harness 的 audit schema。[GPT-Synopsys 資料治理說明](https://news.synopsys.com/2026-09-30-OpenAI-and-Synopsys-Announce-GPT-Synopsys-Frontier-Intelligence-to-Revolutionize-Chip-Design)

## 平台團隊現在能驗證什麼

第一個 PoC 不宜直接要求 autonomous RTL-to-GDS。選一個可回復、證據明確的閉環，例如固定 RTL／SDC 與 tool build 下的 constraint diagnosis 或 regression triage；同時保留人工／script baseline。每次實驗量測 accepted outcomes、engineer review time、tool-hours、license wait、token／compute cost、重試次數與 evidence mismatch，而非只看 agent 完成了多少步。

如果 GPT-Synopsys 能在相同驗收條件下提高 accepted outcome rate，並讓失敗可重播、可隔離、可回復，專用模型才真的降低平台整合成本。若只能增加探索次數，卻無法說明 artifact lineage 與證據有效範圍，更多自動化反而會放大工具費用與錯誤交付風險。

## References

- [OpenAI and Synopsys Announce GPT-Synopsys，2026-09-30](https://news.synopsys.com/2026-09-30-OpenAI-and-Synopsys-Announce-GPT-Synopsys-Frontier-Intelligence-to-Revolutionize-Chip-Design)
- [Synopsys AgentEngineer and Autopilot Platform，2026-09-28](https://news.synopsys.com/2026-09-28-Synopsys-Powers-Autonomous-Engineering-with-a-Broad-Portfolio-of-Long-Horizon-Agents-and-Autopilot-Platform)

