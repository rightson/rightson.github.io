# 研究排程與系列分工

2026-09-30 使用者已同意本版主題、週期與系列分工。這是編輯規格，不代表排程已建立或啟用；runtime 是否生效，必須由 scheduler 的 canonical ID、enabled、schedule、timezone 與新 session 關聯驗證。

## 規則與接續

2026-10-01 使用者核准：IC 設計平台目前只公開以平台架構、工程協作、工具／資料交接、狀態管理、執行恢復或驗收治理為主問題的文章。純 STA／SDC 基礎教材、placement／timing 演算法或單一引擎機制暫不公開；不能只加平台總覽或驗收段落就視為平台文章。封存清單以 `_archive/ic-design-platform/README.md` 為準；封存稿仍算歷史已完成，保留原始 date、categories、series、篇號及查重紀錄，不移回 `_posts/`、不換 slug／日期重發，恢復發布須使用者另行確認。其他分類與十四個系列的研究責任、五個排程器的時程及啟用狀態不變。

- 每次開寫完整讀取最新 default branch 的 `AGENTS.md`、`_config.yml`、本檔、[五個任務指令](schedules/README.md) 與 [系列補充規格](RESEARCH_AUTOMATIONS.json)、直接相關 roadmap 與近期文章。`AGENTS.md` 仍是唯一 agent source of truth；本檔只補充任務分工，不放寬既有門檻。
- 依 2026-10-01 核准前八類及 2026-10-03 新增科學與物理的九類順序分類，詳見 ARTICLE_TAXONOMY.md；既有 permalink 保留；每篇按核心問題選一個 domain，新文章 categories 與 domain 一致。`series` 表示系列接續，不能改動既有 URL。
- 所有 replacement task 使用全新 cloud session。知識進度由 repo roadmap、已發布文章與可核對的 ledger 接續，不使用舊對話狀態。
- 初始化與定期執行分開：一次性停用舊任務／建立新任務的步驟不得放進 recurring prompt。
- 啟動時間採 Asia/Taipei，文章 date 仍按首次實際寫入時間。台股工作日只是執行候選日；每次盤中／盤後先核對官方交易日。
- 會議摘要、私人決策日誌、持倉與實際交易留在各自 session；公開 repo 僅保存適合公開的研究、來源與課程狀態。

## 目前五個執行入口

管理入口：[schedules/README.md](schedules/README.md)。改任務內容與共用規則供下次執行讀取；改時間或 enabled 仍須同步 scheduler，回讀後更新 manifest。完整任務指令見各 group 檔，十四個系列 JSON prompt 為補充規格；時段依五個 group 分派。

2026-10-01 已有五個研究排程；以下是目前工作分派，取代原十四個主題的獨立啟動時間。scheduler 設定仍需回讀核驗。2026-10-01 已將共用規則與五個完整任務指令移至 `schedules/`，雲端只保留讀取 repo 的短 prompt；不新增、重啟或重排任務。

| 排程器 | Asia/Taipei | 系列分派 |
| --- | --- | --- |
| R2G／Agentic Design | 每日 06:00 | 每日雷達；週一 SOTA；週二架構長文與會議摘要 |
| AI 前沿與分享 | 每日 07:30 | 每日摘要；週四分享素材 |
| 技術課程 | 週三至六 19:00 | 三 Networking；四 K8s；五 TPU 與分散式系統；六 LLM Lab |
| 生態系投資研究 | 平日 05:30、17:30；週日 05:30 | 晨報、盤後日誌、週日深研 |
| 市場事件觀察 | 台股交易日 10:30、13:30 | 盤中事件觀察 |

十四個系列及預設分類見 `_data/research_series.yml`；實際分類依文章主問題與 ARTICLE_TAXONOMY.md。公開 repo 的編輯規格不新增額外任務。

## 十四個系列的內容規格

