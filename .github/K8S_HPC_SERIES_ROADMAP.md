# Kubernetes：從執行模型到平台工程

2026-10-01 使用者核准：OS 與資工先備直接沿用，Kubernetes 從零學習。公開分類「系統與平台」，domain `platform-engineering`，series 延續 `k8s-hpc`。每週四 Asia/Taipei 19:00 由既有「技術課程」分支啟動，不新增或重排雲端任務。

## 課程與教材來源

- 完整課程、依賴與實驗方向：[rightson/k8s-lab/docs/learning-plan.md](https://github.com/rightson/k8s-lab/blob/main/docs/learning-plan.md)。40 核心＋8 AI／HPC／EDA 進階單元。
- 教材標準：[lesson-standard.md](https://github.com/rightson/k8s-lab/blob/main/docs/lesson-standard.md)；驗證進度：[learning-progress.json](https://github.com/rightson/k8s-lab/blob/main/docs/learning-progress.json)。
- 所有輔助教材、練習、解答、manifest、程式、實驗與 raw output 放 `rightson/k8s-lab`。網站 repo 只保存公開完整文章及其圖檔、發布／排程入口和歷史文章封存。
- 每次另讀 k8s-lab 最新 default branch metadata、完整 AGENTS.md、README、上述三檔與相關教材；記錄兩個 repo instruction commit SHA。必需規則讀取失敗停止該次發布，保留 recurring task。

## 接續與穩定身分

**下一單元 K082（課程 01）尚未開始。** 從兩副本 API 服務建立控制平面／節點與 Pod／Deployment／Service 全局模型；不先開 OS 基礎篇，也不假設讀者已熟悉 K8s。

舊 #001–#006 與 K001–K081 保留歷史 ID，新課程使用 K082–K129；文章 series_order 使用 82–129，課程單元 01–48 只代表學習順序。舊 K001 曾發布並核驗成功，現已依使用者要求封存，不算新課程完成；原完成紀錄見 [歷史 roadmap](https://github.com/rightson/k8s-lab/blob/main/archive/roadmaps/2026-10-01-k001-k081.md) 與 [_archive/k8s-hpc/README.md](../_archive/k8s-hpc/README.md)。不恢復舊稿、不換 slug／日期重發。

## 階段索引

| 階段 | 穩定 ID | 範圍 |
| --- | --- | --- |
| 01 | K082–K085 | 建立 Kubernetes 全局模型 |
| 02 | K086–K089 | 追蹤一次部署如何真正執行 |
| 03 | K090–K093 | 控制迴路與平台擴充 |
| 04 | K094–K097 | 節點資源與 Linux 效能 |
| 05 | K098–K101 | 網路資料路徑與除錯 |
| 06 | K102–K105 | 儲存與有狀態應用 |
| 07 | K106–K109 | 排程、擴縮與容量管理 |
| 08 | K110–K113 | 安全與多租戶 |
| 09 | K114–K117 | 交付與叢集生命週期 |
| 10 | K118–K121 | 可靠性與完整平台設計 |
| 11 | K122–K125 | AI／HPC 工作負載工程 |
| 12 | K126–K129 | EDA 與混合運算平台 |

## 教學與發布驗收

OS 名詞按需簡短銜接；K8s 新概念先建立問題與最小模型，再進入原始碼、機制、案例、失敗恢復、量化與取捨。完整長文遵守最新網站 AGENTS.md 的至少約 10 分鐘深度、端到端案例、至少兩個機制、故障／恢復、兩個合理替代方案及圖解要求，依既有 reading-time 驗證。公開正文不寫私人背景或幕後流程。

新文章單一 domain/categories 為 platform-engineering，series k8s-hpc；date 是首次實際寫入時間，固定署名依共用 template。每次核對最近20篇標題與description、最新head和blob SHA，保留他人變更、不force-push。

先提交並回讀 k8s-lab 教材與實驗證據，再提交網站文章及圖檔；兩個 repo 分開核驗並記錄階段。只有必要實驗成立、source 回讀、網站 build/deploy 與正式正文／圖檔核驗完成，才在 lab ledger 標記 complete 並接續下一單元。無硬體、行情或權限時記錄受影響部分，不捏造結果。

使用「系列＋排定日期＋時段」核對 lab execution ledger。`k8s-hpc｜2026-10-01｜19:00 Asia/Taipei` 已有 K001 歷史成果，封存不撤銷該次完成，不在相同時段重發新版文章。
