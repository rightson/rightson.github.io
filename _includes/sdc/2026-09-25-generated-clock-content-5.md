## Pre-CTS 看起來一樣，反而是更危險的 Failure Mode

如果 divider output 被直接寫成 20 ns primary clock，而且兩個 waveform 都從 0 ns 開始，在 zero-latency 的 toy model 裡，錯誤版本和正確 generated-clock 版本可能碰巧得到相同的部分 edge time，甚至某些 slack 也一樣。

這不是證明兩種 constraint 等價，而是證明「看 output metric」不足以驗證 constraint correctness。

一旦進入 propagated clock，root source latency、divider 之前的 clock path、generated target 之後的 insertion delay、jitter、uncertainty、phase transformation 都開始參與 clock arrival。正確的 generated clock 可以沿 source lineage 帶入這些關係；獨立 primary clock 則切斷了這條因果鏈。

這類問題特別難抓，因為早期報表未必立即出現 negative slack。Constraint model 可能在某個 stage 恰巧給出合理數字，直到 CTS、hierarchy 或 mode 改變後才偏離 design intent。Sanity 的判準因此不能只是「目前 WNS 是否正常」，而必須驗證 clock model 是否保留正確 provenance。