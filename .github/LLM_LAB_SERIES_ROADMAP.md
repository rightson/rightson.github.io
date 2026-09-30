# LLM Lab：模型到晶片的全棧課程

每週六 09:00 啟動，series: llm-lab。先讀最新 AGENTS.md 與 RESEARCH_SCHEDULES.md。本檔是先備、接續與完成狀態，不代表已啟用排程。新 session 先查既有相關文章／課程作品，以證據接續，不把建立新對話當作所有知識歸零。

每週一個完整單元，直覺、必要數學、可執行程式、baseline、結果解釋與上下層 coupling 連成因果鏈。沒有必要硬體時提供可重現程序並標未實跑；不捏造 benchmark，不為篇幅提前使用尚未教過的先備。技術圖、台灣繁體語氣、來源與發布規則依 AGENTS.md。

## 課程主線與先備

- [ ] L001. Tensor、線性層、loss、autograd 與一個可訓練的最小模型。
- [ ] L002. Attention、位置資訊、Transformer 與可手算／可實作的 forward path。先備 L001。
- [ ] L003. Tokenizer、資料、objective、optimizer 與最小語言模型訓練。先備 L002。
- [ ] L004. 推論、sampling、KV cache、batching、精度與 memory/compute 計算。先備 L003。
- [ ] L005. 工具、Agent runtime、memory、evaluation 與可驗證任務。先備 L004。
- [ ] L006. Profiling、kernel、tiling、fusion、quantization 與效能／誤差。先備 L004。
- [ ] L007. Compiler IR、lowering、runtime 與硬體執行映射。先備 L006。
- [ ] L008. 加速器資料流、systolic array、memory hierarchy 與 roofline。先備 L006、L007；引用 TPU 已教機制。
- [ ] L009. 分散式訓練／推論、collective、網路、容錯與叢集資源。先備 L004、L008；引用 Networking／K8s／DS 系列。
- [ ] L010. 從演算法到可模擬的 RTL datapath、testbench 與正確性。先備 L008。
- [ ] L011. Synthesis、constraint、STA 與設計權衡的最小完整實驗。先備 L010；引用 EDA 已發布教材。
- [ ] L012. APR、ECO、signoff、驗收證據與 design flow 的完整作品。先備 L011。

篇號穩定；必要先修可用新 ID 插入，不重新編號。以上全為候選單元，未宣稱完成。每次先核對是否已有作品；完成需有 source、圖、實跑或未跑的正確證據、build/deploy 與正式頁核驗，補 path／URL。公開稿以核心問題選一個既有 domain，不能為全棧之名把不同主題機械歸為同一分類。
