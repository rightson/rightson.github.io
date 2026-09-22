---
layout: post
title: "R2G 平台的核心不是 Agent：把晶片設計流程做成可調和、可重播的 Control Plane"
date: 2026-09-22 12:58:00 +0800
categories: eda r2g platform-engineering
---

作者：Scott Yo-Ru Chen

如果一條 RTL-to-GDS flow 會執行數小時到數天、跨越多個工具與多台機器、途中可能失敗、重跑、人工介入、修改 constraint、重新產生 artifact，那麼它本質上就不是一個「job」。它是一個長生命週期、帶狀態、會被持續修正的工程系統。

這也是我認為 R2G 平台最容易被低估的地方。

真正需要解決的，不是「如何讓 LLM 會下 Tcl 指令」，而是：

> 如何把 design intent、execution state、artifact lineage、policy、validation 與 recovery 變成一套可持續運行的控制系統。

如果這層不存在，Agent 再聰明，也只是在一個沒有明確狀態模型的 shell 上工作。

## Scheduler 解決的是執行，不是工程狀態

傳統 implementation flow 很自然會長成：

```
Makefile / Tcl / Perl
        ↓
      LSF
        ↓
Fusion Compiler / Innovus / PrimeTime / ...
        ↓
 log / report / output directory
```

這套架構在人類主導時可以工作，因為真正的狀態機其實存在 senior engineer 腦中。

工程師知道：

- 哪一版 SDC 才是現在有效的
- 哪個 checkpoint 還可以 reuse
- 這次 timing regression 是 tool noise 還是真問題
- 哪個 stage 必須重跑
- 哪些 violation 可以接受
- 哪一個修改會讓 downstream result 全部失效

但 scheduler 不知道。

LSF 知道 job 是 Running、Done 或 Exit；它不知道「design 是否更接近可以 tape-out」。

如果要讓 Agent 真正參與工程閉環，第一件事不是增加更多 Agent，而是把這些隱性的工程狀態顯性化。

## R2G 應該有 Desired State 與 Observed State

Kubernetes controller 最重要的抽象並不是 container，而是 reconciliation。

使用者宣告 desired state，controller 持續觀察 current state，再採取動作讓兩者靠近。

這個模型放到 IC design 非常自然。

例如一個 implementation objective 可以被描述成：

```
Desired State
- WNS >= 0
- TNS = 0
- DRC = 0
- area increase <= 2%
- clock definition immutable
- max transition / capacitance clean
```

而平台持續收集：

```
Observed State
- WNS = -83ps
- TNS = -4.1ns
- area = +0.7%
- 31 max transition violations
- route congestion hotspot in region X
```

Agent 的任務，不應是「把下一個 command 猜出來」。

它應該是根據 state delta，提出一個 candidate transition：

```
Observed State
      ↓
Diagnosis
      ↓
Candidate Action
      ↓
Controlled Execution
      ↓
New Evidence
      ↓
Observed State'
```

平台才是真正持有 state 的角色。

這與「Agent 寫腳本」是兩個完全不同的系統層級。

## Durable Execution 才能承受真正的 EDA Flow

長時間 agent workflow 的另一個根本問題是 failure。

worker 會死、network 會斷、license 會拿不到、queue 會塞住、EDA tool 會 crash、filesystem 會短暫不可用。

Temporal 這類 durable execution 系統的核心思想，是把 workflow state 持久保存，讓 process crash 後不需要從頭重新開始。

但 EDA 比一般 SaaS workflow 更麻煩：很多 operation 有昂貴 side effect。

例如：

```
run_place()
run_cts()
modify_sdc()
write_checkpoint()
launch_500_cpu_job()
```

不能因為 orchestrator retry，就盲目再做一次。

因此 R2G 的 durable execution 必須建立在兩個條件上：

1. 每個 action 有明確 identity。
2. 每個 artifact 有可追溯 provenance。

理想上，每一次 stage execution 應該可以表示為：

```
ActionKey =
hash(
  input artifacts
  + tool version
  + PDK / library version
  + parameters
  + constraints
  + environment
)
```

如果 ActionKey 沒變，系統首先應該問：

> 已經有可驗證的 artifact 可以 reuse 嗎？

而不是直接重新執行。

## Artifact Graph 比 Workflow DAG 更重要

這也是我認為 Bazel 與 bazel-orfs 對 EDA 很有啟發性的地方。

bazel-orfs 把 ORFS 中的 stage 轉成 explicit target，input 是 label，dependency 是 graph，stage result 可以 cache；只有真正受到改動影響的 downstream stage 才需要 rebuild。

這其實比「workflow DAG」更接近晶片設計真正需要的抽象。

Workflow DAG 通常描述：

```
synth → floorplan → place → CTS → route
```

但 Artifact Graph 描述的是：

```
RTL ────────┐
SDC ────────┼→ synth checkpoint
Library ────┘          │
                       ├→ STA report
Floorplan config ──────┤
                       ↓
                  placement DB
                       │
CTS config ────────────┤
                       ↓
                    CTS DB
```

兩者差別非常大。

如果只知道 DAG，我知道 stage 的順序。

如果知道 artifact dependency，我才能回答：

- 改了一條 false path，到底哪些 downstream result invalid？
- 換了一個 placement parameter，要不要重新 synthesis？
- tool version 沒變、input 沒變，可以直接 reuse 哪些 checkpoint？
- 同一份 synth output 能不能 branch 五組 placement experiments？

