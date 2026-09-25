## PLL、Phase 與 Multiple Master 讓 Lineage 更重要

Divider 只是最簡單案例。Generated clock 還可能包含 `-multiply_by`、`-invert`、`-edges`、`-edge_shift` 等 transformation。若 source period 是 10 ns，PLL 做 ×2，generated period 會變成 5 ns；但若同時有 phase shift，只寫 5 ns 已經無法描述 capture edge 相對 root edge 的位置。[OpenSTA Command Reference](https://opensta.readthedocs.io/en/latest/Commands/)

另一個容易被忽略的情況是同一個 source node 上存在多個 clock。此時「source object 是哪一個 pin」仍不足以決定 master waveform，工具需要 `-master_clock` 解除歧義。AMD、Intel、OpenSTA 都提供這個概念。[AMD create_generated_clock](https://docs.amd.com/r/2020.2-English/ug835-vivado-tcl-commands/create_generated_clock)

因此 clock sanity 不應只做 syntax lint。它需要回答：source object 上有哪些 clocks、哪個是 master、transformation 是什麼、target 是否存在、generated clock 最後傳到了哪些 sequential sinks。這些才是後續 timing reasoning 的可靠輸入。