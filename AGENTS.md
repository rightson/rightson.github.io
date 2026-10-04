# Rightson GitHub Pages — Agent Operating Guide

本文件是 `rightson/rightson.github.io` 的 **唯一 agent source of truth**。
所有會新增、修改、發布文章，或調整網站內容的 agent，在開始工作前都必須先讀完本文件，再讀取當下任務直接相關的 roadmap／series 規格與最新文章。

- 使用者當次明確指示優先於本文件。
- 專題／排程 prompt 可以增加更嚴格的內容要求，但不得默默降低本文件的安全、來源、permalink、併發寫入與發布驗收規則。
- 不得以舊對話、舊 commit、記憶中的網站狀態取代目前 default branch 的真實內容。
- `CLAUDE.md` 應為指向本文件的 symlink；不要維護第二份 Claude 專用規則。

---

## 0. 每次開寫前的固定流程

任何文章在開始研究或動筆前，依序完成：

1. 讀取 repo metadata，確認 default branch。
2. 讀取最新 default branch 的：
   - `AGENTS.md`
   - `_config.yml`
   - `.github/ARTICLE_TAXONOMY.md` 與 `_data/research_series.yml`
   - 與任務相關的 roadmap / series spec（若存在）
   - 研究排程先讀 `.github/schedules/README.md`、`manifest.json`、`common.md` 與對應 group 任務檔，再讀 `.github/RESEARCH_SCHEDULES.md` 及 `.github/RESEARCH_AUTOMATIONS.json` 的相關系列補充規格。每次先記錄最新 default-branch instruction commit SHA，從該版本完整讀取指令；寫入前仍另核對最新 head。repo 時程是對照紀錄，不會自行重排或啟用 scheduler。
   - 最近至少數篇同 domain／同系列文章，檢查重複與既有語氣。
3. 若任務會影響 layout、search、分類、RSS、about、CSS 或其他網站功能，再讀對應的 `_layouts/`、`_includes/`、`_data/`、`assets/` 與 `SITE_GUIDE.md`。
4. 確認同日／同系列／同 slug 是否已有文章；不得重複建立。
5. 先形成「認知增量」：新證據、新機制、新實驗、新架構比較，或明確修正舊判斷。選材看研究價值、工程影響與可長期保留的理解，不按新舊或熱門程度排序。經典教材的增量也可以是補齊必要先備、推導或可驗證的直覺；不因當天沒有新聞而跳過課程。沒有足夠價值時不為排程硬湊文章，回報原因，但不得自行停用、暫停或刪除 recurring task。
6. 才開始研究、畫圖與寫作。
7. 發布前執行 `python3 scripts/lint_posts.py <新文章路徑>`（規則見第 11 節）；未通過不得提交。

若取得規則、原文或現況失敗，先說明缺口，不可依猜測覆寫檔案。

---

## 1. 網站架構與不可破壞的既有能力

本站使用原生 Jekyll + GitHub Pages：

- 無 remote theme。
- 無 JavaScript framework。
- 無外部字型依賴。
- 搜尋為本站自有 client-side index，不把文章內容送往外部搜尋服務。
- `_posts/` 有變更時，`.github/workflows/post-lint.yml` 會執行 `scripts/lint_posts.py --block`：未通過的新文章被移到 `_blocked/`（附 `.lint.txt` 違規說明），由 bot commit 回 main 並重新觸發 Pages 建置，該次 workflow 標成失敗。被擋下的文章在 bot commit 前的一兩分鐘內可能短暫可見，因此仍須在提交前自行跑 lint。

現有功能應保留：

- 首頁依時間由新到舊顯示文章。
- 九個固定研究 domain（見第 2 節）。
- `/categories/` 靜態分類頁。
- `/search/` 全文搜尋、AND keyword matching、domain/category filters 與 shareable query URL。
- `/search.json` 由 published posts 自動產生。
- 文章 H2/H3 目錄。
- 中英混合閱讀時間估算。
- previous / next navigation。
- responsive table / code。
- browser-native text scaling、keyboard focus、skip navigation、reduced motion。
- RSS：`/feed.xml`。
- About 頁與既有聯絡連結。
- 既有手機分享功能及其他已上線共用 UI。

一般發文任務不得順便更換 theme、style、deployment flow、search implementation 或共用 layout。

---

## 2. 九個公開分類與 URL 穩定性

分類按「文章主要回答什麼問題」判斷；五個排程器是執行入口，十四個主題保留為系列。完整分類邊界與系列預設見 [.github/ARTICLE_TAXONOMY.md](.github/ARTICLE_TAXONOMY.md) 和 `_data/research_series.yml`。

