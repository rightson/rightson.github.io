---
layout: post
title: "同一個 10 ns Clock，Setup 與 Hold 為什麼比較不同的 Edge"
date: 2026-09-24 11:31:48 +0800
domain: timing
categories: eda
description: "同樣是 10 ns clock，setup 與 hold 為什麼會得到完全不同的 timing relationship？從 launch/capture edge、Liberty timing arc 與 OpenSTA 的 max/min analysis，看懂 create_clock 建立的其實是一組時間關係。"
---

昨天先建立了一個最小觀念：**delay 本身沒有 pass 或 fail，只有把 delay 放進 timing requirement 之後，slack 才有意義。** 下一步真正需要釐清的，是這個 requirement 從哪裡來。

對最常見的 synchronous register-to-register path，答案不是一句「clock period 是 10 ns」就結束。STA 真正做的事情，是先找出 data 從哪一個 clock edge 被 launch，再找出應該被哪一個 clock edge capture，最後才把 cell delay、net delay、setup/hold time 等資訊放進這兩個 edge 之間。

也就是說，clock 的核心不是 frequency，而是 **edge relationship**。

這個差別看似只是語意，但它直接決定後面 generated clock、multicycle path、clock groups、latency、uncertainty 甚至 hierarchical SDC 為什麼會變難。

## 一個 10 ns clock，STA 其實看見一整串 edge

最基本的 constraint 可能只有一行：

```tcl
create_clock -name clk -period 10.0 -waveform {0.0 5.0} [get_ports clk]
```

這不是單純告訴工具「100 MHz」。它同時建立了一個 waveform：

```text
0 ns        5 ns        10 ns       15 ns       20 ns
 |-----------|-----------|-----------|-----------|
 ↑           ↓           ↑           ↓           ↑
 rise        fall        rise        fall        rise
```

