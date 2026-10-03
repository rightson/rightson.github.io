---
layout: post
title: "Strata 如何減少長上下文推論的快取等待與重複計算"
date: 2026-10-04 07:31:42 +0800
domain: ai-frontier
categories: ai-frontier
description: "Strata 以 GPU-assisted I/O、跨層記憶體布局與快取感知排程，改善長上下文推論的搬移瓶頸。OSDI 2026 正式版的最高五倍增益，是指定工作負載在相同首字延遲下的吞吐量提升。"
summary:
  - "長前綴命中 DRAM 快取仍要搬入 GPU；只提高命中率，可能把瓶頸轉成 I/O。"
  - "GPU 小頁面與 host page-first 布局各自保留，以專用 I/O kernel 連接計算與儲存需求。"
  - "Strata 延後重複前綴計算、平衡載入與運算，再用現有 decode 工作填補等待。"
  - "最高五倍來自 Llama-70B／LooGLE 的同 TTFT 吞吐比較；今日部署須重新量測。"
---

**長上下文推論即使命中快取，GPU 仍可能花大量時間等待資料。Strata 把快取搬移成本與前綴是否已經算好，一起納入推論排程。**想像多個 Agent 反覆閱讀同一份大型程式庫或技術文件，每次只追加一個很短的問題：保留文件的計算結果，可以省掉大量重算；但那些結果若已移到 CPU 記憶體，下一次使用前仍要搬回 GPU。服務因此同時面對容量、傳輸與工作先後順序三個問題。[OSDI 正式論文，§1–3](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=2)

