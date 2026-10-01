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
