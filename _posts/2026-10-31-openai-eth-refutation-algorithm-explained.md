---
layout: post
title: "OpenAI 如何用精確計數演算法挑戰二十七年的 ETH 假說"
date: 2026-10-31 16:55:11 +0800
domain: ai-frontier
categories: ai-frontier
description: "從可手算的 SAT 範例出發，拆解 OpenAI 以共享線性摘要、低次多項式插值和張量收縮取得次指數時間的主張，並比較 Anthropic 的形式化成果及其對演算法與 EDA 的意義。"
takeaways:
  - who: "OpenAI"
    value: "OpenAI 公開一種精確計算固定子句寬度 k-CNF 滿足解數量的確定性演算法，藉由把跨群依賴壓縮成少量線性摘要，再利用多項式插值與張量收縮取得次指數時間界；若整體論證成立，便足以推翻 ETH。"
  - who: "Anthropic"
    value: "Anthropic 同期公開 Claude 獨立提出的次指數時間 3-SAT 演算法及 Lean 4 形式化，讓研究社群可以同時比較兩條構造路線；但兩份論文的機器驗證範圍、時間界與學術審查狀態仍須分開閱讀。"
  - who: "理論電腦科學研究者"
    value: "理論電腦科學研究者可將 ETH 作為前提得到的條件式困難性結論重新放回檢視，因為相關歸約仍然成立，但其下界解讀會隨假說被反駁而改變；後續工作將集中在簡化構造、移轉速度增益與辨認可保存的下界。"
  - who: "EDA 與 Formal 工程師"
    value: "EDA 與 Formal 工程師可以藉此重新審視 SAT、#SAT、計數與約束最佳化之間的演算法結構，但論文提供的是最壞情況的漸近上界；是否改善實際電路驗證、ATPG 或符號運算，仍須與現有 solver 的工作負載和常數成本比較。"
---

一個有數百萬個布林變數的設計驗證問題，往往讓工程師在「有沒有解」與「多久才能知道」之間做取捨。SAT solver 透過子句學習、傳播與啟發式搜尋，已能解決許多工業問題；但在理論上，某些輸入是否必須耗費指數級時間，始終是另一個問題。