| domain | 公開分類 | 主要問題 |
| --- | --- | --- |
| `ic-design-platform` | IC 設計平台 | 晶片設計流程、EDA、工程協作、資料交接與治理。 |
| `ai-frontier` | AI 技術與工程 | 模型原理、訓練／推論、通用 Agent、工具與實作。 |
| `architecture` | 運算架構 | 加速器、微架構、資料流、記憶體與軟硬體協同。 |
| `networking` | 網路系統 | 協定、封包路徑、互連、壅塞控制與網路效能。 |
| `distributed-systems` | 分散式系統 | 分散式服務、資料模型、一致性、複寫、容錯與恢復。 |
| `platform-engineering` | 系統與平台 | Linux、容器、K8s／HPC、叢集資源、平台效能與維運。 |
| `ai-industry` | 產業與供應鏈 | 公司競爭力、產品、市場供需、客戶關係與價值分配。 |
| `investing` | 投資與交易 | 盈利預期、估值、機構資金、價量與進退場條件。 |
| `science-physics` | 科學與物理 | 自然現象、材料物性、物理機制、實驗與理論研究。 |

- 每篇只有一個 primary `domain`；`series`、公司與技術名稱為次級資料，不增加主選單。系列預設不能取代文章主問題判斷。
- 新文章單一 `categories` 與 `domain` 一致；既有文章重新分類只改 `domain`，保留 filename、date、categories、permalink、既有 series／篇號與正文。`domain` 不改變文章 URL。
- EDA 演算法、STA／SDC、placement、routing、verification、signoff 與設計流程／平台統一歸 `ic-design-platform`。`eda`／`timing` 是舊分類相容值，不能新增為公開選單。
- 模型、訓練／推論與通用 Agent 歸 `ai-frontier`；主問題為 RTL、驗證、synthesis／APR、signoff 的導入、流程與驗收責任，歸 `ic-design-platform`。
- LLM Lab 模型與實作預設 `ai-frontier`；獨立加速器微架構、記憶體或資料流歸 `architecture`。系列 identifier 不變。
- 企業如何成長、競爭及獲利歸 `ai-industry`；股價已反映多少、合理估值、機構資金或進退場條件歸 `investing`。出現 EPS、營收、毛利或現金流數字，不足以歸為投資文。
- 半導體生態系深研預設 `ai-industry`；主問題為合理股價、估值情境或布局條件時歸 `investing`。
- TPU 微架構歸 `architecture`；協定、封包路徑與互連歸 `networking`；服務一致性、複寫與完整服務設計歸 `distributed-systems`；Linux、容器、K8s／HPC、叢集資源與平台維運歸 `platform-engineering`，不因應用於 EDA／AI 而改分類。
- 「AI 前沿每日摘要」使用 `series: ai-frontier-digest`；依本節主問題規則分類，不以系列預設凌駕實際文章內容。
- K8s 課程從零學習，沿用 OS 與資工先備；`series: k8s-hpc`，預設 domain／categories 為 `platform-engineering`。roadmap 指向 rightson/k8s-lab 的 learning-plan、lesson-standard、learning-progress；輔助教材、練習、解答、程式與 raw 實驗證據放該 repo，網站只保存完整文章與文章圖。舊 K001–K081 不沿用，新穩定 ID 為 K082–K129；封存歷史保留，恢復須另行授權。
- 2026-10-01 核准前八類；2026-10-03 核准新增第九類「科學與物理」。未來新增、合併、拆分、更名、重排公開分類或重新分類既有文章，仍須使用者確認；新文章依已核准規則選分類，不必逐篇詢問。
- 同步 `_data/domains.yml`、`_includes/domain-key.html`、本表、roadmap 與五個新排程。顯示順序以 `_data/domains.yml` 為準。

---

## 3. 檔名、front matter、發布時間

文章位置：

`_posts/YYYY-MM-DD-<english-kebab-slug>.md`

基本 front matter：

```yaml
---
layout: post
title: "具體、有資訊量、像工程師會寫的標題"
date: YYYY-MM-DD HH:MM:SS +0800
domain: ic-design-platform
categories: ic-design-platform
description: "一至兩句概括文章真正的核心判斷。"
takeaways:
  - who: "Synopsys"
    value: "一句完整的因果句：得到或失去什麼、經由什麼機制、代價或條件是什麼，40–160 字"
  - who: "OpenAI"
    value: "…"
  - who: "中型設計公司"
    value: "…"
---
```

`takeaways` 顯示在標題下方的「重點」框，寫法依第 4.2 節：

- 3–6 條，總長 250–700 字，讀者約 90 秒讀完。
- `who` 是具體的公司、產品、機構或角色名稱（例如「Synopsys」「中型設計公司」「台積電」「推論服務營運者」）。不用分析類別當標籤，例如使用者、用戶、客戶、競爭者、競爭對手、合作方、長期、投資人、受益者。
- `value` 以該對象為主詞，寫成一句完整的因果句，不寫標題式短語。
- 合起來要涵蓋：誰得到什麼、經由什麼機制、誰付出什麼、長期改變什麼、什麼情況會翻盤。
- 2026-10-04 12:00 前建立、使用 `summary`、`lede` 或舊式 `takeaways` 的文章維持原樣，版面仍會顯示。

### 時間規則

