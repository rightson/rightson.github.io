# Kubernetes：從執行模型到平台工程

本任務只處理 `k8s-hpc`。每次啟動直接執行本文件，不依星期、觸發時段或啟動時間選擇其他主題。

先讀同一 instruction commit 的 `AGENTS.md`、`.github/schedules/common.md`、`.github/ARTICLE_TAXONOMY.md`、`_data/research_series.yml` 及以下研究進度，再讀最近同系列文章。

## 接續來源

- `.github/K8S_HPC_SERIES_ROADMAP.md`

## 本次工作

Kubernetes：從執行模型到平台工程完整長文。讀者沿用 OS、程式與網路先備，Kubernetes 從零學習，OS 基本名詞按需簡短銜接，新 K8s 概念清楚建立動機、系統模型與責任邊界。先讀網站 .github/K8S_HPC_SERIES_ROADMAP.md，再讀 rightson/k8s-lab 最新 default branch metadata、完整 AGENTS.md、README、docs/learning-plan.md、docs/lesson-standard.md、docs/learning-progress.json 與相關教材；記錄兩個 repo instruction commit SHA。依 K082–K129（40 核心＋8 進階）的先備順序推進，初始化下一單元為 K082；後續以 lab ledger 的 next_unit、未完成狀態與先備接續，不固定重跑 K082；舊 #001–#006、K001–K081 均保留歷史但不當新課程完成，不恢復封存稿、不重用篇號、不換日期重發。所有輔助教材、練習、解答、manifest、程式與 raw 實驗放 rightson/k8s-lab，網站放對應完整公開長文與文章圖，domain/categories platform-engineering（系統與平台），series k8s-hpc。先提交並回讀 lab source 與實驗，再發布網站；兩個 repo 各自核驗階段，只有必要實驗及網站 source/build/deploy/public content 全成立才更新 lab 完成進度。硬體或來源不足記錄精確 blockers，不捏造實驗，不縮成摘要。

