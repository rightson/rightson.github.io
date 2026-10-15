# Agentic Design：即時變化與架構深掘

先完整讀取最新 `AGENTS.md` 與 `RESEARCH_SCHEDULES.md`。本檔是選題與知識鏈，不是 scheduler 設定。雷達與架構研究各有獨立主題 prompt，共用公開 evidence queue；執行時間由 Codex 管理。

## 接續與證據

2026-10-01 使用者核准：IC 設計平台目前只公開以平台架構、工程協作、工具／資料交接、狀態管理、執行恢復或驗收治理為主問題的文章。純 STA／SDC 基礎教材、placement／timing 演算法或單一引擎機制暫不公開；不能只加平台總覽或驗收段落就視為平台文章。封存清單以 `_archive/ic-design-platform/README.md` 為準；封存稿仍算歷史已完成，保留原始 date、categories、series、篇號及查重紀錄，不移回 `_posts/`、不換 slug／日期重發，恢復發布須使用者另行確認。其他分類與十四個系列的研究責任保持獨立。

- 新 session 先讀近期平台文章及 EDA roadmap，已談過的同一機制不能換標題重寫。
- 每個候選記錄原始日期、版本、具名系統、來源、input／action／artifact／acceptance、成熟度、已有相關文章與新增問題。
- 只有標題或行銷聲明時保留研究缺口；不能推定公司完整內部架構。
- 週二選一個足夠完整且最能補上知識缺口的問題；以下候選不是依日期強制輪替，也不表示已有可發布證據。

## 深掘候選

- [ ] AD001. Design state 與 typed tool interface：RTL／constraint／report 身分與可修改範圍。
- [ ] AD002. Artifact lineage：修改後哪些證據失效、何時能交付下一個階段。
- [ ] AD003. Durable execution：長程工具呼叫、checkpoint、重試、duplicate 與恢復。
- [x] AD004. Agent memory／skill：驗證成功的經驗如何帶著適用條件重用。2026-10-13 完成帶條件診斷 skill、離線回放與可撤回發布的完整研究；真實 LLM／EDA 泛化與多機實驗另列未完成。
- [ ] AD005. Evaluation：功能、PPA、工程介入、tool budget 與成本的共同 baseline。
- [ ] AD006. Authority／sandbox／policy：授權如何綁定輸出版本與生效邊界。
- [ ] AD007. Spec-to-RTL／verification／physical optimization 的閉環與驗收差異。
- [ ] AD008. 跨廠商 agent integration：狀態匯出、工具介面、治理與自建／採購邊界。

## 週二材料

公開稿有完整背景圖、端到端案例、機制、證據、trade-off、failure recovery。另在本新 session 整合一頁本週研究摘要，含三個判斷、來源、可採取行動與追問；私人公司會議資訊不進公開 repo。

只有 source、build、deploy、正式頁內容均核驗才標完成並補 path／URL／原始日期；其他階段精確記錄，不重新建立同篇。

## 2026-10-07 雷達查核與接續