OpenSTA 把 SDC clock、generated clock、latency、uncertainty、propagated/ideal clock 都當成 timing analysis 的一等物件；`report_checks` 則依據這些 clock 與 timing graph 產生 setup/max 與 hold/min path。[OpenSTA — Parallax Static Timing Analyzer](https://openroad.readthedocs.io/en/latest/main/src/sta/README.html)；[OpenSTA Command Reference](https://opensta.readthedocs.io/en/latest/Commands/)

對兩個都由同一個 rising-edge clock 驅動的 flip-flop，最直觀的 data path 是：

```text
         launch FF                      capture FF
clk ───────►│                               │◄────── clk
            │ Q ───── data path ───────► D │
            └───────────────────────────────┘
```

如果 data 在 0 ns 的 rising edge 被 launch，setup check 預設會問：

> 這筆 data 能不能趕上下一個有效 capture edge？

所以 setup relationship 是：

```text
0 ns                    10 ns
 ↑ launch                ↑ capture
 |-----------------------|
          10 ns
```

但 hold check 問的不是同一件事。

它不是問 data 能不能在 10 ns 前到，而是問：

> 0 ns 這個 capture edge 剛把舊資料收進去之後，新資料會不會太快衝到 endpoint，破壞同一個 edge 的 hold requirement？

因此同一組 rising-edge clocks 的 default hold relationship 是：

```text
0 ns
 ↑ launch / capture
 |
 0 ns
```

Intel Timing Analyzer 的文件也直接用 10 ns same-clock example 說明：default setup relationship 為 10 ns，而 hold relationship 為 0 ns。[Intel Quartus Prime Timing Analyzer User Guide](https://www.intel.com/programmable/technical-pdfs/683068.pdf)

這是理解 STA 很重要的一個分界：**setup 和 hold 不是把同一個公式換個正負號，而是在 timing graph 上回答兩個不同問題。**

## Setup 看的是「最慢會不會太晚」，Hold 看的是「最快會不會太早」

OpenSTA 的 command reference 把這件事表達得很直接：

- `report_checks -path_delay max`：setup / max path analysis
- `report_checks -path_delay min`：hold / min path analysis

來源：[OpenSTA Command Reference](https://opensta.readthedocs.io/en/latest/Commands/)

這裡的 max/min 不是說 clock period 最大或最小，而是 data path 的 propagation 行為。

Setup 關心的是 worst-case late arrival：

```text
launch edge
   ↓
clock-to-Q(max)
   ↓
data path(max)
   ↓
arrival time

arrival 必須早於：capture edge - setup time
```

Hold 則關心 worst-case early arrival：

```text
launch edge
   ↓
clock-to-Q(min)
   ↓
data path(min)
   ↓
earliest new data

earliest new data 必須晚於：capture edge + hold time
```

所以在實體設計裡，setup 與 hold 甚至常常偏好相反的物理結果：setup 希望 data path 更快；hold path 太快時，APR 反而可能需要插 delay cell、buffer 或利用 routing delay 把資料拖慢。

這也是為什麼只看一個 WNS 數字很容易把 timing 問題想得過度簡單。真正的 STA 是在不同 analysis condition 下，同時維持 max path 與 min path 的合法性。

## Library 才告訴 STA：這顆 FF 需要多少 setup 與 hold

SDC 定義 clock relationship，但 flip-flop 本身需要多少 setup time、hold time，以及 clock-to-Q delay，通常不是寫在 SDC 裡，而是來自 Liberty timing model。

一個大幅簡化的 DFF Liberty 可以長成這樣：

```text
D  -- setup_rising / hold_rising --> CK
CK -- rising_edge ----------------> Q
```

Liberty 的 `timing_type` 定義包含 `setup_rising`、`hold_rising`、`rising_edge` 等 sequential timing arc；setup/hold arc 透過 `related_pin` 指向 clock pin。[Liberty Reference Manual](https://people.eecs.berkeley.edu/~alanmi/publications/other/liberty13_03.pdf)

所以一條真正的 setup path 並不是只有：

```text
clock period - data delay
```

而比較接近：

```text
launch clock edge
+ launch clock path
+ CK→Q(max)
+ data path(max)

vs.

capture clock edge
+ capture clock path
- setup time
- uncertainty
```

Hold 也有自己的 min-delay、clock path 與 library hold constraint。

今天的 lab 先刻意把 clock latency、skew、uncertainty、OCV 全部拿掉，只留下 edge selection 與一個 synthetic DFF library。原因不是因為真實晶片這麼簡單，而是先把「誰跟誰比」看清楚，後面每加一個因素才知道它改變的是哪一項。

## create_clock 寫對語法，不代表 clock 真的存在

這裡開始進入 sanity checker 真正有價值的地方。

假設工程師寫了：

```tcl
create_clock -name clk -period 10.0 [get_ports clkk]
```

語法看起來很像是對的，但 design 裡其實只有 `clk`，沒有 `clkk`。

這時候真正應該檢查的不是「有沒有 create_clock 這一行」，而是：

```text
SDC expression
     ↓
object query
     ↓
resolved design object
     ↓
clock object
     ↓
clock propagation
     ↓
clocked sequential endpoints
```

任何一層失敗，都可能讓後面的 timing report 失去原本以為存在的 timing intent。

OpenSTA 的 debugging guide 特別指出：如果 sequential design 沒有出現預期 timing paths，很可能要往 clock propagation 查；`report_arrival` 可以直接觀察 register clock pin 是否真的收到某個 clock 的 rise/fall arrival。對完全沒有 constraint 的 path，`report_checks -unconstrained` 則能把 unconstrained path 顯示出來。[OpenSTA — Debugging Timing](https://opensta.readthedocs.io/en/latest/Debugging/)

因此一個最基本的 clock sanity checker 至少不應只做字串檢查，而應驗證：

```text
clock definition
  ├─ period 是否合理
  ├─ waveform 是否合理
  ├─ target collection 是否非空
  ├─ target 是否是預期 port/pin
  ├─ clock 是否到達預期 sequential cells
  └─ 預期 timing paths 是否真的被 constrain
```

這裡已經可以看出「parser」和「checker」的差別。

Parser 能告訴你：

> 有一條 create_clock command。

Checker 必須回答：

> 這條 command 是否在這份 design 上建立了原本想建立的 timing relationship？

## 同樣 10 ns，不同 edge 關係仍可能是完全不同的 timing 問題

如果所有 design 都只有單一同相 rising-edge clock，SDC 其實不會太難。

真正的複雜度來自：

```text
same period, different phase
same source, divided/generated clock
posedge → negedge transfer
multiple related clocks
multiple unrelated clocks
clock gating
mode-dependent clocks
```

這些情況都告訴我們：**frequency 只是一個 clock property，不足以代表 path relationship。**

例如兩個 clock 都是 10 ns period，但一個 rising edge 在 0 ns，另一個在 2 ns。對跨 clock path 來說，setup requirement 可能先變成 2 ns，而不是直覺上的 10 ns。工具會根據兩組 waveform 尋找合法 launch/capture edge relationship，而不是只拿兩個 frequency 做比較。

這也是下一階段 generated clock 必須保留 source relationship 的原因。若只知道「輸出 clock 是 200 MHz」，卻不知道它從哪個 source edge、經過什麼 divide/multiply/invert relationship 得來，很多 timing relationship 就失去了可以追溯的來源。

## 今天的 OpenSTA Lab：直接看 max 與 min report

今天的 `sdc-lab` 不再只用 Python 算 slack，而開始加入真實開源 EDA flow：

```text
RTL
 ↓
Yosys（可選，確認 synthesis / DFF mapping）
 ↓
structural netlist
 + synthetic Liberty
 + SDC
 ↓
OpenSTA
 ↓
report_checks -path_delay max
report_checks -path_delay min
```

實驗位置：[`rightson/sdc-lab — Experiment 002`](https://github.com/rightson/sdc-lab/tree/main/experiments/002-clock-edge-relationships)

核心 design 只有兩顆 positive-edge DFF：

```text
din → FF1 → FF2 → qout
       ↑      ↑
       └─clk──┘
```

Liberty 中刻意設定 synthetic timing：

```text
CK→Q  = 0.20 ns
setup = 0.50 ns
hold  = 0.10 ns
```

SDC 建立 10 ns clock。OpenSTA run script 分別執行 max 與 min report。這次不要只看最後的 slack，而是逐行找：

1. Startpoint 是哪顆 FF？
2. Endpoint 是哪顆 FF？
3. max report 的 launch/capture clock edge 各是多少？
4. min report 的 launch/capture relationship 為什麼不同？
5. CK→Q 從哪個 Liberty timing arc 來？
6. setup/hold constraint 又從哪個 arc 來？

OpenSTA 官方 example 的標準 flow 本身就是 `read_liberty → read_verilog → link_design → read_sdc/create_clock → report_checks`。[OpenSTA Examples](https://opensta.readthedocs.io/en/latest/Examples/)

另一個故意寫錯的 SDC 則把 target 寫成不存在的 `clkk`。這不是要測 LLM 會不會猜 typo，而是建立更重要的習慣：**先證明 constraint 真正作用在哪個 design object 上，再談 diagnosis。**

## 未來 Agent 真正需要的不是整份 log，而是一包可驗證 evidence

如果未來要讓 agent 判斷「為什麼這條 path timing 異常」，直接把一萬行 timing report 丟給模型不是最好的起點。

對 clock-related issue，至少應該先整理成：

```text
Constraint evidence
- create_clock source line
- resolved target object
- period / waveform

Path evidence
- startpoint / endpoint
- launch clock / capture clock
- selected launch edge / capture edge
- max or min analysis

Library evidence
- CK→Q arc
- setup / hold arc

Tool evidence
- slack
- unconstrained status
- warnings / empty collections
```

這些資料大部分可以由 EDA tool 或 checker deterministic 地取得。

Agent 真正有價值的工作，是在這些已驗證 facts 之上回答：

> 這是一個 clock definition 錯誤、object resolution 錯誤、真正的 data-path timing violation，還是更上游的 design-intent mismatch？

這比讓 LLM 從 raw log 猜原因可靠得多。

今天最重要的結論因此不是「setup 看 max、hold 看 min」這句口訣，而是：

> **Clock constraint 的本質，是建立 timing engine 用來配對 launch/capture edge 的時間關係。Period 只是其中一個參數。**

當這件事建立清楚之後，下一個值得拆解的問題就是 generated clock：如果 clock 不再直接來自 top-level port，而是由 divider、PLL、clock gate 或內部邏輯產生，工具要如何知道它和 source clock 的 edge relationship？
