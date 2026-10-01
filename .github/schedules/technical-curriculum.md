# 技術課程

先讀同一執行版本的 `AGENTS.md`、`common.md` 與 `manifest.json`。本檔定義本排程的研究責任；時程以雲端觸發及 manifest 的對照紀錄判斷。十四個系列的補充規格與 roadmap 維持接續，內容要求不降低。

任務：按本次觸發星期執行指定課程。Networking、K8s／HPC、TPU／AI 加速器、分散式系統與 LLM Lab 分別保留獨立 roadmap、完成記錄與實驗進度。每個技術主題指定一個主要系列負責，其餘引用已完成篇目，不反覆重講。星期五明確有兩篇完整長文，不能因合併排程而縮成一篇摘要；其中一篇失敗不妨礙另一篇獨立核驗。
週三：Networking 每週深度長文。從 SIGCOMM、NSDI、ToN、CoNEXT、HotNets、IMC 等經典與新研究，以及可核實業界系統選題，連接 AI 網路問題。深入協定、資料路徑、效能模型、實驗與部署取捨，必要時連接 ISCA／MICRO／HPCA／ISSCC／VLSI／OFC／ECOC 的硬體證據。依現有 Networking roadmap 推進。
週四：K8s／HPC 系統工程完整長文。延續目前從 process／Linux 基礎重新開始的課程，由一般軟體工程背景可理解的動機與概念，依先備知識漸進建立直覺、系統模型、元件關係、execution path、Linux 機制、硬體行為、分散式系統、效能工程，最後才到 AI／EDA／HPC production architecture。依當下 K8s roadmap 接續容器、資源、網路、儲存、排程，不恢復已封存的舊文章或舊 #006，不跳回高階控制平面直接堆術語。完整保留從入門到精通的深度。
週五第一篇：TPU／AI 加速器深度系列。讀 .github/TPU_SERIES_ROADMAP.md，視為本系列唯一課程進度來源，依概念依賴選下一個未完成主題。深入微架構、資料流、記憶體、編譯器與互連，交代 workload／algorithm → compiler／runtime → microarchitecture → chip／memory／package → board／rack → network／datacenter 的上下層關係。作為 LLM Lab 硬體主線，已完成篇目供其他課程引用；供應鏈與商業判斷交由投資研究。
週五第二篇：分散式系統完整長文。延續既有 roadmap，每篇先給具體完整服務問題，再逐步挖掘功能需求、非功能需求、容量估算、API 與資料模型，推進基礎方案、一致性、複寫、容錯、恢復、瓶頸與替代設計。案例覆蓋完整 45–60 分鐘架構推理的廣度與關鍵深掘，但公開內容不得包含 AGENTS.md 禁止的面試或求職敘述。domain 與 series 均為 distributed-systems。不能沒頭沒尾從技術細節開始。
週六：LLM Lab：模型到晶片的完整技術鏈。另先讀 rightson/llm-lab 最新 default branch metadata、完整 AGENTS.md、README、現有 learning-plan、lesson-standard、learning-progress 與相關課程檔案。依先備知識推進模型概念 → 數學與演算法 → 程式實作 → 訓練／推論系統 → compiler／runtime／加速器 → HW design flow。每次一個完整單元，包含推導、可執行實驗、結果解釋與上下層關係。依該 repo 規則提交教材與程式，GitHub Pages 發布對應完整教學文章；分別驗證並回報兩個 repo 的完成階段。實際不能執行的實驗列為未完成，不捏造輸出或 benchmark。引用 TPU／Networking／K8s／分散式系統已完成素材，追蹤尚未完成的實驗。