| 系列 | 啟動週期（Asia/Taipei） | 產出 | 主要 domain |
| --- | --- | --- | --- |
| `sota-r2g-cad`：SOTA R2G／CAD 平台深度學習 | 每週一 06:00 | 每週一篇深度長文 | ic-design-platform |
| `agentic-design-radar`：Agentic Design 即時雷達 | 每日 06:00 | 重要增量才發布短評 | ic-design-platform |
| `agentic-design-deep-dive`：Agentic Design 架構深掘與會議素材 | 每週二 06:00 | 一篇長文；會議摘要留 session | ic-design-platform |
| `ai-frontier-digest`：AI 前沿每日摘要 | 每日 07:30 | 有增量的一篇技術摘要 | ai-frontier |
| `ai-weekly-share`：AI 每週分享素材 | 每週四 07:30 | session 分享材料；增量足夠才發公開綜述 | ai-frontier |
| `llm-lab`：LLM Lab：模型到晶片的完整技術鏈 | 每週六 19:00 | 每週一篇完整 lab | ai-frontier / architecture / ic-design-platform |
| `mtk-ecosystem-institutional`：MTK／台積電生態系機構與基本面晨報 | 週一至五 05:30 | session 短報；重大假設變化才發文 | investing / ai-industry |
| `mtk-ecosystem-intraday`：盤中價量與事件觀察 | 台股交易日 10:30、13:30 | 只在 session 通知重要變化 | investing |
| `mtk-ecosystem-market-journal`：盤後籌碼與波段決策日誌 | 台股交易日 17:30 | 有價值的公開分析；私人日誌留 session | investing |
| `mtk-ecosystem-deep-dive`：MTK 與半導體生態系深度研究 | 每週日 05:30 | 每週一篇深度研究 | ai-industry / investing |
| `tpu-technical`：TPU／AI 加速器深度系列 | 每週五 19:00 | 每週一篇深度長文 | architecture |
| `networking-deep-dive`：Networking 每週深度長文 | 每週三 19:00 | 每週一篇深度長文 | networking |
| `distributed-systems`：分散式系統深度系列 | 每週五 19:00 | 每週一篇完整系統設計案例 | distributed-systems |
| `k8s-hpc`：Kubernetes：從執行模型到平台工程 | 每週四 19:00 | 每週一篇完整教材，練習與實驗在 k8s-lab | platform-engineering |

## 任務分工

### SOTA R2G／CAD 平台深度學習

從 NVIDIA、AMD、Qualcomm、Broadcom、Marvell 與 Synopsys、Cadence、Siemens 等公開案例，選一個能補齊知識缺口的具名平台或設計方法。研究完整 design intent／IP／SoC／RTL／verification／formal／DFT／synthesis／SDC／APR／ECO／signoff／package 的必要交接，說清 inputs、可改變數、artifacts 與交接；先建立端到端總覽，再深掘至少兩個關鍵機制、設計理由與 trade-off。結論要回答這種做法在什麼條件下改善時程、品質、tool-hours 或人力及其代價；驗收或失效恢復只在它們決定該案例結果時展開。形成跨公司有來源支持的比較與可借鏡的實驗。僅將公開證據支持的內容稱為公司現有做法；徵才、議程標題、行銷聲明不能拼成完整內部架構。開源 flow 可作可重現對照，不把它等同商用先進製程量產。晶片設計方法與平台主問題歸 ic-design-platform。延續既有 EDA roadmap 已公開案例與完成狀態，每週一篇，讓週一／週二有完整消化時間；不重啟舊篇目、不重寫已有 NVIDIA／Qualcomm 案例。

- series：`sota-r2g-cad`
- 任務指令：[schedules/r2g-agentic-design.md](schedules/r2g-agentic-design.md)；系列補充規格：`RESEARCH_AUTOMATIONS.json` 的 `sota-r2g-cad`。
- 接續來源：`.github/EDA_PLATFORM_SERIES_ROADMAP.md`

### Agentic Design 即時雷達

