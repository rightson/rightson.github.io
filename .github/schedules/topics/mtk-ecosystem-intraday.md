# 盤中價量與事件觀察

本任務只處理 `mtk-ecosystem-intraday`。每次啟動直接執行本文件，不依星期、觸發時段或啟動時間選擇其他主題。

先讀同一 instruction commit 的 `AGENTS.md`、`.github/schedules/common.md`、`.github/ARTICLE_TAXONOMY.md`、`_data/research_series.yml` 及以下研究進度，再讀最近同系列文章。

## 接續來源

- `.github/MTK_ECOSYSTEM_RESEARCH.md`

## 本次工作

盤中價量與事件觀察。本任務 series: mtk-ecosystem-intraday。
先從官方交易日資料確認當天是否開市，非交易日直接結束本次觀察，保留排程。檢查資料來源、實際報價 timestamp、延遲與可用範圍；無適合盤中報價時在 session 明確回報資料能力缺口，不把日終／延遲資料冒充即時，不做缺乏支持的盤中進出判斷。以 MTK／台積電與已驗證關係觀察池，觀察價格／成交量、同時段可比較量能、相對強弱、技術關鍵區域與公告／消息的市場反應，檢查與既有 thesis 的分歧。盤中法人與融資券只用最新已公布資料，區分今日價格與前一交易日籌碼。只有出現重要的新變化／風險／條件觸發才在本新 session 通知，未變化保持安靜；同一事件記錄 timestamp 與 fingerprint 去重。這是離散觀察，不宣稱持續即時監控。提供條件式候選與失效條件、資料證據和不確定性，不承諾預測噴發、不代下單、不接觸交易授權。私人盤中訊號不例行發布 GitHub 文章。

先讀 rightson/alpha-quant 最新 default branch metadata 與該 commit 的 seeds/watchlists/ai_supply_chain_universe.csv。實際核對整個 active universe，逐項區分已取得、未更新與缺資料；不能以少數熟悉公司代表全池。讀取失敗需回報覆蓋缺口。核心為 MTK、台積電與有明確客戶、供應商、競爭、替代或產能依賴證據的公司。納入全球 AI infrastructure、HBM／記憶體、儲存、加速器、電力及中國新增產能；追蹤 MTK 在 hyperscaler AI silicon 的責任、SerDes／D2D／memory interface／implementation／integration／packaging／production 與價值分配，並尋找客戶自研或拆分採購的反證。個股篩選與估值先核對最新可取得股價及成交日期／時間，不用舊價判斷低基期或潛在漲幅。
本次全部結果只留在本排程對話或已授權私人紀錄，不提交公開 repo。不得公開個股即時估值、目標價、籌碼判讀、進退場條件、持倉或交易日誌。