- 本次指令 commit：`415507e6ee7b7c5bfd83b08d7dd0fe79ac904e36`；研究紀錄：`agentic-design-radar｜2026-10-07`。本紀錄不設定 scheduler。
- 同日已有 BTTF 文章，保留原始 date `2026-10-07 06:32:00 +0800`、series 與 permalink，不重複建立：`_posts/2026-10-07-bttf-waveform-sql-agent.md`；[正式頁面](https://rightson.github.io/ic-design-platform/2026/10/07/bttf-waveform-sql-agent.html)。
- 該文章在 `415507e6ee7b7c5bfd83b08d7dd0fe79ac904e36` 的 source 已回讀；[Post lint gate](https://github.com/rightson/rightson.github.io/actions/runs/37541662937) 與 [Pages build/deploy](https://github.com/rightson/rightson.github.io/actions/runs/37541661385) 均 success。正式 HTML 回讀含本次標題、`signal_metadata`、95.33% 與 1.96× 的內容，背景 SVG HTTP 200；完成公開內容核驗。
- [BTTF 原始論文](https://arxiv.org/html/2610.06790)，v1 原始日期 2026-10-05：150-query execution accuracy、資料轉換與查詢延遲屬論文自報結果；本次沒有執行其實驗。該篇為雷達成果，不因此將 AD001–AD008 完整深掘標為完成。
- 本次新增 FormalOS 短報與下方 AD009 候選；Cadence 2026-10-06 ViraStack 活動頁目前只提供功能介紹，未取得新技術材料或量化實驗，不據此推定完整部署架構。

## 新增候選

- [ ] AD009. FormalOS 的 verification plan、工具編排與可選 AI 接入。原始公告：2026-10-06；[LUBIS EDA 發布的公告](https://www.globenewswire.com/news-release/2026/10/06/3375128/0/en/lubis-eda-launches-formalos-infrastructure-for-systematic-scalable-formal-verification.html)；[FormalOS VP Creator 官方擴充套件說明](https://marketplace.visualstudio.com/items?itemName=formalos.vp-creator)。
  - 輸入與操作：驗證目標、requirements、tasks、assertions、milestones；VS Code 擴充套件讀寫團隊 plan，以角色控制、樂觀更新與 reconciliation 同步，離線快取標示 stale。
  - 產物與對應：驗證計畫、任務與 assertion 狀態；`.formalos.map.json` 可把 requirement／assertion 對應到 RTL。公告列出 sign-off evidence，但尚缺可逐項驗證的正式放行 schema。
  - 成熟度：公告稱正於 LUBIS 的 active projects 導入，隨 formal verification engagements 部署於客戶環境。預設不包含、託管或呼叫 AI，由客戶自行選擇接入模型；未取得獨立量化效益。
  - 擴充套件將 proof runner、自動回寫 proof results 與 in-editor triage 列為 roadmap；目前計畫同步功能與未來執行閉環分開研究。
  - 新增問題：與既有 GPT-Synopsys 打包服務相比，拆分方法論／工具編排與模型採購，是否降低替換成本並提高計畫一致性？需補 API／版本語意、proof result 綁定、衝突處理、覆蓋定義與實際案例後，再決定深掘。
## 2026-10-08 雷達查核與接續

- 本次指令 commit：`17cabcb8ad469ffad55dd0c0212bcb2ac499614d`；研究紀錄：`agentic-design-radar｜2026-10-08`。本次只接續每日雷達，不修改 scheduler。
- [Cadence 2026-10-07 的 AI 產物驗證與 signoff 說明](https://community.cadence.com/cadence_blogs_8/b/artificial-intelligence/posts/how-to-verify-and-sign-off-ai-generated-design-data)提供新的供應商一手架構邊界：AI 產出的 RTL、assertion、constraint、ECO 與實作變更是待驗證的 engineering input；核准的 specification、constraint、library、IP 與 signoff criteria 仍是權威來源，mental model 只能由這些來源衍生，不能取代它們。
- 驗收證據仍由 simulation、formal、equivalence、regression、STA、power、physical verification 與 signoff database 產生；模型 confidence 或 explanation 不能代替工程證據。Cadence 另主張 material change 應記錄 request、requirement、design revision、agent／model／tool／configuration、constraint／assumption、產物、後續修改、驗證結果、waiver、approval 與可重跑路徑。
- 執行權限與結果有效性分屬兩層：OpenShell 類 sandbox 限制 agent 能讀寫的檔案、憑證、工具、網路與權限；EDA engine 判斷輸出是否符合設計標準。Cadence 明確區分 autonomous execution 與 final signoff，工程師仍負責 intent、exception 與最後接受。
- 這份資料為 AD001、AD002、AD006、AD007 增加 vendor primary evidence，但沒有公開 machine-readable schema、API／版本語意、獨立客戶案例或量化結果，因此不將任何候選標為完成，也不據此推定 ChipStack 的完整內部實作。
- 與前一日 BTTF 相比，BTTF 補的是 waveform 的可查詢 read path；Cadence 本次補的是 generated change 的 authority、evidence 與 acceptance path。兩者互補，但後者與既有「可驗證的 IC 設計狀態」文章高度重疊，認知增量尚不足以另發公開短評，避免用同一機制重寫新文。


## 2026-10-13 AD004 架構深掘與接續

- 指令 commit：`ea435295cf245518b9a516defba45a3aa93387ad`；單元識別 `AD004`，series `agentic-design-deep-dive`。本文首次建立 date `2026-10-13 06:09:00 +0800`，不改既有文章 metadata。
- 完成文章：[讓 EDA Agent 從失敗案例學習，先把診斷 skill 送進離線回放](https://rightson.github.io/ic-design-platform/2026/10/13/eda-diagnostic-skills-offline-replay.html)；source path `_posts/2026-10-13-eda-diagnostic-skills-offline-replay.md`；文章、三張深淺色 SVG、實驗程式與原始輸出同 commit `2962b880d1dbcd594fe1d3fddd762e0d7e99d651`。
- 原始研究：ACE v1（2025-10-06，本文機制與 AppWorld 表格引用版本；現有 v3 2026-03-29）、GEPA v2（2026-02-14）、Reflexion（2023）；另接續 Cadence 2026-10-07 公開工程責任文件及本系列 BTTF 文章。條件式診斷、EDA 案例與發布流程是參考設計，不宣稱公司內部部署。
- 主要新增：將診斷 skill 的可觀察前提與反例分流、資料與案例組隔離、棄答／覆蓋／錯誤成本、bundle 撤回與受影響 run 追蹤串成完整學習路徑；與既有 typed-state／durable-execution／GDP 稿的成果管理分開。
- 最小實驗已跑：`scripts/experiments/agentic_diagnostic_skill_demo.py`；輸出 `scripts/experiments/agentic_diagnostic_skill_demo.results.json`。3 個正向訓練、3 個開發反例、12 個人工設計測試案例；未使用 LLM、EDA 或 PDK。未篩 scope 為 6 正確／6 錯誤／0 棄答，scope v1 為 6／0／6，反例分流 v2 為 9／0／3；這是合成協定測試，不是統計泛化或模型 benchmark。
- 實驗另核對報告 digest 不符、正常晉升、stale parent 衝突、版本撤回與撤回後拒絕重用；限單程序狀態模型，無分散式儲存／交易保證。
- 發布核驗：[Post lint gate](https://github.com/rightson/rightson.github.io/actions/runs/38315374482) success；[Pages build/deploy](https://github.com/rightson/rightson.github.io/actions/runs/38315373927) success；6 個遠端 source byte-for-byte 相符，正式 HTML 含新標題、`inspect-upstream`、75% 與測試 digest，3 張公開 SVG HTTP 200 且內容相符。正文有效中文字 4,199（排除 code、figures 與尾段）；實際公開正文依 `assets/site.js` 算法為 4,712 CJK／764 non-CJK words，16 分鐘。
- 未完成實驗：真實 tool parser、人工確認根因的公開 flow 失敗集、跨設計／時間／工具版本泛化、LLM 萃取與候選演進、EDA 修正及設計檢查、資料庫交易、多機競爭與 crash durability。後續 AD004 延伸先補其中一項實驗，不換標題重寫相同方法。
- 近七天可回讀的既有相關公開文章為 2026-10-07 BTTF；未找到近七天新增 SOTA 文章。本次會議摘要留在對話，不提交公開 repository，也不推定其他 session 的進度。

## 2026-10-13 雷達查核與接續

- 本次指令 commit：`0226d071fe0020687fa280e1919716420d173508`；研究紀錄：`agentic-design-radar｜2026-10-13`。本紀錄只更新證據佇列，不設定或改動 scheduler。
- [SiliCAD EDA_MCP 2026-10-10 合併的 WorkBoard 修正](https://github.com/SiliCAD/EDA_MCP/commit/84b82e8dc8d135450afb090913805891cd555cf6)與[同日 CommandGuard 修正](https://github.com/SiliCAD/EDA_MCP/commit/f2a840fec7598ab8ee94c50e8640b0b7e855af48)提供一組可檢查的開源工程增量：工作板根目錄依顯式參數、環境變數、MCP roots 與預設目錄解析；呼叫序列化；下載以暫存檔加原子替換；git 失敗不再回報假成功；遠端命令與寫入路徑在執行前經 allowlist、dry-run 與 JSONL audit；SCP 路徑拒絕 shell metacharacter，host key 策略由 `no` 改為 `accept-new`。合併內容含對應的離線單元測試。
- 上述 EDA_MCP 證據接續 AD002、AD003、AD006、AD008：它把 workspace identity、artifact baseline、並行修改、遠端 authority 與稽核放進同一條工具路徑；相較只有 MCP tool schema，新增的是變更前檢查、失敗可見性與可恢復寫入。成熟度仍記為「開源工程預覽」：目前沒有公開 release qualification、獨立安全審查、客戶部署或 PPA／生產效益證據；CommandGuard 自身也不是完整 sandbox，無法判斷被呼叫腳本內部的副作用。
- [TPCS 預印本](https://arxiv.org/abs/2610.13067) v1 原始提交日為 2026-10-09，近期才進入可檢索的新文清單。作者提出以 transaction-based function invocation 與 host control flow 剪除 inactive logic，讓同一中介抽象涵蓋微架構建模、cycle-accurate simulation 與 synthesizable RTL generation。作者自報：SMP workload 相對 parallel Verilator 為 36×–42×、accelerator workload 相對 single-thread Verilator 為 3.4×–7.2×，評估 traces 達 cycle-level waveform agreement；生成 RTL 的 clock period 相對手寫版本為 -4.7% 到 +2.6%，standard-cell area 為 -3.3% 到 +4.0%。
- TPCS 不是 agent 系統，也沒有公開證據顯示已接入 LLM 或 production design flow；以上數字只視為論文 reported result。它先列為 AD001、AD007 的相鄰 substrate 證據：若後續能取得完整介面、design identity、轉譯失敗與 independently reproduced result，才評估是否形成「可執行設計狀態」深掘；不能把更快的 simulation 直接外推成 agent 閉環較可靠。
- 本次沒有新的 EDA 廠商 production deployment、客戶 adoption 或獨立量化效益達到公開短評門檻，因此不建立新文章。下一步分別驗證 EDA_MCP guard 的繞過面與 crash recovery，以及 TPCS 的 benchmark 組成、RTL 子集、生成失敗模式與程式碼可得性；AD001–AD003、AD006–AD008 均不因此標為完成。

## 2026-10-14 雷達查核與接續

- 本次指令 commit：`fb248b4aa7cfe734bef332f11ee20957fa0125e9`；研究紀錄：`agentic-design-radar｜2026-10-14`。本紀錄只更新證據佇列，不設定或改動 scheduler。
- [Cadence 2026-10-13 的 Virtuoso AI Studio／ViraStack 說明](https://community.cadence.com/cadence_blogs_8/b/cic/posts/when-ai-becomes-part-of-your-analog-design-workflow)補上先前活動頁缺少的 analog workflow 細節：由自然語言建立 testbench、產生與修正 SKILL、執行 topology mapping／device scaling／跨製程最佳化；實體設計路徑可由影像提出 floorplan，產生 placement 與 routing 原型，再協調 physical verification、extraction 與 post-layout optimization。
- Cadence 描述的接受責任仍在人：floorplan 先提案、經工程師核准才生成；多個 layout 候選由工程師依面積、open 數與平衡結果選擇；DRC agent 報告並建議修正，工程師決定處理項目；電路行為仍由 simulation 與 verification engine 建立。這為 AD001、AD007 與 AD008 增加了具體的 input／action／artifact／acceptance 路徑，也顯示 agent 層主要協調既有 Virtuoso、Circuit Simulation 與 Pegasus 能力。
- 同一說明自報：具 Virtuoso API 與 design context 的 SKILL 生成相對人工工作提高 95% productivity；6 GHz analog／RF PHY migration flow 縮短 60% design-closure 時間。公開頁面沒有提供樣本數、人工 baseline 定義、製程節點、品質分母、重跑成本、具名客戶或可重現資料，兩項數字只列為 vendor reported result，先接到 AD005 的 evaluation 缺口。
- 成熟度維持「供應商產品材料／development-partner engagement」：Cadence 2026-04-16 的[官方 Super Agent 說明](https://community.cadence.com/cadence_blogs_8/b/artificial-intelligence/posts/reimagining-chip-design-from-spec-to-signoff-with-cadence-ai-super-agents)曾將 ViraStack 列為 early engagements；10 月 13 日新文說明 cloud-enabled、on-premises 與 customer-specific knowledge，但沒有更新 GA 狀態或提出獨立客戶 production deployment。因此不把 demo、早期合作與量產導入混寫。
- 相較 10 月 8 日 Cadence signoff 文件，本次新增的是 analog custom-design 的實際編排粒度與人工核准位置；權威來源、版本綁定、失敗後殘留狀態、回復路徑與跨製程 acceptance schema 仍未公開。下一步驗證兩項 productivity claim 的測量方式、候選 layout 的比較 schema、migration 前後 specification traceability，以及 agent 失敗或工具中斷時如何保存與撤回狀態。AD001、AD005、AD007、AD008 均不因此標為完成。
- 本次沒有第二項同等強度的新 EDA 廠商 production deployment、客戶採用或獨立量化結果；不建立公開短評，避免把單一供應商材料擴寫成部署事實。



## 2026-10-15 雷達查核與接續

- 本次指令 commit：`1763792d9ff19806e5b4c10ff539a9eccae051cf`；研究紀錄：`agentic-design-radar｜2026-10-15`；事件識別 `nvidia-siemens-nemo-gym-liberty-artifact-verifier-20261014`。本紀錄只追加公開證據與待查問題，不設定或改動 scheduler。
- [NVIDIA／Siemens 2026-10-14 技術原文](https://developer.nvidia.com/blog/optimizing-agent-reliability-and-tool-calling-efficiency-for-chip-design-using-nvidia-nemo-gym/)公開 Solido Characterization Suite agent 的具體評估流程。輸入為 SPICE netlist、模型、cell 清單與 PVT 設定；Fuse 透過 MCP servers／skills 接入 coding harness，編排設定、pilot validation、分散式 SPICE、Liberty 產生與比對。NeMo Gym 在固定 task／tools／state／verifier 下從 clean state 收集 rollout，工程師檢視軌跡與診斷後修改 skills、MCP tool descriptions，並簡化重疊的檔案／shell 介面與明定 JSON schema。這是人工參與的 harness／介面調校，原文沒有把本次提升歸因於模型權重更新或 reinforcement learning。
- 新增的工程檢查落在最終 `.lib`：coverage 核對 cell 與 PVT 完整性，validity 核對格式與工具可用性，relative validation 防止新增超出 reference 已有的失敗，accuracy 比較 timing／power 數值的 tolerance，integrity 檢查是否真正產生完整結果而非重用、截短或重排舊值。Reward 為四項二元檢查的乘積，再乘 tolerance 內數值比例；任一二元檢查失敗即為零。這使 missing corner、錯誤 slew threshold 與不完整 cell 能回溯到前段設定，與只檢查 tool-call schema 或 exit code 的做法不同。
- 數字固定為 vendor-reported development benchmark：原始資料範圍為 GF180MCU 的 229 cells／36 PVT corners，但每個調校 run 僅取 **2 cells／36 corners**，約 1.5–2 小時；約 25 個 rollouts，固定 Claude Opus 4.8／Claude Code。原文回報平均 composite verification score 約 55% → 95%，turns 155 → 53，output tokens 約 81K → 29K。95% 不是完整 229-cell library 的通過率，也不是 signoff 成功機率；turn／token 減少不代表整個 characterization wall time 同幅縮短。各輪樣本配置、tolerance 實值、seed、統計區間、獨立 held-out cell／corner 與完整原始 rollout 尚未取得，本次沒有重跑。
- 相較 2026-10-13 AD004 的合成診斷規則與離線回放，這次新增具名 EDA engine、真實 Liberty 產物、reference 比對及防重用檢查，以及固定模型下改善工具介面的實測敘述；沒有解決既有文章列出的跨設計／工具版本泛化、持久化交易、crash recovery 與可撤回發布。主接續 AD005，並補 AD001／AD007；AD004 歷史完成狀態保持，其他候選不標完成。
- 成熟度記為「供應商公開的受控 development benchmark／production-preparation case」，沒有新增獨立客戶 production acceptance 或新 GA 證明。[Siemens 2026-07-26 公告](https://news.siemens.com/en-us/siemens-nvidia-dac-2026/)已提到 NeMo Gym、Solido characterization 與後續 release；本次增量是 verifier 公式、可見錯誤類型、測試子集及調校數字，不重報為新產品發售。該公告的 production-proven results 及速度宣稱不當成這次小子集 benchmark 的獨立驗證。
- 可重現性另查 [NeMo Gym 原始碼](https://github.com/NVIDIA-NeMo/Gym/tree/d5d0188fbbcb79946ac5636e7c16123b2b96a8e6)與 [CVDP README](https://github.com/NVIDIA-NeMo/Gym/blob/d5d0188fbbcb79946ac5636e7c16123b2b96a8e6/resources_servers/cvdp/README.md)。公開 tree 可定位 CVDP server／agent，但未定位本案例的 Solido／Liberty 專屬 verifier、完整 tasks 或 rollout；CVDP 的 RTL test harness 不是本次 characterization scorer。[教學 issue #1705](https://github.com/NVIDIA-NeMo/Gym/issues/1705)為 2026-06-24 建立且仍 open 的舊提案，不列為新完成教學。Demo 影片讀取遭節流，沒有宣稱已觀看；技術原文重試後已可完整讀取。
- 下一步 AD005 優先取得並比較：(1) 固定工具與 reference 版本、明確 tolerance 與負向測試，驗證缺 cell／corner、數值污染與 reference copy 是否能被抓到；(2) 未參與調校的 cell 家族、PVT 與工具版本；(3) skills、MCP 描述及 schema 的分開消融，區分介面改善與反覆看同一測試；(4) 每份合格 Liberty 的 wall time、SPICE／license／token 支出與工程師修改工時。平台導入先建立最終產物 grader 與 trajectory 對應，再擴大 agent 操作，不能僅以回合變少判定可靠性。
- BTTF 10 月 13–14 日媒體轉載重複已發表研究，不另報新成果；SiliCAD EDA_MCP 的 10 月 12 日後 commit 查詢未回傳新項目；Cadence 10 月 13 日 analog workflow 仍依前次紀錄接續。沒有第二項同等強度的新證據，本次採對話短報與候選更新，不建立公開短評，也不宣稱新文章已上線。


## 2026-10-16 雷達查核與接續

- 本次指令 commit：`04b81c91feb734859d26e1a76663fd9e51946419`；研究紀錄：`agentic-design-radar｜2026-10-16`。本次只追加公開來源、成熟度更新與研究問題；保留既有完成狀態，不設定或改動 scheduler。
- 事件識別 `cadence-virtuoso-ai-studio-ic261-production-release-20261014`。[Cadence Release Team 2026-10-14 公告](https://community.cadence.com/cadence_blogs_8/b/cic/posts/virtuoso-ai-studio-ic26-1-now-available)明確稱 Virtuoso AI Studio IC26.1 的 production release 已可從 Cadence Downloads 取得，並將 ViraStack 列入版本介紹。這補上 10 月 14 日紀錄引用 10 月 13 日材料時尚未確認的發售狀態；歷史紀錄保留，現在將基礎產品成熟度更新為「供應商已公告 production release」，不再只沿用早期合作描述。此公告仍未證明每個 agent 功能的授權、平台相容性或具名客戶量產採用；安裝目錄 README、完整支援矩陣與個別功能 entitlement 未取得。
- 同一 release 列出可接續 AD001／AD007／AD008 的具體介面變化：ADE 的 maestro、verifier、setupLib cellviews 改為 binary；DSPF baseline 可供參數探索，最後仍需 extraction／signoff；LVS-based binding 可使用 Calibre 或 Pegasus 的 SVDB。平台工程問題由概念編排進一步落到資料讀取、格式遷移與工具版本相容。下一步核對受支援的匯出／查詢 API、既有 adapter 遷移、DSPF 適用範圍，以及新舊版本下的可重跑性；不以 binary 格式推定已實現加密、權限隔離或完整 lineage。
- 事件識別 `chipagents-build-a-chip-bench-workload-to-gds-evaluation-20261014`。[ChipAgents 10 月 14 日公告](https://chipagents.ai/newsroom/chipagents-nvidia-build-a-chip-bench)及 [NVIDIA 同日公告](https://nvidianews.nvidia.com/news/nvidia-and-semiconductor-leaders-advance-ai-across-chip-design-and-manufacturing-for-ai-defined-labs)確認合作；[技術頁](https://chipagents.ai/research/build-a-chip-bench)公開三個 container 的分工：agent 操作工具、隱藏 VIP 僅供查詢、獨立 grader 持有 reference。功能與乾淨 GDS 先作二元條件，再計 PPA；最佳綜合分數 16.6% 是供應商自報的平均評分，非 tape-out 成功率。各模型使用 OpenCode；live leaderboard 仍列 coming soon，完整 task pack、scorer、固定版本、樣本數與原始 runs 未取得，本次未重現。
- 相較最新 AD004 合成診斷回放與前次 Siemens Liberty scorer，Build-A-Chip-Bench 新增跨 RTL、實體實作與最終 GDS 的共同評量，以及把測試答案與 agent workspace 分離的方法。主接續 AD005／AD007，亦補 AD002／AD003：下一步取得完整評分定義與交集分母，核對功能回歸與 PPA 報告是否綁定同一版提交；再量測慢速工具工作、保留已通過候選及回復較佳版本的成本。案例使用開源工具／PDK，成熟度列「公開方法與初步 vendor-reported benchmark」，不外推先進製程 production signoff 或內部平台部署。
- 去重與缺口：Siemens／NeMo Gym、Cadence 10 月 13 日 analog workflow 及 BTTF 既有成果不重報。SiliCAD EDA_MCP 的 10 月 13 日後 commit 查詢未回傳項目。AI-HDL 預印本原站顯示 v1 為 10 月 9 日，未見二手索引所稱 10 月 15 日更新，因此不當成本次新論文。museRISC 留作未完成的程式／實驗線索，本次未核驗其工具產物，不宣稱製造或實測完成。
- 本次採對話短報與 roadmap 候選更新，不建立新文章，不將 AD001–AD003、AD005–AD009 標為完成；亦未執行新的 EDA／LLM 實驗或進行文章 build／deploy 核驗。
