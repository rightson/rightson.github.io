# Networking 研究與深度接續

每週三 19:00，series: networking-deep-dive，domain/categories: networking。每次先讀最新 AGENTS.md、RESEARCH_SCHEDULES.md 與最近同 domain 文章；本檔是選材規格，不代表 scheduler 狀態。

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
