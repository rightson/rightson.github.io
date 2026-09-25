## Generated Clock 也不是「自動理解 Design Intent」

`create_generated_clock` 能保存 clock provenance，但它仍然依賴工程師提供正確的 source、target 與 transformation。工具不會因為 RTL 裡看見一顆 toggle FF，就保證理解這顆 node 在所有 modes 下都應該被當成 divide-by-2 functional clock。

這裡存在兩個合理邊界。第一種做法是盡量讓工具從 clocking primitive 或已知 PLL 結構自動推導，優點是減少重複 constraint；缺點是 inference 依賴 tool knowledge 與特定 implementation。第二種做法是由 SDC 明確宣告 generated relationship，語意更可審核，但 RTL/netlist 一旦改變，constraint 可能 stale。

因此 sanity checker 最有價值的地方不是替 SDC 多做一層 parser，而是做 cross-check：

```text
SDC 宣稱：u_div/Q = root_clk / 2
        ↕
Netlist evidence：u_div 的 clock/data topology 是否仍符合這個假設？
        ↕
Tool evidence：div2_clk 是否真的到達預期 sinks？
```

未來真正的 issue solver 應該把這三種 evidence 放在一起。只有 SDC 沒有 topology，會相信 stale intent；只有 topology 沒有 SDC，又會把「電路看起來像 divider」誤當成設計者承諾的 timing contract。