這篇研究由第一作者 **Zhiqiang Xie（Stanford University／NVIDIA）**等人提出，正式名稱是 *Strata: Hierarchical Context Caching for Long Context Language Model Serving*，刊於 2026 年 7 月 13–15 日的 OSDI ’26。它建立在 SGLang 上，保留精確的前綴 KV 快取，調整資料移動與排程方式；研究目標是讓長上下文服務在相同回應延遲下承接更多工作。[USENIX 論文頁](https://www.usenix.org/conference/osdi26/presentation/xie-zhiqiang)

先沿下圖的資料路徑看問題：舊前綴保存在越慢的層級，可容納的資料通常越多，卻也離正在計算的 GPU 越遠。即使新問題只有少量 tokens，取回舊前綴仍可能是整個請求最昂貴的步驟。

![長文件被多個短問題重用，KV 保存在 HBM、CPU DRAM 與外部儲存；GPU 執行前需要等待較慢層的資料載入](/images/ai-frontier/2026-10-04/strata-context-bottleneck.svg)

圖一：分層 KV 快取的背景示意，依據 [Strata §2–3](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=3)整理。圖中聚焦需要回載的情境，已在 HBM 的部分可略過搬移；實際執行可逐層重疊。箭頭長度與線寬未表示量測比例。

## 保存的是計算狀態，容量會隨前綴長度增加

自回歸 Transformer 的推論大致分成兩階段。**Prefill** 處理輸入，產生各層 attention 的 keys 與 values；**decode** 逐步生成新 token，反覆讀取既有 KV 並追加新狀態。前綴快取把已算過的輸入保留下來，下一個請求若有相同前綴，就能從已完成的部分往後算。[SGLang HiCache 設計文件](https://docs.sglang.io/docs/advanced_features/hicache_design#why-and-what-is-hicache)

這裡重用的是模型在特定前綴下形成的張量。兩個問題談相同主題，只能說語意接近；精確 prefix caching 要比對實際 token 序列及相容的推論設定。新問題仍須計算，它的 attention 也仍須讀取舊前綴。省下的主要是舊 tokens 的重複 prefill，而完整生成過程仍繼續執行。[Strata §2.1、§7](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=3)

可以用一個透明算例看出容量壓力。假設標準 attention 模型有 32 層、8 個 KV heads、每個 head 128 維，K 與 V 都用每元素 2 bytes 儲存。先忽略 metadata、記憶體對齊與 tensor parallel 切分，每個 token 的 KV 為：

```text
每 token KV = 2（K 與 V）× 32 層 × 8 heads × 128 維 × 2 bytes
             = 131,072 bytes = 128 KiB
65,536 tokens 的 KV = 8 GiB
131,072 tokens 的 KV = 16 GiB
```

這是**假設算例**，用固定張量形狀推導容量，未執行模型。即使文件原始文字只有數百 KB 或數 MB，經過每一層留下的狀態也可能占數 GiB；此外 GPU 還要容納權重、執行中的請求與其他暫存資料。把冷 KV 放到較大的 DRAM 或 SSD，因而是很自然的設計。

然而，以上 8 GiB 若以假設的 **40 GB/s 有效頻寬**搬回 GPU，光資料傳輸就約需 **215 ms**；若儲存讀取只有 **7 GB/s**，同一份資料的讀取量級約為 **1.23 秒**。這兩個數值是分別估算的純傳輸時間，未計排隊、競爭與流水線重疊。短問題省下的重算，接著面對一筆很大的資料帳單。

## 小頁面讓快取精細，卻讓傳輸難以跑滿

GPU 的 KV 記憶體採分頁配置有充分理由：請求長度不同、持續加入與離開，固定保留一整塊最大長度空間會浪費容量。小頁面也能精細重用共同前綴，減少最後一頁未填滿的空間。這些好處解決了 GPU 內部的分配問題；跨 CPU 與 GPU 移動時，卻會遇到不同成本。[Strata §3.1](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=4)

如果每一小片都由 CPU 分別提交 `cudaMemcpyAsync`，系統要處理大量操作描述、提交與完成管理。同樣搬 1 GiB，一次連續傳輸與數十萬次小片搬移，能達到的有效頻寬差異可能很大。用穩態的簡化模型表示：

```text
有效頻寬 ≈ min（鏈路上限，同時在途操作數 × 每次傳輸大小 ÷ 操作延遲）
```

這個關係說明兩條改善路徑：增加單次傳輸大小，或提高可有效處理的併行數。它還受到記憶體、提交成本與共享鏈路限制。Strata 選擇提高細粒度搬移的併行效率，讓快取繼續維持小頁面，而不必只靠把頁面放大來取得頻寬。[Strata §3.1–4.2](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=4)

放大頁面會付出什麼代價？假設兩個請求只有前 1,000 tokens 一樣，完整頁面匹配在 page size 256 時，最多先利用前三頁、共 768 tokens；page size 1 則能更貼近真正的共同前綴。這是忽略其他配置限制的假設算例，重點是**I/O 偏好的大區塊，與前綴重用偏好的細粒度，並沒有相同的最佳點**。

## Strata 讓資料布局配合每一層的工作

整體執行由三種責任配合。**HiRadixTree** 沿 token 前綴記錄 KV 的位置與狀態；**Cache Controller** 搬移、備份與預取資料；**Scheduler** 則依請求的資料需求組 batch，交由 GPU executor 執行。每層計算前都透過 CUDA event 確認所需 KV 已經就緒。Prefill 完成的請求再加入持續運作的 decoding batch。[Strata §4.1、圖 4](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=5)

### GPU-assisted I/O 以少量 SM 處理大量碎片

Strata 啟動專用 CUDA kernel，讓大量 GPU threads 直接在 GPU global memory 與已註冊的 CPU pinned memory 之間讀寫。每個 thread 處理一小片資料，透過索引找到來源與目的位置，分散的 KV 頁面便能一起搬移。它省下逐片由 CPU 提交的負擔，並利用 GPU 的併行能力維持在途資料量。[Strata §4.2](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=6)

GPU 執行搬移仍會消耗 SM、register 與執行資源。論文因此使用少量大型 CUDA blocks，並減少快取污染。H200 微基準採 **2 blocks、每個 1,024 threads**，取得 **48 GB/s**，同時執行的 prefill 效能下降低於 5%，decode 低於 10%。這組結果展示了「拿一小部分計算資源換取有效傳輸」的具體取捨。[Strata 圖 5](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=6)

另一種合理選擇是 batched DMA。正式版討論 CUDA `cudaMemcpyBatchAsync`，在相同微基準達 **38 GB/s**；它使用 DMA engine，避免與模型爭用 SM。載入在關鍵路徑時，可優先追求較高傳輸效率；背景備份較不急迫時，可優先減少運算干擾。兩個方向可以採不同 I/O 路徑。[Strata §6](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=14)

### GPU 按 layer 排列，host 按 page 排列

Transformer 逐層運算，GPU 端採 **layer-first**，把同一層的 KV 配置在對應的記憶體區域。外部儲存卻常需要讀寫「某一頁跨所有層的 KV」；沿用 GPU 布局，這一頁就分散成許多小區塊。Host 採 **page-first**，把同一頁各層資料集中，就能提供較連續的儲存 I/O。[Strata §4.2.1、圖 6](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=7)

![GPU 的 layer-first 與 host 的 page-first 排列對照，I/O kernel 搬移時依索引轉換位置，外部儲存可按完整頁面傳送](/images/ai-frontier/2026-10-04/strata-layout-transform.svg)

圖二：依據 [Strata §4.2.1](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=7)整理的布局示意。A、B 是邏輯頁面，數字表示模型層；只畫三層以呈現排列關係。

專用 kernel 在搬移時計算目的位址，就能完成這個轉換。兩個最佳化作用於不同接點：GPU threads 改善 **CPU↔GPU 的細碎傳輸**；page-first 改善 **host↔外部儲存的連續性**。邏輯 page 的大小與每層的實體排列因此可以分別選擇，無須逼所有層共用同一種布局。

## 搬得更快之後，排程還要處理三種等待

光改善 I/O 仍有剩餘瓶頸。正式論文的 Qwen2.5-14B／LooGLE 分析中，傳統配置的 prefill 有 **74% 時間**卡在 KV 傳輸；換成高效率 I/O 後，仍約有 **24%**是載入停頓。若歷史前綴很長、新 tokens 很少，下一層 KV 的搬移就可能長於當前層的運算，原本逐層重疊的設計無法完全遮蔽它。[Strata 圖 1、§3.2](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=3)

### 尚未算好的共同前綴，先讓一個請求完成

假設請求 A 正在為一段冷前綴建立 KV，B 幾乎同時到達並使用相同前綴。若系統只查已完成的快取，兩者都會被當成 miss，重複計算同一大段輸入。論文稱為 **delay hit**：B 晚一點執行，本來就能命中 A 即將完成的結果。[Strata §3.2、§4.3.1](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=7)

Strata 在 HiRadixTree 加入暫態節點：`in-queue` 表示已有請求準備建立這段前綴，`in-flight` 表示正在計算，完成後才變成指向有效 KV 的一般節點。後續匹配的請求延後執行，保留在等待佇列前端。預設以超過 **100 個匹配 tokens** 作為延後條件，避免為很短的偶然重複付出排隊成本。[Strata §4.3.1](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=8)

這讓「稍微晚開始」有機會換到更早完成。但等待有成本：若只共享很短前綴，或前一個請求完成仍要很久，延後可能傷害 B 的回應時間。門檻與服務延遲需求因此需要一起調整。

### 已經存在的共同前綴，盡量一起載入使用

另一種情況是 KV 已在 host，只差搬進 GPU。此時把使用同一前綴的請求放進同一 batch，可以共用載入結果與 GPU cache pages，論文稱為 **bundle hit**。兩種決策的差別很具體：資料還在建立時，先避免重算；資料已存在時，設法攤平搬移成本。[Strata §4.3.2](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=8)

對不同前綴的請求，scheduler 也會平衡 batch 的載入與運算。例如 A 需要載入很長的歷史 KV、只增加短問題，C 的歷史 KV 已在 GPU、但有較多新 tokens 要計算；合在一起，C 的工作便有機會遮蔽 A 的傳輸。持續湊更多同樣需要大量載入的請求，則會讓整批一起堵住。

論文以「**從 CPU 載入的歷史 tokens／新 prefill tokens**」近似 batch 的載入壓力，預設門檻為 100。這是 token 數量比，並且需要依模型與硬體 profiling；真正的時間還受到 attention 形狀、batch、有效頻寬及 kernel 效率影響。演算法每次仍先放入佇列首個請求，被降優先序的請求也保留次序，以降低長期飢餓的風險。[Strata Algorithm 1](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=8)

### 仍有載入空檔，就讓現有 decode 先工作

如果整個 prefill batch 仍需等待，Strata 可以先執行已有的 decoding batch，讓 decode 與 KV 載入重疊。Decode 常主要使用 HBM 頻寬，host→GPU 載入則受到 CPU-GPU 互連限制，兩者有部分互補空間。論文採 prefill／decode 在同一 GPU 上交替的設計；這裡重疊的是**載入與 decode**。[Strata §4.1、§4.3.3](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=8)

![快取感知排程的三項決策，延後尚未完成的共同前綴、共用已存在的前綴載入，並以 decode 填補傳輸等待](/images/ai-frontier/2026-10-04/strata-cache-aware-scheduling.svg)

圖三：依據 [Strata §4.3](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=7)整理的排程示意。圖中順序用來解釋相依與重疊，未表示實測時間比例。

這三步把快取狀態轉成不同動作。只用「命中率高低」決定順序，會把正在計算、已在 host、已在 GPU 的前綴混為一談；Strata 則辨認哪份資料值得等、哪筆搬移能共用，以及空檔能放進什麼工作。

## 走完一次請求，就能看見排程如何省下工作

延續前面的**假設算例**：A 使用 65,536-token 前綴，KV 已在 host，追加 128 tokens；另一個 C 的前綴已在 GPU，要追加 1,024 tokens。單看 A，載入／新計算的 token 比是 **512**；兩者放進同一批後，比值降到約 **56.9**：

```text
A 單獨執行：65,536 ÷ 128 = 512
A 與 C 合批：65,536 ÷（128 + 1,024）≈ 56.9
```

8 GiB 的搬移量保持相同，增加的是 C 原本就要完成的有用工作。這示範了 balanced batching 的目的：讓同一段時間容納互補需求。實際是否能遮蔽約 215 ms 的傳輸，還要看各層的 attention 與矩陣運算時間；token 比值只負責快速篩選。

若 B 又使用 A 的相同 host 前綴，scheduler 可優先讓 B 一起利用已載入的 cache pages。若 A 的前綴一開始完全沒算過，處理方式就改為先完成 A，再讓 B 重用。兩種情況都需要 metadata 正確表達「資料位於哪裡、是否已就緒」，才能決定一起做或稍後做。

資料載入後，GPU executor 在每層對應的完成事件之後才讀 KV。A 的新 tokens 完成 prefill，第一個 token 才能交給使用者，接著加入 decode。整段 TTFT 因而包含排隊、未被遮蔽的傳輸、prefill 與排程開銷；拿純複製頻寬推算使用者延遲，會漏掉好幾段路徑。[Strata §4.1–4.3](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=5)

### 只要外部儲存慢下來，預取政策就會影響回應時間

現在假設前綴後半段只存在 SSD。Cache Controller 在請求排隊時先啟動預取；若 SSD 壅塞，輪到請求執行時，仍可能留下尚未完成的讀取。Strata 預設的 **best-effort** 政策此時終止未完成的預取，利用已在 host／GPU 的連續前綴，其餘部分重新計算。偵測點是請求被選中時的預取完成狀態，使用者承擔的是額外 prefill 時間。[Strata §4.2.1](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=7)

也可以設定 **wait-complete**，等快取全部到位再執行，或使用 **timeout** 限制等待時間。前者可能省下昂貴重算，後者提供等待上限。選擇應比較預估剩餘讀取時間與重算成本，並考慮尾端延遲要求。這是分層快取最直接的失效情境：較慢層雖有資料，仍可能因到得太晚而失去這次重用的機會。[HiCache 預取政策](https://docs.sglang.io/docs/advanced_features/hicache_design#prefetch-from-l3)

### 備份太積極，也會消耗下一次載入需要的資源

快取產生後是否往下保存，會影響未來命中與當下傳輸壓力。Strata 提供三種策略，預設以存取計數選擇值得備份的資料，各層則預設使用 LRU 淘汰。[Strata §4.4](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=9)

| 策略 | 何時往較慢層備份 | 主要取捨 |
| --- | --- | --- |
| Write-back | 接近上層淘汰時 | 降低即時備份流量與下層占用，但容量吃緊時才備份可能阻塞 |
| Write-through | 新 KV 產生後啟動備份 | 保留較積極，消耗更多寫入頻寬與下層容量 |
| Selective write-through | 存取計數達設定條件 | 用已觀察到的重用篩選熱資料，可能錯過第一次重用 |

這裡的 write-through 是快取複本政策。要討論持久保存，還需分辨資料目前只到 DRAM、已交給外部 backend，或真的完成儲存端寫入；這些完成條件應由部署使用的 controller 與 backend 定義。[HiCache 寫回與共享說明](https://docs.sglang.io/docs/advanced_features/hicache_design#data-write-back)

## 最高五倍的結果，需要連同工作負載一起閱讀

OSDI 正式版使用三個主要模型：Llama-3.1-8B、Qwen2.5-14B-Instruct-1M、Llama-3.1-70B。主測試平台配有 8 張 H200，但 **8B／14B 實際各用一張 GPU，70B 用四張做 tensor parallelism**。主要 CPU cache 測試配置 1 TB pinned DRAM。以下是實驗的軟體快照，數字對應這些版本。[Strata §5.1](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=9)

| 比較對象 | 論文版本與設定 |
| --- | --- |
| vLLM＋LMCache | vLLM 0.8.5、LMCache 0.2.1；page 32、LMCache chunk 256 |
| TensorRT-LLM-HiCache | TensorRT-LLM 0.17.0；啟用 CPU offload、page 32 |
| SGLang-HiCache baseline | 以 SGLang 0.4.5 建置的比較實作；逐層重疊、`cudaMemcpyAsync`、page 32 |
| Strata | 建立於 SGLang 0.4.5；page 1，加入論文的 I/O 與排程機制 |

其中 **SGLang-HiCache 是論文建置的 baseline 名稱**，閱讀今日 upstream 文件時要另按版本核對。正式版也明確指出，vLLM-LMCache 與 TensorRT-LLM-HiCache 已使用 CUDA kernels 加速 KV I/O；差距包含干擾控制、快取粒度與排程，不能把全部結果歸因於對手逐頁提交 memcpy。[Strata §5.3.1](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=11)

### LooGLE 比較的是同樣首字延遲下能服務多少工作

下表是 LooGLE 在**相同平均 TTFT 下，輸出 token 吞吐量的最高倍率**。表中三欄各有自己的 baseline；五倍是 Llama-70B 的特定結果。[Strata §5.2.1、圖 8](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=10)

| 模型 | 相對 SGLang-HiCache | 相對 vLLM-LMCache | 相對 TensorRT-LLM-HiCache |
| --- | ---: | ---: | ---: |
| Llama-3.1-8B | 3.2× | 2.6× | 1.9× |
| Qwen2.5-14B | 3.9× | 2.1× | 1.9× |
| Llama-3.1-70B | 5.0× | 5.0× | 3.75× |

這個指標可以理解成：在使用者等待第一個 token 的平均時間維持相同時，服務端能承接更多生成工作。它與「固定流量下延遲縮短多少」是兩個不同方向的比較。2025 年 8 月的 [arXiv v1 摘要](https://arxiv.org/abs/2508.18572v1)寫作 5× lower TTFT；此處採 2026 年 OSDI 正式版的指標與條件。

測試流量也解釋了效益來源。LooGLE 平均輸入 **21,613 tokens**、輸出 **15.6 tokens**；NarrativeQA 是 **54,797／13**；多 Agent 的 ReviewMT 是 **17,708／208.3**。長輸入、短輸出使 prefill 與 cache loading 在總成本中格外突出。請求到達主要以 Poisson 分布模擬，最多允許 128 個請求在途；128 是併發上限。[Strata 表 1、§5.1](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=9)

NarrativeQA 另採 warm-cache 設定：先算好全部文件的 CPU KV，再清空 GPU KV，量測重新啟動負載後的穩態表現。短上下文 ShareGPT 則刻意將 GPU 快取限制在約 500K tokens，結果大致維持可比的效能。這些配置讓讀者知道各組曲線究竟在測哪種壓力。[Strata §5.2.2–5.2.3](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=10)

### 拆開最佳化，才能判斷機制是否真的有幫助

在 Qwen2.5-14B／LooGLE 的拆解實驗中，只改 scheduler 的最高吞吐量達 baseline 的 **1.8×**，只改 I/O 達 **2.3×**。低流量時，小 batch 的 I/O 壓力較輕，排程調整較能消除等待；高流量時，持續傳輸能力更容易成為限制。這支持了同時處理兩層問題的設計，也說明倍率會隨負載改變。[Strata §5.3.1、圖 9](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=11)

外部儲存則是另一組實驗：**DeepSeek-V3、8 張 H20、page 32、12 requests/s**，換成 page-first 後，平均 TTFT 從 **5.03 秒降到 2.42 秒**，generation throughput 從 **27.43 升至 36.41 tokens/s**。它呈現的是跨層布局的收益，主實驗多數只使用 HBM 與 DRAM。[Strata §5.3.5、圖 13](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=13)

GH200 的結果還提出另一個判斷：更快的 CPU-GPU 通道需要對應軟體。論文的 Llama-8B／LooGLE sustained bandwidth，傳統比較實作在 PCIe H200 與 GH200 分別約 **10.80、19.43 GB/s**，Strata-IO 則約 **40.30、150.50 GB/s**。這組工作負載量測呈現了軟體對可用頻寬的影響；同時，完整排程仍能進一步改善服務曲線。[Strata §5.4、圖 14–15](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=13)

## 現行 HiCache 可以沿哪幾個接點閱讀

SGLang 的 [HiCache 官方文件](https://docs.sglang.io/docs/advanced_features/hicache_design)已提供分層快取、layout、I/O backend 與預取政策。若要把論文接到程式碼，應固定版本，從 metadata、搬移與完成事件一路追到排程。以下以 commit `4ab720e6557b44d07bde471ed52a178795298f1a` 為閱讀快照：

- [`cache_controller.py`](https://github.com/sgl-project/sglang/blob/4ab720e6557b44d07bde471ed52a178795298f1a/python/sglang/srt/managers/cache_controller.py#L963-L1000) 合併 load queue，提交 host→device 作業，建立逐層完成事件及 ACK；重疊排程下也用 stream fence 避免尚未完成的寫入與載入撞到同一批頁面。
- [`l2_transfer.py`](https://github.com/sgl-project/sglang/blob/4ab720e6557b44d07bde471ed52a178795298f1a/python/sglang/srt/mem_cache/l2_transfer.py#L144-L179) 逐層提交 host→device 搬移，再透過 `on_layer_done` 將完成事件排入同一個 stream；計算端等待該事件才使用 KV。[事件的 record／wait 實作](https://github.com/sgl-project/sglang/blob/4ab720e6557b44d07bde471ed52a178795298f1a/python/sglang/srt/managers/cache_controller.py#L65-L76)說明了「已提交」與「可使用」之間的同步。
- [`schedule_policy.py`](https://github.com/sgl-project/sglang/blob/4ab720e6557b44d07bde471ed52a178795298f1a/python/sglang/srt/managers/schedule_policy.py#L373-L430) 用等待佇列的 radix tree 辨認尚未成為實體快取的共同前綴，暫時降低重複請求的優先序。這提供部分相關排程行為的程式碼依據。

這裡還有一個會改變平台規劃的作用範圍：**HiCache 的 HBM 與 host DRAM 都屬於單一 inference instance；跨 instance 重用要透過具備共享設定的 L3 backend。**單純提高 `--hicache-ratio`，增加的是各 instance 自己的 host cache。Replica 數量、路由方式與 backend namespace，因而會一起影響重用率。[HiCache Tier Sharing Scope](https://docs.sglang.io/docs/advanced_features/hicache_design#tier-sharing-scope)

## 導入判斷應看省下多少重算，以及留下多少等待

Strata 最匹配的情境，是多個請求反覆使用長前綴，而 HBM 容量不足以長期保留所有可重用資料。大型文件問答、共享背景的 Agent 分支、多輪長對話，都可能出現這種結構。反過來，如果前綴幾乎只用一次，更多下層容量主要增加保存與寫入成本；如果時間大多花在很長的 decode，改善 prefill 的整體影響就會下降。這些是依機制提出、可用實際請求紀錄檢驗的推論。

合理的評估應拆成三組對照：**相同工作負載的單層與分層快取、相同容量的不同 I/O 實作、相同 I/O 的不同排程策略**。固定模型、精度、硬體、到達率與前綴重用分布，記錄每層命中率、重算 tokens、有效傳輸頻寬與 I/O stall，再看 p95／p99 TTFT、每 token 延遲及符合 SLO 的完成量。這是建議的實驗設計，本文沒有自行執行 GPU benchmark。

平均 TTFT 與最高吞吐量都改善，仍可能有少數請求因排程調整而等待更久。正式版在公平性討論中指出，避免 starvation 與滿足每個請求的 SLO 是兩個層次；下一步需要把延遲目標與公平性加入 batch formation。[Strata §6](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf#page=14)

先前的[AI 推論儲存分層文章]({% post_url 2026-09-23-ai-inference-ssd-profit-capture %})討論了儲存如何減少 GPU 等待。Strata 把其中的技術條件具體化：保存得更多、移動得更快、安排得更合理，分別處理不同的限制。若增加 host 容量後命中率上升，但重算成本下降的同時 I/O stall 增長，下一筆工程投入就應先檢查資料路徑與排程；若幾乎沒有可重用前綴，則先回到工作負載本身，評估分層快取的必要性。

## 證據範圍

- 技術機制與主要效能數字採 **OSDI 2026 正式版**。2025 年 arXiv v1 的摘要與最終指標不同；文中的 5× 是特定模型與資料集在相同平均 TTFT 下的吞吐量，不是所有請求的延遲改善倍率。
- 比較使用論文指定的舊版軟體。不能據此宣稱 Strata 勝過 2026 年最新的 vLLM、LMCache、TensorRT-LLM 或 SGLang。已讀的現行程式碼證實分層搬移與部分前綴排程，尚不足以證明啟用 HiCache 就完整啟用論文全部排程策略。
- Qwen 模型具備 1M context window，不代表實驗已驗證百萬-token 服務；NarrativeQA 排除超過 128K 的文件。多數端到端測試不用 SSD，Mooncake delay-hit 分析則使用模擬及無限快取假設，應與實機結果區分。
- 論文主要聚焦單一 compute instance 的管理與排程，可包含 tensor parallelism。它不是完整的叢集排程器；稀疏、線性及混合 attention 的適用性、跨租戶隔離、故障後的暫態節點清理，也需要另行設計與驗證。
- GPU-assisted I/O 仍有資源干擾，排程也不保證逐請求公平性。跨 GPU 世代、共享記憶體平台或不同精度，需重新評估頻寬、KV 大小與運算比。
- 容量、傳輸時間、頁面粒度與 A／B／C 請求數字皆為明示假設算例。精確前綴重用需相容的模型與執行設定；文中未宣稱任意配置 bitwise 相同，也未以原始碼閱讀冒充實跑 benchmark。

## 參考資料

1. Zhiqiang Xie et al. [Strata: Hierarchical Context Caching for Long Context Language Model Serving](https://www.usenix.org/conference/osdi26/presentation/xie-zhiqiang)，OSDI ’26，2026 年 7 月，頁 1–16。本文 PDF 連結使用檔案頁碼，較論文印刷頁碼多一頁封面。
2. [Strata 正式論文 PDF](https://www.usenix.org/system/files/osdi26-xie-zhiqiang.pdf)，主要定位：§3 瓶頸、§4 設計、§5 評估、§6 限制與後續方向。
3. [Strata arXiv v1](https://arxiv.org/abs/2508.18572v1)，2025 年 8 月 26 日；用於交代版本與摘要指標差異。
4. SGLang，[HiCache System Design and Optimization](https://docs.sglang.io/docs/advanced_features/hicache_design)，分層作用範圍、metadata、I/O、layout 與預取／寫回政策。
5. SGLang，[Cache Controller 固定版本](https://github.com/sgl-project/sglang/blob/4ab720e6557b44d07bde471ed52a178795298f1a/python/sglang/srt/managers/cache_controller.py)，host／device 傳輸佇列、同步與完成管理。
6. SGLang，[L2 Transfer 固定版本](https://github.com/sgl-project/sglang/blob/4ab720e6557b44d07bde471ed52a178795298f1a/python/sglang/srt/mem_cache/l2_transfer.py)，逐層載入與完成 callback。
7. SGLang，[Scheduling Policy 固定版本](https://github.com/sgl-project/sglang/blob/4ab720e6557b44d07bde471ed52a178795298f1a/python/sglang/srt/managers/schedule_policy.py)，等待佇列的前綴匹配與暫時降優先序。
