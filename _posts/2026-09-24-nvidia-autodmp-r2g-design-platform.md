---
layout: post
title: "NVIDIA AutoDMP 的 R2G 整合：把巨集佈局探索接回真實 PPA"
date: 2026-09-24 15:23:08 +0800
domain: eda
categories: eda
description: "從 NVIDIA AutoDMP 的公開程式拆解 GPU 搜尋、候選 DEF 與實體後端的接點，分析兩層 PPA 評估、macro-only 取捨，以及研究流程移植成可靠 CAD 平台時需要補上的驗收機制。"
---

要把晶片設計平台做成能持續改善結果的系統，先得解決一個很現實的矛盾：便宜的評分不夠準，準確的評分又太貴。每一組 floorplan 都完整跑完 APR，探索次數會被時間與授權限制；只看線長或擁塞估計，又可能選出最後 timing 更差的佈局。

NVIDIA 的 **AutoDMP** 提供一個值得直接拆解的工程參考：GPU 上大量探索巨集與標準元件的佈局，保留不同取捨的候選，再送回既有實體設計流程驗收。第一作者 Anthony Agnesina、研究機構 NVIDIA，於 ISPD 2023 發表這項工作，並公開程式碼。它不是 NVIDIA 完整內部 CAD 平台，也不是 2026 年新發布的產品；可借鏡的是一個有實際程式入口與後端接法的設計探索系統。[研究與論文](https://research.nvidia.com/publication/2023-03_autodmp-automated-dreamplace-based-macro-placement)、[官方程式碼](https://github.com/NVlabs/AutoDMP)

## 從 SoC 整合往下，真正難的是物理條件互相牽制

假設一個 AI 加速器分區有多組運算單元、64 個 SRAM，以及連接它們的控制與資料路徑。邏輯整合完成，只代表連線與功能關係已經成立。把 SRAM 靠近運算單元可能減少線長，卻也可能擠掉標準元件的位置；替走線保留通道，又可能拉長某些關鍵路徑。這是本文的假設案例，不是 NVIDIA 某顆晶片的內部配置。

如果只讓各個 IP 各自得到漂亮的局部結果，整合時仍可能失敗。因為 SRAM 位置、pin orientation、可用金屬層、cell density 與後續 clock tree，會共同決定資料路徑究竟能不能實現。AutoDMP 論文處理的正是這類 mixed-size placement：巨集與標準元件一起考慮，而不是先把大型方塊塞進去，才讓剩下的邏輯自行找空間。[AutoDMP 論文，第 1–3 節](https://d1qx31qr3h6wln.cloudfront.net/publications/AutoDMP.pdf)

它的邊界也要講清楚：AutoDMP 不負責把所有 IP 自動組成 SoC，不會替專案決定 clock intent，也不是完整 signoff 系統。它提供的是可嵌入 RTL-to-GDS 流程的「實體探索子系統」。這種有明確輸入、輸出與責任範圍的能力，比一個宣稱什麼都做的平台名稱更容易接進現有方法。

<figure>
<img src="/images/eda/2026-09-24/autodmp-r2g-flow.svg" alt="AutoDMP 的實際整合邊界：既有 RTL 與約束先形成實體 checkpoint，GPU 探索輸出候選 DEF，再交給 CPU 上的實體設計流程驗收。" width="840" height="900" loading="lazy">
<figcaption>圖一：依據 <a href="https://github.com/NVlabs/AutoDMP/blob/866a1cb286a0c037ddf27feeeea1e12b68c9161c/scripts/genFlow.py">genFlow.py</a> 與 <a href="https://github.com/NVlabs/AutoDMP/blob/866a1cb286a0c037ddf27feeeea1e12b68c9161c/scripts/run_invs_AutoDMP.tcl">實體流程 Tcl</a> 整理；不是 NVIDIA 全公司 CAD 架構圖。</figcaption>
</figure>

## 公開程式把接點放在 checkpoint，而不是一句自然語言指令

先看真正的程式入口。`scripts/genFlow.py` 建立實驗目錄、準備 synthesis handoff，執行 PreDP，啟動調參工作，再把候選分別送進 PostDP。它區分是否使用經最佳化的 netlist，以及是否只保留 AutoDMP 的 macro placement；這些開關會改變後端如何接手，不能只視為方便命名的參數。[genFlow.py](https://github.com/NVlabs/AutoDMP/blob/866a1cb286a0c037ddf27feeeea1e12b68c9161c/scripts/genFlow.py)

`run_invs_AutoDMP.tcl` 的前段從 `syn_handoff` 取得 netlist 與 SDC，載入 library、MMMC、floorplan 等設定，匯出 Bookshelf 資料並保存 `preDP` checkpoint。後段重新載入該設計狀態，更新 constraint mode，讀入候選 DEF 的 component placement，修整巨集位置，接著完成供電網路、place-opt、CTS、routing 與 post-route optimization。[實體流程原碼](https://github.com/NVlabs/AutoDMP/blob/866a1cb286a0c037ddf27feeeea1e12b68c9161c/scripts/run_invs_AutoDMP.tcl)

這個接法的價值在於：外部搜尋器提出的是一份「在這個設計版本上可嘗試的佈局」，而不是取得整套 flow 的任意修改權。成熟工具仍然處理它擅長的 physical legalization、timing optimization 與 routing。資料交換有邊界，後端責任也沒有因加入 AI 而消失。

但格式相同不表示語意相同。DEF 中的座標必須對應正確的 instance、單位、orientation 與基準 netlist；搜尋器使用的 floorplan 也必須與驗收環境相容。平台整合最先要驗證的，通常是「這份候選究竟改了哪個設計」，而非模型用了多少參數。

## 兩個不同的最佳化迴圈，不能混成一個黑盒

內層是 placement 求解。把元件座標記成 `z=(x,y)`，可將目標概括為 `平滑線長(z) + λ × 密度懲罰(z)`。線長項傾向把相連元件拉近，密度項避免所有東西堆在同一區。DREAMPlace 以可微分計算與 GPU 加速求梯度；這不是讓神經網路直接猜出每個元件的位置。[DREAMPlace 與 AutoDMP 方法說明](https://developer.nvidia.com/blog/autodmp-optimizes-macro-placement-for-chip-design-with-ai-and-gpus/)

連續最佳化也不會自動滿足所有離散實作限制。AutoDMP 的 macro halo 做法，是搜尋時在巨集周圍預留空間，再於 legalization 前移除這些搜尋用的 padding，降低修整位置時對整體佈局的破壞。這種搜尋技巧不能取代製程或 IP 規定的實際 keepout；兩者的來源與驗收條件不同。[論文第 4.3.3 節](https://d1qx31qr3h6wln.cloudfront.net/publications/AutoDMP.pdf)

外層才是參數搜尋。AutoDMP 選取 16 個會影響求解結果的參數，以多目標 Bayesian optimization 探索。其 MOTPE 方法根據已有樣本的目標表現區分較好與較差區域，再調整下一批參數的取樣。也就是說，GPU 求解器處理龐大的座標空間，搜尋器處理較小的演算法設定空間，兩者不是同一種學習問題。[官方技術文章](https://developer.nvidia.com/blog/autodmp-optimizes-macro-placement-for-chip-design-with-ai-and-gpus/)

這個分工可直接用來檢查自己的平台設計：真正需要探索的是 floorplan 的物理自由度、工具參數，還是設計架構本身？若把這些全部交給同一個 agent 隨意改，最後即使 PPA 改善，也很難辨認改善來自哪個決策。先限制一輪實驗只改一種可解釋的自由度，才有辦法累積可信的經驗。

## 第一層留下不同取捨，第二層才回答工程結果

假設兩個候選，一個線長較短但局部擁塞較高，另一個線長稍長但走線空間較充足。太早把兩者壓成單一分數，就等於先決定「多少擁塞可以交換多少線長」。這個交換比例若沒有根據，最佳解很可能只是權重設定的產物。

AutoDMP 第一層使用線長、密度與擁塞等代理指標保留 Pareto 候選，再縮減候選數量，交給較昂貴的 EDA 後端。原研究的實驗流程每個設計搜尋 1,000 個點，再選 5 個候選進行後端評估。這些數字是該研究配置，不是任何專案都該照抄的預設值。[官方實驗流程](https://developer.nvidia.com/blog/autodmp-optimizes-macro-placement-for-chip-design-with-ai-and-gpus/)

代理指標的 Pareto front，不保證就是 routed PPA 的 Pareto front。簡化模型看不見的細節，可能在 buffer insertion、CTS、timing repair 或 routing 時才出現。第二層的意義是承認第一層不完整，而不是將第一層的最好分數換個名字稱為 signoff。

<figure>
<img src="/images/eda/2026-09-24/autodmp-two-level-evaluation.svg" alt="兩層評估：廉價代理指標產生多個互不支配候選，只有少量候選進入昂貴實體流程；代理指標排名可能與 routed PPA 不同。" width="840" height="780" loading="lazy">
<figcaption>圖二：依據 <a href="https://d1qx31qr3h6wln.cloudfront.net/publications/AutoDMP.pdf">AutoDMP 第 4.4 節</a> 整理。圖中的候選 A、B、C 僅為機制示意，不是論文量測值。</figcaption>
</figure>

這裡還有一個讀原碼才容易注意到的差異：`AutoDMP_utils.tcl` 的 `ppa_cost` 雖然保留 WNS、TNS、power 參數，但函式實際只使用線長、水平／垂直擁塞與 density。`load_candidate` 內的 power 與 timing 呼叫也被註解；因此這個 helper 的最低分，不能當成已經完成 timing／power 最佳化的證據。[候選評分原碼](https://github.com/NVlabs/AutoDMP/blob/866a1cb286a0c037ddf27feeeea1e12b68c9161c/scripts/AutoDMP_utils.tcl)

這不是說研究結果無效。論文中的完整實驗、外層產生多個候選 run 的 Python，以及單一 Tcl helper，各自負責不同層次。導入時必須把它們對起來。最容易出問題的方式，是只複製一個叫做 `ppa_cost` 的函式，就誤以為已經得到 PPA 閉環。

## 用一個小例子區分「被選中」與「可接受」

把前面的加速器分區固定在相同 netlist 與 floorplan，假設代理模型得到下表。線長是相對值，擁塞是示意分數，三者密度相同；所有數字都是為了說明判斷過程而建立，不是實際 EDA 結果。

| 候選 | 相對線長，越小越好 | 擁塞分數，越小越好 | 完整後端的最差 setup slack |
| --- | --- | --- | --- |
| A | 100 | 0.22 | −0.08 ns |
| B | 103 | 0.19 | +0.01 ns |
| C | 106 | 0.25 | 尚未評估 |

C 在兩個代理指標都輸給 A 與 B，第一層可以先不選它。A 與 B 則沒有誰全面勝出，值得分別進後端。假設正式驗收要求最差 setup slack 不小於零，最後只有 B 通過這一條；A 即使線較短，仍不能因平均分數漂亮而被接受。這裡刻意使用最差 setup slack，不把正 slack 寫成 WNS。

如果 B 的 hold、功耗或實體規則又不合格，它也只能停在候選狀態。平台因此需要分開保存兩種東西：搜尋使用的連續分數，以及必須同時成立的接受條件。前者讓探索器知道往哪裡走，後者決定一份結果能否交給下一個責任者。沒有可接受候選，本輪結論就是未達標，不應偷偷放寬 clock period 讓系統顯得成功。

這個區分也影響資料累積。工具 timeout 是沒有取得完整量測，不能記成零擁塞或零違例；候選匯入失敗是輸入問題，也不等於演算法的 PPA 特別差。把這些狀態全部塞進一個極差分數，搜尋器會把基礎設施故障學成設計規律，下一輪反而避開原本可能有價值的區域。

## 兩種後端接法，代價落在重用與修復之間

公開流程提供 `macrosOnly` 分支：只保留 macro 位置時，標準元件會被設為未放置，再由後端完整執行 place-opt；保留全體 placement 時，則以 incremental place-opt 接續。兩者都仍需要後端處理合法化、供電與時序等影響。[後端分支](https://github.com/NVlabs/AutoDMP/blob/866a1cb286a0c037ddf27feeeea1e12b68c9161c/scripts/run_invs_AutoDMP.tcl)

我的工程判斷是，初次導入更適合先試 macro-only。它犧牲部分既有 placement 結果，卻把標準元件最佳化留給團隊熟悉的 flow，較容易隔離問題。等到資料交換、實作條件與結果相關性都穩定，再比較保留全體 placement 能否省下足夠 runtime，且不增加後續修復代價。

無論選哪條路，都不能把「少跑一段」直接算成加速。如果省下 global placement，卻多花兩輪 route repair，整體仍可能更慢。比較單位應是取得一份符合相同驗收條件的結果，所需的總資源與等待時間，而不是單一 command 的 elapsed time。

## 從可跑的研究腳本，走到部門能共用的平台

AutoDMP 公開實作已能展示協調方式，但不是企業級執行環境的完整範本。`genFlow.py` 會複製 run directory、使用 Slurm wrapper、等待 `training.complete`，並啟動候選後端流程；它也包含廣泛的 `chmod 777` 與未全面檢查結果的 shell 呼叫。這些是可核對的研究腳本內容，不應原樣成為多專案共享環境的權限與成功判準。[協調程式](https://github.com/NVlabs/AutoDMP/blob/866a1cb286a0c037ddf27feeeea1e12b68c9161c/scripts/genFlow.py)

實際移植時，我會先補「候選與基準設計的綁定」，而非先換掉整套 orchestration。以下是作者提出的最小紀錄，不是 NVIDIA 已實作的 schema：

```yaml
candidate_id: demo-017
baseline:
  netlist_sha256: "<實際雜湊>"
  sdc_sha256: "<實際雜湊>"
  libraries_digest: "<實際版本摘要>"
  preplacement_checkpoint: "<不可變識別>"
proposal:
  component_def_sha256: "<實際雜湊>"
  mode: macros_only
  changed_instances: [sram_0, sram_1]
evaluation:
  flow_revision: "<已核准版本>"
  corner_set: "<已核准分析情境>"
  run_id: "<獨立執行識別>"
  status: awaiting_validation
```

假設搜尋期間，上游重新綜合而改了 SRAM instance 名稱。若候選只以目錄名稱對應，舊 DEF 可能被送進新 checkpoint；即使工具能繼續執行，結果也不再是原本那個實驗。檢查點應放在匯入前：比對 netlist 與 checkpoint 身分，確認巨集集合、master 與座標單位，再把不相容候選拒絕在邊界外。

恢復也不應靠「沿用還在的資料夾」。如果 route 工作中斷，保留輸入與失敗紀錄，以同一份不可變基準重建獨立 run；只在 flow 明確支援、且 checkpoint 與版本吻合時續跑。通過後再建立接受紀錄，不把部分生成的 report 或完成旗標當成工程驗收。

<figure>
<img src="/images/eda/2026-09-24/autodmp-candidate-validation.svg" alt="作者建議的候選驗收路徑：先比對基準與輸入，再執行既定後端和報告檢查；版本不符或工作失敗都不能晉升為已接受候選。" width="840" height="780" loading="lazy">
<figcaption>圖三：作者設計的移植驗收流程；問題背景來自 <a href="https://github.com/NVlabs/AutoDMP/blob/866a1cb286a0c037ddf27feeeea1e12b68c9161c/scripts/genFlow.py">AutoDMP run 協調</a> 與 <a href="https://github.com/NVlabs/AutoDMP/blob/866a1cb286a0c037ddf27feeeea1e12b68c9161c/scripts/run_invs_AutoDMP.tcl">checkpoint／DEF 接點</a>。圖中版本核對及接受紀錄是建議補強，不是原專案既有保證。</figcaption>
</figure>

還有一個容易漏掉的比較邊界：兩個候選即使最初來自同一份 RTL，經過不同的前處理、cell sizing 或 buffering，後端實際看到的 netlist 也可能不同。因此接受紀錄至少應能追到「匯入時」與「驗收時」的產物版本。若流程會修改邏輯，還必須依原有方法安排等價性檢查；placement 檔本身不提供這項保證。

同樣的 timing 數字，也要問它在哪個階段與哪組分析情境下產生。pre-CTS 的 clock 假設、post-CTS 的 clock 結果，以及 routing 前後的寄生估計，不能被收進同一欄便直接排序。若平台只保留最終一個 WNS，會失去判斷「哪個階段把候選變壞」所需的證據。先把 stage、corner、constraint set 與 tool revision 留完整，比增加更多漂亮的儀表板更有用。

## 算清楚節省了什麼，也算清楚可能漏掉什麼

以透明假設比較：有 80 組候選，每次完整後端需 8 小時、16 CPU cores，並假設各占一份授權資源。全部完整跑是 640 個授權占用小時、10,240 core-hours。若每個候選先用 3 GPU-minutes 篩選，只讓 8 個進完整後端，則變成 4 GPU-hours，加上 64 個授權占用小時與 1,024 core-hours。這是容量算例，並非 AutoDMP 或任何商用工具的實測。

CPU 與授權占用在這個假設下減少九成，但不能宣稱總成本也必定減少九成。還有 GPU 價格、資料準備、排隊、失敗重跑與維護成本；GPU-hours 和 CPU core-hours 也不能直接相加。更重要的是：若真正最好的候選在第一層被丟掉，少花錢同時也可能少得到有價值的結果。

因此比較基準不只該有「80 次全部完整跑」這種昂貴方案，也要有相同後端預算下的 random search，以及工程師既有 recipe。額外安排少量未入選候選做完整驗收，估計篩選的漏失風險。若代理排名與後端表現長期無關，應先修正代理模型或搜尋範圍，而不是把 GPU 數量加倍。

資源配置也要分成兩個池。GPU worker 可以快速產生候選，不代表 CPU 後端與授權能同速消化。若候選到達速度長期超過後端吞吐量，增加前端平行度只會拉長等待時間。移植時可先限制待驗收候選數，將完成驗收的速度反饋給搜尋預算；實際 admission policy 是平台新增責任，不是 AutoDMP 名稱本身提供的功能。

最後還要防止挑選偏差。探索組若從五份結果挑最好的一份，baseline 只跑一次，看到的差距同時包含方法與抽樣機會。比較可用同樣的後端次數與相同驗收條件，報告成功率、最佳值、中位數及總資源；至少跨幾個不同巨集比例與擁塞程度的分區。只有一個順手案例勝出，還不足以決定部門全面導入。

原研究對 270 萬 cells、320 macros 的設計報告約三小時的搜尋尺度；這不能解讀成三小時完成整顆 SoC 的 RTL-to-GDS，更不包含所有量產 signoff 工作。[NVIDIA 研究摘要](https://research.nvidia.com/publication/2023-03_autodmp-automated-dreamplace-based-macro-placement) 評估自己的結果時，也應把搜尋時間、候選後端時間與最終驗收時間分開記錄。

## 最值得搬回平台的，是分層評估與可替換的探索器

起步不必先重做公司所有 CAD infrastructure。挑一個巨集密集、基準 flow 已穩定的公開設計分區，固定 netlist、constraints、libraries 與後端設定，只比較既有 recipe、隨機參數搜尋、模型引導搜尋。先驗證候選能正確往返，再比較相同完整後端次數下的合法率、routed timing、資源與變異。

閱讀程式時，可以依序從 `genFlow.py` 的 PreDP／Tuner／PostDP 接點，追到 `run_invs_AutoDMP.tcl` 的 checkpoint 與 placement 分支，最後才看調參器。上游 README 說明了 NVDLA 範例、兩個平行 worker 的小型搜尋，以及對 TILOS MacroPlacement 資料和 flow 的依賴；不是 clone 後就已擁有商用工具、完整 PDK 或所有實驗材料。[建置與測試說明](https://github.com/NVlabs/AutoDMP/blob/866a1cb286a0c037ddf27feeeea1e12b68c9161c/README.md)、[調參 master／worker 入口](https://github.com/NVlabs/AutoDMP/blob/866a1cb286a0c037ddf27feeeea1e12b68c9161c/tuner/run_tuner.sh)

AI 的角色也可以更精確：從歷史候選建議下一組參數、整理失敗原因，或提出待審核的搜尋空間。基準 SDC、合法性要求與接受條件仍由既有工程責任者控制。最小驗證若連不用 LLM 都無法穩定比較，加上一個 agent 只會讓因果更難追。

NVIDIA 在 ASP-DAC 2026 的 C3PO 研究，進一步以 timing、routability 與 wirelength 的共同最佳化為題；它與 AutoDMP 的外層探索不是同一套方法，也不能據此假定兩者已整合或同樣開源。[C3PO 官方發表頁](https://research.nvidia.com/labs/electronic-design-automation/publication/lu2026aspdac/) 對平台而言，這提示一個可持續的方向：求解器會演進，但資料接點、比較基準與結果驗收，必須讓不同方法仍能公平競爭。

未來六到十八個月，值得累積的三項能力是：讓候選精確對應設計版本、讓便宜模型與完整後端之間有可量測的相關性、讓搜尋器能替換而不必重寫整條 flow。具備這三點後，才有條件回答某個新 AI 方法究竟改善了工程結果，還是只是更快產生更多實驗。

## 參考資料

1. [AutoDMP: Automated DREAMPlace-based Macro Placement](https://d1qx31qr3h6wln.cloudfront.net/publications/AutoDMP.pdf) — Anthony Agnesina 等，NVIDIA，ISPD 2023；DOI: 10.1145/3569052.3578923。
2. [AutoDMP Optimizes Macro Placement for Chip Design with AI and GPUs](https://developer.nvidia.com/blog/autodmp-optimizes-macro-placement-for-chip-design-with-ai-and-gpus/) — NVIDIA Technical Blog，2023-03-27。
3. [AutoDMP 官方 repository 與 README](https://github.com/NVlabs/AutoDMP/blob/866a1cb286a0c037ddf27feeeea1e12b68c9161c/README.md) — NVIDIA；本文程式分析固定於 commit `866a1cb286a0c037ddf27feeeea1e12b68c9161c`，不以查閱時間冒充發表時間。
4. [genFlow.py](https://github.com/NVlabs/AutoDMP/blob/866a1cb286a0c037ddf27feeeea1e12b68c9161c/scripts/genFlow.py) — NVIDIA，流程生成、run directory、候選執行協調。
5. [run_invs_AutoDMP.tcl](https://github.com/NVlabs/AutoDMP/blob/866a1cb286a0c037ddf27feeeea1e12b68c9161c/scripts/run_invs_AutoDMP.tcl) — NVIDIA，PreDP／PostDP、DEF 與實體後端接點。
6. [AutoDMP_utils.tcl](https://github.com/NVlabs/AutoDMP/blob/866a1cb286a0c037ddf27feeeea1e12b68c9161c/scripts/AutoDMP_utils.tcl) — NVIDIA，候選載入與 proxy cost 實作。
7. [run_tuner.sh](https://github.com/NVlabs/AutoDMP/blob/866a1cb286a0c037ddf27feeeea1e12b68c9161c/tuner/run_tuner.sh) — NVIDIA，搜尋 master 與 worker 啟動介面。
8. [C3PO: Commercial-Quality Global Placement via Coherent, Concurrent Timing, Routability, and Wirelength Optimization](https://research.nvidia.com/labs/electronic-design-automation/publication/lu2026aspdac/) — Yi-Chen Lu 等，NVIDIA 研究發表頁，ASP-DAC 2026；僅用於後續研究方向對照。
