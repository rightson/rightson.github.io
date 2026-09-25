## source 與 target 回答兩個不同問題

在 `create_generated_clock` 裡，`-source [get_ports clk]` 表示 waveform transformation 從哪個 clock source 開始；最後的 `[get_pins u_div/Q]` 則表示 generated clock 實際建立在哪個 design object。OpenSTA 將 divide、multiply、invert、edge selection 等資訊都放在這個 source→target 關係上。[OpenSTA Command Reference](https://opensta.readthedocs.io/en/latest/Commands/)

對 10 ns、50% duty-cycle 的 root clock，source edge 可以編成：

```text
edge index     1    2    3    4    5
time (ns)      0    5   10   15   20
transition     ↑    ↓    ↑    ↓    ↑
```

標準 divide-by-2 可等價看成 `-edges {1 3 5}`：generated rising 對 source edge 1，generated falling 對 source edge 3，下一個 rising 對 source edge 5。Intel 的 command reference 也直接給出這個等價關係。[Intel create_generated_clock](https://www.intel.com/content/www/us/en/programmable/quartushelp/24.2/tafs/tafs/tcl_pkg_sdc_ver_1.5_cmd_create_generated_clock.htm)

所以 50 MHz 只是結果；edge mapping 才保留它怎麼來。