追蹤最近 24–72 小時新增且尚未報告的 Agentic Design／AI EDA 產品、論文、官方技術說明、開源專案與實際導入證據。每期最多 3–5 項，說明新能力、底層機制、與舊做法的差異、prototype／preview／GA／production 的成熟度、平台工程影響與下一個值得驗證的問題。週三、週四額外指出相對週二架構文章的重大新增變化。只研究 Agentic Design 與設計流程；通用 AI 廣度交由 ai-frontier-digest。以本 session 短報為預設，足夠認知增量才產出約 1,000–2,000 中文字的公開短評，包含必要背景圖與一手來源；無重大變化簡短回報並留待下次。將值得深掘的題目加入相關 roadmap 候選，不每次重寫長文。

- series：`agentic-design-radar`
- 任務指令：[schedules/r2g-agentic-design.md](schedules/r2g-agentic-design.md)；系列補充規格：`RESEARCH_AUTOMATIONS.json` 的 `agentic-design-radar`。
- 接續來源：`.github/AGENTIC_DESIGN_SERIES_ROADMAP.md`

### Agentic Design 架構深掘與會議素材

從最新雷達與 roadmap 選一個有足夠公開原文、值得完整掌握的新理念或架構，深入 design state／compiler IR／tool interface、artifact lineage、長程執行／記憶、evaluation、sandbox／policy／authority、失敗恢復或跨工具閉環，依題目選必要機制。先用 RTL、Tcl、SDC、report、checkpoint 與實際設計階段建立可理解的流程，不用抽象平台名詞代替機制。比較至少兩個合理方案與既有人工／script baseline；有完整端到端案例、failure scenario、量化證據與最小可驗證實驗，清楚標示實跑／未跑。公開一篇符合長文規則的研究文章。另在本 session 提供一頁週三／週四會議摘要，整合最近七天已發布 SOTA 與 Agentic 素材，含 3 個核心判斷、支持證據、可採取行動、導入風險、主管可能追問與可用回答；只引用可讀取材料，不假稱能看到其他 session，不把私人會議摘要推到公開 repo。

- series：`agentic-design-deep-dive`
- 任務指令：[schedules/r2g-agentic-design.md](schedules/r2g-agentic-design.md)；系列補充規格：`RESEARCH_AUTOMATIONS.json` 的 `agentic-design-deep-dive`。
- 接續來源：`.github/AGENTIC_DESIGN_SERIES_ROADMAP.md`, `.github/EDA_PLATFORM_SERIES_ROADMAP.md`

### AI 前沿每日摘要

每天維持 agentic platform owner 對世界最新技術的廣度掌握。追蹤前沿模型公司、模型能力與訓練／推論方法、reasoning／multimodal、Agent 工具／memory／evaluation／runtime、open-weight、新興熱門專案及重大活動（例如 DevDay）。先核實最近 24–72 小時的實際新增消息，重大活動可跨日接續不同認知增量。精選最多 5 項，回答發生什麼、技術差異、實際可用範圍、對平台的影響與值得試什麼。熱門度只作發現線索，核對官方 repo／release／論文與評測，避免把 star 數、demo 或 vendor benchmark 當成熟度。公開一篇約 1,200–2,500 中文字、具背景圖與必要比較的摘要，深題留給其他系列，固定 domain/categories: ai-frontier。不把產業估值或 EDA 特有工程細節塞進本系列。無重大認知增量就在 session 回報，不硬湊文章。

- series：`ai-frontier-digest`
- 任務指令：[schedules/ai-frontier-share.md](schedules/ai-frontier-share.md)；系列補充規格：`RESEARCH_AUTOMATIONS.json` 的 `ai-frontier-digest`。
- 接續來源：最新同系列文章與原始來源；選題進度保留在本新 session。

### AI 每週分享素材

彙整最近七天網站已發布 AI 前沿摘要與可核對的新來源，挑 3 個適合週五分享的技術主題。提供 5–10 分鐘分享提綱、每題一個明確技術 insight、關鍵圖／比較、可展示的 demo（只有實際可用才推薦展示）、agentic platform 影響、Q&A 與來源。指出本週相對上週改變的判斷，避免再堆一份新聞清單。完成即在本新 session 交付素材，私人公司資訊不入 repo；可公開且有獨立認知增量的綜述才新增文章，domain/categories: ai-frontier。公開版本仍完整遵守 AGENTS.md，不能以會議筆記名義降低來源、寫作或圖解門檻。

