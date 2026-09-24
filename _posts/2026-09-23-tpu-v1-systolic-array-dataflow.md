---
layout: post
title: "TPU v1 的效率來自資料重用：256×256 Systolic Array 如何把記憶體存取變成 65,536 個 MAC 的流水線"
date: 2026-09-23 19:43:00 +0800
domain: architecture
categories: ai-industry
description: "TPU v1 要達到 92 TOPS，關鍵在於讓權重與 activation 在 256×256 systolic array 中被重複使用，並用 tile 與 double buffering 把資料搬移藏到計算後面。這篇從 MatrixMultiply(B)、pipeline、shape utilization 與 weight reuse 拆解第一代 TPU 的資料流。"
---

上一篇談的是 Google 為什麼必須做 TPU；這一篇處理更底層的問題：把 65,536 個 MAC 放在晶片上，並不自然等於 92 TOPS。效率取決於這些 MAC 能否每個 cycle 都拿得到資料，而且不必為每一次 multiply-add 都回 SRAM 或 DRAM 取數。

CPU 與 GPU 的通用性建立在 register file、instruction scheduling、cache、threading 與大量控制邏輯上。TPU v1 做了相反的選擇：一旦 workload 已經被壓縮成大量 dense matrix multiply，硬體就不必再問「下一個 operand 在哪個 register、哪條 instruction 要讀它」。它可以把計算單元直接排成固定的空間結構，讓資料自己沿著陣列流動。

systolic array 的價值在這裡：它用空間上的資料重用，交換通用處理器的控制與搬移成本，重點並不在乘法器數量。

## 92 TOPS 只是算術上限，資料必須先供得上

TPU v1 的 Matrix Multiply Unit 是 `256 × 256` 個 8-bit MAC，共 65,536 個運算單元。晶片頻率約 700 MHz，因此理論 MAC throughput 是：

`65,536 × 700M ≈ 45.9 TMAC/s`