- `date` 採 Asia/Taipei。
- 新文章的 `date` 是 Markdown **首次實際產生並寫入**的時間，保留 HH:MM:SS +0800。
- 不用排程預定時間、GitHub commit time、Pages deploy time 或 filesystem mtime 冒充文章建立時間。
- 後續修訂保留原始 `date`；不要因重新生成或部署改寫。
- 既有文章缺乏可靠時分時，不推測、不批次補造。
- 文章頁由共用資訊列顯示到「時:分」，正文不要再手寫發布時間。

### 署名規則

- 所有公開文章在標題下方、日期旁以小字顯示固定署名：**Scott Yo-Ru Chen · AI-assisted**。
- 作者姓名與 AI 協助標示集中於 `_config.yml` 的 `author`、`ai_assistance`，由 `_includes/post-byline.html` 統一呈現，適用於所有既有與未來文章。
- front matter 不需自行加入 `author`；不要在正文開頭或結尾重複署名，也不要逐篇加入 AI 協作聲明。
- 「AI-assisted」表達 AI 協助研究與撰寫，不把 AI 列為共同作者，也不自動聲稱作者已逐篇人工審訂。
- 正文、圖說與表格不標註作者立場：不寫「作者整理／作者推論／作者設計／作者分析」，也不標示是否經人工審閱。證據性質改用中性標示：依來源整理寫「依據 XXX 整理」，推論寫「推論」，自行提出的架構寫「參考設計」，試算寫「假設算例」。

---

## 4. 通用寫作指引

本節是全站每篇文章共同的寫作原則。系列規格可以更嚴格或補充細節，但不得違反本節。第 5–9 節是本節在篇幅、IC 平台、來源、圖表與連結上的細則。

### 4.1 寫作前先想清楚（只影響內容深度，不寫成文章結構）

1. 先決定這篇要回答的核心問題（各分類的核心問題見第 5 節表格），結論要回答它，不能只回答「要注意哪些風險」。
2. 找出真正決定結果的機制，至少兩個，並用一個完整案例或端到端路徑串起來。
3. 直接得到好處的有誰：依好處大小排序並說明理由；好處的實質內容是什麼（成本、時間、營收、市占、議價力、資料、通路），能量化就量化。
4. 誰付錢、誰承擔成本；得利的和付錢的若不是同一方，要說破。
5. 長期的額外代價：綁定、依賴、資料流向、可重現性、成本型態改變、技能退化，各由誰承擔。
6. 長期會發生什麼轉變：控制點往哪裡移，誰的談判位置變強或變弱。
7. 什麼會被淘汰或壓縮：中間層、產品類別、工作內容、商業模式。
8. 鑑往知來：至少一個有日期、有來源的前例，講清楚相同與不同之處，以及據此能推出什麼走向。
9. 至少一個附時間範圍的預判，以及會證實或推翻它的具體訊號。
10. 想出與主要判斷相反、最有說服力的走向，它成立需要什麼條件，以及目前為何仍維持原判斷或需要修正。
11. 至少比較兩種合理方案或解讀的取捨，不預設「多一層、多一個 agent」一定比較好。
12. 只有核心問題涉及系統執行、故障或維運時，才寫出錯情境：哪裡失效、留下什麼狀態、怎麼發現、怎麼處理。

第 3–10 條適用於事件、產品、公司、論文與市場分析。教材型系列（`tpu-technical`、`distributed-systems`、`k8s-hpc`、`llm-lab`）與 `science-physics` 只做與題目相關的部分；教材文章討論具體產品或產業事件時，仍應完整回答。

### 4.2 開頭：讓讀者 90 秒內掌握

13. 標題直接寫結論或具體問題，不用冒號。不用例行模板（今日結構變化、XX 技術雷達、重算版），不用日期當標題核心（除非日期本身就是事件），不堆砌 SEO 同義詞。
14. 標題下方先放重點整理（front matter `takeaways`，格式見第 3 節），讀完要能向別人轉述：哪些具體的公司或角色得到什麼、經由什麼機制、誰付出什麼、長期改變什麼、什麼情況會翻盤。
15. 重點用具體名稱當主詞，每條是一句完整的因果句，不寫標題式短語，也不用分析類別當標籤。
16. 正文開頭交代理解所需的背景：這件事在更大的系統裡負責什麼、原本的做法為什麼合理、是什麼讓問題浮現。背景以支撐核心問題為準，不寫無關歷史，也不預設讀者已懂尚未教過的先備。

### 4.3 論證與語氣

17. 結論先行，正文用判斷句推進（分散式系統系列依下方需求先行順序）。
18. 保留條件、資料缺口、適用範圍集中放在文末 `## 證據範圍`，正文不逐句加「不能、不代表、不等於」劃界。
19. 每章推進一步推理，同一個結論不換句話重複；收尾留下能改變判斷的理解，以及下一個可驗證的問題。
20. 抽象概念要落到讀者熟悉的具體物件，例如 IC 設計平台要講到 RTL、SDC、netlist、checkpoint、license、報告數值。入門文章先補直覺與最小模型，進階文章保留必要深度；不用術語密度代替解釋。
21. 數字要附 baseline、單位、條件與假設。
22. 不讓每個主題都收斂成同一組詞，例如驗收、邊界、證據、恢復；只有核心問題本身是治理或故障處理時，這些詞才是結論。
23. 不用模板句型，例如「不是 A 而是 B」「X 的價值取決於 Y」「值得注意的是」「真正的 X」（完整清單見下方「禁止重複句型」）。
24. 不靠假口語、驚嘆號、刻意反問或虛構的親身經驗來營造人味。

