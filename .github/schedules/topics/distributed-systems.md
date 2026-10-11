# 分散式系統深度系列

本任務只處理 `distributed-systems`。每次啟動直接執行本文件，不依星期、觸發時段或啟動時間選擇其他主題。

先讀同一 instruction commit 的 `AGENTS.md`、`.github/schedules/common.md`、`.github/ARTICLE_TAXONOMY.md`、`_data/research_series.yml` 及以下研究進度，再讀最近同系列文章。

## 接續來源

- `.github/DISTRIBUTED_SYSTEMS_SERIES_ROADMAP.md`

## 本次工作

分散式系統深度系列。本任務 series: distributed-systems。
完整遵守 .github/DISTRIBUTED_SYSTEMS_SERIES_ROADMAP.md 與 AGENTS.md 的專用敘事順序。從具體服務使用情境與需求開始，給出功能、規模／SLO／一致性／耐久性／不變量，建立能走完正常請求的最小 API、資料模型與狀態擁有者設計；用帶單位的容量推導、偏斜流量、競態、故障或新需求證明缺口，再引入分片、cache、replication、quorum、lease、fencing 等必要機制。每次演進都比較合理替代與代價，追蹤失效點、殘留狀態、使用者可見結果、偵測與恢復；需求變體必須完成推導。累積大型服務設計與工程推理能力，不用元件清單或標準答案模板。沿既有穩定 ID 與進度接續，先核對最新已發布短網址、ID、限流文章與 roadmap 差異，不重寫已完成案例。domain/categories/series: distributed-systems。

案例涵蓋完整 45–60 分鐘架構推理的廣度與關鍵深掘；公開內容不含面試或求職敘述。需求先行，不從孤立細節開始。
