---
layout: post
title: "BTTF 把 waveform 轉成 SQL，讓 Agent 進入 post-simulation debug"
date: 2026-10-07 06:32:00 +0800
domain: ic-design-platform
categories: ic-design-platform
series: agentic-design-radar
permalink: /ic-design-platform/2026/10/07/bttf-waveform-sql-agent.html
description: "BTTF 將大型 waveform 正規化成可查詢的關聯資料，再以多 Agent 分工做訊號搜尋、assertion 檢查與 RTL 定位；新結果顯示 EDA Agent 的能力開始取決於設計資料是否具有低延遲、可組合的查詢介面。"
takeaways:
  - who: "BTTF"
    value: "BTTF 把 VCD 的 signal metadata 與時間變化拆成關聯資料，讓模型以 schema-aware SQL 查詢大型模擬結果；150 題整體 execution accuracy 為 95.33%，顯示 post-simulation debug 可以從 GUI 人工瀏覽轉成工具化查詢。"
  - who: "晶片驗證團隊"
    value: "晶片驗證團隊若先把 waveform、coverage、log 與 RTL version 做成可定位的資料介面，Agent 就不必把大量 dump 塞進 context；代價是 ingestion、索引、scope 正規化與資料保留策略成為新的平台工作。"
  - who: "EDA 平台團隊"
    value: "EDA 平台團隊可以把模型與 simulator 之間的介面從文字 log 擴成 query service，讓既有 deterministic engine 繼續產生結果、Agent 負責查詢與關聯；這比替每套 GUI 錄製操作軌跡更容易量測正確率與延遲。"
  - who: "EDA 工具供應商"
    value: "EDA 工具供應商若提供穩定的 waveform、coverage 與 source mapping API，會直接降低 Agent 整合成本；若資料仍鎖在 proprietary viewer 與檔案格式，模型再強也會把大量時間耗在資料轉譯與定位。"
---

大型模擬失敗後，工程師常做的不是重新寫 RTL，而是打開 waveform、沿 hierarchy 找訊號、定位 assertion 失敗時間，再回到對應的 RTL。這段工作很適合人用 GUI 探索，卻不適合直接把原始 dump 丟給 LLM：一個 SoC block 的 VCD 可以超過數 GB，時間序列又需要精確的 scope、timestamp 與 value semantics。

