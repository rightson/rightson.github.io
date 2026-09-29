---
layout: post
title: "Kubernetes 為什麼不把『執行成功』當成正確性：Reconciliation Loop 如何把故障變成可重試的狀態差"
date: 2026-09-23 08:05:00 +0800
domain: distributed-systems
categories: eda
description: "Kubernetes 把 correctness 定義成 desired state 與 observable state 的差距，並持續重新計算下一個動作。這篇從 level-triggered control、list/watch、resourceVersion、Reflector、workqueue、idempotency，一路推到 EDA/HPC control plane 應如何設計。"
---

很多自動化系統都建立在一個很直覺的假設上：只要把步驟照順序執行完，而且每一步都回傳成功，系統就正確。

在一台機器、幾十個步驟、幾分鐘完成的 script 裡，這通常夠用；但當系統變成幾千台 node、幾十萬個 object、controller 隨時可能重啟、網路可能 partition、外部 storage 或 scheduler 回應延遲，而且工作可能持續數小時到數天時，「曾經執行成功」與「現在仍然正確」就會分離。

假設一個 flow 做了四件事：建立 compute resource、掛載 volume、送出 job、最後寫入完成狀態。第三步完成後 process crash，第四步沒有執行。系統重新啟動時，應該從哪裡接？如果只是重播 script，可能重複建 volume、重複 submit job；如果選擇跳過，又可能漏掉實際未完成的工作。再進一步，如果 job 當下成功，但一小時後 node 掛掉，過去的 success code 對現在的 correctness 幾乎沒有意義。

Kubernetes 沒有把力氣放在「讓每個 command 更可靠」，而是改寫 correctness 的定義：系統正不正確，由現在觀察到的狀態是否接近期望狀態決定，與過去做過什麼無關。

Reconciliation loop 就是圍繞這個定義建立的機制。

<figure>
  <img src="/assets/images/k8s/reconcile-command-vs-state.svg" alt="imperative command sequence 與 desired-state reconciliation 的差異" style="max-width:100%;height:auto;">
  <figcaption>圖 1｜Imperative automation 把正確性寄託在過去的 command sequence；reconciliation 則反覆比較 desired state 與 observed state。依據 <a href="https://kubernetes.io/docs/concepts/architecture/controller/">Kubernetes Controllers</a> 與 <a href="https://kubernetes.io/docs/concepts/overview/working-with-objects/">Kubernetes Objects: spec/status</a> 重繪整理。</figcaption>
</figure>

## 當環境會持續改變，command history 就不再是 source of truth

先把問題縮到最基本。

如果一個系統完全不會被外界改變，執行一次命令就足夠。你建立四個 process，只要命令成功，四個 process 就永遠存在；那麼「做過什麼」與「現在是什麼」幾乎等價。

真實 distributed system 恰好相反。node 會失效、process 會 crash、operator 會手動修改資源、network 會 timeout、cloud API 可能回傳 ambiguous result、storage attachment 可能卡在中間狀態。系統很少從 A 到 B 一次性前進，更常見的是在外部擾動下持續偏離目標。

因此，一個可以長時間維持 correctness 的 control plane，至少需要三種性質：

1. 目標必須被持久保存。controller crash 之後，不能靠記憶知道原本想做什麼。
2. 現況必須能重新觀察。不能假設上一次 action 的結果仍然成立。
3. 下一步必須能從「目標與現況」重新推導。不能依賴完整 command history 才知道接下來做什麼。