### 4.4 證據與來源（細則見第 7 節）

25. 可驗證的主張要在段落附近放一手來源連結，文末再完整列出。
26. 連結要讓讀者能直接定位到被引用的數字或段落，不連整包資料端點或社群轉述。
27. 核對原始發表日、事件日與版本，不把抓取日當發布日。
28. 原型、預覽、正式上線、量產部署分開寫；只有公開證據支持的，才寫成公司現有能力。
29. 廠商宣稱要寫清 benchmark 條件和缺少的資訊。
30. 區分來源事實、廠商自報結果、推論、假設算例與參考設計，用中性詞標示，不標註作者立場，也不標示是否經人工審閱。

### 4.5 不留痕跡

31. 思考框架只體現在內容裡：章節標題寫具體主張或情境，不用分析類別當標題，不用粗體標籤開段，不出現框架詞彙，例如最大受益者、受益者、第一階、第二階、反方論點、影響與槓桿、槓桿（營運槓桿、財務槓桿等財務名詞除外）、鑑往知來、利害關係人、takeaway、預測與訊號、本文的判斷。
32. 不用「對使用者／對競爭者／對合作方」逐一列舉，直接寫公司或角色的名字和遭遇。
33. 分析的順序和篇幅依題目調整，連續幾篇的段落結構要輪換，不讓讀者看出固定模板。第 4.1 節各項不必各自成段，可以合併在兩三個章節裡，但每一項都要在正文找得到實質內容。
34. 不寫幕後過程：素材怎麼取得、翻譯或轉述鏈、搜尋時間窗（例如「近 72 小時」，改寫成具體日期）、排程或重算流程、coverage audit、寫作方法與提示詞（例如第一性原理、寫作框架、prompt）。
35. 私人研究框架的術語和符號（例如 regime reversal、good-news failure、estimate peak、Capital ↑），一律改寫成讀者看得懂的具體數據變化。

### 4.6 圖表（細則見第 8 節）

36. 圖要回答問題：資料怎麼走、誰握有狀態、哪裡會卡、哪裡會出錯。不用裝飾圖湊數。
37. 開頭附一張背景或端到端總覽圖，放在背景之後、細節之前；每張圖附 alt、圖說和來源，自己提出的架構標成參考設計。
38. 圖裡的文字也要遵守第 4.5 節的不留痕跡原則。
39. 手機寬度下仍能看懂，並支援深色模式。

### 4.7 語言

40. 使用台灣慣用的繁體中文，完全避免中國大陸用語；依語境使用通訊、效能、資料、運作、程式、軟體、硬體、記憶體、佇列、頻寬、最佳化、部署等用法。英文術語比生硬翻譯精準時，直接保留英文。

### 分散式系統系列的敘事順序

適用於 `series: distributed-systems` 的完整案例，優先於本節一般的「結論先行」語氣；實質完成標準與篇目以 `.github/DISTRIBUTED_SYSTEMS_SERIES_ROADMAP.md` 為準。

- 開頭先描述具體使用者或業務情境：誰使用服務、目前遇到什麼問題、希望改善什麼。先讓待設計問題成立，再提出架構；不得尚未交代需求就宣布最終選型或深層機制。
- 逐步釐清會改變設計的需求，給出案例中的明示假設與答案：功能與非目標、唯一範圍、讀寫模式、規模、SLO、一致性、耐久性及不變量。問題要有實質答案，不用連串反問代替需求定義。
- 先做出可走完正常請求的最小設計，交代 API、資料模型、狀態擁有者與成功回應的意義。不能用元件清單代替端到端路徑，也不先假設分片或全球多活。
- 再以帶單位的容量推導、偏斜流量、競態、故障或需求變動，證明最小設計在哪裡不足，才引入下一個機制。每次演進都說清觸發問題、合理替代方案、選擇原因及代價；需求尚未支撐前，不直接指定 token bucket、quorum、lease、fencing 或特定產品。
- 深掘自然接在相應瓶頸之後，說明資料結構、演算法、原子性、複寫確認與失效邊界。正文須連成可重建的決策鏈，不是換過開頭的機制清單。
- 故障要追蹤失效點、殘留狀態、使用者可見結果、偵測與恢復，再交代安全隔離、觀測及上線／遷移取捨。需求變體須完成推導，不能只留下問題。
- 收尾回到起始需求，核對已成立的承諾及未解限制，再銜接已發布先備或下一個自然問題。
- 章節使用具體釐清問題或設計結論，依案例安排，不套固定目錄、不寫角色扮演或虛構對話。公開正文只呈現服務需求、技術來源與工程判斷。
- `series: distributed-systems` 的新文章使用 `domain: distributed-systems` 與 `categories: distributed-systems`。既有文章若因舊 `categories` 形成公開網址，只修正 `domain` 以歸入分散式系統，保留原 permalink。
- 改寫既有文章時保留檔名、date、categories、permalink 及原有 domain；除非使用者另行授權分類調整。保留技術深度、量化推導與來源，不能以縮成提綱代替改寫。