10 月 5 日公開的 [Back to the Future（BTTF）](https://arxiv.org/abs/2610.06790)提出另一種做法：先把 waveform 轉成關聯資料，再讓 Agent 操作資料庫。論文處理的 4.2 GB VCD 含 18,450 個 nets，將訊號宣告與時間變化拆成兩張主要 table；上層 Agent 以自然語言規劃，再產生 schema-aware SQL、執行 assertion 檢查，並把異常訊號連回版本化 RTL。

這和本系列先前討論的 [可驗證 IC 設計狀態](/ic-design-platform/2026/09/23/ai-native-ic-platform-typed-design-state.html)接上了一個缺口：設計狀態即使有版本，若大量動態結果仍只能靠人打開 viewer 搜尋，Agent 仍無法有效使用它。BTTF 的新意是把 post-simulation artifact 變成低延遲、可組合的查詢介面。

<figure>
  <a href="/images/ic-design-platform/2026-10-07/bttf-waveform-sql-agent.svg"><img src="/images/ic-design-platform/2026-10-07/bttf-waveform-sql-agent.svg" alt="Simulator 產生 VCD waveform，前處理將訊號 metadata 與時間變化寫入 SQLite；Orchestrator 分派分析與驗證 Agent 查詢資料庫並定位 RTL。" width="900" height="560" loading="lazy"></a>
  <figcaption>圖一：依據 BTTF 論文的 waveform preprocessing 與 multi-agent 架構重繪。資料路徑與角色來自論文；方塊配置為示意。</figcaption>
</figure>

## Waveform 先變成資料庫，context 問題才變成 query 問題

BTTF 的第一層不是 LLM，而是資料轉換。它把 signal declaration 放進 `signal_metadata`，把每次 value transition 以 timestamp 與 foreign key 寫入 `signal_changes`。Agent 查「某訊號第一次變成 42 的時間」時，不需要讀完整 VCD，只需要產生對應的 filter 與排序查詢。

這個選擇把成本從 token 移到 ingestion 與 index。論文的 fully unpruned database 為 1,420 MB，平均 query latency 410.5 ms；移除 clock transition 後縮到 480 MB，latency 降到 125.2 ms，保留 98.51% functional toggle coverage。再移除 zero-toggle signals，資料量降到 395 MB、latency 94.8 ms，論文報告 active-net coverage 仍為 100%。更激進的 below-average pruning 雖縮到 185 MB、41.6 ms，coverage 只剩 64.23%。[BTTF Table 1](https://arxiv.org/html/2610.06790#S4)

這組數字指出平台上的實際取捨：資料壓縮不能只看 storage ratio。若 pruning 移除了 root-cause 需要的低活動訊號，Agent 查得再快也沒有用。較合理的第一步是移除高頻 clock transition 與完全沒有切換的訊號，再依 debug workload 決定是否需要更積極的摘要。

Ingestion 本身也有工程成本。論文以 batched insertion 取代逐 row 寫入，最高得到 2.89× database generation speedup。對大型 regression farm 而言，這表示 waveform-to-queryable-store 應視為 simulation pipeline 的正式 stage，而不是 debug 發生後才臨時轉檔。

## 多 Agent 的收益來自工具分工，也付出近兩倍 latency

BTTF 把工作拆成 Orchestration、Analysis、Verification 與 Evaluation。Analysis Agent 專注 schema 與 SQL；Verification Agent 執行 ASSERT、ASSERT_STATIC、ASSERT_NEVER、ASSERT_KNOWN、COVER 等規則並關聯 source；Evaluation Agent 再檢查 query 是否符合 schema、時間條件與 scope。

150 個 expert-annotated queries 的整體 execution accuracy 為 95.33%。其中 scope/net discovery、value change count、event timing check 都報告 100%；RTL attribution 為 87.5%，static SVA check 為 84.62%，dynamic SVA check 為 90.91%。這些差距很重要：資料查詢已相當穩定，跨 waveform 到 source 或 assertion semantics 的任務仍較難。[BTTF benchmark](https://arxiv.org/html/2610.06790#S4)

論文也比較單一 Agent 與多 Agent。多 Agent 在五項 autorater 指標上的 reasoning quality 高 17.3%，但平均 latency 是 1.96×。因此平台不需要把每個查詢都送進完整協作流程。單一訊號 value lookup 可以走直接工具；需要跨 scope、source 與 assertion 的多步 root-cause 才值得付出 orchestration latency。

這也修正了「Agent 越多越可靠」的直覺。分工有價值的前提，是每個角色握有不同且明確的工具能力；若只是把同一份 context 在多個模型間轉述，成本會增加，資料品質卻沒有改善。

## 從 VerilogCoder 到 BTTF，介面正在從程式結構延伸到執行狀態

2025 年的 [VerilogCoder](https://ojs.aaai.org/index.php/AAAI/article/view/32000)已經讓 coding agent 透過 AST-based waveform tracing 處理硬體設計問題。BTTF 往前推了一步：它不只讓 Agent 看程式結構，而是把大量 temporal state 轉成一般資料系統熟悉的 relational query。

這個演進對 IC 設計平台的含義，比「又多一個 verification agent」更大。既有 EDA flow 已經有 simulator、waveform database、coverage database、log 與 source control；Agent 平台需要補的是穩定的 machine interface，讓這些 artifact 能被查詢、交叉定位與量測。

可行的導入順序是先做 read-only debug path。固定一批 regression failures，保留 engineer golden answers，量測 scope discovery、timestamp lookup、RTL attribution 與 assertion diagnosis 的正確率、P50/P95 latency、資料轉換時間與 storage overhead。等 read path 穩定，再決定是否讓 Agent 產生新的 assertion、test stimulus 或 RTL patch。這樣能把「會查」和「會改」分成兩個可獨立評估的能力。

未來 6–12 個月若這條路線成立，最值得觀察的訊號不是更大的 LLM，而是 EDA vendor 與內部 CAD 平台是否開始提供穩定的 waveform／coverage query API、source mapping，以及能跨 regression run 比較的 schema。若每套 simulator 仍需獨立解析 proprietary dump，BTTF 的方法仍有研究價值，但導入成本會停留在資料轉譯層。

## 週三相對週二的新增變化

本週既有 Agentic Design 主線已涵蓋模型操作 EDA 工具、design state 與跨工具流程。BTTF 新增的是另一個方向：Agent 不只需要 action surface，也需要為大型執行結果設計 query surface。

這會改變平台優先順序。對 post-simulation verification，先建立可查詢的 artifact layer，可能比先做 GUI agent 或增加模型 context 更有效。BTTF 的結果已顯示資料表示方式能把 4.2 GB waveform 轉成百毫秒級查詢；下一步要驗證的是相同方法能否跨 simulator、coverage database 與更長 regression window 保持準確。

## 證據範圍

BTTF 是 2026 年 10 月 5 日公開的研究論文，benchmark 使用 Gemini 2.5 Pro、4.2 GB VCD、18,450 nets 與 150 個人工標註 query；95.33% 是該資料集的 execution accuracy。論文沒有提供商用 full-chip regression 的 production deployment，也沒有證明 SQLite 是所有 waveform 規模的最佳 storage engine。

文中的 read-only 導入順序、direct-query fast path 與跨 artifact query layer 是依論文結果提出的工程推論。若後續在不同 simulator、proprietary waveform、數十到數百 GB window 或多使用者環境中，ingestion 成本、source mapping error 或 query latency 明顯惡化，就需要改用 columnar／time-series storage、分散式索引或 vendor-native API，而不能直接沿用目前配置。

## References

- Je Yang, Ivan Lobov, Thomas Karpati, [Back to the Future: Rethinking EDA Infrastructure for Agentic Systems in Chip Design Verification](https://arxiv.org/abs/2610.06790), 2026-10-05.
- BTTF HTML full text, [framework、preprocessing 與 benchmark tables](https://arxiv.org/html/2610.06790).
- Chi Ho, Haoxing Ren, Brucek Khailany, [VerilogCoder: Autonomous Verilog Coding Agents with Graph-based Planning and AST-based Waveform Tracing Tool](https://ojs.aaai.org/index.php/AAAI/article/view/32000), AAAI 2025.
