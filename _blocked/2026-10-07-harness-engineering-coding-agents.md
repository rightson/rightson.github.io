---
layout: post
title: "Coding Agent 真正的差異開始出現在模型外面"
date: 2026-10-07 12:47:00 +0800
domain: ai-frontier
categories: ai-frontier
description: "分析 11 套 Agent、約 400 萬行程式碼的研究，把 coding agent 拆成 model 與 harness；真正值得吸收的不是宣告框架、向量搜尋或 MCP 誰輸誰贏，而是理解模型外圍如何決定工作能否可靠完成。"
takeaways:
  - who: "Coding Agent 使用者"
    value: "同一個前沿模型放進不同 Agent，實際體驗仍可能差很多，因為檔案怎麼找、工具何時呼叫、失敗後如何繼續，以及完成前檢查什麼，都由模型外圍的 harness 決定。"
  - who: "Agent 平台工程師"
    value: "研究最有價值的訊號，是成熟產品普遍自行掌握核心執行迴圈與工具介面；採用現成元件仍然可行，但關鍵執行語意需要能觀察、測試與控制。"
  - who: "Skills 與 MCP 生態系"
    value: "Skills 與 MCP 的採用數量接近，較合理的理解是兩者形成互補分工：前者攜帶工作方法與知識，後者提供外部能力介面，支援數量本身沒有決定技術勝負。"
  - who: "Coding Agent 產品團隊"
    value: "到 2027 年，模型能力若持續收斂，產品差異更可能集中在搜尋、工具、權限、長任務狀態與結果檢查；模型若再大幅跳升，harness 的最佳設計也會跟著改變。"
---

如果把 Claude Code、Codex CLI、Gemini CLI 或 OpenHands 換成同一顆模型，它們會變成差不多的產品嗎？

答案很可能是 **不會**。

模型決定 Agent 能理解與推理到什麼程度；但程式碼從哪裡找、工具怎麼呼叫、上下文滿了怎麼整理、指令失敗後怎麼繼續，以及最後憑什麼判定工作完成，都發生在模型外面。這一整層，近來常被稱為 **harness**。

