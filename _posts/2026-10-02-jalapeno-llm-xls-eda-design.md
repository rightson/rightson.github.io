---
layout: post
title: "Jalapeño 用通用模型探索設計，XLS 與 EDA 接手成果驗證"
date: 2026-10-02 02:53:27 +0800
domain: ic-design-platform
categories: ic-design-platform
permalink: /ic-design-platform/2026/10/02/jalapeno-llm-xls-eda-design.html
description: "Richard Ho 的採訪說明通用模型如何協助硬體原始碼最佳化；XLS 語意、獨立驗證與 EDA signoff 決定候選能否交付，資料在地性、封裝及 fleet 彈性則牽動系統取捨。"
---

通用 LLM 已經可以參與晶片設計的原始碼最佳化，工程團隊的競爭力因此多了一個來源：把前沿模型接到既有 EDA 流程，讓模型協助探索，再用工程證據決定是否採用。Richard Ho 在 Ian Cutress 的採訪中描述 OpenAI 開發 Jalapeño 的經驗：團隊使用未針對這項硬體任務微調的內部模型，處理設計中的面積與效能問題；他舉出一個節省超過 13% die area 的案例，同時強調仍使用標準 EDA 流程完成 signoff。[採訪來源](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

晶片設計原本就依賴分工：架構決定計算與資料如何配置，前段把需求變成可驗證的邏輯，後段把邏輯放進製程與實體限制，封裝再把運算、記憶體及介面連成系統。當開發速度、效能目標與面積預算同時吃緊，局部修改可能牽動多個階段。LLM 的機會在於協助閱讀跨模組的設計意圖、找出可改寫的位置；它提出的候選仍要回到這條交付鏈。

這篇採訪還把設計方法連到資料中心策略：XLS 提供較接近軟體的硬體描述，NUMA 凸顯資料在地性，封裝擴大系統設計空間，而可跨推論階段使用的加速器保留了整個 fleet 的調度彈性。本文以採訪為主要技術來源，並由這篇 [Facebook 觀點貼文](https://www.facebook.com/share/p/1CEZyFpDTh/?mibextid=wwXIfr)提出的九項觀察延伸分析；另附[相關影片](https://youtu.be/8s7uYtCM1bc)。以下的機制解釋、假設算例與工程建議為作者整理或推論；圖中未公開的流程細節均標為作者參考設計。

<figure>
<a href="/images/ic-design-platform/2026-10-02/jalapeno-design-flow.svg"><img src="/images/ic-design-platform/2026-10-02/jalapeno-design-flow.svg" alt="工程師固定規格、版本與目標，LLM 提出 XLS 程式碼候選，compiler 產生 RTL；功能驗證與 EDA 實作提供證據，由工程師決定採納，失敗候選回到探索。" width="600" height="1050"></a>
<figcaption>圖一：作者參考流程。依<a href="https://morethanmoore.substack.com/p/interview-with-richard-ho-openai">採訪</a>所述的模型最佳化、XLS 與標準 EDA signoff，以及<a href="https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/README.md">XLS 官方工具鏈</a>整理；版本固定、驗收順序與回退連線為作者設計，非 OpenAI 公開內部架構。</figcaption>
</figure>

沿圖往下看，模型輸出的是候選修改；compiler、驗證與實作才逐步回答候選是否可用。這個責任分配能解釋為什麼未做 IC 設計專用微調的模型仍可能有價值，也能解釋為什麼模型再強都不能自行宣告 tapeout。

## 13% 面積改善與九個月時程，分母決定了結論

Ho 描述的起因很具體：團隊依模擬與邏輯面積估計設定效能目標，後來發現設計無法完全放進預定空間，必須考慮犧牲效能。他們轉向模型尋找最佳化方法，並報告一個節省超過 13% die area 的例子。這是受訪者報告的工程成果，節錄未提供原始 netlist、面積報告、製程、corner 或可重現的對照實驗。[採訪：機器學習輔助設計段落](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

因此，13% 可以支持「模型協助找到了有實質價值的修改」，不能直接換算成每顆晶片成本下降 13%。必須先知道比較的是哪一版設計、同樣的效能限制是否成立、量測在何階段完成，以及哪些固定面積不會跟著邏輯一起縮小。記憶體、I/O、實體留白或封裝限制都可能改變最後收益；本文不替 Jalapeño 補造這些未披露條件。

一個**假設算例**能說明範圍的重要性。若原始面積為 100 個任意面積單位，其中可改寫邏輯占 40，其他部分固定為 60；可改寫部分縮小 13%，全體只降到 94.8，改善是 5.2%。若 13% 本來就以整顆 die 為分母，則是降到 87。兩者回答不同問題。這個算例不是重解釋 Ho 的數字，而是說明讀面積成果時必須保留分母。

九個月開發時程也需要起訖點：從架構定案、RTL 開始、第一次 tapeout，或拿到可用矽晶片，會得到不同的週期。現有採訪節錄支持「模型使團隊更快接近效能目標」，但沒有交代九個月的定義與未使用模型的對照週期。因此，九個月不能被當成已量測的 AI 加速倍率，更不能把全部時程壓縮歸因於 LLM。[採訪：時程與效能取捨段落](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

工程上值得追問的是：模型減少了哪一段關鍵路徑？少一次原始碼重寫、少一次實作迭代，與平行跑更多候選，會留下不同證據。總週期還受 IP 取得、驗證、後段收斂和製造限制影響。只有知道哪些等待被消除，才可能判斷另一家公司能否重現收益。

## 未做硬體專用微調，仍需要一套使用方法

Ho 回答模型是否微調時，表示使用原始模型，許多是比公開版本稍微領先的內部模型。他也說團隊請機器學習研究人員協助找出取得最佳結果的方法。兩個陳述應一起讀：模型沒有針對這個設計任務再微調，使用過程仍有研究與工程 know-how。[採訪：模型與 EDA 夥伴段落](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

「沒有 IC 設計專用微調」不等於「從未接受任何 post-training」。通用模型本身可能經過指令與推理能力的後訓練，採訪節錄沒有公開完整訓練歷程；不能由這個回答推斷所用模型是只有預訓練的 base model。同樣地，內部版本稍微領先公開模型，也不保證今天隨便選一個公開 LLM，就能得到相同面積與週期改善。

作者判斷，這個案例削弱了「必須等 EDA 廠商完成各模組 AI 化，設計公司才有收益」的假設。IDM 或 fabless 團隊可以先評估獨立前沿 LLM 與現有流程的組合。不過，可採用的模型只是起點：要挑選可修改的設計範圍、提供足夠上下文、保留驗收規則，並把修改交回工具執行。這些能力決定模型建議能否變成工程成果。

Ho 認為其內部模型在相關工作上比 EDA 公司提供的方案強，這是他的使用觀察，沒有附上跨廠商、相同設計與預算的公開 benchmark。它可以形成研究問題，不能被擴大成「LLM 全面勝過 EDA」；雙方甚至可能負責不同層次，一邊產生原始碼候選，一邊解決實體實作或數值分析。[採訪：內部模型的評價](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

| 導入方式 | 適合的工程情境 | 團隊要付出的代價 |
| --- | --- | --- |
| 獨立 LLM 接既有 EDA | 需要跨程式碼與設計意圖提出新候選，且能自行建立驗收 | 維護上下文、執行介面、版本與結果追溯 |
| EDA 內建 AI 功能 | 搜尋變數與工具資料緊密相連，已有可比較的分析目標 | 核對功能範圍、資料可攜性與工具版本限制 |
| 既有 compiler／專用最佳化器 | 問題已形式化，合法變換與目標相對穩定 | 搜尋範圍較固定，跨規格推理需由工程師補足 |

表一：作者對導入選擇的比較，非三種方法在 Jalapeño 上的實測。通用模型、工具內建 AI 與專用最佳化可以共存；選擇應取決於問題位置與完整交付成本。

## XLS 把模型的修改接到可檢查的硬體語意

Ho 說團隊大量使用 XLS，許多模型最佳化發生在 XLS 程式碼上；較接近 Rust 的語法與語意，讓軟體背景的工程師與模型較容易理解。這提供了一個關鍵機制：改變模型操作的抽象層，可能比先增加領域微調更快打開可用的搜尋空間。[採訪：XLS 段落](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

官方文件將 **XLS（Accelerated HW Synthesis）**定位為高階硬體綜合工具鏈，可從高階功能描述產生可綜合的 Verilog／SystemVerilog。這裡要區分工具鏈與語言：**DSLX** 是其中受 Rust 啟發、以不可變運算式與資料流為中心的語言，具有固定大小物件、任意位元寬度等硬體特性；它不是一般 Rust 程式直接轉成晶片。[XLS README](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/README.md)、[DSLX Reference](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/dslx_reference.md)

具體路徑是 DSLX 描述功能，轉成 XLS IR，經最佳化及排程，再生成 RTL。XLS IR 保留資料流與固定寬度型別；排程決定運算放在哪個 pipeline stage，code generation 將結果轉成具有 ports、registers 等 RTL 物件的 block。官方也提供 IR 求值、等價檢查與 Verilog 生成工具。[IR 語意](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/ir_semantics.md)、[工具索引](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/tools.md)

高階表示的收益，在於模型可以先思考運算的關係，而不用同時手寫每個暫存器與控制細節。例如兩個分支是否可以共用運算、某個位元寬度是否足夠、條件判斷能否前移，都是可提出的候選。但共用資源可能增加 mux 與控制相依，縮窄位元也可能丟掉合法輸入；「程式碼更短」沒有自行保證面積更小。

這裡有兩個互補機制。第一，明確型別與資料流讓部分語意能被 compiler 或 solver 檢查，模型的自然語言理由不再是唯一依據。第二，把 pipeline 與實體結果交回工具量測，能發現高階等價修改的物理代價。抽象層提高探索效率，驗收仍必須穿過抽象層。

這也說明 XLS 的邊界。純函式描述輸入到輸出的映射；有狀態的 proc 還要處理跨時間狀態與 channel 通訊，最後 block 才具體表示 RTL。函式等價不自動證明 reset、backpressure、整合 latency 與協定行為全部正確。不同抽象層各自有檢查義務，不能只拿一份高階測試通過就放行整顆晶片。[XLS 的 function／proc／block 定義](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/ir_semantics.md)

## 從模型候選到 signoff，不能共用一個「正確率」

Ho 明確表示短期內不認為模型會取代 EDA，仍以標準 EDA 流程 signoff。他用數億個 gates 的設計說明，即使模型號稱 99.99% 正確，也不足以直接 tape out。這是一個規模與責任的提醒，並非一項模型準確率測試。[採訪：模型限制與驗證段落](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

若把三億個 gates 與萬分之一失誤率機械式相乘，會得到三萬。**這只能當作說明尺度的算術，不能當成晶片 bug 預測**：模型建議的錯誤率、gate 數與實際失效並不是獨立同分布的事件。工程驗收需要回答特定設計性質是否成立，不能用平均正確率覆蓋少數致命反例。

Ho 還提到，有些模型最佳化在當下未被團隊完全理解，快速推進的壓力使完整驗證更重要。作者認為，這應改變工作的分配：工程師可以縮短手工探索時間，卻要維持規格、輸入假設與採納責任。模型產生修改與模型解釋修改，可能共享同一個錯誤前提；第二次詢問模型不能取代獨立工具證據。[採訪：未完全理解的原始碼最佳化](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

下面用一個**作者設計的假設案例**走完這條路徑。某個運算單元將兩個 16-bit unsigned 輸入相加，輸出定義為完整 17-bit 結果。模型因觀察到測試資料數值偏小，建議先在 16-bit 寬度相加，再擴充到 17-bit，希望減少邏輯。對小數值它可能看起來完全正確，對 65,535 加 1 卻會先溢位成零；正確結果應是 65,536。

第一步固定規格與 baseline，明確禁止模型把輸入限制改成「總和不超過 65,535」。第二步保存候選，將原設計與候選依相同型別語意求值，加入邊界值；適用時用等價檢查找反例。若 proof 未完成或 timeout，就保持未知，不把沒有找到反例當成通過。XLS 官方工具可以提供 IR 求值與 IR 等價檢查，但其可處理範圍仍要依實際設計核對。[XLS 求值與等價工具](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/tools.md)

第三步是恢復：留下失敗候選、完整輸入與反例，不更新已核准設計；模型可以再提出「先把兩個 operand 擴充，再做 17-bit 加法」的修正。新候選是新版本，重新檢查後才量測 PPA。這不是一次宣稱已執行的 XLS 實驗，數值反例只是可直接重算的型別語意案例。

<figure>
<a href="/images/ic-design-platform/2026-10-02/jalapeno-candidate-acceptance.svg"><img src="/images/ic-design-platform/2026-10-02/jalapeno-candidate-acceptance.svg" alt="16-bit 先加後擴充丟失進位；語意驗證保留反例與舊版本，先擴充再相加的新候選重新驗證，通過後才進行 PPA 與整合驗收。" width="600" height="880" loading="lazy"></a>
<figcaption>圖二：作者假設案例與驗收設計，非 Jalapeño 實際電路。固定寬度運算與工具能力參考<a href="https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/dslx_reference.md">DSLX Reference</a>及<a href="https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/tools.md">XLS Tools</a>；沒有宣稱已完成工具實測。</figcaption>
</figure>

第四步回到同一份實作條件。功能正確的候選還要經 synthesis、實體實作與適用的時序／功耗檢查；必要的整合、DFT、實體與封裝驗收仍由對應 owner 負責。若面積縮小卻使時序失敗，或者上游修改已改變介面，就不能沿用上一版本的放行報告。此處為作者提出的交付方法，不是採訪已揭露的 OpenAI 工具清單。

這與本站[配置式設計管理的分析](/ic-design-platform/2026/09/30/nvidia-gdp-multivendor-design-source-of-truth.html)可以銜接：模型讓候選數量增加，配置管理則讓每份結果回到確定的輸入。探索能力越強，越需要防止「候選甲的面積改善」與「候選乙的正確性報告」被拼成不存在的成功設計。

## 類比風險提醒我們，驗證方法必須符合物理問題

採訪中，Ho 把類比部分與訊號完整性列為較難確定的風險，並談到 Broadcom 的相關專長。這支持「數位最佳化的成功不能直接外推到類比與實體介面」，卻不足以證明 AI 完全無法協助類比設計。[採訪：FPGA 與矽晶片對應、類比風險](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

作者解讀是，工程師的物理經驗仍有重要位置：離散邏輯測試沒有覆蓋的問題，不能靠增加同類測試就自動解決。若風險涉及訊號完整性，驗收要能對應相關物理模型與量測；若是數位協定，則要回到交易與時序語意。哪些方法能夠提供足夠證據，取決於問題本身。

Ho 對工具供應商提出的 PCIe 控制器挑戰，正好把這個門檻具體化：符合需求，同時比團隊更快、更好、面積更小，並滿足 PPA。採訪沒有界定 controller 邏輯、PHY、各世代規格與量測條件，所以不能把這段話當成涵蓋所有數位與類比介面的正式 benchmark。[採訪：PCIe 工具評估](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

可操作的測試應先固定交付範圍，再量「到達可驗收結果的時間」。生成幾百行可編譯程式碼與交付一個符合需求的 IP，差距就在約束、反例、實體證據和整合責任。這也是 EDA 廠商仍能提供價值的地方：把候選變成可靠交付的成本，並不會因模型能力進步而消失。

## 一顆涵蓋多種推論階段的晶片，保留 fleet 的選擇權

Cutress 問到業界常討論的 prefill、speculative decoding 與完整 decode 分工。Ho 的回答從整個資料中心 fleet 出發：一旦把硬體固定分配給某一階段，資本支出與電力配置也跟著被鎖住；工作負載與模型比例變動後，原先買好的比例未必合適。他因此偏好能涵蓋較廣工作範圍、可在不同負載間調度的裝置。[採訪：推論分工與同質硬體](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

這是**推論領域內的泛化**，不能擴大為「Jalapeño 像 GPU 一樣支援所有運算工作」。Ho 所說的涵蓋 Pareto 範圍，是架構選擇的主張；節錄沒有提供跨模型、跨階段的完整效能曲線。他也承認正式部署後可能辨識出目前看不出的效率代價。既有 fleet 仍會使用 CPU 與 GPU，並不等於整個資料中心只剩一種處理器。

用一個**假設容量模型**看這個取捨：兩種工作 P、D 各配置 50 單位專用容量，總需求為 100。若需求變成 P=70、D=30，且兩種容量不能互換，實際最多服務 50+30=80，仍有 20 單位閒置。若 100 單位共用容量都能服務兩種工作，即使每單位有效能力因泛用設計降為 0.9，也可能服務 90。

這個算例假設工作可在同一尺度衡量、兩者能獨立排程，沒有計入資料搬移、記憶體容量與服務延遲限制；它不是 Jalapeño 的效能模型。它只說明局部單位效率與 fleet 利用率可以往不同方向走。專用硬體在比例穩定時可能更好，共用硬體在需求易變時可能更有彈性；部署評估要把兩者放進同一套需求情境。

## NUMA 的方向，是讓資料位置成為可利用的成本差異

Ho 說 NUMA 是正確方向，甚至預期 GPU 團隊可能採取類似路線。技術上，NUMA 的區別是**存取成本隨發起端與記憶體位置而變**；UMA 指較一致的記憶體存取模型，並不是「一塊實體記憶體邏輯切給不同處理器」。記憶體是否共享、位址空間是否統一、快取是否一致，還要分開討論。[採訪：NUMA 段落](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)、[Linux：What is NUMA?](https://github.com/torvalds/linux/blob/d24e8ac715de2e16a53c144005b1863660a5fbea/Documentation/mm/numa.rst)

Linux 的文件用多個 cell、local memory 與互連說明 NUMA，強調要取得可擴展頻寬，多數存取必須落在本地或較近的記憶體。這提供一般機制背景，不能據此宣稱 Jalapeño 採用 Linux 式 ccNUMA、一致性協定或特定實體拓樸。採訪節錄沒有提供這些細節。

NUMA 的收益也不能只從硬體方塊推導。作者認為，若運算分區與常用資料一起放在較近的資源，能減少遠端流量；如果 runtime 把工作移走卻把資料留在原處，local memory 就失去作用。模型切分、權重配置、KV cache 的生命週期與排程，需要共同決定哪些資料值得搬、何時搬，以及搬移能否被之後的重用攤平。

<figure>
<a href="/images/ic-design-platform/2026-10-02/jalapeno-locality-tradeoff.svg"><img src="/images/ic-design-platform/2026-10-02/jalapeno-locality-tradeoff.svg" alt="兩個運算區域各有本地記憶體；同區存取較近，跨區存取經互連。移動計算卻留下資料會增加遠端存取，複製資料則消耗容量與搬移時間。" width="600" height="740" loading="lazy"></a>
<figcaption>圖三：作者 NUMA 概念圖，非 Jalapeño 官方拓樸，不表示實測延遲、頻寬或快取一致性。定義依<a href="https://github.com/torvalds/linux/blob/d24e8ac715de2e16a53c144005b1863660a5fbea/Documentation/mm/numa.rst">Linux NUMA 文件</a>，與採訪架構主張的連結為作者分析。</figcaption>
</figure>

一個**假設串行存取模型**：本地延遲 100 ns、遠端 300 ns，若 80% 存取為本地，平均是 140 ns；本地比例降到 50%，平均升到 200 ns。真實加速器有平行請求、預取、快取與排隊，不能直接拿這個平均當吞吐預測。但它足以展示在地性是執行條件，不是硬體名稱。

要驗證 NUMA 是否有利，至少要一起觀察本地命中比例、遠端流量、互連壅塞、每個區域的容量壓力與服務時間。固定資料位置有利於重用，卻可能形成負載不均；移動或複製資料有利於平衡，又增加容量與一致性管理成本。Ho 的方向值得研究，實際優勢仍要落到 workload 與軟體映射的證據。

## 封裝擴大設計空間，也重新界定合作夥伴的價值

Ho 把當前稱為封裝的黃金時代，談到 wafer、panel、光學元件，以及如何把元件有效整合。他描述 OpenAI 直接與記憶體供應商溝通，因為團隊負責高層系統規劃，會討論需要什麼記憶體、如何配置與平衡；Broadcom 則提供重要 IP、合作經驗及取得大量供應的能力。[採訪：記憶體、封裝與合作夥伴](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

作者的技術解讀是，架構邊界正在超出單顆邏輯 die。計算放在哪裡、資料在哪裡、介面可提供什麼，以及封裝能如何連接，必須一起考慮。若本地記憶體能改善存取，還要確認對應容量、連線與系統限制是否允許；因此封裝會影響架構可實現的選項，不能只在 RTL 完成後才被當成組裝問題。

這些陳述支持 OpenAI 保有相當程度的系統與高層設計主導權，也支持其團隊直接參與原始碼最佳化。**它們沒有證明 OpenAI 包辦全部 front-end／RTL，也沒有證明 Broadcom 只做 physical design。**採訪明確談到 Broadcom 的 IP、介面專長與供應取得，將其角色縮成後段實作反而會漏掉已披露的價值。

對 turnkey 模式的影響，可以提出有條件的產業推論：當客戶自己掌握架構與部分前段工程能力，服務商可包辦的範圍可能改變，價值分配也可能轉向 IP、實體整合、封裝與供應鏈。但採訪未公開合約、工作範圍、定價與利潤，不能由設計主導權直接推導 Broadcom 附加價值或獲利下降。技術分工與商業結果之間，仍需要另一組證據。

## 下一個可驗證問題：公開模型能否降低完整設計迭代成本

這篇採訪提供的新認知，是通用模型、可檢查的高階硬體表示，以及既有 EDA 驗收，可以組成一條有工程價值的設計路徑。對設計團隊而言，可以現在就評估前沿 LLM；對 EDA 廠商而言，需要證明整合方案能降低完整交付成本；對 ASIC 夥伴而言，客戶設計能力與 IP、實體及供應能力如何互補，比「全包或只做後段」的二分法更接近問題。

下一個實驗應固定一個可公開的硬體模組、規格、compiler 與實作條件，比較工程師既有方法、獨立公開 LLM，以及可取得的工具內建方案。記錄合法候選比例、等價失敗、PPA、工具耗時、工程師介入，以及到達相同驗收門檻的總時間。若總時間下降且證據完整，才開始擴大到更多模組；若只增加候選數與說明文字，則還沒有重現 Jalapeño 經驗的工程收益。

## 參考資料

1. [Interview with Richard Ho, OpenAI](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai) — Ian Cutress，More than Moore。本文依所提供的採訪中譯節錄轉述；原刊日期及未附入的段落未核實，不將其標為本日新事件。13% 為受訪者報告，沒有公開重現資料。
2. [XLS README](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/README.md) — Google XLS 官方 repository；版本 `1f1e152a856d`。用於工具鏈定位，不能據此外推 OpenAI 採用同一版本。
3. [DSLX Reference](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/dslx_reference.md)、[IR Semantics](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/ir_semantics.md)、[XLS Tools](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/tools.md) — 同一 XLS 版本的語言、抽象層與求值／等價／生成介面。
4. [觀點來源：Facebook 貼文](https://www.facebook.com/share/p/1CEZyFpDTh/?mibextid=wwXIfr) — 九項觀察的來源連結；本文不將其中的產業推論當成受訪者已證實的事實。貼文作者與發布日期未核實。
5. [相關影片](https://youtu.be/8s7uYtCM1bc) — 使用者提供的影片來源，未逐段核對字幕與時間碼；本文採訪轉述仍以所提供中譯節錄為依據。
6. [What is NUMA?](https://github.com/torvalds/linux/blob/d24e8ac715de2e16a53c144005b1863660a5fbea/Documentation/mm/numa.rst) — Linux 官方文件；版本 `d24e8ac715de`。文件註明起始於 1999 年 11 月；用於一般定義，不代表 Jalapeño 實作。