- series：`ai-weekly-share`
- 任務指令：[schedules/ai-frontier-share.md](schedules/ai-frontier-share.md)；系列補充規格：`RESEARCH_AUTOMATIONS.json` 的 `ai-weekly-share`。
- 接續來源：最新同系列文章與原始來源；選題進度保留在本新 session。

### LLM Lab：模型到晶片的完整技術鏈

以 .github/LLM_LAB_SERIES_ROADMAP.md 的先備與穩定篇號維持全棧主線：模型概念→數學與演算法→程式實作→訓練／推論系統→compiler／runtime→專用加速器→RTL、驗證、synthesis、STA、APR 與 signoff。每週一個完整單元，先建立直覺與必要推導，再給可執行程式、環境／版本、baseline、預期觀察與結果解釋；本次可執行時實跑並保留證據，無所需硬體時交付可重現程序，清楚標未實跑，不編造結果。安排合理規模，不能要求尚未教過的知識。透過真正改變效能或正確性的上下層 coupling 連結 SW 到 HW，其他專門系列擁有的機制以已發布文章引用，避免重寫。課程進度以 repo 與實際完成作品接續，不依舊 session。主要模型／演算法／實作歸 ai-frontier，獨立硬體微架構歸 architecture，獨立 EDA 或平台問題依 AGENTS.md 分類。

- series：`llm-lab`
- 任務指令：[schedules/technical-curriculum.md](schedules/technical-curriculum.md)；系列補充規格：`RESEARCH_AUTOMATIONS.json` 的 `llm-lab`。
- 接續來源：`.github/LLM_LAB_SERIES_ROADMAP.md`, `.github/TPU_SERIES_ROADMAP.md`, `.github/K8S_HPC_SERIES_ROADMAP.md`, `.github/DISTRIBUTED_SYSTEMS_SERIES_ROADMAP.md`

### MTK／台積電生態系機構與基本面晨報

以 .github/MTK_ECOSYSTEM_RESEARCH.md 維持 MTK、台積電與有證據的上下游／客戶／競爭／替代關係觀察池，保留既有 AI 供應鏈觀察範圍作次要雷達，不自行猜出完整 98 檔清單。每天核對最近 24–72 小時公司公告、營收／財報／法說、產品與客戶進展、競爭，以及機構評級與 revenue／EPS／gross margin／operating margin／shipment／ASP／capex／target price／multiple 修正。記錄機構、原文日期、old→new、預測期間、核心假設與公開來源；無法取得原始研究时標示媒體轉述／來源受限，不捏造或繞過付費牆。問清模型哪個假設改變、consensus revision 是否加速／減速、共識分歧、re-rating／de-rating 與估值已反映程度。與 latest 已公布價格／籌碼交叉驗證但不重做盤後報告。輸出最多 5 個重要變化和其投資論點影響；無新增重要變化保持精簡。重大公開研究才寫文章，估值／交易核心歸 investing，經營與供應鏈核心歸 ai-industry，不公開私人持倉。

- series：`mtk-ecosystem-institutional`
- 任務指令：[schedules/ecosystem-investment.md](schedules/ecosystem-investment.md)；系列補充規格：`RESEARCH_AUTOMATIONS.json` 的 `mtk-ecosystem-institutional`。
- 接續來源：`.github/MTK_ECOSYSTEM_RESEARCH.md`

### 盤中價量與事件觀察

