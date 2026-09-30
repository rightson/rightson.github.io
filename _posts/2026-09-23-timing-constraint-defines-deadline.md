---
layout: post
title: "STA 的時間需求從哪裡來：SDC、Arrival Time 與 Slack"
date: 2026-09-23 12:35:00 +0800
domain: eda
categories: eda
description: "STA 結果建立在 netlist、delay model 與 timing intent 上；先理解需求如何形成 deadline，才能分辨路徑太慢與 constraint 寫錯。"
---


STA 的 pass／fail 來自電路延遲與時間需求的比較。相同 netlist，在不同 clock period 或介面條件下可能得到不同 slack；如果需求沒有被正確描述，漂亮的 timing report 也不足以證明晶片能在預期系統中工作。

數位晶片同時承擔功能與時間兩種責任。RTL 描述應計算什麼，實體電路決定資料傳播需要多久，接收端則要求資料在適當的時刻穩定。Synthesis 與 APR 需要知道這個期限，才能在面積、功耗與速度間取捨；STA 再以 timing model 檢查結果。SDC 是設計意圖進入這條流程的重要介面。[OpenSTA](https://github.com/The-OpenROAD-Project/OpenSTA)

因此，學 SDC 應先建立「需求如何成為 required time」的直覺，再讀 command 語法。這能避免把 negative slack 一律當成電路問題，或把 positive slack 一律當成成功。以下用同一條路徑、兩種 clock period，追蹤 arrival time、required time 與 constraint coverage，也建立後續 checker 與 diagnosis 所需的證據。

圖中電路保持不變，資料都在 6.5 ns 抵達；改變 clock period 後，required time 卻從 9.2 ns 變成 5.2 ns，slack 因而由正轉負。先把「電路花多久」與「需求允許多久」分開，就能理解 SDC 為何會直接改變 STA 的判定。

![同一條資料路徑的 arrival 為 6.5 ns；10 ns 與 6 ns 時脈建立不同 required time 和 slack](/images/timing/2026-09-23/sdc-deadline-context.svg)

圖：作者依正文算例繪製，假設 clock-to-Q 0.5 ns、logic delay 6 ns、setup 0.8 ns，省略 skew 與 uncertainty。分析物件參考：[OpenSTA](https://github.com/The-OpenROAD-Project/OpenSTA)。

## 邏輯正確，不代表時間正確

先看一個最小的 synchronous path：

    launch FF
       │
       │ clk → Q delay
       ▼
    combinational logic
       │
       │ cell + net delay
       ▼
    capture FF

資料從 launch flip-flop 出發後，需要經過 cell delay、interconnect delay，最後抵達 capture flip-flop。假設整條 data path 花了 3 ns，這個數字本身沒有「快」或「慢」的意義。

如果下一個有效 capture edge 在 10 ns 之後，3 ns 很寬鬆；如果下一個 capture edge 只有 2 ns，3 ns 就不可能滿足要求。所以 timing engine 至少需要知道兩件事：data 實際何時到達，以及 data 最晚必須何時到達。

## Arrival Time 與 Required Time

先忽略 clock skew、uncertainty、OCV 等後續複雜因素。對一條 register-to-register path，可以先用最簡化的模型理解：

    Arrival Time
    ≈ launch clock edge
    + clock-to-Q
    + combinational path delay

而 setup check 的 required time 可以先近似成：

    Required Time
    ≈ capture clock edge
    - setup time

兩者相減：

    Slack = Required Time - Arrival Time

如果 slack ≥ 0，代表資料在 deadline 前到達；如果 slack < 0，代表資料太晚。

例如 clock period = 10 ns、clock-to-Q = 0.5 ns、combinational delay = 6 ns、setup time = 0.8 ns：

    Arrival  = 0 + 0.5 + 6.0 = 6.5 ns
    Required = 10.0 - 0.8    = 9.2 ns
    Slack    = 9.2 - 6.5     = +2.7 ns

但如果只把 clock period 改成 6 ns，其他電路完全不變：

    Required = 6.0 - 0.8 = 5.2 ns
    Slack    = 5.2 - 6.5 = -1.3 ns

同一條 netlist、同一條 data path，因為 timing requirement 改變，就從 pass 變成 violation。Constraint 並不描述 circuit 已經是什麼；它告訴 timing engine，這個 circuit 必須在什麼時間世界裡工作。

## create_clock 建立分析用的時間座標系

最基本的 SDC 通常會出現：

    create_clock -name clk -period 10.0 [get_ports clk]

Intel 的 Timing Analyzer 文件說明 create_clock 會定義 clock 的 period、waveform 與 target；OpenSTA 的公開範例也以相同方式建立 clock，再加入 I/O timing constraints。[Intel Timing Analyzer — create_clock](https://www.intel.com/content/www/us/en/docs/programmable/683243/25-1/create-clock-create-clock.html)；[OpenSTA gcd.sdc](https://github.com/The-OpenROAD-Project/OpenSTA/blob/master/test/nangate45/designs/gcd.sdc)

但如果只記住「period 10 就是 100 MHz」，會漏掉更重要的概念。這條 command 讓 timing engine 有能力建立一系列 clock edges：

    0 ns      10 ns      20 ns      30 ns
     │          │          │          │
     ▼          ▼          ▼          ▼
    launch    capture     capture     capture

從此之後，工具才能建立 launch/capture relationship。create_clock 不只是設定 frequency；它建立後續 timing analysis 的時間參考系。

因此 base clock 往往必須先定義。Intel 文件指出 generated clock 與其他 constraints 經常引用 base clock，而引用未定義 clock 的 constraint 不會產生預期分析。[Intel Timing Analyzer — Creating Base Clocks](https://www.intel.com/content/www/us/en/docs/programmable/683243/24-1/creating-base-clocks.html)

## I/O delay 與 SDC 描述的 design intent

考慮 input path：

    external device → input port → internal FF

晶片內部的 STA 看得到 input port 之後的 internal delay，但資料並不是在 clock edge 的 0 ns 憑空出現在 chip boundary。外部 device 需要時間產生資料，board path 也有 propagation delay，因此才會需要：

    set_input_delay -max 2.0 -clock clk [get_ports din]

同理，output port 外面的 receiving device 也會對資料抵達時間有要求，因此會出現 set_output_delay。LibreLane 的 timing closure 文件也把 clock、input/output delay、output load、input driving condition 等列為基本 timing constraints。[LibreLane — Timing Constraints](https://github.com/librelane/librelane/blob/main/docs/source/usage/timing_closure/index.md)

> STA 分析的對象是「netlist + timing intent」，單有 netlist 並不夠。

少了後者，很多 path 即使可以計算 propagation delay，也無法判斷是否符合實際的 system requirement。

## 最危險的情況不一定是 negative slack

初學 STA 很容易建立「negative slack = 有問題；positive slack = 沒問題」的直覺。這個判斷只在一個重要前提成立：**constraint 本身是正確而完整的。**

假設實際的 clock period 是 5 ns，但 SDC 錯寫成：

    create_clock -period 50 [get_ports clk]

工具可能得到非常漂亮的 positive slack。design 並沒有變好，deadline 被錯誤放寬了十倍。再極端一點，如果某些重要 path 根本沒有被正確 constrain，它們甚至可能不會以你預期的方式進入 timing checks。

所以「timing clean」與「constraint correct」是兩個不同問題。前者問：在目前 constraints 下是否有 violation？後者問：constraints 是否真的描述了我們想實作的 design intent？SDC sanity checker 要處理的主要是第二個問題。

## Sanity checker 第一層到底應該檢查什麼

如果未來要建立 SDC sanity system，第一層甚至不需要 LLM。它首先應該能回答 deterministic questions：clock 是否真的建立、target object 是否存在、period/waveform 是否合理、clock 是否覆蓋預期 sequential elements、I/O 是否有 timing context，以及是否存在 unconstrained endpoints 或套到空 collection 的 constraints。

OpenSTA 本身就是適合公開實驗的 timing engine：它可以讀 Verilog netlist、Liberty、SDC，並提供 timing checks 與 timing setup checking。[OpenSTA](https://github.com/The-OpenROAD-Project/OpenSTA)

parse 一行 SDC 並不難，困難在於：

> 我們如何證明 constraint 實際作用在正確的 design object 與 timing path 上？

這也是後面 hierarchical SDC 會變得困難的原因。get_ports clk 在小型 top-level design 很直觀；當 design 進入 hierarchy、block integration、名稱轉換與不同 implementation stage 後，「這個 constraint 到底綁到了誰」可能比 command syntax 本身困難得多。

## 最小實驗：只改 clock period

今天的第一個 lab 只需要一個兩級 sequential design：

    din → FF1 → combinational logic → FF2 → dout

準備 relaxed.sdc 與 aggressive.sdc，兩份檔案唯一差異是 clock period：

    # relaxed.sdc
    create_clock -name clk -period 10.0 [get_ports clk]

    # aggressive.sdc
    create_clock -name clk -period 2.0 [get_ports clk]

保持 RTL/netlist 與 Liberty 完全相同，分別執行 STA。要觀察的重點在結果，command 寫法是次要的：當 physical path 沒變，只有 requirement 改變時，required time 與 slack 如何跟著改變？

這個實驗建立後續會反覆使用的基準：

    Design topology
    + delay model
    + timing constraints
            ↓
    Timing graph analysis
            ↓
    arrival / required
            ↓
    slack

未來會逐步破壞其中不同部分：clock target 寫錯、漏掉 input delay、generated clock 沒建立、false path 套太廣、hierarchical object 找不到。每一次都問同一件事：工具看到了什麼？它為什麼做出這個 timing 結論？

## 從 checker 再往 agent 前進

如果 timing report 出現異常，agent 不應第一步就猜「可能是 SDC 有問題」。它應該取得 design objects、clock definitions、constraint coverage、timing paths 與 tool diagnostics，先經過 deterministic checks 形成 evidence package，再進行 reasoning / diagnosis。

LLM 適合處理「多個證據之間如何形成 diagnosis」；決定什麼叫 setup violation 仍是 timing engine 的工作。

這個分工會成為後續系列的一條主線：**EDA tool 負責計算；checker 負責建立可驗證事實；agent 負責在事實之上推理。**

第一個需要建立的事實因此是：Delay 本身不是 violation。只有當 delay 被放進一個 timing requirement 裡，才有 pass 或 fail 的意義。

下一個問題是：STA 到底如何從 launch edge 與 capture edge 建立 setup 與 hold check？