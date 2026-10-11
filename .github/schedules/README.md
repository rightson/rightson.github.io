# 研究主題 prompt 入口

Codex 雲端排程器管理所有執行時間、週期、時區、enabled、模型及對話關聯。GitHub 只管理 prompt、寫作規則、研究 roadmap 與進度，不定義或保存執行時程，也不按觸發時間路由主題。

一個啟用主題一份文件，一個排程器直接指定一份主題文件。MTK／台積電的四條研究線已合併為 csp-capex-ecosystem；舊系列與文章只保留歷史，其他主題保持獨立。

| 主題 | prompt |
| --- | --- |
| SOTA R2G／CAD 平台深度學習 | [sota-r2g-cad](topics/sota-r2g-cad.md) |
| Agentic Design 即時雷達 | [agentic-design-radar](topics/agentic-design-radar.md) |
| Agentic Design 架構深掘與會議素材 | [agentic-design-deep-dive](topics/agentic-design-deep-dive.md) |
| AI 前沿每日摘要 | [ai-frontier-digest](topics/ai-frontier-digest.md) |
| AI 每週分享素材 | [ai-weekly-share](topics/ai-weekly-share.md) |
| LLM Lab：模型到晶片的完整技術鏈 | [llm-lab](topics/llm-lab.md) |
| TPU／AI 加速器深度系列 | [tpu-technical](topics/tpu-technical.md) |
| Networking 每週深度長文 | [networking-deep-dive](topics/networking-deep-dive.md) |
| 分散式系統深度系列 | [distributed-systems](topics/distributed-systems.md) |
| Kubernetes：從執行模型到平台工程 | [k8s-hpc](topics/k8s-hpc.md) |
| CSP 高資本支出供應鏈關鍵動態 | [csp-capex-ecosystem](topics/csp-capex-ecosystem.md) |

## 讀取協定

取得最新 default branch metadata 與 commit SHA；完整讀取同一 commit 的 AGENTS.md、common.md 與雲端 prompt 明確指定的主題文件，再讀分類、相關 roadmap、最近成果與進度。直接執行指定主題，時間缺漏或延遲不改變主題。必需指令缺檔、讀取失敗或截斷時停止該次發布並回報，保留任務。寫入前核對最新 head／blob SHA，保留其他人的變更，依 AGENTS.md 核驗完成階段。

manifest.json、RESEARCH_AUTOMATIONS.json 與 RESEARCH_SCHEDULES.md 只索引文件及責任，不保存 runtime 設定，也不複製第二份 prompt。修改時間只在 Codex 進行；一般 prompt 修改供下一次讀取最新 commit。改文件路徑時同步雲端 prompt。
