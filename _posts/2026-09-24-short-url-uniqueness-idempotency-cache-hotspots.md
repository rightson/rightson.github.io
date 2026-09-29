---
layout: post
title: "設計短網址服務：從分享與撤銷需求推導可靠讀寫"
date: 2026-09-24 08:28:05 +0800
domain: distributed-systems
categories: networking
series: distributed-systems
series_order: 1
description: "從建立、分享與撤銷連結的需求出發，先完成權威讀寫，再由重試、熱門流量及失效競態推導唯一鍵、冪等與快取邊界。"
---

行銷團隊要把活動頁放進簡訊，客服要分享帶查詢參數的支援頁，使用者則會把收到的連結存進聊天紀錄。長網址不方便轉傳，因此我們要提供一個服務：提交目的網址，取得短連結；之後任何人點擊，都能前往原本的頁面。

需求還有另一面。活動可能到期，連結可能被濫用，建立時也可能遇到網路逾時。收件者期待舊連結一直代表同一個目的地，管理者卻需要在必要時停止跳轉。要設計的問題因此是：如何讓建立與跳轉可靠，同時保留到期、撤銷與大量分享的能力？先把這些承諾說清楚，才能決定哪些資料可以快取、哪些操作需要共同確認。

## 分享出去的連結需要哪些承諾

先釐清「縮短」以外的功能。誰能建立？這裡假設登入的租戶可以建立連結，公開訪客不需登入即可跳轉；管理者只能停用自己租戶的連結。相同目的網址可不可以建立兩條短網址？可以，因為不同活動可能需要獨立生命週期，所以不能拿 destination 當唯一鍵。

目的地能不能修改？第一版建立後固定，只支援到期與停用。這讓已分享的連結有穩定意義，也減少快取更新的種類。自訂 alias 可選，衝突必須告知呼叫者；自訂網域、頁面預覽和逐次精確點擊計數先不納入。過期的 slug 不再分配給其他目的地，避免聊天紀錄中的舊入口突然指向另一個網站。

建立成功後能不能立即點擊？這裡要求可以；因此第一版的回源讀取必須看到已確認建立，不能任意讀取落後副本。停用需要多快？假設最晚三十秒不再接受新的跳轉判定，已經送出的 HTTP 回應無法撤回。這個有界延遲之後會限制快取的有效期限；若產品要求停用確認後立刻生效，架構必須另作選擇。

兩個不能妥協的不變量是：同一 slug 永遠只代表同一筆連結；同一租戶用相同請求識別重試建立時，得到同一筆資源，相同識別搭配不同參數則拒絕。前者防止連結混淆，後者防止逾時把一次建立變成多筆。

