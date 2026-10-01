---
layout: post
title: "Jalapeño 用通用模型探索設計，XLS 與 EDA 接手成果驗證"
date: 2026-10-02 02:53:27 +0800
domain: ic-design-platform
categories: ic-design-platform
permalink: /ic-design-platform/2026/10/02/jalapeno-llm-xls-eda-design.html
description: "Jalapeño 由軟體工作負載決定架構，以通用模型與 XLS 加快設計探索，再經 EDA、bring-up 與量產驗證交付；NUMA 映射、benchmark 條件與機群調度共同決定實際收益。"
---

Jalapeño 的開發經驗顯示，通用 LLM 可以協助晶片原始碼最佳化，收益卻要放回軟體與硬體共同決策的流程衡量：先確認工作負載能映射到架構，再用模型加快探索，以 EDA 與完整驗證採納候選，最後在矽晶片及資料中心機群中檢驗成果。Richard Ho 在 Ian Cutress 的採訪中報告一個節省超過 13% die area 的案例，使用的內部模型未針對該硬體任務微調，signoff 仍走標準 EDA 流程。[採訪來源](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

晶片設計原本就依賴分工：架構決定計算與資料配置，前段把需求變成可驗證邏輯，後段在製程與物理限制下實作，封裝連接運算、記憶體與介面。LLM 與 agent 的工作組成快速變動，卻要由開發週期長、投入後難以改動的硬體承接。這個落差使可程式性、設計速度及軟體可實作性成為同一個問題；局部面積改善只是其中一段。

本文以 More than Moore 的 Richard Ho 採訪為主要技術來源，刊出日期依補充整理為 **2026 年 9 月 30 日**；[YouTube 錄影](https://youtu.be/8s7uYtCM1bc)與文章是同一場訪談，不算兩份獨立佐證。最初的九項觀察來自這篇 [Facebook 貼文](https://www.facebook.com/share/p/1CEZyFpDTh/?mibextid=wwXIfr)。訪談內容依中譯節錄與補充整理轉述，技術補充另連結官方文件；以下的假設算例、驗收流程與未公開連線均標為作者分析或參考設計。

<figure>
<a href="/images/ic-design-platform/2026-10-02/jalapeno-design-flow.svg"><img src="/images/ic-design-platform/2026-10-02/jalapeno-design-flow.svg" alt="工程師固定規格、版本與目標，LLM 提出 XLS 程式碼候選，compiler 產生 RTL；功能驗證與 EDA 實作提供證據，由工程師決定採納，失敗候選回到探索。" width="600" height="1050"></a>
<figcaption>圖一：作者參考流程。依<a href="https://morethanmoore.substack.com/p/interview-with-richard-ho-openai">採訪</a>所述的模型最佳化、XLS 與標準 EDA signoff，以及<a href="https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/README.md">XLS 官方工具鏈</a>整理；版本固定、驗收順序與回退連線為作者設計，非 OpenAI 公開內部架構。</figcaption>
</figure>

沿圖往下看，模型輸出的是候選修改；compiler、驗證與實作才逐步回答候選是否可用。這個責任分配能解釋為什麼未做 IC 設計專用微調的模型仍可能有價值，也能解釋為什麼模型再強都不能自行宣告 tapeout。

## 架構定案前，先讓編譯器、kernel 與推論團隊走通

採訪前言的整理將 Jalapeño 定位為**推論加速器**，Broadcom 是設計夥伴，Celestica 負責板卡與機架整合。這裡的推論用途也包含研究與訓練流程中的模型執行；它不能被概括成只服務終端使用者。Ho 提到 reasoning 與強化學習迴圈讓推論需求的重要性浮現，工作負載的變化直接影響架構重心。[採訪：架構動機與前言](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

下列規格依採訪前言的補充整理列出，屬來源報告，未在本文重現量測。它們用來界定討論尺度，不能取代模型服務效能。

| 範圍 | 採訪整理所列規格 | 判讀時要保留的條件 |
| --- | --- | --- |
| 單顆裝置 | 一顆運算 die、一顆 I/O chiplet；216 GiB HBM4、15.4 TB/s | 容量與標稱頻寬不代表全部 kernel 都能有效使用 |
| 功耗 | 峰值 700 W，持續運作約 550 W | 測試負載、量測邊界與平均窗口仍需核對 |
| 系統範圍 | 128 顆構成一個 local domain，2,048 顆構成一套系統 | Local domain 不能自行推定為快取一致性或故障隔離範圍 |
| 運算峰值 | 2,048 顆系統在 FP4 下約 27 EFLOP/s | 低精度運算峰值不能直接換算成合格輸出 tokens/s |

表二：依[採訪前言](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)的補充整理，非本文實測；單顆功耗與整套系統算力不可混用分母。

Ho 描述，架構定案前的主要利害關係人是 compiler、kernel 最佳化與推論團隊，團隊以快速且準確的模擬器展示預期效果，讓軟體端先認同再推進。硬體與研究團隊同處一地、共用會議與資訊，降低了需求往返的距離。這是公開訪談中的協作方式，不代表模擬器原始碼、誤差範圍或全部內部介面已公開。[採訪：軟體先行與組織協作](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

作者認為，這個順序能提早暴露三種不同失敗：運算可表達但 compiler 難以映射，映射成功但 kernel 無法取得預期效率，局部 kernel 很快但整個服務被資料搬移或排程拖慢。若只展示一個理想算子的峰值，這些問題會延後到架構難以修改時才浮現。因此架構評估的交付物應包括代表性模型、映射策略、kernel 路徑與服務假設，讓下一階段知道效能承諾基於什麼。

可程式性也有具體代價：保留選項可能增加控制、儲存與編譯器工作，固定功能則可能有較高局部效率。Ho 從 TPU 經驗提出避免過度擬合單一模型的教訓；作者將它理解為讓新工作負載有可承接的路徑。這不保證未來所有模型都能有效映射，也不代表每個功能都應做成可程式。[採訪：刻意避開的陷阱](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

## 13% 面積改善與九個月時程，分母決定了結論

Ho 描述的起因很具體：團隊依模擬與邏輯面積估計設定效能目標，後來發現設計無法完全放進預定空間，必須考慮犧牲效能。他們轉向模型尋找最佳化方法，並報告一個節省超過 13% die area 的例子。這是受訪者報告的工程成果，節錄未提供原始 netlist、面積報告、製程、corner 或可重現的對照實驗。[採訪：機器學習輔助設計段落](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

因此，13% 可以支持「模型協助找到了有實質價值的修改」，不能直接換算成每顆晶片成本下降 13%。必須先知道比較的是哪一版設計、同樣的效能限制是否成立、量測在何階段完成，以及哪些固定面積不會跟著邏輯一起縮小。記憶體、I/O、實體留白或封裝限制都可能改變最後收益；本文不替 Jalapeño 補造這些未披露條件。

一個**假設算例**能說明範圍的重要性。若原始面積為 100 個任意面積單位，其中可改寫邏輯占 40，其他部分固定為 60；可改寫部分縮小 13%，全體只降到 94.8，改善是 5.2%。若 13% 本來就以整顆 die 為分母，則是降到 87。兩者回答不同問題。這個算例不是重解釋 Ho 的數字，而是說明讀面積成果時必須保留分母。

九個月開發時程也需要起訖點：從架構定案、RTL 開始、第一次 tapeout，或拿到可用矽晶片，會得到不同的週期。現有採訪節錄支持「模型使團隊更快接近效能目標」，但沒有交代九個月的定義與未使用模型的對照週期。因此，九個月不能被當成已量測的 AI 加速倍率，更不能把全部時程壓縮歸因於 LLM。[採訪：時程與效能取捨段落](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

工程上值得追問的是：模型減少了哪一段關鍵路徑？少一次原始碼重寫、少一次實作迭代，與平行跑更多候選，會留下不同證據。總週期還受 IP 取得、驗證、後段收斂和製造限制影響。只有知道哪些等待被消除，才可能判斷另一家公司能否重現收益。

## 未做硬體專用微調，仍需要一套使用方法

Ho 回答模型是否微調時，表示使用原始模型，許多是比公開版本稍微領先的內部模型。他也說團隊請機器學習研究人員協助找出取得最佳結果的方法。兩個陳述應一起讀：模型沒有針對這個設計任務再微調，使用過程仍有研究與工程 know-how。[採訪：模型與 EDA 夥伴段落](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

Ho 對模型為何有效的解釋，是模型能在自己的 context 中同時考慮不同設計區塊，系統性找出可以調整的「軟點」，而人較難端到端串起這些關聯。這是受訪者對成功原因的解釋，沒有附上上下文大小、輸入範圍或消融實驗；不能據此宣稱整顆晶片的全部原始碼一次放入模型，或證明某種特定推理演算法。[採訪：模型如何掌握設計關聯](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

作者推論，跨區塊視野的價值在於改寫相依關係：某段運算是否重複、兩個模組是否需要同時持有中間結果，以及某個局部選擇是否讓下游更難實作。這與只調整一個數值參數的搜尋不同。不過，模型若遺漏介面條件、時序假設或合法輸入範圍，也會提出看似全局合理的錯誤修改；上下文廣度必須由獨立驗收補上可靠性。

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

## I/O 提早回來、A0 帶起軟體、B0 驗證量產，各自降低不同風險

補充採訪整理指出，I/O chiplet 先回來，團隊利用部分元件提早做驗證；A0／B0 兩次 stepping 一開始就列入計畫。A0 已具有所需效能功能，主要供軟體 bring-up，B0 在訪談當時進行量產驗證。因此不能將「有 B0」直接解讀為 A0 出錯後才救援，也不能將 B0 在實驗室驗證寫成已完成大量部署。[採訪：投片與 bring-up](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

這裡的 **shift-left** 是把能提前做的工作移到較早階段，例如在全系統到齊前先驗證可取得的介面或啟動路徑。它不會自動覆蓋尚不存在的組合：部分元件通過，仍可能在完整系統整合、其他 corner 或長時間運作下出現新問題。A0 讓軟體能提早接觸真實硬體，B0 的量產驗證則面對另一組放行條件。

<figure>
<a href="/images/ic-design-platform/2026-10-02/jalapeno-software-silicon-feedback.svg"><img src="/images/ic-design-platform/2026-10-02/jalapeno-software-silicon-feedback.svg" alt="工作負載先經編譯器、kernel 與推論團隊在模擬器中評估，設計再經 EDA 驗收；提早取得的 IO chiplet、A0 軟體 bring-up 與 B0 量產驗證提供不同證據，實測差異回饋模型與軟體。" width="600" height="1100" loading="lazy"></a>
<figcaption>圖三：作者依<a href="https://morethanmoore.substack.com/p/interview-with-richard-ho-openai">採訪補充整理</a>繪製的交付與回饋模型。A0／B0 為預先規劃的 stepping；連線、交付物及差異處理是作者設計，不表示每階段的日期、比例或 OpenAI 內部執行順序。</figcaption>
</figure>

作者建議把模擬器、FPGA 與矽晶片的相關性當成可維護的工程資料。若同一輸入在三者出現差異，先保存可重現的工作負載、軟體版本與量測條件，再分類為模型近似、實作行為、軟體錯誤或物理限制；原因未明前，降低相關效能預測的可信度，停止用舊預測放行受影響的組態。這是本文提出的失敗處理，不是聲稱 Jalapeño 曾發生某項故障。

相對地，全部等到正式矽晶片才驗證，前期投入較少，問題卻更晚被發現；早期模擬與多階段驗證增加維護成本，也依賴模型足夠準確。Ho 報告模擬、FPGA 與矽晶片的相關性良好，仍將類比及訊號完整性列為不確定處。合理策略是逐步增加與實際系統的關聯證據，而不把一次相關性良好當成所有負載與 corner 都成立。[採訪：模型與矽的相關性](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

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

Linux 的文件用多個 cell、local memory 與互連說明 NUMA，強調要取得可擴展頻寬，多數存取必須落在本地或較近的記憶體。這是一般機制背景，不能據此宣稱 Jalapeño 採用 Linux 式 ccNUMA 或相同一致性協定。[Linux NUMA 定義](https://github.com/torvalds/linux/blob/d24e8ac715de2e16a53c144005b1863660a5fbea/Documentation/mm/numa.rst)

補充採訪整理進一步描述，Jalapeño 將 HBM bank 與運算核心相連，盡量在相應區域完成運算以避免資料搬移。架構有 ring，但 Ho 的說明著重高頻寬路徑；現有材料仍不足以重建全部連線、仲裁與一致性機制。這比單純說「採用 NUMA」更具體：硬體把資料位置的成本差異交給軟體利用，收益取決於模型是否能被有效安排到這些資源。[採訪：記憶體與運算配置](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

Ho 表示當時測過的開源模型都能映射，機器學習也協助映射；這個範圍應保留「當時測過」的條件。長 context 與 KV cache 仍要由 compiler 與 kernel 處理，他也承認極長 context 可能有界限，尚未完成分析。因此不能由一組開源模型通過，外推所有模型、任意序列長度與併發都具有相同效率。[採訪：映射與長 context](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

NUMA 的收益也不能只從硬體方塊推導。作者認為，若運算分區與常用資料一起放在較近的資源，能減少遠端流量；如果 runtime 把工作移走卻把資料留在原處，local memory 就失去作用。模型切分、權重配置、KV cache 的生命週期與排程，需要共同決定哪些資料值得搬、何時搬，以及搬移能否被之後的重用攤平。

<figure>
<a href="/images/ic-design-platform/2026-10-02/jalapeno-locality-tradeoff.svg"><img src="/images/ic-design-platform/2026-10-02/jalapeno-locality-tradeoff.svg" alt="兩個運算區域各有本地記憶體；同區存取較近，跨區存取經互連。移動計算卻留下資料會增加遠端存取，複製資料則消耗容量與搬移時間。" width="600" height="740" loading="lazy"></a>
<figcaption>圖四：作者 NUMA 概念圖，非 Jalapeño 官方拓樸，不表示實測延遲、頻寬或快取一致性。定義依<a href="https://github.com/torvalds/linux/blob/d24e8ac715de2e16a53c144005b1863660a5fbea/Documentation/mm/numa.rst">Linux NUMA 文件</a>，與採訪架構主張的連結為作者分析。</figcaption>
</figure>

一個**假設串行存取模型**：本地延遲 100 ns、遠端 300 ns，若 80% 存取為本地，平均是 140 ns；本地比例降到 50%，平均升到 200 ns。真實加速器有平行請求、預取、快取與排隊，不能直接拿這個平均當吞吐預測。但它足以展示在地性是執行條件，不是硬體名稱。

要驗證 NUMA 是否有利，至少要一起觀察本地命中比例、遠端流量、互連壅塞、每個區域的容量壓力與服務時間。固定資料位置有利於重用，卻可能形成負載不均；移動或複製資料有利於平衡，又增加容量與一致性管理成本。Ho 的方向值得研究，實際優勢仍要落到 workload 與軟體映射的證據。

### 長 context 的壓力，同時來自容量與位置

KV cache 保留每層先前 token 的 key／value，讓後續生成重用；一般 cache tensor 包含 batch、heads、序列長度與每個 head 的維度。快取可動態成長，也可採固定、滑動視窗、量化或 offload，不同方法有不同記憶體與速度取捨。[Transformers：快取原理](https://github.com/huggingface/transformers/blob/a005fc82babfe8871d87746decad2dbee100a125/docs/source/en/cache_explanation.md)、[Cache strategies](https://github.com/huggingface/transformers/blob/a005fc82babfe8871d87746decad2dbee100a125/docs/source/en/kv_cache.md)

用一個**作者假設的完整保留 KV 模型**計算容量：64 層，每層 8 個 KV heads，每個 head 為 128 維，每個值 2 bytes，一個請求含 131,072 tokens。key 與 value 都保留時，容量是：

`2 × 64 × 8 × 128 × 2 × 131,072 = 34,359,738,368 bytes = 32 GiB`

四個這樣的請求就需要 128 GiB，尚未加入模型 weights、暫存空間、allocator 留白、複製或分片開銷。此例沒有使用壓縮、prefix sharing 或 sliding window，也不是 Jalapeño 所測模型；它只說明 216 GiB 的名目總容量不能全部當成可自由配置的 KV 預算。

在 NUMA 型配置下，總容量足夠仍可能有局部不足：若某些 layers 或請求把 KV 集中在少數區域，其餘記憶體閒置也未必能低成本使用。保留資料位置有利於重用，重新分片有利於平衡，但要付出搬移與同步。作者建議同時測 context 長度、併發數與映射策略，記錄每區容量、遠端流量及 token 延遲；如此才能辨認限制來自總容量、局部容量、互連或 kernel。

## Benchmark 要連同軟體、預測方式與操作點一起比較

補充採訪整理記載，OpenAI 採用第三方 InferenceX 方法，以開源模型展示結果，並邀 SemiAnalysis 驗證；Ho 說正式生產環境使用 MTP，公開展示因開源模型沒有現成 draft model，採用 STP，目標是超越對手已公布的 MTP 數字。這些是採訪中的比較安排，不能由 InferenceX 的存在自動推定所有 Jalapeño 數字已具完整、公開、可重現的第三方測試。[採訪：benchmark 選擇](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

InferenceX 官方 repository 將自身定位為持續追蹤軟體與硬體的推論效能平台；其結果文件保留模型、framework、精度、speculative mode、輸入／輸出長度、併發、拓樸，以及吞吐、延遲與可取得的功耗資料。這些欄位說明結果的身分包括整個服務設定，不能只剩晶片名稱。[InferenceX README](https://github.com/SemiAnalysisAI/InferenceX/blob/49460fc6f8612349ba654d26e6333e19df525414/README.md)、[結果與量測欄位](https://github.com/SemiAnalysisAI/InferenceX/blob/49460fc6f8612349ba654d26e6333e19df525414/inferencex-e2e/docs/results-and-ingestion.md)

在這個比較脈絡中，STP 是單 token 預測，MTP 是多 token 預測；多 token 路徑的結果還會受提案、驗證、接受率與額外運算影響。**STP 超過另一套系統的 MTP 成績，可以支持該設定下的服務結果，不能單獨隔離出晶片微架構的貢獻。**若要拆解原因，應先固定模型品質與服務條件，再分別比較同一預測模式，以及各平台可達的最佳端到端組合。

採訪前言整理所述的 Hot Chips 2026 數字，包括相對 GB200／GB300 在所選峰值吞吐測點的每瓦效能 1.5–1.9 倍、延遲改善 1.7–3.6 倍，以及 Pareto 邊緣操作點最高 104 倍。這些結果沒有在本文重新量測，缺少逐點的模型、版本、batch／併發、SLO 與功耗明細，不能混成「Jalapeño 通常快 104 倍」。[採訪前言與效能比較](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

Pareto frontier 表示在吞吐與延遲等目標間，尚無另一個配置能同時改善所有目標的一組操作點。若比較落在對手難以有效提供服務的區域，比值可能很大；其工程意義是某個服務條件的可達性，與常見負載下的平均加速不同。GPU 與 Jalapeño 的全部測點、品質與 SLO 還要一起看，才能判斷哪一段 frontier 有實際用途。

作者提出的最小比較契約有四組條件：固定模型與輸出品質；固定輸入／輸出長度、到達模式與併發；交代 STP／MTP、精度、parallelism 與軟體版本；以相同服務 SLO 及功耗邊界量測合格吞吐。比較低併發互動與高併發批次時應各畫曲線，不能用一邊的最佳吞吐對另一邊的最佳延遲。

品質驗收也不能省略。InferenceX 的評估文件明確區分 throughput-only 工作與 model evaluation，跳過 eval 的 run 只提供吞吐證據；AgentX 則另有 trace replay、暖機與執行條件。這提供可檢查的評估機制，不代表 Jalapeño 已在所有這些流程上通過。[InferenceX 評估與 AgentX](https://github.com/SemiAnalysisAI/InferenceX/blob/49460fc6f8612349ba654d26e6333e19df525414/inferencex-e2e/docs/eval-agentx-procedures.md)

Ho 希望 benchmark 擴展到 agentic、diffusion 與多模態，因為測什麼會影響硬體朝哪裡最佳化。對本文的設計主線而言，這形成一個回饋：架構先接受代表性軟體負載的檢驗，部署後再用更接近服務的測量修正下一代需求。一次展示能證明部分能力，尚不能替未知 workload 寫下完整承諾。[採訪：benchmark 與後續方向](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

## 封裝擴大設計空間，也重新界定合作夥伴的價值

Ho 把當前稱為封裝的黃金時代，談到 system-on-wafer、panel、晶圓級整合與光學元件，以及如何把元件有效連接。他描述 OpenAI 直接與記憶體供應商溝通，因為團隊負責高層系統規劃，會討論需要什麼記憶體、如何配置與平衡；Broadcom 則提供重要 IP、合作經驗及取得大量供應的能力。[採訪：記憶體、封裝與合作夥伴](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

作者的技術解讀是，架構邊界正在超出單顆邏輯 die。計算放在哪裡、資料在哪裡、介面可提供什麼，以及封裝能如何連接，必須一起考慮。若本地記憶體能改善存取，還要確認對應容量、連線與系統限制是否允許；因此封裝會影響架構可實現的選項，不能只在 RTL 完成後才被當成組裝問題。

這些陳述支持 OpenAI 保有相當程度的系統與高層設計主導權，也支持其團隊直接參與原始碼最佳化。**它們沒有證明 OpenAI 包辦全部 front-end／RTL，也沒有證明 Broadcom 只做 physical design。**採訪明確談到 Broadcom 的 IP、介面專長與供應取得，將其角色縮成後段實作反而會漏掉已披露的價值。

補充採訪整理將 Broadcom 的選擇理由分成 IP、長期合作經驗與量產規模。SerDes、控制器等能力有其他供應商可以競爭，但取得足量晶圓、記憶體及封裝產能，需要已能承接大量供應的夥伴。Ho 也區分「加快設計到 bring-up」與「量產爬坡」：有限量可以嘗試加速取得，大量供應不能只靠多付錢插隊。[採訪：Broadcom 與供應規模](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

這使設計平台的輸出多了一個現實邊界。RTL、signoff 與軟體都完成，只證明設計進入下一階段；實際可部署量還要看晶圓、記憶體、封裝、板卡與機架交付是否同步。採訪前言將 Celestica 列為板卡與機架整合夥伴，正好提醒我們不能把合作鏈只畫到 GDS。[採訪前言：系統整合夥伴](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

作者推論，fleet 的硬體選擇還包含供應時程與使用壽命：一款局部效率較高但取得量不足的裝置，可能無法承接所需服務；一款可調度的裝置則有機會在需求比例變動後繼續使用。Ho 所述將最新硬體服務高階需求、較舊且已折舊的硬體服務較低價層級，是一種容量分層構想；是否划算仍取決於功耗、SLO、維護與機會成本，不能只因帳面折舊結束就視為免費。[採訪：硬體壽命與服務分層](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

對 turnkey 模式的影響，可以提出有條件的產業推論：當客戶自己掌握架構與部分前段工程能力，服務商可包辦的範圍可能改變，價值分配也可能轉向 IP、實體整合、封裝與供應鏈。但採訪未公開合約、工作範圍、定價與利潤，不能由設計主導權直接推導 Broadcom 附加價值或獲利下降。技術分工與商業結果之間，仍需要另一組證據。

## 用同一組工作負載，驗證探索、交付與服務收益

Jalapeño 的經驗把三個決策接起來。先由軟體團隊與模擬證據確認架構可承接的負載，再讓模型在 XLS 等可檢查表示中尋找候選，最後用 EDA、矽晶片與服務量測決定能交付什麼。這條路徑使「AI 加速設計」有了具體接點：探索可以更快，工程責任與未完成驗證仍要保留。

下一個可公開重現的實驗，應從一個固定規格的硬體模組開始，比較工程師既有方法、獨立公開 LLM，以及可取得的工具內建方案。固定 compiler、合法修改範圍與實作條件，記錄候選的等價失敗、PPA、工具耗時、工程師介入，以及到達相同驗收門檻的總時間。面積與時間改善都要回到同一個 baseline，不能把不同候選的最佳結果拼成一筆成果。

再往系統層推進時，保留同一組代表性 workload，在不同 context、併發與 prefill／decode 比例下比較映射、局部容量、遠端流量及合格吞吐。若局部 PPA 改善卻增加資料搬移，或更高 tokens/s 來自品質下降，就沒有完成原先的承諾。若服務效益成立，還要觀察硬體供應與調度能否把它轉成持續可用容量。

對 EDA 廠商而言，可驗證的機會是降低整條交付鏈的成本；對設計團隊而言，前沿模型的可用性讓它們能更早探索，但不保證自動取得 OpenAI 的成果；對 ASIC 夥伴而言，IP、實體整合、封裝與量產取得，仍是將設計變成可用基礎設施的重要能力。下一個最有價值的證據，是這些能力如何在相同品質與服務限制下，一起縮短時間、降低成本。

## 參考資料

1. [Interview with Richard Ho, OpenAI](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai) — Ian Cutress，More than Moore。刊出日期依補充整理為 2026 年 9 月 30 日；本文依中譯節錄與補充整理轉述，未逐段直接核對全文。規格、13% 面積、投片狀態及 Hot Chips 比較均為來源報告，不是本文獨立重現。
2. [XLS README](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/README.md) — Google XLS 官方 repository；版本 `1f1e152a856d`。用於工具鏈定位，不能據此外推 OpenAI 採用同一版本。
3. [DSLX Reference](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/dslx_reference.md)、[IR Semantics](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/ir_semantics.md)、[XLS Tools](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/tools.md) — 同一 XLS 版本的語言、抽象層與求值／等價／生成介面。
4. [觀點來源：Facebook 貼文](https://www.facebook.com/share/p/1CEZyFpDTh/?mibextid=wwXIfr) — 九項觀察的來源連結；本文不將其中的產業推論當成受訪者已證實的事實。貼文作者與發布日期未核實。
5. [相關影片](https://youtu.be/8s7uYtCM1bc) — 依補充整理，為 Substack 內嵌的同場訪談，不能當成獨立佐證；未逐段核對字幕與時間碼。
6. [What is NUMA?](https://github.com/torvalds/linux/blob/d24e8ac715de2e16a53c144005b1863660a5fbea/Documentation/mm/numa.rst) — Linux 官方文件；版本 `d24e8ac715de`。文件註明起始於 1999 年 11 月；用於一般定義，不代表 Jalapeño 實作。
7. [InferenceX 官方 repository](https://github.com/SemiAnalysisAI/InferenceX/blob/49460fc6f8612349ba654d26e6333e19df525414/README.md)、[Results and Ingestion](https://github.com/SemiAnalysisAI/InferenceX/blob/49460fc6f8612349ba654d26e6333e19df525414/inferencex-e2e/docs/results-and-ingestion.md)、[Evaluation and AgentX Procedures](https://github.com/SemiAnalysisAI/InferenceX/blob/49460fc6f8612349ba654d26e6333e19df525414/inferencex-e2e/docs/eval-agentx-procedures.md) — SemiAnalysisAI，版本 `49460fc6f861`。引用方法、結果身分與品質驗收；此版本不當作 Hot Chips 當時的固定版本，也不據此認定 Jalapeño 比較已獲全部獨立驗證。
8. [How caching works](https://github.com/huggingface/transformers/blob/a005fc82babfe8871d87746decad2dbee100a125/docs/source/en/cache_explanation.md)、[Cache strategies](https://github.com/huggingface/transformers/blob/a005fc82babfe8871d87746decad2dbee100a125/docs/source/en/kv_cache.md) — Hugging Face Transformers 官方文件，版本 `a005fc82babf`。引用 KV 結構與容量／速度取捨，非 Jalapeño 軟體實作。
