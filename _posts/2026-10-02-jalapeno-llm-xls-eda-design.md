---
layout: post
title: "OpenAI 用通用 LLM 最佳化 Jalapeño，EDA 的 AI 加值開始面臨競爭"
date: 2026-10-02 02:53:27 +0800
domain: ic-design-platform
categories: ic-design-platform
permalink: /ic-design-platform/2026/10/02/jalapeno-llm-xls-eda-design.html
description: "OpenAI 以通用 LLM 與 XLS 改善 Jalapeño 的設計，驗證與 signoff 沿用 EDA。設計公司可以自行取得模型帶來的加值，EDA 廠商的內建 AI 得靠完整設計流程的成果競爭。"
takeaways:
  - who: "OpenAI"
    value: "OpenAI 用沒有做 IC 設計專用微調的 LLM 協助 Jalapeño 最佳化，其中一例省下超過 13% die area，修改多在 XLS 完成，團隊再以既有驗證與 EDA 流程確認功能和實作結果。"
  - who: "IC 設計團隊"
    value: "IC 設計團隊可以把獨立 LLM 接到現有工具，自己取得模型帶來的設計收益，也要自行負擔上下文整理、工具串接、版本管理與驗證工作，這些使用經驗會逐步留在公司內部。"
  - who: "EDA 工具商"
    value: "EDA 工具商的內建 AI 會面對現有 EDA 加獨立 LLM 的比較，若能持續更快達到相同 PPA、節省整合與工程時間，就有額外收費的理由，產品競爭也會更直接落到完整設計流程的成果。"
  - who: "Broadcom"
    value: "Broadcom 以 IP、介面、實體整合與量產取得能力承接 OpenAI 的設計，客戶掌握更多架構與前段工作後，turnkey 服務的分工會改變，夥伴需要靠可交付的系統與產能持續證明價值。"
---

