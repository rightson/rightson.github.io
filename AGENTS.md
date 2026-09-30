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
   - 與任務相關的 roadmap / series spec（若存在）
   - 最近至少數篇同 domain／同系列文章，檢查重複與既有語氣。
3. 若任務會影響 layout、search、分類、RSS、about、CSS 或其他網站功能，再讀對應的 `_layouts/`、`_includes/`、`_data/`、`assets/` 與 `SITE_GUIDE.md`。
4. 確認同日／同系列／同 slug 是否已有文章；不得重複建立。
5. 先形成「認知增量」：新證據、新機制、新實驗、新架構比較，或明確修正舊判斷。選材看研究價值、工程影響與可長期保留的理解，不按新舊或熱門程度排序。經典教材的增量也可以是補齊必要先備、推導或可驗證的直覺；不因當天沒有新聞而跳過課程。沒有足夠價值時不為排程硬湊文章，回報原因，但不得自行停用、暫停或刪除 recurring task。
6. 才開始研究、畫圖與寫作。

若取得規則、原文或現況失敗，先說明缺口，不可依猜測覆寫檔案。

---

## 1. 網站架構與不可破壞的既有能力

本站使用原生 Jekyll + GitHub Pages：

- 無 remote theme。
- 無 JavaScript framework。
- 無外部字型依賴。
- 搜尋為本站自有 client-side index，不把文章內容送往外部搜尋服務。

現有功能應保留：

- 首頁依時間由新到舊顯示文章。
- 八個固定研究 domain（見第 2 節）。
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

## 2. 八個公開分類與 URL 穩定性

分類名稱採學術會議與業界通用詞彙；每篇選一個主要 `domain`：

| domain | 公開分類 | 內容 | 常見對應 |
| --- | --- | --- | --- |
| `ai-industry` | 產業分析 | AI／半導體需求、供應鏈、產能、政策、價值分配 | 產業研究 |
| `investing` | 投資與交易 | 投資假設、估值、催化劑、資金動向、交易與風險 | 投資研究 |
| `eda` | 電子設計自動化 | EDA 演算法、synthesis、placement、routing、sizing、STA／SDC、timing closure、verification、signoff 方法 | DAC、ICCAD、TAU |
| `ic-design-platform` | IC 設計平台 | 多人協作、IP／SoC 整合、跨工具交接、R2G 流程、設計資料與執行治理平台 | CAD infrastructure、design management |
| `architecture` | 計算機架構 | 加速器（TPU／GPU／ASIC）、處理器微架構、記憶體階層、資料流、效能模型 | ISCA、MICRO、HPCA |
| `networking` | 網路與互連 | 網路協定、交換晶片、光通訊、scale-up／scale-out 互連、資料中心網路 | SIGCOMM、NSDI、Hot Interconnects |
| `distributed-systems` | 分散式系統 | 叢集管理（Kubernetes、Slurm）、控制面、一致性、複寫、容錯、大規模服務設計 | OSDI、SOSP、EuroSys |
| `ai-frontier` | AI 前沿技術 | 前沿模型、訓練／推論演算法、reasoning／multimodal、Agent／工具／memory／evaluation、open-weight 競爭與即時技術討論 | AI 前沿技術摘要、模型與系統研究 |

規則：