### 禁止重複句型（標題、description、開頭段）

以下句型已在站上過度使用，**標題與 `description` 一律不得使用**，開頭第一段也避免：

- 「X 真正的（突破／核心／關鍵／難點／效率）不是 A，而是 B」
- 「X 的核心／本質不是 A，而是 B」、「不是 A，而是 B」、「而不只是 A」
- 「X 才是真正的拐點／分水嶺」、「X 的分水嶺：…」
- 開頭段的「我認為 X 最值得注意的地方，不是…也不是…真正的…」、「今天（真正）最值得注意的，不是…而是…」、「我現在比較在意的，不是…而是…」
- 「X 的價值／可靠性／可信度取決於（在於、來自、前提是）Y」、「X 值得研究，是因為…」、「最值得注意／警戒的是…」

改用直接陳述結論或具體問題，例如：
- ✗「NVLink 6 真正的突破不是 3.6 TB/s，而是把故障恢復做成跨層控制迴路」
- ✓「NVLink 6 從 PHY retry 到 NCCL 彈性恢復，把故障處理做成跨層控制迴路」

發布前必做：
1. 列出最近 20 篇文章的標題與 `description`，確認新標題的句法骨架（去掉專有名詞後的結構）沒有與任何一篇相同。
2. 同一句法骨架在最近 20 篇中最多出現一次；系列標記（如「創始篇」「Day N」）不算骨架，但不可取代具體結論。
3. 若標題仍需對比，只陳述被修正的具體誤解與證據，不用「不是…而是…」模板。

---

## 5. 深度文章的預設品質門檻

當任務是技術 deep dive、EDA / networking / distributed systems / TPU 類長文，若專題規格沒有另訂更嚴格門檻，預設以 **至少約 10 分鐘實質閱讀深度** 為目標。

建議正文約 4,000–6,000 中文字；深題可更長。圖說、References、front matter、大段程式碼不算拿來湊篇幅。

### 結論要回答所屬分類的核心問題

每篇的結論必須回答 primary domain 的核心問題。框架是工具，不是結論：不得把每個主題都收斂成「驗收、證據、邊界、恢復、契約」。只有文章的核心問題本身就是治理、驗收或故障處理時，這些詞才是結論。

| domain | 結論要回答 | 典型的好結論 |
| --- | --- | --- |
| `ic-design-platform` | 哪種流程或平台設計，在什麼條件下改善時程、品質、tool-hours 或人力 | 「固定 IP 配置後，整合週期由數週縮到數天，代價是客製彈性」 |
| `ai-frontier` | 模型或 Agent 機制怎麼運作、能力到哪裡、該怎麼用 | 「新版把思考預算交給 API 參數，長任務成本可下降約三成」 |
| `architecture` | 計算、資料搬移與記憶體的瓶頸在哪，取捨如何量化 | 「INT8 讓 MAC 面積降到約六分之一，換來校準成本」 |
| `networking` | 延遲、頻寬、壅塞或可靠性由哪個機制決定，量級多少 | 「400G/lane 省下一半通道，DSP 功耗占比升到 X%」 |
| `distributed-systems` | 依第 4 節「分散式系統系列的敘事順序」，交代每次設計演進的觸發與代價 | 依系列 roadmap |
| `platform-engineering` | OS／容器／K8s 的執行機制與可重現實驗結果 | 依系列 roadmap |
| `ai-industry` | 誰拿到利潤、為什麼、能維持多久 | 「HBM 每片晶圓的利潤是一般 DRAM 的數倍，排擠效應會延續到 2027」 |
| `investing` | 價格隱含什麼預期，哪些數據出現就推翻判斷 | 「現價要求 EPS 再成長 34%；下一季毛利率低於 X% 即失效」 |
| `science-physics` | 自然現象由哪些物理機制決定，實驗與理論支持到哪裡 | 「應變梯度可誘發冰的電極化；介面與液體傳輸影響有效反應」 |

其餘要件見第 4.1–4.3 節。

若網站現有 reading-time algorithm 可取得，發布前依同一算法確認；未達門檻應補機制、案例與證據，不可硬寫 `reading_time: 10` 或修改演算法作弊。

短評、投資快訊等若有明確 task-specific 篇幅規格，以該任務為準；不要為套用長文規則而灌水。

---

## 6. EDA / IC Design Platform 文章的特殊要求

EDA 方法與 IC 設計平台均依第 2 節歸 `ic-design-platform`，共用以下工程證據與保密要求。

EDA 類文章不限 R2G，應把視野放到完整 IC design platform：

