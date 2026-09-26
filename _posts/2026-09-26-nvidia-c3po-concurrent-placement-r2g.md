---
layout: post
title: "NVIDIA C3PO 把時序與壅塞放進同一輪全域佈局：R2G 驗收揭露的取捨"
date: 2026-09-26 12:11:33 +0800
domain: eda
categories: eda
description: "C3PO 以可微分 STA、RUDY 壅塞梯度與動態權重替換全域 placement，送回同一套商用後段流程驗收；部分案例線長下降卻有時序退化，說明平台需保存多目標與各階段證據。"
---

晶片的全域佈局若只追求線長短，很容易在時序或繞線階段付出代價。NVIDIA Research 的 **C3PO** 把 wirelength、cell density、時序與估計壅塞放進同一輪座標更新，並直接替換商用實體設計流程中的 global placement，再讓相同的 legalization、clock optimization、routing 與 route optimization 接手。這個接法讓「placement 指標漂亮」與「R2G 結果真的改善」可以分開檢查。[C3PO 原始論文，圖 1、表 III](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)

這是 Yi-Chen Lu 與 NVIDIA Research 等作者在 **ASP-DAC 2026** 發表的研究系統，不是 2026 年 9 月推出的商用產品，也沒有公開證據證明 NVIDIA 全公司的 ASIC 專案都採用它。論文有完整演算法、公開 benchmark 與商用後段工具的對照，但沒有開放該商用工具的名稱、完整 recipe 或私有設計。值得學的是：如何讓 placement 的優化訊號接近後段成本，以及如何在一個明確的工具邊界驗證它。[NVIDIA 論文頁](https://research.nvidia.com/labs/electronic-design-automation/publication/lu2026aspdac/)、[ASP-DAC 2026 議程](https://www.aspdac.com/aspdac2026/program/program-abstract.html)

## 從 floorplan 到 route，錯誤目標會被逐段放大

RTL 與 synthesis 交出 netlist，SDC、library、floorplan 與巨集限制決定哪些位置可用、哪些路徑需要多快。Global placement 此時要為大量標準元件和部分 macro 找座標；它還不是最終 legal placement，也沒有最終寄生參數。線長代理指標可以很快評分，卻無法保證 detailed routing 的 detour、buffer 與 clock tree 不會吃掉原來的好處。

一條 critical path 即使在 global placement 估計較短，也可能與其他 nets 爭用同一條走線通道。局部擁塞使繞線繞遠、電阻電容升高；工具再插 buffer、擴 cell，可能回頭擠壓密度及功耗。相反地，為了改善擁塞而一律 inflate cell、留出大片空白，又會拉長線。這不是單一權重能預先定對的靜態問題：元件每移動一次，RC、slew、criticality 與擁塞熱點都會變。[論文第 II–III 節](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)

本系列先前分析的 [AutoDMP](/eda/2026/09/24/nvidia-autodmp-r2g-design-platform.html) 解的是 macro placement 候選及工具參數搜尋，將少量候選送進後段比較。C3PO 面對另一個層級：**同一個 global placement run 裡，每輪如何移動 cells、如何平衡彼此牴觸的目標**。兩者都由 NVIDIA 研究提出，也都以後段 PPA 驗收，但論文沒有說它們已串成同一套內部平台；不能把研究系統拼成未公開的 production flow。[AutoDMP 論文](https://research.nvidia.com/publication/2023-03_autodmp-automated-dreamplace-based-macro-placement)、[C3PO 原文](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)

![C3PO 在 R2G 流程中的替換範圍](/images/eda/2026-09-26/c3po-flow-boundary.svg)

圖一：依據 [C3PO 論文圖 1、圖 2](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)重畫研究實驗的工具邊界；「相同下游 recipe」是論文的對照條件，不代表公開了 NVIDIA 內部完整 R2G 流程。

## 第一個機制：時序梯度要追到 cell 座標

常見 timing-driven placement 對 slack 不佳的 net 加權，再讓 wirelength 最佳化把這些 net 拉短。問題是同一 net 有多個 sink，某個非 critical 分支也可能改變 shared RC 與 input slew；單一 net weight 不知道移動哪個 cell 才真正改善 endpoint arrival。按 arc 加權較細，但若只看單段的局部代價，仍會失去 timing graph 上的連鎖效應。[論文表 I 與第 II-A 節](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)

C3PO 的輸入是 cell／pin 座標、net connectivity、library timing table，以及由實驗 flow 帶入的設計與製程條件。前向計算先為 net 建 rectilinear Steiner tree，再用 Elmore 模型求 net delay 與 slew；cell delay 由 Liberty 類型的 load／slew table 取得；沿 timing graph 傳播 arrival，形成 WNS／TNS。反向計算將目標對 net delay、cell arc、Steiner node 的變化一路傳回座標，得到移動某個 cell 對時序目標的方向。論文把相關 forward／backward 做成 CUDA kernel，核心是可微分的時序模型，**並非由 LLM 猜測擺放位置**。[論文第 III-B 節、圖 3](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)

這裡的「精確梯度」要讀準語境：它是相對於**論文採用的平滑模型與當輪拓撲**，不是對最終詳細繞線後的 signoff timing 做精確微分。Steiner topology 的生成本身不連續；作者用 FLUTE 決定節點，再把 Steiner 點上的梯度分給相鄰實際節點。當位置改變，拓撲需重算。多 fan-in 的 latest arrival 也用 temperature 為 0.1 的 log-sum-exp 平滑 hard max。若直接把這些近似當作真實 signoff，模型會在路徑切換或 routing detour 時失準。[論文式 (1)–(12)](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)

更細的一個選擇是 cell delay lookup。早期 placement 可能把元件擠在一起，產生 timing table 之外的 load／slew。簡單雙線性插值若在界外鉗到角落，梯度容易失去辨識力；C3PO 在相鄰表格值上解一個含交互項的多項式，取得對 load、slew 的偏導數。這仍須依原 library 的適用範圍理解；論文並未證明所有界外電氣狀態都物理有效。對平台而言，要保存不只一個 slack 數字，還包括 library 版本、clock／mode、當輪 cell 座標及模型例外，才有可能查明某次「改善」從何而來。[論文式 (6)–(11) 與表 I](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)

## 第二個機制：讓壅塞反饋成可移動的方向

壅塞估計不能等詳細繞線完成才回饋 placement；那時大部分座標已定。C3PO 以 RUDY 類指標，把 net 的 bounding box 覆蓋到 routing bins，估計每個 bin 的需求。net 的邊界、跨度與 bin overlap 都由 pin 座標決定，因此可以對 pin 位置求導。作者特別處理移動一個邊界 pin 造成 overlap 和分母 span 同時改變；若多個 pin 同占外框邊緣，就分配 max 函數的 subgradient。[論文第 III-C 節、式 (13)–(16)](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)

實際差異可以用一個簡化情境理解。假設兩條高扇出 net 的 bounding boxes 疊在狹窄通道上。只看 HPWL，移動某個 sink 向 source 靠近可能是好事；但若因此把外框壓到同一群 routing bins，局部 demand 反而提高。RUDY 梯度會提供另一個移動方向，讓求解器權衡「net 較短」與「熱區是否可繞」。這個情境是作者依演算法所作的說明，不是 NVIDIA 論文揭露的某顆產品內部案例。

與 cell inflation 相比，直接調整座標的優點是不必以整片空白換路由餘裕；代價是 RUDY 終究只是 routing demand proxy，沒有看見全部 layer、via、pin access 與 DRC 限制。論文在 FPU／DES 的示例中，相對 cell inflation 的 RouteOverflow 最多降低 45.4%，並宣稱 HPWL 代價很小；這是其指標與 benchmark 條件下的比較，不能換算成製程 signoff 的通過率。[論文圖 4 與第 III-C 節](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)

![時序與壅塞的座標梯度如何形成](/images/eda/2026-09-26/c3po-gradients.svg)

圖二：依據 [C3PO 論文圖 2、圖 3 與式 (13)–(16)](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)整理；虛線框強調模型近似與下游工具驗收的不同責任。

## 權重在每輪佈局都要重算

線長、密度、TNS／WNS 與 RouteOverflow 的單位不同，梯度量級也不同。手動給一組固定係數，換一個 design 或 placement 階段就可能失效。C3PO 先保留 wirelength 加 density 的主梯度 `g0`，再計算時序及壅塞等次目標的梯度 `gi`；依各梯度的內積構造矩陣，解一個加正則項的小型線性系統，最後將次目標權重限制為非負。換句話說，權重取決於**當輪梯度的方向關係**，不是單純將所有分數正規化後相加。[論文第 III-D 節、式 (17)–(24)](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)

例如時序梯度若與基本 placement 方向相近，給它權重較不容易破壞收斂；若它要求把 cells 推向嚴重密集區，系統需要壓制這個次目標。保留 `g0` 是關鍵工程限制：純粹的多目標最小範數解，可能讓數個次要目標互相抵銷，連密度都不再下降。正則化參數與初始 guidance vector 仍是設計選擇，不能把「省去手調一組 loss weight」擴張成「完全沒有參數，也保證每個 design 收斂」。[論文式 (17)–(24)](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)

更根本的限制是設計意圖仍由人與既有 flow 提供。求解器可以對既定 timing graph 求導，卻不能從 netlist 自行確定某個路徑究竟應視為 false path、multi-cycle path，或跨 clock domain 的異步關係。SDC 若錯了，精準的梯度會更有效率地優化一個錯誤問題。移植時，`constraint_mode`、`clock_definition`、`exception_set` 與 MMMC corner 必須是輸入契約的一部分；不同 corner 的代價如何聚合、哪些違例是 hard gate，要由設計團隊先給出決策。論文的公開資料不足以推定它支援任何特定公司內部的 MMMC signoff 政策。這也是讓 agent 參與此類流程時應先限制其權限的理由：可以建議候選和比較 report，不能為了讓目標函數好看而自行放寬設計者核准的 constraint。

這裡也能看出與 AutoDMP 不同的算力用法。AutoDMP 的外層搜索大量 run，再挑候選進昂貴後段；C3PO 在每個 run 內投資 GPU kernel 計算多個直接目標，試圖減少因錯誤 proxy 導致的無效候選。兩者成本模型不同：前者消耗較多平行實驗與後段評估，後者增加每輪 timing／routability 分析、GPU 記憶體及與既有工具的接線。若公司缺 GPU 而商用 placement 已足夠，替換核心求解器未必划算；若受限於少量可用 license，先提高候選品質可能有價值。這是平台取捨推論，不是論文的公司採購建議。[AutoDMP](https://research.nvidia.com/publication/2023-03_autodmp-automated-dreamplace-based-macro-placement)、[C3PO](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)

## 一次完整的 R2G 交接：ARIANE136

論文的 ARIANE136 benchmark 有約 113,000 個 cells、136 個 macros，以 ASAP7 研究製程條件執行。兩條路徑接受相同 design／floorplan：基準由商用工具做 global placement，實驗路徑改由 C3PO 同時擺 macro 與 standard cell；之後兩者走**相同的下游 recipe 與 seed**，比較 place-opt、clock-opt、route-opt 的結果。這是比僅比較 global-placement HPWL 更接近 R2G 的實驗；但它仍是公開 benchmark 與論文所用的商用 flow，不代表先進量產製程。[論文圖 1、表 III](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)

可將這個交接具體表示為一份平台**參考 manifest**，欄位是作者設計，並非 C3PO 公開 API：

```yaml
design: ARIANE136
input: {netlist_hash: "...", constraints_hash: "...", library_hash: "..."}
floorplan: {macro_count: 136, units: "...", blockages_hash: "..."}
global_place: {engine: C3PO, seed: "...", output_def_hash: "..."}
evaluation: {recipe_hash: "...", stages: [place_opt, clock_opt, route_opt]}
acceptance: {routed_wirelength_um: "...", wns_ns: "...",
             tns_ns: "...", violation_count: "..."}
```

資料流是 `netlist/constraints/floorplan → 求解座標 → placement artifact → 後段最佳化 → reports`。能寫入 `output_def_hash`，不表示該輸出已被接受；要等下一步的工具 report 及相同 baseline 比較。論文沒有公布這份 manifest、實際輸出檔名或商用 EDA 工具的私有介面，因此這裡只定義移植時應具備的可追溯契約，不冒充其內部實作。

結果也提醒我們別只挑漂亮的欄位。ARIANE136 的 route-opt routed wirelength 由 970,236 μm 降至 891,853 μm，約少 8.0%；switching power 由 40.06 mW 降至 36.58 mW。但 route-opt TNS 由 −0.035 ns 變成 −0.101 ns，違例 endpoint 數由 14 增至 38；其 WNS 則由 −0.008 ns 小幅變成 −0.007 ns。此處 route-opt 的時序結果**沒有全面改善**。另一個 ARIANE133 例子，route-opt 線長由 1,003,527 μm 到 921,253 μm，TNS 由 −0.009 ns 到 −0.004 ns，結果方向又不同。[論文表 III](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)

因此若設計的 release gate 包括 TNS 或違例數，ARIANE136 的這個候選不能只因線長與 switching power 較好就自動升為 golden。它可能值得保留給工程師做 ECO、調整時序權重或追加 route 分析；論文表格沒有揭露所有 signoff corner、DRC 或例外審核，不能據此宣布能 tape-out。這是根據表格所作的驗收推論，不是作者對該 benchmark 的正式 release 決策。

同一張表的 MEMPOOL 更能說明「平均改善」的陷阱。它有約 162,000 個 cells、20 個 macros；route-opt routed wirelength 由 1,400,162 μm 降至 1,346,411 μm，約 3.8%，但 TNS 由 −12.2k ns 到 −12.4k ns，違例 endpoint 由 18.1k 到 19.2k。FPU 的 routed wirelength 改善約 16.7%，route-opt WNS 由 −0.947 ns 略為惡化至 −0.950 ns，TNS 則由 −28.1 ns 到 −27.7 ns。不同設計、不同 metric 的符號不能被「PPA 更好」一句話抹平；WNS、TNS、違例數也不能用百分比互相抵銷。[論文表 III](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)

若設計團隊先定義目標為「routing 成本下降且不得新增 timing violation」，這些數據會產生不同的判斷：ARIANE133 值得進一步檢查其他 corner；ARIANE136 和 MEMPOOL 應留在候選區；FPU 則需要比對容許的 WNS margin 與統計變異。這是刻意選的一個**假設性驗收政策**，並非論文內建的門檻。對工程師而言，政策不能事後看見數字才改，否則同一批 placement 可以在不同報表裡被宣稱成功。平台至少要將實驗事前的 `objective`、`hard_gate`、`secondary_metric` 與版本一併保存，報表才有可比較的語意。

執行 trace 可以簡化成四個有責任人的轉移：`prepared`（設計與約束凍結）→ `candidate`（全域座標與輸出 hash）→ `evaluated`（商用後段所有階段及其 reports）→ `accepted/rejected`（事先約定的 gate）。如果 clock-opt 成功、route-opt 在 license timeout 中斷，這個 run 只能停在 `partial_evaluation`；不能用 clock-opt 的較佳 slack 代替 routed timing。若重試，應從可重用 checkpoint 接續，並記下工具版本與重試次數；若不能保證同 recipe、同 seed，就另立實驗編號。這條狀態機是作者設計的移植方案，其目的在防止跨階段偷換比較條件，不是 C3PO 論文公開的控制面。

![ARIANE136 的不同結果與驗收分支](/images/eda/2026-09-26/c3po-acceptance.svg)

圖三：左半數字取自 [C3PO 論文表 III 的 route-opt 行](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)；右半「候選／審查／不升版」是作者設計的 CAD 平台驗收分支。

## 故障後留下什麼，以及怎麼退回

考慮另一個**假設性**故障：global placement 的 job 用 netlist v17 與 SDC v8 產出座標，後段隊列延遲期間有人將 clock constraint 更新為 SDC v9；後段 worker 若只拿「最新 SDC」接上舊 DEF，仍可能跑出格式完整的 report，卻已不是原來同一組輸入的比較。壞在 handoff 身分，殘留物是 v17/v8 的 placement、v17/v9 的 route report，以及可能已排隊的其他衍生 jobs。

檢測方法是要求每一個 checkpoint、report 與結果列出 netlist、SDC、library、floorplan、recipe 版本與 hash。若 downstream inputs 與候選的 frozen manifest 不一致，就標記 `invalid_input_lineage`，不把該 run 算進 PPA 比較；保留舊結果供排查，將 v9 的相依 stage 重新排程，只有通過相同 manifest 的新結果才可晉級。這是作者提出的執行治理方案，C3PO 論文沒有描述其排程器或 rollback API。

另一種實際常見的失敗是 proxy 指標變好、route-opt 卻變差。前者需要版本鎖定及重跑；後者需要產品級 acceptance gate 與專家審查，**不能**靠 retry 原封不動的 job 修好。Placement artifact 已形成，仍不等於可以覆寫 golden placement。可採兩段發布：先把 C3PO 座標存為候選，再由完整相同的後段工具鏈生成 report，經 QoR／timing／DRC 門檻判定後才更新指向採用版本的指標。若發現負 slack，report 要保留當時的 corner、path group、setup／hold 類型與 violation endpoints，讓負責的工程師知道是同一條路徑惡化，還是新瓶頸浮現；只看總 TNS 無法決定修哪一個 constraint 或 placement。對宏觀變數和最終 signoff 未公開的地方，保證只能落在我們自己的流程契約，不是對 NVIDIA 研究系統的保證。

這個隔離還牽涉平行運行時的資源效率。若同一設計有十個候選，每個都從 synthesis 重跑到 routing，成本通常被重複的前段與後段 license-hour 主導；但直接共用「看似同名」的 checkpoint，又可能把錯誤的 library、floorplan 或 SDC 帶入另一個候選。可安全共享的單位是**內容相同且工具語意相容的輸入快照**；從 global placement 起，兩條分支的座標、後續優化及 reports 應分開保存。假設完整後段一個候選要 20 license-hour，十個候選是 200 license-hour；先用低成本 proxy 篩到兩個再完整驗收，理論上剩 40 license-hour，前提是 proxy 不會排除真正可行者。這是用明示假設的預算算例，沒有量測任何公司的授權消耗。

## 平台該換求解器，還是先把驗收做對

| 方案 | 優點 | 成本與延遲 | 正確性／維護代價 |
| --- | --- | --- | --- |
| 原商用 global placer，按既有 recipe 調參 | 原有工具與 signoff 接口成熟 | CPU／license 及大規模 sweep 可能昂貴 | 工具封閉；只看預設目標時可能忽略跨階段代價 |
| C3PO 類可微分多目標 placement，替換 global place | 時序、壅塞、線長同輪作用；研究報告 global placement 快 10–30 倍 | 需 GPU、kernel、timing／routing 模型與商用後段整合；論文說**完整 flow runtime 相近** | proxy 與真實 signoff 不同；移植要處理 library、corner、macro、legalization 與工具版本 |
| 保留既有 global place，先加統一候選驗收及實驗紀錄 | 最快釐清哪種目標真的影響 route-opt | 多一次完整後段評估與儲存成本 | 無法直接改善求解器，但能防止錯誤候選晉級 |

此表的研究速度與比較條件依 [論文表 III 的 runtime 註記](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)；第三列是作者方案。不要把 10–30 倍的 **global placement** 加速寫成 10–30 倍 tape-out 加速。論文使用一張 NVIDIA A100 96 GB、AMD EPYC 7742 與 2 TB RAM 的平台；表 II 顯示 MEMPOOL 的 timing update，C3PO 約 6.19 秒、DATE’25 方法約 717.3 秒，但這不是每個完整 APR job 的 elapsed time。[論文表 II 與實驗設定](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf)

而且「相同 seed」只降低一個變因，無法證明一次運行就刻畫了 run-to-run variation。論文的表格沒有多 seed 的置信區間，也沒有不同商用工具、不同節點與不同 PDK 的交叉試驗。合理的工程導入應先在自己可用的設計集做 paired comparison：固定 flow、corner 與資源，逐案記錄 WNS／TNS、違例數、route overflow、功耗、wirelength 和失敗率，再看改善是否跨設計一致。若只挑最優的一個 benchmark 報百分比，平台會傾向追求容易展示的代理分數，卻忽略真正昂貴的 rerun 與 signoff 風險。

如果只能投資一項 6–18 個月能力，我會先建**同設計版本、同 seed、同後段 recipe 的候選驗收契約**，讓 placement 的替換成為可控實驗。最小驗證不需私有 PDK：選一個公開宏與 standard cell benchmark，固定開源 library、SDC、工具版本和 seed，以基準 placement 與一個 timing／congestion aware placement 產生兩份候選，跑同一套 OpenROAD 後段；記錄 GP 指標、post-route WNS／TNS、wirelength、overflow、DRC 與 wall-clock。先問兩組候選的排序是否在 post-route 反轉，再決定是否值得投入求解器。開源結果只能驗證**平台契約與 proxy 的風險**，不能複製 C3PO 對商用工具或先進節點的效益。

這項驗證也能推翻我的建議：若多個不同 benchmark 的 GP 排名穩定預測 post-route，現有流程已完整保留輸入 lineage，且新增 gate 的延遲超過它避免的浪費，那就沒有理由先造另一層平台。反之，若 ARIANE136 這類線長改善與 timing 違例增加經常並存，下一步該接的是 placement→STA／routing 的可比較 report 與版本約束；將來再考慮讓 agent 調整允許的設計自由度。真正值得往下追的，是 [INSTA 的可微分 STA](https://research.nvidia.com/labs/electronic-design-automation/) 如何在較快的迴圈與 signoff 精度之間設定邊界。

## References

1. [C3PO: Commercial-Quality Global Placement via Coherent, Concurrent Timing, Routability, and Wirelength Optimization](https://hhsiao30.github.io/papers/yichen_apsdac26__Camera_Ready_eXpress.pdf) — Yi-Chen Lu 等，NVIDIA Research／ASP-DAC 2026，2026 年 1 月；作者保存的 camera-ready 原文。
2. [C3PO publication page](https://research.nvidia.com/labs/electronic-design-automation/publication/lu2026aspdac/) — NVIDIA Design Automation Research Group，2026 年 1 月。
3. [ASP-DAC 2026 Program Abstract](https://www.aspdac.com/aspdac2026/program/program-abstract.html) — ASP-DAC，2026 年 1 月，場次 5E-2。
4. [AutoDMP: Automated DREAMPlace-based Macro Placement](https://research.nvidia.com/publication/2023-03_autodmp-automated-dreamplace-based-macro-placement) — NVIDIA Research／ISPD 2023，2023 年 3 月；比較不同 placement 搜尋層級。
