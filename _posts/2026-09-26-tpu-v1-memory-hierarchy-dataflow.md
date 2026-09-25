---
layout: post
title: "TPU v1 用 24 MiB SRAM 撐起 167 GiB/s 資料路徑：Memory Hierarchy 如何餵飽 65K MAC"
date: 2026-09-26 05:15:48 +0800
domain: architecture
categories: architecture
description: "TPU v1 的 DDR3 weight path 只有 30 GiB/s，但 256×256 MXU 的 activation path 需要約 167 GiB/s。Google 因此把 weights、activations 與 partial sums 依資料壽命、重用率與精度拆成 8 GiB DDR3、24 MiB Unified Buffer、Weight FIFO 與 4 MiB 32-bit accumulators。"
---

[前一篇](/architecture/2026/09/25/tpu-v1-int8-silicon-economics.html)把 INT8 的價值拆到 silicon economics：算術變便宜之後，晶片可以塞進 65,536 個 MAC。接下來真正困難的是供料。

TPU v1 在 700 MHz 運作，Matrix Multiply Unit 每個 cycle 需要送入 256 個 activation element。若是 8-bit activation，單純把這條資料路徑換算成頻寬：

`256 B/cycle × 700M cycle/s = 179.2 GB/s ≈ 166.9 GiB/s`

