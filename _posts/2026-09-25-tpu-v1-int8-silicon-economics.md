---
layout: post
title: "INT8 把 TPU v1 的晶片預算換成更多 MAC：精度如何同時改寫面積、功耗與頻寬"
date: 2026-09-25 05:03:49 +0800
domain: architecture
categories: architecture
description: "8-bit quantization 讓 TPU v1 能在有限面積與功耗內塞入 65,536 個 MAC，並同時降低權重儲存與資料搬移成本；代價則是 rounding、clipping 與 accumulator 位寬管理。"
---

[上一篇](/ai-industry/2026/09/23/tpu-v1-systolic-array-dataflow.html)拆了 TPU v1 的 256×256 systolic array，但還留著一個更底層的問題：**為什麼這顆晶片有可能在 28 nm、40 W 等級的設計裡放進 65,536 個 MAC？**

答案要從 precision 開始看。

一個乘法器不是抽象的「一個 multiply」。operand 從 8-bit 變成 16-bit，代表 partial product、adder tree、register、wire、SRAM port 與資料路徑都變寬；面積、切換電容與資料搬移能量一起上升。Google 在第一代 TPU 論文裡直接引用當時的 circuit-cost 估計：**8-bit integer multiply 相較 IEEE-754 FP16 multiply，可低約 6 倍 energy、6 倍 area；integer add 的差距更大，energy 約 13 倍、area 約 38 倍。** 這些數字不是 TPU 實測，而是論文用來說明低精度 arithmetic 為何能大幅改變 ASIC cost structure 的前提。[Jouppi et al., ISCA 2017](https://arxiv.org/pdf/1704.04760)

換句話說，quantization 對 TPU v1 不是部署後的小優化；它直接決定了晶片可以長成什麼樣子。

## Inference 為什麼有資格使用較低 precision

Training 與 inference 對數值的需求並不相同。

Training 必須更新 weight，gradient 可能跨很大的 dynamic range，微小差異還會在很多 step 中累積。Inference 的 weight 已經固定，硬體要做的是把既有模型映射成大量 dot product。只要模型對小幅數值誤差具有足夠容忍度，就沒有理由每一個 operand 都維持 training 時的 floating-point precision。

第一代 TPU 論文把這件事描述得很直接：quantization 將 floating-point number 轉成 narrow integer，而 8-bit 在許多 inference workload 上已經足夠。[Google Research](https://research.google/pubs/in-datacenter-performance-analysis-of-a-tensor-processing-unit/)

後來 Google 團隊在 CVPR 2018 更完整描述 integer-only inference 的 quantization scheme。常見的 affine mapping 可寫成：

r = S × (q − Z)

其中 r 是 real value，q 是量化後 integer，S 是 scale，Z 是 zero-point。模型不是把小數點直接砍掉，而是先決定一段 real-value range，再把它映射到有限的 integer code。8-bit 只有 256 個 code，因此一定會產生 rounding；超出 representable range 的值還會被 clipping。[Jacob et al., CVPR 2018](https://openaccess.thecvf.com/content_cvpr_2018/html/Jacob_Quantization_and_Training_CVPR_2018_paper.html)

<figure>
  <img src="/images/architecture/2026-09-25/affine-quantization-mapping.svg" alt="Affine quantization 將 real value 映射到有限 8-bit integer code" style="max-width:100%;height:auto;">
  <figcaption>圖 1｜Affine quantization 的核心是 scale 與 zero-point，而不是直接截掉小數。依據 <a href="https://openaccess.thecvf.com/content_cvpr_2018/html/Jacob_Quantization_and_Training_CVPR_2018_paper.html">Jacob et al., CVPR 2018</a> 重繪整理。</figcaption>
</figure>

這裡的 trade-off 很清楚：precision 降低後，hardware efficiency 上升；但 model accuracy 可能因 rounding、clipping、outlier 而下降。Quantization-aware training 的價值，就是在 training 時先模擬這些誤差，讓模型學會適應 integer representation。CVPR 2018 的工作顯示，weights 與 activations 同時量化成 8-bit 時，模型 memory footprint 相較 32-bit floating point 可接近縮小四倍，並能在其測試模型上維持接近浮點版本的 accuracy。[Jacob et al., CVPR 2018](https://openaccess.thecvf.com/content_cvpr_2018/html/Jacob_Quantization_and_Training_CVPR_2018_paper.html)

這是 general quantization mechanism；不能倒推成 TPU v1 使用完全相同的 TensorFlow Lite quantizer。可以確定的是，TPU v1 的主要 Matrix Multiply Unit 以 8-bit integer operand 為設計中心。

### Quantization 真正犧牲的是解析度，不只是有效位數

假設某層 activation 的有效範圍是 -1 到 1，若用對稱 INT8 表示，可以粗略把 scale 想成 1/127。real value 0.37 會被映射到最接近的 integer code，大約是 47；還原後約為 47/127 = 0.3701。單次誤差很小。

問題在於 range 不會永遠這麼漂亮。若同一層偶爾出現 magnitude 20 的 outlier，而 quantizer 又必須讓 20 落在 representable range 內，scale 會被迫放大。原本密集落在 -1 到 1 的多數 activation，就只剩很少的 integer code 可用。這時候即使沒有 clipping，rounding noise 也會急遽增加。

反過來，如果 quantizer 把 range 收窄到多數資料所在區域，resolution 會更好，但 outlier 會飽和在最大／最小 code。這就是 clipping error。

所以 8-bit 是否「夠用」不是單純看 bit 數，而是看 tensor distribution、scale 的選擇、不同 channel 的 range，以及模型對誤差的敏感度。後來 per-channel quantization 會重要，就是因為同一個 layer 裡不同 output channel 的 weight distribution 可能差很多；共用一個 scale 往往讓少數 outlier 決定整個 tensor 的 resolution。

這也說明硬體與模型之間真正的契約：硬體提供低精度 arithmetic 的效率，compiler / quantizer 必須把 tensor 映射到那個數值空間，模型則要在這個誤差模型下仍然維持可接受 accuracy。缺任何一層，8-bit MAC 都只是一個便宜但不好用的乘法器。

## 8-bit 讓同樣 die budget 容納更多 arithmetic

TPU v1 採 28 nm、700 MHz。Matrix Multiply Unit 裡有：

256 × 256 = 65,536

個 8-bit MAC。

每 cycle，每個 MAC 做一個 multiply 與一個 add；把兩者各算一個 operation：

65,536 × 700M × 2 ≈ 91.75 TOPS

也就是論文報告的約 92 TOPS。

如果 multiplier 本身是整顆 chip 最昂貴的元件之一，那 precision 下降就等價於釋放 transistor budget。Google Cloud 當年的技術文章把這件事說得更直白：TPU 使用 65,536 個 8-bit integer multiplier，而當時常見 GPU 只有數千個 32-bit floating-point multiplier；只要 application accuracy 允許 8-bit，硬體便有機會塞進數十倍更多 multiplier。[Google Cloud TPU deep dive](https://cloud.google.com/blog/products/ai-machine-learning/an-in-depth-look-at-googles-first-tensor-processing-unit-tpu)

| Arithmetic | TPU v1 論文引用的相對 circuit cost | 架構含義 |
| --- | ---: | --- |
| INT8 multiply vs FP16 multiply | 約 1/6 energy、1/6 area | 相同面積／功耗預算能配置更多乘法器 |
| INT8 add vs FP16 add | 約 1/13 energy、1/38 area | accumulator 周邊 arithmetic 更容易壓低成本 |
| INT8 weight vs FP32 weight | raw storage 為 1/4 | weight memory 與傳輸 byte 數同步下降 |

表 1｜前兩列為 TPU v1 論文引用的 circuit-cost 估計；第三列是位元寬的直接算術結果，與 Jacob et al. 報告的近 4× model-memory reduction 一致。來源：[Jouppi et al., ISCA 2017](https://arxiv.org/pdf/1704.04760)、[Jacob et al., CVPR 2018](https://openaccess.thecvf.com/content_cvpr_2018/html/Jacob_Quantization_and_Training_CVPR_2018_paper.html)。

值得注意的是，TPU floorplan 也反映這個取捨：Matrix Multiply Unit 只佔約四分之一 die，但已經容納 65K MAC；大量面積反而留給 Unified Buffer 與其他 data-storage structure。當 arithmetic 被低精度做便宜之後，**memory 會開始變成下一個最昂貴的資源。**

### 為什麼 bit-width 會這麼直接地變成面積與功耗

從電路角度看，N-bit integer multiplier 要處理 N×N 個 partial-product 關係，再透過 reduction tree 與 final adder 合併。實際 cell library、Booth encoding、pipeline depth 與 timing target 會改變精確 scaling，因此不能把「bit 數減半」機械地等同「面積變四分之一」。但方向很清楚：operand 越寬，需要參與切換的邏輯、wire 與 register 越多。

Floating point 還多了 exponent、mantissa normalization、rounding、exception handling 等資料路徑。TPU v1 選擇 inference-only 的 8-bit integer datapath，等於把這些通用 floating-point 成本從最熱的 matrix multiply path 移除。

更重要的是，這不是只省單顆 MAC 的 power。65,536 個 MAC 每個 cycle 同時切換時，任何每-operation energy 的差異都會被放大 65K 倍；而面積節省也會反過來讓 wire 更短、array 更緊密，進一步降低資料移動成本。domain-specific accelerator 的優勢常常就是這種乘數效應：一個局部簡化同時作用在數萬個平行單元上。

因此「INT8 比 FP16 少 8 bits」這種描述太表面。真正改變的是整顆晶片在固定 power envelope 內能承受多少 active arithmetic density。

<figure>
  <img src="https://storage.googleapis.com/gweb-cloudblog-publish/images/tpu-15dly1.max-500x500.PNG" alt="第一代 TPU block diagram，顯示 Unified Buffer、Matrix Multiply Unit、Accumulator 與 Weight FIFO" style="max-width:100%;height:auto;">
  <figcaption>圖 2｜TPU v1 block diagram。低精度讓 Matrix Multiply Unit 可以做得極度密集，但晶片仍需要大面積 Unified Buffer、Accumulator 與 Weight FIFO 支撐資料供應。來源：<a href="https://cloud.google.com/blog/products/ai-machine-learning/an-in-depth-look-at-googles-first-tensor-processing-unit-tpu">Google Cloud TPU architecture deep dive</a>。</figcaption>
</figure>

## 8-bit 也把同一條 memory bus 變得更有用

假設一個 model 有 100M weights。

只看 raw representation：

| Representation | 100M weights 所需空間 |
| --- | ---: |
| FP32 | 約 400 MB |
| FP16 | 約 200 MB |
| INT8 | 約 100 MB |

表 2｜單純依位元寬計算，不含 metadata、alignment、compression 或 padding。INT8 相對 FP32 減少四分之三的 raw bytes。

這件事對 accelerator 特別重要，因為一個 MAC 再便宜，如果每次計算都必須等 off-chip DRAM，compute density 並不會自動變成 application throughput。

TPU v1 的 Weight Memory 是 8 GiB DDR3，透過 Weight FIFO 把 weight 餵進 Matrix Multiply Unit；Unified Buffer 則保存 activation。當 weight 從 32-bit 降到 8-bit，同樣的 physical bandwidth 理論上能搬四倍數量的 weight element。這等於在沒有改 DRAM channel 的情況下，把「每秒能供應多少 operand」提高。

但這個收益沒有把 memory wall 消失。

Google 的實測顯示，六個 representative workload 裡有四個仍受 memory bandwidth 限制；論文甚至估算，把 TPU 的 DDR3 memory system 換成當時 K80 等級的 GDDR5，achieved TOPS 可以接近三倍。[Jouppi et al., ISCA 2017](https://arxiv.org/pdf/1704.04760)

這很能說明 accelerator 演化的規律：當 precision 讓 compute 變便宜，瓶頸就往 memory 移。

### 用 100M weights 算一次：低 precision 同時改變容量與等待時間

TPU v1 論文的六個 production workload 裡，最大模型約有 100M weights。若只做 raw-size 算例，FP32 需要約 400 MB、FP16 約 200 MB、INT8 約 100 MB。

第一代 TPU 的 Weight Memory 頻寬約為 30 GiB/s。若極度簡化地假設整個 100 MB weight set 必須從 DRAM 順序搬一次，而且忽略 protocol、burst efficiency、bank conflict 與重用，理論傳輸時間大約是：

FP32：400 MB / 30 GiB/s ≈ 12–13 ms  
INT8：100 MB / 30 GiB/s ≈ 3–4 ms

這不是 TPU workload 的實測 latency，因為真實 execution 會 tile、reuse、pipeline，並把 weight transfer 和 compute 重疊；不同 model 的 reuse 也完全不同。但這個算例揭露一件很重要的事：precision reduction 不只把 model「裝得下」，還直接縮短同一條 memory channel 上每份 tensor 的服務時間。

當系統進入 bandwidth-bound 區域，這種 byte reduction 往往比增加更多 MAC 更有價值。反過來，如果 workload 的 arithmetic intensity 很高，同一份 weight 被重用上千次，weight bandwidth 的影響就會降低，compute array utilization 才重新成為主要問題。

這正是 roofline model 後面會出現的理由：需要把 operations 與 bytes 放在同一個模型裡，才能知道下一顆 transistor 應該花在 MAC、SRAM 還是 memory interface。

## Precision 在 TPU v1 上直接等於 throughput

TPU v1 的 Matrix Unit 可以接受不同 precision 組合，但 speed 不一樣。

論文明確寫道：8-bit weight × 8-bit activation 時是 full speed；若一邊是 8-bit、一邊是 16-bit，Matrix Unit 只有 half speed；兩邊都是 16-bit 時只剩 quarter speed。[Jouppi et al., ISCA 2017](https://arxiv.org/pdf/1704.04760)

<figure>
  <img src="/images/architecture/2026-09-25/tpu-v1-precision-throughput.svg" alt="TPU v1 在不同 8-bit 與 16-bit operand 組合下的相對 Matrix Unit throughput" style="max-width:100%;height:auto;">
  <figcaption>圖 3｜TPU v1 Matrix Unit 的 relative speed：8b×8b 為 full speed，混合 8/16-bit 為 half speed，16b×16b 為 quarter speed；圖中的 92/46/23 TOPS 依論文 92 TOPS peak 線性推導。依據 <a href="https://arxiv.org/pdf/1704.04760">Jouppi et al., ISCA 2017</a> 重繪整理。</figcaption>
</figure>

所以 precision 在 TPU v1 上不是 software format 選項，而是 hardware throughput parameter。當 operand width 加倍，固定 datapath 與 MAC array 可以同時處理的 element 數下降，整個 accelerator 的 peak arithmetic rate 跟著掉。

這也解釋了為什麼「同一個 model 量化成 INT8」可能同時得到三種收益：每個 arithmetic unit 變小、變省電；相同 die area 可以放更多 parallel MAC；相同 SRAM/DRAM bandwidth 可以搬更多 element。

這三件事同時發生，才會形成 ASIC 級的效率差，而不是單純把 model file 壓縮四倍。

## Accumulator 不能跟著一路縮成 8-bit

若所有 data path 都縮成 8-bit，dot product 很快就會 overflow。

拿一個 256-element signed INT8 dot product 做最簡單的 worst-case estimate：

127 × 127 × 256 = 4,129,024

2²² = 4,194,304，所以光 magnitude 就接近 22 bits；再考慮 sign、跨 tile accumulation 與實際 network layer 的範圍，8-bit accumulator 顯然不夠。

TPU v1 因此用 8-bit operand 做 multiply，但 16-bit product 會送進 **32-bit Accumulator**。論文描述的是 4 MiB accumulator memory，內含 4096 組、每組 256 個 32-bit accumulator。[Jouppi et al., ISCA 2017](https://arxiv.org/pdf/1704.04760)

這是 low-precision accelerator 很重要的一個設計原則：**輸入 precision 可以很低，但 reduction path 往往需要更高 precision。**

把所有資料都壓成最窄位元，不代表整體效率最高。若 accumulator 太窄，需要頻繁 rescale、saturate，甚至造成 accuracy loss，省下來的面積可能在其他地方付回去。

### Low precision 的 failure mode 往往發生在 reduction，不是在 multiply

假設單一 product 都能精確放進 16 bits，也不代表幾百、幾千個 product 相加後仍能安全。dot product 本質上是 reduction；誤差與 dynamic range 都會沿著 reduction tree 累積。

這也是為什麼硬體常採用「窄 input、寬 accumulator」：把大量最頻繁的 multiply 做便宜，同時在相對少數的 accumulation state 上付出較高 bit-width 成本。這是一個比「所有地方都 INT8」更好的 area/accuracy trade-off。

對 compiler 而言，這還會產生 requantization boundary。某一層的 32-bit accumulated result，送進下一層 8-bit activation 前，必須重新套用 scale、rounding 與 saturation。若 scale 選錯，問題不是 arithmetic throughput 下降，而是整層輸出 distribution 被扭曲。

因此 quantized accelerator 的 correctness 不能只驗證「integer kernel 算對」。至少還要驗證三個邊界：輸入 tensor 的 quantization parameter 是否匹配、accumulator 是否可能 overflow、輸出 requantization 是否維持模型允許的 error budget。

這種數值 contract 後來會一路延伸到 compiler IR：tensor 不只需要 shape 與 dtype，還需要 scale、zero-point、per-tensor/per-channel 等 quantization metadata。硬體越專用，software stack 就越需要精確描述這些語意。

## Quantization 的成本最後會回到模型與 compiler

硬體端希望 bit 越少越好；模型端則希望數值誤差越少越好。兩者不會自然一致。

如果一層 activation 大多落在 [-1, 1]，但偶爾出現 20 的 outlier，要保留 20，就必須把 scale 放大，讓 [-1, 1] 的大多數值只用到很少幾個 integer code；如果把 range 縮小，outlier 又會被 clipping。

因此 quantization 最終會變成一個 cross-layer problem：

model distribution → quantizer / training → compiler representation → integer kernel → MAC / accumulator → memory traffic

這也是後來 per-channel quantization、quantization-aware training、mixed precision 會變得重要的原因。它們都在處理同一個 trade-off：哪一些 tensor 可以降 precision，哪一些需要保留更多 dynamic range。

對 TPU v1 而言，Google 先抓住了 inference workload 最有價值的一個區域：大量 weight/activation 可以用 8-bit，而 accumulator 保留 32-bit。這個選擇讓晶片能以很小的 control overhead 建立極高 MAC density。

## INT8 解掉 arithmetic cost，下一堵牆就是 memory

回頭看第一代 TPU，可以把設計因果鏈濃縮成：

Inference accuracy tolerance  
→ 8-bit quantization  
→ smaller / lower-energy arithmetic  
→ 65,536 MAC systolic array  
→ 92 TOPS compute density  
→ memory bandwidth becomes dominant

這條鏈比「INT8 比 FP32 快四倍」更精確。位元寬下降不只改變 arithmetic count，而是重新分配整顆晶片的 area、power 與 bandwidth budget。

也正因如此，下一篇不能只繼續看 MAC。

當 65K 個 MAC 已經便宜到可以同時工作，真正困難的問題變成：**24 MiB Unified Buffer、4 MiB Accumulator、Weight FIFO 與 8 GiB DDR3 要怎麼讓資料供應跟得上？**

那就是 TPU v1 memory hierarchy 的設計起點。

## References

1. [Norman P. Jouppi et al., “In-Datacenter Performance Analysis of a Tensor Processing Unit,” ISCA 2017](https://arxiv.org/pdf/1704.04760).
2. [Google Research — In-Datacenter Performance Analysis of a Tensor Processing Unit](https://research.google/pubs/in-datacenter-performance-analysis-of-a-tensor-processing-unit/).
3. [Benoit Jacob et al., “Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference,” CVPR 2018](https://openaccess.thecvf.com/content_cvpr_2018/html/Jacob_Quantization_and_Training_CVPR_2018_paper.html).
4. [Google Cloud — An in-depth look at Google’s first Tensor Processing Unit (TPU), May 12, 2017](https://cloud.google.com/blog/products/ai-machine-learning/an-in-depth-look-at-googles-first-tensor-processing-unit-tpu).