先從官方交易日資料確認當天是否開市，非交易日直接結束本次觀察，保留排程。檢查資料來源、實際報價 timestamp、延遲與可用範圍；無適合盤中報價時在 session 明確回報資料能力缺口，不把日終／延遲資料冒充即時，不做缺乏支持的盤中進出判斷。以 MTK／台積電與已驗證關係觀察池，觀察價格／成交量、同時段可比較量能、相對強弱、技術關鍵區域與公告／消息的市場反應，檢查與既有 thesis 的分歧。盤中法人與融資券只用最新已公布資料，區分今日價格與前一交易日籌碼。只有出現重要的新變化／風險／條件觸發才在本新 session 通知，未變化保持安靜；同一事件記錄 timestamp 與 fingerprint 去重。這是兩個固定觀察窗，不能宣稱持續即時監控。提供條件式候選與失效條件、資料證據和不確定性，不承諾預測噴發、不代下單、不接觸交易授權。私人盤中訊號不例行發布 GitHub 文章。

- series：`mtk-ecosystem-intraday`
- 任務指令：[schedules/market-events.md](schedules/market-events.md)；系列補充規格：`RESEARCH_AUTOMATIONS.json` 的 `mtk-ecosystem-intraday`。
- 接續來源：`.github/MTK_ECOSYSTEM_RESEARCH.md`

### 盤後籌碼與波段決策日誌

確認官方交易日與資料 availability，再取得當日官方價格、成交量、外資／投信、融資券，以及有證據的歷史基線，處理單位、除權息與非交易日。追蹤 5／10／20 日籌碼變化、外資占成交量／金額、投信同步性、融資增減、MA5／20／60、20 日均量、相對強弱與近期高低點；缺資料的指標標缺漏，不填零、不捏造、不阻止其他證據完整的公司產出。尋找早期 accumulation、distribution、利多不漲、price/EPS 與 research/capital 分歧，同步做 downside scan。維持同一投資論點的日期序列與原始判斷，區分觀察／布局候選／追蹤中／風險升高，提供觸發、失效、減碼／獲利了結條件、替代解釋與尚缺證據；單一訊號不作確定結論。可公開且有認知增量的分析最多一篇，domain/categories: investing；個人持倉、實際交易與私人決策日誌只留本 session。公開 repo 只保存來源可追溯的研究 ledger，保留歷史而不事後改寫。

- series：`mtk-ecosystem-market-journal`
- 任務指令：[schedules/ecosystem-investment.md](schedules/ecosystem-investment.md)；系列補充規格：`RESEARCH_AUTOMATIONS.json` 的 `mtk-ecosystem-market-journal`。
- 接續來源：`.github/MTK_ECOSYSTEM_RESEARCH.md`

### MTK 與半導體生態系深度研究

每週一個主問題，結合 CTO 技術理解、CFO 財務與資本配置、buy-side 預期差與投資教育。輪替 AI ASIC／TPU、手機、車用及其他產品線，研究客戶、設計合作、台積電製程／先進封裝、供應鏈／競爭者／替代方案；同時追蹤全球 AI 基礎設施需求、capex、產能瓶頸、earnings pool、定價權、第二供應商與供給擴張，以保留原 AI 基礎設施週報的視野。將技術／產品變化連到 shipment、ASP、content、營收、毛利率、EPS、現金流與估值 driver，建立透明 bull/base/bear 情境、敏感度、催化劑、反證與市場已反映程度。不以相關性推定業務關係、設計得標或經濟利益；TPU 微架構由 TPU 系列負責，引用其已發布結果而不重寫。公開一篇來源完整的研究，主問題為商業／產業歸 ai-industry，估值／交易歸 investing；不得把估值情境說成保證股價或可反覆獲利的確定機會。更新公開 thesis／evidence ledger，保留舊判斷與修訂原因。

- series：`mtk-ecosystem-deep-dive`
- 任務指令：[schedules/ecosystem-investment.md](schedules/ecosystem-investment.md)；系列補充規格：`RESEARCH_AUTOMATIONS.json` 的 `mtk-ecosystem-deep-dive`。
- 接續來源：`.github/MTK_ECOSYSTEM_RESEARCH.md`, `.github/TPU_SERIES_ROADMAP.md`

### TPU／AI 加速器深度系列

