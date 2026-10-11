# TPU／AI 加速器深度系列

本任務只處理 `tpu-technical`。每次啟動直接執行本文件，不依星期、觸發時段或啟動時間選擇其他主題。

先讀同一 instruction commit 的 `AGENTS.md`、`.github/schedules/common.md`、`.github/ARTICLE_TAXONOMY.md`、`_data/research_series.yml` 及以下研究進度，再讀最近同系列文章。

## 接續來源

- `.github/TPU_SERIES_ROADMAP.md`

## 本次工作

TPU／AI 加速器深度系列。本任務 series: tpu-technical。
延續 .github/TPU_SERIES_ROADMAP.md 的穩定 ID、先備、已完成與驗證狀態。每次先處理既有 source committed／public verification pending 篇目，再選下一個先備已具備的未完成項，不因新 session 重啟 TPU v1 已講過內容。深入 workload→compiler/runtime→microarchitecture→memory→chip/package→ICI/DCN→pod 中一個主要問題，交代設計動機、資料流、完整具體例子、tensor／bandwidth／latency／roofline 算例與失效／性能邊界。優先 Google 官方技術原文與原始架構／系統論文，核對代際與 availability；不把商業供應鏈猜測寫成架構事實。domain/categories: architecture；series: tpu-technical。與 LLM Lab 的課程鏈互相引用，與 K8s／distributed-systems 遵守既有 ownership，商業與供應鏈另由 MTK 生態系研究。

.github/TPU_SERIES_ROADMAP.md 是本系列唯一課程進度來源；依概念相依選下一個未完成主題，連接 workload／algorithm → compiler／runtime → microarchitecture → chip／memory／package → board／rack → network／datacenter。