`spec / architecture → RTL → verification / formal / DFT → synthesis → STA / SDC → APR / ECO → signoff → package / chiplet / system`

可研究：

- AI-native CAD platform
- agentic workflow / orchestration
- compiler / IR
- typed design state
- design data management
- artifact lineage
- incremental / durable execution
- distributed execution
- checkpoint / recovery
- policy / sandbox / authority
- semantic tool interface
- evaluation / evidence
- trajectory mining
- expert knowledge capture
- multi-physics / chiplet / package co-optimization

### 產業平台文章

可從先進平台切入：
- EDA vendor：Synopsys、Cadence、Siemens EDA 等。
- IC 設計公司公開的 CAD / design infrastructure：NVIDIA、AMD、Broadcom、Qualcomm、Marvell 等。
- OpenROAD 等開源系統可作 mechanism reference 或 reproducible experiment。

但必須：
- 只把公開證據支持的內容稱為公司現有能力。
- 不從 job posting、零碎 conference 文字或 marketing statement 推導不存在的完整內部架構。
- 自己畫的「合理參考架構」清楚標成「參考設計」或「推論」，不畫成廠商官方架構。
- prototype / demo / preview / GA / production deployment 分開寫。
- 開源 flow 的結果不可直接外推到商用 advanced-node production。

### SYN/APR / STA/SDC 文章

盡量落到具體工程物件：
- RTL / netlist
- Tcl / Perl / Makefile
- SDC / UPF
- logs / reports / checkpoints
- synthesis / P&R / STA / formal / LEC / DRC
- license / queue / shared filesystem / scratch（若與主題有關）

陌生 platform abstraction 要先透過熟悉的 design flow 語意落地，不只列 control plane、state、agent、policy 等抽象名詞。

---

## 7. 來源與引用：任何可驗證主張都要能追溯

### 來源優先順序

優先：
1. 原始論文／conference paper。
2. 官方 technical document / specification。
3. 官方 repository / issue / PR / commit。
4. 官方 engineering blog / product technical material。
5. 高品質二手來源僅作補充或 discovery lead。

### 寫法

- 所有外部可驗證的技術事實、量化結果、產品能力、論文結論、架構主張，在相關段落附近放 **可點擊 Markdown link**。
- References 末尾再列完整來源；不能只堆裸 URL。
- 核對原始 publication date、revision date、event date，不把搜尋／抓取日當發布日。
- 舊資料可以用，但要自然標出原始年份／日期，不冒充今日消息。
- vendor claim 要寫清 benchmark 條件、缺失資訊與可能 marketing bias。
- 連結必須讓讀者能直接定位到被引用的數字或段落。不連整包 OpenAPI 或 JSON 端點（例如 `openapi.twse.com.tw`、`response=json`），改連 TWSE／TPEx／公開資訊觀測站可查詢的網頁並寫明查詢日期與欄位；不以 Facebook 等社群貼文作來源，找到原始出處再引用。

### 研究價值與證據範圍

- 學術選材重視前瞻性、重要問題、機制洞見與可信證據，不以 production grade 作為研究價值門檻。
- 清楚交代實驗條件、規模、baseline 與結論邊界即可；不要把「尚非 production grade」當成每篇學術文章的例行免責段落。
- Demonstration、模擬、benchmark 與實際部署仍須依證據正確命名。只有與當篇工程判斷有關時，才深入部署、可製造性或可靠性缺口；不得把外推寫成實測或部署事實。

### 多作者論文

正文通常只寫：
**第一作者 + 所屬機構**。

其餘作者可留在 References 或原文連結；機構不確定就不要猜。

### 事實與推論

清楚分開以下性質，但用中性標示，不標註作者立場：
- 來源事實
- 論文／vendor reported result
- 推論
- 假設算例
- 參考設計

推論要有力度，正文直接寫成判斷句；不能偽裝成來源已證實。保留條件集中寫在文末 `## 證據範圍`，不在每句後面加否定式劃界。

---

## 8. 圖表與視覺

技術 deep dive 原則上安排 2–4 個真正有資訊價值的 visual：

- architecture diagram
- sequence / control-flow
- data path
- state machine
- failure / recovery path
- topology
- performance / queueing comparison
- trade-off table

規則：

- 每篇 IC 設計平台長文至少有一張平台架構或端到端流程總覽圖，置於必要背景後、局部機制前，說清輸入、角色／工具、交付物與驗收責任。總覽圖不能以元件清單或裝飾圖代替；其餘圖放在對應機制附近。既有文章修訂亦適用。
- 優先原創 SVG 或 repo 已確認能直接顯示的格式。
- 不把未渲染 Mermaid 原始碼當成完成圖片。
- 圖要回答問題：資料怎麼走、誰擁有 state、哪裡排隊、哪裡驗證、哪裡會失敗、怎麼恢復。
- 不用 stock image 或裝飾性插圖湊圖數。
- 每張圖有 alt text、caption、來源。
- 依 primary source 重畫：標「依據 XXX 整理／重繪」並附 link。
- 自己提出的架構：標「參考設計」。
- 直接引用或改繪外部圖片前確認允許的引用／授權條件。
- 圖中文字與箭頭需在手機寬度仍可理解。
- 圖中文字遵守第 4.5 節：不出現框架詞彙、作者立場標註或幕後流程。
- 網站會跟隨系統深淺色。新增或修改 SVG 後執行 `python3 scripts/svg_dark_mode.py <svg 檔案>`，為圖加上深色配色（可重複執行）；並在深色模式下確認文字可讀。
- 圖檔與 Markdown 同 commit，避免文章先上線但圖片 404。

