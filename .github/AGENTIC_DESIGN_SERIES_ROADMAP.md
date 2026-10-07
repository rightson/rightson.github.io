# Agentic Design：即時變化與架構深掘

先完整讀取最新 `AGENTS.md` 與 `RESEARCH_SCHEDULES.md`。本檔是選題與知識鏈，不是 scheduler 設定。即時雷達每日 06:30；完整架構研究每週二 06:00。兩者共用公開 evidence queue，runtime 必須另行驗證。

## 接續與證據

2026-10-01 使用者核准：IC 設計平台目前只公開以平台架構、工程協作、工具／資料交接、狀態管理、執行恢復或驗收治理為主問題的文章。純 STA／SDC 基礎教材、placement／timing 演算法或單一引擎機制暫不公開；不能只加平台總覽或驗收段落就視為平台文章。封存清單以 `_archive/ic-design-platform/README.md` 為準；封存稿仍算歷史已完成，保留原始 date、categories、series、篇號及查重紀錄，不移回 `_posts/`、不換 slug／日期重發，恢復發布須使用者另行確認。其他六類與十四個系列的研究責任、五個排程器的時程及啟用狀態不變。

- 新 session 先讀近期平台文章及 EDA roadmap，已談過的同一機制不能換標題重寫。
- 每個候選記錄原始日期、版本、具名系統、來源、input／action／artifact／acceptance、成熟度、已有相關文章與新增問題。
- 只有標題或行銷聲明時保留研究缺口；不能推定公司完整內部架構。
- 週二選一個足夠完整且最能補上知識缺口的問題；以下候選不是依日期強制輪替，也不表示已有可發布證據。

## 深掘候選

- [ ] AD001. Design state 與 typed tool interface：RTL／constraint／report 身分與可修改範圍。
- [ ] AD002. Artifact lineage：修改後哪些證據失效、何時能交付下一個階段。
- [ ] AD003. Durable execution：長程工具呼叫、checkpoint、重試、duplicate 與恢復。
- [ ] AD004. Agent memory／skill：驗證成功的經驗如何帶著適用條件重用。
- [ ] AD005. Evaluation：功能、PPA、工程介入、tool budget 與成本的共同 baseline。
- [ ] AD006. Authority／sandbox／policy：授權如何綁定輸出版本與生效邊界。
- [ ] AD007. Spec-to-RTL／verification／physical optimization 的閉環與驗收差異。
- [ ] AD008. 跨廠商 agent integration：狀態匯出、工具介面、治理與自建／採購邊界。

## 週二材料

公開稿有完整背景圖、端到端案例、機制、證據、trade-off、failure recovery。另在本新 session 整合一頁本週研究摘要，含三個判斷、來源、可採取行動與追問；私人公司會議資訊不進公開 repo。

只有 source、build、deploy、正式頁內容均核驗才標完成並補 path／URL／原始日期；其他階段精確記錄，不重新建立同篇。

## 2026-10-07 雷達查核與接續

- 本次指令 commit：`415507e6ee7b7c5bfd83b08d7dd0fe79ac904e36`；執行識別：`agentic-design-radar｜2026-10-07｜09:00 Asia/Taipei`。雲端時程與本檔的早期對照不同，本次不修改 scheduler。
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
