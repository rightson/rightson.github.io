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
5. 先形成「新資訊增量」：新證據、新機制、新實驗、新架構比較或明確修正舊判斷。沒有資訊增量時，不為了排程硬湊文章。
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
- 七個固定研究 domain（見第 2 節）。
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

## 2. 七個公開分類與 URL 穩定性

分類名稱採學術會議與業界通用詞彙；每篇選一個主要 `domain`：

| domain | 公開分類 | 內容 | 常見對應 |
| --- | --- | --- | --- |
| `ai-industry` | 產業分析 | AI／半導體需求、供應鏈、產能、政策、價值分配 | 產業研究 |
| `investing` | 投資與交易 | 投資假設、估值、催化劑、資金動向、交易與風險 | 投資研究 |
| `eda` | 電子設計自動化 | RTL-to-GDS flow、SYN/APR、驗證、DFT、IC 設計平台／CAD 基礎設施、AI for EDA | DAC、ICCAD |
| `timing` | 靜態時序分析 | STA、SDC、clock 關係、setup／hold、timing closure、OCV／SI | TAU、STA |
| `architecture` | 計算機架構 | 加速器（TPU／GPU／ASIC）、處理器微架構、記憶體階層、資料流、效能模型 | ISCA、MICRO、HPCA |
| `networking` | 網路與互連 | 網路協定、交換晶片、光通訊、scale-up／scale-out 互連、資料中心網路 | SIGCOMM、NSDI、Hot Interconnects |
| `distributed-systems` | 分散式系統 | 叢集管理（Kubernetes、Slurm）、控制面、一致性、複寫、容錯、大規模服務設計 | OSDI、SOSP、EuroSys |

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
  - STA／SDC／timing closure 歸 `timing`；flow、平台、驗證、SYN/APR 方法歸 `eda`。
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

以 **目前 default branch 的共用 layout 與本文件最新規則** 為準，不沿用舊對話推測。

目前站規為：
- 公開文章不顯示作者姓名，不在正文重複署名。
- front matter 不需要自行加入 `author`。
- 「作者整理／作者推論／作者設計」僅用來標識證據性質，不代表公開署名。
- 若使用者未來明確恢復署名，應修改共用規則一次，而不是每篇文章自行硬寫。

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

### 文字

- 繁體中文為主，保留必要英文術語。
- 結論先行，句子有資訊，不以口號製造力道。
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

- 優先原創 SVG 或 repo 已確認能直接顯示的格式。
- 不把未渲染 Mermaid 原始碼當成完成圖片。
- 圖要回答問題：資料怎麼走、誰擁有 state、哪裡排隊、哪裡驗證、哪裡會失敗、怎麼恢復。
- 不用 stock image 或裝飾性插圖湊圖數。
- 每張圖有 alt text、caption、來源。
- 依 primary source 重畫：標「依據 XXX 整理／重繪」並附 link。
- 自己提出的架構：標「作者設計」。
- 直接引用或改繪外部圖片前確認允許的引用／授權條件。
- 圖中文字與箭頭需在手機寬度仍可理解。
- 圖檔與 Markdown 同 commit，避免文章先上線但圖片 404。

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

發布流程：

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