延續 .github/TPU_SERIES_ROADMAP.md 的穩定 ID、先備、已完成與驗證狀態。每次先處理既有 source committed／public verification pending 篇目，再選下一個先備已具備的未完成項，不因新 session 重啟 TPU v1 已講過內容。深入 workload→compiler/runtime→microarchitecture→memory→chip/package→ICI/DCN→pod 中一個主要問題，交代設計動機、資料流、完整具體例子、tensor／bandwidth／latency／roofline 算例與失效／性能邊界。優先 Google 官方技術原文與原始架構／系統論文，核對代際與 availability；不把商業供應鏈猜測寫成架構事實。domain/categories: architecture；series: tpu-technical。與 LLM Lab 的課程鏈互相引用，與 K8s／distributed-systems 遵守既有 ownership，商業與供應鏈另由 MTK 生態系研究。

- series：`tpu-technical`
- 任務指令：[schedules/technical-curriculum.md](schedules/technical-curriculum.md)；系列補充規格：`RESEARCH_AUTOMATIONS.json` 的 `tpu-technical`。
- 接續來源：`.github/TPU_SERIES_ROADMAP.md`

### Networking 每週深度長文

維持能通吃頂尖國際會議與業界 AI 網路系統的知識。每週從 SIGCOMM、NSDI、Hot Interconnects 等原始論文、官方協定／硬體規格或實際工程案例選一個能補上知識缺口的題目；兼顧經典基礎與 scale-up／scale-out、RDMA/RoCE、congestion／flow control、collectives、NIC／switch、optical／CPO、failure recovery 等前沿。先建立 workload、topology、資料路徑與瓶頸，再解機制與演算法，量化延遲／頻寬／queue／fairness／utilization，說清實驗 baseline、部署限制、合理替代與 failure path。引用近期相關已發布篇目、不重寫 CSIG／STORM／NVLink／UALink 已談過的相同問題，除非有新證據或新的完整推導。domain/categories: networking，更新 roadmap 的候選與可驗證完成記錄。

- series：`networking-deep-dive`
- 任務指令：[schedules/technical-curriculum.md](schedules/technical-curriculum.md)；系列補充規格：`RESEARCH_AUTOMATIONS.json` 的 `networking-deep-dive`。
- 接續來源：`.github/NETWORKING_SERIES_ROADMAP.md`

### 分散式系統深度系列

完整遵守 .github/DISTRIBUTED_SYSTEMS_SERIES_ROADMAP.md 與 AGENTS.md 的專用敘事順序。從具體服務使用情境與需求開始，給出功能、規模／SLO／一致性／耐久性／不變量，建立能走完正常請求的最小 API、資料模型與状態擁有者設計；用帶單位的容量推導、偏斜流量、競態、故障或新需求證明缺口，再引入分片、cache、replication、quorum、lease、fencing 等必要機制。每次演進都比較合理替代與代價，追蹤失效點、殘留狀態、使用者可見結果、偵測與恢復；需求變體必須完成推導。累積大型服務設計、面試與工程推理能力，不用元件清單或標準答案模板。沿既有穩定 ID 與進度接續，先核對最新已發布短網址、ID、限流文章與 roadmap 差異，不重寫已完成案例。domain/categories/series: distributed-systems。

- series：`distributed-systems`
- 任務指令：[schedules/technical-curriculum.md](schedules/technical-curriculum.md)；系列補充規格：`RESEARCH_AUTOMATIONS.json` 的 `distributed-systems`。
- 接續來源：`.github/DISTRIBUTED_SYSTEMS_SERIES_ROADMAP.md`

### Kubernetes：從執行模型到平台工程

