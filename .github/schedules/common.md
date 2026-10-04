# 五個研究排程的共用規則

AGENTS.md 是全站 agent 規則來源。本檔補充五個排程共用的執行要求；專屬責任見各任務檔。每次讀取同一個最新 default-branch commit 的版本，不混用不同 revision。

每次執行只處理本次排程指定的研究分支；所有時間以 Asia/Taipei 解讀。用觸發的排定日期、星期與時段判斷分支，延遲啟動仍處理原時段，不依啟動時刻誤切其他分支；若無法確認時段就回報缺口。讀取可持續保存的各系列 roadmap、最近成果與進度，使用「系列＋排定日期＋時段」核對本次是否已完成；既有完成成果只引用，不重複發布。這是防止同一次執行重試重發，不得以主題相近為由省略必要課程深度。各系列分別記錄進度、阻塞、實驗與驗證狀態，不能因合併成一個排程而跳過其中一個分支。
所有公開文章寫入 rightson/rightson.github.io。每次先讀最新 default branch metadata、完整 AGENTS.md、_config.yml、直接相關 roadmap、.github/RESEARCH_SCHEDULES.md、.github/RESEARCH_AUTOMATIONS.json 與最近同系列文章；發布前另核對最近 20 篇標題與 description。以當下 AGENTS.md 為寫作與發布規則來源，不以本 prompt 摘要、記憶或舊對話代替；本次使用者核准的五分組與分支節奏優先於舊排程清單。必需規則讀取失敗就回報缺口並停止該次發布，保留 recurring task，不自行暫停或刪除。
寫作遵守 AGENTS.md 第 4 節「通用寫作指引」全部 40 條，系列任務檔只能更嚴格。重點提醒：標題直接寫結論且不用冒號；標題下方的重點整理（takeaways）以具體公司或角色為標籤、每條一句完整因果句，90 秒內能轉述誰得到什麼、誰付出什麼、長期改變什麼、什麼情況會翻盤；正文以判斷句推進，保留條件集中於文末「## 證據範圍」；證據性質用「依據 XXX 整理」「推論」「參考設計」「假設算例」標示，不標註作者立場；第 4.1 節的思考步驟只變成內容，不出現框架詞彙、分析類別標題、粗體標籤或「對 X：」列舉，段落結構在連續幾篇間輪換；不寫素材取得過程、搜尋時間窗、私人研究框架術語與幕後方法。技術事實就近引用一手來源，連結要能定位到被引用的數字或段落，不連 OpenAPI／JSON 端點或社群貼文；核實日期、版本、成熟度、資料時間與 benchmark 條件。短訊不得冒充完整長文。
完整技術長文須至少約 10 分鐘實質閱讀深度，結論回答 primary domain 的核心問題（AGENTS.md 第 5 節表格）。依網站既有 reading-time 算法驗證，不硬填時數；加入開頭背景圖及必要機制圖。圖附 alt、caption、來源，圖中文字同樣不留痕跡，SVG 支援深淺色與手機閱讀，Markdown 與圖檔同 commit。
至少連一篇相關既有文章。提交前執行 python3 scripts/lint_posts.py <新文章路徑>，未通過就修改後重跑，不得提交；環境不能跑 Python 時逐條對照 AGENTS.md 第 11 節的 lint 清單。「Post lint gate」workflow 會把未通過的新文章移到 _blocked/ 並標成失敗；文章出現在 _blocked/ 時回報「被 lint 擋下、未上線」，依 _blocked/<檔名>.lint.txt 修正後移回 _posts/ 重新提交，不得宣稱發布成功。
每篇依「文章主要回答什麼問題」選九類之一，並讀取最新 .github/ARTICLE_TAXONOMY.md 與 _data/research_series.yml：晶片設計流程、EDA 演算法、STA／SDC、verification、synthesis／APR、signoff、交接與治理用 ic-design-platform（IC 設計平台）；模型、訓練／推論及通用 Agent 用 ai-frontier（AI 技術與工程）；加速器微架構、記憶體、資料流與軟硬體協同用 architecture（運算架構）；協定、封包路徑、互連與壅塞用 networking（網路系統）；分散式服務、資料模型、一致性、複寫、容錯與恢復用 distributed-systems（分散式系統）；Linux、容器、K8s／HPC、叢集資源、平台效能與維運用 platform-engineering（系統與平台）；企業成長、競爭、獲利、供需及價值分配用 ai-industry（產業與供應鏈）；股價已反映的預期、估值、機構資金、價量及进退場條件用 investing（投資與交易）；自然現象、材料物性與物理實驗用 science-physics（科學與物理）。只出現營收、EPS、毛利或現金流數字不代表投資文。十四個系列維持獨立 roadmap 與穩定 series／篇號；系列預設分類僅供起點，LLM Lab 的硬體資料流可歸 architecture，半導體深研若以合理股價或布局為主則歸 investing，通用 Agent 歸 AI 而設計流程導入與驗收歸 IC 平台。每篇只有一個 primary domain，系列、公司與技術名稱作次級資料，不增加主選單，不建立 eda／timing 獨立公開分類。新文章 categories 與 domain 使用相同單一值；既有文章僅以 domain 修正顯示分類，保留 filename、date、categories、permalink、原有 series 與 series_order，不變動正文或網址。series 延續現有穩定 identifier；SOTA 用 sota-r2g-cad，AI 摘要用 ai-frontier-digest，TPU 用 tpu-technical，Networking 用 networking-deep-dive，分散式系統用 distributed-systems，K8s 用 k8s-hpc；其餘按 research_series.yml，未有接續證據不硬套歷史文章。
公開文章不得含公司內部資料、私人會議材料、持倉、個人投資交易日誌、憑證或非公開 PDK。會議提綱與私人投資日誌留在本排程對話或已授權的私人紀錄，不能提交公開 repo。不傳訊給第三人、不下單或修改券商帳戶。
寫入前讀最新 head 與目標 SHA，保留其他 agent 的變更，不 force-push。依最新 AGENTS.md 完成必要靜態檢查、source 回讀與 build/deploy/public-content 驗證，只有完整證據成立才稱發布成功；精確記錄已寫入、已提交、部署或公開核验的階段。成功發布並核驗後才更新既有 roadmap，保留穩定篇號與歷史完成記錄。無新增價值的快訊不硬湊文章；課程依先備知識持續推進，無價值快訊不影響該週已排定的完整課程。
例行回報只列成果、原始來源、正式 URL、下一個已記錄進度或精確未完成階段。來源、行情或實驗失敗時指出受影響部分；不捏造結果、共識、即時價格或已完成發布。