### 開頭的背景示意圖

- 所有技術文章與 lab 的開頭應搭配一張有助於理解背景與研究動機的示意圖。先用一至三個段落建立具體情境，再在進入局部機制前放圖；圖要讓讀者看見系統如何運作、原有設計為何合理，以及問題在哪個位置浮現。
- 依題目選擇情境、端到端流程、系統邊界、拓樸、時間軸或原有方案與需求變化的對照。分散式系統案例先畫使用者與服務需求，不在需求未成立前把最終架構畫成既定答案。
- 圖前後要有具體導讀，指出應沿哪條資料／控制路徑、觀察哪個相依或瓶頸，以及它如何銜接本文的核心問題。圖片不能代替必要的背景文字，也不以術語方塊清單、無關插圖或重複正文湊數。
- 既有文章亦適用：逐篇檢視開頭，已有合適圖時重用、移至合適位置並補導讀；缺少時補畫。保留技術深度、來源、date 與 permalink，不必為此整篇重寫。
- 概念圖、假設案例與參考設計須清楚標示；廠商或論文的實作只能依 primary source 呈現。示意圖的線寬、顏色與位置不冒充實測效能或比例。遵守本節 SVG、圖說、手機可讀性與深色模式規則。

建議圖片路徑：
`images/<domain>/YYYY-MM-DD/<descriptive-name>.svg`

---

## 9. 內部連結、SEO 與可讀性

- 每篇有具體 `description`，摘要核心結論，不寫「本文將介紹」。
- 每篇至少連一篇相關既有文章或系列導讀，建立 topic cluster；不要濫塞內鏈。
- 新系列若已形成知識鏈，可建立 roadmap / hub，但不新增公開 domain。
- 重要內容不要只存在圖裡；正文需有可索引文字。
- 圖有描述性 alt。
- 不 keyword stuffing。
- canonical / Open Graph / sitemap / structured data 等應由共用 template 管理，不在個別文章手工複製。
- 若修改 SEO template，需先核對 Jekyll 輸出，避免重複 canonical、錯誤 dateModified 或 JSON-LD。

---

## 10. 寫入 GitHub 時的併發與安全規則

此 repo 可能同時被多個 agent / automation 寫入。

因此：

- 每次寫入前重新讀取目標檔案最新 blob SHA。
- 保留其他 agent 已提交的修改。
- 不 force-push。
- 不用過時檔案整份覆寫 main。
- 同一路徑連續 update 必須串行。
- 發現 branch/head 已改變時先重新讀取與 rebase/merge 語意，不盲目 retry。
- 不為了讓 Pages 重新跑而送空 commit。

不得公開：
- 公司內部程式碼、PDK、private RTL、log、skill、case、客戶資料。
- 未公開 CAD 架構、憑證、token、帳號、內部 endpoint。
- 私人投資持倉、未公開工作資訊，除非使用者當次明確要求且適合公開。

---

## 11. 發布與 permalink：commit 成功不等於網站發布成功

Jekyll permalink 不能靠直覺自行拼接。

特別注意：
- categories 可能進入 default post URL。
- `domain` 不等同 URL path。
- 發布前先讀 `_config.yml`、現有文章與目前 Jekyll 規則。
- 不把 GitHub blob URL 當 public article URL。

使用者若指定僅做內容／front matter／來源／圖文靜態檢查與遠端提交確認，採該任務的精簡流程：不例行輪詢 Actions、HTTP 或 Pages artifacts，不建立、下載或保存 ZIP／TAR 等壓縮封存檔，也不新增驗證 workflow。只有明確發布異常才針對性除錯。回報 commit 與依 permalink 推導的 URL，明示未做 HTTP 驗證；不得宣稱已驗證上線。

一般發布流程：

1. 取得最新 default branch。
2. 建立／修改文章與圖片。
3. 做 front matter / links / sources / image paths / duplicate check，並執行 `python3 scripts/lint_posts.py <新文章路徑>`。未通過就修改後重跑，不得提交。執行環境無法跑 Python 時，逐條對照下方 lint 清單自查；部署 workflow 仍會擋下未通過者。
4. 能本地 build 時執行 `bundle exec jekyll build`；若無法 build，明確區分未驗證項。
5. Commit 到授權的 branch / default branch。
6. 回讀遠端檔案，確認本次內容真的存在。
7. 檢查對應 GitHub Pages build。
8. 確認 deploy 成功。
9. 取得依 **實際 Jekyll permalink** 形成的正式 URL。
10. 正式頁面必須顯示本次標題／正文；**HTTP 200 本身不足以證明新版本已上線**。
11. 只有 source + build + deploy + public content 均成立，才回報「發布成功」。

