---
layout: post
title: "啟動程式後，Linux 如何建立、執行與回收一個 process？"
date: 2026-10-01 19:14:36 +0800
domain: distributed-systems
categories: distributed-systems
series: k8s-hpc
series_order: 1
description: "從同一支轉檔程式的兩次執行，釐清 program、process 與 thread；以 fork、exec、等待和強制終止的實跑紀錄，追出程序結束後仍須驗收的結果與殘留狀態。"
---

一支轉檔程式可以同時處理兩份輸入。檔案裡的程式碼相同，兩次工作的進度、錯誤與輸出卻必須分開；其中一次被停止，也不應讓另一份成果被誤判完成。作業系統需要替每一次執行保留身分、記憶體與執行進度，讓啟動者能追蹤它何時開始、目前等待什麼、最後如何結束。

這個執行單位就是 process，以下稱為程序。一個程序內還可以有多條 thread，也就是執行緒，分工處理不同步驟。先把這些關係弄清楚，之後才有辦法理解容器裡跑的是什麼、服務重啟了哪個單位，以及一個工作「已停止」究竟留下哪些東西。本篇先停在一台 Linux 機器，不需要 Kubernetes 或核心內部知識。

下圖沿著「程式檔案 → 啟動者 → 兩次執行 → 結果檔」閱讀。最需要留意的是底部：程序的生命週期與結果檔的生命週期並不重合。這個差距會決定失敗後能否安全重做。

![同一份程式檔案經啟動者產生兩個獨立程序，各有執行緒與輸出；停止程序不會撤銷已寫入檔案](/images/distributed-systems/2026-10-01/program-process-background.svg)

