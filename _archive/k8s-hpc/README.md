# Archived Kubernetes / HPC series

The five published articles from 2026-09-22 through 2026-09-26 and the unfinished scheduler #006 draft were withdrawn on 2026-09-29. This series is replaced by a new prerequisite-led curriculum. Jekyll explicitly excludes `_archive`; these six manuscripts do not count as completed lessons.

Original Markdown and image blobs are preserved without alteration:

- `_posts/2026-09-22-kubernetes-control-plane-hpc-foundation.md`
- `_posts/2026-09-23-kubernetes-reconciliation-control-loop.md`
- `_posts/2026-09-24-kube-apiserver-policy-serialization-boundary.md`
- `_posts/2026-09-25-etcd-kubernetes-mvcc-watch-quorum.md`
- `_posts/2026-09-26-kube-controller-manager-informer-workqueue-lease.md`
- `_drafts/kube-scheduler-placement-transaction.md`

Markdown retains original absolute image paths for provenance; matching SVG files are under this archive. Restoration would require an intentional new editorial decision, current source verification, and restoring the assets together. The current website roadmap points to rightson/k8s-lab for the active curriculum and completion ledger.

## 2026-10-01 課程改版

使用者核准改為具備 OS 先備、Kubernetes 從零開始的完整課程。K001 process 基礎篇亦下架，原始 Markdown、date、categories、series、series_order 與三張 SVG 原樣保存在本目錄；不換日期或 slug 重發。

- `_posts/2026-10-01-linux-program-process-thread-lifecycle.md`
- 原公開網址：`https://rightson.github.io/distributed-systems/2026/10/01/linux-program-process-thread-lifecycle.html`（下架後不作公開先修）
- 原發布 commit：`08254e5fd166bf9951edb4486be1f38f6767d091`；原驗證紀錄仍保留，封存不抹除歷史成果。
- K001–K081 舊 roadmap：[歷史原文](https://github.com/rightson/k8s-lab/blob/main/archive/roadmaps/2026-10-01-k001-k081.md)。
- K001 程式與原觀測紀錄：[k8s-lab archive](https://github.com/rightson/k8s-lab/tree/main/archive/k001)。遷移不是新增測量。

舊 #001–#006 與 K001–K081 均保留歷史身分。新課程使用 K082–K129，series 延續 `k8s-hpc`；學習單元 01–48 是課程順序，不重用舊篇號。恢復封存文章須使用者另行授權。