若 deployment pending、工具不能讀正式站或 verification 不完整，精確寫目前完成到哪一層，不假稱完成。

若「Post lint gate」workflow 標成失敗，或文章出現在 `_blocked/`，代表被 lint 擋下、沒有上線。依 `_blocked/<檔名>.lint.txt` 修正，移回 `_posts/`（保留原檔名與 date）後重新提交。

### lint 清單（`scripts/lint_posts.py`，適用 2026-10-02 13:00 之後建立的文章）

- front matter 具備 title、date、domain、categories（與 domain 相同）、description、takeaways（3–6 條，`who` 為具體名稱且不是分析類別，`value` 40–160 字，總長 250–700 字）。2026-10-02 13:00 至 2026-10-04 12:00 建立的文章可用舊的 summary、lede 或 takeaways。
- 2026-10-04 12:00 之後、非豁免的文章：正文（`## 證據範圍` 之前）至少有一段同時出現早於發文年份的年份與外部來源連結（前例），以及至少一處指向未來的時間範圍（預判）。
- 標題、description、重點、章節標題與正文不使用第 4.5 節列出的分析框架詞彙，也不用「對 X：」的逐一列舉句式。
- 標題不含冒號；標題、description、開頭段不使用第 4 節列出的模板句型。
- 正文不出現作者立場標註、素材取得過程、排程搜尋窗口、私人研究框架術語或符號、幕後寫作方法。
- 有 `## 證據範圍` 段落；該段之前的正文，否定／保留語（不能、不代表、不等於、並非、而非、不可、不宜、未必）每萬字不超過 12 次。
- 框架詞（驗收、邊界、證據、恢復、契約、閘門、可採信）每萬字上限：`ic-design-platform`、`distributed-systems` 為 25，其餘分類為 15。
- 至少一個站內文章連結與一個外部來源連結；不連 OpenAPI／JSON 端點或 Facebook。

---

## 12. 只有在改網站程式時才做的完整站點驗證

若修改 layout、include、CSS、JS、search、category、RSS、SEO 或共用 UI，至少檢查：

- `/`
- `/categories/`
- `/search/`
- 一篇既有文章
- 一篇新文章
- `/feed.xml`
- `/search.json`

搜尋至少測：
- 僅正文存在的 keyword。
- multi-keyword AND query。
- domain/category filter。
- zero-result。
- index load failure。

視覺至少測：
- mobile overflow。
- table/code horizontal behavior。
- keyboard focus。
- TOC。
- images。
- 若 CSS 更新，使用 versioned asset URL 避免舊 cache。

Article-only content commit 不必為了形式重跑所有 UI 測試；只做與本次變更相稱的驗證。

---

## 13. 保留與刪除規則

IC 設計平台目前只公開以平台架構、工程協作、工具／資料交接、狀態管理、執行恢復或驗收治理為主問題的文章。純 STA／SDC 基礎教材、placement／timing 演算法或單一引擎機制暫不公開；不能只加平台總覽或驗收段落就視為平台文章。封存清單以 `_archive/ic-design-platform/README.md` 為準；封存稿仍算歷史已完成，保留原始 date、categories、series、篇號及查重紀錄，不移回 `_posts/`、不換 slug／日期重發，恢復發布須使用者另行確認。其他分類與十四個系列的研究責任、五個排程器的時程及啟用狀態不變。

- 不任意修改既有文章 filename、date、categories、permalink。
- 未經要求，不順手改寫舊文章。
- 已刪除且不得重建：
  - `_posts/2025-09-21-welcome-to-jekyll.markdown`
  - `_posts/2025-09-21-create-cline-cli.md`
- 刪除文章後，需確認首頁、分類、搜尋索引與實際 URL 的狀態符合預期。

---

## 14. 完成回報

回報保持短而可驗證。

一般文章：
- 標題
- repo path
- commit SHA
- 正式 URL（若已驗證）
- 若尚未正式上線，寫清楚停在 commit / build / deploy / HTTP content 哪一層

技術 deep dive 可額外回報：
- 正文有效長度
- 網站 reading-time 的驗證結果或採用的估算依據
- 圖片數量

不要：
- 將本地修改說成已發布。
- 將 commit success 說成 Pages success。
- 在一次回覆後宣稱仍在背景工作。
- 重複整份研究流程或 agent 操作流水帳。

---

## 15. SITE_GUIDE.md 的角色

`SITE_GUIDE.md` 是給人閱讀的網站架構摘要與維護提示；其中與本文重疊的 Publishing / Features / Validation 規則已納入本文件。

若兩者未來出現不一致：
1. 使用者當次明確要求優先。
2. `AGENTS.md` 為 agent canonical instruction。
3. `SITE_GUIDE.md` 應同步修正，而不是讓兩套規則長期分岔。

任何 agent 在「開寫文章前」只要遵守第 0 節，就必然會先讀到這套規則。