Kubernetes：從執行模型到平台工程完整長文。讀者沿用 OS、程式與網路先備，Kubernetes 從零學習，OS 基本名詞按需簡短銜接，新 K8s 概念清楚建立動機、系統模型與責任邊界。先讀網站 .github/K8S_HPC_SERIES_ROADMAP.md，再讀 rightson/k8s-lab 最新 default branch metadata、完整 AGENTS.md、README、docs/learning-plan.md、docs/lesson-standard.md、docs/learning-progress.json 與相關教材；記錄兩個 repo instruction commit SHA。依 K082–K129（40 核心＋8 進階）的先備順序推進，初始化下一單元為 K082；後續以 lab ledger 的 next_unit、未完成狀態與先備接續，不固定重跑 K082；舊 #001–#006、K001–K081 均保留歷史但不當新課程完成，不恢復封存稿、不重用篇號、不換日期重發。所有輔助教材、練習、解答、manifest、程式與 raw 實驗放 rightson/k8s-lab，網站放對應完整公開長文與文章圖，domain/categories platform-engineering（系統與平台），series k8s-hpc。先提交並回讀 lab source 與實驗，再發布網站；兩個 repo 各自核驗階段，只有必要實驗及網站 source/build/deploy/public content 全成立才更新 lab 完成進度。硬體或來源不足記錄精確 blockers，不捏造實驗，不縮成摘要。週四 Asia/Taipei 19:00 保持不變。

- series：`k8s-hpc`
- 任務指令：[schedules/technical-curriculum.md](schedules/technical-curriculum.md)；系列補充規格：`RESEARCH_AUTOMATIONS.json` 的 `k8s-hpc`。
- 接續來源：`.github/K8S_HPC_SERIES_ROADMAP.md`

## 舊任務的替換關係

| 舊任務 | 新任務／處理 |
| --- | --- |
| EDA 技術雷達、AI EDA 技術雷達 | 即時變化由 agentic-design-radar 負責；公司公開平台案例由 sota-r2g-cad 負責 |
| 頂尖 IC 設計平台／R2G 系列 | sota-r2g-cad，每週一 |
| EDA 平台工程週報、Big CAD 轉型週報 | agentic-design-deep-dive，每週二；新增消息進 daily radar |
| AI 前沿技術摘要 | ai-frontier-digest，加上 ai-weekly-share |
| LLM Lab 深度學習 | llm-lab，保留全棧課程主線 |
| AI 機構投資情報 | mtk-ecosystem-institutional |
| MTK ASIC 綜合訊號 | intraday、market-journal、deep-dive 三種不同時間尺度 |
| AI 基礎設施週報 | mtk-ecosystem-deep-dive 保留全球需求、供給、價值分配與競爭視野 |
| TPU 技術深度系列 | tpu-technical，每週五早上 |
| Networking 每週深度長文 | networking-deep-dive，每週三晚上 |
| 分散式系統深度系列 | distributed-systems，每週五晚上 |
| K8s HPC 技術系列 | k8s-hpc，每週四晚上；K082–K129 課程接續 |

## 跨系列 ownership

- SOTA R2G／CAD 擁有公司公開設計方法與平台案例；Agentic radar 擁有新增變化；Agentic deep dive 擁有理念、架構與本週會議研究摘要。
- AI frontier 擁有通用模型／Agent 廣度；LLM Lab 串起可重現全棧課程，TPU 擁有加速器微架構／資料流／compiler mapping 的專門深度。
- Networking 擁有資料路徑與協定；K8s/HPC 擁有 OS、容器與叢集工程；Distributed Systems 擁有完整服務需求、一致性、複寫與故障設計。遵守既有各 roadmap 更細的 ownership。
- 機構晨報擁有假設與預期修正；盤中擁有當時價格／事件；盤後擁有官方價量籌碼與條件日誌；週末研究擁有技術到財務、競爭與估值的完整論點。
- 跨系列消化材料依 repo 與一手來源，不假稱能讀取其他 session。相關主題以既有文章內鏈接續，不能換標題重寫相同內容。

## 遷移驗收

舊相關任務全部 enabled=false 且保留；14 項新版各有唯一 canonical ID、enabled=true、正確週期／Asia/Taipei 與不同於任何舊 session 的新 conversation ID。盤中一天兩次屬同一新版任務。prompt 與本 registry 一致，每個初始化 session 只建立自己的一項任務。所有同名副本、未完成建立、未知 outcome 都要回讀清單核對，不盲目重建。