Kubernetes object 的 `spec` / `status` 分離正好對應這個需求。官方文件把 `spec` 描述為希望系統達到的 desired state，而 `status` 由系統元件更新，描述目前觀察到的狀態；control plane 持續讓 actual state 接近 desired state。[Kubernetes Objects](https://kubernetes.io/docs/concepts/overview/working-with-objects/)

這種分離來自 fault model 的需求，與 YAML 語法習慣無關。

假設某個自訂 EDA Run object 長這樣：

```yaml
apiVersion: r2g.example.com/v1
kind: AprRun
spec:
  design: top_a
  netlistDigest: sha256:...
  sdcDigest: sha256:...
  tool: innovus-26.1
  backend: lsf
  resources:
    cpu: 32
    memory: 256Gi
status:
  phase: Running
  backendJobId: "8451932"
  artifactDigest: ""
```

這裡要看的是語義：即使 controller process 完全消失再重啟，它仍然可以只靠 API 中的 spec/status，加上對 LSF 與 artifact store 的重新觀察，推導「現在還缺什麼」。

如果 `spec` 還存在，但 LSF job 已不存在，而且也沒有有效 artifact，下一步可能是重送；如果 LSF job 還在，controller 不應該因為自己忘記 history 就重新 submit；如果 artifact 已完成，只是 status 還沒更新，正確動作應該是補寫 status，而不是重跑 APR。

把 intent 與 execution history 分開，是讓 controller 可被殺掉、重啟、升級的前提。

## Event 只能提醒你「可能變了」，不能代表真相

接著會出現第二個問題：既然 controller 必須反覆比較 desired/current state，難道每秒把整個 cluster 全掃一次？

小系統可以，大系統很快就不行。

假設有 200,000 個 Pod，50 個 controller，每個 controller 每秒 `LIST` 一次全部 object。即使每個 object 平均只有 2 KiB，粗略資料量就是：

`200,000 × 2 KiB × 50 ≈ 19 GiB/s`

這還沒計算 serialization、TLS、JSON/protobuf decode、etcd read、GC 與 API server CPU。大型 cluster 不可能靠高頻 full polling 維持反應速度。

所以 Kubernetes API 提供 list/watch。client 先取得一個一致的 object snapshot 與對應 `resourceVersion`，再從這個版本開始 watch 後續變化。官方 API Concepts 明確描述：watch 會回傳在指定 `resourceVersion` 之後發生的 create/update/delete 事件；連線中斷後可以從最後版本續接，歷史版本過舊時則可能收到 `410 Gone`，此時 client 必須重新 list 再建立 watch。[Kubernetes API Concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/)

但這裡有一個容易誤解的地方：**Kubernetes controller 不是典型 event-driven workflow engine。**

它雖然接收 event，correctness 卻不應依賴「每個 event 必須恰好收到一次」。event 的角色更像 interrupt：提醒 controller 某個 key 值得重新檢查。controller 做決策之前，仍然應讀取最新 state。

如果一個 Pod 先更新兩次，queue 裡最後只有一次 `namespace/name`，沒有問題，因為 reconcile 要處理的是「它現在長什麼樣子」，不是逐筆重播歷史事件。如果相同 event 重複進 queue，也不應改變最終結果。如果 controller crash 後錯過一段 event，只要重新 list/watch 能重建 state，correctness 仍可恢復。

Level-triggered control 與 edge-triggered workflow 的差別就在這裡。

<figure>
  <img src="/assets/images/k8s/reconcile-list-watch-queue.svg" alt="Kubernetes controller 的 list watch cache workqueue reconcile data path" style="max-width:100%;height:auto;">
  <figcaption>圖 2｜典型 controller data path：Reflector 透過 list/watch 建立 local cache，event 只把 key 放入 workqueue；worker 再依最新 state 執行 reconcile。依據 <a href="https://kubernetes.io/docs/reference/using-api/api-concepts/">Kubernetes API Concepts</a>、<a href="https://github.com/kubernetes/client-go">client-go</a> 與 client-go `tools/cache` / `util/workqueue` 設計重繪整理。</figcaption>
</figure>

## Reflector、cache、workqueue：把 failure 納入正常處理路徑

client-go 把這套 pattern 做成相當標準化的組件。

`Reflector` 負責 list/watch，把遠端 API state 投影到本地 cache；Informer 在 cache 變化時觸發 handler；handler 通常不直接做昂貴操作，而是把 object key 丟進 workqueue；worker 從 queue 取 key，再做 reconcile。

這個多一層 cache、再多一層 queue 的設計，看起來像額外複雜度，但它其實在解三種不同的時間尺度：

- API change stream 可能很快；
- controller 處理每個 object 的速度可能較慢；
- 外部系統 API 甚至可能需要數秒或數分鐘。

如果 event handler 直接同步呼叫 cloud API、LSF、storage 或 license system，任一外部延遲都會阻塞 event consumption，最終造成 watch backlog 或 controller 自己失去反應能力。queue 把「偵測到變化」與「實際處理」解耦，並提供去重、rate limit、retry/backoff。

client-go 的 rate-limiting workqueue 明確提供 `AddRateLimited()`，而官方 example 在成功同步後會 `Forget()` 過去的 rate-limit history；失敗則重新排入 queue。這是 controller failure model 的一部分：transient error 預期會發生，因此 retry 屬於正常 path，不算 exception path。[client-go workqueue source](https://github.com/kubernetes/client-go/blob/master/util/workqueue/rate_limiting_queue.go)｜[client-go workqueue example](https://github.com/kubernetes/client-go/blob/master/examples/workqueue/main.go)

假設一個 controller 同時管理 10,000 個 external volumes，其中 storage API 暫時有 2% request 失敗。如果沒有 per-key retry/backoff，很容易出現兩種極端：整個 controller 因單一 failure 停住，或所有 failure 立即 tight-loop retry，反過來把已經過載的 storage control plane 打死。

workqueue 除了排隊，也把每個 resource 的進度隔離，使 transient failure 可以局部重試，且錯誤率上升時自動降低 retry pressure。

## Idempotency 才讓「至少再做一次」比「保證只做一次」更實際

只要有 retry，就會撞上下一個問題：如果上一次 action 其實已成功，只是 controller 沒來得及記錄成功呢？

這是 distributed systems 裡最常見的 ambiguous outcome。

例如 controller 呼叫 storage API 建立一個 2 TiB volume：storage backend 已經建立完成，也回傳成功；但回應封包在途中遺失，或 controller 剛收到 response 就 crash，尚未寫回 Kubernetes status。重啟後 controller 只看到「spec 要 volume；status 不知道 volume 已存在」。

如果 reconcile 寫成：

```text
if status.volumeId == "":
    createVolume()
```

那麼 retry 可能再建立第二顆 volume。

更健壯的設計是：先用 stable identity 去 external system 查詢，例如用 Kubernetes object UID / deterministic external name；若已存在就 adopt，若不存在才 create。這讓重複 reconcile 變成安全操作。

controller 追求的是 **repeatable convergence**，不追求 exactly-once action。

因此「reconcile 可以被任意重跑」幾乎是 Kubernetes controller 的基本設計準則。你不需要證明某一個 event 從沒重複，也不需要持久化每一個中間 command；只要每次都能從當前 reality 重新推導安全的下一步，crash 就主要變成額外 latency，而不是 state corruption。

<figure>
  <img src="/assets/images/k8s/reconcile-failure-idempotency.svg" alt="controller 在 side effect 後 crash 時 idempotent retry 與重複建立的差異" style="max-width:100%;height:auto;">
  <figcaption>圖 3｜controller 最危險的時間點是 side effect 已成功、status 尚未持久化。Idempotent reconcile 透過重新觀察外部 state，把 ambiguous outcome 收斂回正確狀態。依據 <a href="https://kubernetes.io/docs/concepts/architecture/controller/">Kubernetes controller pattern</a> 與 client-go retry/workqueue 行為重繪整理。</figcaption>
</figure>

## 為什麼 reconcile 要重新讀 state，而不是相信 queue 裡的 event payload

如果 event 已經告訴 controller object 的內容，為什麼不直接用 event payload 做事？

因為 event 送達時，世界可能已經變了。

假設一個 Job resource 在短時間內被修改：

1. CPU request 從 8 改成 16；
2. 使用者立刻又改成 32；
3. controller worker 此時才取到第一個 update event。

如果 worker 把第一個 event 當成命令，就可能按照 16 CPU 配置外部資源；但 cluster 的 desired state 已經是 32。更糟的是，如果 event 處理順序因 retry 變化，舊 event 可能在新 event 之後執行，造成 state 倒退。

比較安全的做法是只把 key 放進 queue：`default/job-a`。實際 reconcile 時再從 informer cache 或 API 取得最新 object。於是多個快速 update 可以自然 collapse 成「處理一次最新狀態」。

所以很多 Kubernetes controller 的核心函式看起來都像：

```text
reconcile(key):
    obj = cache.get(key)
    if obj does not exist:
        cleanup if needed
        return
    observed = inspectExternalState(obj)
    diff = compare(obj.spec, observed)
    act(diff)
    updateStatus()
```

program state 存在於 **API object + external observable state**，queue event 只負責觸發。

這個差異對 EDA flow 特別重要。傳統 Makefile 或 flow script 常把「上一步已完成」存在某個 marker file、return code 或 run directory 中。這在單一 execution context 內很好用，但當同一個 project 被多個 user、agent、scheduler、retry path 共同操作時，implicit marker 很快會失去唯一性。

如果要建立 department-scale control plane，比較可行的方向是先把高階 state 變成 explicit、queryable、versioned object，不必把每個 Tcl step 都改成 Kubernetes Pod：

`Queued → Admitted → WaitingLicense → Running → Verifying → Completed / Failed`

然後讓每個 transition 都可以由 observable evidence 重新推導，而不是只有某支 script 知道自己跑到第幾行。

## Reconciliation 不等於 workflow：兩者處理的是不同問題

另一個常見誤區是：既然 reconciliation 這麼強，所有 workflow engine 都應該改成 controller。這個推論不成立。

Workflow 描述的是因果順序：A 成功後做 B，B 的輸出成為 C 的輸入。Temporal、Argo Workflows、Airflow、Makefile、EDA flow graph 都在解「工作如何按 dependency 前進」。

Reconciliation 解的是另一件事：**不管過去發生過什麼，現在距離希望維持的狀態還差多少？**

對一個一次性的 `make` build，完整 DAG 很重要；對「cluster 永遠必須有三個 API server」而言，你不需要重播三年前建立 API server 的 workflow，只需要持續確保三個仍存在。

大型平台通常兩者都需要。

以 synthesis → APR → STA 為例，stage dependency 本身適合 workflow semantics；但「APR run 已被承諾、所需 license/resource 已配置、artifact 必須最終出現、失敗後可恢復」則適合 reconciliation。workflow engine 可以是 execution backend，controller 則管理高階 state contract。

這樣切割可以避免一個常見 platform mistake：拿一個 workflow engine 來假裝是整個 control plane，最後所有外部 drift、retry、manual intervention、resource lifecycle 都只能塞成更多 workflow branch；或反過來，把 controller 當成 DAG engine，導致 sequence semantics 變得難以理解。

## Optimistic concurrency：以 version conflict 取代長時間 lock

當多個 controller 或 user 可以同時修改 object，還會出現並行更新問題。

Kubernetes object 的 `resourceVersion` 不只支援 watch，也用於 concurrency control。簡化來說，你讀到 version 100，準備更新；如果另一個 actor 已先把 object 更新成 101，你基於舊版本提交的 update 可能收到 conflict。正確做法是重新讀取、重新計算，再 retry；不能假設「我剛剛讀過，所以我擁有它」。[Kubernetes API Concepts](https://kubernetes.io/docs/reference/using-api/api-concepts/)

這是一種 optimistic concurrency 思維：通常不持有長時間 distributed lock，而是在 commit 時確認基礎 state 是否仍然有效。

這與 reconciliation 非常相容。因為 reconcile 本來就必須能重算，所以 conflict 只代表「你的 observation 過時了」，不是災難。

在大型 EDA control plane 裡，同樣可以借用這個思路。Project lead 改 priority、resource manager 改 queue policy、license controller 改 admission status、execution controller 更新 backend job ID，如果所有元件都共享一個大 lock，可靠性與 throughput 很快受限。更好的模式通常是讓 ownership boundary 清楚、status field 可分工，再用 version conflict/retry 保護更新。

## Controller 本身的負載：retry storm 與 API Priority and Fairness

一旦大量 controller 都透過 API server 讀寫 state，新的瓶頸會出現：control plane 本身可能被自己的 automation 打垮。

想像 1,000 個 controller instance 因 API server 短暫變慢同時 timeout，然後一起立即 retry。這就是 retry storm。原本只是 2 秒 latency spike，最後可能被放大成持續 overload。

因此 backoff 是 stability mechanism，不只是 courtesy；API server 自己也需要 flow control。Kubernetes 的 API Priority and Fairness（APF）把 incoming request 分類到不同 priority level，限制 concurrency，並以 queue/fair queuing 防止單一 noisy client 餓死其他 control traffic。官方文件甚至把 leader-election、built-in controller、kubelet 等流量分成不同優先類型，目的就是避免過載時 control plane 失去自救能力。[API Priority and Fairness](https://kubernetes.io/docs/concepts/cluster-administration/flow-control/)

這裡形成一個遞迴結構：

- workload 需要 controller 幫它收斂；
- controller 自己依賴 API server；
- API server 也需要 admission/queueing/fairness 來控制 controller 的流量；
- 所以 control plane 不是沒有 queue，只是把 queue 明確放在正確的層。

這也預告下一篇為什麼要專門拆 kube-apiserver：它是整個分散式控制系統的語義入口、併發邊界與 overload boundary，遠超過「放 YAML 的 REST server」。

## 把 reconciliation 模型用在 AI / EDA / Foundry 的 control plane

如果只看 container execution，EDA 或 Foundry 很容易得出「Kubernetes 沒必要，LSF 已經跑得很好」的結論。這個判斷對 execution layer 可能完全正確。

但 control-plane 問題其實是另一層：

- 這個 run 的 desired result 是什麼？
- 哪個版本的 RTL/netlist/SDC/PDK/tool 構成它的 identity？
- 目前卡在 license、compute、storage 還是 flow dependency？
- backend job 不見了，應該重送還是等待？
- artifact 已經存在但 status 沒更新，怎麼修復？
- user 手動改過 backend state，control plane 應該 adopt 還是 overwrite？
- 同一個 design run 在 K8s、LSF、bare metal 之間切換時，平台能否仍用一致語義追蹤？

這些問題與「container 好不好」無關，卻與 reconciliation 非常相關。

因此一個比較合理的 semiconductor platform architecture，可能不是：

`Kubernetes replaces LSF`

而是：

`domain desired state → reconciliation control plane → execution adapter → K8s / LSF / Slurm / bare metal`

底下的 execution backend 保留各自最強的 scheduler、license、NUMA、storage、MPI/RDMA 特性；上層統一的是 intent、policy、status、evidence、artifact lineage 與 recovery semantics。

<figure>
  <img src="/assets/images/k8s/reconcile-eda-hybrid-control-plane.svg" alt="EDA HPC hybrid control plane 以 reconciliation 管理多種 execution backend" style="max-width:100%;height:auto;">
  <figcaption>圖 4｜對 EDA/HPC，更有價值的可能是統一 desired state 與 recovery semantics，而不是強迫所有 workload 使用同一 execution engine。圖為本文架構推論，依據 Kubernetes controller model、Slurm/LSF 類 batch scheduler 責任邊界與 EDA shared-storage/license 工作模式整理。</figcaption>
</figure>

這個模式還有一個重要結果：**平台可以逐步導入，而不是 big-bang migration。**

你可以先讓 controller 只觀察 LSF job，不改 execution；接著統一 run status；再加入 artifact verification；最後才把部分 container-friendly stage 移到 Kubernetes Job。每一步都增加 control-plane leverage，但不必一開始就碰最敏感的 PDK、license、NFS/SAN 或 commercial tool runtime assumption。

## 檢驗方式：故障後能否只靠目前的 state 推導下一步

一個 reconciliation-oriented system 是否設計得好，可以用一個很苛刻但有效的問題檢驗：

**把 controller 在任意一行程式後 kill -9，十分鐘後換另一台機器啟動；它能不能不依賴舊 process memory，也不需要人工解讀 log，就重新判斷下一步？**

如果答案是不行，通常代表某些 critical state 還藏在 execution history、local file、implicit side effect 或 operator memory 裡。

這並不表示所有 transient detail 都必須塞進 Kubernetes API。好的設計反而會很克制：只把「足以重新推導 correctness」的 durable state 保存下來；大量 ephemeral event、trace、log 仍放在 observability system。

reconciliation 要明確化的是決定系統是否正確所需的最小狀態，並非把所有事情狀態化。

當這個概念建立起來，下一個問題就非常自然：所有 controller 都把 kube-apiserver 當共同入口，那麼 API server 到底承擔了什麼？為什麼 authentication、authorization、admission、defaulting、validation、resourceVersion、watch、optimistic concurrency、flow control 都集中在這一層？如果它只是普通 REST server，整個 reconciliation model 根本撐不起來。

下一篇會沿著一個 Kubernetes API request 的完整生命週期，拆開 kube-apiserver 如何成為整個 cluster 的 serialization point 與 policy boundary。
