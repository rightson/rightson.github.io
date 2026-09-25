## 兩個都是 20 ns，Timing Model 仍可能不同

若 divider output 直接被當成新的 primary clock，SDC 可以寫成：

```tcl
create_clock -name root_clk -period 10.0 [get_ports clk]
create_clock -name div2_clk -period 20.0 [get_pins u_div/Q]
```

數值沒有錯，但它只描述「u_div/Q 上有一個 20 ns clock」。另一種寫法是：

```tcl
create_generated_clock -name div2_clk -source [get_ports clk] -divide_by 2 [get_pins u_div/Q]
```

後者多保存了 source relationship。AMD Vivado 的 `create_clock` 文件明確提醒：derived clock 若誤用 `create_clock`，child clock 不會繼承 source clock 的 insertion delay 與 jitter，可能造成錯誤 timing calculation。[AMD create_clock](https://docs.amd.com/r/2023.2-English/ug835-vivado-tcl-commands/create_clock)

因此 sanity checker 不能因為兩個 clock period 都是 20 ns 就判定等價。它必須知道這個 internal clock 究竟是獨立 oscillator，還是 root clock 的衍生物。