若把 multiply 與 add 各算一個 operation，就是約 91.8 TOPS，通常寫成 92 TOPS。[Jouppi et al., ISCA 2017](https://research.google/pubs/in-datacenter-performance-analysis-of-a-tensor-processing-unit/)｜[Google Cloud TPU v1 deep dive](https://cloud.google.com/blog/products/ai-machine-learning/an-in-depth-look-at-googles-first-tensor-processing-unit-tpu)

但如果這 65,536 個 MAC 每個 cycle 都各自從 SRAM 讀兩個 operand，再把結果寫回 SRAM，記憶體埠數、wire、energy 與面積會先失控。Google 對第一代 TPU 的描述很直接：systolic array 讓一次讀進來的資料在相鄰 ALU 間繼續流動，不必反覆經過 register file 或大型 SRAM。

<figure>
  <img src="https://storage.googleapis.com/gweb-cloudblog-publish/original_images/Systolic_Array_for_Neural_Network_2g8b7.GIF" alt="Google TPU systolic array 執行矩陣乘法的資料流動畫" style="max-width:100%;height:auto;">
  <figcaption>圖 1｜矩陣資料以 wavefront 形式穿過相鄰 MAC，重點是把讀入一次的 operand 在陣列內重複使用。來源：<a href="https://cloud.google.com/blog/products/ai-machine-learning/an-in-depth-look-at-googles-first-tensor-processing-unit-tpu">Google Cloud — An in-depth look at Google’s first TPU</a>。</figcaption>
</figure>

從晶片設計角度看，這個差異非常大。長距離讀 register file 或 SRAM，需要 decoder、wordline、bitline、mux 與較長 interconnect；相鄰 MAC 間的短 wire 則單純得多。當演算法本身具有高度規律的 data reuse，硬體就可以把「資料搬移」從反覆 memory access，改成鄰近 processing element 間的 forwarding。

## MatrixMultiply(B) 已經把硬體形狀寫進 ISA

TPU v1 有一條 matrix multiply instruction，而這條 instruction 的 operand shape 幾乎直接揭露了硬體結構。

論文中的 `MatrixMultiply/Convolve` 接受一個可變大小的 `B × 256` activation matrix，乘上一個固定 `256 × 256` weight tile，輸出 `B × 256`，並在權重已就位後以 B 個 pipelined cycles 完成。[ISCA 2017](https://arxiv.org/abs/1704.04760)

也就是：

`[B × 256] × [256 × 256] → [B × 256]`

這和一般 CPU ISA 的思路不同。CPU 的 instruction 描述一次 scalar/vector operation；TPU 的 instruction 描述一整塊 tensor computation。軟體看到的是 `MatrixMultiply(B)`，硬體看到的則是：256-wide activation stream 應該持續餵入一個已經載好 weights 的 256×256 array。

TPU v1 的 dataflow 可以粗略理解成「一個 weight tile 在陣列中停留一段時間，activation rows 持續流過它」。嚴格說來，Google 的公開資料描述的是 weights 預先載入、input 從另一方向流入；用現代 accelerator 術語看，它具有明顯的 weight-stationary 特徵。比起分類名稱，更有用的事實是**同一組 weights 能被 B 個 input rows 重複使用**。

假設 `B=256`，一個 64 KiB weight tile 載入後可以連續處理 256 列 activation。若 `B=1024`，同一組 weights 的成本會被更多 input rows 攤薄；若 `B` 很小，weight load 與 pipeline overhead 就會顯得昂貴。這也是 latency-sensitive inference 永遠存在的矛盾：batch 做大，array 比較容易吃滿；batch 做小，tail latency 比較好，但硬體效率下降。

## Double buffering 與 weight load 的時間重疊

TPU v1 的 Matrix Unit 可以容納一個 64 KiB weight tile，另外再放一份 tile 做 double buffering。Google 論文指出，將一個 weight tile shift 進 array 需要約 256 cycles；第二份 buffer 的目的，就是在目前 tile 計算時，同時準備下一份 tile。[ISCA 2017](https://research.google/pubs/in-datacenter-performance-analysis-of-a-tensor-processing-unit/)

<figure>
  <img src="/assets/images/tpu/2026-09-23/tpu-v1-tile-pipeline.svg" alt="TPU v1 weight tile load 與 compute overlap" style="max-width:100%;height:auto;">
  <figcaption>圖 2｜Weight Memory → Weight FIFO → Matrix Unit 的 tile pipeline。Matrix Unit 保留 active tile 與下一個 tile；下一份 64 KiB weights 的 256-cycle load 可以和目前的 MatrixMultiply 重疊。依據 <a href="https://research.google/pubs/in-datacenter-performance-analysis-of-a-tensor-processing-unit/">Jouppi et al., ISCA 2017</a> 與 <a href="https://cloud.google.com/blog/products/ai-machine-learning/an-in-depth-look-at-googles-first-tensor-processing-unit-tpu">Google Cloud TPU v1 deep dive</a> 重繪整理。</figcaption>
</figure>

這裡可以直接做一個簡單推導。

若目前 tile 的 `MatrixMultiply(B)` 只有 `B=64`，compute 本身只有 64 個 pipelined cycles；下一個 weight tile 卻需要約 256 cycles 才能完全載好。即使有 double buffering，還是可能等 weights。

若 `B=256`，compute window 也有 256 cycles，理想情況下剛好可以把下一個 tile load 藏掉。

若 `B=1024`，weight load 相對更容易被完整 amortize。

可見 systolic array 的 throughput 不能只用 array size 一個數字描述。實際 throughput 大致是：

`array utilization × data reuse × pipeline overlap × memory availability`

少掉任何一項，65,536 個 MAC 都可能只是晶片上的閒置面積。

## 256 這個維度會一路反向約束 compiler

固定大小的 array 帶來效率，也帶來 rigidity。

假設某一層的內積維度正好是 256，hardware tile 可以完整利用。如果是 512，可以乾淨切成兩個 256 tile。如果是 320，至少需要兩個 tile：第一個用滿 256，第二個只有 64 個有效欄位。

只看這一個維度，平均有效 utilization 大約是：

`320 / (2 × 256) = 62.5%`

其餘 37.5% 的陣列位置可能被 padding 或無效工作吃掉。實際 compiler 還可以藉由 batch、feature dimensions、convolution lowering 等方式重新排 layout，但核心問題不會消失：**演算法的 tensor shape 必須被切成硬體喜歡的形狀。**

<figure>
  <img src="/assets/images/tpu/2026-09-23/tpu-v1-array-utilization.svg" alt="256-wide TPU array 在不同 tensor width 下的概念性利用率" style="max-width:100%;height:auto;">
  <figcaption>圖 3｜固定 256-wide array 對 tensor shape 的約束。圖為概念性示例，不是 Google benchmark：64/128-wide 工作只能使用部分 columns；512-wide 則可切成兩個完整 tile。依據 TPU v1 的 256×256 array 與 MatrixMultiply shape 規格整理；硬體尺寸來源：<a href="https://research.google/pubs/in-datacenter-performance-analysis-of-a-tensor-processing-unit/">Jouppi et al., ISCA 2017</a>。</figcaption>
</figure>

因此 accelerator 與 compiler 必須一起看。當 hardware 固定為 256×256，compiler 除了「把 TensorFlow operator 換成 TPU instruction」，還必須處理 tiling、padding、layout、buffer placement，以及哪一段 computation 值得留在 MXU、哪一段交給其他單元。

今天 Google Cloud 的 TPU 文件仍然直接提醒使用者：XLA 會根據 MXU 的實際幾何形狀做 tiling，而 tensor dimensions 是否容易被 tile 會影響效率。[Cloud TPU introduction](https://docs.cloud.google.com/tpu/docs/intro-to-tpu) 這個問題從 v1 到現代 TPU 並沒有消失，只是 array size、precision、compiler 與 workload 都已經更複雜。

## Systolic array 解決 data movement，下一個牆就變成 memory bandwidth

TPU v1 的 systolic array 很成功地降低了 MXU 內部反覆讀寫 SRAM 的需求，但它無法消滅更外層的資料搬移。

weights 還是要從 8 GiB DDR3 Weight Memory 經 Weight FIFO 送進 Matrix Unit；activations 還是要待在 24 MiB Unified Buffer；partial sums 還是要進 4 MiB Accumulators。當 MXU 變得非常快，瓶頸自然往外移。

Google 的實測結果正好證明這件事：六個代表性 production workloads 中有四個受到 memory bandwidth 限制；論文甚至估算，如果把 TPU 的 memory system 換成當時 NVIDIA K80 等級的 GDDR5 bandwidth，achieved TOPS 可以接近三倍。[Jouppi et al., ISCA 2017](https://arxiv.org/abs/1704.04760)

這是一個很典型的 accelerator 演化路徑：

`先把 arithmetic 做便宜 → data movement 成為主成本 → 再把 memory hierarchy 往前推`

理解 TPU v1 的 systolic array，不應停在「Google 用了 256×256 MAC」。Google 把 matrix multiplication 重新表達成一條資料重用流水線，讓 operand 儘量留在晶片內、沿著鄰近 MAC 移動；這個方法成功後，整個系統的瓶頸隨即從 arithmetic 轉移到 memory bandwidth。

下一篇會沿著這個因果鏈繼續往下：TPU v1 為何把主資料路徑壓到 INT8。低 precision 除了是模型壓縮技巧，也直接決定一顆晶片能放多少 MAC、SRAM 要多寬、memory bandwidth 可以服務多少運算，以及最終每瓦能換到多少 inference。
