# 八類公開文章與十四個研究系列

2026-10-01 使用者核准前八類；2026-10-03 核准新增「科學與物理」（science-physics）。五個排程器是執行入口；十四個系列保留各自進度；八個 `domain` 是公開選單。三者不可混用。2026-10-04 依使用者要求收回「投資與交易」（investing）：投資觀點不公開發佈，既有稿件封存於 `_archive/investing/`。

## 分類以文章主要回答的問題為準

| domain | 選單分類 | 主要問題 | 預設系列 |
| --- | --- | --- | --- |
| ic-design-platform | IC 設計平台 | 晶片如何設計、驗證、交接與治理？ | sota-r2g-cad、agentic-design-radar、agentic-design-deep-dive |
| ai-frontier | AI 技術與工程 | 模型與通用 Agent 如何運作、評估與實作？ | ai-frontier-digest、ai-weekly-share、llm-lab |
| architecture | 運算架構 | 運算硬體如何安排計算、資料搬移與記憶體？ | tpu-technical |
| networking | 網路系統 | 資料如何跨節點傳送，如何控制壅塞與恢復？ | networking-deep-dive |
| distributed-systems | 分散式系統 | 服務如何設計資料、狀態、一致性、複寫、容錯與恢復？ | distributed-systems |
| platform-engineering | 系統與平台 | Linux、容器、K8s／HPC 平台如何執行、隔離、配置資源、維運及驗證效能？ | k8s-hpc |
| ai-industry | 產業與供應鏈 | 企業如何成長、競爭、獲利，供需與價值如何分配？ | mtk-ecosystem-deep-dive |
| science-physics | 科學與物理 | 自然現象與材料物性由哪些物理機制決定，如何以實驗和理論理解？ | 單篇專題，無新增排程系列 |

完整系列名稱與預設分類見 `_data/research_series.yml`；選單名稱、順序與說明見 `_data/domains.yml`。以上預設不能代替逐篇閱讀與判斷。

## 邊界與標籤

- 每篇只有一個主要 `domain`；`series`、公司與技術名稱是次級資料，不增加主選單。既有系列 identifier、篇號、roadmap 與完成歷史保持穩定；缺少 `series` 時只在既有 roadmap／文章提供足夠接續證據時補上，不硬把所有歷史稿塞進新版系列。
- EDA 演算法、STA／SDC、placement、routing、verification、signoff 與 R2G 平台均歸 `ic-design-platform`；`eda`、`timing` 是舊分類相容值，不再建立獨立公開分類。
- 通用模型與 Agent 機制歸 `ai-frontier`；主問題在 RTL、驗證、synthesis／APR、signoff 的導入、流程或驗收責任，歸 `ic-design-platform`。
- LLM Lab 主問題為模型、數學與軟體實作時歸 `ai-frontier`；獨立加速器資料流或微架構歸 `architecture`。依主要問題亦可歸網路、系統或 IC 平台；系列 identifier 不變。
- 解釋企業如何成長、競爭及獲利歸 `ai-industry`；判斷股價已反映的預期、合理估值、資金動向或進退場條件屬投資觀點，不公開發佈；mtk-ecosystem-institutional、mtk-ecosystem-intraday、mtk-ecosystem-market-journal 的結果只留在排程對話或私人紀錄。出現營收、EPS、毛利或現金流數字，不足以將文章判成投資文。
- 半導體生態系深研預設 `ai-industry`；主問題為合理股價、估值情境或布局條件時不公開發佈。晨報只有在獨立回答經營或供需問題、且不含估值或進退場判斷時，才依主問題公開分類。
- TPU 微架構歸 `architecture`；其供需、競爭或估值研究依上述邊界分流。互連協定與封包路徑歸 `networking`；服務一致性、複寫與完整服務設計歸 `distributed-systems`；Linux、容器、K8s／HPC、叢集資源與平台維運歸 `platform-engineering`，不因應用於 AI／EDA 而改分類。

## 既有與未來文章

2026-10-01 使用者核准：IC 設計平台目前只公開以平台架構、工程協作、工具／資料交接、狀態管理、執行恢復或驗收治理為主問題的文章。純 STA／SDC 基礎教材、placement／timing 演算法或單一引擎機制暫不公開；不能只加平台總覽或驗收段落就視為平台文章。封存清單以 `_archive/ic-design-platform/README.md` 為準；封存稿仍算歷史已完成，保留原始 date、categories、series、篇號及查重紀錄，不移回 `_posts/`、不換 slug／日期重發，恢復發布須使用者另行確認。其他分類與十四個系列的研究責任、五個排程器的時程及啟用狀態不變。

- 既有文章重新分類只改 `domain`，保留 filename、date、categories、permalink、正文、原始系列與篇號；不靠改 categories 移動網址。已封存文章保持封存。
- 新文章使用單一 `categories`，與所選 `domain` 相同；`series` 使用穩定 identifier，可跨 domain，不隨題目更名。
- 寫作前讀最新 `AGENTS.md`、本檔及對應 roadmap；分類變更同步首頁、分類頁、文章標籤、搜尋索引及排程規格。本次使用者已核准新增 platform-engineering（系統與平台）；其他分類變更仍需使用者授權。
- 完成遷移必須比較所有既有文章的 URL、date、categories、series_order 與正文，並確認每篇僅落入九類之一。

2026-10-01 後續核准：K8s 課程從零建立 Kubernetes 能力並沿用 OS 先備，公開分類名稱為「系統與平台」。LLM Lab 預設仍為 ai-frontier；每篇依主要問題選分類，series llm-lab 保持獨立。

科學與物理研究歸 science-physics；若主問題是運算硬體資料流，仍歸 architecture。新增分類不自動建立研究系列或排程。
