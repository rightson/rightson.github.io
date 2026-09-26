# IC 設計平台系列：公開證據與 R2G 主線

本文件是 AI EDA 技術雷達的編輯路線。每次仍先讀最新 `AGENTS.md`、出版佇列和近期文章。選題以 Qualcomm、NVIDIA、AMD、Marvell **公開揭露的晶片設計方法、工具或實際導入案例**為主角；論文原始發表年份照實標示。這是選題佇列，不代表這些公司有一套已公開的完整內部 control plane。

## 系列要回答的問題

從 IP／SoC 配置與整合、RTL／驗證、synthesis 與 constraints、placement／routing、STA／signoff 到 R2G 交付，逐篇追問：一個階段接受什麼 design state，誰可改哪些變數，產生什麼 artifact，哪份工具證據允許移交下一階段，失敗後如何辨識及恢復。AI、agent、分散式執行與治理，只在有直接工程作用與公開證據時展開；不能代替公司設計流程本身。

每篇選一個具名系統或具體案例，至少能以公開原文定位 input、決策／演算法、輸出、驗證與界限。優先原始論文、公司／EDA 供應商技術演講與工程文件、官方程式碼。只有發表標題、產品行銷文字或徵才敘述，不足以捏造介面、演算法、內部規模與投產狀態。開源專案可以做可重現的對照實驗，不能單獨成為本系列每日長文的主角。新 commit 可補充原有案例，不以「今天有程式變動」決定題目。

## 已有文章：先查重

- [NVIDIA AutoDMP：巨集佈局探索接回 R2G](/eda/2026/09/24/nvidia-autodmp-r2g-design-platform.html)：2023 年研究，已處理 PreDP、DEF 候選、PostDP／PPA。後續不可換說法重寫。
- [Qualcomm FunCovr.ai／Bedrock 的驗證閉環](/eda/2026/09/24/qualcomm-cad-ai-verification-bedrock.html)：公開線索的證據邊界已說明；Bedrock 與 FunCovr.ai 的內部整合未被證實。
- 2026-09-26 的 ORAssistant 是既有文章，不作本系列之後的選題模板。

上方連結僅供選題查重；正式 URL 應依現行站點 permalink 與公開頁核對。

## 候選章節，依證據成熟度選擇，不按新聞日期輪替

- [ ] **NVIDIA C3PO：全域 placement 的 timing、routability 與 wirelength 同時最佳化。** 由 [NVIDIA EDA 研究群出版清單](https://research.nvidia.com/labs/electronic-design-automation/)找到 2026 ASP-DAC 原文；深入 objective、資料結構、候選如何送往後段工具驗證，和既有 AutoDMP 的 macro placement 比較時須有新機制，勿重複敘事。若原文不足，轉下一題。
- [ ] **NVIDIA INSTA／LEGO-Size：placement 後的快速 STA 與 signoff-accurate sizing 回饋。** 同一[研究清單](https://research.nvidia.com/labs/electronic-design-automation/)列 2025 DAC／ISPD 論文和部分程式碼；拆解 timing approximation 對工具呼叫、gate sizing 與 signoff 的責任邊界。選其中一個具體系統，不合併成無法驗證的「NVIDIA 全平台」。
- [ ] **Marvell 3D chiplet 驗證或實體 signoff：跨 die／interposer 的交付條件。** [Marvell DAC 2026 官方議程](https://www.marvell.com/company/events/dac-2026.html)列 SIP flow、TSV／interposer／ESD signoff、3Dblox 產生和早期 DEF power grid shorts 分析。這些目前只是報告標題；須先取得完整簡報／技術資料，證實 input、規則、產物及案例，才可各自成篇。不能把多個報告拼成其內部平台。
- [ ] **AMD 的 AI 驗證回歸：coverage 等效條件下的測試集合與資源。** [Synopsys 對 AMD 的公開案例](https://www.synopsys.com/zh-tw/taiwan/blog/amd-tests-snps-verification-tool.html)可作線索，須追到原始簡報、實驗條件及工具介面；與 Qualcomm 文章相比，新增價值必須落在 regression selection、fault evidence／成本等不同機制。只見數倍改善的宣傳數字不足以成篇。
- [ ] **Qualcomm 後續 R2G 案例：constraint、IP 整合或實體實作。** 只有找到具名公開報告、足夠方法和資料流，才能立題。已有 FunCovr.ai／Bedrock 文章，不能再用同一三組來源改寫。
- [ ] **AMD／Marvell 的 IP／SoC configuration 與 integration。** 優先能核實 design intent → generated RTL／constraints → verification → physical handoff 的技術文件。產品架構、chiplet 規格和客戶方案介紹不能充當設計平台資料；來源不足就暫留佇列。

章節可依公開原文充分程度調序。每次先選最能補上 R2G 因果鏈缺口、且未重複的案例；不要為平均分配公司名稱而寫低證據密度文章。若當日沒有合格素材，在對話說明研究結果與缺口，不發湊數文章，也不改寫既有日期／permalink。每篇結尾指出此系統與前一篇的實際 artifact／constraint／證據交接，及下一個尚未解的工程問題。

## 發布時更新

成功提交並驗證正式頁後，才把對應方框標為完成，補文章 repo path、原始日期與可驗證的正式連結。發現來源不足則保留未完成，註記缺口；不可把題目標題當已證實能力。每日僅一篇，先核對 `.github/EDA_PUBLICATION_QUEUE.md` 與當日其他 agent 的工作。
