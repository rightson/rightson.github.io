# 研究主題與 prompt 索引

本檔保留既有路徑作研究入口，僅索引 prompt 與責任。執行時間、週期、時區、啟用狀態、模型與對話關聯完全由 Codex 雲端排程器管理，不保存於 GitHub。研究 agent 不從本檔推導或判斷分支。

| 主題 | 唯一任務指令 | 進度來源 |
| --- | --- | --- |
| SOTA R2G／CAD 平台深度學習 | [sota-r2g-cad](schedules/topics/sota-r2g-cad.md) | `.github/EDA_PLATFORM_SERIES_ROADMAP.md` |
| Agentic Design 即時雷達 | [agentic-design-radar](schedules/topics/agentic-design-radar.md) | `.github/AGENTIC_DESIGN_SERIES_ROADMAP.md` |
| Agentic Design 架構深掘與會議素材 | [agentic-design-deep-dive](schedules/topics/agentic-design-deep-dive.md) | `.github/AGENTIC_DESIGN_SERIES_ROADMAP.md`、`.github/EDA_PLATFORM_SERIES_ROADMAP.md` |
| AI 前沿每日摘要 | [ai-frontier-digest](schedules/topics/ai-frontier-digest.md) | 最新同系列成果 |
| AI 每週分享素材 | [ai-weekly-share](schedules/topics/ai-weekly-share.md) | 最新同系列成果 |
| LLM Lab：模型到晶片的完整技術鏈 | [llm-lab](schedules/topics/llm-lab.md) | `.github/LLM_LAB_SERIES_ROADMAP.md`、`.github/TPU_SERIES_ROADMAP.md`、`.github/K8S_HPC_SERIES_ROADMAP.md`、`.github/DISTRIBUTED_SYSTEMS_SERIES_ROADMAP.md` |
| MTK／台積電生態系機構與基本面晨報 | [mtk-ecosystem-institutional](schedules/topics/mtk-ecosystem-institutional.md) | `.github/MTK_ECOSYSTEM_RESEARCH.md` |
| 盤中價量與事件觀察 | [mtk-ecosystem-intraday](schedules/topics/mtk-ecosystem-intraday.md) | `.github/MTK_ECOSYSTEM_RESEARCH.md` |
| 盤後籌碼與波段決策日誌 | [mtk-ecosystem-market-journal](schedules/topics/mtk-ecosystem-market-journal.md) | `.github/MTK_ECOSYSTEM_RESEARCH.md` |
| MTK 與半導體生態系深度研究 | [mtk-ecosystem-deep-dive](schedules/topics/mtk-ecosystem-deep-dive.md) | `.github/MTK_ECOSYSTEM_RESEARCH.md`、`.github/TPU_SERIES_ROADMAP.md` |
| TPU／AI 加速器深度系列 | [tpu-technical](schedules/topics/tpu-technical.md) | `.github/TPU_SERIES_ROADMAP.md` |
| Networking 每週深度長文 | [networking-deep-dive](schedules/topics/networking-deep-dive.md) | `.github/NETWORKING_SERIES_ROADMAP.md` |
| 分散式系統深度系列 | [distributed-systems](schedules/topics/distributed-systems.md) | `.github/DISTRIBUTED_SYSTEMS_SERIES_ROADMAP.md` |
| Kubernetes：從執行模型到平台工程 | [k8s-hpc](schedules/topics/k8s-hpc.md) | `.github/K8S_HPC_SERIES_ROADMAP.md` |

全站規則：AGENTS.md；共用研究規則：schedules/common.md；分類：ARTICLE_TAXONOMY.md 與 _data/research_series.yml。RESEARCH_AUTOMATIONS.json 與 schedules/manifest.json 都只保存文件索引，不複製 prompt 或排程設定。

## 跨系列責任

- SOTA 擁有公司公開平台案例；Agentic radar 擁有新增變化；Agentic deep dive 擁有架構長文與私人會議素材。
- AI frontier 擁有通用模型與 Agent 廣度；分享素材整合已完成研究；LLM Lab 串起模型到晶片的實驗課程；TPU 擁有硬體微架構與資料流。
- Networking 擁有協定與資料路徑；K8s/HPC 擁有系統與平台工程；Distributed Systems 擁有完整服務需求、一致性、複寫及容錯設計。
- 機構與基本面研究擁有預期修正；盤中觀察擁有當時事件及價格反應；盤後日誌擁有官方價量籌碼與私人論點；生態系深研擁有完整技術、競爭與財務傳導。
- 各系列引用相關已完成成果，保留獨立 roadmap、穩定篇號與實驗進度；不從其他 session 猜測結果。公開／私人界線由最新 AGENTS.md 與主題文件決定。
