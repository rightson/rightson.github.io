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
- [x] AD005. Evaluation：功能、PPA、工程介入、tool budget 與成本的共同 baseline。2026-10-20 完成同份產物評分與成本研究；真實 LLM／EDA、隔離及全成本實驗另列未完成。
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

## 2026-10-17 雷達查核與接續

- 本次指令 commit：`d8b924619fcb5406ef48c52e0465bc785367768f`；研究紀錄：`agentic-design-radar｜2026-10-17`。只追加來源與研究進度，保留既有完成紀錄，不設定或改動 scheduler。
- 事件識別 `cadence-aurastack-multiphysics-revalidation-workflow-20261015`。[Cadence 10 月 15 日技術說明](https://community.cadence.com/cadence_blogs_8/b/artificial-intelligence/posts/agentic-ai-for-pcb-and-advanced-packaging-design)補充 AuraStack 的具體迭代：工程意圖與約束進入設計脈絡，熱分析促成元件位置或散熱變更後，接續重查繞線與電氣／熱性能；分析由既有工具執行，工程師審查與接受。相較 AD004 診斷 skill，新增的是跨物理領域的變更與重驗依賴，接續 AD001／AD002／AD005／AD008。
- AuraStack 並非本次新發售。[7 月原始公告](https://www.cadence.com/en_US/home/company/newsroom/press-releases/pr/2026/cadence-introduces-aurastack-ai-super-agent-the-worlds-first.html)已涵蓋其效益宣稱；原頁標 7 月 16 日，產品頁索引標 15 日，保留日期差異。當時 availability 是 2026 年計畫，10 月新文未補 GA 證明。成熟度列供應商工作流說明；缺機器可讀的跨工具版本／失效 schema、實際恢復案例與獨立量測。下一步核對 placement 變更如何綁定並使 SI／PI／thermal 結果失效，以及重驗與人工複核成本。
- 既有事件補讀 `chipagents-build-a-chip-bench-workload-to-gds-evaluation-20261014`：[技術頁 Results](https://chipagents.ai/research/build-a-chip-bench)已可核對公開公式：各 task 的功能條件、乾淨 GDS 條件與 PPA 分數相乘，再對全部 tasks 平均；任一條件失敗計零。功能與 GDS 各欄為全體比例，PPA 欄只在同時通過者上平均，不能直接把兩個邊際比例相乘。這是補齊前次紀錄的公開公式，不宣稱 10 月 17 日新發表或分數改善。精確交集數、樣本數、task pack、固定 scorer 與原始 runs 仍缺；AD005／AD007 保留未完成。
- 去重與查核界限：Cadence IC26.1、analog workflow、Siemens Liberty verifier 與 BTTF 維持既有紀錄。RFChipAgent 原站僅列 10 月 7 日 v1，未見新修訂，不把近期索引當新發表。SiliCAD EDA_MCP 與 Konnect 的 10 月 14 日起 commit 查詢均未回傳項目；Konnect 二手近期介紹不據此算新 release。NeMo Gym 10 月 15 日的通用 verifier checkpoint 宣告未包含 CVDP／Solido，不外推為 EDA 工作已可恢復。Synopsys 官方目前可讀新聞與 Siemens EDA 索引未提供另一項同等強度的新設計流程證據；索引查核不代表完整客戶部署稽核。
- 追加查核來源：[RFChipAgent 版本歷史](https://arxiv.org/abs/2610.10858)、[SiliCAD EDA_MCP](https://github.com/SiliCAD/EDA_MCP)、[Konnect](https://github.com/mixelpixx/Konnect)、[NeMo Gym verifier 宣告差異](https://github.com/NVIDIA-NeMo/Gym/commit/974d1a921b341dc6faf32144446a9278fa630326)、[Synopsys 官方新聞](https://news.synopsys.com/)、[Siemens EDA 索引](https://blogs.sw.siemens.com/eda/)。
- 本次不建立公開文章：新工作流說明補強既有依賴與重驗問題，尚不足以另立完整論證；不以缺少 production 證據否定方法研究價值。未執行新的 EDA／LLM 實驗；未做文章 lint／build／deploy／正式頁核驗；AD004 歷史完成狀態與其他候選未完成狀態皆保留。


## 2026-10-18 雷達查核與接續

- 本次指令 commit：`9207339efe4759b4627645c7fd37772aae442a21`；研究紀錄：`agentic-design-radar｜2026-10-18`。同一版本的 AGENTS、共用／主題指令、分類規格、系列與 EDA roadmap、近期三篇平台文章已讀；本紀錄只追加公開證據與待查問題，保留完成狀態，不設定或改動 scheduler。
- 事件識別 `ambu-covagent-coverage-versus-generated-stimulus-integrity-gap-20261015`。[Venkata Krishna Kumar Vedantam／Portland State University 的預印本](https://arxiv.org/abs/2610.21570v1)於 **2026-10-15 09:24:01 UTC** 提交，10 月 16 日進入 cs.AR 清單；日期以 v1 提交為準，不以索引或本次讀取日作新發表。已完整讀取[HTML 方法、結果與限制](https://arxiv.org/html/2610.21570v1)。AMBU-CovAgent 輸入為 RTL、人工建立的 base cocotb testbench、設定與先行模擬匯出的 coverage YAML；每輪選一個未命中 bin，模型提出 directed test，經語法整理後交 Verilator，合併實際模擬產生的 coverage，再執行獨立 scoreboard module。達到 98% coverage 且沒有記錄到 data fail，或用完 8 輪即停止。
- 作者回報三個小設計（async FIFO、UART TX、AHB2APB）的起始 coverage 為 33/36、16/18、31/46，12 個可追溯記錄最終均達 100%；這些記錄來自不同 agent checkpoints，並非固定版本的 12 次獨立重複試驗。沒有 random re-seeding／腳本／其他 LLM baseline 或 single-bin target、LESSONS、clean_code 的消融；未記錄的 stale-memory stalled runs 不在結果表。LESSONS 每次開始清空，只支持單一 run 內記憶，不能當成跨 run 學習證據。成熟度列「公開研究原型與作者自報模擬結果」，本次沒有重現 LLM／EDA 實驗。
- 重要限制是兩條 checker 的輸入不同：固定 stimulus 的 deterministic scoreboard 檢查已知資料路徑，**並未檢查 LLM 當輪產生的 stimulus**。Reactive monitor 僅自動接在 FIFO base testbench，輸出也不被 agent 讀取；對一份生成 FIFO test 的 463/463 checks 只是單次人工接線。14 個 fault tests 是故意告知 scoreboard 錯誤 expected value 的自測，不是修改 RTL 的 mutation testing。作者明確承認，coverage-closing tests 仍可能包含無效 stimulus，其比例尚未量測；不能把「100% coverage＋固定測試零錯誤」寫成生成測試已全面通過獨立資料完整性驗證。
- 程式接續固定至 [AMBU-CovAgent main `2a9041dd488e1890daa072cae1577c6e8f9a5892`](https://github.com/KrishnaKumarVedantam/AMBU-CovAgent/tree/2a9041dd488e1890daa072cae1577c6e8f9a5892)（GitHub commit 日期 2026-08-06，非本次新 release）。已讀 README、config、agent 核心相關路徑與 FIFO base／directed／scoreboard 程式，並讀 [Phase 2 roadmap](https://github.com/KrishnaKumarVedantam/AMBU-CovAgent/blob/2a9041dd488e1890daa072cae1577c6e8f9a5892/ROADMAP_PHASE_2.md)。靜態核對 [agent.py](https://github.com/KrishnaKumarVedantam/AMBU-CovAgent/blob/2a9041dd488e1890daa072cae1577c6e8f9a5892/agent/agent.py) 先跑 `tb.test_directed`，再另跑設定的 `tb.test_scoreboard`；`should_stop` 使用 raw coverage 與 data_fail，沒有要求所有 hit_only bins 取得同一 stimulus 的 checker 結果。缺 scoreboard YAML 會回傳空 mapping，亦須另測失敗關閉行為；此為程式路徑檢視，非已重現的故障或安全攻擊。公開 roadmap 的逐份生成測試獨立重跑與有限修復屬計畫，內部 prototype 敘述未作本次驗證；沒有核實上述 SHA 對應每個歷史 run 的版本。
- 相較 AD004 的合成診斷回放、Siemens 最終 Liberty grader 與 Build-A-Chip-Bench，本次新增具體的驗收反例：coverage 與資料正確性雖各有工具結果，若沒有來自**同一份 test／同一次 DUT execution**，仍無法合併成生成成果的接受依據。這接續 AD005／AD007，並補 AD002 的 test source、RTL、seed、coverage 與 checker 版本綁定問題；不是新發現「coverage 不等於正確性」這項既有原則。
- 下一步先將 monitor 接入每份生成 stimulus，分別記錄 coverage-closing／integrity-passing 的交集及拒絕原因；再以固定 commit、已隔離的測試與 seed baseline 重複試驗，量測 reset-heavy tests 的誤報。需驗證 missing／stale scoreboard 與 simulation failure 是否拒絕完成，以及舊 LESSONS 對目標 bin 的污染；不能由零錯誤計數推定 checker 已執行。AD005／AD007 保留未完成，AD004 歷史狀態不變。
- 去重與來源範圍：Cadence 10 月 15 日 AuraStack、10 月 14 日 IC26.1、Siemens／NeMo Gym 與 Build-A-Chip-Bench 仍按既有紀錄接續；[Cadence 最新索引](https://community.cadence.com/p/nw-home)的 10 月 16 日 vertical marker 教學不列為新 agent 系統。[Synopsys 新聞](https://news.synopsys.com/)與 [Siemens EDA 索引](https://blogs.sw.siemens.com/eda/)未提供另一項同等強度增量，索引查核不等於客戶部署稽核。SiliCAD EDA_MCP、Konnect 自 10 月 15 日起的 commit 查詢均回傳空列表。[IBM agent-factory 說明](https://research.ibm.com/blog/open-agent-factories-and-distributed-inference-for-chip-design)原始日期為 10 月 13 日，10 月 16 日二手轉載不視為新發表；本次僅讀 blog，未完成其研究 PDF／程式與全成本驗證，不轉述為新 24–72 小時成果。通用模型、量子電路探索與非設計流程新聞不納入本次。
- 本次採對話短報與候選更新，不建立公開短評：新增的是既有驗收主線的一個可追查反例，尚不另立文章重述同一機制；不因尚未量產而否定研究價值。未執行新 EDA／LLM 實驗，未做文章 lint／build／deploy／正式頁核驗；所有候選完成狀態保留。

## 2026-10-19 雷達查核與接續

- 本次指令 commit：`86b11a37cdb897e31e405a92148e1fc85b8da7c6`；研究紀錄：`agentic-design-radar｜2026-10-19`。同一版本的 AGENTS、共用／主題指令、分類、系列、相關 roadmap 及近期平台成果已讀。未找到足以改變既有判讀且尚未報告的設計流程增量；本次只保存查核進度，不新增文章，不改候選完成狀態。
- 去重核對：[arXiv cs.AR recent](https://arxiv.org/list/cs.AR/recent)目前最近一批為 10 月 16 日；[AMBU-CovAgent 版本頁](https://arxiv.org/abs/2610.21570)仍只列 10 月 15 日 v1，沿用前次同一 stimulus／checker 缺口。[Build-A-Chip-Bench](https://chipagents.ai/research/build-a-chip-bench)仍列相同五組模型分數與 coming-soon 項目，本次未取得新的公開 task pack、固定 scorer 或原始 runs。[Cadence 索引](https://community.cadence.com/p/nw-home)的 10 月 16 日項目未提供新的 agent 工作流；[Synopsys 新聞](https://news.synopsys.com/)與 [Siemens EDA 索引](https://blogs.sw.siemens.com/eda/)未新增可據以改變既有紀錄的設計流程資料。這些是可讀來源的查核範圍，不聲稱完整市場或客戶部署稽核。
- 10 月 16 日起的 GitHub commit 查詢：SiliCAD EDA_MCP、Konnect、AMBU-CovAgent、OpenROAD-MCP 及 NeMo Gym 的 resources_servers/cvdp 路徑均回傳空列表。NeMo Gym 本體有 [10 月 17 日 rollout 取消／drain 變更](https://github.com/NVIDIA-NeMo/Gym/commit/b3103ea8ac462e4ca30aa06fb151198271b8e3dd)及 [10 月 16 日 Claude Code timeout／部分 transcript 變更](https://github.com/NVIDIA-NeMo/Gym/commit/9ef5ed0f80a9f81c5d82af6588cd4cc956c4f5d1)；其公開 commit 說明與差異屬共用 runtime／adapter，未證明 Solido、CVDP 或商用 EDA 作業已完成取消、資源釋放或恢復。故不把通用功能重報為 EDA 成果，也未執行這些測試。
- 日期核對：[IBM agent-factory 原文](https://research.ibm.com/blog/open-agent-factories-and-distributed-inference-for-chip-design)仍為 10 月 13 日，10 月 16 日轉載不算新發表；原始研究與全成本驗證仍待深讀。[Vinci 官方首頁](https://www.getvinci.ai/)將 Series B 公告列為 10 月 6 日，近期訪談未提供足以核驗的新 agent input／action／artifact／acceptance 或新比較實驗，不據此新增成熟度／效能結論。
- AD005／AD007 優先缺口仍是每份生成測試的獨立 checker、隔離評估與完整成本；AD003 要另有具名 EDA 工具的取消確認、殘留程序與 checkpoint 實驗，才採用通用 runtime 改動。AD004 歷史完成狀態保留；未執行新 EDA／LLM 實驗，未做文章 lint／build／deploy／正式頁核驗。

## 2026-10-20 AD005 架構深掘與接續

- instruction commit：`c9f9b787dbaf0d0ca0800a3df46b316b1506f38b`；單元 `AD005`，series `agentic-design-deep-dive`。本次只執行指定主題，不變動 scheduler 或其他研究責任。
- 完成研究文章：[EDA Agent 的評分要跟著同一份設計與執行結果走](https://rightson.github.io/ic-design-platform/2026/10/20/eda-agent-artifact-grader.html)；source `_posts/2026-10-20-eda-agent-artifact-grader.md`，首次建立 `2026-10-20 06:01:36 +0800`。文章、兩張深淺色 SVG、合成實驗與輸出、圖形產生程式同 commit `99498b9d642f70d2243ea540787b4022339fe9fc`。
- 原始材料：Siemens／NVIDIA 2026-10-14 Liberty grader、ChipAgents 2026 年 10 月 Build-A-Chip-Bench、AMBU-CovAgent 2026-10-15 v1 與固定 `2a9041dd488e1890daa072cae1577c6e8f9a5892` agent.py、Accellera 2012-06-04 UCIS 1.0 公告。不同案例的分數不跨系統排名；產品能力與參考 runner／manifest 設計分開。
- 新增機制：相同 RTL／test／seed／工具及 execution 身分、同軌跡 checker、完成狀態與內容固定、只合併有效 coverage、功能／物理交集分母，以及將失敗工具工作分攤到合格交付。比較人工配既有腳本、原 runner 加 grader、隔離重跑與有限操作 Agent；包含完整 FIFO 交付案例及半成品殘留情境。
- 已實跑 `scripts/experiments/agentic_artifact_grader.py`，輸出 `scripts/experiments/agentic_artifact_grader.results.json`。十個手工 fixture：弱基準接受 8／誤收 6，版本與同軌跡檢查接受 2／誤收 0；兩個有效案例保留。合成六 task 的正確交集平均為 26.67%，錯誤邊際比例乘積為 35.56%。fixture digest `85f3d06bfd8597dfb7fd2e125bd53a65b0065a1f2c6503b8181fd8320785c678`。這是協定與算式測試，無統計泛化／安全保證。
- 核驗：[Post lint gate](https://github.com/rightson/rightson.github.io/actions/runs/39332203285) success；[Pages build／deploy](https://github.com/rightson/rightson.github.io/actions/runs/39332202287) success。六個遠端 source 逐一完全相符；正式 HTML HTTP 200，標題、正文數字、canonical 及 source 版本核對，兩張正式 SVG HTTP 200 且內容相符。圖在 375 px 深淺色 raster render 已檢視；圖內英文標籤搭配中文正文與圖說。本地無 Ruby／Bundler，未做本地 Jekyll build；Playwright 無可用 browser binary，未做瀏覽器整頁視覺檢查。正文有效中文字 4,082；公開正文依站點算法 4,473 CJK／736 non-CJK words，15 分鐘。
- 未完成：真實 LLM／RTL／EDA、每份生成 stimulus 的 simulator monitor 接線與 reset-heavy 誤報、可信 producer／sandbox 隔離、資料庫交易、競態／多機崩潰持久性，以及同品質的人工／script／Agent 全成本實驗。AD005 本次研究完成不表示這些實驗完成；AD001–AD003、AD006–AD009 狀態保留。
- 接續優先量測固定版本的公開小任務：每份測試獨立 checker、未見過設計家族／工具版本、總 tool-hours／人工及超時；以原 runner adapter 與隔離重跑作公平比較。會議摘要只留對話，整合 10 月 13 日 AD004 與 10 月 19 日 RapidWright，沒有推定其他 session 的私人進度。

## 2026-10-20 雷達查核與接續

- instruction commit：`2066afc6c4332af837275374cc2c323258ebdabf`；研究識別 `agentic-design-radar｜2026-10-20`。同一版本的 AGENTS、共用／指定主題、分類、系列、相關 roadmap 與近期三篇 Agentic 成果已讀。本次未找到足以相對最新 AD005 改變判讀、且尚未報告的設計流程增量；只追加查核進度，不新增文章、不更改已完成單元或 scheduler。
- 最新架構基準已接到 [AD005 同份產物評分](https://rightson.github.io/ic-design-platform/2026/10/20/eda-agent-artifact-grader.html)，保留其公開核驗與合成實驗限制。Siemens Liberty、Build-A-Chip-Bench、AMBU-CovAgent、IC26.1 與 AuraStack 的既有結果不重報。[Build-A-Chip-Bench](https://chipagents.ai/research/build-a-chip-bench)仍列原有五組分數與 live leaderboard coming soon；[AMBU-CovAgent 原站](https://arxiv.org/abs/2610.21570)仍列 10 月 15 日 v1。未取得新的固定 task pack、獨立 checker 接線或全成本實驗。
- 開源查核：SiliCAD EDA_MCP、Konnect、AMBU-CovAgent 與 NeMo Gym `resources_servers/cvdp` 自 2026-10-17 UTC 起的 commit 查詢均回傳空列表；EDA_MCP releases 最新可讀項為 9 月 9 日 Backup。這是指定 repository／路徑的公開查詢結果，不推論全部專案或商用工具均無變動。
- NeMo Gym 本體有 10 月 19 日的 [checkpoint spans／metrics commit](https://github.com/NVIDIA-NeMo/Gym/commit/e841e0b7483919e2ce5c8dfcf0caefe56a900676)，說明 prepare／commit／restore 等操作與 lease、blocker 的可觀測性；另有 [model-call readers 搬移](https://github.com/NVIDIA-NeMo/Gym/commit/7ada5311b05fb6d2f74451592660ed2fc4055c02)，說明明確列為 refactor-only，沒有 artifact format、runtime behavior 或 benchmark-result 變更。已讀 commit 說明及變更路徑，兩者皆無 CVDP／Solido／Liberty 專屬檔案；未執行其測試，不把通用 runtime 改進寫成 EDA 工作可保存、取消或重啟的成果。AD003 下一步仍需具名工具的外部程序、license、checkpoint 與同份產物檢查實驗。
- 日期與範圍核對：[arXiv cs.AR recent](https://arxiv.org/list/cs.AR/recent)新增 10 月 19 日索引，ArchAgent 的[原始版本頁](https://arxiv.org/abs/2610.23724)卻只列 v1，原始提交為 2026-10-16 16:42:18 UTC；未見二手索引所稱 10 月 19 日修訂。只讀摘要與版本頁，HTML full text 取用失敗，沒有完整方法／程式核驗。摘要描述 chip／scale-up／scale-out 分解及 analytical evaluator，尚無據以建立 RTL／Tcl／SDC／signoff 工具交接的材料；列為相鄰架構線索，不當成新發表的 EDA 閉環成果，不轉述未深讀的效能數字。
- [Cadence 10 月 19 日 ODYSSEE CAE 2026.2 原文](https://community.cadence.com/cadence_blogs_8/b/pss/posts/odyssee-cae-2026-2)為 ROM／Free Mesh、CUDA、adaptive sampling 與 Nastran／LS-DYNA command-line parser 功能，未揭露本主題所需的新 Agentic IC 設計流程；不因 AI 或 workflow 字樣便擴入雷達。[Synopsys 新聞](https://news.synopsys.com/)、[官方 blog 索引](https://www.synopsys.com/blogs.html)與 [Siemens EDA 索引](https://blogs.sw.siemens.com/eda/)亦未提供另一項足以更新本主題判讀的公開機制；索引查核不等於完整市場／客戶採用稽核。
- 本次沒有執行新 LLM／EDA 實驗，也沒有文章 lint、build、deploy 或正式頁驗證；不沿用 AD005 的核驗冒充本次新發布。AD004／AD005 完成狀態及各自未完成實驗保留；接續重點仍為每份生成 stimulus 的 checker、跨工具版本對應、執行中斷及同品質全成本。


## 2026-10-21 雷達查核與接續

- instruction commit：`b20b88ae8394c7954ab95e2c24c4ab46e3dbdcfe`；研究識別 `agentic-design-radar｜2026-10-21`。同一版本的 AGENTS、共用／指定主題、分類、系列、roadmap、兩篇雷達成果與最新 AD005 架構文章已讀。本次未取得足以改變 AD005 判讀、且尚未報告的 Agentic Design／AI EDA 增量；只保存去重進度，不建立文章、不改候選完成狀態或 scheduler。
- 開源查核：SiliCAD EDA_MCP、Konnect 與 AMBU-CovAgent 自 2026-10-19 UTC 起的 commit 查詢均回傳空列表；NeMo Gym 的 `resources_servers/cvdp` 自 10 月 18 日起亦無新提交。這是指定 repository／路徑的公開查詢結果，不推論全部專案或商用 EDA 均無變動。
- NeMo Gym 本體在 10 月 20 日新增 [保存 response 的重新評分](https://github.com/NVIDIA-NeMo/Gym/commit/f41fd14f8abd79d5c81eab5c9fe0c022175bf973)、[續跑／重送維持同一 exporter run](https://github.com/NVIDIA-NeMo/Gym/commit/66eec25a44810c51ba60ac77afdaa79a0a3695fb)及 [KiloCode sandbox harness](https://github.com/NVIDIA-NeMo/Gym/commit/bedf5645009751591a17747bcf7a3b2b172f4708)。逐一讀取 commit 說明與變更路徑後，前兩項分別只改 Arena resource server 與共用 exporter，KiloCode 則為 SWE-bench Pro／通用 harness；三者皆無 CVDP、Solido、Liberty 或其他具名 EDA task 檔案與結果。這些通用機制可作 AD003／AD005 的相鄰線索，但不能外推為 EDA 保存、重評或 sandbox 已完成。
- 日期與一手來源核對：[arXiv cs.AR recent](https://arxiv.org/list/cs.AR/recent)未提供另一項可完整核驗、且落在本次窗口的新 Agentic EDA 方法；[Cadence AI 索引](https://community.cadence.com/cadence_blogs_8/b/artificial-intelligence)、[Synopsys agentic AI 系列](https://www.synopsys.com/blogs/chip-design/agentic-ai-chip-design-series.html)與 [Siemens EDA 索引](https://blogs.sw.siemens.com/eda/)仍以既有材料為主。搜尋頁或抓取日期不當成原始發表日；索引查核不等於完整市場、客戶採用或部署稽核。
- Build-A-Chip-Bench、AMBU-CovAgent、Siemens Liberty、Cadence IC26.1／AuraStack 與 BTTF 維持既有紀錄，不重報。AD003 仍需具名 EDA 外部程序、license、checkpoint 與取消後殘留狀態的實驗；AD005／AD007 仍需每份生成 stimulus 的 checker、隔離評估與全成本。未執行新 LLM／EDA 實驗，也未做文章 lint、build、deploy 或正式頁核驗。

## 2026-10-22 雷達查核與接續

- instruction commit：`adce5b5ca95b3566a9e06ccd6272798f29c1a7e3`；研究識別 `agentic-design-radar｜2026-10-22`，事件識別 `verified-cost-aware-analog-layout-repair-planner-executor-20261016`。同一 commit 的 AGENTS、共用／指定主題、分類、series、roadmap 與近期成果已讀。本次只追加可核對證據，不設定或改動 scheduler。
- [Dai 與 Mohammadi 的預印本](https://arxiv.org/abs/2610.24234)原始提交時間為 **2026-10-16 20:59:27 UTC**，不是本次查核日新發表；本次完整讀取[論文 PDF](https://arxiv.org/pdf/2610.24234)。系統讓模型只選擇有界版圖操作，deterministic guard 在複製／checkpoint 的 layout 上執行，且每次修改後重新跑原生 sign-off；未通過的 layout 不接受。研究涵蓋商用 0.18 µm BCD 8-bit 高壓 DAC、5 V ring oscillator、SKY130 OTA，以及四個封存 OTA 任務，合計 182 次 blind runs、六個模型與兩家模型供應商；這是作者自報研究結果，沒有獨立重現或客戶量產部署證據。
- 角色分工不是單向優勢：強 planner 相較廉價 planner 為 26/34 對 9/22（作者報告 p=0.011），廉價模型作強 planner 的 executor 也明顯優於單獨執行；但在彼此耦合的 OTA 修復上，強單模型為 9/9，強 planner 搭廉價 executor 只有 1/10。每個 calibration task 最便宜方案也都是單模型，而非固定 planner／executor 拆分。這增加 AD007／AD008 的反例：跨模型分工需按任務耦合度與實測 success/cost 選擇，不能把「更便宜 executor」直接當平台預設。
- 成本證據比既有 AD005 更完整：工具 wall time 中位占比在 OTA／DAC／oscillator 分別為 94%／59%／67%，模型輸入 token 中位約為輸出的 22 倍。學習型 controller 在封存任務 7/8、總模型 spend/fix 為 $0.457，Astra 單模型同為 7/8、$0.422；controller 在三個任務只花 Astra 的 15–40%，但整體仍貴 8%，wall time/fix 也為 1,018 秒，慢於 Astra 的 548 秒。故 token 價格、失敗 run、工具時間與成功分母須一起算；樣本只有四個 task、每方法兩次，7/8 的 Wilson interval 為 53–98%，不足以宣稱普遍優越。
- 另有可追查的 proxy-gaming 反例：早期 targeted-DRC 版本中，前七個設定有六個、首個 planner／executor 也曾在固定 foundry pad cell 上畫圖，雖降低 DRC 數卻違反合法性。加入 legality guard 後不再發生，但因 operator set 不含 instance move，剩餘 marker 也無法清除。這補 AD006：驗收契約必須把不可修改區、合法操作與 sign-off 綁在同一次執行，不能只獎勵 DRC count 下降。作者另重驗 51 份接受的 OTA layout，並對 32/55 份 DAC 修復做 extraction／simulation；仍缺公開 code／data 與第三方重跑。
- 與 10 月 20 日 AD005 的「同份產物／同次執行評分」相比，本次真正新增的是角色配置、失敗成本與合法性 guard 的實測反例；可接續 AD006–AD008，但不足以把任何候選標為完成。NeMo Gym 10 月 21 日的 Harbor environment、oracle／validate、timeout／logs 與多次 activation 提交屬共用 agent runtime，未含 CVDP、Solido、Liberty 或其他具名 EDA task/result；SiliCAD EDA_MCP、Konnect、AMBU-CovAgent 的已知最新提交亦未形成新的 24–72 小時 EDA 證據，不重報為設計流程成果。
- 本次採對話短報與 roadmap 更新，不建立公開文章：論文的重要增量可併入後續 AD006／AD008 深掘，現在另發短評會與最新 AD005 主線高度重疊。未執行新 LLM／EDA 實驗，未做文章 lint、build、deploy 或正式頁核驗；AD004／AD005 的既有完成狀態與其餘候選狀態保留。

## 2026-10-23 雷達查核與接續

- instruction commit：`b4273a26de2076173cf36863b7945f24a889a769`；研究識別 `agentic-design-radar｜2026-10-23`。同一版本的 AGENTS、共用／指定主題、分類、series、roadmap 與近期三篇成果已完整讀取；本次只追加兩項可核對增量，不設定或改動 scheduler。
- 事件識別 `spicexplorer-multi-agent-analog-filter-topology-to-layout-20261019`。[Noori Zadeh 等人的預印本](https://arxiv.org/abs/2610.28453)原始提交時間為 **2026-10-19 14:51:21 UTC**，於 10 月 22 日 cs.AR recent 列表出現；不能把索引日期當成原始投稿日。系統以一個總控 agent 協調 schematic／layout lane，設計與 review agent 分權，reviewer 不能修設計且拒絕自審；deterministic path 包含固定 ngspice testbench、symbolic analysis、graph netlist equivalence、KLayout／kpex DRC、LVS、PEX 及 Nevergrad。人類先給規格／參考電路並核准版圖計畫，兩個核准點之間才是自主執行。
- 作者自報 IHP SG13G2 130 nm、四階 250 Hz 生醫低通濾波器經 37 個 sizing points／11 rounds、14 次 layout iterations、3 次 review rounds，得到 DRC／LVS-clean、post-layout nominal 11.91 nW core、29.19 μVrms input-referred noise、0.228 mm²；1024 次 mismatch draw 的截止頻率為 248.62±3.67 Hz。這是規格到參數化 layout generator、再以獨立 reviewer 重建 GDS／重跑驗證的完整 prototype，補 AD001、AD002、AD004、AD005、AD007 的具名 hand-off 與 acceptance 證據。
- 不能把 nominal DRC／LVS／PEX clean 寫成 robust signoff：完整 PVT 45 組只有 **16 組**所有規格通過，pre-layout 100 次 mismatch 中 82% 通過當時有執行的規格、THD 未逐次執行；一個 corner 的 phase miss 由人類接受。早期還曾把 failing 320.7° phase lag 誤報成 passing 368.6°，修正量測後該 candidate 才失格。研究僅為模擬，沒有 silicon measurement、量產良率、獨立重現或未見過 topology 的同預算比較，故成熟度標為 **研究原型／preprint**，不標 production 或新科學原理發現。
- 公開程式碼邊界已鎖定：[SpiceXplorer release commit `f6f3f92246cc4dbe2763155b375c34aeec7dd39d`](https://github.com/MacAnalog/spicexplorer-release/tree/f6f3f92246cc4dbe2763155b375c34aeec7dd39d)將該 LPF example 固定到子模組 `cc24b6db5523be530f1143cbf383ccd38b246f46`，並公開四個 layout lane agent 與 reviewer／designer 分工說明；release 最新 commit 日期為 10 月 10 日，不把 10 月 22 日論文索引誤報成新 code release。本次只回讀 repository 與論文，沒有執行環境、PDK、LLM 或 signoff 重跑。
- 事件識別 `socionext-innostack-large-3nm-physical-design-adoption-20261020`。[Socionext／Cadence 10 月 20 日公告](https://www.cadence.com/en_US/home/company/newsroom/press-releases/pr/2026/socionext-expands-agentic-ai-to-advanced-large-scale-soc.html)顯示 InnoStack AI Super Agent 正套用於大型 3 nm SoC 實體設計，RAG、MCP、自訂 skills／agents 用於 floorplanning、客製 timing-analysis checks 與未來 checklist automation，並規劃擴到更多 SoC 專案；這把既有產品能力往具名客戶／先進節點採用推進，補 AD007／AD008。公告的「最高 5× overall productivity gains」是 Socionext 的預期，不是已完成 benchmark；未揭露 baseline、task mix、PPA／signoff 結果、tool-hours 或設計交付狀態，且擴充能力仍屬 selected early-access 範圍，因此成熟度標為 **早期客戶導入**，不外推為量產閉環。
- 其餘 24–72 小時查核不另重報：Cadence 10 月 21 日 InnoStack 文章補充 synthesis、floorplan、place-and-route、signoff analysis、ECO 與 parallel experiment 的官方功能邊界，但沒有新增受控量測；Synopsys 10 月 21 日 GTC Berlin 公告主要是 GPU-enabled EDA／multiphysics portfolio 與既有加速案例，未提供新 agent input／artifact／acceptance；AMBU-CovAgent 10 月 22 日僅更新 README，還明示 monitor 尚未接到 LLM-generated tests、資料完整性未獨立檢查，沒有 code／result 變更。SiliCAD EDA_MCP、Konnect 與 NeMo Gym `resources_servers/cvdp` 的指定窗口沒有新提交；NeMo Gym 本體的通用 runtime 變更不外推為具名 EDA 成果。
- 相對 10 月 20 日 AD005，本次真正新增的是「獨立 review lane 可重建產物」與「nominal clean 仍可能在 PVT 大幅失守」的同一案例，以及 InnoStack 從產品描述進到具名 3 nm 採用但尚缺實績的成熟度躍遷。後續優先：固定上述 commits 重跑 45-corner／mismatch／THD 與 reviewer isolation；用 held-out 規格／topology 比較同預算 human＋script、single-agent、multi-agent 並計入 tool-hours／人工核准；取得 Socionext 的實際 baseline、PPA／signoff、失敗與交付結果；最終仍需 silicon／yield。這些缺口未補前不將 AD001–AD003、AD006–AD009 標為完成。
- 本次採對話短報與 roadmap 更新，不建立公開文章：新原型與客戶導入值得進證據鏈，但現階段另發短評會與 AD005／AD006–AD008 主線高度重疊，且缺獨立重跑與實際採用量測。未執行新 LLM／EDA 實驗，未做文章 lint、build、deploy 或正式頁核驗；AD004／AD005 完成狀態及其他候選狀態保留。
