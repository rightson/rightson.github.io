---
layout: post
title: "短網址真正難的不是 Base62：唯一鍵、重試與熱點才決定系統會不會失控"
date: 2026-09-24 08:28:05 +0800
domain: distributed-systems
categories: networking
description: "從一個讀多寫少的短網址服務，推導唯一鍵、冪等建立、redirect cache 與熱點失效；重點不是用哪個資料庫，而是誰對唯一性與可見狀態負責。"
series: distributed-systems
series_order: 1
---

短網址看起來幾乎沒有系統設計難度：存一筆 `slug → destination`，收到 `GET /slug` 後查表，再回一個 redirect。真正開始放大後，問題卻很快從「查一筆 key-value」變成三個完全不同的責任：誰保證 slug 永遠不會指向兩個目的地、誰保證建立請求重送十次仍只有一個結果，以及 cache 故障時誰有能力阻止幾十倍的回源流量把資料庫一起拖垮。

這三件事不能交給同一個「高可用資料庫」模糊處理。唯一性需要一個權威寫入邊界；重試需要把「同一個意圖」變成可辨認的狀態；低延遲則必須允許大量讀取停留在非權威 cache。系統越大，越需要刻意把 correctness 與 acceleration 拆開。

以下設計不是某個既有產品的公開架構，而是一個帶明確假設的工程模型。目標是看清楚：什麼狀態必須強一致，什麼狀態可以丟，什麼流量可以降級，以及一個看似單純的 redirect 如何演變成典型的分散式系統問題。

## 先把服務邊界縮到只剩兩件事

先假設服務只提供兩條主要路徑：

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

第一版先不做自訂網域、不做頁面預覽、不保證每次 click 都精確計數。目的地建立後預設不可修改，只允許 `ACTIVE → DISABLED` 或到期。這個限制看似保守，實際上省掉大量 cache consistency 複雜度；稍後再看如果產品要求可修改目的地，哪些設計必須跟著改。

最重要的兩個不變量是：

1. 同一個 `slug` 在任何時間都只能代表一筆權威 link record。
2. 同一租戶、同一 `Idempotency-Key` 的建立意圖，不管網路重試多少次，都只能得到同一筆 link；若相同 key 搭配不同參數，必須明確拒絕。

