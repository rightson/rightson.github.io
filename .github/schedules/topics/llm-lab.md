# LLM Lab：模型到晶片的完整技術鏈

本任務只處理 `llm-lab`。每次啟動直接執行本文件，不依星期、觸發時段或啟動時間選擇其他主題。

先讀同一 instruction commit 的 `AGENTS.md`、`.github/schedules/common.md`、`.github/ARTICLE_TAXONOMY.md`、`_data/research_series.yml` 及以下研究進度，再讀最近同系列文章。

## 接續來源

- `.github/LLM_LAB_SERIES_ROADMAP.md`
- `.github/TPU_SERIES_ROADMAP.md`
- `.github/K8S_HPC_SERIES_ROADMAP.md`
- `.github/DISTRIBUTED_SYSTEMS_SERIES_ROADMAP.md`

## 本次工作

LLM Lab：模型到晶片的完整技術鏈。本任務 series: llm-lab。
以 .github/LLM_LAB_SERIES_ROADMAP.md 的先備與穩定篇號維持全棧主線：模型概念→數學與演算法→程式實作→訓練／推論系統→compiler／runtime→專用加速器→RTL、驗證、synthesis、STA、APR 與 signoff。每次一個完整單元，先建立直覺與必要推導，再給可執行程式、環境／版本、baseline、預期觀察與結果解釋；本次可執行時實跑並保留證據，無所需硬體時交付可重現程序，清楚標未實跑，不編造結果。安排合理規模，不能要求尚未教過的知識。透過真正改變效能或正確性的上下層 coupling 連結 SW 到 HW，其他專門系列擁有的機制以已發布文章引用，避免重寫。課程進度以 repo 與實際完成作品接續，不依舊 session。主要模型／演算法／實作歸 ai-frontier，獨立硬體微架構歸 architecture，獨立 EDA 或平台問題依 AGENTS.md 分類。

另先讀 rightson/llm-lab 最新 default branch metadata、完整 AGENTS.md、README、現有 learning-plan、lesson-standard、learning-progress 與相關課程檔案，記錄該 repo instruction SHA。依該 repo 規則提交教材與程式，網站發布對應完整教學文章；分別驗證兩個 repo。不能執行的實驗列為未完成，保留實驗進度，不捏造輸出。
