---
layout: post
title: "ORAssistant 的兩次修正揭露 CAD Agent 的驗收盲區：來源映射與評分語意"
date: 2026-09-26 06:04:54 +0800
domain: eda
categories: eda
description: "OpenROAD 的 ORAssistant 修補了文件來源映射、失敗建置與評分方向；對 CAD Agent 而言，可信的回答必須能連回正確版本的證據，評估分數也必須保留語意與門檻。"
---

一個 CAD 助理回答了正確的 Tcl 指令，工程師點開引用卻找不到原始文件；另一個版本把 hallucination score 的方向改了，報表仍沿用舊的高低判斷。這兩種錯誤看起來都不像 EDA 演算法問題，卻足以讓平台把不可靠的建議當成通過驗收的工程知識。

OpenROAD 專案的 ORAssistant 在 9 月 25 日 UTC（台北時間 9 月 26 日凌晨）合併的兩組修正，剛好把這個問題攤開。[文件建置與來源修正](https://github.com/The-OpenROAD-Project/ORAssistant/commit/044ad94fa7e5fe0ce6af15129d0dc4252317cad4)修復了來源 URL 表被重設、文件建置失敗沒有中止，以及重複下載論文；[評估修正](https://github.com/The-OpenROAD-Project/ORAssistant/commit/555a92426489c97830fa4f5e5680663b281641b4)則把 DeepEval 4 的 hallucination、bias、toxicity 分數方向寫進程式與測試。這是開源專案的程式修補，不是商用晶片專案已導入的證據；但它提供了可以逐行檢查的設計平台案例。

## 從問答系統到設計流程，信任鏈在哪裡斷掉

ORAssistant 起於 2024 年的 OpenROAD 問答系統。Aviral Kaintura（National Forensic Sciences University）等人的[原始論文](https://arxiv.org/html/2410.03845v2)描述：把 OpenROAD、OpenROAD-flow-scripts、OpenSTA、Yosys、KLayout 文件及社群討論切塊，建立語意與 BM25 檢索，再經 re-ranking 選擇上下文；系統按安裝、命令、錯誤等主題路由，最後由模型生成答案及引用。這種分工對 EDA 很合理：工程師可能只記得錯誤碼，也可能用自然語言描述「CTS 後 timing 變差」，兩者需要不同檢索方式。[現行 README](https://github.com/The-OpenROAD-Project/ORAssistant/blob/master/README.md)仍把 hybrid retrieval 與各類 retriever 列為主要架構。

論文在 100 題 EDA Corpus、50 題自建 QA、每題五次獨立執行的設定下，報告 ORAssistant 的 EDA Corpus accuracy 90.4%、precision 94.8%，相對基礎 GPT-4o 的 48.4%、48.4%；平均回應時間則為 2.6 秒，GPT-4o 4.7 秒、Gemini 1.5 Flash 2.3 秒。[論文結果表](https://arxiv.org/html/2410.03845v2#S5)值得讀，但這是 2024 年問答 benchmark 與 LLM judge 的結果，不能推成「90.4% 的 APR 動作安全」；也不能直接與 2026 年不同評估器版本的分數畫成同一條趨勢線。

這個轉換還牽涉一個常被忽略的時間問題。文件不是一個永遠指向當前事實的 URL：主分支的 man page 今天可能修正參數預設值，昨天的 run 卻使用上一個容器映像與舊 Tcl。若 agent 在解釋昨天的失敗時檢索今天的文件，就算引用可點開，也未必是當時有效的規則。對 EDA 而言，`evidence_at_query_time` 與 `evidence_at_execution_time` 必須分開；前者支援現在的診斷，後者支援事故回溯。更進一步，constraint 是設計團隊交付的工程假設，report 是工具對特定輸入的觀察，兩者不能在向量資料庫中被當作同等可信的段落。檢索層應保留來源類型與權限，不能讓社群討論覆蓋專案的批准約束。

將問答架構直接複製到企業 CAD farm，還會遇到 corpus 分區。某個製程的錯誤碼與一般 OpenROAD 命令說明可共享，但某客戶的 clock period、IP 名稱、macro 座標與 netlist 不能跨專案出現在同一索引或同一 reranker 的上下文。光在 UI 顯示「你無權讀取」太晚了：檢索前就要決定可見集合，chunk 與 source map 也必須帶相同 policy label。否則模型即使不直接輸出敏感值，也可能透過相似結果與拒答差異洩露其他專案的存在。這是作者對企業環境的架構推論，ORAssistant 的公開資料庫並未聲稱具備這種隔離。

問答的最小可驗證單位是「這句答案由哪份文件的哪個版本支持」。執行型 agent 的最小可驗證單位還要多一層：「誰授權哪個動作、用了哪份設計與 constraint、工具實際改了什麼 artifact、哪份 report 證明結果」。ORAssistant 已有將問題分到 RAG、架構產生與 MCP 動作路徑的[分類圖](https://github.com/The-OpenROAD-Project/ORAssistant/blob/master/backend/src/agents/retriever_graph.py)，也有把 MCP 工具呼叫接進 LangGraph 的[實作](https://github.com/The-OpenROAD-Project/ORAssistant/blob/master/backend/src/agents/retriever_mcp.py)。這證明程式有「回答」與「執行」的路徑，卻不等於它已提供本文後面提出的完整授權與 artifact 驗收契約。

![文件到工程動作的證據鏈](/images/eda/2026-09-26/orassistant-evidence-chain.svg)

圖：作者依 [ORAssistant 論文](https://arxiv.org/html/2410.03845v2)與 [現行程式](https://github.com/The-OpenROAD-Project/ORAssistant/blob/master/backend/src/agents/retriever_graph.py)整理；下方的工程動作驗收閘門為作者設計，非 ORAssistant 官方架構。

## 第一個失效機制：檢索內容還在，來源身分先消失

這次來源修補並非模型突然變得不會回答。[修正 diff](https://github.com/The-OpenROAD-Project/ORAssistant/commit/044ad94fa7e5fe0ce6af15129d0dc4252317cad4)顯示，原本寫出 `source_list.json` 前，程式把累積其他文件來源的 `source_dict` 重設為空字典，接著只加入 GitHub discussions 的映射。文件 chunk 可能還存在、向量索引也可能搜得到；但回傳時找不到原始 URL，引用就斷了。新版本抽出 `write_source_list()`，在既有映射上加入 discussions，並用回歸測試確認 OpenROAD 文件 URL 與 discussion URL 能同時保留。

這個細節對平台資料模型比「引用格式」重要。chunk ID 只是檢索引擎的位址，不是工程證據的身分。若把一份指令文件、某個 tool version 的 man page、某次 run 的 error report 都壓成一段文字，沒有保留 source URI、revision、access scope、擷取時間與 content hash，模型生成的句子即使碰巧正確，也無法回答「這個專案此刻能不能採用」。一個可落地的 evidence record 至少應連結 `source_id → repository/version/path/span/hash → allowed_scope`；對 run report 再加 `run_id/stage/input_artifact`。這是本文的參考資料模型，不是 ORAssistant 現有 schema。

同一組修正還把 OpenROAD、ORFS 文件的 `make html` 與 manpage build 改成失敗即退出，並把同一 PDF URL 的重複下載排除。[build_docs.py](https://github.com/The-OpenROAD-Project/ORAssistant/blob/master/backend/build_docs.py)與[新增測試](https://github.com/The-OpenROAD-Project/ORAssistant/blob/master/backend/tests/test_build_docs.py)可核對。過去的風險不是單純「少幾份文件」：建置指令即使回傳非零，後續仍可能產出一個看似成功的知識庫，讓缺漏在回覆品質下降後才被發現。相反地，fail-closed 會讓這次 corpus generation 明確失敗，保留上一版可用 snapshot；但若來源網站暫時故障，也會犧牲新版本上線速度。工程上需要同時提供可用性與新鮮度訊號，而不是把兩者混成一個綠燈。

測試中的 source map 行為還揭示一種多階段 pipeline 的典型錯誤：前面每一個 producer 都確實寫入自己的映射，最後一個 consumer 卻在合併邊界重新初始化共同狀態。單元測試若只測「GitHub discussion 有 URL」，會通過；只有同時放入來自 OpenROAD 文件與 discussion 的樣本，才能抓到跨來源的資料遺失。對設計平台也一樣：LEF、Liberty、SDC、UPF、RTL 分別解析成功，不代表最後的 run manifest 還保有每個來源的 identity。驗證應跨越 artifact join，而不是只對每個 importer 打勾。

此外，`make html` 回傳非零與 `source_list.json` 不完整是兩個不同失敗。前者屬於 producer 沒產生預期輸出；後者屬於 aggregate 組裝時遺失關聯。若只檢查檔案存在，舊檔會讓壞的 build 看似成功；若只檢查 process exit code，語意上不完整的映射仍可能上線。比較穩妥的發佈程序是先在 staging 建立候選 corpus，檢查文件數、不同來源的 mapping coverage、唯一 URL 比率與抽樣回鏈；全部通過後才原子切換 serving snapshot。回退時保留上一版 corpus 與其 embedding model、source map 配對，不能只回退其中一個檔案。

這也解釋了為什麼「索引最新」不是唯一目標。對正在排查故障的工程師，舊但完整且標清版本的說明，比新但缺了一半引用的答案更可用；對安全性或製程規則變更，反過來可能必須禁止引用舊版。平台因此需要明確的 freshness policy：哪些來源可短暫沿用上一版，哪些來源一旦更新失敗就要讓回答降級甚至拒答。政策要按資料類型定，不能由 RAG 模型臨場猜。

![知識庫建置的失敗路徑與恢復點](/images/eda/2026-09-26/orassistant-corpus-failure.svg)

圖：作者依 [9 月 25 日修正與測試](https://github.com/The-OpenROAD-Project/ORAssistant/commit/044ad94fa7e5fe0ce6af15129d0dc4252317cad4)整理失效點；snapshot 發布閘門與回復策略是作者設計。

## 第二個失效機制：數字一樣，判分意義翻了面

ORAssistant 另一組同日修正針對 DeepEval 版本升級。[retrieval metric 程式](https://github.com/The-OpenROAD-Project/ORAssistant/blob/master/evaluation/auto_evaluation/src/metrics/retrieval.py)註明，DeepEval 4 的 hallucination score 是「答案沒有與 context 矛盾的比例」，高分較好、須大於或等於 0.7；DeepEval 3 使用矛盾比例，低分較好。若把舊版 0.7 當成新版同一門檻，兩者實際容許的矛盾程度不同，升級前後的 pass rate 不能直接比較。bias 與 toxicity 也由不良意見比例轉向無不良意見比例。[程式 diff](https://github.com/The-OpenROAD-Project/ORAssistant/commit/555a92426489c97830fa4f5e5680663b281641b4)把這個方向寫清楚，並以 mocked judge verdict 測試 threshold 的判斷。

新增測試提供一個乾淨的量化例子：十份 context 中有三份被判矛盾，新版 score 為 0.7，通過；四份矛盾，score 0.6，失敗。[測試程式](https://github.com/The-OpenROAD-Project/ORAssistant/blob/master/evaluation/auto_evaluation/tests/test_metrics.py)只驗證 scoring 與 threshold 的語意，judge 的輸出是 mock，**不代表實際十份 EDA 文件裡有三份錯誤**。這點要與論文的 benchmark 結果分開。若內部 dashboard 只記 `metric=hallucination, threshold=0.7, score=0.7`，沒有版本、方向、輸入 context 與 judge 資訊，半年後無法重建「通過」究竟是什麼意思。

更可靠的評估事件應包含 `metric_name`、`metric_impl/version`、`score_direction`、`threshold/comparator`、`judge_model/version`、`dataset_revision`、`retrieval_corpus_hash`、`tool_release`、`sample_id` 與原始 verdict。這些欄位看起來囉嗦，卻讓升級可做雙跑：同一批題目同時計算舊版與新版，先看排序、錯誤類型和邊界樣本，再決定是否改門檻。沒有這個橋接期，圖上的進步可能只是量尺換了方向。

評分方向之外，指標本身也必須對準工程風險。一般 RAG hallucination metric 問的是回答與提供的 context 是否矛盾；它不會自動知道該 context 是否屬於正確的 OpenROAD 版本，也不會知道變更 placement density 是否破壞 hold、congestion 或 routability。因此同一個 agent 應至少有三層獨立測試：citation validity（來源是否可回鏈且版本相符）、answer groundedness（敘述是否受證據支持）、flow outcome（工具產物是否滿足設計驗收）。前兩層失敗時可以阻止 action proposal；前兩層通過仍不能跳過第三層。把問答 benchmark 的百分比拿來當 tape-out 風險，是評估對象錯位。

可以用一個透明的假設算例看出這個落差。假設一百次建議各有 90% 機率引用正確、90% 機率通過語意審核、90% 機率在實體工具驗收通過；若三者獨立，端到端只有 `0.9³ = 72.9%`。這不是 ORAssistant 測得的可靠度，三事件也不一定獨立，只用來說明單一 90% 指標無法直接代表整條工作流。實際情況可能更差：錯誤來源會同時污染答案與動作，形成相關失敗；也可能因後段嚴格驗收而被擋下。評估報表應分層顯示每個 gate 的條件通過率與攔截成本，不能用一個總分掩蓋不同失敗型態。

![評估版本與門檻方向的比較](/images/eda/2026-09-26/orassistant-metric-semantics.svg)

圖：作者依 [ORAssistant 指標修正](https://github.com/The-OpenROAD-Project/ORAssistant/commit/555a92426489c97830fa4f5e5680663b281641b4)與 [mocked verdict 測試](https://github.com/The-OpenROAD-Project/ORAssistant/blob/master/evaluation/auto_evaluation/tests/test_metrics.py)重畫；例子是測試資料，不是現場量測。

## 把問題放回一條 SYN／APR flow

以下是一個**作者設計的最小情境**，不是 ORAssistant 原專案實測。假設一個公開 toy RTL 的 floorplan 在 placement 後出現 timing regression，工程師問：「是否能調整 placement density？改完要看哪些 report？」平台先把問題連到特定 ORFS 版本的變數文件，檢索回 `PLACE_DENSITY` 的定義、適用 stage 與設計端覆寫優先順序。[ORFS FlowVariables](https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts/blob/master/docs/user/FlowVariables.md)確有這個變數及設定途徑；但是「文件提到可調」並不等於「這個 design 改了就會改善 timing」。

推薦的執行記錄可表為：

```yaml
proposal:
  design_revision: <public-toy-rtl-commit>
  stage: placement
  change: {PLACE_DENSITY: <candidate>}
  evidence: {doc_uri: <versioned-url>, doc_hash: <sha256>}
  input: {netlist: <hash>, sdc: <hash>, prior_odb: <hash>}
  policy: {scope: sandbox, approval: required-before-write}
  acceptance:
    - timing_report_from_same_run
    - utilization_and_congestion_report
    - baseline_comparison_with_same_tool_revision
```

這裡的關鍵是 `proposal` 和 `run` 分離。助理可以說明變數，但只能以候選參數提交 sandbox。flow controller 驗證 scope、成本、版本與授權後才啟動；結果 ODB、log、timing、congestion report 都要綁同一個 run ID。若新候選的 timing 變好但 congestion 惡化，就不能只貼一個 WNS 數字宣稱成功。若工具 timeout，保留 partial artifacts 為 `failed/incomplete`，不拿前一輪的 report 配這一輪的 config；若重試，輸入 hash 與 run key 決定沿用哪個 checkpoint，而不是靠檔名 `latest`。這套驗收與恢復是本文推導的設計方案。

把這個情境映射到平常的工程工作，`proposal` 就像一份有版本的 Tcl 修改建議；`run manifest` 是 Makefile、工具版本、輸入檔與環境變數的封存索引；`acceptance` 是一組可機器讀取的 report 判準。原本由資深工程師口頭記住「這個 option 在這個 design 不要開」的知識，可以先轉成帶條件的 guardrail，再讓 agent 引用。它的權威性仍要由 flow owner 授予，不能因模型從幾份成功 report 歸納出規則就自動成為 policy。這也讓 policy 的變更有測試入口：新規則先 replay 歷史 run，計算擋掉多少已知失敗、誤擋多少合法修復，再進入影子模式。

若一次參數探索要同時跑三個候選，還需要分清「共享哪一段已驗證前綴」。RTL 與 SDC 未變時，可以共享 synthesis netlist 或 placement 前 checkpoint；但工具版本、corner、license 特性或上游 seed 改了，直接重用 checkpoint 可能讓三個候選實際上不是可比較的實驗。以內容 hash 和明確依賴圖決定 cache key，能減少重跑；以 stage name 或人類可讀路徑決定，則容易把舊輸出混入新 run。這是典型的分散式執行正確性問題，與 agent 會不會寫 Tcl 是兩個層次。

ORAssistant 的 MCP 路徑讓上述風險更加具體：[trigger 說明](https://github.com/The-OpenROAD-Project/ORAssistant/blob/master/backend/MCP_AGENT_TRIGGER.md)把「run synthesis」「make clean_all」等語句導向動作；[目前的 prompt 範例](https://github.com/The-OpenROAD-Project/ORAssistant/blob/master/backend/src/prompts/tool_examples.py)要求從可用工具選一個。工具選擇成功只證明意圖被翻譯成呼叫，不能證明呼叫已獲授權、影響範圍可接受，更不能證明設計結果合格。對共享 license、scratch 與多專案資料來說，`clean_all` 比一次錯誤回答更難補救。本文不聲稱 ORAssistant 缺乏所有外層防護；公開程式與文件不足以證實端到端的企業級審批與隔離保證。

## 兩種平台方案的真正取捨

直接把文件搜尋與 MCP 工具接到模型，是很好的探索原型：開發快、研究者能觀察工具使用、文件一更新就能試新知識。代價是知識庫、模型判斷和 tool write path 太容易被視為同一個「成功」。來源 URL 遺失時仍有文字；評分器升級時仍有數字；tool exit code 為零時仍不一定有可採信的設計結果。

另一種方案在兩者中間加一個薄的 evidence／execution gate：檢索只回版本化證據；agent 只產出 typed proposal；gate 做 scope、approval、budget、idempotency 與 artifact binding；工具 report 再由獨立驗收器讀取。它增加 schema、狀態存放、跨工具 adapter 與維運成本，也會讓探索慢一點；但它把「模型可以建議」與「平台願意承諾結果」分開。若任務只是查一條 OpenROAD 指令，這層 gate 不必參與。只有在改 Tcl、提交 batch job、覆寫 checkpoint、跨專案讀 report 時，授權與可恢復性才值得這筆成本。

對分散式執行尤其不能只在 job queue 加一個 agent。source corpus、agent proposal、flow input、tool container、EDA result 和 evaluator 各自可能在不同時間更新。最小一致性單位應是一次 run 的 manifest，記錄全部版本與 artifact hash；多個 worker 可以重試同一個步驟，但只有通過驗收的結果能被提升為下游 stage 的 input。當某個文件重建失敗時，不應讓新向量索引搭配舊 source map；當 evaluator 換版時，不應悄悄覆蓋原有分數。這些是可在開源 flow 做出的平台保證，不依賴取得商用 PDK。

還有一個部署順序問題。正式環境的 corpus 與 evaluator 不必在同一秒更新，但每一次回答都要能說出它使用哪個穩定組合。假設索引 A 已發布、source map B 正在寫入，若 serving 端只讀 `latest`，同一筆回覆可能混用 A 的 chunk ID 與 B 的 URL。可把 corpus manifest 當成 immutable release，將 embedding index、source map、parser 版本與允許的文件範圍放在同一個 manifest hash 下；服務程序只切換 manifest pointer。更新失敗時仍服務完整的上一版，並標示知識新鮮度；不是把半套新資料交給模型補空白。這種做法和 APR checkpoint 的原子交接是同一個工程問題：下游只接受成套、可追溯的輸入。

對治理而言，審核點也不應只設在聊天介面。若 agent 先從不當範圍檢索，再由人類批准工具呼叫，敏感資料已進入模型上下文；若只在檢索層做 ACL，卻讓工具用服務帳號跨專案寫入，也同樣失守。讀取授權、proposal 授權與執行授權需要綁定同一 project identity，最後的 report artifact 再按相同範圍標記。拒絕一個提案時保留理由與最小必要 trace，才能區分模型誤判、政策過嚴與工具異常，而不必把原始私有報告送進跨專案知識庫。

## 接下來該驗證什麼

第一步不用把 agent 放進 APR 最貴的迴圈。用十份公開 ORFS 文件、三個故意失效的來源、一份 toy report，建立「每個回答的引用都能回到精確版本」測試；再故意讓文件 build 失敗，確認新 corpus 沒有被標成 ready。第二步拿同一批十個 mocked verdict 做兩版 metric adapter，測試高低方向、邊界值、歷史分數不可比較的標記。第三步才把一個無寫權的建議升級成 sandbox proposal，觀察 run manifest 是否能在 timeout／retry 後避免把舊 report 接到新參數。

這三步如果做不出來，增加更強模型或更多 skill 只會讓不確定性跑得更快。ORAssistant 這次的修補提醒我們：CAD agent 的品質會被最普通的資料工程與評估工程決定。下一個值得追的證據，不是它能呼叫多少 EDA 命令，而是知識、權限、執行與驗收能否在同一個 run 上對得起來。

## References

1. [ORAssistant: A Custom RAG-based Conversational Assistant for OpenROAD](https://arxiv.org/html/2410.03845v2) — Aviral Kaintura et al., arXiv v2, 2024-11-30。
2. [ORAssistant repository and architecture README](https://github.com/The-OpenROAD-Project/ORAssistant/blob/master/README.md) — The OpenROAD Project，持續更新。
3. [Fix corpus source mapping and docs build failures](https://github.com/The-OpenROAD-Project/ORAssistant/commit/044ad94fa7e5fe0ce6af15129d0dc4252317cad4) — ORAssistant commit，2026-09-25。
4. [Pin DeepEval 4 score direction](https://github.com/The-OpenROAD-Project/ORAssistant/commit/555a92426489c97830fa4f5e5680663b281641b4) — ORAssistant commit，2026-09-25。
5. [ORAssistant evaluation harness and mocked metric tests](https://github.com/The-OpenROAD-Project/ORAssistant/blob/master/evaluation/auto_evaluation/tests/test_metrics.py) — The OpenROAD Project，2026-09-25 版本。
6. [OpenROAD Flow Scripts variables](https://github.com/The-OpenROAD-Project/OpenROAD-flow-scripts/blob/master/docs/user/FlowVariables.md) — The OpenROAD Project，線上文件。
