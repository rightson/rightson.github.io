---
layout: post
title: "INSTA 把 signoff 時序壓進實體設計內迴圈：一次校準、GPU 傳播與驗收邊界"
date: 2026-10-01 06:00:07 +0800
domain: eda
categories: eda
series: sota-r2g-cad
description: "NVIDIA INSTA 以商用 reference tool 的一次性初始化建立可微分 GPU 時序引擎，讓 placement／sizing 取得高速回饋；正式交付仍須回到 reference signoff 重新驗收。"
---

實體設計最佳化長期受一個結構性矛盾限制：真正可信的 signoff 時序模型很精細，適合判定設計能否交付；placement、gate sizing 與 ECO 卻需要反覆嘗試大量候選，每一輪都呼叫完整 signoff engine，探索速度便被最昂貴的分析拖住。若改用簡單 wirelength、net weight 或 learned predictor，迴圈雖然變快，最佳化方向又可能和最後的 WNS／TNS 相反。

NVIDIA Research 在 DAC 2025 發表的 [INSTA](https://research.nvidia.com/labs/electronic-design-automation/publication/lu2025dac/) 提供另一種介面：不重造一套宣稱能取代 signoff 的 STA，而是先從 reference timing tool 匯出一次已解析的 timing state，再用 GPU 執行高速 statistical propagation，並讓 arrival time、slack 對 cell／net arc delay 可微分。這使它更像 signoff 前方的一個「高保真內迴圈」，而非最終放行者。論文獲 DAC 2025 Best Paper，程式亦由 [NVLabs 公開](https://github.com/NVlabs/INSTA)。

這個界線很重要。INSTA 論文報告在一個 1,500 萬 pins、商用 3 nm 設計上，full-graph timing propagation 低於 0.1 秒，與未具名 reference signoff tool 的 endpoint slack correlation 達 0.999；但 correlation 不是 tapeout 證據。可借鏡的平台設計，是把快速代理放在候選搜尋內側，把權威工具保留在初始化、週期性校準與 release gate。[IEEE 摘要列出的條件與結果](https://ieeexplore.ieee.org/document/11132858/)

先沿下圖看兩個不同責任的迴圈。內圈追求每秒可評估多少候選；外圈回答目前模型、corner、exception 與 netlist 是否仍足以支持正式交付。兩者若被壓成同一個「timing pass」，速度與正確性都會失去可管理的邊界。

<figure>
  <a href="/images/eda/2026-10-01/insta-signoff-feedback-overview.svg"><img src="/images/eda/2026-10-01/insta-signoff-feedback-overview.svg" alt="Reference signoff 工具輸出一次性時序狀態給 INSTA；INSTA 在 GPU 上快速評估 placement 與 sizing 候選，只有通過校準與正式 signoff 的結果才進入 R2G 放行。" width="920" height="760" loading="lazy"></a>
  <figcaption>圖一：依據 <a href="https://research.nvidia.com/labs/electronic-design-automation/papers/yichen_INSTA_dac25.pdf">INSTA 論文</a>與<a href="https://github.com/NVlabs/INSTA">公開程式</a>整理；release gate、失效判定與 evidence bundle 是作者提出的平台接法，不代表 NVIDIA 內部流程。</figcaption>
</figure>

## 一次初始化不是讀入網表，而是凍結一份 timing semantics

傳統 STA 從 netlist、Liberty、寄生參數、clock、SDC、mode／corner 與 derate 推導 timing graph。對大型商用工具而言，delay model、exception semantics 和 variation handling 並非全部公開；若另一個工具自行讀取原始檔案並重建模型，即使 graph topology 相同，也可能因 slew、load、arc interpolation、clock pessimism 或例外處理不同而產生系統性偏差。

INSTA 的關鍵選擇，是由 reference tool 先完成這些專有語意，再把已解析的狀態交給 GPU engine。公開程式的 [`do_initialization()`](https://github.com/NVlabs/INSTA/blob/main/src/core/insta.py) 依序讀取有效 pins、排除 timing 的 pins、cell arcs、net arcs、startpoint／endpoint attributes、launch clock latency 與 POCV guardband，建立 timing graph、levelize，再預先計算 propagation collateral。輸入不是一份模糊的「STA report」，而是一組能重建特定分析狀態的 CSV／report：

```text
all_between_sp_ep_pins.csv   # 分析範圍內的 pins
no_timing_pins.csv           # reference tool 已判定不傳播 timing 的 pins
cell_arcs.csv                # cell arc delay / variation
net_arcs.csv                 # net arc delay / variation
sp_attributes.csv            # startpoint arrival distribution
ep_attributes.csv            # endpoint required / reference result
clock_latency_timing_launch.rpt
pocvm_guardband.csv          # variation / guardband collateral
```

上列檔名可由公開的 [`src/core/insta.py`](https://github.com/NVlabs/INSTA/blob/main/src/core/insta.py) 與 [`src/io/parsers.py`](https://github.com/NVlabs/INSTA/blob/main/src/io/parsers.py)核對。它揭露了平台整合最值得參考的地方：**快速引擎的 cache key 必須包含 timing semantics，不只是 netlist hash**。同一份 netlist 若換了 SDC exception、library corner 或 POCV table，舊初始化便不再代表目前要 signoff 的問題。

合理的初始化 manifest 可以寫成下列形式。這是作者設計的最小契約，並非 INSTA 官方檔案格式：

```yaml
timing_snapshot: top-ss0p72v125c-func-r17
design:
  netlist_digest: sha256:<...>
  parasitic_digest: sha256:<...>
analysis:
  mode: functional
  corner: ss_0p72v_125c
  sdc_digest: sha256:<...>
  library_set_digest: sha256:<...>
  pocv_digest: sha256:<...>
reference:
  tool_release: <approved-release>
  export_recipe: <versioned-script>
insta:
  source_commit: <commit>
  input_bundle_digest: sha256:<...>
acceptance:
  endpoint_corr_floor: 0.995
  max_abs_slack_error_ps: <project-threshold>
```

這份 manifest 解決的不是重現 Docker image，而是回答「這個 proxy 對哪一個 timing problem 有效」。INSTA 的公開 Dockerfile 固定 Ubuntu 20.04、CUDA 11.8 與 Conda 環境，能改善軟體可重現性；但 container 並不包含商用 reference tool、設計 library 或匯出 recipe，也不能替 input bundle 證明正確。[公開安裝條件](https://github.com/NVlabs/INSTA/blob/main/README.md#note-key-requirements-for-pre-compiled-kernels)

## Top-K statistical propagation：保留會改變 CPPR 的候選來源

STA 在有 reconvergent paths 與 on-chip variation 時，不能只為每個節點保留一個最大 arrival。兩條候選路徑可能共享 launch clock path；若在 graph 中太早丟掉次佳候選，後面做 common-path pessimism removal（CPPR）時，就失去比較正確來源的資訊。INSTA 公開 README 指出其 GPU kernel 執行 Top-K statistical arrival propagation，固定 `K=256`，並處理 advanced-node OCV 下不可忽略的 CPPR。[README 的 Top-K 說明](https://github.com/NVlabs/INSTA#top-k-arrival-propagation-k-is-fixed-to-256)

公開實作會為每個 graph node 配置 rise／fall arrival mean、standard deviation、startpoint ID 與 max arrival 等 tensor；[`clear_timing_cache()`](https://github.com/NVlabs/INSTA/blob/main/src/timing/propagation.py) 顯示這些 tensor 的主要形狀是 `max_gid × topK`。levelization 後，同一層的 arcs 能批次送入 CUDA；cell arc 與 net arc 的 mean、std、sigma 及索引則先由 [`precompute_collaterals()`](https://github.com/NVlabs/INSTA/blob/main/src/timing/collaterals.py)整理。這把不規則 timing graph 轉成 GPU 較容易消化的分層 tensor 工作。

<figure>
  <a href="/images/eda/2026-10-01/insta-topk-propagation.svg"><img src="/images/eda/2026-10-01/insta-topk-propagation.svg" alt="Timing graph 依 level 展開，每個 pin 保存最多 256 組 rise 和 fall 的 arrival distribution 與 startpoint；GPU 批次傳播後在 endpoint 做 CPPR 與 slack 計算。" width="920" height="780" loading="lazy"></a>
  <figcaption>圖二：依據 INSTA 的 <a href="https://github.com/NVlabs/INSTA/blob/main/src/timing/propagation.py">tensor 配置</a>、<a href="https://github.com/NVlabs/INSTA/blob/main/src/timing/collaterals.py">collateral 預計算</a>與論文說明重繪；箭頭只表達資料相依，不代表實際 kernel 數量。</figcaption>
</figure>

這個機制的成本也很清楚。`K` 越大，越不容易過早丟掉之後可能因 CPPR 成為關鍵的候選，但記憶體與排序成本也隨之增加；`K=1` 便宜，卻無法等價保留多 startpoint 的 statistical competition。公開程式把一般 evaluation 的 Top-K propagation 和 differentiable propagation 分成兩條路：`do_eval_propagation()` 用 Top-K 評估 correlation；`do_diff_propagation()` 則建立可反向傳播的 timing path，README 範例用 `(-insta.tns).backward()` 取得 cell／net arc gradients。[公開 API](https://github.com/NVlabs/INSTA/blob/main/README.md#using-insta)

因此，平台不應把「gradient step 已改善」直接當作「Top-K signoff proxy 已改善」。較安全的分層是：gradient path 用來提出全域方向，Top-K evaluator 排序候選，reference tool 再驗證少量 finalists。這三層若共用相同 snapshot identity，才能知道誤差來自最佳化方向、快速 evaluator，還是 reference design state 已經改變。

### 一個 CPPR 小例子：第二名候選可能才是修正後的第一名

假設 endpoint `E` 有兩條 setup 候選。路徑 A 的原始 arrival 是 980 ps，包含 70 ps 可與 capture clock 共用的 pessimism；路徑 B 的原始 arrival 是 950 ps，只能移除 10 ps。若只按修正前 arrival 保留一條，A 會以 980 ps 勝出；完成 CPPR 後，A 變成 910 ps，B 則是 940 ps，真正較差的反而是 B。這是解釋資料需求的假設算例，不是 INSTA 論文 benchmark。

在 reconvergence、rise／fall、不同 launch clocks 與 statistical variation 同時存在時，候選數會迅速增加。Top-K 的角色不是枚舉所有完整 paths，而是在每個局部節點保留足夠多、且帶 startpoint 身分的 arrival 候選，使後面的 pessimism correction 還有選擇空間。`K=256` 是公開實作的固定值，不代表任何設計都已證明 256 必然足夠；平台仍需用 reference tool 檢查 critical endpoint 的 tail error，並觀察被 reference 判為關鍵的 path 是否曾在 proxy 內被過早剪掉。

這也說明只看 Pearson correlation 的盲點。若一百萬個非關鍵 endpoints 都很準，少數接近零 slack 的 endpoints 卻排序錯誤，整體 correlation 仍可能非常漂亮，ECO 決策卻會選錯目標。實務驗收應另加三個量：負 slack endpoints 的 recall、最差 N 條路徑的集合重疊，以及 slack error 的 p95／p99。這些門檻要按「用 proxy 做粗篩」或「用 proxy 直接驅動 sizing」分級；後者的錯誤成本更高，校準要求也應更嚴格。

## 可微分時序讓最佳化看到全域方向，但不替工具決定合法動作

常見 timing-driven optimization 會從最差 paths 或 violation endpoints 出發，逐步 sizing、buffering 或調整 placement。這種局部策略穩健且容易守住合法性，但大量 near-critical paths 同時競爭時，某一顆 cell 的改動可能改善一條路徑、惡化更多共享路徑。INSTA 將 TNS 對 cell arc 與 net arc delay 的梯度抽出，讓最佳化器能看到「哪一批 arcs 對全域 timing objective 最敏感」。

梯度不是 gate-sizing command。cell arc delay 的下降可以由換大 drive cell、降低負載、縮短線長或加入 buffer 達成，各方案對面積、功耗、routing、hold 與 DRC 的代價不同。INSTA-Size 必須把連續的 timing gradient 映射回離散 library cells；INSTA-Place 則把 net arc 敏感度轉為 placement 目標。論文摘要報告三組結果：

- 作為既有 industrial gate-sizing flow 的 evaluator，incremental `update_timing` runtime 約快 25 倍，且幾乎沒有 accuracy loss。
- INSTA-Size 相對 reference signoff engine 的 sizing 結果，最高改善 15% TNS，同時 sizing 的 cells 數量少 68%。
- INSTA-Place 在 ICCAD 2015 benchmark 上，相對一個 state-of-the-art net-weighting placer，最高改善 16% HPWL 與 59.4% TNS。

這些都是論文作者報告的特定 workload 結果，不是所有設計的保證。第一項採商用先進節點設計但未公開工具、完整 runtime 分布與所有 corner；第三項則是公開 benchmark，不能外推成 3 nm full-chip production 結果。[論文摘要與比較範圍](https://ieeexplore.ieee.org/document/11132858/)

把它接回工程平台時，可將一次候選更新寫成下列狀態轉移：

```text
VALIDATED_SNAPSHOT
  → gradient proposal
  → legal sizing / placement action
  → incremental parasitic + arc update
  → INSTA Top-K evaluation
  → candidate ranking
  → reference STA validation
  → ACCEPTED | REJECTED | SNAPSHOT_STALE
```

`legal sizing / placement action` 必須由 physical design tool 或有明確規則的 optimizer 負責，因為 timing gradient 不知道 row legality、cell availability、EM、IR、hold、clock 或 routing constraint。`reference STA validation` 也不能只重算單一 setup view：候選若改善 setup 卻造成 hold、功耗或壅塞退化，仍不得進入 release branch。

## 一個完整案例：從 size 候選到可交付 ECO

假設一個已 placement 的 block 在 functional slow corner 有 8,000 個 negative-slack endpoints。reference STA 先輸出與目前 netlist、寄生、SDC、library／POCV 對應的 INSTA input bundle；平台完成 initialization 後，以 endpoint correlation、worst slack error 和 critical-set overlap 驗收 snapshot。通過後才允許 optimizer 取得 gradients。

第一輪先求 `-TNS` 的 gradient，將敏感度映射到可替換的等功能 cell family，產生 200 個 legal upsizing 候選；實體工具完成合法化並更新受影響的 net delay。INSTA 快速傳播新 arrival，刪除 TNS 改善不足、WNS 惡化或修改 cells 過多的候選。保留的前 10 名再交給 reference STA 重算相關 view，並執行 hold、DRC、功耗與 routing 檢查。最後只有 evidence 完整的候選被寫成 ECO patch 與新的 checkpoint。

若以透明算例估算內圈效益：假設 reference incremental timing 每輪 2.5 秒，INSTA evaluator 每輪 0.1 秒，1,000 個候選的 timing evaluation 由 2,500 秒降為 100 秒，理想差距為 25 倍；再讓前 10 名回到 reference tool，各 2.5 秒，總 timing wall time 約 125 秒。這只是用論文「25 倍」關係建立的示範，不是 NVIDIA 實測重播；實際還包含 parasitic update、legalization、資料搬移、GPU 啟動、license queue 與多 view 驗收。

關鍵不在把 reference STA 呼叫降到零，而是把昂貴工具集中在模型建立與少量高價值候選。若每輪 netlist 改動都迫使完整重初始化，shadow engine 的固定成本會吃掉收益；若只改少數 arc 卻仍跑完整 graph，GPU 的 0.1 秒級傳播可能已足夠便宜。平台應量測 `snapshot build time`、`candidate update time`、`proxy evaluation time`、`reference validation time` 與 proxy rejection rate，而非只引用 propagation kernel 的單一數字。

### 接成服務時，工作單位應是 snapshot × candidate，而不是一個 Python process

公開範例以 Python 物件載入單一 design directory，適合研究重現；多人平台還需要明確的工作身分。最小 request 應包含 immutable snapshot ID、candidate patch、objective、analysis view、attempt ID 與輸出 schema。worker 回傳的不只是 WNS／TNS，也要列出實際載入的 snapshot digest、受影響 arcs、runtime、GPU 型號、程式 commit 與錯誤分類。缺一個必要輸入時應拒絕執行，不能悄悄改用工作目錄裡的預設檔。

候選 patch 也不宜直接傳一整份新 netlist。對 sizing，可用「instance → approved equivalent cell」表示；對 placement，可用 instance 座標差分並附合法化狀態；對 buffer insertion，則必須帶新 instances、nets 與命名規則。平台先驗證 patch 可套用到指定 base snapshot，再由 physical tool 產生新的寄生與 arc update。這能把「最佳化器提出什麼」與「工具實際接受什麼」分開，失敗時也能重播。

GPU 資源與 signoff license 的排程目標並不相同。INSTA worker 適合長駐 GPU 並重用 graph／tensor，降低反覆 initialization 與資料搬移；reference STA job 則受商用 license、memory 與 queue 管理。若每個 proxy candidate 都各自啟一個 container，啟動成本和重複 snapshot 載入可能淹沒 0.1 秒 propagation。較合理的控制方式，是依 snapshot affinity 將候選送到已載入該 snapshot 的 worker，批次完成後再把少量 finalists 送到 signoff queue。

這裡還有隔離需求。不同專案的 timing collateral 可能含設計名稱、階層與 library 特徵；共用 GPU service 要限制 worker 能讀取的 snapshot，輸出也不能跨專案進入 cache。公開 INSTA repository 沒有宣稱提供 multi-tenant authorization、scheduler、artifact store 或 license broker。把研究 kernel 產品化，主要工作會落在這些平台責任，而不是再包一層 REST API。

## INSTA 解決 timing 回饋速度，沒有封閉整個 R2G

這套方法最容易被過度延伸成「有了 signoff-accurate differentiable STA，就能自動完成 physical design」。公開證據支持的範圍比較窄：它加速已初始化 timing state 的 propagation，提供 timing gradients，並在 gate sizing 與 placement 實驗中展示效益。它沒有取代 global／detailed routing、extraction、SI、hold、EM／IR、DRC／LVS、formal equivalence 或多模式多 corner release management。

首先，net delay 不是只由兩個 cells 的座標決定。候選移動後，routing topology、coupling、buffering 與 congestion 可能改變；若 proxy 使用未更新或近似的 net arc，timing 速度再快也只是在分析舊物理狀態。其次，setup TNS 的 gradient 不會自動顧及 hold。放大一顆 cell 或重排路徑可能改善 slow corner setup，卻破壞 fast corner hold；若 objective 沒把多 view 納入，最佳化器會合理地犧牲未被計分的條件。

再者，signoff 工具的「準」是對指定輸入與分析設定而言。0.999 correlation 是論文所報案例結果，不是 API 的永久屬性；換設計、library、corner、clock architecture 或 export script 都應重新驗證。最後，gradient 只描述局部敏感度。當 cell replacement 造成離散跳變、routing congestion 改變拓樸，或 legalization 將 instance 推到遠處，線性方向不一定仍成立。平台應保存 proposal 前後的 predicted delta 與 reference delta，持續量測何時梯度開始失真。

這些限制不減少 INSTA 的價值，反而界定了正確插入點：在可合法產生候選、能快速更新物理近似、且外層仍有 deterministic signoff 的區段，縮短「提出 → 評估 → 淘汰」時間。它與先前的 [C3PO 佈局最佳化](/eda/2026/09/26/nvidia-c3po-concurrent-placement-r2g.html)形成具體接點：C3PO 需要連續的 timing／routability 回饋；INSTA 則示範如何讓較接近 signoff semantics 的 timing evaluator 進入同類內迴圈。兩篇都不能證明 NVIDIA 量產 flow 已按本文方式串接。

## 最危險的故障不是程式崩潰，而是 snapshot 靜悄悄過期

假設 optimizer 已跑 400 輪後，另一位工程師修正一條 multicycle path，library 團隊又更新某類 cells 的 POCV guardband；INSTA service 沒有收到事件，仍以舊 CSV 與 tensor cache 評分。它可以穩定輸出數值，correlation dashboard 甚至仍顯示初始化時的 0.999，但目前 reference problem 已變了。這種 silent staleness 比 crash 更危險，因為所有介面表面都正常。

<figure>
  <a href="/images/eda/2026-10-01/insta-stale-snapshot-recovery.svg"><img src="/images/eda/2026-10-01/insta-stale-snapshot-recovery.svg" alt="SDC、library 或寄生資料變更後，舊 INSTA snapshot 被標為 stale；進行中的候選隔離，重新由 reference tool 匯出、校準，再選擇重評估或捨棄。" width="920" height="760" loading="lazy"></a>
  <figcaption>圖三：作者設計的失效與恢復流程；INSTA 公開研究證明快速 timing 能力，未宣稱已提供這套多使用者 snapshot governance。</figcaption>
</figure>

故障點是權威 design state 與 shadow timing state 分岔。殘留物包括舊 graph、GPU tensors、已排名候選、optimizer trajectory 及可能已產生的 ECO patch。偵測至少要比較 snapshot manifest 與目前 resolved inputs；此外每隔固定候選數或當 critical set 大幅變動時，抽樣呼叫 reference STA，重新計算 slack correlation、max error 與 critical-set overlap。只比平均 correlation 仍可能漏掉最差 endpoints，因此 release gate 需檢查尾端誤差。

恢復時不要直接刪掉舊結果。先把舊 snapshot 與其候選標成 `stale` 並禁止 promote，保存足夠證據供 diff；由 reference tool 重新輸出受影響 corner 的 bundle，重建 graph／collaterals，再用一組固定 validation set 校準。若只有 optimizer 超參數改變而 timing snapshot 未變，可重用初始化；若 SDC、library、POCV、netlist topology 或 parasitic semantics 改變，應重新判定哪些 cache 可安全重用。公開程式能清理及重建 timing tensors，但沒有替多人流程實作上述 artifact lineage 與 promotion policy，這是平台層需補上的能力。[timing cache 實作](https://github.com/NVlabs/INSTA/blob/main/src/timing/propagation.py)

## 三種設計路線的取捨

| 路線 | 正確性來源 | 迭代延遲 | 維護成本 | 主要失效模式 | 適合位置 |
| --- | --- | ---: | ---: | --- | --- |
| 每輪直接呼叫 reference signoff | 同一套權威模型 | 最高，且受 license／queue 影響 | flow integration 較單純 | 探索數量不足、成本過高 | release gate、少量 finalists |
| INSTA 類校準式 statistical engine | reference snapshot + graph propagation | 低；論文報告最高 25× incremental timing 加速 | 需管理 export、snapshot、GPU 與再校準 | stale snapshot、未覆蓋的 view／constraint | sizing／placement 內迴圈 |
| 純 ML slack predictor | training data distribution | 推論可極低 | 需訓練、特徵、drift 與解釋治理 | OOD、critical-path topology 改變 | 粗篩、早期估算 |

INSTA 的工程吸引力在中間位置：它保留 timing graph 與 statistical propagation 的結構，因此比黑箱 predictor 容易指出哪個 arc 與 startpoint 造成結果；同時又透過 reference initialization 避開自行複製專有 delay semantics 的不切實際目標。代價是它不再是可脫離 reference tool 任意搬動的獨立 STA；reference export、版本相容與再校準成為正式平台介面。

## 六到十八個月最值得驗證的能力

第一個可複用能力是 **signoff-derived snapshot contract**：把 netlist、constraint、corner、variation 與匯出 recipe 綁成不可混用的 timing identity。第二個是 **多精度 evaluation ladder**：gradient proposal、Top-K proxy、reference validation 各自產生不同等級的 evidence。第三個才是 **GPU timing service**；若前兩者不存在，速度只會更快地產生不可追溯結果。

導入順序也應依風險遞增。第一階段只做 shadow evaluation：INSTA 讀取 reference snapshot、預測既有 ECO 的 timing delta，但不控制任何工具動作，用歷史 checkpoint 計算誤差分布。第二階段讓它排序由既有合法化工具產生的候選，工程師仍從 reference STA 結果決定採納。第三階段才允許 gradient 直接影響 sizing／placement proposal，而且要限制可動 cell family、最大移動距離、每輪修改數與可用 corner。任何階段若 critical-set recall 或 reference acceptance rate 下降，就退回前一層，而不是靠放寬門檻維持自動化率。

每次 release 建議保存四組 evidence。`snapshot evidence` 證明輸入、reference export 與 proxy calibration；`proposal evidence` 說明 objective、gradient 及候選 patch；`execution evidence` 記錄 physical tool 真正套用的變更與 parasitic update；`acceptance evidence` 則保存 reference STA、多 view 檢查及最後 checkpoint。這四組資料讓一次失敗可追到「模型過期、提案錯誤、工具未照提案執行」或「signoff 另有約束」，避免所有差異都被歸類成 AI 不準。

上線指標也要同時包含品質與成本：每千個候選節省多少 reference-tool 分鐘、finalists 的一次通過率、proxy 漏掉的關鍵 endpoint 數量、snapshot 平均有效期，以及一次重新校準要占用多少工程與運算資源。只追求候選吞吐量，可能讓 signoff queue 在後段承受更多低品質工作；只追求 correlation，又可能無法證明整體 turnaround time 確實縮短。

最終判斷應以完成可交付 ECO 所需的總時間與返工率為準。

最小實驗不必等待 3 nm full chip。選一個已有商用 STA 或 OpenSTA baseline 的中型 placed block，固定單一 setup view，建立 100–500 個 legal sizing candidates。比較三條路線：reference-only、簡單 criticality／net-weight heuristic、INSTA 類 snapshot evaluator。記錄初始化時間、單候選 latency、WNS／TNS 誤差、top-10 排名一致率、最後 reference tool 接受率與實際修改 cells 數量；再刻意注入一次 SDC exception 變更，確認舊 snapshot 會被拒絕。

支持導入的條件，是 proxy 在 critical endpoints 的尾端誤差受控、候選排序能穩定減少 reference calls，且 snapshot 失效可在錯誤 ECO 被 promote 前攔下。若初始化與資料轉換成本高於節省的迭代時間、不同 corner 需各自建立而無法管理、或 top candidates 經 reference tool 重排後幾乎失去相關性，就應停止把它當作 production inner loop。這個驗證會把「GPU STA 很快」轉成真正的平台決策：哪些設計變數可以放心高速探索，哪些承諾仍只能由 signoff 工具作出。

## 參考資料

1. [INSTA: An Ultra-Fast, Differentiable, Statistical Static Timing Analysis Engine for Industrial Physical Design Applications](https://research.nvidia.com/labs/electronic-design-automation/papers/yichen_INSTA_dac25.pdf) — Yi-Chen Lu et al., NVIDIA Research, DAC 2025。
2. [INSTA publication page](https://research.nvidia.com/labs/electronic-design-automation/publication/lu2025dac/) — NVIDIA Electronic Design Automation Research，2025 年 6 月；Best Paper Award。
3. [NVLabs/INSTA](https://github.com/NVlabs/INSTA) — NVIDIA 官方公開程式庫；README、Docker 環境、輸入 parser、timing graph 與 GPU propagation 實作。
4. [IEEE Xplore: INSTA](https://ieeexplore.ieee.org/document/11132858/) — 2025 ACM/IEEE Design Automation Conference，DOI 10.1109/DAC63849.2025.11132858；數值與 baseline 條件以摘要所載為準。
5. [NVIDIA Design Automation Research Group](https://research.nvidia.com/labs/electronic-design-automation/) — NVIDIA Research；研究範圍、INSTA 開源與 DAC 2025 獲獎紀錄。