redirect 的 SLO 要高於建立連結。假設 redirect 可用性目標為 99.99%，建立 API 為 99.9%，因為讀路徑直接存在於使用者點擊鏈路，而建立失敗通常可以安全重試。Google SRE 將 availability 視為成功請求比例的一種 SLI，並提醒 99.99% 若換算成整體時間，每月只有約 4.3 分鐘不可用預算；對部分可用的服務，直接量「有效請求成功比例」通常比單純 outage 分鐘更有意義。[Google SRE：Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) 與 [Availability Table](https://sre.google/sre-book/availability-table/) 提供了這個量化框架。

![短網址的讀寫路徑](/images/distributed-systems/2026-09-24/short-url-read-write-path.svg)

*圖：作者設計；HTTP redirect 語義依據 [RFC 9110](https://www.rfc-editor.org/rfc/rfc9110.html)，cache-aside 與 cache failure 的操作風險參考 [AWS Builders' Library：Caching challenges and strategies](https://aws.amazon.com/builders-library/caching-challenges-and-strategies/)。*

## 數量級先決定哪些問題值得解

以下是**假設算例**，不是實際產品流量。

假設每天建立 2,000 萬條短網址，每天產生 20 億次 redirect。平均寫入約：

`20,000,000 / 86,400 ≈ 231 writes/s`

若尖峰是平均的 8 倍，大約 1,850 writes/s。

redirect 平均約：

`2,000,000,000 / 86,400 ≈ 23,148 reads/s`

若尖峰約 10 倍，就是 23 萬 reads/s。

這個比例先告訴我們一件事：第一個瓶頸大概率不是「建立連結的寫入吞吐」。幾千次每秒的寫入，即使放在具唯一索引與交易能力的單一主資料庫，也還有相當大的工程空間。真正會先把系統推向分散式的是讀流量、熱門 key，以及資料累積後索引工作集變大。

再估儲存。若每筆 link row 含目的 URL、slug、owner、建立時間、狀態、版本及必要索引，粗估 300 bytes：

`20M × 365 × 300 B ≈ 2.19 TB/year`

就算乘上三份複寫，再算索引與空間放大到原始資料的 1.5 倍，也大約是 10 TB/year 等級。它不是小數字，但也不是需要一開始就建立全球多主資料庫的理由。反過來說，若 99% redirect 都命中 cache，23 萬 QPS 的尖峰只留下約 2,300 QPS 回到權威儲存；若 cache fleet 同時失效，回源卻會瞬間放大到原本的 100 倍。**短網址的主要容量風險因此不是平均資料量，而是 cache mode switch。**

AWS Builders' Library 將這類情況描述得很精準：cache 一開始只是降低延遲與成本，久了下游容量會逐漸依賴 cache hit ratio；一旦 cold cache 或 cache fleet 故障，原本的加速層就變成容量相依。[Caching challenges and strategies](https://aws.amazon.com/builders-library/caching-challenges-and-strategies/) 特別提醒，若沒有為 cache miss 模式保留足夠下游容量，cache 就不是單純 latency cache，而是 capacity cache。

這個分類會決定故障策略。若資料庫只能承受 5,000 QPS，而 redirect 平常是 200,000 QPS，那 cache 故障時「直接全部回源」根本不是降級，而是把局部故障轉成全站故障。

## slug 產生器只能提出候選，唯一索引才有權宣布成功

常見做法是 Base62，把 `[0-9A-Za-z]` 當成 62 個符號。7 字元空間是：

`62^7 ≈ 3.52 × 10^12`

8 字元則是：

`62^8 ≈ 2.18 × 10^14`

如果用隨機 7 字元 slug，很多設計會說「空間有 3.5 兆，碰撞幾乎不可能」。這句話少了使用量。

若系統累積 10 億個有效 slug，空間占用率約 `1e9 / 3.52e12 = 0.028%`。對下一次隨機產生而言，撞到既有值的機率也是約 0.028%，平均約每 3,500 次建立就會遇到一次 collision。這不是災難，但已經遠遠不是「永遠不會發生」。如果累積到 100 億條，單次 collision 機率就接近 0.28%。

真正可靠的設計因此不是把亂數位數拉到一個讓人心安的數字，而是：

1. generator 產生 candidate slug；
2. 權威資料庫對 `slug` 設唯一約束；
3. insert 若因 unique conflict 失敗，重新產生 candidate；
4. 只有 transaction commit 後，slug 才正式存在。

這裡資料庫 unique constraint 才是 uniqueness authority。亂數品質只影響 collision retry 的頻率與可猜測性，不負責 correctness。

另一條路是取單調遞增 ID 再做 Base62。優點是沒有 collision retry，而且 slug 可以很短；缺點是直接暴露建立量與順序，也把 ID allocation 變成跨節點協調問題。可以使用區段預配、時間型 ID 或其他方法降低中央 allocator 壓力，但那其實已經進入下一層問題。這篇的建立 QPS 不高，因此我會先選「足夠大的 random slug + unique constraint」，把複雜度留給真正需要它的地方。

自訂 alias 則完全不同。`/apple` 不是「隨機 collision」，而是資源競爭。它必須直接走唯一索引，失敗就回 `409 Conflict`；不能偷偷改成 `/apple1`，因為那改變了呼叫者的語意。

## 網路逾時最危險的地方，是你不知道剛才到底有沒有成功

建立 API 有一個典型失效序列：

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

真正重要的是：`idempotency` 記錄與 link 建立必須處在同一個原子提交邊界。不能先 insert link，稍後「best effort」補 idempotency row；也不能先記 key，再另外建立 link。AWS 在 [Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) 強調了同一件事：辨認 request token 與執行 mutation 的狀態必須具有 all-or-nothing 性質，否則服務仍會掉進「資源建立成功但 token 沒記到」或相反的裂縫。

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

同一個 key 如果被兩台 server 同時處理，應由 `(tenant_id, idempotency_key)` unique constraint 決定唯一 winner。loser 重新讀取已提交結果並回相同語義，而不是靠 process-local lock。這就是「狀態擁有者」的重要性：application mutex 只在單一 process 內有效；資料庫約束才看得到所有 writer。

idempotency record 要保留多久，則是 API contract。若只保留 24 小時，代表 24 小時後的相同 key 可以被當成新 intent；若希望同一 key 永遠代表同一資源，就必須把這個綁定保存得和 link 一樣久。不能一邊承諾永久冪等，一邊讓 dedup table 每天清空。

還有一個容易忽略的情況：同一個 idempotency key，第二次 request 換了 URL。這不能直接回第一次結果，否則 caller 會以為新參數生效。最安全的契約是保存 canonicalized request hash；key 相同但內容不同就回 validation error。AWS 的文章也明確討論了這種「same request ID, different intent」。

## redirect path 的第一原則：cache 可以消失，權威狀態不能倒過來依賴它

讀取最簡單的路徑是 cache-aside：

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

cache eviction 不影響 correctness，只影響 latency 與下游 load。這個界線非常重要。Facebook 在 NSDI 2013 的 [Scaling Memcache at Facebook](https://www.usenix.org/conference/nsdi13/technical-sessions/presentation/nishtala) 也明確把 memcache 放在非權威位置：cache miss 回到持久層；write 先修改 database，再刪除 stale cache。論文同時顯示，cache 一旦被用在極大規模，真正困難的不是 hash table，而是 stale set、thundering herd 與故障時回源行為。

對不存在的 slug 也要做短時間 negative caching。公開短網址空間一定會被 crawler、scanner、拼字錯誤與惡意 enumeration 掃描。若每個 404 都打資料庫，一個簡單的 random scan 就能繞過 positive cache。negative cache 例如 5–30 秒，不需要長；它的目的不是把不存在狀態永久記住，而是把短時間重複 miss 擋在持久層前面。

但 cache hit ratio 不能只看整體平均。假設有一個熱門 slug 突然收到 80,000 QPS，其他流量合計 120,000 QPS。如果 shared cache 以 `hash(slug)` 單點路由，那這個 key 可能把單一 cache shard 打滿，即使整體 fleet CPU 只用 20%。Facebook 的論文就記錄過單一 key 可能占一台 memcached server 約 20% 的請求，並指出故障後若單純把 key 重新 hash 到剩餘節點，會把 hot key 壓力轉嫁給另一台 server，形成連鎖風險。

因此短網址特別適合兩層 cache：

- 每個 redirect process 先有小型 L1 cache，把極熱門 slug 複製到所有服務節點，主動利用 replication 分散 hot-key read。
- shared cache 負責較大 working set，降低 database QPS。
- L1 TTL 短，例如數秒到數十秒；shared cache 可以較長，但失效必須受控。
- 不存在 key 也進短 TTL negative cache。

這個做法犧牲了一點記憶體效率，卻把「一個 key 對應一個 cache owner」改成「越熱門的 key 越自然複製到更多 redirect process」。對 read-heavy redirect 服務，這通常比追求完美 cache memory utilization 更重要。

## cache invalidation 真正的 bug 不是忘了 delete，而是 delete 之後舊資料又被塞回來

假設一個連結因 abuse 被停用。寫入流程如果只是：

1. database 將 `status=DISABLED`；
2. delete cache key；

看似合理，仍有一個競態。

在更新前，reader A cache miss，去 database 讀到舊的 `ACTIVE`。接著管理者把 database 改成 `DISABLED` 並 delete cache。最後 reader A 才把剛才讀到的舊 `ACTIVE` 寫回 cache。結果是「invalidate 成功之後，舊資料復活」。

這就是 stale set。Nishtala 等人在 Facebook 的 memcache 設計中使用 lease：cache miss 時只讓持有特定 token 的 client 回填；如果期間發生 delete，lease 被 invalidated，舊 reader 即使晚到也無法再把 stale value 寫回。論文也用 lease 抑制 thundering herd，對同一 key 控制能取得 refill token 的 client；在其公開測量中，一組容易 herd 的 key，其 cache miss 導致的 peak database query rate 從 17K/s 降到 1.3K/s。[Scaling Memcache at Facebook](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170.pdf)

短網址不一定要複製 Facebook 的完整實作，但必須解決同一個時序問題。可採三種層級：

**方案 A：短 TTL，接受有界 stale。**  
最簡單。L1 只 cache 5 秒，shared cache 30 秒。停用後最差 30 秒仍可能 redirect。若產品容許，這是最低成本解。

**方案 B：invalidation + refill lease/fencing。**  
cache miss 取得 refill token；disable/update 會推進該 key 的 generation，使舊 token 失效。舊 reader 無法在 invalidation 後重新填入舊資料。這能把 stale window 壓到 event propagation 與正在執行請求的邊界。

**方案 C：每次 redirect 都查權威狀態。**  
correctness 最直觀，卻幾乎放棄 cache 的容量價值。除非停用即時性是絕對要求，而且流量很小，否則這不是合理預設。

我的選擇是 B 作為 shared cache 的 correctness boundary，加上短 L1 TTL。對安全停用事件，再主動 broadcast L1 invalidation。如此即使某節點漏掉事件，TTL 仍提供最終上限；若整個 invalidation bus 故障，也不會永久把 stale state 留住。

![停用與 stale refill 的競態](/images/distributed-systems/2026-09-24/short-url-stale-refill.svg)

*圖：作者設計；stale set 與 lease 機制依據 Rajesh Nishtala 等人於 NSDI 2013 發表的 [Scaling Memcache at Facebook](https://www.usenix.org/system/files/conference/nsdi13/nsdi13-final170.pdf) 整理。*

## cold cache 不是「變慢」，而是另一種負載模型

再看第二個故障。

正常尖峰 200,000 redirect QPS，整體 cache hit ratio 99%，database 約 2,000 QPS。某次 shared cache fleet 因設定錯誤全部 restart。若所有 redirect server 立即把 miss 送到 database，後端負載瞬間變成 200,000 QPS。

這不是普通的 1% latency regression，而是服務模式從「99% RAM lookup」切換成「100% persistent lookup」。Google SRE 在 [Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/) 特別指出，cold cache 會讓原本便宜的請求突然變昂貴；若服務容量是按 warm-cache 狀態規劃，重新啟動本身就可能造成 outage。AWS 也建議對 miss 使用 request coalescing，避免同一 uncached resource 同時發出大量下游請求。

所以恢復策略不能是「讓所有 miss 自由回源」：

1. L1 cache 即使 shared cache 重啟仍保留一部分熱門 key。
2. 同一 process 對相同 slug 的 concurrent miss 做 singleflight/request coalescing。
3. shared cache refill 也用 lease，讓同一 key 只有少數 request 回源。
4. database 前設 admission control；超過安全 QPS 時，不是排出無限長 queue，而是快速拒絕部分 miss。
5. 對近期曾成功 cache 的 ACTIVE link，可在明確 bounded stale policy 下暫時 serve stale；對 `DISABLED`、過期與安全敏感狀態不可反向復活。
6. cache fleet 回復時逐步導入流量並預熱，不把 100% request 一次灌入 cold nodes。

這裡最難的 trade-off 是：redirect 服務能不能在權威 store 暫時不可用時繼續使用 stale destination？

如果 link 建立後 immutable，而且 disable 最慢允許 30 秒生效，答案可以是「有限度地可以」。若該 cache entry 的 hard TTL 未超過 30 秒，服務權威 store 故障時仍回 redirect，availability 會高很多。但如果業務要求 abuse takedown 立即生效，stale serving 就與安全不變量衝突。此時寧可讓部分 redirect 失敗，也不能把已停用的惡意連結重新放出來。

所以「可不可以 serve stale」不是 cache 技術問題，而是產品狀態語義問題。

## 301、302 與 CDN：省掉 origin QPS，也可能省掉你的控制權

若所有短網址都是永久、不可修改，而且不需要 origin 觀察每次 click，那麼 `301` 加長 TTL CDN cache 是非常強的設計。大量熱門 redirect 甚至不會進入自己的機房。

但這個優化有三個代價。

第一，RFC 9110 明確說 301 代表 permanent URI，future references 應改用新 URI，而且 301 本身可以 heuristic cache。這會讓目的地變更或撤銷更難快速生效。

第二，origin 不再看到每一次 redirect。click analytics 必須改由 CDN/edge logs 取得，不能假設 application request count 就是使用量。

第三，cache purge 變成 control plane 的一部分。只要產品允許停用，edge cache 就必須有 bounded TTL 或可靠 purge；否則「資料庫已 disabled」與「全球 client 仍繼續 redirect」可以同時為真。

因此我不會用 HTTP status 當純粹效能選項。它其實在決定「誰掌握未來 redirect 的控制權」。基線設計用 `302`，並透過 [RFC 9111：HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html) 定義的明確 freshness / Cache-Control 控制允許的 edge caching；若之後推出真正 immutable link，才提供可長期快取的 permanent mode。

click event 也不應成為 redirect correctness 的同步依賴。redirect 成功後可以把 event 寫入 local buffer 或非同步 pipeline；analytics pipeline 壅塞時允許 drop、sample 或延後，不該讓使用者因為計數服務故障而無法跳轉。等到需要精確事件語義時，再處理 durable queue 與 consumer offset，而不是在第一版把所有副作用塞進 redirect transaction。

## expiry 與 delete 不能只靠 TTL，因為「不存在」也有語義

短網址還有一個容易被忽略的狀態：`EXPIRED`、`DISABLED` 與真正的 `NOT_FOUND` 不能全部壓成同一個 cache miss。

如果一筆 link 到期後直接從 database hard delete，後續 request 看到 404，看起來很乾淨；但這會失去幾個重要能力：無法判斷 slug 是否曾經被使用、無法阻止舊 slug 被重新分配給另一個目的地，也無法在 abuse investigation 或 audit 時追溯曾經存在的狀態。更危險的是，如果 slug 可以被回收，舊 email、QR code 或瀏覽器歷史中的同一短網址，幾個月後可能突然指向完全不同的網站。這不是 storage cleanup，而是 identifier reuse 改變了外部契約。

因此基線設計把 slug 視為永久占用的 namespace。record 可進入：

`ACTIVE → DISABLED`  
`ACTIVE → EXPIRED`

但不把 slug 重新配置給其他 destination。payload 可以在 retention policy 到期後縮成 tombstone，只保留 slug、final state、必要 audit metadata。RFC 9110 對 `410 Gone` 的語義是「資源已經有意永久不可用」；如果產品希望明確區分「從沒存在」與「曾存在但已移除」，可以讓 `NOT_FOUND → 404`、`DISABLED/EXPIRED tombstone → 410`，但這屬於對外 API 契約，不能因為清資料方便就臨時改動。

這也改變 negative cache。404 可以短暫 cache，例如 10 秒，用來吸收 scanner；410 tombstone 卻可以 cache 更久，因為它已是權威終態。兩者都不是「查不到所以一樣」。一旦狀態有語義，cache key/value 就必須保留足以做正確判斷的資訊。

如果未來法規或隱私要求必須刪除 destination 本文，也可以保留不可逆 tombstone：slug digest、狀態與時間，而不是保留完整 URL。這讓「不可重新使用 identifier」與「刪除敏感內容」可以同時成立。

## 可用性不是讓所有元件都變成四個九，而是知道哪條路徑必須活著

redirect 與 create 的 failure domain 不需要完全相同。建立服務掛掉 10 分鐘，既有短網址仍應該能跳轉；analytics pipeline 掛掉，不應該拖垮 redirect；管理介面掛掉，也不代表 data plane 要停止服務。

因此我會把服務切成三種責任，而不是單純拆微服務：

- **redirect data plane**：只做 slug lookup、狀態判斷與 HTTP redirect，依賴 L1/shared cache 與權威 read path。
- **mutation control plane**：create、disable、expiry management，負責唯一性、idempotency 與 invalidation。
- **telemetry path**：click/event 記錄，允許延後、sample 或降級。

這三條路徑可以一開始仍部署在同一個 binary，重點不是 process 數量，而是資源與失效依賴不能反向耦合。例如 analytics queue full 時，不允許 redirect thread block；create database connection pool 飽和，也不能吃光 redirect 的 connection/CPU budget。

同理，資料庫 replica 的角色也要清楚。若 redirect 允許讀 replica，replication lag 就會變成 correctness 的一部分：新建立的 slug 可能在 create 成功後短時間 404，剛停用的 link 也可能在 replica 仍顯示 ACTIVE。若產品要求 create 成功後立即可用，最簡單的做法不是喊「read-after-write consistency」，而是讓新 link 在一小段時間內直接走 authority、或把 create 成功結果同步寫入 cache，並且為該 cache entry 設定明確版本。若停用要求更強，則不能讓 lagging replica 在 invalidation 後重新填舊資料。

因此 replica 並不是免費的 read scaling。每新增一條 read path，就要回答：它允許看到多舊的狀態？如果超過界線，誰能偵測並阻止它成為 cache refill source？這種問題比「有幾個 replica」更接近真正的可用性設計。

## partition key 其實已經藏在 API 裡

這個資料模型天然以 `slug` 做 point read，因此長期若必須 sharding，`hash(slug)` 是很直接的 partition key。random slug 本身分布均勻，能避免以 user ID 或建立時間分片帶來的寫入熱點。

但建立 API 還有另一個 access pattern：依 `(tenant_id, idempotency_key)` 查重。若把 links 只依 `hash(slug)` 分片，idempotency lookup 就不能靠 slug 定位。最乾淨的做法是把 idempotency record 做成另一個小型權威表，依 `hash(tenant_id, idempotency_key)` 分區；transactional creation 如果跨兩個獨立 shard，就會重新引入 distributed transaction 問題。

這也是為什麼不該過早 sharding。第一階段把 `links` 與 `idempotency` 留在同一個可交易的資料庫，先拿到最簡潔的原子性。只有當單一 writer、索引大小、IOPS 或 storage growth 真正接近界線，再考慮：

- 預先配置 slug 所屬 shard，讓 idempotency 與 link 建立路由到同一 authority；
- 或把「建立 request」先變成一筆 durable intent，再非同步配置 link；
- 或接受跨 shard transaction 的協調成本。

這些方案都比「上來就用分散式 KV」昂貴。分散式系統的成熟度不在元件數，而在是否知道哪個複雜度已經被需求逼出來。

## 第一次真正需要壓測的不是平均 QPS，而是偏斜與模式切換

這個服務上線前，我會把測試重點放在幾個分布，而不是只跑均勻 random load。

**Zipf hot-key load。**  
讓前 0.1% slug 吃掉 30%–50% redirect，觀察單一 cache shard、單一 app node 的 queue、CPU、NIC、lock contention。平均 QPS 綠色不代表 hot partition 沒有崩。

**cold-cache impulse。**  
在 200k QPS 下清掉 shared cache，觀察 database admission control 是否真的把回源壓在安全範圍，而不是等待 connection pool 自己爆掉。Google SRE 對 cascading failure 的建議很核心：元件超過能力時應 fail early / shed load，而不是讓資源耗盡後整體 throughput 反而下降。

**lost response after commit。**  
刻意在 transaction commit 後、HTTP response 前斷線，確認 client retry 仍拿回相同 slug；同一 idempotency key 改 request body 時必須拒絕。

**invalidation race。**  
讓 reader 在讀到舊 DB value 後暫停；另一條 thread 執行 disable + invalidate；再恢復 reader，確認舊 refill 被 generation/lease 拒絕。這個測試比「cache delete 成功」重要得多。

**dependency brownout。**  
讓 database latency 從 5 ms 漸進增加到 500 ms。確認 in-flight request 有上限、timeout 小於 caller deadline、retry 有 budget，不會因 timeout → retry → 更多 timeout 形成正回饋。Google SRE 對 retry amplification 的例子甚至指出，多層各自重試會乘法放大最下游嘗試次數；在 overload 時，重試本身就可能成為故障放大器。[Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/)

服務日常最值得看的 SLI 也因此很具體：valid slug redirect success rate、p50/p99 redirect latency、L1/shared cache hit ratio、database lookup QPS、top hot-key share、cache refill coalescing ratio、idempotency replay rate、slug collision retry rate、invalidation propagation lag，以及 cache cold-start 時的 backend saturation。不要用「CPU 還有 40%」取代這些語義層指標。

## 安全邊界不能因為服務只是 redirect 就省略

短網址天然會把真正目的地藏在可信任網域後面。OWASP 的 [Unvalidated Redirects and Forwards Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html) 指出，攻擊者可以利用可信任 host 包裝惡意目的地，增加 phishing 成功率。短網址本來就允許使用者提供 destination，因此「完全禁止外部 redirect」不是可行答案，必須把 abuse control 當成產品能力。

建立時至少要：

- 僅允許明確支援的 scheme，例如 `https` 與必要時的 `http`；
- canonicalize URL 後再做 policy check，避免不同 encoding 繞過規則；
- 保存 owner/tenant 與 audit metadata；
- 讓 link 有可快速切換的 `DISABLED` 狀態；
- 對建立 API 做 tenant-level rate limit，避免大量產生 spam links；
- 若另有 crawler/preview/scanner 會主動抓取 destination，該元件必須與 redirect data path 隔離，並另外防 SSRF；redirect server 本身不需要為了跳轉去 fetch 目的站。

安全要求再次回到 cache consistency：如果 `DISABLED` 是 abuse response，invalidation lag 就不是單純「資料新不新」，而是 security SLO。這也是我不接受無界 stale cache 的原因。

## 什麼時候應該換掉這個設計

目前的基線是：單一交易型 authority + random slug unique constraint + 原子 idempotency record + L1/shared cache + bounded stale + refill fencing。它刻意沒有做 multi-region active-active。

有三種條件會迫使架構改變。

第一，建立量提升到單一 writer 或 index maintenance 已成為明確瓶頸。此時才值得把 ID allocation 與 write ownership 分散出去；random collision 不再是主要問題，跨 shard uniqueness 與 request routing 才是。

第二，全球 redirect latency 要求進一步壓低，而且單區域 outage 不能影響既有 link。這會把權威資料複寫、edge state、停用傳播與 region failover 拉進來。讀取可以多區，寫入 authority 是否也多區則是另一個更昂貴的決定。

第三，產品要求「目的地可立即修改且全球秒級一致」。這會直接破壞目前用 TTL 吸收 stale 的簡單模型。cache version、invalidation ordering、edge purge 與寫後讀一致性都必須升級；如果還同時要求永久 redirect cache，就會出現語義衝突。

短網址之所以適合作為第一個完整系統，不是因為它簡單，而是因為它把很多重要邊界暴露得非常乾淨：ID generator 不等於 uniqueness authority，retry 不等於再次執行，cache 不等於資料庫副本，平均 QPS 不等於最壞負載，HTTP status 也不只是回應碼。

下一個自然問題是：當「產生唯一 ID」本身也不能再依賴單一資料庫時，誰有權分配數字？如果多台 worker 同時發 ID、時鐘會倒退、process 會重啟，又要怎麼證明永遠不重複？這會把我們帶到分散式 ID 服務。

## References

1. [RFC 9110: HTTP Semantics](https://www.rfc-editor.org/rfc/rfc9110.html) — IETF, 2022.
2. [Making retries safe with idempotent APIs](https://aws.amazon.com/builders-library/making-retries-safe-with-idempotent-APIs/) — Amazon Builders' Library.
3. [Caching challenges and strategies](https://aws.amazon.com/builders-library/caching-challenges-and-strategies/) — Amazon Builders' Library.
4. [Scaling Memcache at Facebook](https://www.usenix.org/conference/nsdi13/technical-sessions/presentation/nishtala) — Rajesh Nishtala et al., NSDI 2013.
5. [Addressing Cascading Failures](https://sre.google/sre-book/addressing-cascading-failures/) — Google SRE.
6. [Service Level Objectives](https://sre.google/sre-book/service-level-objectives/) — Google SRE.
7. [RFC 9111: HTTP Caching](https://www.rfc-editor.org/rfc/rfc9111.html) — IETF, 2022.
8. [Unvalidated Redirects and Forwards Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html) — OWASP.
