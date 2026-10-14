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

## 接續候選

### IRN 的選擇性重傳如何維持 RDMA 完成語意

- 原始日期／來源：2018-06-21，[Revisiting Network Support for RDMA extended version](https://arxiv.org/html/1806.08159v1)，SIGCOMM 2018 工作。
- 主要問題：失序資料、SACK bitmap、BDP-FC 與 operation completion 如何共同控制丟包後的傳送與交付。
- 先備：QP、packet sequence、ACK／NACK、RDMA WRITE／READ／SEND 與完成通知；本次 PFC／ECN 資料預算。
- 相關文章：本次 RoCE buffer 長文、STORM RNIC 排程。
- 尚缺：逐 operation 的完整機制推導、原文 §5／§6 及 Appendix B 的語意核對、有限在途狀態的量化與故障重播。當前僅完成選材，不宣稱已實作或已驗證 production transport。