當 experiment cost 被壓低，Agent 就不必每一步都「一次猜對」。

它可以：

```
Generate candidates
      ↓
Cheap branch execution
      ↓
Measure
      ↓
Discard / cache
      ↓
Promote winner
```

這比期待 LLM 一次找到最佳 Tcl 更可信。

## Agent 必須被 Policy 包住，而不是擁有環境

真正進入 production 之後，還有另一個問題：Agent 不應該天然擁有與工程師相同的 authority。

NVIDIA OpenShell 現在採用 gateway + sandbox + declarative policy 的方式，把 control plane 與 execution boundary 分開；filesystem/process policy 可以在 sandbox creation 時鎖定，network/provider authority 則可以動態更新。

這種分層非常值得移植到 EDA。

例如：

```
Immutable Boundary
- project filesystem scope
- tool binary
- process capability
- PDK read-only boundary

Runtime Authority
- allowed design
- allowed stage
- allowed Tcl namespace
- resource quota
- LSF queue

High-Risk Action
- SDC modification
- clock definition change
- UPF modification
- signoff waiver
        ↓
Human approval
```

所以未來 Agent 權限模型不能只是：

```
can_run_innovus = true
```

而應該更接近：

```
agent:
  stage: post_cts
  can:
    - resize_cell
    - buffer_net
  cannot:
    - change_clock_definition
  limits:
    area_delta: 2%
  require_approval:
    - modify_sdc
```

這才是可以逐步放大 autonomy 的方式。

## Evidence 才是 State Transition 的唯一依據

Agent 最大的錯誤之一，是把「我完成了」當成完成。

EDA 平台不能接受這件事。

```
Agent says done
      ↓
無效
```

真正的 state transition 必須由 deterministic evidence 觸發。

例如：

```
Action
  ↓
Artifact persisted
  ↓
Clean validation
  ├─ STA
  ├─ DRC
  ├─ LEC
  ├─ power
  └─ QoR thresholds
  ↓
Evidence Gate
  ↓
State transition
```

LLM 可以判斷下一步值得嘗試什麼。

但「這一步是否成功」應該由 EDA engine 決定。

這也是 probabilistic reasoning 與 deterministic engineering truth 之間最重要的邊界。

## 我認為合理的 R2G Platform Architecture

把這些拼起來，R2G 比較合理的形狀不是一個大型 Agent framework，而是：

```
                  Human / Agent
                       │
                       ▼
                Intent / FlowSpec
                       │
                       ▼
              ┌─────────────────┐
              │   R2G Control   │
              │      Plane      │
              └─────────────────┘
                │      │      │
          reconcile   policy  observe
                │      │      │
                ▼      ▼      ▼
          Typed Artifact / State Graph
                       │
                       ▼
                Execution Plane
             ┌─────────┼─────────┐
             ▼         ▼         ▼
            LSF       K8s      Local
             │
             ▼
      EDA Engine / Tool APIs
             │
             ▼
       Artifact + Metrics
             │
             ▼
         Evidence Gate
             │
             └────────────→ Observed State
```

這個架構裡，Kubernetes 不是必要條件。

Temporal 也不是必要條件。

Bazel 也不一定要直接導入。

真正重要的是它們背後共同的幾個系統能力：

- desired/current state separation
- reconciliation
- durable state
- deterministic replay boundary
- artifact provenance
- incremental invalidation
- policy-enforced execution
- evidence-based state transition

這些能力才是平台資產。

## 90 天內真正值得做的事情

如果要快速驗證這個方向，我不會先做一個「全自動 APR Agent」。

我會先挑一個已經反覆發生、可以量化的 flow loop。

例如 post-CTS timing closure。

只做五件事：

1. 定義最小 `FlowSpec`：objective、constraint、allowed action、acceptance criteria。
2. 建立 `ObservedState`：WNS/TNS、area、violations、checkpoint、tool/version。
3. 對每一次 action 建立 artifact lineage。
4. 每個 transition 必須經 deterministic Evidence Gate。
5. 允許同一 checkpoint branch 3–5 個 candidate experiments，量 latency、reuse ratio、成功率與 cost。

如果這個 prototype 可以做到：

- process crash 後可 resume
- 同一 artifact 不重算
- failed experiment 可 isolated
- Agent 無法越權
- 每一次成功都有 evidence
- 所有 trajectory 可 replay

那就已經不是一個 demo。

它開始具備真正的 semiconductor control plane 特徵。

## 我的判斷

未來 EDA Agent 的競爭不會停在「哪一個模型比較懂 Innovus」。

模型能力會快速商品化，vendor-native agent 也一定會變強。

真正難複製的是：

```
Engineering State
+ Artifact Graph
+ Policy
+ Evidence
+ Execution History
+ Organization-specific Methodology
```

如果 R2G 能把這些東西變成一套穩定的平台語意，那麼未來接 Claude、GLM、Qwen、vendor agent，甚至完全不同的 execution backend，都只是 implementation choice。

真正留下來的，是一套公司自己掌握的晶片設計控制系統。

## References

- Kubernetes, *Controllers*  
  https://kubernetes.io/docs/concepts/architecture/controller/
- Temporal, *Durable Execution*  
  https://docs.temporal.io/
- The OpenROAD Project, *bazel-orfs*  
  https://github.com/The-OpenROAD-Project/bazel-orfs
- NVIDIA, *OpenShell*  
  https://github.com/NVIDIA/OpenShell