2026-10-01 使用者核准：IC 設計平台目前只公開以平台架構、工程協作、工具／資料交接、狀態管理、執行恢復或驗收治理為主問題的文章。純 STA／SDC 基礎教材、placement／timing 演算法或單一引擎機制暫不公開；不能只加平台總覽或驗收段落就視為平台文章。封存清單以 `_archive/ic-design-platform/README.md` 為準；封存稿仍算歷史已完成，保留原始 date、categories、series、篇號及查重紀錄，不移回 `_posts/`、不換 slug／日期重發，恢復發布須使用者另行確認。其他分類與十四個系列的研究責任、五個排程器的時程及啟用狀態不變。

## 版本與維護

五個 runtime group 的完整執行入口見 manifest.json 與各自任務檔；RESEARCH_AUTOMATIONS.json 的十四筆 automations 保留系列補充規格，不是十四個啟動任務。五個 group 的分支時段優先於早期系列 prompt 內的舊時段，其他內容要求保留。AGENTS.md、ARTICLE_TAXONOMY.md 與封存規則以本次讀取的最新版本為準。

repo 指令的變更供下一次執行讀取；已經開始的執行沿用啟動時記錄的 instruction commit SHA。這是讀取 repo 的執行協定，並非 GitHub 自動同步 ChatGPT 設定。時程、enabled、模型、權限仍由雲端 scheduler 管理；只有使用者要求變更時才同步，不能僅因 repo 文件有新時間就自行改 scheduler。讀不到 repo 就停止該次工作並精確回報，保留任務啟用狀態。

