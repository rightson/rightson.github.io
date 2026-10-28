# Networking 研究與深度接續

series: networking-deep-dive，domain/categories: networking。每次先讀最新 AGENTS.md、RESEARCH_SCHEDULES.md 與最近同 domain 文章；本檔是選材規格，不代表 scheduler 狀態。

從頂尖國際會議原始論文、官方規格與實際工程證據選一個能補上知識缺口的問題。經典原理與 AI network 前沿交錯，必要先備用最小模型建立，不靠術語密度。維持 workload／topology／data path／bottleneck→mechanism→quantitative evidence→trade-off／failure／deployment 的完整理解。

## 長期主題

- Queue、congestion、flow control、fairness 與可量化負載模型。
- TCP、RDMA/RoCE、NIC/switch 資料路徑與 offload 的控制責任。
- Collective、scale-up／scale-out、topology mapping 與 workload coupling。
- Optical、CPO、OCS 與電氣／光學轉換及重配置成本。
- Fault detection、retry、recovery 與有效服務／算力。
- 學術方法如何跨越實驗假設、真實工作負載與部署限制。

最近已存在 CSIG、STORM、NVLink 6、UALink 2.0、collective/optical reconfiguration 等文章，寫作前直接回讀。新題須有不同機制、新證據或完整新推導，不改名重發。跨層章節與 TPU／K8s／DS ownership 依相關 roadmap 分工。

候選記錄論文／規格原始日期、來源、主要新問題、先備、相關文章與缺口。正式完成狀態依 AGENTS.md 的 source、build、deploy、public content 驗收，不用出版列表冒充實測。

## 已核驗完成記錄

### RoCE 的 PFC／ECN 回饋延遲與 buffer 預算