2026 年 10 月 26 日，OpenAI 公開論文 *The Exponential Time Hypothesis is False*，宣稱為任意固定子句寬度的 k-SAT 找到次指數時間的確定性精確計數演算法。Anthropic 隨後發表 Claude 獨立提出的 3-SAT 論證。兩份成果都附上 Lean 形式化，並引發理論電腦科學界的公開檢視。[OpenAI 論文 §1](https://mathcommunity.github.io/oai-math-revised/papers/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf#page=2)、[OpenAI 公告](https://openai.com/index/building-scientific-understanding-with-academic-communities/)、[Anthropic 原始說明](https://github.com/anthropics/formal-math/blob/main/eth/README.md)。

沿下圖先抓住整條論證的因果鏈：原始問題是精確計數；演算法先把依賴變成可以分離的結構，再以代數工具回推原始答案。後面每一章會拆開其中一段。

![從 k-CNF 的滿足解計數開始，經過代數轉換、共享線性摘要與局部分組，再利用插值及張量收縮取得次指數時間的論文推導路徑](/images/ai-frontier/2026-10-31/eth-proof-roadmap.svg)

圖一：依據 [OpenAI 論文 §2–6 與 Appendix D](https://mathcommunity.github.io/oai-math-revised/papers/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf#page=7)整理的概念路徑。方塊表示數學構造間的關係，並非可直接照順序串接的程式模組。

## ETH 假設了什麼樣的計算極限

先用最小的邏輯式理解 SAT。布林變數只有 0 與 1；`∨` 表示 OR，`∧` 表示 AND，`¬` 表示 NOT。下面的公式有三個變數：

~~~text
F(a,b,c) = (a ∨ b) ∧ (¬a ∨ c)
~~~

若 `a=0`，第一個子句強制 `b=1`，`c` 有兩種選擇；若 `a=1`，第二個子句強制 `c=1`，`b` 也有兩種選擇。因此，八種指派中恰有四種滿足公式，寫成 `#F=4`。

SAT 只問 `#F>0`；**#SAT 要求回傳精確的 `#F`**。計數結果包含可滿足性資訊，所以一個可精確計數的演算法也能回答 SAT。對一般公式逐一檢查 `n` 個變數，最多要面對 `2^n` 種指派；每增加一個變數，搜尋空間便加倍。

3-CNF 是每個子句至多三個 literal 的合取式。1999 年提出、於 2001 年系統化發表的 **Exponential Time Hypothesis（ETH，指數時間假說）**，主張 3-SAT 在最壞情況下沒有 `2^{o(n)}` 時間的演算法。[Impagliazzo–Paturi](https://www.sciencedirect.com/science/article/pii/S0022000000917276)、[Impagliazzo–Paturi–Zane](https://cseweb.ucsd.edu/~paturi/myPapers/pubs/ImpagliazzoPaturiZane_2001_jcss.pdf)。

這裡必須分清三個量級：

| 時間量級 | 例子 | 演算法上的意思 |
| --- | --- | --- |
| 指數時間 | `2^n`、`1.3^n` | 指數仍是 `Θ(n)`，改善底數依然符合 ETH |
| 次指數時間 | `2^{n/√log n}` | 指數除以隨 `n` 成長的因子，屬於 `2^{o(n)}` |
| 多項式時間 | `n^3` | 比次指數更強的效率主張，足以涉及 P 與 NP 的核心問題 |

以 1999 年 Schöning 的隨機區域搜尋為例，其 3-SAT 時間界約為 `poly(n)·(4/3)^n`，已大幅優於暴力搜尋，但仍維持 `2^{Θ(n)}` 的形式。[Schöning, FOCS 1999](https://ieeexplore.ieee.org/document/814612)。ETH 就是在這條改良演算法的歷史之上，提出「是否存在無法跨越的指數下界」。

## OpenAI 宣稱跨越了哪一道牆

OpenAI 論文的 Theorem 1.1 對每個**固定** `k≥2`，給出一個可精確計算 k-CNF 滿足解數量的確定性演算法。以 `n` 個變數與 `m` 個子句表示，論文摘要把時間界概括為：

~~~text
T(n,m) = (n+m)^{O_k(1)} · 2^{n/(log n)^{1/2+o(1)}}
~~~

主文更明確地陳述一般情況為 `poly_k(n,m)·2^{O_k(n log log n / √log n)}`；若 `m≤Dn`，可得到 `poly(n,m)·2^{O_{k,D}(n/√log n)}`。對固定 `k`、固定 `D`，這些指數都是 `o(n)`。[論文 Theorem 1.1](https://mathcommunity.github.io/oai-math-revised/papers/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf#page=2)。

原理很直接：

~~~text
(n / √(log n)) / n = 1 / √(log n) → 0
~~~

因此，若演算法及其時間分析都成立，3-SAT 就具有 `2^{o(n)}` 演算法，與 ETH 直接矛盾。**論文攻擊的是最壞情況的漸近成長率**；複雜度符號中的常數、前置成本及大規模構造，都與實際執行時間有關。

## 把滿足解改寫為可以運算的多項式

第一個技術轉折，是把「滿足所有子句」改寫成代數求和。對一個 OR 子句，例如 `a∨¬b∨c`，定義滿足指示多項式：

~~~text
Φ(a,b,c) = 1 − (1−a)b(1−c)
~~~

當 `a,b,c∈{0,1}` 時，子句成立就有 `Φ=1`，否則 `Φ=0`。把所有子句相乘，只有同時滿足全部子句的指派會留下 `1`：

~~~text
#F = Σ_{x ∈ {0,1}ⁿ} Π_{e∈F} Φ_e(x)
~~~

這個等式完全精確，卻仍含有 `2^n` 個求和項。其用途是讓布林條件進入**線性代數、多項式變形與插值**的世界。[論文 §2.2，式 (2.2)](https://mathcommunity.github.io/oai-math-revised/papers/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf#page=8)。

假如所有子句天然分成幾群，且任一子句只使用其中一群的變數，計數便可分開做，再把群的答案相乘。例如 `(a∨b)∧(c∨d)` 的兩群各有三種合法指派，所以總共有 `3×3=9` 種。暴力枚舉全部四個變數需要考慮 16 種指派；兩群各枚舉四種，合計只需要八次局部指派檢查。一般化到 `r` 個、每群大小至多 `2n/r` 的群組，枚舉上界約為 `r·2^{2n/r}`。

但是實際公式大量交錯共享變數。硬把公式切群，跨群子句會使「各群計數相乘」失效。**論文的主要構造，就是讓原本耦合的公式在特定代數變形下可以分群處理。**

## 共享線性摘要如何切斷跨群依賴

先看一個可手算的假設算例：

~~~text
G = (a ∨ b) ∧ (b ∨ c) ∧ (c ∨ d)
~~~

把變數分成左群 `{a,b}`、右群 `{c,d}`。中間的 `(b∨c)` 連接兩群，所以直接把兩群的解數相乘會出錯。改為先固定共用狀態 `b`，局部問題就能分開：

| 固定的 `b` | 左群可行指派 | 右群可行指派 | 乘積 |
| --- | ---: | ---: | ---: |
| `0` | 1（`a=1`） | 2（`c=1`，`d` 任意） | 2 |
| `1` | 2（`a` 任意） | 3（`c∨d`） | 6 |
| 合計 | | | **8** |

這個例子的關鍵操作，是把原本跨群的相依，轉成少量共用量的枚舉。真正的演算法把共用量推廣成**線性測量** `y_g=C_g x_g`，其中 `x_g` 是第 `g` 群的變數向量、`C_g` 是整數矩陣。固定所有 `y_g` 後，變形後的每個子句可由其中一群的局部變數，以及其他群已固定的摘要值計算。[論文 §2.4，式 (2.5)–(2.6)](https://mathcommunity.github.io/oai-math-revised/papers/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf#page=10)。

![一條跨越左右變數群的子句讓計數無法直接相乘；固定共享測量後，各群局部加總，再將每種測量的乘積加總](/images/ai-frontier/2026-10-31/eth-shared-summary.svg)

圖二：依據 [OpenAI 論文 §2.4](https://mathcommunity.github.io/oai-math-revised/papers/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf#page=10)整理的計數分離機制；`b` 的小例子用於直覺說明，與論文正式構造使用的線性摘要不同。

其數學形式可以讀成：

~~~text
H(t) = Σ_y Π_{g=1}^r [Σ_{x_g:C_g x_g=y_g} A_g(x_g;y)]
~~~

括號內先算一群；群與群的結果相乘；最後加總所有共用測量。演算法時間主要受兩項控制：**每群要枚舉多少局部指派**，以及**共享測量有多少種可能值**。測量維度如果跟 `n` 一樣大，枚舉摘要仍可能回到原本的指數規模，所以低維摘要才是關鍵。

## 用低次多項式插值取回原始答案

第二個技術轉折更精巧：論文在參數 `T` 上建立一族變形公式 `H(T)`，要求 `T=0` 時恢復原始問題，也就是 `H(0)=#F`；而在 `T=1,2,…,Q` 時，變形公式具有上一節所需的分群與摘要結構。[論文 §2.3–2.5](https://mathcommunity.github.io/oai-math-revised/papers/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf#page=9)。

想像一個簡單的二次多項式 `h(T)=u+vT+wT²`。即使 `T=0` 不容易直接求值，只要在其他位置取得足夠資訊，就能用插值反推常數項 `u=h(0)`。一般情況的困難是：若 `H` 的次數太高，直接蒐集所有插值點也會花很大代價。

OpenAI 的方法讓每個變數出現位置使用低次的**替代線性形式**，再在容易計算的點讀取若干個 Taylor 係數；這類利用函數值及導數資訊的恢復方法，稱為 **Hermite interpolation**。若 `H` 的次數上限為 `3nR`，以 `Q` 個容易處理的點分攤，直觀上每點需要的局部係數數目約與 `nR/Q` 同階。[論文 §2.5，式 (2.4)、(2.7)–(2.9)](https://mathcommunity.github.io/oai-math-revised/papers/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf#page=11)。

要同時達成「易於分群」與「替代式次數低」，論文 §4 以矩陣的低秩結構、適當的分組與多項式係數構造，使其他群對某個子句的影響可以用少量測量表示。這不是單靠插值就能加速：**可插值的低次族與可分離的局部計數必須同時成立**。前者負責把答案取回，後者負責降低每個取樣點的成本。

論文 §2.6 把成本拆成三項：取得 Taylor 資料所需的局部修正、枚舉共用測量、枚舉單一變數群。參數 `Q`、替代式次數 `R`、群數 `r` 及摘要比例 `τ` 必須共同調整，才能讓總指數低於任何固定比例的 `n`。[論文式 (2.10)–(2.11)](https://mathcommunity.github.io/oai-math-revised/papers/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf#page=12)。

## 從任意 k-CNF 走到稀疏多項式計數

前面描述的直接分離方法，需要處理變數出現次數或子句密度。論文的完整路徑進一步使用**稀疏化與分支**，把一般 k-CNF 拆成可加總、彼此不重複的子問題，再把子句違反情形轉成有限域 `F₂` 上的稀疏多項式方程。[論文 §2.8–2.9、§5–6](https://mathcommunity.github.io/oai-math-revised/papers/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf#page=19)。

這一段很容易誤讀。把一個方程看成 `P_i(x)=0`，數學上是在計算所有方程的共同零點。論文 §6 並非把每個原始子句逐一轉成一條新方程，那樣方程總數仍可能過大；它透過短的 parity tests 與確定性選取，讓約 `O(n)` 條稀疏方程便能辨認滿足指派。其選取過程又會呼叫 §5 的精確計數器，逐步縮減仍誤通過的非滿足指派。[論文 §6.1–6.3](https://mathcommunity.github.io/oai-math-revised/papers/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf#page=40)。

這裡有兩個成本需要一起守住：一方面，方程要少且每條方程的 monomial 數量要小；另一方面，將方程轉為可計數的代數形式後，還要保有適當的總次數。若只追求方程數量減少，卻讓每條方程變成密集且極高次，仍然無法推出次指數演算法。

## Appendix D 利用張量收縮收緊時間界

OpenAI 論文主文已給出次指數時間的構造，Appendix D 再改用 **tensor network contraction（張量網路收縮）** 來得到較強的時間界。它把布林計數表示為由局部張量組成的網路；整體收縮等價於把內部索引全部求和，因而得到總計數。[論文 Appendix D](https://mathcommunity.github.io/oai-math-revised/papers/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf#page=54)。

最小例子是矩陣乘法中的共享索引：`Σ_j A_{ij}B_{jk}`。直接計算每個完整索引組合會很昂貴，但若能選好中間結果的合併順序，重複的局部計算便能共用。張量網路把這個思想推廣到許多局部因子的乘積與總和；網路的結構、切割方式及中間張量大小控制成本。

論文利用特定張量網路構造與收縮方式，在稀疏子句情況達成 `2^{O(n/√log n)}` 量級，在一般固定 `k` 的情況達成 `2^{O(n log log n/√log n)}` 量級，並維持多項式空間。這些是**論文宣稱的最壞情況漸近界**，尚非執行 SAT benchmark 的成績。

## Anthropic 的獨立結果與 Lean 實際檢查的內容

Anthropic 公開的 *A 2^{o(n)} Time Algorithm for 3-SAT* 宣稱，以確定性演算法在 `2^{O(n log log n/√log n)}` 時間內完成 #3-SAT。其 [README](https://github.com/anthropics/formal-math/blob/main/eth/README.md) 摘錄了一個張量網路的遞迴改善構想：把網路節點排列成格點，對跨線操作做代數分解，再選擇較便宜的收縮與重新分組方式，使收縮成本參數在放大問題規模時下降。兩家公司都說其模型在 10 月 16 日獨立取得結果。[Anthropic 原始論文](https://hexagonmath.org/2610.00577v1)。

兩份研究在目標上接近，但閱讀時應把**自然語言主文、Lean 定理陳述、Lean proof kernel 通過、外部研究者確認數學含義**分成四層。OpenAI 的 [Lean scope note 378](https://github.com/openai/math/blob/main/lean/docs/378.md) 明列：目前機器檢查的是固定 `k` 下 `poly(L)·2^{O_k(n(log log n)^2/√log n)}` 的計數界，`L` 是輸入編碼位元長度；論文較強的時間界尚需對照其額外推導。Anthropic 則表示 `MainResults.lean` 的形式化結果已由 Lean 4 檢查，並安排以獨立 kernel `nanoda` 再核對，但 repo 也提醒讀者：程式本身不會自動確認 Lean 的定理陳述與論文自然語言敘述相同。

| 檢查層次 | 能回答的問題 | 仍需額外做的工作 |
| --- | --- | --- |
| 公式與論文 | 演算法、時間界、假設如何陳述 | 逐項重建推導、核對模型 |
| Lean 定理 | 在形式系統中究竟宣稱什麼 | 對照自然語言問題定義 |
| Lean kernel | 證明項是否推出已陳述的定理 | 確認形式化與原始主張相符 |
| 獨立學術審查 | 整體主張能否由外部社群重現與接受 | 公開反例搜尋、簡化證明、交叉檢查 |

OpenAI 邀請 ETH 原始提出者 Russell Impagliazzo、Ramamohan Paturi，與 MIT 的 Ryan Williams 組織社群檢視。三人於 10 月 26 日的公開聲明明確表示，參與檢視**並不構成對結果的認證**。截至 10 月 31 日，公開資料顯示已有簡化講義、形式化重建與小型範例測試，尚無三人審查團隊的最終結論。[公開審查聲明](https://ethdiscussion.blog/category/uncategorized/)、[審查進度整理](https://papex.org/blog/eth-refutation-what-has-been-checked)。

## 推翻 ETH 之後哪些結論會改變

假設 ETH 最終被確認為假，最直接的變化是演算法下界的解讀。凡是寫成「**若 ETH 成立，則某問題在某個參數下需要指數時間**」的定理，原本的條件式邏輯仍正確；但其前提失效，便不能再藉此斷言該問題具有相同的實際困難程度。某些歸約也可能反過來提供新的演算法：若能把問題轉成大小僅線性增加的 SAT instance，就有機會繼承次指數時間界。[原始稀疏化與歸約論文](https://cseweb.ucsd.edu/~paturi/myPapers/pubs/ImpagliazzoPaturiZane_2001_jcss.pdf)。

這裡的規模保存十分重要。假設某問題的輸入規模是 `N`，歸約後 SAT 變數數量變成 `n=N²`，那麼 `2^{o(n)}` 只能推出 `2^{o(N²)}`，無法直接推出 `2^{o(N)}`。複雜度分類沿著歸約傳遞時，必須保留實際的參數膨脹。OpenAI 論文本身也特別提醒：一般多項式時間歸約不足以把所有 NP 問題都變成相同參數的次指數演算法。[論文 §1](https://mathcommunity.github.io/oai-math-revised/papers/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf#page=3)。

更長遠的研究問題，是這種代數分離能力能否延伸至一般 circuit、非固定寬度約束、最佳化以及計數以外的結構。若只能在特殊的局部因子網路裡壓低收縮成本，其應用便會相對集中；若能形成一般性的結構參數與演算法工具，相關領域就可能出現新的速度上界。

## EDA 工程會先受益於哪一類問題

SAT 與 #SAT 在晶片設計相關工作中分別對應不同需求。等價檢查、bounded model checking、部分 ATPG 流程主要關心是否有反例；design-space analysis、模型計數與機率評估則可能需要知道有多少組配置滿足限制。它們的形式化模型、量詞、位元向量與電路展開規模各不相同，直接把 SAT 複雜度改良換算成工具加速倍率，會忽略工作負載結構。

可採取三種不同的工程方向：

| 方向 | 可能得到的收穫 | 必須付出的成本 |
| --- | --- | --- |
| 現有 CDCL／SMT／Formal solver | 延續成熟的學習、傳播、incremental solving 與產業工作負載最佳化 | 最壞情況仍可能具有指數時間 |
| 代數計數與張量方法 | 探索可利用因子局部性、結構參數與共享中間結果的問題 | 張量收縮順序、記憶體與巨大常數可能吃掉優勢 |
| 混合式求解器 | 用現有 solver 化簡，再在特定子問題使用精確計數或代數分解 | 需要辨認何種 instance 值得切換與支付轉換成本 |

可以把實驗問題設得很具體：從公開的小型 RTL／Formal benchmark 產生 CNF，固定 `n`、`m`、子句寬度、連結程度、可滿足比例與編碼方式，對照現有 SAT solver、#SAT counter 與研究原型的 runtime、記憶體峰值以及結果一致性。若演算法論證首先只在極大 `n` 才展現漸近優勢，工程上最值得抽取的反而可能是**某種可移植的局部代數化簡策略**，而非立刻替換主求解器。

本站先前的 [Coding Agent 與 harness 機制研究]({% post_url 2026-10-07-harness-engineering-coding-agents %}) 討論模型輸出如何經過工具與外部結果檢查，才成為工程上可使用的工作成果。這次事件把相同問題推向數學研究：探索者可以是 AI，但可供後人使用的成果仍須有可重建的定義、演算法與正確性論證。

## 接下來一年可驗證的研究走向

到 2027 年 10 月，可以沿三條公開紀錄辨認這次突破究竟改變了多少電腦科學。第一，獨立學者是否完成定理敘述、計算模型與複雜度上界的逐項對照，並產生較短、可重建的證明。第二，是否有人將構造轉成可執行 solver，在明確界定的問題族上超越既有方法。第三，是否出現利用此算法的新型歸約或計數上界，而且轉換後的參數仍保有次指數改善。

也存在另一種走向：即使 ETH 的數學反例成立，過大的常數與特殊的構造成本仍讓產業求解器繼續以 CDCL、局部搜尋和問題特定最佳化為主。這種結果會保留理論突破的價值，同時限制短期工程影響；若未來出現可在實際 SAT／EDA 測試上穩定獲益的實作，才需要調整這項判斷。

OpenAI 與 Anthropic 這次共同呈現了一個新的研究流程：模型生成候選定理與演算法，形式化系統檢查其數學敘述，再由研究社群把結果轉成可以理解、延伸和挑戰的知識。最有力量的後續成果，將是研究者能以更短的證明、更好的演算法，回答原始論文尚未解決的「為什麼可以這麼快」。

## 證據範圍

- 本文導讀以 OpenAI 2026 年 10 月 25 日修訂的 67 頁論文為主，並輔以 Anthropic 10 月 27 日論文與兩方公開的 Lean 說明。主文的較強時間界、形式化檢查範圍和社群審查狀態分別列出；目前沒有把廠商主張當作已由獨立審查確立的定理。
- 分群枚舉與固定 `b` 的算例均屬教學用簡化模型，不是 OpenAI 正式的低次替代式、線性測量矩陣或完整張量收縮演算法；文章介紹的是核心機制與各章推導關係，並非對 67 頁全部引理的獨立數學驗算。
- `2^{o(n)}` 仍可能遠慢於現有求解器，也不代表 P=NP、不直接危及依賴其他困難性假設的密碼系統，或讓一般 NP 問題透過任意多項式歸約得到 `2^{o(N)}` 時間。
- 截至 2026 年 10 月 31 日，社群已有公開研討與部分重建工作，尚無三位審查召集人的最終正式認證；OpenAI 與 Anthropic 內部 AI 探索的具體實驗流程依各自披露描述。

## 參考資料

1. OpenAI, [*The Exponential Time Hypothesis is False*](https://mathcommunity.github.io/oai-math-revised/papers/The-Exponential-Time-Hypothesis-is-False-October-25-2026/paper.pdf)，2026 年 10 月 17 日初稿，10 月 25 日修訂，67 頁；主文 §2–6 與 Appendix D 為本文主要技術依據。
2. OpenAI, [*Working with academic communities to build scientific understanding*](https://openai.com/index/building-scientific-understanding-with-academic-communities/)，2026 年 10 月 26 日；公開合作與發表時序。
3. OpenAI, [Lean Scope Note 378](https://github.com/openai/math/blob/main/lean/docs/378.md)，形式化涵蓋的定理與較弱的時間界。
4. Anthropic, [*A 2^{o(n)} Time Algorithm for 3-SAT*](https://hexagonmath.org/2610.00577v1)，2026 年 10 月 27 日；[論文與 Lean 說明](https://github.com/anthropics/formal-math/blob/main/eth/README.md)。
5. Impagliazzo, Paturi, [*On the Complexity of k-SAT*](https://www.sciencedirect.com/science/article/pii/S0022000000917276)，JCSS，2001 年；ETH 的定義。
6. Impagliazzo, Paturi, Zane, [*Which Problems Have Strongly Exponential Complexity?*](https://cseweb.ucsd.edu/~paturi/myPapers/pubs/ImpagliazzoPaturiZane_2001_jcss.pdf)，JCSS，2001 年；稀疏化與細粒度歸約。
7. Schöning, [*A Probabilistic Algorithm for k-SAT and Constraint Satisfaction Problems*](https://ieeexplore.ieee.org/document/814612)，FOCS 1999；較早的指數時間改良演算法。
8. Impagliazzo, Paturi, Williams, [*ETH Refutation: Examination and Discussion*](https://ethdiscussion.blog/category/uncategorized/)，2026 年 10 月 26 日；獨立公開檢視聲明。
9. Papex, [*Has the ETH refutation been verified?*](https://papex.org/blog/eth-refutation-what-has-been-checked)，2026 年 10 月 31 日；社群檢視進度彙整。