- 每篇新文章只有一個 primary `domain`，依文章的核心問題決定，不按關鍵字機械分類。
- 新文章的 `categories` 原則上使用與 `domain` 相同的單一值。
- **既有文章的 `categories` 不可為了重新分類而修改。** Jekyll default post URL 會受 categories 影響，修改可能直接破壞外部連結；重新分類只改 `domain`。
- `domain` 用於內容分區，不應改變文章 URL。
- **分類變更前必須先向使用者提出方案並取得確認**，包括：新增、合併、拆分或更名公開分類、調整顯示順序，以及改變既有文章的 `domain`。確認後再同步 `_data/domains.yml`、`_includes/domain-key.html`、本表與相關 roadmap。
- 新文章依本表與邊界規則選定 `domain`，不需逐篇詢問；若核心問題無法明確對應任一分類，先詢問，不自行新增分類。
- 不用細碎 category/tag 製造分類噪音。首頁、分類頁與文章頁只對讀者顯示 `domain`；`categories` 僅用於既有 URL 與搜尋篩選。
- 顯示順序依 `_data/domains.yml`。
- 邊界：
  - 「AI 前沿技術摘要」排程使用 `series: ai-frontier-digest`；新文章固定 `domain: ai-frontier` 與 `categories: ai-frontier`。既有本系列移入時只改 `domain`，保留原 `categories`、檔名、date 與 permalink。
  - 模型能力、訓練／推論方法、通用 Agent 技術及 open-weight 比較歸 `ai-frontier`；需求、供應鏈、產能與價值分配歸 `ai-industry`，估值與交易歸 `investing`。獨立的硬體微架構、互連、控制面或 EDA 深掘仍按下列既有邊界分類；AI 前沿技術摘要中為理解模型／Agent 而引用跨層機制，不改變本系列的主要分類。
  - STA／SDC／timing closure 與 EDA 演算法歸 `eda`；多人協作、IP／SoC 整合、跨工具資料交接、R2G 流程與設計資料／執行治理歸 `ic-design-platform`。依正文的主要問題分類，不按排程名稱或廠商名稱決定；C3PO／AutoDMP 等以 placement 最佳化為主的文章歸 `eda`。
  - TPU／加速器的微架構與資料流歸 `architecture`；其商業、供應鏈或估值歸 `ai-industry`／`investing`。
  - Kubernetes／HPC 叢集與控制面歸 `distributed-systems`，即使應用案例是 EDA；NVLink／UALink／光互連等資料路徑歸 `networking`。
  - 光互連技術機制歸 `networking`；光通訊公司估值／交易分析歸 `investing`。

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
domain: eda
categories: eda
description: "一至兩句概括文章真正的核心判斷。"
---
```

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
- 「作者整理／作者推論／作者設計」仍用來標識證據性質，不取代固定署名。

---

## 4. 標題、摘要與文章語氣

### 標題

- 標題先寫「觀察後得到的具體技術／產業結論」或明確工程問題。
- 不使用例行模板，例如：
  - 今日結構變化
  - 今日唯一研究問題
  - XX/XX 技術雷達
  - 重算版／更新版
- 不用日期當標題核心，除非日期本身就是事件。
- 不為 SEO 堆砌同義關鍵字；標題要能準確回答「這篇到底在講什麼」。

### 全站技術文章的推理與敘述

- 開頭先提出具體核心判斷或問題，同時建立足以理解它的全局背景：這項技術在更大系統中負責什麼、原有設計為何合理、什麼需求或限制使問題浮現。不要尚未交代問題，就直接丟出局部實作、產品規格或論文摘要。
- 進入細節前說清研究動機與價值：瓶頸從何而來、理解錯會影響哪個設計判斷、這篇增加哪個非顯然且能長期保留的 insight。背景的範圍以支撐核心問題為準，不寫無關歷史，也不預設讀者已懂尚未教過的先備。
- 論述自然由「為何值得解決」推進到「機制如何運作」，最後落到「哪些判斷與決策因此改變」。這是內容的因果關係，不是固定章節名稱；不硬分 Why / How / What，也不在公開文章介紹寫作方法。
- 依題目與讀者階段深入必要的模型、數學、程式、資料／控制路徑、實驗與證據。持續追問 assumptions、baseline、適用條件、trade-off、failure mode 與未解問題；不要為形式跨層，只有上下層 coupling 會改變結論時才延伸。
- 章節應各自推進推理，不把同一結論換句話說反覆填入。收尾留下具體、能改變研究或工程判斷的理解，以及下一個可驗證問題。
- 這些要求適用於所有技術類型與 lab，不取代各系列的讀者設定、先備順序、深度、實驗或交付規格。入門文章先補直覺與最小模型，進階文章保留必要技術深度；不可用術語密度代替解釋。

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

改用直接陳述結論或具體問題，例如：
- ✗「NVLink 6 真正的突破不是 3.6 TB/s，而是把故障恢復做成跨層控制迴路」
- ✓「NVLink 6 把故障恢復做成跨層控制迴路：從 PHY retry 到 NCCL 彈性恢復」

發布前必做：
1. 列出最近 20 篇文章的標題與 `description`，確認新標題的句法骨架（去掉專有名詞後的結構）沒有與任何一篇相同。
2. 同一句法骨架在最近 20 篇中最多出現一次；系列標記（如「創始篇」「Day N」）不算骨架，但不可取代具體結論。
3. 若標題仍需對比，只陳述被修正的具體誤解與證據，不用「不是…而是…」模板。

### 文字

- 使用台灣慣用的繁體中文，保留必要英文術語；完全避免中國大陸用語。依語境使用「通訊、效能、資料、運作、程式、軟體、硬體、記憶體、佇列、頻寬、最佳化、部署」等台灣用法；英文比生硬翻譯精準時直接保留。
- 一般文章結論先行；分散式系統系列依上節先建立問題與需求。句子有資訊，不以口號製造力道。
- 用工程問題、限制、機制、證據、trade-off 推進論述。
- 不在文章中提「第一性原理」「Golden Circle」「寫作框架」「prompt」「本篇如何帶讀者理解」等幕後方法。
- 推理可以從最根本約束出發，但方法只體現在內容，不自我介紹。
- 不用機械化 AI 句型反覆填充，例如「真正的核心不是 X，而是 Y」若沒有新的具體證據就不要重複。
- 不在正文交代 routine、coverage audit、資料截點流程、重算流程等與讀者無關的幕後操作。
- 不為模仿人味加入假口語、驚嘆號、刻意反問或虛構親身經驗。

---

## 5. 深度文章的預設品質門檻

當任務是技術 deep dive、EDA / networking / distributed systems / TPU 類長文，若專題規格沒有另訂更嚴格門檻，預設以 **至少約 10 分鐘實質閱讀深度** 為目標。

建議正文約 4,000–6,000 中文字；深題可更長。圖說、References、front matter、大段程式碼不算拿來湊篇幅。

長度不是目的。文章應至少具備：

1. 具體 engineering contradiction / bottleneck。
2. 現有方法為什麼在特定條件下失效。
3. 至少兩個真正決定結果的 mechanism。
4. 一個完整具體案例或 end-to-end path。
5. 一個 failure scenario：失效點、殘留狀態、偵測、恢復／rollback 與保證邊界。
6. 至少兩種合理設計的 trade-off；不要預設多一層平台或多一個 agent 一定較好。
7. 至少一項量化證據或透明算例，標明 baseline、單位、假設與限制。
8. 收斂到實際工程影響與下一個可驗證問題。

若網站現有 reading-time algorithm 可取得，發布前依同一算法確認；未達門檻應補機制、案例與證據，不可硬寫 `reading_time: 10` 或修改演算法作弊。

短評、投資快訊等若有明確 task-specific 篇幅規格，以該任務為準；不要為套用長文規則而灌水。

---

## 6. EDA / IC Design Platform 文章的特殊要求

`eda` 與 `ic-design-platform` 分別依第 2 節分類；兩者仍共用以下工程證據與保密要求。

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
- 自己畫的「合理參考架構」清楚標成作者設計／推論，不畫成廠商官方架構。
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

### 研究價值與證據範圍

- 學術選材重視前瞻性、重要問題、機制洞見與可信證據，不以 production grade 作為研究價值門檻。
- 清楚交代實驗條件、規模、baseline 與結論邊界即可；不要把「尚非 production grade」當成每篇學術文章的例行免責段落。
- Demonstration、模擬、benchmark 與實際部署仍須依證據正確命名。只有與當篇工程判斷有關時，才深入部署、可製造性或可靠性缺口；不得把外推寫成實測或部署事實。

### 多作者論文

正文通常只寫：
**第一作者 + 所屬機構**。

其餘作者可留在 References 或原文連結；機構不確定就不要猜。

### 事實與推論

清楚分開：
- source fact
- paper / vendor reported result
- 作者推論
- 假設算例
- 作者設計方案

作者推論可以有力度，但不能偽裝成來源已證實。

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
- 自己提出的架構：標「作者設計」。
- 直接引用或改繪外部圖片前確認允許的引用／授權條件。
- 圖中文字與箭頭需在手機寬度仍可理解。
- 網站會跟隨系統深淺色。新增或修改 SVG 後執行 `python3 scripts/svg_dark_mode.py <svg 檔案>`，為圖加上深色配色（可重複執行）；並在深色模式下確認文字可讀。
- 圖檔與 Markdown 同 commit，避免文章先上線但圖片 404。

### 開頭的背景示意圖

- 所有技術文章與 lab 的開頭應搭配一張有助於理解背景與研究動機的示意圖。先用一至三個段落建立具體情境，再在進入局部機制前放圖；圖要讓讀者看見系統如何運作、原有設計為何合理，以及問題在哪個位置浮現。
- 依題目選擇情境、端到端流程、系統邊界、拓樸、時間軸或原有方案與需求變化的對照。分散式系統案例先畫使用者與服務需求，不在需求未成立前把最終架構畫成既定答案。
- 圖前後要有具體導讀，指出應沿哪條資料／控制路徑、觀察哪個相依或瓶頸，以及它如何銜接本文的核心問題。圖片不能代替必要的背景文字，也不以術語方塊清單、無關插圖或重複正文湊數。
- 既有文章亦適用：逐篇檢視開頭，已有合適圖時重用、移至合適位置並補導讀；缺少時補畫。保留技術深度、來源、date 與 permalink，不必為此整篇重寫。
- 概念圖、假設案例與作者設計須清楚標示；廠商或論文的實作只能依 primary source 呈現。示意圖的線寬、顏色與位置不冒充實測效能或比例。遵守本節 SVG、圖說、手機可讀性與深色模式規則。

建議圖片路徑：
`images/<domain>/YYYY-MM-DD/<descriptive-name>.svg`

---

## 9. 內部連結、SEO 與可讀性

- 每篇有具體 `description`，摘要核心結論，不寫「本文將介紹」。
- 適當連到既有相關文章／系列導讀，建立 topic cluster；不要濫塞內鏈。
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
3. 做 front matter / links / sources / image paths / duplicate check。
4. 能本地 build 時執行 `bundle exec jekyll build`；若無法 build，明確區分未驗證項。
5. Commit 到授權的 branch / default branch。
6. 回讀遠端檔案，確認本次內容真的存在。
7. 檢查對應 GitHub Pages build。
8. 確認 deploy 成功。
9. 取得依 **實際 Jekyll permalink** 形成的正式 URL。
10. 正式頁面必須顯示本次標題／正文；**HTTP 200 本身不足以證明新版本已上線**。
11. 只有 source + build + deploy + public content 均成立，才回報「發布成功」。

若 deployment pending、工具不能讀正式站或 verification 不完整，精確寫目前完成到哪一層，不假稱完成。

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
