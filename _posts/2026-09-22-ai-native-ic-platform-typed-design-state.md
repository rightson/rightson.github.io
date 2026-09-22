---
layout: post
title: "AI 原生 IC Design Platform 的核心：不是更多 Agent，而是 Typed Design State"
date: 2026-09-22 23:05:00 +0800
author: Scott Yo-Ru Chen
domain: eda
categories: eda
description: "當 AI 開始跨越 RTL、verification、synthesis、APR 與 signoff，真正的瓶頸不再是模型會不會呼叫工具，而是整個 IC design platform 是否有可驗證、可重播、可分層操作的設計狀態。"
---

作者：Scott Yo-Ru Chen

我認為 AI 驅動 IC Design Platform 接下來真正的分水嶺，不是再增加一批 design agent，也不是替每一套 EDA tool 補一個 MCP server。真正決定平台能不能從「好用的助理」走向「可信任的工程系統」的，是設計狀態本身能不能被機器清楚理解、修改、驗證與重播。

今天三個訊號剛好從不同方向指向同一件事。UCLA 的 Zijian Ding 在 ICCAD 2026 invited paper 中顯示，讓同一類 coding agent 從 RTL 提升到 HLS 層操作，再回到 RTL refinement，11 個 benchmark 上相對 Direct RTL Design 取得 2.62× geometric-mean speedup；而單純 Agent-based HLS 也有 2.31×。這不是證明 HLS 永遠優於 RTL，因為論文同時顯示小型 kernel 上 direct RTL 仍可能較好，而且每組實驗只跑一次；真正重要的是「agent 操作哪一層表示」會直接改變它能利用的設計知識與探索效率。[來源：Zijian Ding, UCLA, ICCAD 2026](https://arxiv.org/abs/2609.21157)

同一時間，Synopsys 的 Thomas Andersen 把 autonomous engineering 描述成從 command-driven tool use 轉向 goal-directed workflow execution：人定義 intent、constraints、thresholds 與 priorities，系統決定如何推進 workflow；而且真實工程不可能只靠單一 agent，需要 generation、verification、diagnosis、analysis、planning、correction 等能力協同。[來源：Synopsys](https://www.synopsys.com/blogs/chip-design/agentic-ai-autonomous-engineering.html)

更值得注意的是 OpenROAD Project 的 Øyvind Harboe 今天在 bazel-orfs 的設計討論中提出一個非常工程化的觀點：如果某個 stage 只能產出 degraded result，不應只在 orchestrator 或 log 裡記住「它有問題」，而應把 degraded marker 寫進 declared artifact；如此 marker 會進入 content hash，進而影響 downstream action key，使 clean artifact 與 degraded artifact 永遠不會被 cache 系統誤認為同一個狀態。這目前是 repo 中的設計提案，不是我所宣稱已成為正式 ORFS 行為，但它點出了 AI-native EDA platform 很關鍵的一個 state-model 問題。[來源：bazel-orfs commit, Øyvind Harboe](https://github.com/The-OpenROAD-Project/bazel-orfs/commit/1631e5e8faa15cee3c1e0991419a4c4a7b235fef)

三件事合起來，我得到的結論是：未來的 IC design platform 必須從「一堆 tool + scripts + agents」升級成「一個具有多層 Typed Design State 的 engineering system」。

![AI-native IC design platform multi-level state stack](/assets/images/eda/ai-native-ic-platform-state-stack.svg)

*圖 1：我對 AI-native IC Design Platform 的狀態分層。整理自 UCLA AHRR 的 abstraction-level 結果、Synopsys autonomous engineering 的 goal-directed workflow 概念，以及現有 EDA flow 的 artifact/evidence 結構。*

## 問題本質：IC design 不是一條 command sequence，而是一連串 state transition

今天大多數 EDA automation 看起來仍像這樣：

```text
run_genus.tcl
→ run_innovus.tcl
→ run_pt.tcl
→ parse_report.py
→ engineer decides what to change
→ rerun
```

這種方式對人類工程師有效，因為真正的 state model 藏在工程師腦中。工程師知道哪一版 RTL 對應哪一組 SDC，知道某次 WNS 改善是否是因為 path group 被改壞，知道 floorplan 變動後哪些 downstream result 已經失效，也知道一份 report 雖然 job exit code 是 0，但其實結果不能用。

Agent 不具備這種隱含背景。如果平台只把 shell、Tcl、log、report 丟給模型，它就必須同時推理三件本來應由平台負責的事：目前真正的 design state 是什麼、下一步允許修改什麼、什麼證據足以宣告成功。

這也是為什麼「增加 tool API」不等於「得到自主 IC design」。API 只解決 action surface；它沒有解決 state semantics。

真正的 design state 至少有五層。

第一層是 intent：功能目標、PPA、power budget、可靠度、schedule、允許變更的邊界與 acceptance criteria。

第二層是 architecture / behavioral representation：hierarchy、protocol、dataflow、algorithmic structure，以及 HLS、DSL 或 domain-specific compiler 能表達的設計知識。

第三層是 RTL 與 constraints：Verilog/SystemVerilog、SDC、UPF、DFT intent、formal assumptions。這裡已經不是單純「code」，因為 constraints 本身會改變 EDA 對設計的語意理解。

第四層是 implementation state：netlist、floorplan、placement、CTS、route、RC、timing graph、physical database。

第五層則是 evidence：STA、SI、IR/EM、DRC、LVS、LEC、coverage，以及每一個 waiver 的 provenance。

一個 AI system 若只看其中一層，就很容易做出局部正確、系統錯誤的決策。

## 為什麼 abstraction layer 會直接改變 Agent 能力

Zijian Ding 的 AHRR 結果最值得注意的地方，不是 2.62× 這個數字，而是 case study 顯示 HLS abstraction 把大量 hardware design knowledge 壓縮進 compiler semantics。論文中的 ROB1 case，agent 在 HLS 只需要用少量 pragma 表達 256-way parallelism，Vitis HLS 再把 intent 展開成大規模 RTL；同一 agent 直接寫 RTL 時只做出較窄的平行結構。這表示 abstraction 並不是把低階自由度拿掉而已，它其實把大量已知工程模式變成模型可以利用的「結構化先驗」。[來源](https://arxiv.org/abs/2609.21157)

但這不代表平台應該全部升到 HLS。論文也顯示小型 kernel 上 direct RTL 可以勝過 HLS；而 Post-HLS RTL Refinement 又能在部分案例繼續回收低階最佳化空間。比較合理的結構不是選一個唯一 abstraction，而是建立 multi-level design state：

```text
Intent
  ↓
Architecture / Behavioral IR
  ↓
HLS / DSL / generated RTL
  ↓
RTL + Constraints
  ↓
Netlist / Physical DB
  ↓
Signoff Evidence
```

Agent 應該在「最高但仍足以控制結果」的 abstraction 上修改；只有當 verifier 顯示問題出在低階 realization，才往下 refinement。

這與 compiler 的最佳化原理其實很接近：高階 IR 保留 semantic information，低階 IR 暴露 target-specific optimization。IC design agent 若永遠直接從 Tcl、Verilog 或 tool console 開始，相當於把所有工程問題都降成 machine-level patch，再要求模型自己重建上層意圖。

## 平台真正需要的不是 memory，而是可持久化的 engineering state

Agent system 很容易把「memory」當成核心能力：把過去 trajectory 存起來、把 senior engineer 的操作做 RAG、把之前的 error/fix pair 放進 knowledge base。這些都重要，但它們不是 authoritative state。

一個 flow 真正能被依賴的 state，必須具備四個性質：

1. **Typed**：平台知道它是 RTL、SDC、ODB、timing result、coverage result，還是 waiver，而不是只看到一個檔名。
2. **Versioned**：每個 artifact 能回溯到 parent state、tool version、參數與輸入。
3. **Validated**：平台知道這份結果通過哪些 checker，也知道哪些 checker 尚未通過。
4. **Replayable**：換一個 worker 或乾淨環境，仍能重新建立並驗證同一個狀態。

這就是為什麼 bazel-orfs 今天那個 degraded marker 的討論很值得重視。假設 place stage 在某個低成本探索模式下仍留下 unrouted nets，但為了讓 downstream route/signoff 繼續暴露其他問題，平台選擇讓 stage 產出 artifact 而不是立即 fail。如果 degraded 只寫在 log，下一層就可能把它當成正常 checkpoint；如果 degraded 狀態本身進 artifact metadata 與 hash，那麼 cache identity、lineage 與 downstream action key 都會跟著分流。

![Typed artifact state and cache semantics](/assets/images/eda/ai-native-ic-platform-artifact-state.svg)

*圖 2：將 quality state 放入 artifact identity，可讓 clean / degraded result 在 cache 與 downstream dependency 上天然分離。概念整理自 [bazel-orfs 2026-09-22 design discussion](https://github.com/The-OpenROAD-Project/bazel-orfs/commit/1631e5e8faa15cee3c1e0991419a4c4a7b235fef)。*

這個概念如果擴大到商用 IC design platform，我會希望每一個重要 artifact 至少帶有：

```text
Artifact {
  type
  payload
  parent_artifacts[]
  tool + version
  parameters
  environment
  quality_state
  validators[]
  metrics
  owner / policy domain
  timestamp / provenance
}
```

這樣 Agent 才能問出工程上真正有意義的問題：

「這份 post-CTS checkpoint 是不是由目前這版 SDC 產生？」

「這個 WNS improvement 是從哪一個 parent state 分支出來？」

「這份 route result 是否帶著 upstream floorplan degraded marker？」

「這個 result 通過的是 quick checker，還是 production signoff checker？」

這些問題比「某個 log 裡有沒有 ERROR」重要得多。

## Autonomy 的可靠性邊界：Agent 可以決策，但不能自行定義成功

Siemens EDA 在今年 DAC 後公開的 long-running agent 架構把 physics-based deterministic EDA engines 放在 ground-truth layer，agent 的決策持續被工具結果驗證，而不是只在 workflow 結尾做一次檢查。Siemens 同時把 orchestration、self-verification、governance/security、reasoning model 與 accelerated compute 分成不同層。[來源：Siemens EDA](https://blogs.sw.siemens.com/cicv/2026/07/29/self-verifying-eda-ai-agents/)

這個方向與 Synopsys 的 goal-directed autonomous engineering 相容：Agent 負責把 workflow 往 objective 推進，但「是否真的達到 objective」應由外部 evidence 決定，而不是由 agent 的自然語言結論決定。

![Verifier-backed closed loop](/assets/images/eda/ai-native-ic-platform-closed-loop.svg)

*圖 3：可信任的 autonomous design loop。整理自 Synopsys autonomous engineering、Siemens self-verifying EDA agents，以及現有 EDA signoff practice。*

如果把這個邊界畫清楚，整個系統可以容許模型犯錯。Agent 可以提出錯誤 hypothesis、試錯誤 parameter、甚至產生無效 patch，只要錯誤被隔離在 candidate branch，而且 candidate 不能在沒有 evidence 的情況下升級成 trusted state。

因此真正重要的不是讓每一次 reasoning 都正確，而是讓錯誤嘗試便宜、隔離、可回復，而且不污染正式 design state。

## Failure mode：最危險的不是 Agent 做錯，而是平台不知道哪裡開始不可信

AI-native IC platform 我最擔心的 failure mode 有四種。

第一，**state ambiguity**。同一個檔名或 workspace 裡混入不同版本 artifact，agent 以為自己在分析 current state，實際上拿到 stale report。

第二，**constraint drift**。RTL 沒變，但 SDC、UPF、library、RC corner 或 tool setting 變了；平台若只追 code diff，會把不可比較的 QoR 當成可比較。

第三，**false completion**。command 執行成功、job exit 0、agent 說「fixed」，但 clean replay 的 STA、formal、LEC 或 regression 並沒有通過。近期 SecTB-RTL 甚至展示了 provider schema acceptance 與 production semantic validity 可以嚴重脫節：1,860 次呼叫中有 1,857 次被 provider 接受，卻只有 9 次通過 production semantic validator。這個實驗最重要的訊息不是某個模型好或壞，而是 schema/tool-call success 不能替代工程語意驗證。[來源：Hang Xiao, SecTB-RTL](https://arxiv.org/abs/2609.19844)

第四，**hidden degradation**。為了探索或縮短 turnaround time，平台允許某些 stage 用 approximate / fast / partial mode，但 quality state 沒有進入 lineage，導致後續結果看起來「完成」卻建立在不相容的前提上。

這四種問題都不是靠更大的 LLM 解決，而是 state model、dependency model 與 validation contract 的問題。

## 對 IC Design Platform 架構的含義

如果上述判斷成立，我會把 AI-native IC design platform 拆成五個長期穩定層，而不是綁在某一個模型或 agent framework 上。

**第一層：Design State / IR Plane**

保存 intent、hierarchy、RTL、constraints、physical state、signoff evidence 與 lineage。這是最重要的 system of record。

**第二層：Compiler / Lowering Plane**

負責 abstraction 之間的 lowering 與 canonicalization，例如 architecture → HLS/RTL、RTL → netlist、logical constraint → tool-specific Tcl。Agent 不應自己重新發明所有 lowering semantics。

**第三層：Execution Plane**

承載 Genus、Fusion Compiler、Innovus、ICC2、PrimeTime、Calibre、formal/simulation 等實際工作，底下可以是 LSF、Kubernetes、grid scheduler 或 cloud。scheduler 可以替換，但 execution contract 不能漂移。

**第四層：Evidence Plane**

由 deterministic checker 產生可以機器判讀的 engineering evidence。它決定 state transition，而不是 LLM。

**第五層：Agent / Optimization Plane**

在前四層之上做 hypothesis、planning、DSE、debug、root-cause analysis、skill reuse 與跨 flow coordination。模型與 harness 都應該是 replaceable component。

這種分層有一個很重要的效果：未來無論使用 Claude、GPT、Gemini、GLM 或公司內部模型，真正累積下來的資產不會是 prompt，而會是 design state、artifact lineage、validator、decision trajectory 與 reusable methodology。

## Trade-off：狀態越完整，平台成本越高

這套架構不是免費的。

把每個 artifact 都做完整 provenance，會增加 metadata、storage 與 schema governance 成本；checkpoint 太細，cache footprint 會爆炸；validator 太多，agent 每一步的 latency 會上升；abstraction 太高，可能犧牲低階 QoR；abstraction 太低，又會把 agent 拉回 Tcl/RTL micro-management。

因此平台不應追求「所有東西都 typed、所有 substep 都 checkpoint」。比較合理的是把 state boundary 放在三種位置：

1. 會影響大量 downstream work 的 expensive boundary；
2. 需要 human/agent decision 的 semantic boundary；
3. 能提供 deterministic acceptance evidence 的 trust boundary。

例如 synthesis netlist、floorplan、post-place、post-CTS、route、signoff 是自然候選；但某些 tool 內部的幾十個 optimization substep 未必需要全部升格成 platform-level artifact。

## 未來 6–18 個月，我會優先做的三件事

第一，建立最小可用的 **Typed Artifact Contract**。先不要企圖建完整 design database，選 synthesis、APR、STA 三個 flow，定義 artifact type、parent、tool/version、parameters、quality state、metrics、validators。

第二，建立 **cross-layer invalidation**。修改 RTL、SDC、UPF、library、floorplan parameter 時，平台必須知道哪些 downstream result 已經失效，而不是靠 engineer 判斷要重跑哪一段。bazel-orfs 對 stage-level content hash 與 incremental rebuild 的實作值得直接研究。[來源：bazel-orfs](https://github.com/The-OpenROAD-Project/bazel-orfs)

第三，讓 Agent 在不同 abstraction 上工作，而不是只做 Tcl automation。可以選一個具體 design task，比較：

```text
A. raw Tcl / report loop
B. semantic tool API
C. typed state + semantic transformation
D. higher-level intent / IR + lowering + verifier
```

量測的不只是成功率，而是工程師介入次數、無效 rerun、token / compute cost、QoR、可重播性與跨 design generalization。

真正值得追求的終局不是「AI 可以操作 EDA tool」。那只是 automation surface。

更有價值的終局是：工程師定義設計目標與不可違反的邊界，平台把設計表示成可理解、可追溯、可驗證的多層狀態；Agent 在適當的 abstraction 上探索；compiler 與 EDA engines 做 lowering 和 realization；deterministic evidence 決定哪一個結果可以被下一階段信任。

到了那一步，AI 才不是掛在 IC design flow 旁邊的 assistant，而是進入 design platform 本身的 execution semantics。

## References

1. Zijian Ding, Yang Zou, Yizhou Sun, Jason Cong, *Can Agents Design Better Chips with a Higher Level Abstraction?*, ICCAD 2026.  
   https://arxiv.org/abs/2609.21157
2. Thomas Andersen, Synopsys, *Agentic AI and Autonomous Engineering*.  
   https://www.synopsys.com/blogs/chip-design/agentic-ai-autonomous-engineering.html
3. Emma-Jane Crozier, Siemens EDA, *Self-verifying, long-running EDA AI agents that engineers can trust*.  
   https://blogs.sw.siemens.com/cicv/2026/07/29/self-verifying-eda-ai-agents/
4. Øyvind Harboe, OpenROAD Project / bazel-orfs, design discussion on degraded artifact markers and action-key semantics, 2026-09-22.  
   https://github.com/The-OpenROAD-Project/bazel-orfs/commit/1631e5e8faa15cee3c1e0991419a4c4a7b235fef
5. The OpenROAD Project, *bazel-orfs*.  
   https://github.com/The-OpenROAD-Project/bazel-orfs
6. Hang Xiao et al., *Trust, but Validate the Instrument: Auditing AI-Generated RTL Verification Plans on Authored Security-Regression Proxies*.  
   https://arxiv.org/abs/2609.19844
