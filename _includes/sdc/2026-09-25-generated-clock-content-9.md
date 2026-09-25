## 一個數字例子：Latency 一進來，錯誤 Model 就不再只是語意差異

假設 root clock 在 top-level port 的 logical edge 是 0 ns，但實際到 divider source 之前已有 0.8 ns source latency；divider output 到 capture FF 的 clock tree 再增加 0.4 ns。Data path 從 root-clock launch FF 到 capture D 需要 6.5 ns。

在 generated-clock model 裡，capture side 的 clock arrival 應包含從 root lineage 延續下來的 clock context，再加上 generated network 的 propagation。若把 divider output 重新宣告成一顆獨立 primary clock，分析器看到的 clock origin 會從 u_div/Q 重新開始；原本 0.8 ns 的上游 context 可能不再存在於這顆 child clock 的模型裡。

這裡不能把 0.8 ns 一律解讀成 setup 一定變好或變壞，因為最後 slack 還取決於 launch/capture latency、common path、uncertainty 與 analysis mode。重要的是：兩個模型已經在計算不同的 clock arrival。這也是為什麼「period 都是 20 ns」不構成等價證明。

真正要比較的是完整的 arrival breakdown，而不是只看 headline WNS。