2026 年 9 月公開的論文 [Harness Engineering: Anatomy, Architecture, and Evolution of Coding Agents](https://arxiv.org/abs/2609.00006) 嘗試把這件事系統化。研究分析 11 套 Agent 與約 400 萬行 Python、TypeScript、Rust 程式碼，涵蓋 Claude Code、Codex CLI、Gemini CLI、OpenHands、Aider、OpenCode、Mistral Vibe、Hermes 等系統，也把 OpenClaw 放進比較。

最值得帶走的不是「哪個技術輸了」，而是這個結構：

~~~text
使用者工作
    ↓
  Model       理解、推理、提出下一步
    ↓
 Harness      loop / context / search / tools / policy / state
    ↓
真實環境      repo / shell / compiler / tests / Git / API
~~~

真正的 Coding Agent，是三層一起工作。

## Harness 到底是什麼

最簡單的理解是：

> **Model 決定下一步可能做什麼；Harness 決定模型看得到什麼、做得到什麼，以及做完之後系統相信什麼。**

假設任務是「修掉 repository 裡造成測試失敗的 bug」。只有模型時，我們可以把程式貼進 prompt，請模型回答修改方式。加入 harness 後，工作會變成：找 repository 結構、搜尋錯誤與測試、讀檔、產生 patch、寫入、執行測試、讀取失敗、再次修改，最後確認 diff 與測試結果。

模型只參與其中幾個決策點；大量可靠性來自外圍程式把「思考」接成「可以完成的工作」。

本站先前討論[模型升級如何牽動工具回合與工作狀態](/ai-frontier/2026/10/01/model-upgrade-thinking-tool-history-contract.html)時，已經碰到同一個問題：模型 API 可以換，正在進行的工作卻還包含工具結果、歷史狀態與外部副作用。Harness 正是承接這些責任的地方。

## 為什麼成熟產品自己掌握核心迴圈

研究樣本中的產品沒有直接依賴 LangChain、LangGraph、AutoGen 等通用 agentic framework 來承擔核心 runtime。這很值得注意。

Coding Agent 的主迴圈表面上甚至可以簡化成：

~~~python
while not done:
    response = model(context, tools)
    result = execute(response.tool_calls)
    context.append(result)
~~~

真正困難的是每一行後面的問題：工具逾時時操作到底有沒有發生？Context 太大時哪些內容可以丟？模型連續走錯方向時何時停止？Shell 可以碰哪些路徑？Agent 說測試成功時，系統是否真的拿到對應 revision 的成功結果？

產品做到後面，這些行為會直接影響除錯、成本與安全，因此核心 runtime 往往需要很高的可控性。

但這個觀察只能推出：**這批成熟產品傾向自己掌握關鍵執行語意。** 它沒有證明通用 framework 沒有價值。

[Anthropic 在 2024 年的 Building effective agents](https://www.anthropic.com/research/building-effective-agents) 就提出一個至今仍實用的方向：從簡單、可組合的模式開始，只在需要時增加複雜度；使用 framework 時，也要理解底層行為。這個歷史脈絡比「framework 已死」更接近現在看到的產品演化。

## Coding Agent 不用向量搜尋了嗎

研究中的 Agent 普遍使用 ripgrep、glob、檔案樹、語法解析等方式尋找程式，而沒有把 vector embedding 當成主要 code retrieval 路徑。

這很合理。程式碼有大量問題具有強烈結構線索：function 在哪裡被呼叫、誰寫入 config key、error string 從哪裡丟出、哪個 class implement 某個 interface。對這類問題，文字搜尋、symbol index、AST 或 language server 通常便宜、快速，而且結果容易解釋。

例如已經看到：

~~~text
ConfigError: unsupported target architecture
~~~

第一步用 rg 找出這段字串，往往比先把整個 repository 做 embedding 更直接。

但另一類問題不同：「這個系統裡負責使用者取消工作後清理資源的邏輯在哪裡？」如果不知道專案把它命名成 abort、cancel、cleanup、reaper 還是 finalize，semantic search 就可能補上 lexical search 的盲點。

Cursor 公開的 [Semantic Search at Cursor](https://cursor.com/blog/semsearch) 描述 regex 與 semantic search 並存，並報告自家離線評估與線上實驗的改善。這足以說明「研究樣本沒有採用」與「這種方式已經輸掉」是兩個不同命題。

較合理的方向是 **hybrid retrieval**：已知 symbol、error、filename 時優先走 grep / glob / symbol / AST；問題語意模糊、跨文件、未知命名時，再加入 semantic retrieval，最後仍回到原始檔案確認。

## Skills 真的打敗 MCP 嗎

論文統計中，Skills 出現在 9/11 個系統，MCP 出現在 8/11 個系統。如果只看數字，很容易寫成「SKILL.md 9：8 擊敗 MCP」。問題是兩者主要回答不同問題。

**Skill 比較像「這件工作怎麼做」。** 它可以包含步驟、領域知識、範例、script 與注意事項。

**MCP 比較像「我要怎麼接到外面的能力」。** 它讓 Agent 用標準化介面取得工具、資源與外部服務。

~~~text
Skill：做 release 前先跑哪些檢查？
              ↓
            Agent
              ↓
MCP / CLI / API：怎麼取得 CI、issue、artifact 或部署狀態？
~~~

因此，9/11 與 8/11 比較像兩種機制都快速進入 Agent 生態，而不是只能留下一個勝方。

真正重要的分界反而是：**文字指引與實際權限是兩回事。** Skill 可以寫「不要修改 production」，真正阻止寫入 production 的能力，仍應由 credential、sandbox、server-side authorization 或執行環境限制。方法可以放在 Markdown，安全限制則需要由機器執行。

## OpenClaw 提醒我們別把分類當成事實

論文把 OpenClaw 當成 coding agent 之外的對照案例，因為它更接近 personal AI assistant gateway。這個比較方向有價值，但若進一步說 OpenClaw「自己不會寫程式，只把 coding 外包給其他 Agent」，就太絕對。

論文所選版本附近的 OpenClaw 文件已列出 read、exec、edit、write 等核心工具。也就是說，它的**產品定位不是 coding-first**，與它**能不能直接讀寫程式碼**，是兩個不同問題。可參考 [OpenClaw v2026.6.11 的 Agent 文件](https://github.com/openclaw/openclaw/blob/v2026.6.11/docs/concepts/agent.md)。

這個小落差反而是很好的閱讀提醒：source-code study 仍包含分類、命名與研究者判斷。研究最大的價值是提供比較地圖；重要結論仍值得回到對應版本的文件與程式碼確認。

## Harness 改變的是 Agent 的工程單位

早期使用 LLM 寫程式，我們常把工程單位想成：

~~~text
Prompt → Model → Answer
~~~

Coding Agent 把它擴大成：

~~~text
Task → Observe → Decide → Act → Inspect → Update state → Check
         ↑                                      │
         └──────────────────────────────────────┘
~~~

這就是 harness engineering 真正有意思的地方。

優化 prompt 仍然重要，但工程問題已經變成：**怎麼設計一個能反覆取得真實回饋、保留狀態、限制動作，最後用外部結果判斷是否完成的迴圈。**

所以「Agent = Model + Harness」是很好用的心智模型，卻不是 Model 50%、Harness 50%。模型變強可能讓 loop 少跑幾輪；反過來，模型不變，只要 retrieval 更準、工具回饋更清楚、context 管理更好，也可能提高整件工作的完成率。

兩者是耦合系統。

## 如果自己做 Agent，先投資哪裡

| 優先 | 能力 | 最先回答的問題 |
| --- | --- | --- |
| 1 | Tool interface | 模型能做哪些事，結果如何明確回傳？ |
| 2 | Search / context | 每一輪真正需要看到哪些資訊？ |
| 3 | Loop state | 工作做到哪裡，外部世界已發生什麼？ |
| 4 | Permission | 哪些動作可以直接做，哪些需要限制？ |
| 5 | Result checking | 系統憑什麼接受「完成」？ |
| 6 | Extension | 新工具、新 Skill、新資料源如何加入？ |

這個順序刻意沒有把「換更強模型」放進表內，因為模型選擇是另一個維度。如果問題其實是 Agent 沒讀到正確檔案、工具回傳資訊不足，或完成條件根本沒被程式檢查，更大的模型可能只是在更昂貴地走同一條錯路。

反過來也一樣。遇到真正需要深層推理、跨檔案理解或陌生問題分解的任務，模型能力仍可能直接決定上限。

## 到 2027 年值得觀察什麼

第一，模型與 harness 的評測會逐漸拆開：固定模型比較不同 Agent，也固定 Agent 比較不同模型。

第二，Skills 會從提示文件往可管理的工作資產演進。版本、來源、信任等級、依賴與測試，會比「多放幾份 Markdown」更重要。

第三，長任務狀態會成為主要競爭點。Coding Agent 從幾分鐘走向數小時甚至跨天工作後，restart、checkpoint、外部副作用與中途改需求，都會逼 runtime 從聊天迴圈變成真正的工作執行系統。

如果到了 2027 年，反而是模型能力跳升讓工具層大幅簡化，那就表示價值重心仍更靠近 model。這也是「harness 會持續變重要」最值得觀察的反例。

## 證據範圍

本文以論文公開內容、OpenClaw 對應版本文件、Anthropic 2024 年工程文章與 Cursor semantic search 技術文章交叉閱讀；沒有重新執行 11 套 Agent 的原始碼分析，也沒有重跑 Cursor 的實驗。論文呈現的是特定版本與樣本的架構觀察，不能直接當成 framework、向量檢索、Skills 或 MCP 的效能排名。

## 來源

- [Harness Engineering: Anatomy, Architecture, and Evolution of Coding Agents](https://arxiv.org/abs/2609.00006)
- [Anthropic: Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [Cursor: Semantic Search at Cursor](https://cursor.com/blog/semsearch)
- [OpenClaw v2026.6.11: Agent concepts](https://github.com/openclaw/openclaw/blob/v2026.6.11/docs/concepts/agent.md)
- [Agent Skills](https://agentskills.io/what-are-skills)
- [Model Context Protocol](https://modelcontextprotocol.io/)