- 文章：[RoCE 用 PFC 接住在途資料，用 ECN 降低持續進入的流量](https://rightson.github.io/networking/2026/10/14/roce-pfc-ecn-feedback-buffer-budget.html)。
- 原稿：`_posts/2026-10-14-roce-pfc-ecn-feedback-buffer-budget.md`；series／domain：networking-deep-dive／networking。
- Instruction commit：`c67427ebf0bd745ed9bd03bf3b27c7e9b2146e58`；文章、四張 SVG、試算程式與結果同 commit：`fd3d9e3b695f41afd7ef569f46ae6ddbbf4950e2`。
- 原始依據：IEEE 802.1Qbb；RFC 3168（2001）；DCQCN（SIGCOMM 2015）；Microsoft RoCE 部署（SIGCOMM 2016）；IRN（SIGCOMM 2018、2018-06-21 extended version）；Cumulus Linux 5.17 定點文件；SONiC watchdog 文件與固定版本 CLI。
- 新增理解：兩種控制延遲的資料量、ingress PG／egress queue 的不同計帳、同步 headroom 需求、同優先級共同等待與持續暫停的處置成本；未重寫 CSIG／STORM 的訊號或排序機制。
- 量化階段：已執行 `scripts/experiments/roce_feedback_budget.py`，結果在相鄰 `.results.json`；首次反應的解析峰值與獨立離散守恆核對通過。這是指定假設的流體算例，未執行 DCQCN／IRN artifact、packet simulation 或實體 RNIC／switch 實驗。
- 靜態檢查：本地文章 lint 通過；GitHub Post lint gate run 38556118042 成功；四張 SVG XML、引用路徑、深淺色及 390 px 渲染已檢查。
- Source：七個新增檔案依文章 commit 完整回讀，內容及 blob SHA 相符。
- Build／deploy：GitHub Pages run [38556116858](https://github.com/rightson/rightson.github.io/actions/runs/38556116858) 對應上述文章 commit，建置與部署成功。
- Public content：2026-10-14 19:24:06 +0800 核對正式頁面標題、正文、數值與 Liquid 連結；四張公開 SVG 與提交檔案逐 byte 相符。正式 article text 依現行 site.js（CJK／400＋其他詞／220，向上取整）為約 19 分鐘。
- 歷史文章未修改日期、URL、分類或篇號。本條僅記錄本次已成立的發布與算例階段。

## 已核驗完成記錄

### IRN 讓失序封包先落地，補齊缺口後才宣告 RDMA 完成

- 文章：[IRN 讓失序封包先落地，補齊缺口後才宣告 RDMA 完成](https://rightson.github.io/networking/2026/10/21/irn-selective-retransmission-rdma-completion.html)。
- 原稿：`_posts/2026-10-21-irn-selective-retransmission-rdma-completion.md`；series／domain：networking-deep-dive／networking。
- Instruction commit：`832e329b3f352868b8079106bc3f97e206939726`；文章、四張 SVG、試算程式與結果同 commit：`bded9a7fe2f627e1708006dae41135870d96a320`。
- 原始依據：IRN extended paper（2018-06-21，SIGCOMM 2018）；RFC 5040／5041；DCQCN（SIGCOMM 2015）。
- 新增理解：累積 ACK／SACK bitmap／recovery sequence 的修補路徑，BDP-FC 對 queue 與 bitmap 的雙重上限，Write／Read／Send／Atomic 的 OOO placement 與 completion gating，以及 tail packet 先到時仍不可交付 CQE 的條件。
- 量化階段：已執行 `scripts/experiments/irn_selective_retransmission.py`，結果在相鄰 `.results.json`；64 包、PSN 7／29 遺失的固定案例中，go-back-N 總傳送 121 包，選擇性重傳 66 包；12 包 completion 案例到 PSN 2 補洞後才可見。這是 deterministic packet accounting 與 BDP 公式，不是 network simulation、RTL 或實體 RNIC 實驗。
- 靜態檢查：本地文章 lint 通過；GitHub Post lint gate run [39590115212](https://github.com/rightson/rightson.github.io/actions/runs/39590115212) 成功；四張 SVG 的 XML、引用路徑、深淺色、日期簽名及正式頁面載入均通過。
- Source：七個新增檔案依文章 commit 完整回讀，blob SHA 全部相符。
- Build／deploy：GitHub Pages run [39590115159](https://github.com/rightson/rightson.github.io/actions/runs/39590115159) 對應上述文章 commit，建置與部署成功。
- Public content：2026-10-21 19:13:05 +0800 以正式頁面核對標題、正文、121→66 包數值、證據範圍、內部連結與四張公開 SVG；現行 site.js 顯示約 12 分鐘閱讀。
- 歷史文章未修改日期、URL、分類或篇號。本條僅記錄已成立的發布與算例階段。

## 已核驗完成記錄

### Eunomia 讓 RDMA 用動態 bitmap 承受常態多路徑失序

- 文章：[Eunomia 讓 RDMA 用動態 bitmap 承受常態多路徑失序](https://rightson.github.io/networking/2026/10/28/eunomia-dynamic-bitmap-rdma-reordering.html)。
- 原稿：`_posts/2026-10-28-eunomia-dynamic-bitmap-rdma-reordering.md`；series／domain：networking-deep-dive／networking。
- Instruction commit：`280232b80671ae343c374717e2e796ecd4d29c88`；文章、四張 SVG、試算程式與結果同 commit：`14920be23f98005d83a4a594c71c1eb130217f89`。
- 原始依據：Eunomia preprint（2024-12-11）與 APNet 2025 官方議程；MP-RDMA（NSDI 2018）；ConWeave（SIGCOMM 2023）；IRN extended paper（2018-06-21）。
- 新增理解：Hybrid Dynamic bitmap 以 circular／linear 區段避免擴張時重排舊 bits；第一個 OOO packet 才配置 48-byte metadata 與 2-byte blocks；ACK／SACK ordering feedback 與 DCQCN 分工；SEND／RECV completion gating 與 WRITE 末包增加一個 RTT；allocator exhaustion、QP generation、metadata 更新順序及 fallback 故障路徑。
- 量化階段：已執行 `scripts/experiments/eunomia_bitmap_budget.py`，結果在相鄰 `.results.json`。一百萬 QP、64-bit active bitmap 的明示假設下，固定配置 41 MB；動態配置在 5%／20%／60%／100% active ratio 為 6.8／15.2／37.6／60 MB，交會點約 66.1%。這是 deterministic memory accounting，不是論文量測、RTL synthesis 或實體 RNIC 實驗。
- 靜態檢查：本地文章 lint 通過；GitHub Post lint gate run [40677952843](https://github.com/rightson/rightson.github.io/actions/runs/40677952843) 成功；四張 SVG 的 XML、深淺色、日期簽名與正式頁面載入均通過。本地環境沒有 Bundler／Jekyll 執行器，因此未宣稱本地 build。
- Source：七個新增檔案依文章 commit 完整回讀，內容及 blob SHA 全部相符。
- Build／deploy：GitHub Pages run [40677951913](https://github.com/rightson/rightson.github.io/actions/runs/40677951913) 對應文章 commit，建置與部署成功。
- Public content：2026-10-28 19:12:44 +0800 以正式頁面核對標題、15 分鐘閱讀時間、正文、66.1% 交會點、證據範圍、內部連結與四張公開 SVG；四張圖均完成載入且有非零 natural dimensions。
- 歷史文章未修改日期、URL、分類或篇號。本條僅記錄已成立的發布、算例與公開驗收階段。

## 接續候選

### Commodity RNIC 如何用 in-network support 承受 packet spraying

- 原始日期／來源：2025-08-07，APNet 2025 Reinventing RDMA session 的〈Enabling Packet Spraying over Commodity RNICs with In-Network Support〉。
- 主要問題：若不能修改 RNIC，交換器要保存哪些失序資訊、在何處恢復順序，才能讓 packet spraying 不觸發 commodity RNIC 的 go-back-N。
- 先備：Eunomia 的 endpoint bitmap／completion gate、ConWeave 的目的 ToR reorder state、IRN 的 fixed BDP bitmap。
- 相關文章：本次 Eunomia 長文、IRN selective retransmission、RoCE PFC／ECN、ConWeave。
- 尚缺：交換器資料路徑與 state lifecycle 的逐步推導；buffer／ACK／failure 成本；與 endpoint reorder、flowlet switching 及現代 RNIC context cache 的量化比較。當前僅完成選材。
