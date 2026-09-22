---
layout: post
title: "TPU 創始篇：Google 為什麼在 2013 年決定做一顆推論 ASIC？"
date: 2026-09-22 13:40:00 +0800
author: Scott Yo-Ru Chen
domain: ai-industry
categories: ai-industry
description: "TPU v1 的真正起點不是追求最高 TOPS，而是 Google 發現：若語音搜尋大規模採用 DNN，既有 CPU 資料中心可能需要直接翻倍。這篇從 workload、P99 latency、INT8、systolic array、memory hierarchy 到 PCIe 整合，拆解第一代 TPU 為何長成這個樣子。"
---

今天回頭看 TPU，很容易把它理解成「Google 自己做的 GPU」。這個理解會錯過整條技術演化最重要的起點：**第一代 TPU 並不是為了打造一顆更通用的平行處理器，而是 Google 發現，神經網路推論一旦變成大規模線上服務，CPU 的成本結構會先崩掉。**

2017 年 Google 在 ISCA 公開第一代 TPU 的實測論文時，揭露了一個比 92 TOPS 更關鍵的背景：2013 年內部估算，如果使用者每天只做約三分鐘的語音搜尋，而語音辨識全面改採深度神經網路，既有資料中心的計算量可能需要接近翻倍。Google 因此啟動高優先級 ASIC 專案，目標不是做一顆漂亮的研究晶片，而是在極短時間內把 inference 的 cost-performance 提升一個數量級；從設計到部署只用了約 15 個月。[Google Research 原始論文](https://research.google/pubs/in-datacenter-performance-analysis-of-a-tensor-processing-unit/)｜[ISCA 2017 PDF](https://arxiv.org/pdf/1704.04760)

這個決策奠定了之後十年的 TPU 路線：先找出真正限制 AI system economics 的瓶頸，再讓硬體、compiler、memory、network 和資料中心一起往那個瓶頸收斂。

## TPU 的起點不是 FLOPS，而是資料中心容量

2013 年的 Google 面對的問題不是「矩陣乘法能不能更快」，而是「如果 DNN inference 滲透到 Search、Translate、speech 等大量服務，現有機房能不能承受」。

兩者差很多。

如果只是單一模型速度不足，可以加 CPU、換 GPU、增加 batch size。但如果 workload 本身正在快速滲透所有產品，硬體效率直接變成資料中心的 CAPEX、電力、rack 數量和服務容量。此時，把每一次 inference 的成本下降 2 倍，不只是 benchmark 變快，而可能等價於少蓋大量 server。

Google 的論文指出，第一代 TPU 服務的六個代表性 neural-network workloads，包括 MLP、LSTM 與 CNN，覆蓋當時約 95% 的 TPU inference workload。值得注意的是，CNN 當時只佔其中很小一部分；MLP 與 LSTM 才是實際資料中心的重要負載。這也是一個很好的提醒：**accelerator 應該依真實 workload distribution 設計，而不是依當時最熱門的論文模型設計。**

TPU v1 因此沒有試圖成為萬用 accelerator。Google 把 training 留給現成 GPU，把第一顆 TPU 專注在 production inference。

## 真正的 KPI 是 P99 latency，不是把 GPU 跑滿

線上 inference 有一個與 HPC 很不同的限制：使用者正在等答案。

一個 batch 越大，矩陣乘法通常越容易把 GPU 填滿，throughput 也越漂亮；但 batch 必須等更多 request 湊齊，queueing latency 會上升。對 Search、speech、Translate 這種 user-facing service，平均吞吐量高卻無法守住 tail latency，並沒有實際價值。

Google 在 TPU v1 論文中特別強調 99th-percentile response time。CPU/GPU 常見的 out-of-order execution、cache hierarchy、multithreading、prefetching 等機制，能提高平均利用率，卻也增加 execution time 的動態性。TPU 反過來選擇一個相對 deterministic 的 execution model。

這個取捨看起來「比較笨」，卻非常符合服務端 inference：

- 不追求所有程式都跑得好，只跑 neural-network inference。
- 不追求大型 batch 才能展現效率，而希望在 latency constraint 下仍維持高吞吐。
- 不需要複雜的 CPU-style speculative machinery，把 transistor budget 留給 MAC array 與 SRAM。
- execution 越可預測，scheduler 越容易估算 capacity，也越容易守住 SLO。

所以第一代 TPU 的設計核心不是「比 GPU 多多少 ALU」，而是：**在 latency SLO 之內，能完成多少 inference。**


<figure>
  <img src="https://storage.googleapis.com/gweb-cloudblog-publish/images/tpu-15dly1.max-500x500.PNG" alt="第一代 TPU block diagram：Unified Buffer、Matrix Multiplier Unit、Accumulator、DDR3 與 host interface" style="max-width:100%;height:auto;">
  <figcaption>圖 1｜第一代 TPU block diagram。可直接看到 24 MiB Unified Buffer、Matrix Multiplier Unit、accumulator 與 DDR3 weight memory 的資料路徑。來源：<a href="https://cloud.google.com/blog/products/ai-machine-learning/an-in-depth-look-at-googles-first-tensor-processing-unit-tpu">Google Cloud, “An in-depth look at Google’s first Tensor Processing Unit (TPU)”</a>。</figcaption>
</figure>

## 為什麼是 INT8：先把不需要的 precision 拿掉

training 與 inference 的數值需求不同。

訓練時需要更新 weights、累積 gradient，dynamic range 與數值穩定性要求高；但模型訓練完成後，許多 inference workload 可以透過 quantization，把浮點權重與 activation 轉成較窄的 integer representation。

TPU v1 因而把主力資料路徑設計成 8-bit multiply。Google 當年的論文引用硬體成本比較指出，8-bit integer multiply 相對 16-bit floating-point multiply，可以顯著降低 energy 與 area。

這件事的重要性不只是「INT8 比 FP16 小一半」。

假設晶片面積與功耗預算固定，單一 MAC 越便宜，就可以放越多 MAC；同時 SRAM 與資料搬移也能用更窄的 datapath。換句話說，quantization 不是單純 software optimization，而是直接改變 silicon economics。

TPU v1 把這個優勢推到很極端：核心 Matrix Multiply Unit 是一個 **256 × 256 的 MAC array**，總共有：

`256 × 256 = 65,536 MACs`

晶片運作在約 700 MHz。如果一個 multiply 與一個 add 各算一個 operation，理論峰值就是：

`65,536 × 700M × 2 ≈ 91.75 TOPS`

這就是論文所報告約 92 TOPS 的來源。

92 TOPS 本身沒有神秘之處。真正的工程選擇是：Google 願意犧牲 general-purpose flexibility，換來 65,536 個低精度 MAC 可以在很小的控制成本下規律運轉。

## 256×256 systolic array：重點是少搬資料，不只是多做乘法

如果只把 65,536 個乘法器堆在晶片上，還不會自然得到高效率。最大的敵人往往不是 arithmetic，而是 data movement。

從 SRAM 讀一次資料所消耗的能量，可能比一次窄位元 multiply-add 高得多；更不用說從 off-chip DRAM 搬資料。於是 TPU v1 使用 systolic execution：資料像波一樣穿過規律排列的 processing elements，讓同一份 weight 或 activation 在 array 內被重複使用，而不是每次 MAC 都回 Unified Buffer 重新讀取。

TPU 的 MatrixMultiply 指令可以把一個 `B × 256` 的 input，乘上一個 `256 × 256` 的 weight tile，輸出 `B × 256`。weight 從 array 上方載入，activation 從另一方向流入，partial sum 沿規律路徑累積。

把它想成工廠輸送帶會比較精確：不是 65,536 個工人各自跑去倉庫拿零件，而是零件沿著固定路徑經過每一站，每一站只做自己那個 MAC。


<figure>
  <img src="https://storage.googleapis.com/gweb-cloudblog-publish/original_images/Systolic_Array_for_Neural_Network_2g8b7.GIF" alt="Systolic array 執行矩陣乘法的資料流動畫" style="max-width:100%;height:auto;">
  <figcaption>圖 2｜Systolic array 中 input、weight 與 partial sum 以規律方式在相鄰 MAC 間流動，核心價值是資料重用而非單純堆疊乘法器。來源：<a href="https://cloud.google.com/blog/products/ai-machine-learning/an-in-depth-look-at-googles-first-tensor-processing-unit-tpu">Google Cloud TPU architecture deep dive</a>。</figcaption>
</figure>

這帶來三個效果：

1. 大量 MAC 可以共享資料流，降低 SRAM read/write 次數。
2. control logic 可以非常小，因為資料與計算模式高度規律。
3. compiler 可以把較大的矩陣切成固定 tile，再安排 double buffering 與資料搬移。

論文公開的 floorplan 很能說明設計哲學：control 只佔很小比例，大片面積留給 Matrix Multiply Unit、Unified Buffer 與 accumulators。這幾乎就是 domain-specific accelerator 的視覺化定義。

## 24 MiB Unified Buffer：TPU v1 其實已經在對抗 memory wall

TPU v1 常被記住的是 256×256 systolic array，但如果只看到 compute，會漏掉下一代 TPU 為什麼必然出現。

第一代 TPU 具有約 24 MiB 的 on-chip Unified Buffer，用來保存 intermediate activation；另外有約 4 MiB accumulator memory。加總起來，論文摘要稱為約 28 MiB software-managed on-chip memory。weights 則主要放在板上的 8 GiB DDR3 Weight Memory，透過 Weight FIFO 餵給 Matrix Multiply Unit。

這個 hierarchy 大致可以看成：

`Host DRAM → PCIe → Unified Buffer → Matrix Unit → Accumulators → Unified Buffer`

另一條 weight path 則是：

`8 GiB DDR3 Weight Memory → Weight FIFO → Matrix Unit`

這是一個非常重要的架構分界。CPU 習慣讓 cache hierarchy 猜測什麼資料接下來會被使用；TPU 更傾向讓 software/compiler 明確安排資料的位置與搬移。代價是 compiler/runtime 必須更懂硬體，收益則是 predictability 與更低的硬體控制成本。

更有意思的是，Google 的實測顯示六個代表 workload 中有四個受到 memory bandwidth 限制。論文甚至估算，如果把 TPU 的 memory system 換成當時 K80 等級的 GDDR5 bandwidth，實際 TOPS 可以大幅增加。

也就是說，**第一代 TPU 在成功把 MAC 做得極度便宜之後，立刻撞上 memory wall。**

這正是之後 TPU v2 開始採用 HBM、走向 training 的合理下一步，而不是單純把 systolic array 再放大。

## 為什麼它是 PCIe 卡，而不是重做整台伺服器

TPU v1 還有一個容易被忽略的設計決策：它是一張 PCIe Gen3 x16 coprocessor card，可以插進既有 server。

這不是最理想的 accelerator integration，卻是極佳的 time-to-deployment 決策。

Google 當時最重要的是快速把 inference capacity 拉上來。如果第一代 TPU 同時要求新 host CPU、新 motherboard、新 rack、新 network 與新的 programming model，整個專案可能來不及解決 2013 年看到的容量問題。

因此它採取一個很務實的切割：

- host server 繼續處理大型 application 與 control flow；
- TPU 執行神經網路的主要 tensor computation；
- host 透過 PCIe 把指令送進 TPU；
- TPU 儘可能一次把整個 model 從 input 跑到 output，減少 host-device interaction。

甚至 instruction fetch 都沒有設計成完整 processor 的樣子，而是由 host 把 TPU instructions 送進 instruction buffer。整顆 TPU 更接近一個大型、可程式化的 matrix coprocessor，而不是另一顆 CPU。


<figure>
  <img src="https://storage.googleapis.com/gweb-cloudblog-publish/images/tpu-2x0vv.max-600x600.PNG" alt="TensorFlow 到 TPU 的軟體堆疊：StreamExecutor API、user space driver、kernel driver 與 TPU" style="max-width:100%;height:auto;">
  <figcaption>圖 3｜第一代 TPU 並非獨立主機，而是被既有 Google application / TensorFlow stack 驅動的 accelerator。來源：<a href="https://cloud.google.com/blog/products/ai-machine-learning/an-in-depth-look-at-googles-first-tensor-processing-unit-tpu">Google Cloud TPU architecture deep dive</a>。</figcaption>
</figure>


這個決策揭露了一個很值得記住的系統原則：**第一代專用硬體的最佳架構，不一定是理論上最漂亮的架構，而是能最快嵌入既有 production system 的架構。**

## TPU v1 解決了 compute economics，卻故意留下很多問題

TPU v1 的成功不代表它已經是一個完整 AI supercomputer。

它沒有把 training 當成主要目標；沒有 HBM；沒有 TPU-to-TPU scale-up fabric；沒有後來的 Pod；沒有今天針對 MoE、KV cache、decode、collectives 的專門機制；sparse support 也因 time-to-deploy 而沒有放進第一版。

但這些「缺少的東西」反而很適合拿來理解 TPU 演化。

第一代先證明一件事：把 neural-network inference 的核心 operation 固定下來，可以用 ASIC 把 cost-performance 拉開一個數量級。當 compute 變便宜之後，瓶頸依序往外移：

`MAC → on-chip memory → HBM → chip-to-chip interconnect → pod topology → compiler sharding → datacenter network → power/cooling`

到了 2026 年，Google 已經公開第八代 TPU，並第一次把同一世代分成偏 training 的 TPU 8t 與偏 inference / post-training 的 TPU 8i；第七代 Ironwood 則已在 Google Cloud GA。[Google Cloud TPU](https://cloud.google.com/tpu)｜[第八代 TPU architecture deep dive](https://cloud.google.com/blog/products/compute/tpu-8t-and-tpu-8i-technical-deep-dive)

從 v1 到 TPU 8，最值得研究的不是 TOPS 增加了多少，而是**每一代 TPU 都在追逐上一代成功之後暴露出的下一個瓶頸。**

下一篇就從這顆晶片最具代表性的結構進一步往下拆：**256×256 systolic array 到底如何讓 65,536 個 MAC 在每個 cycle 持續工作，以及 tile、weight reuse、accumulator 與 double buffering 如何共同決定實際效率。**
