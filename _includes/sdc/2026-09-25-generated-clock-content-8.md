## Agent 需要的是 Evidence Package，不是一個 WNS

Generated-clock issue 至少要整理四組資料。Constraint evidence 包含 base clock、generated source、master、target、divide/multiply/edges/phase；topology evidence 包含 source 到 divider/PLL/mux 再到 generated target，以及 target 到 clock sinks；timing evidence 包含 launch/capture clock、selected edge pair、clock arrival、data arrival、required time、slack；tool evidence 則包含 empty collection、multiple-master ambiguity、unconstrained path 與 propagation diagnostics。

只給 agent 一行 `WNS = -0.18 ns`，它沒有足夠資訊區分 data path 太慢、generated source 選錯、phase relation 錯、master ambiguous，或 hierarchy target 已失效。Agent 的價值應該建立在 timing engine 與 checker 已確認的 facts 上，而不是重新猜 STA。

## 下一步：I/O Constraint 把晶片外的時間世界接進來

到這裡，我們已有 primary clock 與 generated clock。下一個 prerequisite 是 I/O timing：chip boundary 外面的 launch/capture register 不在 netlist 裡，`set_input_delay`、`set_output_delay` 必須把 external device、board delay 與 interface requirement 壓縮成 STA 可分析的 contract。

Generated clock 解決「內部 clock 從哪裡來」；I/O constraint 接著回答「晶片外面的時間世界怎麼接進來」。

## References

- [OpenSTA Command Reference](https://opensta.readthedocs.io/en/latest/Commands/)
- [Intel create_generated_clock](https://www.intel.com/content/www/us/en/programmable/quartushelp/24.2/tafs/tafs/tcl_pkg_sdc_ver_1.5_cmd_create_generated_clock.htm)
- [Intel Timing Analyzer User Guide](https://www.intel.com/programmable/technical-pdfs/683068.pdf)
- [Intel falling-edge divided clock example](https://www.intel.com/content/www/us/en/support/programmable/articles/000074682.html)
- [AMD create_generated_clock](https://docs.amd.com/r/2020.2-English/ug835-vivado-tcl-commands/create_generated_clock)
- [AMD create_clock](https://docs.amd.com/r/2023.2-English/ug835-vivado-tcl-commands/create_clock)