OpenAI 設計 Jalapeño 時，用沒有做 IC 設計專用微調的內部 LLM 協助最佳化，Richard Ho 在採訪中提到，其中一個案例省下超過 13% die area。模型只比當時公開版本稍微領先，設計修改多在 XLS 程式碼上完成，最後仍用標準 EDA 流程 signoff。設計公司因此多了一種選擇：把前沿 LLM 接到現有 EDA 流程，直接改善自己的設計。[採訪來源](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

EDA 廠商靠內建 AI 收取額外價值，會面臨更直接的競爭。IDM／fabless 可以把獨立 LLM 接到既有工具，自己建立設計方法、累積最佳化經驗。這會把一部分 AI 加值留在設計公司手上。Jalapeño 展示了這條路：模型協助修改，XLS 提供適合操作的硬體描述，EDA 負責驗證與實作。

這條路值得走，因為模型變化很快，晶片從開發到量產卻需要很長時間。硬體團隊要加快設計，又得保留可程式性，讓後來的工作負載能跑在同一套硬體上。LLM 能增加可探索的設計方案，軟體與 EDA 團隊則決定哪些方案值得實作。下圖把這個分工放回設計流程來看。

<figure>
<a href="/images/ic-design-platform/2026-10-02/jalapeno-design-flow.svg"><img src="/images/ic-design-platform/2026-10-02/jalapeno-design-flow.svg" alt="工程師固定規格、版本與目標，LLM 提出 XLS 程式碼候選，compiler 產生 RTL；功能驗證與 EDA 實作提供證據，由工程師決定採納，失敗候選回到探索。" width="600" height="1050"></a>
<figcaption>圖一：依據<a href="https://morethanmoore.substack.com/p/interview-with-richard-ho-openai">採訪</a>與<a href="https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/README.md">XLS 工具鏈</a>整理的參考設計，包含版本固定、功能驗證、實作及失敗後回到原版本的做法。</figcaption>
</figure>

模型負責提出修改，XLS 把高階描述轉成 RTL，驗證與 EDA 工具檢查功能和實作結果。工程師要決定修改能否採用，也要確認相關報告對應同一版設計。這套分工讓模型能參與探索，同時沿用晶片設計原有的檢查方法。

## 架構先讓 compiler、kernel 與推論團隊確認

Jalapeño 定位為推論加速器，Broadcom 是設計夥伴，Celestica 負責板卡與機架整合。推論也會出現在研究和訓練流程裡，例如強化學習迴圈中的模型執行。Ho 提到，他在 2023 年加入 OpenAI 時，reasoning 的可行性開始浮現，這讓推論需求直接影響架構方向。[採訪：架構動機](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

採訪前言列出的規格如下：

| 項目 | 規格 | 比較時需要知道的條件 |
| --- | --- | --- |
| 單顆裝置 | 一顆運算 die、一顆 I/O chiplet；216 GiB HBM4、15.4 TB/s | kernel 能用到多少頻寬，取決於存取與排程 |
| 功耗 | 峰值 700 W，持續運作約 550 W | 負載、量測範圍與平均時間尚未列出 |
| 系統配置 | 128 顆構成一個 local domain，2,048 顆構成一套系統 | local domain 的名稱未交代快取一致性或故障隔離範圍 |
| 運算峰值 | 2,048 顆系統在 FP4 下約 27 EFLOP/s | 峰值算力還要經過模型與服務測試，才能得到 tokens/s |

規格來源：[採訪前言](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)。單顆功耗與整套系統的算力，要用各自的範圍比較。

Ho 說，架構定案前主要要說服的是 compiler、kernel 最佳化與推論團隊。他們先做又快又準的模擬器，展示工作負載跑上去的效果，軟體團隊認同之後才繼續推進。硬體與研究團隊也在同一個地方工作，共用會議和資訊，讓設計需求可以直接討論。[採訪：軟體先行](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

這個順序很合理。架構能表達某種運算，compiler 未必能有效映射；compiler 映射成功，kernel 未必跑得快；kernel 很快，整個服務又可能卡在資料搬移或排程。若前期只看理想算子的峰值，等 RTL 和實體設計已經投入大量工作，才發現軟體用不起來，修改的成本會很高。

因此，架構評估至少要拿出代表性模型、compiler 映射方式、kernel 執行路徑和服務設定。這些資料讓後面的工程師知道，效能估計依賴哪些假設，哪些地方還需要補軟體。

Ho 從 TPU 的經驗學到，要避免把架構過度擬合到某一個模型。LLM 與 agent 的工作組成會變，保留可程式性可以多留一些調整空間。不過，控制邏輯、儲存與 compiler 都要付出成本；固定功能在適合的工作上仍可能比較有效率。哪些功能值得保留彈性，要從預期的模型變化判斷。[採訪：可程式性](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

## 13% 面積改善，模型已經參與設計收斂

Ho 描述的問題是：依照模擬與邏輯面積估計設定的效能目標，後來發現放不進原先預定的空間。團隊原本可能要降低效能，於是請模型找最佳化方法，其中一個案例省下超過 13% die area。[採訪：AI 輔助設計](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

13% 的意義在於，模型找到的修改足以影響設計能否達標。原本可能得犧牲效能的問題，有了另一個解法，LLM 已經參與設計收斂。至於成本收益，還要看記憶體、I/O、實體留白與封裝占比；比較其他方法時，則需要相同 baseline、製程與 corner 的面積報告。

用一個假設算例來看：原始面積是 100 個任意面積單位，其中可改寫邏輯占 40，其他部分固定為 60。若可改寫部分縮小 13%，總面積會變成 94.8，全體改善 5.2%；若 13% 本來就以整顆 die 為分母，則會降到 87。這個算例只說明分母的差異，沒有重新解釋 Ho 報告的成果。

時程也是同一個問題。Ho 說，若沒有模型，即使是優秀工程師，也得在更長開發週期和較低效能之間取捨。模型替團隊增加了同時達到時程與效能目標的機會。[採訪：時程與效能取捨](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

設計團隊導入時，應優先找這種卡住效能與面積的工作。少一次原始碼重寫、少一輪實體收斂，或同時跑更多方案，都可能縮短 critical path。把模型用在這些地方，比先替所有工具加上對話介面更接近工程收益。

## 模型可以通用，設計 know-how 要自己建立

Ho 回答模型有沒有微調時，強調使用原始模型，許多是略領先公開版的內部模型。他同時提到，團隊請機器學習研究人員協助找出取得最佳結果的方法。也就是說，沒有 IC 設計專用微調，仍然需要研究人員和工程師知道怎麼使用。[採訪：模型與研究團隊](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

Ho 對模型為何有效的解釋，是模型能在 context 中同時考慮不同區塊，找出設計裡可以調整的地方。工程師各自理解某個區塊，要把全晶片的關聯串起來很難。這個解釋指向一種值得優先嘗試的用法：把相依區塊與限制一起交給模型分析。[採訪：模型如何理解設計](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

跨區塊分析確實可能找到局部最佳化漏掉的機會。例如兩段運算是否重複、兩個模組是否需要同時保存中間結果，或上游的一個選擇是否讓下游多出控制邏輯。這類修改要同時理解功能和相依關係；如果模型漏掉介面、時序或合法輸入範圍，修改也可能看起來合理，實際上卻錯了。

這裡的「原始模型」指沒有再做 IC 設計專用微調。通用模型本身仍可能有指令或推理能力的 post-training。對導入決策有用的資訊是，團隊可以先用現成模型處理設計問題，再依結果決定是否需要領域訓練。

這也是 EDA 廠商面臨的競爭壓力。模型能力可以從工具之外取得，客戶就有條件比較「現有 EDA 加獨立 LLM」與「EDA 內建 AI」。內建功能若能省下整合、搜尋或收斂時間，客戶有理由付費；設計團隊自己完成這些工作，也能把經驗留在內部。

know-how 就在這些工作裡：選出適合修改的模組，提供設計意圖、原始碼和限制，再把修改送回既有工具檢查。團隊每跑完一輪，就能累積哪些資訊有用、哪些修改常失敗，以及哪些結果值得進一步實作。這些經驗會決定通用模型在自己設計上能發揮多少能力。

Ho 也直接表示，自家內部模型在相關工作上，比 EDA 公司圍繞模型開發的方案強。這是受訪者的使用判斷，而客戶能自行比較兩條導入路線，已經足以改變工具商的競爭方式。原始碼修改、工具參數搜尋和實體分析各有適合的方法，產品要用實際工作成果說服客戶。[採訪：對 EDA 方案的看法](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

| 導入方式 | 適合的問題 | 團隊需要處理的工作 |
| --- | --- | --- |
| 獨立 LLM 加既有 EDA | 跨原始碼與設計意圖提出修改 | 提供 context，串接工具，保存版本並驗證結果 |
| EDA 內建 AI | 搜尋變數與工具資料密切相關，目標已明確 | 確认功能範圍、資料可攜性與版本限制 |
| compiler／專用最佳化器 | 合法變換與目標已形式化、相對穩定 | 補足工具搜尋範圍以外的設計判斷 |

上表是導入方式的比較，並非 Jalapeño 實測。三種方式可以一起使用，實際選擇要看問題和整合成本。

## XLS 讓模型比較容易理解硬體描述

Ho 說團隊大量使用 XLS，模型最佳化的部分多半是 XLS 程式碼。語法與語意接近 Rust，對軟體背景的人比較容易理解，當時的模型也比較懂軟體，對 Verilog／SystemVerilog 仍有困難。使用 XLS 讓團隊能先利用模型已經比較熟悉的表示方式。[採訪：XLS](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

XLS（Accelerated HW Synthesis）是高階硬體綜合工具鏈，可以從高階功能描述產生可綜合的 Verilog／SystemVerilog。其中的 DSLX 是受 Rust 啟發的語言，以不可變運算式與資料流為主，包含固定大小物件、任意位元寬度等硬體特性。它和一般 Rust 程式還是有差別。[XLS README](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/README.md)、[DSLX Reference](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/dslx_reference.md)

流程是 DSLX 描述功能，轉成 XLS IR，經最佳化與排程，再生成 RTL。IR 保留資料流和固定寬度型別，排程決定運算放在哪一個 pipeline stage，code generation 再產生 ports、registers 等 RTL 物件。XLS 也有 IR 求值、等價檢查與 Verilog 生成工具。[IR Semantics](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/ir_semantics.md)、[XLS Tools](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/tools.md)

模型在這一層可以先分析運算關係，少處理一些暫存器與控制細節。例如兩個分支能否共用運算、位元寬度是否足夠，或條件判斷能否前移。不過，共用資源可能增加 mux 與控制相依；縮窄位元可能丟失合法結果。程式碼變短，最後的電路未必比較小。

型別、資料流與工具檢查讓這些修改有辦法被逐一確認。compiler 或 solver 可以檢查部分語意，排程與實體實作則會顯示 pipeline、時序和面積的代價。高階描述比較容易修改，也要一路檢查到產生的硬體。

XLS 的 function、proc、block 各有不同範圍。純函式描述輸入到輸出的映射，proc 還有跨時間的狀態與 channel 通訊，block 才具體表示 RTL。函式等價通過之後，reset、backpressure、整合 latency 和協定行為仍需要自己的檢查。[XLS IR 定義](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/ir_semantics.md)

## 模型的修改，還是要經過驗證與 signoff

Ho 說，短期內模型不會取代 EDA，signoff 仍走標準流程。他用數億個 gates 的設計說明，即使模型有 99.99% 正確率，也不夠直接 tapeout。這個數字是在說明精確度要求，並非模型準確率的實測。[採訪：模型限制](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

晶片驗證要檢查具體行為：某個合法輸入是否丟資料，reset 後狀態是否正確，修改是否保留原有功能。一個會讓晶片失效的反例，就足以否決修改。把三億 gates 乘上錯誤率只是在做尺度比喻；設計是否可用，要由這些具體檢查決定。

Ho 還提到，團隊一開始沒有完全理解某些模型做的原始碼最佳化，趕時程時只能靠完整驗證確認沒有破壞其他部分。工程師因此可以少花時間手工搜尋，但規格、輸入假設和採用修改的責任仍在。再問一次模型為什麼這樣改，可能只得到基於同一個錯誤前提的解釋。[採訪：原始碼最佳化與驗證](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

用一個假設的加法器就能看出問題。規格要求兩個 16-bit unsigned 輸入相加，輸出完整的 17-bit 結果。模型看到測試資料數值都很小，建議先用 16-bit 相加，再擴充成 17-bit，想減少邏輯。小數值測試會通過，但 65,535 加 1 會先溢位成 0，正確輸出應該是 65,536。

檢查時先固定原規格與 baseline，輸入範圍仍然是所有合法的 16-bit 值。讓原設計和修改版用同樣的型別語意求值，加入邊界值，再視設計使用等價檢查。proof 若 timeout 或未完成，結果就是未知，需要繼續處理。XLS 的 IR 求值與等價工具可用來做這類檢查，實際適用範圍要依工具和設計確認。[XLS Tools](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/tools.md)

找到反例後，保留失敗版本、輸入和反例，正式設計維持原版。下一版若改成「先把兩個 operand 擴充到 17-bit，再相加」，也要重新驗證，通過後才比較 PPA。這是型別語意的假設案例，沒有執行 XLS 工具測試。

<figure>
<a href="/images/ic-design-platform/2026-10-02/jalapeno-candidate-acceptance.svg"><img src="/images/ic-design-platform/2026-10-02/jalapeno-candidate-acceptance.svg" alt="16-bit 先加後擴充丟失進位；語意驗證保留反例與舊版本，先擴充再相加的新候選重新驗證，通過後才進行 PPA 與整合驗收。" width="600" height="880" loading="lazy"></a>
<figcaption>圖二：16-bit 加法假設算例，依據<a href="https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/dslx_reference.md">DSLX 型別語意</a>與<a href="https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/tools.md">XLS 工具文件</a>說明檢查順序。</figcaption>
</figure>

功能通過後，仍要在相同條件下做 synthesis、實體實作和時序／功耗檢查。面積縮小但時序失敗，這個方案就不合原目標；上游介面改了，原有整合報告也要重新確認。DFT、實體與封裝的檢查，仍由各階段的工程團隊負責。這是可採用的檢查流程，訪談沒有公開 OpenAI 的完整工具清單。

候選版本變多之後，版本管理也會變重要。修改 A 的面積與正確性報告要一起保存，修改 B 則有自己的一組結果，才有辦法知道哪一版同時通過功能和 PPA。本站另一篇[配置式設計管理文章](/ic-design-platform/2026/09/30/nvidia-gdp-multivendor-design-source-of-truth.html)討論的正是這種跨工具、跨團隊的版本問題。

## I/O chiplet、A0、B0 分別處理哪些工作

採訪中，I/O chiplet 先回來，團隊先用部分元件做驗證；A0／B0 兩次 stepping 則是一開始就規劃好的。A0 已有目標效能所需功能，供軟體 bring-up；B0 在訪談當時進行量產驗證。這個安排把軟體啟動和量產準備分開推進，能提早做的工作就先做。[採訪：投片與 bring-up](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

這種 shift-left 做法，把能提早做的驗證往前移。例如全系統還沒到齊，可以先測拿得到的介面和啟動路徑；A0 則讓軟體團隊開始用真正的硬體。完整系統組合、其他 corner 和長時間運作，仍要等相應條件具備才有辦法測。

<figure>
<a href="/images/ic-design-platform/2026-10-02/jalapeno-software-silicon-feedback.svg"><img src="/images/ic-design-platform/2026-10-02/jalapeno-software-silicon-feedback.svg" alt="工作負載先經編譯器、kernel 與推論團隊在模擬器中評估，設計再經 EDA 驗收；提早取得的 IO chiplet、A0 軟體 bring-up 與 B0 量產驗證提供不同證據，實測差異回饋模型與軟體。" width="600" height="1100" loading="lazy"></a>
<figcaption>圖三：依據<a href="https://morethanmoore.substack.com/p/interview-with-richard-ho-openai">採訪</a>整理的參考設計。A0／B0 是預先規劃的 stepping，交付物與差異處理用來說明各階段的工作。</figcaption>
</figure>

模擬器、FPGA 與矽晶片的結果要能持續對照。假設同一個 workload 出現差異，先留下輸入、軟體版本和量測條件，再確認是模擬近似、硬體實作、軟體錯誤，還是物理限制。原因還沒找到，就暫停沿用受影響的效能預測，避免拿已經不準確的估計繼續決定設計。這是建議的處理方式，並非 Jalapeño 已發生的故障。

等到正式矽晶片才開始測，可以少維護早期環境，但問題會發現得很晚。模擬與多階段驗證讓團隊較早修正問題，也要付出工具、模型和對照資料的維護成本。Ho 說模擬、FPGA 與矽的相關性良好，類比與訊號完整性仍是較不確定的地方。[採訪：模擬與矽的相關性](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

## 類比與訊號完整性，仍需要工程經驗

Ho 在採訪中指出，類比部分和訊號完整性比較難確定，也談到 Broadcom 在這些領域的專長。工程師的物理經驗在這裡仍有很高價值。數位修改可以依靠明確的型別、邏輯和等價關係檢查；類比與高速介面則要面對製程、訊號和實際量測，這也讓 Broadcom 的相關能力持續有用。[採訪：類比風險](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

離散邏輯的測試沒有涵蓋訊號完整性時，多跑同樣的測試也補不了這個問題。訊號完整性要用相應的物理模型與量測，數位協定則要檢查交易與時序。數位、類比都在同一顆晶片裡，驗證方法還是各有適用範圍。

Ho 給 EDA／ML 供應商的考題很直接：用 AI 做出符合他們 compliance 要求的 PCIe 控制器，而且比他的團隊更快、更好、面積更小，PPA 也達標，做到了再拿來看。訪談沒有列出 controller／PHY 的範圍、PCIe 世代或量測設定，正式比較時仍要把這些條件補齊。[採訪：PCIe 控制器挑戰](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

這個要求合理。產生幾百行可以編譯的程式碼，後面還有規格、反例、實體限制和整合工作。要比較 AI 工具，就固定交付範圍，量從開始到 IP 通過同樣檢查所需的時間。EDA 廠商如果能把這段做得更快、更容易用，仍然有很清楚的價值。

## 一顆晶片涵蓋 prefill、decode，保留調度彈性

大多數人想到自研 ASIC，會先想到針對特定工作做專用化。Jalapeño 在推論用途上，卻選擇讓同一種裝置涵蓋較廣的工作範圍。Cutress 問到業界常見的 prefill、speculative decoding 與完整 decode 分工，Ho 從整個資料中心 fleet（機群）回答：硬體一旦固定分給某個階段，CapEx 和電力也跟著投入；之後模型與工作比例變了，原來買好的比例未必合適。[採訪：推論分工](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

如果同一種裝置能在不同工作之間調度，團隊就比較容易把容量重新分配。這是推論用途裡的泛化，範圍仍和 GPU 的全部用途不同。Ho 認為 Jalapeño 能涵蓋整個 Pareto 範圍。他也承認，正式部署後可能才看得出為這種彈性付出的效率代價。

他並不反對 CPU、GPU 與推論加速器並存，fleet 仍會使用這些裝置。他比較擔心的是，把某一群硬體永久指定給某一種工作，之後很難隨需求調整。[採訪：異質基礎設施](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

用一個假設的容量模型來看。P、D 兩種工作各有 50 單位專用容量，總需求是 100；需求若變成 P=70、D=30，兩種容量又不能互換，最多只能服務 50+30=80，還有 20 單位閒置。若改成 100 單位可共用容量，即使每單位能力因泛用設計降為 0.9，也可能服務 90。

這個算例假設工作可換成相同容量單位、獨立排程，省略資料搬移、記憶體與延遲限制。它把取捨說得很清楚：工作比例穩定，專用硬體比較容易發揮效率；比例常變，共用硬體比較容易避免閒置。我認為 OpenAI 以 fleet 調度彈性決定這個方向是合理的，因為模型與推論階段的比例持續在變。部署後要量的是，這份彈性省下多少閒置，以及付出多少單位效率。

## NUMA 的好處，要靠資料與運算一起配置

Ho 認為 NUMA 是正確方向，甚至預期 GPU 團隊也可能走這條路。NUMA（Non-Uniform Memory Access）表示記憶體存取成本，會隨發起存取的運算單元和資料位置改變；UMA 則是存取成本較一致的模型。它們的區別在存取成本，實體記憶體的塊數、位址空間是否統一，以及快取是否一致，還要另外確認。[採訪：NUMA](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)、[Linux：What is NUMA?](https://github.com/torvalds/linux/blob/d24e8ac715de2e16a53c144005b1863660a5fbea/Documentation/mm/numa.rst)

Linux 的 NUMA 文件始於 1999 年 11 月，用多個 cell、本地記憶體與互連來解釋，若要隨規模增加而取得更多頻寬，多數存取就要落在本地或較近的記憶體。這可以幫助理解 NUMA，但 Jalapeño 的具體實作仍要以它公開的架構為準。[Linux NUMA 文件](https://github.com/torvalds/linux/blob/d24e8ac715de2e16a53c144005b1863660a5fbea/Documentation/mm/numa.rst)

Linux 的文件用多個 cell、本地記憶體與互連來解釋，若要隨規模增加而取得更多頻寬，多數存取就要落在本地或較近的記憶體。這可以幫助理解 NUMA，但 Jalapeño 的具體實作仍要以它公開的架構為準。[Linux NUMA 文件](https://github.com/torvalds/linux/blob/d24e8ac715de2e16a53c144005b1863660a5fbea/Documentation/mm/numa.rst)

採訪中，Jalapeño 把 HBM bank 與運算核心相連，盡量在對應區域完成運算，減少搬移資料；Ho 也談到架構中的 ring 和高頻寬路徑。這樣的配置讓軟體有明確的最佳化方向：把常用資料和相關運算放在附近，優先利用本地頻寬。[採訪：記憶體與運算配置](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

Ho 說，當時測過的開源模型都能映射，機器學習也參與映射工作。不過長 context 與 KV cache 仍要由 compiler 和 kernel 處理，極長 context 的限制也還沒完成分析。已測模型能跑得上去，和任意模型、長度、併發都能有效率地跑，是不同程度的要求。[採訪：模型映射](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

實際使用時，runtime 若把計算移走，卻把常用資料留在原處，就會增加遠端存取。模型切分、weights 配置、KV cache 的生命週期和排程要一起考慮，才能決定哪些資料值得搬、什麼時候搬，以及後續重用能否抵銷搬移成本。

<figure>
<a href="/images/ic-design-platform/2026-10-02/jalapeno-locality-tradeoff.svg"><img src="/images/ic-design-platform/2026-10-02/jalapeno-locality-tradeoff.svg" alt="兩個運算區域各有本地記憶體；同區存取較近，跨區存取經互連。移動計算卻留下資料會增加遠端存取，複製資料則消耗容量與搬移時間。" width="600" height="740" loading="lazy"></a>
<figcaption>圖四：依據<a href="https://github.com/torvalds/linux/blob/d24e8ac715de2e16a53c144005b1863660a5fbea/Documentation/mm/numa.rst">Linux NUMA 文件</a>整理的本地與遠端存取概念圖。</figcaption>
</figure>

再用一個假設的串行存取模型來看：本地延遲 100 ns、遠端 300 ns，80% 存取在本地，平均是 140 ns；本地比例降到 50%，平均就升到 200 ns。這裡量的是平均串行存取延遲；實際加速器的吞吐還受平行請求、預取、快取和排隊影響。資料配置是軟體能直接改變的一項成本。

所以測 NUMA 的效益，要一起看本地存取比例、遠端流量、互連壅塞、每區容量與服務時間。資料固定在原位置有利於重用，也可能造成負載不均；移動或複製可以改善分配，卻會增加容量、搬移及同步成本。同一套硬體，軟體安排不同，結果可能差很多。

### 長 context 還會遇到局部容量不足

KV cache 保存每層先前 token 的 key／value，讓後續生成可以重用。一般 cache tensor 包含 batch、heads、序列長度和每個 head 的維度。動態成長、固定大小、滑動視窗、量化和 offload 等方式，會有不同的容量與速度取捨。[Transformers：快取原理](https://github.com/huggingface/transformers/blob/a005fc82babfe8871d87746decad2dbee100a125/docs/source/en/cache_explanation.md)、[Cache strategies](https://github.com/huggingface/transformers/blob/a005fc82babfe8871d87746decad2dbee100a125/docs/source/en/kv_cache.md)

假設一個完整保留 KV 的模型有 64 層，每層 8 個 KV heads，每個 head 是 128 維，每個值 2 bytes，一個請求含 131,072 tokens。key 和 value 都保留，所需容量是：

`2 × 64 × 8 × 128 × 2 × 131,072 = 34,359,738,368 bytes = 32 GiB`

四個這樣的請求就需要 128 GiB，還沒加入 weights、暫存空間、allocator 留白、複製或分片的開銷。此例沒有壓縮、prefix sharing 或 sliding window，也不是 Jalapeño 的測試模型；即使裝置有 216 GiB，仍要先扣掉其他用途，才能知道 KV cache 可用多少。

NUMA 還多了位置問題。總容量足夠，但某些 layers 或請求的 KV 集中在少數區域，局部仍可能放不下；其他區域有空間，也要付出遠端存取或重新分片的成本。保留原位置有利於重用，重新分片有利於平衡，兩邊需要靠 context 長度、併發與映射方式的測試來比較。

測試若同時記錄每區容量、遠端流量和 token 延遲，就比較容易分辨是總容量不夠、局部配置不均，還是互連與 kernel 拖慢了執行。只看 HBM 總容量，會漏掉這些問題。

## 效能數字要連同 STP／MTP 和服務條件看

採訪中，OpenAI 採用第三方 InferenceX 方法，以開源模型展示結果，也邀 SemiAnalysis 驗證。Ho 說正式生產環境使用 MTP，公開展示時因開源模型沒有現成 draft model，採用 STP，目標是超過對手已公布的 MTP 數字。這些結果要按各自的預測方式與服務設定比較。[採訪：benchmark](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

InferenceX 的結果文件會保留模型、framework、精度、speculative mode、輸入／輸出長度、併發、拓樸，以及吞吐、延遲和可取得的功耗資料。同一顆晶片，這些設定換了，量出的服務效能也會變。[InferenceX README](https://github.com/SemiAnalysisAI/InferenceX/blob/49460fc6f8612349ba654d26e6333e19df525414/README.md)、[Results and Ingestion](https://github.com/SemiAnalysisAI/InferenceX/blob/49460fc6f8612349ba654d26e6333e19df525414/inferencex-e2e/docs/results-and-ingestion.md)

這裡的 STP 是單 token 預測，MTP 是多 token 預測。多 token 路徑還會受提案、驗證、接受率與額外運算影響。STP 成績超過另一套系統的 MTP，可以比較那兩套設定的服務結果；要判斷晶片架構本身貢獻多少，還得固定模型品質與服務條件，分別比較同一預測模式，以及各平台最佳的端到端組合。

採訪前言列出的 Hot Chips 2026 比較數字，包括相對 GB200／GB300，在所選峰值吞吐測點的每瓦效能 1.5–1.9 倍、延遲改善 1.7–3.6 倍，以及 Pareto 邊緣操作點最高 104 倍。這些數字仍缺逐點的模型、版本、batch／併發、SLO 和功耗明細，104 倍尤其需要看它出現在哪個條件。[採訪前言：效能比較](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

Pareto frontier 是一組在吞吐與延遲等目標之間，無法同時再改善所有目標的操作點。某個服務條件若落在對手很難達到的區域，比值可能很大，但常見負載下的結果可能不同。104 倍能說明特定操作點的差距，還需要整條曲線才能判斷哪些服務用得上。

比較時，模型與輸出品質、輸入／輸出長度、請求到達方式和併發要固定；STP／MTP、精度、parallelism、軟體版本也要交代。最後用相同 SLO 與功耗範圍量通過品質要求的吞吐。低併發互動與高併發批次各畫一條曲線，才能看出同一個服務條件下，哪套系統提供較多有效容量。

InferenceX 的評估文件也把 throughput-only 工作和 model evaluation 分開。跳過 eval 的 run 只提供吞吐資料，AgentX 則另有 trace replay、暖機與執行條件。模型品質會影響效能比較，所以還要確認所引用的結果實際跑了哪些評估。[InferenceX Evaluation and AgentX](https://github.com/SemiAnalysisAI/InferenceX/blob/49460fc6f8612349ba654d26e6333e19df525414/inferencex-e2e/docs/eval-agentx-procedures.md)

Ho 希望 benchmark 能補上 agentic、diffusion 和多模態，因為測試項目也會影響硬體設計方向。若 benchmark 只涵蓋現有的文字推論，硬體容易跟著那些工作最佳化；新型態的服務需要自己的測試，才能讓下一代架構有資料可依據。[採訪：benchmark 的後續方向](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

## 封裝的黃金時代，Broadcom 的價值也包括供應能力

Ho 認為現在是封裝的黃金時代，談到 system-on-wafer、面板級、晶圓級整合與光學元件。他也說 OpenAI 直接和記憶體供應商討論，因為團隊負責高層系統設計，需要決定記憶體配置、平衡和實體佈局；Broadcom 則提供 IP、介面專長與大量供應的能力。[採訪：記憶體與封裝](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

這讓晶片架構得提早考慮封裝。運算放在哪裡、記憶體容量怎麼分、介面有多少頻寬，以及元件可以怎麼連，會一起決定系統能做什麼。若架構依賴本地記憶體的效率，就得確認封裝與互連能支持那種配置，等 RTL 完成才開始處理，可能已經太晚。

從訪談可以看出，OpenAI 掌握系統與高層設計方向，也直接參與原始碼最佳化。這支持一個分工判斷：客戶端保留設計主導權，ASIC 夥伴要靠 IP、實體整合和供應能力提供價值。Broadcom 在 SerDes、介面與量產取得上的角色，對這種客戶尤其重要。[採訪：合作夥伴分工](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

Ho 選擇 Broadcom 的理由包括 IP、長期合作經驗與量產規模。SerDes 和控制器也有其他強的供應商，但軟體公司內部的新硬體團隊，要取得足量台積電晶圓、記憶體和封裝產能，需要能承接大量供應的夥伴。他也說，有限量可以設法加速，大量供應很難靠多付錢插隊；加快設計到 bring-up，和量產爬坡還是兩段工作。[採訪：Broadcom 與量產](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

這會改變 turnkey ASIC 服務的價值分配。客戶越能自己掌握架構與前段設計，夥伴越需要用 IP、實體整合、封裝和量產能力證明價值。對 Broadcom 的判斷應該跟著這些工作走：它替客戶解決多少介面問題、整合多大系統，以及能交付多少產能。這裡談的是分工方向，獲利影響還要看合約與定價。

設計完成之後，晶圓、記憶體、封裝、板卡和機架都要跟得上，才有可部署的容量。採訪前言把 Celestica 列為板卡與機架整合夥伴，也說明交付還有晶片之外的工作。[採訪前言](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

fleet 的成本還要看硬體能用多久。Ho 描述的構想是，最新硬體服務高階需求，較舊、已折舊的硬體服務較低價的層級，直到電力成本不划算為止。折舊結束後仍有電力、維護和機會成本，是否留下來用，也要看它能不能滿足該層服務的 SLO。[採訪：硬體壽命](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai)

## EDA 內建 AI 得和獨立 LLM 比較

Jalapeño 提供了一個可以嘗試的做法：讓通用模型在 XLS 等高階描述上找修改，團隊用既有 compiler、驗證和 EDA 流程確認結果。要判斷其他公司能取得多少效益，可以從固定規格的硬體模組開始，比較工程師既有方法、獨立公開 LLM 和工具內建 AI。

compiler、合法修改範圍、製程與實作條件都固定，記錄等價檢查的失敗、PPA、工具耗時、工程師介入，以及到相同驗收要求所需的總時間。這樣才有辦法知道，模型省下的是搜尋時間，還是連後面的收斂工作也變快；面積和時間改善，也要出自同一個 baseline 和同一版候選。

往系統層看，則需要同一組 workload 在不同 context、併發與 prefill／decode 比例下的結果，包含局部容量、遠端流量和通過品質要求的吞吐。局部 PPA 改善若增加資料搬移，服務未必比較快；tokens/s 增加若伴隨品質下降，也得重新比較。供應數量和調度彈性，最後會決定這些效能能變成多少實際服務容量。

未來十二個月，我預期企業評估 EDA 的 AI 功能時，會更常拿獨立 LLM 做對照，比較完整設計工作所需的時間。通用模型能由設計公司直接取得，EDA 的內建 AI 就得靠省下的整合、驗證和實作工作來競爭。若固定規格的模組測試顯示，內建方案持續比獨立 LLM 更快達到相同 PPA，我會提高對工具商 AI 加值的評價；若獨立模型加現有流程已能做到，這份加值就更多留在設計公司。Ho 的 PCIe 控制器考題，正好把這個比較具體化。

## 證據範圍

13% 面積改善、裝置規格、A0／B0 狀態與 Hot Chips 效能數字，皆為採訪所報告的成果。面積比較尚缺 baseline、製程、corner 與原始報告；九個月時程也缺起訖與對照週期。採訪和影片的逐段核對、刊出日期與時間碼仍待確認。

模型未做 IC 設計專用微調，是這次導入判斷的依據。模型的完整訓練歷程、context 大小、輸入範圍，以及和各家 EDA AI 的同條件比較尚未公開。內部版本略領先公開版，使用方法也有機器學習研究人員參與。

STP／MTP 成績要保留模型、軟體、品質、併發、SLO 與功耗條件。104 倍出現在 Pareto 邊緣操作點，完整逐點曲線與設定仍有待公開。極長 context 的映射限制、泛用設計的效率代價，以及機群利用率增益，也需要部署資料來量化。

面積、加法器、容量、存取延遲與 KV cache 都是明示假設的算例；加法器未執行 XLS 工具測試。四張圖是參考設計或概念圖，流程連線與失敗處理用來說明機制。引用的 XLS、Linux、InferenceX、Transformers 版本是文件基準，OpenAI 的實際工具版本與完整架構另需確認。

EDA 與 turnkey 服務的價值分配屬產業推論。OpenAI 與 Broadcom 的完整 front-end／RTL 分工、合約與定價尚未公開；判斷會隨同規格設計的總時間、PPA、整合成本及量產交付結果調整。

## 參考資料

1. [Interview with Richard Ho, OpenAI](https://morethanmoore.substack.com/p/interview-with-richard-ho-openai) — Ian Cutress，More Than Moore；Jalapeño 設計、模型使用、XLS、架構與合作夥伴的主要來源。
2. [同場訪談錄影](https://youtu.be/8s7uYtCM1bc) — Richard Ho 與 Ian Cutress 的訪談影片。
3. [XLS README](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/README.md)、[DSLX Reference](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/dslx_reference.md)、[IR Semantics](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/ir_semantics.md)、[XLS Tools](https://github.com/google/xls/blob/1f1e152a856d223eaa474f01d67abd8e5ec727c7/docs_src/tools.md) — Google XLS 官方文件，引用版本 `1f1e152a856d`。
4. [What is NUMA?](https://github.com/torvalds/linux/blob/d24e8ac715de2e16a53c144005b1863660a5fbea/Documentation/mm/numa.rst) — Linux 官方文件，引用版本 `d24e8ac715de`，文件始於 1999 年 11 月。
5. [InferenceX README](https://github.com/SemiAnalysisAI/InferenceX/blob/49460fc6f8612349ba654d26e6333e19df525414/README.md)、[Results and Ingestion](https://github.com/SemiAnalysisAI/InferenceX/blob/49460fc6f8612349ba654d26e6333e19df525414/inferencex-e2e/docs/results-and-ingestion.md)、[Evaluation and AgentX Procedures](https://github.com/SemiAnalysisAI/InferenceX/blob/49460fc6f8612349ba654d26e6333e19df525414/inferencex-e2e/docs/eval-agentx-procedures.md) — SemiAnalysisAI 官方 repository，引用版本 `49460fc6f861`。
6. [How caching works](https://github.com/huggingface/transformers/blob/a005fc82babfe8871d87746decad2dbee100a125/docs/source/en/cache_explanation.md)、[Cache strategies](https://github.com/huggingface/transformers/blob/a005fc82babfe8871d87746decad2dbee100a125/docs/source/en/kv_cache.md) — Hugging Face Transformers 官方文件，引用版本 `a005fc82babf`。
