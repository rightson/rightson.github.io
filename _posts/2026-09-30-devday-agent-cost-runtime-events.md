---
layout: post
title: DevDay 2026：較低成本模型與持續型 Agent 改變工作設計
date: 2026-09-30 08:39:59 +0800
domain: ai-industry
categories: ai-industry
series: ai-frontier-digest
description: GPT-6.1 Sol、Ultrafast、雲端 Agent、MCP Events 與 Private Intelligence 分別改變成本、等待、工作接續及資料邊界；效益須以相同品質下的成功交付衡量。
---

DevDay 2026 把 AI 應用的設計範圍向外推了一層：模型價格與速度決定能做多少推理，持續存在的執行環境決定工作能否接續，事件介面決定何時開始，授權與資料保護則決定可以接進哪些流程。這些能力一起改善，開發者才有機會把一次問答變成可追蹤、可恢復的工作。

這個方向有具體需求。分析文件、修正程式或整理客戶回饋，都需要多次讀取資料、使用工具、等待外部結果，再確認交付物。每一步都可能增加費用、耗時或失敗機會。單純提高模型分數，無法回答斷線後要不要重跑、資料更新後是否仍有效，以及一次成功需要多少人工驗收。

OpenAI 在 9 月 29 日的 [DevDay 公告](https://openai.com/index/devday-2026-recap/)同時推出或預告模型、agent 與開發介面。以下選出五個會改變工程決策的進展：GPT-6.1 Sol、Ultrafast、dots 與雲端執行、MCP Events，以及 Private Intelligence。本文的系統比較與算例是分析推導，並非 OpenAI 公開的內部實作。

先沿圖中的工作迴路看：模型提案之後，工具可能執行、等待或失敗，結果還要被記錄與驗收，才能決定是否接續。模型成本、持續狀態、事件與授權各自處理這條路徑的不同限制；這也是比較 DevDay 各項能力時的系統背景。

![Agent 工作跨越模型提案、工具執行與等待、結果紀錄和驗收；成本、狀態與授權分別限制工作路徑](/images/ai-industry/2026-09-30/agent-work-background.svg)

圖：作者提出的一般 Agent 工作流程，非 OpenAI 官方內部架構；各項公開能力以 [DevDay 2026 Recap](https://openai.com/index/devday-2026-recap/)為準。

## 五項進展分別鬆動哪個限制

| 技術進展 | 對應的限制 | 首先該驗證的問題 |
| --- | --- | --- |
| GPT-6.1 Sol | 同一預算能負擔多少模型呼叫 | 相同任務品質下，每件成功交付成本是否下降？ |
| Ultrafast | 多輪互動中模型生成造成的等待 | 模型生成占整體時間多少？ |
| dots／Agents API 雲端執行 | 工作跨時段、跨工具時的狀態接續 | 斷線與等待之後，能否確認同一工作的結果？ |
| MCP Events | 外部資料更新與 agent 啟動之間的落差 | 漏送、重送與權限撤銷如何處理？ |
| Private Intelligence | 機敏資料與安全審查的處理邊界 | 哪些資料會留在哪裡，由什麼元件解密？ |

表一：作者整理的限制對照。各項能力與推出狀態以後文的一手來源為準。

這張表也說明，採用順序不必與發布順序相同。若目前每天只做少量單次問答，模型升級可能已足夠；若工作經常卡在外部工具或人工確認，增加生成速度的效益就有限。先量到瓶頸，才知道新能力是否值得接入。

## GPT-6.1 Sol 讓多輪工作有更大的成本空間

[GPT-6.1 Sol 官方資料](https://openai.com/index/introducing-gpt-6-1-sol/)列出標準 API 價格：每百萬 input tokens 為 2 美元、cached input 為 0.10 美元、output 為 10 美元。OpenAI 報告其 DeepSWE v1.1 結果可匹敵 Astra；這是指定評估環境下的廠商結果，不能直接推成所有團隊的程式任務都能等價替換。

工程上的價值，應放進一個完整工作的帳。假設一次分析有十輪呼叫，每輪讀入二萬 tokens、輸出二千 tokens；其中一萬八千 input tokens 是可重用前綴，另二千是新資料。使用上述價格，可得到以下透明算例。

| 相同十輪工作 | Input 費用 | Output 費用 | 模型費用合計 |
| --- | ---: | ---: | ---: |
| 每輪全部按一般 input 計價 | 200,000 × 2 / 1,000,000＝0.40 美元 | 20,000 × 10 / 1,000,000＝0.20 美元 | 0.60 美元 |
| 首輪一般計價，後九輪前綴均命中快取 | 38,000 × 2 / 1,000,000＋162,000 × 0.10 / 1,000,000＝0.0922 美元 | 0.20 美元 | 0.2922 美元 |

表二：作者假設算例，價格依上述官方資料。第二列假設前綴符合快取條件、後九輪全數命中；未計工具、雲端環境、重試與人工成本，並非實測。

在這個工作形狀下，快取使模型費用減少約 51.3%，但 output 費用沒有下降。若改成每輪生成很長的報告，output 比重就會提高；若前綴反覆變動，快取收益也會減少。系統因此需要區分穩定指令、共用資料與每輪新證據，並透過實際帳單確認哪些 tokens 真的命中快取，不能只靠估計的重複文字量。

公開資料也沒有完整揭露 GPT-6.1 Sol 的模型結構與訓練細節；不能從價格較低就認定它使用特定蒸餾、稀疏化或推論演算法。此時可以驗證的是任務上的行為與成本，底層原因仍需等技術證據。

另一個值得挑戰的假設，是便宜模型必然降低總成本。假設模型呼叫每件省下 0.3 美元，卻讓工程師多花五分鐘修正，端到端成本可能反而提高。合理比較單位應是「通過相同驗收的交付物」，並同時記錄成功率、重試、人工修訂與完成時間。模型費用只是其中一項。

採用上有兩個合理選項：全部工作固定使用同一模型，流程簡單、容易建立基準；或依任務與驗收失敗升級模型，讓較低成本模型處理可清楚核對的工作。後者可能省錢，也增加路由、版本與重試管理的複雜度。沒有可判定的驗收條件時，路由器很容易只把失敗藏到下一層。

## Ultrafast 的收益要沿著關鍵路徑計算

DevDay 的速度宣稱區分 Codex 與 API 場景；具體接入方式則見 [Ultrafast 文件](https://developers.openai.com/api/docs/guides/ultrafast-mode)：使用較高成本的服務層級，並建議多輪 agent 採用 WebSocket，以減少重複連線的網路負擔。這份文件與活動摘要的速度表述不同，因此不能把最高倍數當成每種工作都適用的量測。

從應用看，時間至少由模型生成、工具執行、通訊與排隊構成。假設原本一件工作花 100 秒，其中 40 秒可以由模型服務加速，60 秒是串行工具與其他等待。即使把那 40 秒理想地加速六倍，總時間仍是 60＋40／6＝66.7 秒，端到端加速約 1.5 倍。若可加速部分占 80%，同樣算例才會到 3 倍。這裡的六倍是演算假設，不是對實際服務的效能承諾。

工具很多的 agent 尤其需要量測這個比例。模型快速選出下一步之後，若還要等待五秒搜尋、三十秒測試或十分鐘人工批准，生成率很快就不再主導交付。相反地，連續編輯、短工具回合與即時互動，可能更容易受益。相同技術在不同 execution path 上，經濟價值不同。

因此，速度實驗應保留同一模型、工作、工具及驗收條件，分段量測延遲。比較 standard 與 Ultrafast 時，除了完成時間，也要觀察費用與排隊分布；只記平均 tokens/s，會漏掉使用者真正遇到的長尾等待。若更快服務讓單位時間啟動更多工具工作，下游容量不足時還可能增加排隊，抵銷部分收益。這是需要驗證的系統推論。

## 雲端 agent 把「接續工作」變成明確的產品能力

[dots 的發布說明](https://openai.com/index/introducing-dots/)描述由 GPT-6 Astra 驅動、使用自身雲端電腦的持續型 agent，並開始在符合資格的方案與市場推出；specialist dots 則處於企業試點。這些狀態必須分開，不能把組織試點的權限與整合方式當成所有使用者已取得的能力。

另外，[dots 的安全說明](https://openai.com/index/how-we-build-safety-security-and-privacy-into-dots/)將 proactive research 限制於唯讀工具，後續行動仍需遵守授權與檢查。持續運作因此包含兩種不同權限：發現線索，以及對外部系統採取動作。

這個分工值得保留到自建平台。研究工作可以在已有權限的資料中尋找變化，卻不應因為找到一個看似合理的下一步，就自行擴大寫入範圍。以 bug 修復為例，讀取回饋與建立待審查修改可以有不同授權；即使使用者允許修正，也要確認授權是否包含合併與部署。工作接續多久，不會自動改變它的權限。這是參考設計取捨，並非新的通用產品保證。

這類產品解決的是時間尺度問題。聊天回合通常在使用者等待時完成；一項持續責任可能跨越晚上、新資料抵達與別人的回覆。工作因此需要保存目標、輸入版本、目前步驟與已完成結果。模型 context 內的敘述有助於推理，但外部系統是否真的被修改，仍須由工具或資料來源確認。

面向開發者，[Agents API 的 computer-use 文件](https://developers.openai.com/api/docs/guides/agents-api/tools/computer-use)已把 hosted browser、session ID、事件追蹤與存取確認放進同一流程；斷線後先恢復相同 session，再決定是否重試。接入成本可能下降，但應用仍要確認工作結果，不能把網路恢復等同於業務完成。

具體來看，假設一個 agent 收到 bug report，要重現、修改程式、執行測試，再建立待審查 PR。這是本文的參考案例：先固定 issue 與 repository revision，保存這次工作的識別；修正及測試都對應同一版本，PR 再連回測試證據。收到建立 PR 的回應之後，還需核對遠端 PR 是否包含預期修改。

最麻煩的故障發生在「外部成功、自己沒收到」。PR 已建立，連線卻在回應途中斷掉。此時重新發出整個任務，可能建立第二個 PR；直接宣告失敗，又會遺漏已完成的成果。

| 應用可見狀態 | 外部可能留下什麼 | 恢復時的第一步 |
| --- | --- | --- |
| 測試尚未完成 | 暫存修改、正在執行的工作 | 查同一工作狀態，確認結果屬於哪個版本 |
| 建立 PR 請求逾時 | PR 可能已存在，也可能尚未建立 | 依工作識別與來源分支核對遠端物件 |
| 等待批准 | 提案已保存，外部資料可能已更新 | 檢查批准對象與目前版本是否仍相容 |
| 權限已撤銷 | 舊結果仍可能存在 | 停止後續存取，保留可稽核狀態 |

表三：作者設計的恢復檢查，非 dots 或 Agents API 已保證的完整交易語意。

這個案例指出雲端環境與業務可靠性的邊界。平台可以幫忙維持 session；應用的 job record 則要連結外部物件、版本與驗收。API 適合明確的讀寫和結果核對，UI 操作可涵蓋沒有合適 API 的系統，卻更容易受到畫面、登入與互動狀態變化影響。兩者可以並用，但應把外部完成證據留在可查詢的位置。

## MCP Events 縮短「資料已變，agent 還不知道」的等待

[OpenAI 的 MCP Events 接入文件](https://developers.openai.com/plugins/build/mcp-events)描述事件訂閱、webhook delivery 與 callback verification；該整合採用 draft 規格，也列出未支援的控制通知。這提供可實作介面，但仍應與 [MCP 工作小組的標準化範圍](https://modelcontextprotocol.io/community/working-groups/triggers-events)區分，不能推成所有 client 已互通。

事件介面的作用，是讓外部系統主動告知有變化。原本每隔五分鐘輪詢一次，若變化均勻分布於輪詢間隔，理想的平均發現等待約為兩分半，還沒算查詢與執行。事件通知可移除這段固定等待；代價則是要處理訂閱存續、認證與交付故障。這是時間模型推導，不是官方延遲量測。

對前述 bug 修復案例，事件只需要告知某個 issue 更新，不應把事件文字直接當成最新權威需求。agent 啟動後重新讀取 issue，確認仍有權限、目前版本與處理範圍，再決定要做什麼。通知是工作線索，來源系統才持有當前狀態。這能避免延遲抵達的舊通知讓 agent 修正已撤回的要求。

重送與回饋循環也必須一起看。若建立 PR 本身又觸發新事件，沒有範圍與工作身分檢查，agent 可能不斷回應自己的輸出。參考設計可以用來源事件識別去重，再以目標 issue、revision 與動作類型確認同一工作是否已完成；但「忽略重複通知」不能掩蓋上次執行未完成的情況。通知已收下與交付物已產生，必須是不同狀態。

當來源事件頻率很高，逐件呼叫模型還可能放大費用。同一 issue 在一分鐘內修改五次，可以先合併通知，再讀最新狀態；涉及每筆都必須處理的交易，則不能任意合併。這個取捨由業務不變量決定，無法單靠模型判斷哪些歷史可丟棄。

## Private Intelligence 改變資料保護的驗證位置

[Private Safety Processing 文件](https://developers.openai.com/api/docs/guides/private-safety-processing)描述：受保護安全紀錄放在客戶控制的儲存，經硬體驗證的安全 runtime 解密審查，明文輸出受到限制。DevDay 另提到 Private Inference 的後續 preview；兩者處理的範圍不同，不能合併成所有推論已採相同保護的宣稱。

企業評估這類能力，需要拆開三件事：資料是否用於訓練、內容留存在哪裡、執行期間哪些元件可以接觸明文。任何一項改善，都不會自動回答另外兩項。保存加密紀錄也需要理解金鑰、有效期限、授權與故障處理；保護內容的機制，不能只從一個產品名稱判定。

對架構的影響，是把部分信任放到可驗證的執行與解密邊界。參考驗收可以核對應用的每個輸出：模型內容、工具輸入、追蹤紀錄、錯誤訊息與外部附件各自流向哪裡。即使推論或安全審查受到保護，若應用把完整文件寫到一般 debug log，資料仍會從另一條路徑離開。

因此，這項進展最適合從少量、可追蹤的資料流程驗證。先固定資料類型、儲存政策與實際使用的 endpoint，再檢查故障時是否產生額外紀錄。它可能擴大可採用前沿模型的情境，但不足以直接推導某個企業的所有資料都能送入相同服務。

## 下一個實驗應量到成功交付，而非只換模型

最值得先做的實驗，是選一組已知結果的文件分析或 bug 修復工作，固定資料、工具與驗收，建立舊方案基準，再逐項加入新能力。記錄每件成功交付的總費用、完成時間、人工修改與失敗恢復。額外刻意在外部操作完成後切斷連線，檢查是否會重複建立物件；這能測出一般正常流程看不到的可靠性差異。

這也接續本站對 [CAD agent 證據身分](/eda/2026/09/26/orassistant-evidence-and-metric-contract.html)的討論：系統需要保留結果成立的條件。DevDay 擴大了可組合的能力，下一個可驗證問題是：**在相同品質門檻下，這些組合能讓多少工作減少等待與人工接手，且故障後仍能核對一次完整交付？**

## 來源

- [OpenAI：DevDay 2026 Recap，2026-09-29](https://openai.com/index/devday-2026-recap/)
- [OpenAI：Introducing GPT-6.1 Sol，2026-09-29](https://openai.com/index/introducing-gpt-6-1-sol/)
- [OpenAI API：Ultrafast mode](https://developers.openai.com/api/docs/guides/ultrafast-mode)
- [OpenAI：Introducing dots，2026-09-29](https://openai.com/index/introducing-dots/)
- [OpenAI：How we build safety, security, and privacy into dots，2026-09-29](https://openai.com/index/how-we-build-safety-security-and-privacy-into-dots/)
- [OpenAI API：Agents API computer use](https://developers.openai.com/api/docs/guides/agents-api/tools/computer-use)
- [OpenAI Developers：MCP Events](https://developers.openai.com/plugins/build/mcp-events)
- [Model Context Protocol：Triggers and Events Charter](https://modelcontextprotocol.io/community/working-groups/triggers-events)
- [OpenAI API：ZDR with Private Safety Processing](https://developers.openai.com/api/docs/guides/private-safety-processing)