Google 公開的 block diagram 正好標出約 **167 GiB/s** 的 Unified Buffer → systolic data path。問題是同一顆 TPU 的外部 weight DDR3 只有約 **30 GiB/s**，host 端又受 PCIe Gen3 x16 約 12.5 GB/s effective bandwidth 限制。[Jouppi et al., ISCA 2017](https://research.google/pubs/in-datacenter-performance-analysis-of-a-tensor-processing-unit/)｜[Google Cloud TPU v1 deep dive](https://cloud.google.com/blog/products/ai-machine-learning/an-in-depth-look-at-googles-first-tensor-processing-unit-tpu)

這個差距直接決定 TPU v1 的 memory hierarchy。65K MAC 不可能每個 cycle 都到外部 DRAM 找 operand；資料必須先被搬進更靠近 compute 的地方，而且不同資料的壽命、重用方式與數值寬度不同，不能只靠一塊「大 cache」解決。

<figure>
  <img src="https://storage.googleapis.com/gweb-cloudblog-publish/images/tpu-15dly1.max-500x500.PNG" alt="第一代 TPU block diagram，顯示 PCIe、DDR3 Weight Memory、Weight FIFO、Unified Buffer、Matrix Multiply Unit 與 Accumulator" style="max-width:100%;height:auto;">
  <figcaption>圖 1｜TPU v1 的官方 block diagram。最重要的不是元件名稱，而是資料路徑的不對稱：weight 從 DDR3 以約 30 GiB/s 進來，activation 在片上以約 167 GiB/s 餵給 Matrix Unit。來源：<a href="https://cloud.google.com/blog/products/ai-machine-learning/an-in-depth-look-at-googles-first-tensor-processing-unit-tpu">Google Cloud — An in-depth look at Google’s first Tensor Processing Unit</a>。</figcaption>
</figure>

## 一塊 memory 無法同時滿足三種資料

神經網路 inference 的三種主要狀態，存取行為完全不同。

Weights 很大，但推論期間基本上只讀；同一組 weights 可以服務一批 input。Activations 與 layer intermediate 的容量小得多，卻會在相鄰 layers 之間反覆讀寫。Partial sums 更特殊：每個 dot product 會把大量窄乘積累加成較寬的數值，寫入頻率高，而且不能跟 input 一樣維持 8-bit。

TPU v1 因此把資料拆成三個層級：

- **8 GiB off-chip DDR3 Weight Memory**：保存大量 read-only model weights。
- **24 MiB on-chip Unified Buffer**：保存 activations 與 intermediate results，直接作為 Matrix Unit input。
- **4 MiB 32-bit Accumulators**：保存 Matrix Unit 產生的 partial sums。

Weights 到 Matrix Unit 中間再加一層 **Weight FIFO**；Matrix Unit 本身保留一個 64 KiB weight tile，並有另一份 tile 做 double buffering。論文指出 Weight FIFO 深度為四個 tiles，目的在於讓 weight fetch 與 execution 解耦。[ISCA 2017 PDF](https://arxiv.org/pdf/1704.04760)

<figure>
  <img src="/images/architecture/2026-09-26/tpu-v1-memory-roles.svg" alt="TPU v1 將 weights、activations 與 partial sums 分別放到不同 memory structure 的資料路徑" style="max-width:100%;height:auto;">
  <figcaption>圖 2｜TPU v1 依資料壽命、重用率與 precision 分離 storage：大型唯讀 weights 放在 8 GiB DDR3，熱 activations 放 24 MiB Unified Buffer，reduction state 放 4 MiB 32-bit Accumulators。依據 <a href="https://research.google/pubs/in-datacenter-performance-analysis-of-a-tensor-processing-unit/">Jouppi et al., ISCA 2017</a> 與 <a href="https://cloud.google.com/blog/products/ai-machine-learning/an-in-depth-look-at-googles-first-tensor-processing-unit-tpu">Google Cloud TPU v1 deep dive</a> 重繪整理。</figcaption>
</figure>

這種切割的價值，在於每一塊 memory 都只為一類問題付成本。若把 8 GiB weights 全做成 on-chip SRAM，die area 不可能接受；若把 activations 留在 DDR3，167 GiB/s 的 Matrix Unit input rate根本供不上；若 partial sum 也壓成 INT8，幾百個 products 累加後很快 overflow。

memory hierarchy 因此不是附屬於 compute 的配角。它其實在回答：哪些 bytes 值得留在最昂貴的 on-chip area，哪些可以接受 off-chip latency，哪些必須用更寬 precision 保存。

## 24 MiB Unified Buffer 比 cache 更接近軟體管理的 register file

Google 把 Unified Buffer 描述成 24 MiB SRAM；Google Cloud 的介紹甚至用「work as registers」來形容它。[Google Cloud](https://cloud.google.com/blog/products/ai-machine-learning/an-in-depth-look-at-googles-first-tensor-processing-unit-tpu)

它和 CPU cache 最大的差異，不只是容量。

Cache 需要 tag、replacement policy、miss handling、coherence 或至少 cache-management machinery，硬體會動態猜哪些資料應該留下。TPU v1 的 Unified Buffer 更接近 software-managed scratchpad：compiler/runtime 明確安排資料何時從 host 搬進來、哪一塊 address range 保存哪個 activation、何時再送進 Matrix Unit。

24 MiB 可以寫成：

`96K × 256 × 8 bit = 24 MiB`

每一列剛好是 256 個 INT8 element，也就是 Matrix Unit 每 cycle 的 activation width。另一個直觀換算是：

`24 MiB / 64 KiB = 384`

如果只用最簡化的 256×256 INT8 activation tile 來看，Unified Buffer 理論上可以容納 384 個 64 KiB tiles。真實 compiler allocation 還會受到 tensor shape、padding、不同 layer 的 live range 與 input/output overlap 影響，但這個量級已足以看出它不是一般小型 cache。

更重要的是頻寬。256 bytes/cycle 在 700 MHz 下就是約 167 GiB/s。這條 on-chip path 比 30 GiB/s 的 weight DDR3 高約 5.6 倍，比 host PCIe effective bandwidth 更高一個數量級。

<figure>
  <img src="/images/architecture/2026-09-26/tpu-v1-bandwidth-hierarchy.svg" alt="TPU v1 host I/O、weight DDR3 與 Unified Buffer 到 MXU 的頻寬層級比較" style="max-width:100%;height:auto;">
  <figcaption>圖 3｜TPU v1 的 bandwidth hierarchy。167 GiB/s 片上 activation path、30 GiB/s DDR3 weight path 與約 12.5 GB/s effective PCIe host path 的差距，迫使資料必須 resident 並被重用。數值依據 <a href="https://research.google/pubs/in-datacenter-performance-analysis-of-a-tensor-processing-unit/">ISCA 2017 TPU paper</a> 與 <a href="https://cloud.google.com/blog/products/ai-machine-learning/an-in-depth-look-at-googles-first-tensor-processing-unit-tpu">Google Cloud TPU v1 deep dive</a> 整理；圖中介面頻寬不代表 application-level sustained throughput。</figcaption>
</figure>

這種 scratchpad 設計的 trade-off 很明確。硬體變得簡單、資料位置可預測，P99 latency 也比較不會受到 cache miss pattern 擾動；代價則是 compiler 必須自己管理 live range、搬移與 overlap。cache 把複雜度放在 silicon；TPU v1 把相當一部分複雜度推回 compiler。

論文還透露一個很實際的 physical-design 決策：24 MiB 的大小部分原因是配合 Matrix Unit 在 die 上的 pitch，同時在極短開發週期下讓 compiler 更容易處理。floorplan 裡 Unified Buffer 約佔 **29%** die、Matrix Multiply Unit 約 **24%**、Accumulators 約 **6%**；control 僅約 2%。[Jouppi et al., ISCA 2017](https://arxiv.org/pdf/1704.04760)

這提醒我們 accelerator architecture 並不是把抽象模型最佳化到極致。SRAM 容量、macro shape、wire pitch、compiler complexity 與 time-to-deploy 會一起決定最後的數字。

## Weight FIFO 解的是等待時間，重用才解得了頻寬

Weight path 更容易被誤解。

TPU v1 的 weights 放在 8 GiB DDR3 Weight Memory，推論期間是 read-only。這讓一張卡可以同時保存許多 production models，不需要每次 inference 都從 host PCIe 重傳整個模型。真正計算前，weights 先被讀進 on-chip Weight FIFO，再送到 Matrix Unit。

Matrix Unit 的一個 weight tile 是：

`256 × 256 × 8 bit = 64 KiB`

論文指出，把這個 tile shift 進 systolic array 需要 256 cycles，所以 Matrix Unit 放了第二份 tile 做 double buffering；當 tile A 正在計算，tile B 可以準備進入下一輪。Weight FIFO 又再往前放四個 tiles，讓 `Read_Weights` 採用 decoupled access/execute：送出 address 之後，不必等整個 fetch 完成才讓 instruction 本身結束。若 activation 或 weights 還沒 ready，Matrix Unit 才會真正 stall。[Jouppi et al., ISCA 2017](https://arxiv.org/pdf/1704.04760)

但 FIFO 只能藏 latency，不能違反 bandwidth conservation。

用公開數字做一個理想化算例。64 KiB weight tile 從 30 GiB/s DDR3 搬進來，單純 serialization time 約：

`64 KiB / 30 GiB/s ≈ 2.03 µs`

700 MHz 下約是：

`2.03 µs × 700 MHz ≈ 1,424 cycles`

相較之下，tile 從 Matrix Unit 的內部 buffer 以 256 bytes/cycle shift 進 256×256 array，只需要：

`64 KiB / 256 B = 256 cycles ≈ 0.366 µs`

這兩個數字不是矛盾；它們是兩個不同階段。外部 DDR3 → Weight FIFO 是較慢的 refill path，FIFO / local buffer → array 是較寬的內部 path。

<figure>
  <img src="/images/architecture/2026-09-26/tpu-v1-weight-tile-timing.svg" alt="TPU v1 一個 64 KiB weight tile 在 DDR3 fetch、array load 與 MatrixMultiply 不同 B 值下的時間尺度" style="max-width:100%;height:auto;">
  <figcaption>圖 4｜一個 64 KiB tile 的理想化時間尺度。30 GiB/s DDR3 fetch 約需 1,424 cycles；內部 shift 進 array 只需 256 cycles。若同一 tile 僅支撐 B=256 的 MatrixMultiply，steady-state weight bandwidth 明顯供不上；B 提高到約 1.4K 以上，才有機會靠重用把單一 tile fetch 攤平。算例依據 <a href="https://arxiv.org/pdf/1704.04760">Jouppi et al., ISCA 2017</a> 的 64 KiB tile、700 MHz、30 GiB/s 與 MatrixMultiply(B) 行為；真實 layer 仍取決於 mapping、prefetch 與 reuse。</figcaption>
</figure>

現在把它和 [systolic-array 那篇](/ai-industry/2026/09/23/tpu-v1-systolic-array-dataflow.html)的 `MatrixMultiply(B)` 接起來。

若同一個 256×256 weight tile 只處理 `B=256` rows，compute window 約 256 cycles，也就是 0.366 µs。外部 DDR3 fetch 一份新 tile 卻要約 1,424 cycles。就算 FIFO 已經提前抓資料，長期 steady state 還是不能每 256 cycles 消耗一個全新的 tile，因為上游每秒供應的 bytes 不夠。

如果 `B=2048`，同一組 weights 被 2048 rows 重用，compute window 約 2.93 µs；在理想連續傳輸下，已經長於一個 64 KiB tile 的 2.03 µs DDR3 fetch。這時 weight bandwidth 比較有機會被藏在計算後面。

這個算例刻意簡化，不能當成 TPU layer 的實測 performance。真實模型還有多個 tiles、不同 shapes、pipeline overlap、DDR bank behavior 與 compiler scheduling。但它揭露了最重要的關係：

**FIFO 解 latency；data reuse 解 bandwidth。**

如果 arithmetic intensity 不夠，再深的 FIFO 最後還是會空。

## 4 MiB Accumulator 是 reduction state，不是一般 activation storage

另一個容易被忽略的元件是 4 MiB Accumulator memory。

INT8 × INT8 會產生較寬 product，而一個 dot product 還要把數百個 product 相加。[前一篇](/architecture/2026/09/25/tpu-v1-int8-silicon-economics.html)已用 worst-case 算例說明，256 個 `127×127` 累加後 magnitude 已接近 22 bits；因此 TPU v1 用 32-bit accumulator 保存 partial sums。

4 MiB 的組織是：

`4096 × 256 × 32 bit = 4 MiB`

256 對應 Matrix Unit 每 cycle 輸出的 256 個 partial sums；4096 則不是任意數字。論文說明，TPU roofline 的 knee 大約需要 1350 operations/byte 才能到 peak，設計先把 accumulator depth round 到 2048，再複製一份讓 compiler 可以 double buffer，最後得到 4096 rows。[Jouppi et al., ISCA 2017](https://arxiv.org/pdf/1704.04760)

這裡可以看到一個很漂亮的 cross-layer loop：

`external memory bandwidth → roofline knee → required reuse window → accumulator capacity → compiler double buffering`

也就是說，Accumulator 容量不是只由「一個 tensor 多大」決定，而是被整顆晶片要維持 peak throughput 所需的 arithmetic intensity 反推回來。

當 Matrix Unit 完成 accumulation，資料再經 activation、normalize / pool 等 pipeline，最後寫回 Unified Buffer，成為下一層的 input。這讓 intermediate result 大多數時間留在 chip 上，不必每個 layer 都穿過 PCIe 或 DDR3。

## Failure mode 很單純：資料沒到，65K MAC 一起等

TPU v1 沒有複雜 cache miss hierarchy，並不代表 memory stall 消失。相反地，stall 的原因被變得更直接。

論文描述 Matrix Unit 的原則就是 keep it busy；如果 input activation 或 weight data 沒 ready，Matrix Unit 會 stall。Weight load 可以 decoupled 發出、activation 可以由 compiler 提前搬到 Unified Buffer，但任何一段 schedule 算錯，最後都會在同一個地方付代價：整個 256×256 array 沒有有效 work。

可以想像一個 failure scenario：

1. compiler 預期 tile N+1 已透過 `Read_Weights` 進入 FIFO；
2. DDR3 service time 因前面 traffic 或 mapping 比估計更久；
3. tile N 計算結束；
4. next tile 尚未 ready；
5. Matrix Unit stall，65,536 個 MAC 同時閒置。

這和 CPU cache miss 的表面症狀不同，但本質一樣：compute pipeline 等 memory。TPU 的優勢是 state 比較顯式、可預測；劣勢是 compiler/runtime 必須更準確地把資料搬移排進 timeline。

因此 software-managed memory 不會免費得到 deterministic performance。它只是把「硬體動態猜測」換成「軟體靜態安排」。當 workload shape 很規律，這筆交換非常划算；當 shape、sparsity 或 control flow 變得高度動態，compiler burden 就會急速上升。

## 為什麼六個 production workload 裡四個仍然 memory-bound

第一代 TPU 已經做了很多看似極端的 data-movement optimization：

- INT8 把 operand bytes 壓小；
- systolic array 讓資料在鄰近 MAC 間重用；
- 24 MiB Unified Buffer 把 hot activation 留在片上；
- Weight FIFO 與 double buffering 提前搬 weights；
- 4 MiB Accumulator 讓 reduction 不必反覆寫回外部 memory。

結果仍然是 Google 報告六個代表性 workload 中有四個落在 memory-bound 區域；論文甚至估計，如果把 TPU weight memory 換成當時 K80 等級的 GDDR5，achieved TOPS 可以接近三倍。[Jouppi et al., ISCA 2017](https://research.google/pubs/in-datacenter-performance-analysis-of-a-tensor-processing-unit/)

這不表示 TPU v1 的 memory hierarchy 設計失敗。剛好相反：它把 arithmetic 成本壓低到足以讓下一個限制清楚浮現。

CNN 的 convolution 通常能讓 weights 在大量 spatial positions 上反覆使用，因此 arithmetic intensity 高，比較容易靠近 compute roof。Fully connected 與 LSTM layer 的 weight reuse 較低，大量參數必須持續從 weight memory 送進來，就更容易撞到 30 GiB/s 的斜率上限。下一階段真正要分析的，就是 operations/byte 如何決定同一顆 TPU 到底看到 92 TOPS，還是只看到一小部分。

不過在進入 roofline 之前，還有一個 production constraint 不能跳過。

提高 `B` 可以增加 weight reuse、比較容易把 30 GiB/s fetch 藏在計算後面；但線上 inference 的 request 不能無限等 batch。當服務要求 P99 latency，例如 TPU v1 論文中 MLP0 約 7 ms 的 tail-latency constraint，硬體利用率與 batch size 就會直接衝突。

所以 memory hierarchy 最後把問題推到下一層：**資料重用需要時間，線上服務卻限制你能等多久。**

下一篇會處理 TPU v1 的 #05：P99 latency 與 throughput 為什麼會迫使 datacenter inference processor 採用和傳統 throughput machine 不同的設計。

## References

1. [Norman P. Jouppi et al., “In-Datacenter Performance Analysis of a Tensor Processing Unit,” ISCA 2017 — Google Research](https://research.google/pubs/in-datacenter-performance-analysis-of-a-tensor-processing-unit/)
2. [Jouppi et al., ISCA 2017 — arXiv PDF](https://arxiv.org/pdf/1704.04760)
3. [Kaz Sato, Cliff Young, “An in-depth look at Google’s first Tensor Processing Unit (TPU),” Google Cloud, 2017-05-12](https://cloud.google.com/blog/products/ai-machine-learning/an-in-depth-look-at-googles-first-tensor-processing-unit-tpu)
