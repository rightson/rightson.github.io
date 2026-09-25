## Sanity Checker 要驗證一條 Lineage Chain

對 generated clock，deterministic checker 至少要驗證：

```text
master clock
    ↓
source object 是否存在
    ↓
source object 上是否真的有 master clock
    ↓
waveform transformation 是否合理
    ↓
generated target 是否存在
    ↓
generated clock 是否真的建立
    ↓
clock 是否傳到預期 sequential sinks
    ↓
root/generated domain path 是否被正確分析
```

例如 synthesis 後 hierarchy 改名，`u_div/Q` 可能不再存在；clock mux source 上可能同時有兩個 clocks 卻漏了 master；divider implementation 改了，SDC 還留著舊 `-divide_by`。這些都比「period 是不是 20 ns」更接近真實 failure。

今天的 [SDC Lab Experiment 003](https://github.com/rightson/sdc-lab/tree/day3-generated-clock-lineage-clean/experiments/003-generated-clock-lineage) 就故意比較兩種模型：正確版本用 `create_generated_clock`，比較版本在相同 divider output 上建立獨立 20 ns clock。Lab 的 checker 即使看到兩者 period 相同，也會拒絕遺失 source/master lineage 的版本。