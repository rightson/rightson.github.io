---
author: Scott Yo-Ru Chen
layout: post
title: "R2G 技術雷達：真正的核心是抽象層、可驗證執行與 Flow Graph"
date: 2026-09-22 12:11:00 +0800
categories: eda r2g agentic-ai
---

今天最值得注意的，不是又多一個 EDA Agent，而是三個方向開始收斂：高階抽象能顯著提高 agent 的設計效率；production agent 必須以環境最終狀態而不是「工具有呼叫成功」來判分；OpenROAD 生態則正在把 MCP、可重播 flow graph、可觀測工具介面組成更完整的 agent-native substrate。

這讓我對 R2G 的判斷更明確：真正值得長期投資的不是某一個 LLM 或 agent framework，而是把「工程意圖」轉成可執行、可驗證、可重播的 flow。

## Research：抽象層可能比模型本身更重要

UCLA 的 Zijian Ding、Yang Zou、Yizhou Sun 與 Jason Cong 在最新工作 *Can Agents Design Better Chips with a Higher Level Abstraction?* 中，比較直接 RTL、Agent-based HLS、Post-Compiler HLS Refinement、Post-HLS RTL Refinement 等方法。其 AHRR 流程先讓 agent 在 HLS 層完成設計，再以 RTL refinement 收回低階最佳化空間；在 11 個 FPGA benchmark 上，相對 Direct RTL Design 得到 2.6× geometric-mean speedup。

這個結果真正重要的不是 HLS 本身，而是它重新證明了一件事：Agent 的能力高度取決於它操作的 abstraction。

直接讓 agent 操作大量 RTL、Tcl、report 與工具細節，等於逼 reasoning model 同時處理「目標」與「底層機械細節」。如果中間有一層能保存設計意圖、constraint 與 transformation semantics 的 IR，agent 可以先在較穩定的空間做決策，再由 compiler / lowering 把意圖展開成 vendor-specific flow。

對 R2G，我會把它抽象成：

Human Intent
→ R2G IR / Flow Contract
→ Tool-specific lowering
→ EDA execution
→ deterministic evidence
→ low-level refinement

這比單純增加 MCP tools 更重要。

## Industry：Agent 是否成功，必須看 Environment State

NVIDIA 9/21 的 agent evaluation 技術文章把評估明確拆成兩層：

1. Process score：每一個 step / tool call 是否合理。
2. Outcome score：最後環境是否真的達成目標。

這個區分對 EDA 特別重要。

「PrimeTime command 執行成功」不是結果。
「Innovus script 沒有 exception」也不是結果。
真正的結果必須是重新讀取 artifact 後，timing、area、power、DRC、LEC 或其他 acceptance criteria 真的成立。

因此 R2G 的 completion contract 應該是：

Agent says done
→ ignore

Artifact persisted
→ clean replay

Deterministic checker passes
→ state transition allowed

NVIDIA 建議 production evaluation 同時追 success rate、multiple-trial consistency、steps per success、cost per success。這也代表未來比較 Claude、GLM、Qwen 或不同 harness，單看 benchmark accuracy 幾乎沒有意義；我們真正要量的是「同一個 R2G engineering task，在同一套 tool/environment 下，多少成本可以穩定完成」。

## Practitioner：OpenROAD 生態正在長出 Agent-native execution substrate

OpenROAD Project 在 9/21 同時持續更新 OpenROAD、OpenSTA、ORFS、bazel-orfs、OpenROAD-MCP 與 ORAssistant。

其中兩個方向尤其值得注意。

第一，OpenROAD-MCP 的 `read_orfs_metrics` 已經把原本大量 `find + cat + jq + grep` shell 操作收斂成一次具 domain semantics 的呼叫，同時讀取 stage metrics、rules gate、errors 與 warnings。官方 API 文件指出，這類 shell sequence 在 capability study 中約占 39% 的 shell usage。

第二，bazel-orfs 把 RTL-to-GDS flow 表成 explicit dependency graph：input 是 label、stage 是 target、artifact 可 cache，只有被修改所影響的 downstream stage 需要重跑。其 README 甚至直接把這種架構描述成「Plumbing an AI understands」。

這兩件事其實是同一個方向：

Semantic Interface
+
Typed Dependency Graph
+
Incremental Execution
+
Deterministic Validation

如果 R2G 擁有這四層，Agent 就不需要知道所有 shell plumbing，也不需要每一次從頭跑完整 flow。

## 我的判斷

未來 6–18 個月，我會優先投資三件事。

第一，建立 R2G IR / Flow Contract。讓 design intent、constraint、acceptance criteria 與可修改範圍成為正式資料，而不是 prompt 裡的文字。

第二，建立 Engineering Eval Harness。每個重要 agent task 都必須可以從 persisted artifact clean replay，並由 deterministic EDA result 判斷成功。

第三，建立 Incremental Flow Graph。知道一個變更 invalidate 哪些 downstream state，讓 agent 可以快速 branch、experiment、compare，而不是每次重新跑完整流程。

最終我認為比較合理的架構不是：

LLM → Tcl

而是：

Intent
→ R2G IR / Contract
→ Agent Reasoning
→ Semantic Tool / Raw Tool
→ Typed Flow Graph
→ EDA Engine
→ Deterministic Evidence
→ State Transition

LLM 可以替換，harness 可以替換，甚至底層 scheduler 可以從 LSF 換成 Kubernetes。

真正應該留下來的，是 design state、artifact lineage、engineering contract、evaluation result，以及累積下來的 trajectory。

## References

- Zijian Ding et al., *Can Agents Design Better Chips with a Higher Level Abstraction?*  
  https://arxiv.org/abs/2609.21157
- NVIDIA, *How to Evaluate AI Agents From Tool Calls to Task Completion*  
  https://developer.nvidia.com/blog/how-to-evaluate-ai-agents-from-tool-calls-to-task-completion/
- OpenROAD-MCP API  
  https://github.com/The-OpenROAD-Project/OpenROAD-MCP/blob/main/docs/API.md
- bazel-orfs  
  https://github.com/The-OpenROAD-Project/bazel-orfs
