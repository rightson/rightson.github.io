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

