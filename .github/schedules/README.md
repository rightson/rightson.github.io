# 五個研究排程：指令管理入口

2026-10-01 將既有五個研究排程改為每次從本 repo 讀取指令。這次只遷移指令位置，保留相同 automation ID、啟動時間、時區與啟用狀態，不建立額外任務。

## 在哪裡修改

| 排程器 | Asia/Taipei 時程 | 任務指令 |
| --- | --- | --- |
| R2G／Agentic Design | 每日 06:00 | [r2g-agentic-design](r2g-agentic-design.md) |
| AI 前沿與分享 | 每日 07:30 | [ai-frontier-share](ai-frontier-share.md) |
| 技術課程 | 週三至六 19:00 | [technical-curriculum](technical-curriculum.md) |
| 生態系投資研究 | 平日 05:30／17:30；週日 05:30 | [ecosystem-investment](ecosystem-investment.md) |
| 市場事件觀察 | 平日 10:30／13:30，執行時核對交易日 | [market-events](market-events.md) |

所有任務共用要求修改 [common.md](common.md)；全站寫作、分類、來源、發布與封存規則修改 [AGENTS.md](../../AGENTS.md) 及其指定規格。各系列進度仍保存在原 roadmap。五個任務的完整執行指令為「AGENTS.md＋common.md＋對應任務檔＋本次相關系列補充規格」。

[manifest.json](manifest.json) 保存五個任務的穩定 ID、任務檔路徑、十四個系列分派及回讀雲端的時程對照。它是透明的 runtime snapshot，不會自行建立、啟用或重排雲端任務；目前使用者同意的週期未變。

## 每次啟動如何讀取

1. 雲端 scheduler 觸發既有任務；短 prompt 指定 repo 與固定 group key。
2. 透過已連接的 GitHub 讀 repo metadata、最新 default branch 的 commit SHA。
3. 從該 commit 完整讀取 AGENTS.md、本 README、manifest、common 及任務檔，再讀本次相關分類規格、系列補充規格、roadmap 與進度。不只讀 GitHub 頁面摘要，不依賴會被清除的本地工作目錄。
4. 以原排定觸發日期、星期與 Asia/Taipei 時段選本次分支；重試與延遲仍處理原時段，無法確定就回報缺口。
5. 記錄 instruction commit SHA；讀取失敗、缺檔或內容截斷就停止該次發布並回報，不用舊 prompt 猜做，也不因此停用 recurring task。
6. 寫入前另取得最新 head／blob SHA，保留其他 agent 的文章與進度。初始指令版本的記錄不代表可以用過時 tree 覆寫 main。

## 修改後何時生效

- 改 common 或任務檔並 commit：下一次執行依短 prompt 讀取新版本；已開始的執行保持其啟動時版本。這是本 repo 的讀取約定，不是自動同步服務。
- 改觸發時間或 enabled：需由 ChatGPT scheduler 更新，再回讀並同步 manifest 與 RESEARCH_SCHEDULES.md。僅改 repo 時程不會改變觸發時間。
- 改任務檔路徑、group key 或 repo：同步修改雲端短 prompt 的入口，避免舊路徑失效。一般修改正文不用重新貼完整指令到五個排程器。
- RESEARCH_AUTOMATIONS.json 的十四筆 automations 是系列補充規格；runtime_groups 連到本目錄。五個 group 的時段優先於早期系列 prompt 的舊時段，內容深度、實驗與公開／私人邊界保持原要求。
- 本目錄保存在公開 GitHub repo，但不新增網站選單或文章。只保存公開研究規格與排程對照，不保存私人投資日誌、持倉、公司內部資料或憑證。

## 驗證範圍

遷移驗收：五個任務指令完整拆分、十四個系列各有一個 group owner、遠端檔案回讀、五個雲端 prompt 回讀、ID／schedule／timezone／enabled 不變。這些核對不等同已執行下一次研究，也不為測試入口重複發布文章。

