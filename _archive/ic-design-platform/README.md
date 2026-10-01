# IC 設計平台：暫停公開的非平台文章

2026-10-01 使用者核准：IC 設計平台目前只公開以平台架構、工程協作、工具／資料交接、狀態管理、執行恢復或驗收治理為主問題的文章。純 STA／SDC 基礎教材、placement／timing 演算法或單一引擎機制暫不公開；不能只加平台總覽或驗收段落就視為平台文章。封存清單以 `_archive/ic-design-platform/README.md` 為準；封存稿仍算歷史已完成，保留原始 date、categories、series、篇號及查重紀錄，不移回 `_posts/`、不換 slug／日期重發，恢復發布須使用者另行確認。其他六類與十四個系列的研究責任、五個排程器的時程及啟用狀態不變。

本目錄由 `_config.yml` 的 `_archive` exclusion 排除，不產生公開文章頁、首頁條目、分類、搜尋索引或 RSS。封存原文 byte-for-byte 保留；引用圖片保留於原路徑，方便恢復及避免其他文章引用失效。封存原文仍存於本公開 repository。

| 原始日期 | 文章 | 封存原文 | 原公開 URL（已下架） |
| --- | --- | --- | --- |
| 2026-09-23 | STA 的時間需求從哪裡來：SDC、Arrival Time 與 Slack | [Markdown](_posts/2026-09-23-timing-constraint-defines-deadline.md) | `https://rightson.github.io/eda/2026/09/23/timing-constraint-defines-deadline.html` |
| 2026-09-24 | Launch 與 Capture Edge：Setup、Hold 如何建立不同期限 | [Markdown](_posts/2026-09-24-clock-edges-define-setup-hold.md) | `https://rightson.github.io/eda/2026/09/24/clock-edges-define-setup-hold.html` |
| 2026-09-24 | AutoDMP 的分層搜尋：快速佈局如何接到後段 PPA 驗收 | [Markdown](_posts/2026-09-24-nvidia-autodmp-r2g-design-platform.md) | `https://rightson.github.io/eda/2026/09/24/nvidia-autodmp-r2g-design-platform.html` |
| 2026-09-26 | C3PO 如何校準佈局目標：時序、壅塞與後段結果的落差 | [Markdown](_posts/2026-09-26-nvidia-c3po-concurrent-placement-r2g.md) | `https://rightson.github.io/eda/2026/09/26/nvidia-c3po-concurrent-placement-r2g.html` |
| 2026-10-01 | INSTA 把 signoff 時序壓進實體設計內迴圈：一次校準、GPU 傳播與驗收邊界 | [Markdown](_posts/2026-10-01-nvidia-insta-signoff-feedback-loop.md) | `https://rightson.github.io/eda/2026/10/01/nvidia-insta-signoff-feedback-loop.html` |

## 恢復條件

只有使用者另行核准後，才可將原檔移回原 `_posts/` 路徑；保持 front matter、檔名與圖片路徑，原 URL 因而可恢復。`manifest.json` 記錄原始路徑、URL、metadata 與內容雜湊；不得為了續刊自動恢復或重編篇號。