作為假設 SLO，合法、有效連結的跳轉成功率為 99.99%，p99 低於 50 ms，量測邊界為區域入口到送出回應，不包含目的站延遲；建立 API 成功率為 99.9%，p99 低於 300 ms。建立失敗尚可安全重試，既有連結則直接位於點擊路徑，兩者不需要同樣的資源預算。99.99% 在三十天約相當於 4.32 分鐘全部不可用，但部分請求失敗應以成功請求比例量測。[Google SRE：Service Level Objectives](https://sre.google/sre-book/service-level-objectives/)說明了這種 SLI 與目標的區別。

## 先讓建立與跳轉走完同一份權威資料

先不加入快取。部署一組無狀態 API 節點，背後使用同一個具交易與唯一索引的資料庫。建立時驗證租戶與目的網址，產生 slug，寫入連結，交易確認後回應；點擊時以 slug 查同一份權威資料，檢查狀態與到期時間，再回轉址。API 只需要兩條主要路徑：

```http
POST /v1/links
Idempotency-Key: 9f3...

{
  "url": "<destination-url>",
  "custom_alias": null,
  "expires_at": null
}
```

成功後回傳：

```json
{
  "slug": "aZ81KdP",
  "short_url": "<short-origin>/aZ81KdP"
}
```

讀取路徑只有：

```http
GET /aZ81KdP
```

如果連結有效，就回 `302 Found` 與 `Location`。HTTP 規格把 `302` 定義為目前資源暫時位於另一個 URI，因此原 URI 仍應作為未來請求的入口；`301` 則代表永久 URI 變更，且可以被 heuristic cache。[RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html) 的這個差異會直接影響產品能力：如果目的地可能修改、連結可能被停用，或流量統計需要在服務端可見，就不能隨意把所有 redirect 都做成長時間可快取的永久轉址。

這個版本的資料列包含 `slug` 主鍵、destination、tenant_id、status、version、created_at 與 expires_at。讀取索引先只服務 slug 點查；租戶管理頁若要列出連結，再增加 `(tenant_id, created_at, slug)` 索引，避免掃描全表。建立、停用及版本變動的權威都在資料庫，應用節點只持有正在處理的請求。

正常路徑能走通，還不代表兩個不變量已成立。下一步先檢查兩台建立節點選到相同 slug，以及同一建立請求被重送的情況；這兩個問題與流量大小無關，必須在加速讀取前解決。

## 兩台節點選到同一 slug，誰決定成功

slug 需要短、可以放進 URL，且不直接暴露建立順序。先選隨機值，再用 Base62 編碼，把 `[0-9A-Za-z]` 當成 62 個符號。7 字元空間是：

`62^7 ≈ 3.52 × 10^12`

8 字元則是：

`62^8 ≈ 2.18 × 10^14`

如果用隨機 7 字元 slug，很多設計會說「空間有 3.5 兆，碰撞幾乎不可能」。這句話少了使用量。

若系統累積 10 億個有效 slug，空間占用率約 `1e9 / 3.52e12 = 0.028%`。對下一次隨機產生而言，撞到既有值的機率也是約 0.028%，平均約每 3,500 次建立就會遇到一次 collision。這不算災難，但離「永遠不會發生」已經很遠。如果累積到 100 億條，單次 collision 機率就接近 0.28%。

可靠的設計不靠把亂數位數拉到讓人心安的長度，流程是：

1. generator 產生 candidate slug；
2. 權威資料庫對 `slug` 設唯一約束；
3. insert 若因 unique conflict 失敗，重新產生 candidate；
4. 只有 transaction commit 後，slug 才正式存在。

這裡資料庫 unique constraint 才是 uniqueness authority。亂數品質只影響 collision retry 的頻率與可猜測性，不負責 correctness。

另一條路是取單調遞增 ID 再做 Base62。優點是沒有 collision retry，而且 slug 可以很短；缺點是直接暴露建立量與順序，也把 ID allocation 變成跨節點協調問題。可以使用區段預配、時間型 ID 或其他方法降低中央 allocator 壓力，但那其實已經進入下一層問題。目前需求不要求序號排序，因此先選「足夠大的 random slug + unique constraint」，把複雜度留給需要它的地方。

自訂 alias 則完全不同。`/apple` 的衝突屬於資源競爭，和隨機 collision 無關。它必須直接走唯一索引，失敗就回 `409 Conflict`；不能偷偷改成 `/apple1`，因為那改變了呼叫者的語意。

## 建立已提交卻逾時，重試應得到什麼

唯一索引擋住了不同資源搶同一 slug，卻擋不住同一意圖建立兩個不同 slug。考慮這個失效序列：

1. client 送出 `POST /v1/links`；
2. server 成功 insert 並 commit；
3. server 回應途中連線中斷；
4. client 只看到 timeout；
5. client 再送一次相同 request。

如果服務沒有 idempotency contract，第二次 request 會產生另一個 slug。資料沒有「壞掉」，但同一個使用者意圖變成兩筆資源。這種錯誤很難靠事後去重，因為同一個目的 URL 本來就可能合法建立多個短網址。

所以建立 API 接受 caller 產生的 `Idempotency-Key`。資料模型至少需要兩個唯一邊界：

```text
links
  slug              UNIQUE PRIMARY KEY
  destination
  tenant_id
  status
  version
  created_at
  expires_at

idempotency
  tenant_id
  idempotency_key
  request_hash
  slug
  response_snapshot
  UNIQUE (tenant_id, idempotency_key)
```

關鍵在於：`idempotency` 記錄與 link 建立必須處在同一個原子提交邊界。不能先 insert link，稍後「best effort」補 idempotency row；也不能先記 key，再另外建立 link。AWS 在 [Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) 強調了同一件事：辨認 request token 與執行 mutation 的狀態必須具有 all-or-nothing 性質，否則服務仍會掉進「資源建立成功但 token 沒記到」或相反的裂縫。

![建立連結時的冪等與碰撞邊界](/images/distributed-systems/2026-09-24/short-url-idempotency.svg)

*圖：作者設計；idempotent request token 的原子提交語義參考 [AWS Builders' Library：Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/)。*

transaction 可以概念化成：

```text
BEGIN

if exists idempotency(tenant, key):
    if request_hash differs:
        reject
    else:
        return prior response

repeat:
    slug = random_base62(8)
    try insert links(slug, ...)
    if unique_conflict: continue

insert idempotency(tenant, key, request_hash, slug, response)

COMMIT
```

同一個 key 如果被兩台 server 同時處理，應由 `(tenant_id, idempotency_key)` unique constraint 決定唯一 winner。loser 重新讀取已提交結果並回相同語義，不依賴 process-local lock。原因在於狀態擁有者的範圍：application mutex 只在單一 process 內有效；資料庫約束才看得到所有 writer。

idempotency record 要保留多久，則是 API contract。若只保留 24 小時，代表 24 小時後的相同 key 可以被當成新 intent；若希望同一 key 永遠代表同一資源，就必須把這個綁定保存得和 link 一樣久。不能一邊承諾永久冪等，一邊讓 dedup table 每天清空。

還有一個容易忽略的情況：同一個 idempotency key，第二次 request 換了 URL。這不能直接回第一次結果，否則 caller 會以為新參數生效。最安全的契約是保存 canonicalized request hash；key 相同但內容不同就回 validation error。AWS 的文章也明確討論了這種「same request ID, different intent」。

此時殘留狀態是資料庫中已提交的 link 與請求記錄，client 則只有 timeout。服務可由相同 key 的 replay 指標辨識重試，恢復方式是查回已提交結果；不是刪掉第一筆再建立。若資料庫故障接手會遺失已確認交易，這個保證也會失效。因此成功回應的耐久性必須涵蓋允許的接手情境：新主節點要含所有已確認交易，且舊主已被隔離；無法證明時暫停寫入。快取中曾看過該 slug 並不能補回遺失的權威狀態。

## 讀寫量把哪條路徑推到瓶頸

建立語義先穩定後，再問這個全走資料庫的版本能撐多少讀取。以下是**假設算例**，不是實際產品流量。

假設每天建立 2,000 萬條短網址，每天產生 20 億次 redirect。平均寫入約：

`20,000,000 / 86,400 ≈ 231 writes/s`

若尖峰是平均的 8 倍，大約 1,850 writes/s。

redirect 平均約：

`2,000,000,000 / 86,400 ≈ 23,148 reads/s`

若尖峰約 10 倍，就是 23 萬 reads/s。

這個比例先告訴我們一件事：第一個瓶頸大概率不是「建立連結的寫入吞吐」。約 1,850 次／秒的建立量，讓單一交易型主庫值得先做容量驗證；是否撐得住仍取決於索引、交易內容、硬體及延遲，不能由 QPS 直接保證。會先把系統推向分散式的是讀流量、熱門 key，以及資料累積後索引工作集變大。

再估儲存。若每筆 link row 含目的 URL、slug、owner、建立時間、狀態、版本及必要索引，粗估 300 bytes：

`20M × 365 × 300 B ≈ 2.19 TB/year`

就算乘上三份複寫，再算索引與空間放大到原始資料的 1.5 倍，也大約是 10 TB/year 等級。這個量不小，但還不足以支撐一開始就建立全球多主資料庫。另一方面，若 99% redirect 都命中 cache，23 萬 QPS 的尖峰只留下約 2,300 QPS 回到權威儲存；若 cache fleet 同時失效，回源卻會瞬間放大到原本的 100 倍。因此短網址的主要容量風險來自 cache mode switch，平均資料量反而其次。

AWS Builders' Library 將這類情況描述得很精準：cache 一開始只是降低延遲與成本，久了下游容量會逐漸依賴 cache hit ratio；一旦 cold cache 或 cache fleet 故障，原本的加速層就變成容量相依。[Caching challenges and strategies](https://aws.amazon.com/builders-library/caching-challenges-and-strategies/) 特別提醒，若沒有為 cache miss 模式保留足夠下游容量，cache 就已從 latency cache 變成 capacity cache。

這個分類會決定故障策略。若資料庫只能承受 5,000 QPS，而 redirect 平常是 200,000 QPS，那 cache 故障時「直接全部回源」等於把局部故障轉成全站故障。

## 從重複讀取推導 shared cache 與熱門 key 複製

讀尖峰遠高於寫入，而且目的地固定，現在才有理由把重複查詢搬到記憶體。先加入 shared cache，以 cache-aside 走完一次讀取；下列 L1 是遇到熱門 key 後的第二步：

```text
GET /aZ81KdP
  → L1 local cache
  → shared cache
  → authoritative store
  → fill cache
  → 302 Location: destination
```

資料庫是唯一 authority。cache 裡的 value 可以包含：

```text
slug
destination
status
version
expires_at
cached_at
```

cache eviction 不影響 correctness，只影響 latency 與下游 load。這個界線非常重要。Facebook 在 NSDI 2013 的 [Scaling Memcache at Facebook](https://www.usenix.org/conference/nsdi13/technical-sessions/presentation/nishtala) 也明確把 memcache 放在非權威位置：cache miss 回到持久層；write 先修改 database，再刪除 stale cache。論文同時顯示，cache 一旦被用在極大規模，難點會落在 stale set、thundering herd 與故障時回源行為，hash table 本身反而簡單。

對不存在的 slug 也要做短時間 negative caching。公開短網址空間一定會被 crawler、scanner、拼字錯誤與惡意 enumeration 掃描。若每個 404 都打資料庫，一個簡單的 random scan 就能繞過 positive cache。negative cache 例如 5–30 秒，不需要長；它只負責把短時間重複 miss 擋在持久層前面，不用永久記住不存在狀態。

但 cache hit ratio 不能只看整體平均。假設有一個熱門 slug 突然收到 80,000 QPS，其他流量合計 120,000 QPS。如果 shared cache 以 `hash(slug)` 單點路由，那這個 key 可能把單一 cache shard 打滿，即使整體 fleet CPU 只用 20%。Facebook 的論文就記錄過單一 key 可能占一台 memcached server 約 20% 的請求，並指出故障後若單純把 key 重新 hash 到剩餘節點，會把 hot key 壓力轉嫁給另一台 server，形成連鎖風險。

因此短網址特別適合兩層 cache：

- 每個 redirect process 先有小型 L1 cache，把極熱門 slug 複製到所有服務節點，主動利用 replication 分散 hot-key read。
- shared cache 負責較大 working set，降低 database QPS。
- L1 TTL 短，例如數秒到數十秒；shared cache 可以較長，但失效必須受控。
- 不存在 key 也進短 TTL negative cache。

這個做法犧牲了一點記憶體效率，卻把「一個 key 對應一個 cache owner」改成「越熱門的 key 越自然複製到更多 redirect process」。對 read-heavy redirect 服務，這通常比追求完美 cache memory utilization 更重要。

![短網址的讀寫路徑](/images/distributed-systems/2026-09-24/short-url-read-write-path.svg)

*圖：作者設計；HTTP redirect 語義依據 [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html)，cache-aside 與 cache failure 的操作風險參考 [AWS Builders' Library：Caching challenges and strategies](https://aws.amazon.com/builders-library/caching-challenges-and-strategies/)。*

## 到期、停用與不存在，要保存不同狀態

加上快取後，先釐清它實際保存哪些狀態：`EXPIRED`、`DISABLED` 與從未存在的 `NOT_FOUND` 不能全部壓成同一個 cache miss。

如果一筆 link 到期後直接從 database hard delete，後續 request 看到 404，看起來很乾淨；但這會失去幾個重要能力：無法判斷 slug 是否曾經被使用、無法阻止舊 slug 被重新分配給另一個目的地，也無法在 abuse investigation 或 audit 時追溯曾經存在的狀態。更危險的是，如果 slug 可以被回收，舊 email、QR code 或瀏覽器歷史中的同一短網址，幾個月後可能突然指向完全不同的網站。identifier reuse 改變的是外部契約，影響遠超過 storage cleanup。

因此基線設計把 slug 視為永久占用的 namespace。record 可進入：

`ACTIVE → DISABLED`  
`ACTIVE → EXPIRED`

但不把 slug 重新配置給其他 destination。payload 可以在 retention policy 到期後縮成 tombstone，只保留 slug、final state、必要 audit metadata。RFC 9110 對 `410 Gone` 的語義是「資源已經有意永久不可用」；如果產品希望明確區分「從沒存在」與「曾存在但已移除」，可以讓 `NOT_FOUND → 404`、`DISABLED/EXPIRED tombstone → 410`，但這屬於對外 API 契約，不能因為清資料方便就臨時改動。

這也改變 negative cache。404 可以短暫 cache，例如 10 秒，用來吸收 scanner；410 tombstone 卻可以 cache 更久，因為它已是權威終態。兩者雖然都「查不到」，意義並不相同。一旦狀態有語義，cache key/value 就必須保留足以做正確判斷的資訊。

如果未來法規或隱私要求必須刪除 destination 本文，也可以保留不可逆 tombstone：slug digest、狀態與時間，不保留完整 URL。這讓「不可重新使用 identifier」與「刪除敏感內容」可以同時成立。

到期判斷不能只等待 cache eviction。每次跳轉都比較 `expires_at` 與可信的服務時間，且 cache freshness 不得跨過 expires_at；背景掃描將狀態改成 EXPIRED 是整理工作，不是停止跳轉的唯一機制。不同節點的時鐘誤差也要算進允許的到期偏差，超出門檻的節點撤出服務。

## 停用之後，為什麼舊資料還能回填

終態可以保存，但 ACTIVE 的快取仍會與停用競爭。假設一個連結因 abuse 被停用。寫入流程如果只是：

1. database 將 `status=DISABLED`；
2. delete cache key；

看似合理，仍有一個競態。

在更新前，reader A cache miss，去 database 讀到舊的 `ACTIVE`。接著管理者把 database 改成 `DISABLED` 並 delete cache。最後 reader A 才把剛才讀到的舊 `ACTIVE` 寫回 cache。結果是「invalidate 成功之後，舊資料復活」。

這種情況稱為 stale set。Nishtala 等人在 Facebook 的 memcache 設計中使用 lease：cache miss 時只讓持有特定 token 的 client 回填；如果期間發生 delete，lease 被 invalidated，舊 reader 即使晚到也無法再把 stale value 寫回。論文也用 lease 抑制 thundering herd，對同一 key 控制能取得 refill token 的 client；在其公開測量中，一組容易 herd 的 key，其 cache miss 導致的 peak database query rate 從 17K/s 降到 1.3K/s。[Scaling Memcache at Facebook](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170.pdf)

短網址不一定要複製 Facebook 的完整實作，但必須解決同一個時序問題。可採三種層級：

方案 A：短 TTL，接受有界 stale。  
最簡單。L1 只 cache 5 秒，shared cache 30 秒。停用後最差 30 秒仍可能 redirect。若產品容許，這是最低成本解。

方案 B：invalidation + refill lease/fencing。  
cache miss 取得 refill token；disable/update 會推進該 key 的 generation，使舊 token 失效。舊 reader 無法在 invalidation 後重新填入舊資料。這能把 stale window 壓到 event propagation 與正在執行請求的邊界。

方案 C：每次 redirect 都查權威狀態。  
correctness 最直觀，卻幾乎放棄 cache 的容量價值。除非停用即時性是絕對要求，而且流量很小，否則這不是合理預設。

我的選擇是 B 作為 shared cache 的 correctness boundary，加上短 L1 TTL。對安全停用事件，再主動 broadcast L1 invalidation。如此即使某節點漏掉事件，TTL 仍提供最終上限；若整個 invalidation bus 故障，也不會永久把 stale state 留住。

![停用與 stale refill 的競態](/images/distributed-systems/2026-09-24/short-url-stale-refill.svg)

*圖：作者設計；stale set 與 lease 機制依據 Rajesh Nishtala 等人於 NSDI 2013 發表的 [Scaling Memcache at Facebook](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170.pdf) 整理。*

實作時每個 slug 的 generation 與 refill token 由同一個 cache owner 原子管理。miss 回傳當前 token；失效推進 generation 並拒絕舊 token；回填必須在 owner 上比較 token 後才寫入。token 不能只存在讀者本機，也不能用先讀 generation、再無條件 set 的兩個操作替代，否則中間仍有競態。owner 重啟時舊 token 全部失效，從權威資料重新讀取；回源不能選可能落後於停用版本的副本。

跨資料庫與快取仍沒有原子交易。停用交易除了增加 link.version，也在同一交易記錄待傳遞的失效事件；傳送失敗可依 slug 與版本重送。cache owner 只接受較新的失效版本，避免亂序事件使世代倒退。這是本設計的補強，並非上述論文替服務提供的現成保證。事件傳遞降低常態延遲，三十秒上限仍由 hard TTL 兜底：TTL 從來源讀取時間起算，回填時扣掉在途時間；本機 L1 及 edge 只能繼承剩餘 freshness，不能每跨一層重新延長三十秒。

## 快取全部重啟，如何保住權威庫

現在正常流量已依賴快取，再追蹤整層快取消失的故障。

正常尖峰 200,000 redirect QPS，整體 cache hit ratio 99%，database 約 2,000 QPS。某次 shared cache fleet 因設定錯誤全部 restart。若所有 redirect server 立即把 miss 送到 database，後端負載瞬間變成 200,000 QPS。

這已超出普通的 1% latency regression：服務模式從「99% RAM lookup」切換成「100% persistent lookup」。Google SRE 在 [Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/) 特別指出，cold cache 會讓原本便宜的請求突然變昂貴；若服務容量是按 warm-cache 狀態規劃，重新啟動本身就可能造成 outage。AWS 也建議對 miss 使用 request coalescing，避免同一 uncached resource 同時發出大量下游請求。

所以恢復策略不能是「讓所有 miss 自由回源」：

1. L1 cache 即使 shared cache 重啟仍保留一部分熱門 key。
2. 同一 process 對相同 slug 的 concurrent miss 做 singleflight/request coalescing。
3. shared cache refill 也用 lease，讓同一 key 只有少數 request 回源。
4. database 前設 admission control；超過安全 QPS 時快速拒絕部分 miss，不排出無限長 queue。
5. 對近期曾成功 cache 的 ACTIVE link，可在明確 bounded stale policy 下暫時 serve stale；對 `DISABLED`、過期與安全敏感狀態不可反向復活。
6. cache fleet 回復時逐步導入流量並預熱，不把 100% request 一次灌入 cold nodes。

這裡最難的 trade-off 是：redirect 服務能不能在權威 store 暫時不可用時繼續使用 stale destination？

如果 link 建立後 immutable，而且 disable 最慢允許 30 秒生效，答案可以是「有限度地可以」。若該 cache entry 的 hard TTL 未超過 30 秒，服務權威 store 故障時仍回 redirect，availability 會高很多。但如果業務要求 abuse takedown 立即生效，stale serving 就與安全不變量衝突。此時寧可讓部分 redirect 失敗，也不能把已停用的惡意連結重新放出來。

所以「可不可以 serve stale」要由產品狀態語義決定，cache 技術本身給不出答案。

故障當下，持久庫中的連結仍完整，shared cache 的內容消失，各節點 L1 則保留不同子集。熱門連結可能繼續成功，首次或冷門點擊可能得到快速的 503；不能把容量拒絕偽裝成 slug 不存在的 404。偵測依據是 miss QPS 突增、回源併發與資料庫延遲，而非只等 cache 健康檢查失敗。恢復後先放少量 refill、確認命中率和回源延遲，再增加准入；若後端只能安全承受 5,000 QPS，200,000 QPS 全 miss 時最多只能放行約 2.5% 的未合併查詢，剩餘需求要由 L1、合併、有限 stale 或明確拒絕承擔。

## 如果連結永久不變，CDN 能接走多少責任

如果需求改成永久公開連結、不允許撤銷，讀取可以走另一條更便宜的路。

若所有短網址都是永久、不可修改，而且不需要 origin 觀察每次 click，那麼 `301` 加長 TTL CDN cache 是非常強的設計。大量熱門 redirect 甚至不會進入自己的機房。

但這個最佳化有三個代價。

第一，RFC 9110 明確說 301 代表 permanent URI，future references 應改用新 URI，而且 301 本身可以 heuristic cache。這會讓目的地變更或撤銷更難快速生效。

第二，origin 不再看到每一次 redirect。click analytics 必須改由 CDN/edge logs 取得，不能假設 application request count 就是使用量。

第三，cache purge 變成 control plane 的一部分。只要產品允許停用，edge cache 就必須有 bounded TTL 或可靠 purge；否則「資料庫已 disabled」與「全球 client 仍繼續 redirect」可以同時為真。

因此 HTTP status 不宜當成純粹的效能選項，它同時決定了誰掌握未來 redirect 的控制權。基線設計用 `302`，並透過 [RFC 9111：HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html) 定義的明確 freshness / Cache-Control 控制允許的 edge caching；若之後推出確定 immutable 的 link，才提供可長期快取的 permanent mode。

click event 也不應成為 redirect correctness 的同步依賴。redirect 成功後可以把 event 寫入 local buffer 或非同步 pipeline；analytics pipeline 壅塞時允許 drop、sample 或延後，不該讓使用者因為計數服務故障而無法跳轉。等到需要精確事件語義時，再處理 durable queue 與 consumer offset；第一版不必把所有副作用塞進 redirect transaction。

## 資料增長後，如何維持建立交易的原子性

快取降低讀取壓力，卻沒有消除每年資料與索引的增長。只有當權威庫的容量量測接近界線，才需要把寫入 ownership 拆開。

這個資料模型天然以 `slug` 做 point read，因此長期若必須 sharding，`hash(slug)` 是很直接的 partition key。random slug 本身分布均勻，能避免以 user ID 或建立時間分片帶來的寫入熱點。

但建立 API 還有另一個 access pattern：依 `(tenant_id, idempotency_key)` 查重。若把 links 只依 `hash(slug)` 分片，idempotency lookup 就不能靠 slug 定位。最乾淨的做法是把 idempotency record 做成另一個小型權威表，依 `hash(tenant_id, idempotency_key)` 分區；transactional creation 如果跨兩個獨立 shard，就會重新引入 distributed transaction 問題。

所以不該過早 sharding。第一階段把 `links` 與 `idempotency` 留在同一個可交易的資料庫，先拿到最簡潔的原子性。只有當單一 writer、索引大小、IOPS 或 storage growth 實際接近界線，再考慮：

- 預先配置 slug 所屬 shard，讓 idempotency 與 link 建立路由到同一 authority；
- 或把「建立 request」先變成一筆 durable intent，再非同步配置 link；
- 或接受跨 shard transaction 的協調成本。

這些方案都比「上來就用分散式 KV」昂貴。判斷何時引入，要看哪個複雜度已經被需求逼出來，元件數本身說明不了什麼。

## 公開轉址入口需要哪些安全限制

短網址天然會把實際目的地藏在可信任網域後面。OWASP 的 [Unvalidated Redirects and Forwards Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html) 指出，攻擊者可以利用可信任 host 包裝惡意目的地，增加 phishing 成功率。短網址本來就允許使用者提供 destination，因此「完全禁止外部 redirect」不是可行答案，必須把 abuse control 當成產品能力。

建立時至少要：

- 僅允許明確支援的 scheme，例如 `https` 與必要時的 `http`；
- canonicalize URL 後再做 policy check，避免不同 encoding 繞過規則；
- 保存 owner/tenant 與 audit metadata；
- 讓 link 有可快速切換的 `DISABLED` 狀態；
- 對建立 API 做 tenant-level rate limit，避免大量產生 spam links；
- 若另有 crawler/preview/scanner 會主動抓取 destination，該元件必須與 redirect data path 隔離，並另外防 SSRF；redirect server 本身不需要為了跳轉去 fetch 目的站。

安全要求再次回到 cache consistency：如果 `DISABLED` 是 abuse response，invalidation lag 就從「資料新不新」變成 security SLO，所以我不接受無界 stale cache。

## 上線要驗證偏斜、失效與回滾容量

這個服務上線前，我會把測試重點放在幾個分布，不只跑均勻 random load。

Zipf hot-key load。  
讓前 0.1% slug 吃掉 30%–50% redirect，觀察單一 cache shard、單一 app node 的 queue、CPU、NIC、lock contention。平均 QPS 綠色不代表 hot partition 沒有崩。

cold-cache impulse。  
在 200k QPS 下清掉 shared cache，觀察 database admission control 能否把回源壓在安全範圍，不是等 connection pool 自己爆掉。Google SRE 對 cascading failure 的建議是：元件超過能力時應 fail early / shed load，避免資源耗盡後整體 throughput 反而下降。

lost response after commit。  
刻意在 transaction commit 後、HTTP response 前斷線，確認 client retry 仍拿回相同 slug；同一 idempotency key 改 request body 時必須拒絕。

invalidation race。  
讓 reader 在讀到舊 DB value 後暫停；另一條 thread 執行 disable + invalidate；再恢復 reader，確認舊 refill 被 generation/lease 拒絕。這個測試比「cache delete 成功」重要得多。

dependency brownout。  
讓 database latency 從 5 ms 漸進增加到 500 ms。確認 in-flight request 有上限、timeout 小於 caller deadline、retry 有 budget，不會因 timeout → retry → 更多 timeout 形成正回饋。Google SRE 對 retry amplification 的例子甚至指出，多層各自重試會乘法放大最下游嘗試次數；在 overload 時，重試本身就可能成為故障放大器。[Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/)

服務日常最值得看的 SLI 也因此很具體：valid slug redirect success rate、p50/p99 redirect latency、L1/shared cache hit ratio、database lookup QPS、top hot-key share、cache refill coalescing ratio、idempotency replay rate、slug collision retry rate、invalidation propagation lag，以及 cache cold-start 時的 backend saturation。不要用「CPU 還有 40%」取代這些語義層指標。

導入快取時先保留全走資料庫的既有讀路徑，影子查詢比較 slug、狀態與版本，再逐步提高快取流量；監看錯誤跳轉與停用延遲，不能只看 hit ratio。回滾若要繞過快取，入口也必須同時降低准入量，否則會重演 cold-cache 故障。資料分片遷移則要維持每個 slug 的單一寫入 owner，在複製與切換期間保留路由版本與 tombstone；舊分區未隔離前，不讓兩邊同時接受建立或停用。

## 回到分享、重試與撤銷的承諾

回到最初的分享需求：交易型權威狀態與永久占用的 slug 保存連結身分，原子請求記錄讓建立重試得到同一資源。讀取以 L1、shared cache 降低熱門流量的成本，generation 擋住失效後的舊回填，剩餘 freshness 與到期判斷限制失效窗口。即使傳遞失效事件失敗，既有連結也不會無限期維持 ACTIVE。

這個方案仍有明確界線。快取全失效時會拒絕部分點擊；已送出的轉址不能撤回；單區域權威庫接手必須守住已確認交易。若停用要求改為確認後立即生效，每次跳轉就需要經過能看到最新狀態的判定邊界，或把停用確認延後到所有可服務的快取 owner 都完成切換。這會把可用性與協調成本放回讀取路徑，不能只縮短 TTL 宣稱滿足。

下一個問題來自建立端：當許多資料分區都需要取號，卻不能共同依賴每筆建立交易的唯一索引時，誰有權分配數字？[全域 ID 服務](/networking/2026/09/28/distributed-id-range-clock-worker-ownership.html)接著處理號段、時鐘與節點接手的邊界。

## References

1. [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html) — IETF, 2022.
2. [Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) — Amazon Builders' Library.
3. [Caching challenges and strategies](https://aws.amazon.com/builders-library/caching-challenges-and-strategies/) — Amazon Builders' Library.
4. [Scaling Memcache at Facebook](https://www.usenix.org/conference/nsdi13/technical-sessions/presentation/nishtala) — Rajesh Nishtala et al., NSDI 2013.
5. [Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/) — Google SRE.
6. [Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) — Google SRE.
7. [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html) — IETF, 2022.
8. [Unvalidated Redirects and Forwards Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html) — OWASP.

