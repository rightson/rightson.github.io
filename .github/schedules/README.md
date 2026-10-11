# 研究主題 prompt 入口

Codex 雲端排程器管理所有執行時間、週期、時區、enabled、模型及對話關聯。GitHub 只管理 prompt、寫作規則、研究 roadmap 與進度。本目錄不定義或保存任何執行時程，也不按觸發時間路由主題。

一個主題一份文件，一個排程器直接指定一份主題文件；同次啟動只執行指定主題。修改時間只在 Codex 進行，無須修改 GitHub。即使啟動延遲或手動執行，主題也保持相同。

| 主題 | prompt |
| --- | --- |
| SOTA R2G／CAD 平台深度學習 | [sota-r2g-cad](topics/sota-r2g-cad.md) |
| Agentic Design 即時雷達 | [agentic-design-radar](topics/agentic-design-radar.md) |
| Agentic Design 架構深掘與會議素材 | [agentic-design-deep-dive](topics/agentic-design-deep-dive.md) |
| AI 前沿每日摘要 | [ai-frontier-digest](topics/ai-frontier-digest.md) |
| AI 每週分享素材 | [ai-weekly-share](topics/ai-weekly-share.md) |
| LLM Lab：模型到晶片的完整技術鏈 | [llm-lab](topics/llm-lab.md) |
| MTK／台積電生態系機構與基本面晨報 | [mtk-ecosystem-institutional](topics/mtk-ecosystem-institutional.md) |
| 盤中價量與事件觀察 | [mtk-ecosystem-intraday](topics/mtk-ecosystem-intraday.md) |
| 盤後籌碼與波段決策日誌 | [mtk-ecosystem-market-journal](topics/mtk-ecosystem-market-journal.md) |
| MTK 與半導體生態系深度研究 | [mtk-ecosystem-deep-dive](topics/mtk-ecosystem-deep-dive.md) |
| TPU／AI 加速器深度系列 | [tpu-technical](topics/tpu-technical.md) |
| Networking 每週深度長文 | [networking-deep-dive](topics/networking-deep-dive.md) |
| 分散式系統深度系列 | [distributed-systems](topics/distributed-systems.md) |
| Kubernetes：從執行模型到平台工程 | [k8s-hpc](topics/k8s-hpc.md) |

## 讀取協定

1. 取得 rightson/rightson.github.io 最新 default branch metadata 及 commit SHA。
2. 從該 commit 完整讀取 AGENTS.md、common.md 及雲端 prompt 指定的 topics/<topic-key>.md，再讀分類規格、相關 roadmap、最近成果及進度。
3. 記錄 instruction commit SHA。讀取失敗、缺檔或截斷時停止該次發布並精確回報，保留任務。
4. 直接執行指定主題，不以星期、時段、啟動時間或本索引選擇其他主題。
5. 寫入前核對最新 head 與目標 blob SHA，保留其他人的變更；依 AGENTS.md 驗證完成階段。

manifest.json 與 .github/RESEARCH_AUTOMATIONS.json 只提供主題文件索引，不是排程設定，也不是第二份 prompt。通用要求只在 common.md 維護；各主題完整責任只在對應文件維護。十四個系列沿用穩定 identifier、roadmap 與歷史完成記錄。此目錄不新增網站公開選單或文章。
