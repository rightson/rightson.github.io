# 七類文章與十四個研究系列

2026-10-01 使用者核准。五個排程器是執行入口；十四個系列保留各自進度；七個 `domain` 是公開選單。三者不可混用。

## 分類以文章主要回答的問題為準

| domain | 選單分類 | 主要問題 | 預設系列 |
| --- | --- | --- | --- |
| ic-design-platform | IC 設計平台 | 晶片如何設計、驗證、交接與治理？ | sota-r2g-cad、agentic-design-radar、agentic-design-deep-dive |
| ai-frontier | AI 技術與工程 | 模型與通用 Agent 如何運作、評估與實作？ | ai-frontier-digest、ai-weekly-share、llm-lab |
| architecture | 運算架構 | 運算硬體如何安排計算、資料搬移與記憶體？ | tpu-technical |
| networking | 網路系統 | 資料如何跨節點傳送，如何控制壅塞與恢復？ | networking-deep-dive |
| distributed-systems | 分散式系統 | 服務、作業系統與叢集如何管理狀態、資源及可靠性？ | distributed-systems、k8s-hpc |
| ai-industry | 產業與供應鏈 | 企業如何成長、競爭、獲利，供需與價值如何分配？ | mtk-ecosystem-deep-dive |
| investing | 投資與交易 | 股價反映多少預期，何時布局、減碼或退出？ | mtk-ecosystem-institutional、mtk-ecosystem-intraday、mtk-ecosystem-market-journal |

完整系列名稱與預設分類見 `_data/research_series.yml`；選單名稱、順序與說明見 `_data/domains.yml`。以上預設不能代替逐篇閱讀與判斷。

## 邊界與標籤

- 每篇只有一個主要 `domain`；`series`、公司與技術名稱是次級資料，不增加主選單。既有系列 identifier、篇號、roadmap 與完成歷史保持穩定；缺少 `series` 時只在既有 roadmap／文章提供足夠接續證據時補上，不硬把所有歷史稿塞進新版系列。
- EDA 演算法、STA／SDC、placement、routing、verification、signoff 與 R2G 平台均歸 `ic-design-platform`；`eda`、`timing` 是舊分類相容值，不再建立獨立公開分類。
- 通用模型與 Agent 機制歸 `ai-frontier`；主問題在 RTL、驗證、synthesis／APR、signoff 的導入、流程或驗收責任，歸 `ic-design-platform`。
- LLM Lab 主問題為模型、數學與軟體實作時歸 `ai-frontier`；獨立加速器資料流或微架構歸 `architecture`。依主要問題亦可歸網路、系統或 IC 平台；系列 identifier 不變。
- 解釋企業如何成長、競爭及獲利歸 `ai-industry`；判斷股價已反映的預期、合理估值、資金動向或進退場條件歸 `investing`。出現營收、EPS、毛利或現金流數字，不足以將文章判成投資文。
- 半導體生態系深研預設 `ai-industry`；主問題為合理股價、估值情境或布局條件時歸 `investing`。晨報預設 `investing`，若公開稿獨立回答經營或供需問題，亦依主問題分類。
- TPU 微架構歸 `architecture`；其供需、競爭或估值研究依上述邊界分流。互連協定與封包路徑歸 `networking`；服務一致性、Linux、容器、K8s／HPC 資源管理歸 `distributed-systems`，不因應用於 AI／EDA 而改分類。

## 既有與未來文章

- 既有文章重新分類只改 `domain`，保留 filename、date、categories、permalink、正文、原始系列與篇號；不靠改 categories 移動網址。已封存文章保持封存。
- 新文章使用單一 `categories`，與所選 `domain` 相同；`series` 使用穩定 identifier，可跨 domain，不隨題目更名。
- 寫作前讀最新 `AGENTS.md`、本檔及對應 roadmap；分類變更同步首頁、分類頁、文章標籤、搜尋索引及排程規格。不得自行新增第八類。
- 完成遷移必須比較所有既有文章的 URL、date、categories、series_order 與正文，並確認每篇僅落入七類之一。
