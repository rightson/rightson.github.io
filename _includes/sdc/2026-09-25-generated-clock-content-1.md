昨天先釐清了 `create_clock` 如何建立 launch/capture edge。下一步是：如果 capture clock 不是直接從 top-level port 進來，而是經過 divider、PLL 或 clock-generation logic 才產生，STA 如何知道它和原始 clock 的關係？

假設 root clock 是 100 MHz，內部 divider 產生 50 MHz。只看輸出可以得到 20 ns period，但這還少了一個關鍵資訊：div2 clock 的 edge 是由 root clock 的哪些 edge 推導而來。

```text
root_clk: 0   5   10  15  20  25  30 ns
          ↑   ↓   ↑   ↓   ↑   ↓   ↑
div2_clk: 0       10      20      30 ns
          ↑       ↓       ↑       ↓
```

Generated clock 要保存的不是 frequency label，而是這條 parent-child timing lineage。