圖 1：作者設計的兩份轉檔工作情境；程序建立與執行緒關係依據 [Linux fork(2)](https://man7.org/linux/man-pages/man2/fork.2.html) 及 [pthreads(7)](https://man7.org/linux/man-pages/man7/pthreads.7.html) 整理。方塊尺寸不表示記憶體用量。

## 同一份程式碼，為什麼需要兩個執行身分

Program 是一組準備被執行的指令，例如磁碟上的執行檔或 Python 腳本。Process 是這些指令某一次執行所處的環境：目前走到哪裡、能讀寫哪些位址、持有哪些已開啟檔案，以及作業系統如何識別它。為兩份資料各啟動一次相同程式，就能得到兩個程序；修改其中一個程序的普通私有變數，不會直接把另一個程序的變數一起改掉。[fork(2) 對父子記憶體空間的說明](https://man7.org/linux/man-pages/man2/fork.2.html)

可以先把一個程序想成一份正在進行的工作紀錄。程式碼回答「能做哪些步驟」，工作紀錄回答「這次做到哪裡」。兩個程序可能讀同一份來源檔、使用同一套程式庫；各自具有執行環境，不代表它們完全不會共用資源。若都把結果寫到同一路徑，仍會互相覆蓋。程序邊界提供的是執行與記憶體的基本分隔，檔案命名和成果交付仍由程式設計負責。

Linux 用 PID 識別程序，PPID 表示父程序的識別。父子關係讓啟動者有辦法等待自己啟動的工作，取得其結束結果；這比只記住程式名稱可靠，因為同名程式可能同時存在多份。PID 也會被重用，不能把昨天保存的一個數字當成永久工作身分。[fork(2)](https://man7.org/linux/man-pages/man2/fork.2.html)、[核心 proc 文件的 PID 重用說明](https://www.kernel.org/doc/html/latest/filesystems/proc.html)

在本篇的假設轉檔服務裡，工作身分可以是 `conversion-17`，程序 PID 則是這次執行的位置。重新執行時，工作仍是同一份輸入，但得到新的程序。把這兩個識別分開保存，才能回答「同一工作重試了幾次」與「現在應觀察哪個程序」。這是作者提出的應用設計，作業系統不會替應用自動維護這層對應。

## 建立新程序與換上新程式，是兩個不同動作

一條容易理解的啟動路徑，是父程序先呼叫 `fork()` 建立子程序，再由子程序呼叫 `exec` 系列函式執行指定程式。`fork()` 成功後，父程序收到子程序 PID，子程序收到零，因此相同程式碼能依回傳值分別走父、子分支。父程序可以繼續管理工作，子程序則準備執行任務。[Linux fork(2)](https://man7.org/linux/man-pages/man2/fork.2.html)

接著的 `exec` 替換呼叫者的程式映像：子程序改用新的程式碼與記憶體內容執行，PID 維持不變。成功的 `exec` 不會回到原本那行的下一行；若檔案不存在、權限不足或格式不合，才會回到呼叫者並帶出錯誤。因此「子程序已建立」與「目標程式已開始」需要不同證據。[Linux execve(2)](https://man7.org/linux/man-pages/man2/execve.2.html)

這裡只拆解一條可觀察的路徑。程式庫也可以提供 `posix_spawn` 或更高層的啟動介面；shell 遇到不同命令時，也不一定每次都建立新程序。使用者在終端機輸入命令，只表示要求啟動某項工作，不能據此推定所有底層步驟都相同。[Python os 文件的 exec 與 spawn 介面](https://docs.python.org/3/library/os.html)

![父程序 fork 產生新的子程序身分，子程序 exec 後維持 PID，再在同一程序內建立兩條執行緒](/images/distributed-systems/2026-10-01/fork-exec-thread-boundary.svg)

圖 2：依據 [fork(2)](https://man7.org/linux/man-pages/man2/fork.2.html)、[execve(2)](https://man7.org/linux/man-pages/man2/execve.2.html) 與 [pthread_create(3)](https://man7.org/linux/man-pages/man3/pthread_create.3.html) 整理的概念路徑。實驗刻意讓父程序在 fork 時只有一條執行緒。

套到轉檔情境，父程序先保存輸入位置、輸出目錄和子程序 PID；子程序換上轉檔程式，讀取輸入並回報就緒，最後才處理資料。若 `exec` 失敗，父程序要把它歸為啟動失敗，不能等待一個永遠不會產生的結果檔。後面的實驗用非零退出碼處理這條錯誤路徑，但沒有注入 exec 失敗；已實跑範圍會另外列明。

另一個容易誤解的地方是啟動與可用性的差距。建立程序之後，應用可能仍在載入資料或檢查設定。本篇的實驗要求子程序主動回報就緒，才進行下一步觀察。這是一個很小的應用協定，卻已能把「存在一個程序」與「它已到達指定步驟」分開。

## Thread 是同一份工作環境裡的執行進度

若轉檔需要一條執行緒處理資料、另一條接收停止要求，可以在同一程序內建立 thread。每條執行緒有自己的執行進度與堆疊，但同一程序的執行緒共用記憶體空間和已開啟檔案等資源。這讓交接資料方便，也讓錯誤的共享存取可能破壞整份工作。[Linux pthreads(7)](https://man7.org/linux/man-pages/man7/pthreads.7.html)

Linux 的一般原生執行緒有自己的 TID；同組執行緒共用程序的識別，而主執行緒的 TID 等於該程序 PID。`/proc/<PID>/task/` 提供這個程序各條執行緒的觀察入口。[proc_pid_task(5)](https://man7.org/linux/man-pages/man5/proc_pid_task.5.html)

先用以下兩個具體問題選擇邊界：若一份輸入出錯，是否希望另一份輸入繼續工作？若要分享大量中間資料，是否願意負責同步存取？

| 方案 | 適合的需求 | 需要承擔的代價 |
| --- | --- | --- |
| 一個程序依序處理所有輸入 | 工作簡單，吞吐要求不高 | 某份輸入卡住，後續工作跟著等待 |
| 一個程序內多條執行緒 | 中間資料須頻繁共用 | 共享狀態的同步與整個程序故障影響 |
| 多個程序各處理一份輸入 | 要把重試、停止與失敗範圍分開 | 跨程序交接、啟動成本及資源重複 |

表格是作者依此情境提出的比較，沒有替三種方案做效能排名。執行緒數增加，不表示 CPU 同時做的工作一定增加；還要看有多少執行緒可執行、多少正在等待，以及實際 CPU 資源。若某個語言 runtime 另有限制，還須另外考慮。本篇只用 Python thread 建立可觀察身分，沒有測量 Python 計算平行度，也沒有將 thread 數當成吞吐 benchmark。

## 程序存在的時候，可能正在等待

有 PID 並不表示程式每一刻都在用 CPU。它可能等輸入、等另一條執行緒的通知，或已經結束但尚未被父程序回收。Linux 的狀態欄位可見 `R`、`S`、`D`、`T`、`Z` 等值；本篇只需要辨識可執行或執行中的 `R`、可中斷等待的 `S`，以及已終止待回收的 `Z`。[proc_pid_status(5)](https://man7.org/linux/man-pages/man5/proc_pid_status.5.html)

因此調查「工作為什麼沒有進展」時，第一個問題應是程式在哪個步驟等待。若子程序還在等父程序提供下一份輸入，提高 CPU 數量通常不會改變這個相依；若它確實持續計算，再研究 CPU 是否不足。狀態只提供查找方向，單次快照不會告訴你完整因果，也不能把所有 `S` 都判成異常。

本篇把子程序停在明確的等待點。主執行緒等父程序送來 `finish`，另一條執行緒等事件通知。父程序取得就緒回報後，才查狀態和執行緒數，因此能穩定看見兩條執行緒存在。這種控制步驟的實驗，比啟動後隨便等幾秒再截圖，更容易分辨觀察到了哪個階段。

## 用一個最小 trace 走完建立、執行與結束

[完整實驗程式](https://github.com/rightson/rightson.github.io/blob/main/scripts/experiments/k001/process_lifecycle.py) 使用 Python 標準函式庫；Linux 上可從 repo 根目錄執行：

```sh
python3 scripts/experiments/k001/process_lifecycle.py
```

它只建立、終止自己的直屬子程序，結果放在自動清除的暫存目錄；不需要 root，也不查其他使用者的程序。需要 Linux 的 `/proc`、`fork`、`exec` 和 `waitid` 支援，Windows 或 macOS 不適用這條觀察路徑。`execv` 和 `waitpid` 的 Python 介面見 [os 文件](https://docs.python.org/3/library/os.html)。

完整順序如下。父程序建立兩條 pipe，這裡先把它們理解為單向傳訊管道：一條傳指令，一條收回報。父程序 fork 子程序，子程序把管道接到標準輸入和輸出，再 exec 同一份 Python 腳本的 worker 分支。Worker 建立背景執行緒，寫入 `result.tmp`，回報 PID、TID 與就緒狀態，然後等待指令。

父程序讀到回報後，比對 fork 回傳 PID 與 worker 自報 PID，檢查確實只有兩條執行緒，再選擇正常完成或注入失敗。正常路徑送出 `finish`：worker 喚醒並等待背景執行緒結束，寫入完整資料，將暫存檔改名為結果檔，最後退出。失敗路徑則對自己的子程序送出 SIGKILL。程式最後另外重做一次失敗工作，驗證恢復路徑。

這是作者於 2026 年 10 月 1 日實跑的結果，環境為 Linux `6.18.44`、Python `3.12.14`。[原始觀察紀錄](https://github.com/rightson/rightson.github.io/blob/main/scripts/experiments/k001/observed.jsonl) 保留了實際 PID 和 TID；它們每次重跑會不同。

| 路徑 | 就緒時的 thread 數 | 終止後、回收前 | Python 解碼結果 | 回收後本次觀察入口 | 留下的檔案 |
| --- | ---: | --- | ---: | --- | --- |
| 正常完成 | 2 | Z | 0 | 已消失 | `result.txt` |
| SIGKILL 中斷 | 2 | Z | -9 | 已消失 | `result.tmp` |
| 清除暫存後重新執行 | 2 | Z | 0 | 已消失 | `result.txt` |

`-9` 是本實驗由 Python 將 wait 狀態解碼後的表示，指被 signal 9 終止；它不是作業系統把正常退出碼設為負九，也不保證 shell 使用相同表示。[Python os.waitstatus_to_exitcode](https://docs.python.org/3/library/os.html)

這次環境還出現一個觀察邊界：正常子程序的 `getpid()` 是 7，`/proc/self/status` 的 `Pid` 卻是 737613。程序所在的識別視角與掛載的 `/proc` 視角不同；`NSpid` 可用來對照。程式讓 worker 讀自己的觀察路徑並回報，不拿 PID 7 直接猜 `/proc/7`。這裡只先記住「識別須連同觀察範圍理解」，隔離機制留待後續課程。[proc_pid_status(5) 的 NSpid 定義](https://man7.org/linux/man-pages/man5/proc_pid_status.5.html)

本次 trace 是程式在關鍵步驟取得的身分、狀態與檔案觀察，沒有逐條捕捉核心 syscall，沒有量測 CPU、記憶體用量或啟動延遲。三次成功通過檢查，支持的是這三條生命週期路徑，不能外推為高併發下的可靠性或效能結果。

## 結束、回收與工作成功，需要三份不同證據

正常退出會產生可供父程序取得的結束狀態。若父程序尚未回收，Linux 可以暫時保留 zombie，讓父程序之後取得結果；`waitpid` 消費相應狀態並完成回收。本篇刻意先用 `waitid` 的 `WNOWAIT` 觀察終止，再讀 Z，最後才呼叫 `waitpid`。[Linux wait(2)](https://man7.org/linux/man-pages/man2/wait.2.html)

Zombie 已不再執行使用者程式，不是那份轉檔工作還在背景繼續計算。若一個 launcher 長期忽略所有子程序的回收，這些等待取得的退出紀錄就會累積；處理方向是修正父程序的等待責任。本實驗只短暫保留狀態供觀察，並在所有路徑回收自己建立的子程序。[wait(2)](https://man7.org/linux/man-pages/man2/wait.2.html)

從應用角度，還要驗收第三件事：結果是否完整。退出碼零代表程式回報成功；它不自動證明結果符合使用者需求。例如程式可能漏處理最後一筆資料，卻仍正常退出。這份實驗除了檢查退出結果，也核對結果檔存在、暫存檔消失；真正轉檔服務還應檢查輸入身分、筆數、格式與必要的資料完整性。這些是應用提出的承諾，不能交給 PID 或退出碼代替。

![正常完成與強制終止分成兩條路徑，父程序分別檢查結果，再回收退出紀錄；失敗路徑仍留下暫存檔](/images/distributed-systems/2026-10-01/termination-recovery.svg)

圖 3：作者依本次實跑整理。終止與回收語意參考 [signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html) 及 [wait(2)](https://man7.org/linux/man-pages/man2/wait.2.html)；檔案驗收和重做策略為本實驗的應用設計。

## 強制停止留下的半成品，要由誰收拾

在失敗路徑裡，worker 已把部分內容寫到 `result.tmp`，隨後收到 SIGKILL。這個 signal 不能由程式攔截、忽略或阻擋，使用者程式無法保證執行自己的最後清理步驟。[Linux signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html)

偵測證據是父程序取得的 signal 終止結果，以及仍存在的暫存檔。殘留狀態是已寫入檔案的部分內容；程序回收並未撤銷它。恢復則是本案例明示的政策：這個工作只有本地轉檔，沒有對外交易，父程序捨棄未完成輸出，再從原始輸入重新執行。新的 PID 表示新的 attempt，不能沿用失敗程序的執行進度。

正常路徑使用同一目錄的暫存檔與 `rename`，讓讀者看到的正式名稱對應到完成版本。改名的原子性可以縮小「讀到半份正式檔」的窗口，但它不等於突然斷電後的持久性保證；本次沒有測斷電，也沒有建立 `fsync` 的耐久性流程。[Linux rename(2)](https://man7.org/linux/man-pages/man2/rename.2.html)

合理替代方案之一是直接寫正式檔，另存一個完成標記。讀者每次都要先驗證標記與檔案版本一致，否則仍可能誤讀半成品。另一個方案是每次 attempt 使用獨立目錄，驗收後再發布指向完整版本的索引；它保留更多除錯資料，也增加垃圾清除與儲存成本。本篇採用單次暫存檔，因為工作只有一個小型輸出，驗收與清除規則容易說清楚。

還有一個必須停住的邊界：如果工作已經送出付款、寄出訊息或修改外部服務，清除本地暫存檔不能撤銷那些效果。是否能重做，要由外部操作的識別、回覆與去重設計決定；「程序死了就再跑一次」在那種情境下資訊不足。本篇的恢復結論限於可從原始輸入重做的本地工作。

## 用等待時間檢查多執行緒是否值得

以下是透明的假設算例，不是本次實測。假設一份工作有三步：讀取輸入等待 80 ms、計算 20 ms、寫出結果等待 40 ms。依序完成需要 140 ms。若所有步驟沒有重疊，理想吞吐約為每秒 `1000 / 140 = 7.14` 份；其中 CPU 計算時間只占 `20 / 140 = 14.3%`。

這說明為什麼等待可能值得被其他工作填補。若有多份彼此獨立的輸入，可以讓一份等待時處理另一份。但四條 thread 不能直接推定吞吐增加四倍：假設所有工作共用的儲存每秒最多承接 12 份，端到端吞吐仍受這個上限約束；若另受單一序列步驟限制，也須納入計算。

再換一個假設：資料已在記憶體裡，每份計算 140 ms，幾乎沒有等待。此時增加背景執行緒並不會消除計算量，需要看可用 CPU 與 runtime 能否真正平行執行。前一個情境的等待重疊理由，不能照搬到後一個情境。這正是先分辨「程序存在、執行緒可執行、正在等待」的價值。

實際驗證至少應固定相同輸入、完成驗收與資源限制，再比較一個依序程序、多執行緒程序及多程序 worker。記錄每秒完成數、單份工作尾端延遲、錯誤率與總記憶體成本；只量啟動了幾條 thread，無法回答使用者得到多少完整成果。本次未做這組效能比較，保留為後續實驗問題。

## 下一層要問的是 CPU 如何輪流服務這些進度

沿著這份轉檔 trace，現在可以逐項辨認：檔案裡的 program 定義步驟，process 保存一次執行的環境，thread 保存其中一條執行進度；fork 建立新身分，exec 替換程式，等待與退出需要父程序觀察，成果則另外驗收。

這套模型已足以診斷三種常見誤判：程序已建立卻尚未就緒；執行緒存在卻正在等輸入；程序已回收卻仍留下未完成檔案。接下來的 K002 會處理另一個自然問題：當可執行的進度比 CPU 核心多，一顆 CPU 如何輪流服務它們，而我們看到的時間與吞吐又會如何改變？

## References

- [Linux man-pages：fork(2)](https://man7.org/linux/man-pages/man2/fork.2.html)：程序建立、父子差異與多執行緒 fork 的限制。
- [Linux man-pages：execve(2)](https://man7.org/linux/man-pages/man2/execve.2.html)：替換程式映像及錯誤。
- [Linux man-pages：pthreads(7)](https://man7.org/linux/man-pages/man7/pthreads.7.html) 與 [pthread_create(3)](https://man7.org/linux/man-pages/man3/pthread_create.3.html)：共享與個別執行緒狀態。
- [Linux man-pages：proc_pid_task(5)](https://man7.org/linux/man-pages/man5/proc_pid_task.5.html) 與 [proc_pid_status(5)](https://man7.org/linux/man-pages/man5/proc_pid_status.5.html)：執行緒觀察、狀態及識別視角。
- [Linux 核心：The /proc Filesystem](https://www.kernel.org/doc/html/latest/filesystems/proc.html)：程序觀察介面與 PID 重用邊界。
- [Linux man-pages：wait(2)](https://man7.org/linux/man-pages/man2/wait.2.html) 與 [signal(7)](https://man7.org/linux/man-pages/man7/signal.7.html)：終止、回收及 signal 語意。
- [Linux man-pages：rename(2)](https://man7.org/linux/man-pages/man2/rename.2.html)：檔名替換與原子性。
- [Python：os 標準函式庫](https://docs.python.org/3/library/os.html)：本次程式使用的程序及 wait 介面；實跑版本為 3.12.14，線上預設文件版本另行更新。
