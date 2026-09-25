## Edge Mapping 會直接改變 Setup Relationship

考慮最小 design：

```text
                      +---------------------+
root clk ------------>| u_div (toggle DFF) |---- div2 ----+
   |                  +---------------------+              |
   |                                                       v
   +----> u_launch DFF ---- data_q -----------------> u_capture DFF
```

`u_launch` 由 root clock 驅動，`u_capture` 由 div2 clock 驅動。root rising edges 為 0、10、20、30 ns；div2 rising edges 為 0、20、40 ns。STA 不是把兩個 frequency 丟進公式，而是從兩組 edge sequence 找合法 launch/capture pair。

如果 divider 的 active edge 改變，mapping 也會改。Intel 公開範例使用 `-edges {2 4 6}` 表示從 source falling edge 建立 divided clock；generated rising 不再對應 source edge 1。[Intel falling-edge divide example](https://www.intel.com/content/www/us/en/support/programmable/articles/000074682.html)

這也解釋了為何 phase、invert、PLL multiply 等情況無法只靠 period 表達：同樣的頻率，可以有不同的 edge relationship。