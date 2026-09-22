# TPU Technical Series Roadmap

> Internal editorial roadmap for the TPU deep-dive series published on rightson.github.io.
> This file lives under `.github/` and is **not** a Jekyll post.
> Public articles must follow `AGENTS.md`.

## Objective

Build a coherent, non-repetitive technical curriculum that explains Google TPU across the complete stack:

`workload / algorithm → compiler / runtime → microarchitecture → chip / memory → package / board → ICI / DCN → pod / datacenter`

The series should not become a product-spec chronology. Every article must answer:

1. What bottleneck made this design necessary?
2. How does the mechanism solve it?
3. What trade-off or new bottleneck does the solution create?
4. How does this connect to the previous and next layers of the TPU system?

## Editorial constraints

- Read `AGENTS.md`, this roadmap, and recent `_posts/` before writing.
- Publish exactly one primary topic per article.
- Minimum article depth: **at least a 5-minute read**. Target roughly 2,500–4,500 Traditional Chinese characters excluding front matter and references; longer is acceptable when the topic requires it.
- Every article must contain at least one concrete technical example, calculation, tensor shape, bandwidth/latency example, topology mapping, or compiler mapping.
- Prefer **2–4 technically meaningful visual elements per article** when the topic supports them: architecture/block diagrams, dataflow diagrams, memory hierarchy, chip/package/board/rack relationships, topology, roofline/bandwidth charts, or tables. Avoid decorative stock imagery.
- Every visual must include an explicit source citation in its caption. If using an original Google/paper figure, link the primary source. If redrawing a diagram, label it as `依據 ... 重繪/整理` and cite all primary sources used to construct it. Do not present an unsourced schematic as fact.
- Prefer Google / Google Cloud / Google DeepMind primary sources and peer-reviewed architecture/system papers.
- Clearly separate public facts, reported experimental results, and author inference.
- Do not repeat an existing article unless new evidence materially changes the conclusion.
- Mark an item `[x]` only after the public post is committed and verified.
- Add newly disclosed TPU generations or major architectural topics to this roadmap rather than replacing prior topics.
- Keep generation-history articles interleaved with cross-layer deep dives so the series does not spend many consecutive days on one layer.

## Current generation boundary — 2026-09-22

- TPU7x / Ironwood: seventh-generation TPU, generally available on Google Cloud.
- TPU 8t and TPU 8i: eighth-generation TPU systems publicly announced by Google Cloud and listed as coming soon.
- Primary current-generation references:
  - https://cloud.google.com/tpu
  - https://docs.cloud.google.com/tpu/docs/tpu7x
  - https://cloud.google.com/blog/products/compute/tpu-8t-and-tpu-8i-technical-deep-dive

---

## Phase 1 — Why TPU existed

- [x] 01. TPU v1 origin: why Google built an inference ASIC instead of simply buying more CPUs/GPUs  
  Public post: `_posts/2026-09-22-tpu-v1-origin-inference-asic.md`
- [ ] 02. TPU v1 datapath: how the 256×256 systolic array sustains 65,536 MACs
- [ ] 03. INT8 inference: why precision reduction changes silicon economics
- [ ] 04. TPU v1 memory hierarchy: 24 MiB Unified Buffer, 4 MiB accumulators, Weight FIFO, and 8 GiB DDR3
- [ ] 05. P99 latency versus throughput: why datacenter inference changes processor design
- [ ] 06. Roofline analysis of TPU v1: why memory bandwidth became the next wall
- [ ] 07. TPU v1 compiler/runtime: CISC-like commands, software-managed memory, and deterministic execution
- [ ] 08. Why TPU v1 was a PCIe coprocessor: production integration versus architectural purity

## Phase 2 — From inference chip to training machine

- [ ] 09. Why training required TPU v2: gradients, precision, memory capacity, and communication
- [ ] 10. BF16: why exponent range mattered more than mantissa width for deep-learning training
- [ ] 11. TPU v2 TensorCore anatomy: MXU, vector unit, scalar/control, and dataflow
- [ ] 12. HBM enters TPU: arithmetic intensity, optimizer state, activations, and bandwidth
- [ ] 13. TPU v2 interconnect: when accelerator architecture became a distributed-system problem
- [ ] 14. TPU v3: higher compute density, liquid cooling, and power as an architectural constraint
- [ ] 15. From single device to TPU Pod: what changes when hundreds of accelerators train one model
- [ ] 16. Data parallelism versus model parallelism on early TPU Pods

## Phase 3 — Scaling the pod

- [ ] 17. Collective communication fundamentals: all-reduce, all-gather, reduce-scatter, and all-to-all
- [ ] 18. 2D and 3D torus topology: mapping logical parallelism onto physical links
- [ ] 19. TPU v4 architecture: why scaling compute forced a network redesign
- [ ] 20. TPU v4 optical circuit switching: topology reconfiguration as a machine-learning primitive
- [ ] 21. TPU v4 SparseCore: embeddings as an irregular-memory workload
- [ ] 22. TPU v4 MegaCore: combining cores and what it changes for execution
- [ ] 23. Scale-up versus scale-out: ICI inside a pod and DCN between pods
- [ ] 24. Failure domains at pod scale: checkpointing, repair, and useful FLOPs versus peak FLOPs
- [ ] 25. Why communication overlap matters more as model size increases

## Phase 4 — Compiler and programming model

- [ ] 26. XLA and HLO: how tensor programs become TPU programs
- [ ] 27. SPMD and GSPMD: why sharding belongs in the compiler
- [ ] 28. JAX mesh and PartitionSpec: mapping model dimensions to TPU topology
- [ ] 29. Layout and tiling: why mathematically identical matmuls can perform very differently
- [ ] 30. Fusion: eliminating intermediate memory traffic
- [ ] 31. Rematerialization / activation checkpointing: trading compute for memory
- [ ] 32. Pallas and custom kernels: where compiler automation stops
- [ ] 33. Host-device execution boundaries: when CPU orchestration stalls TPU utilization
- [ ] 34. Performance debugging: recognizing compute-, memory-, and communication-bound TPU workloads

## Phase 5 — Transformer anatomy on TPU

- [ ] 35. Transformer block mapped to TPU: QKV, attention, MLP, normalization, and residuals
- [ ] 36. Matmul tensor shapes: batch, sequence, hidden dimension, heads, and TPU tiling
- [ ] 37. Attention scaling: when the workload is compute-bound versus memory-bound
- [ ] 38. Flash-style attention concepts and why data movement dominates long sequences
- [ ] 39. KV cache: why inference turns into a memory-capacity and bandwidth problem
- [ ] 40. Prefill versus decode: two fundamentally different workloads inside LLM inference
- [ ] 41. Continuous batching: latency/throughput trade-offs in TPU serving
- [ ] 42. Speculative decoding: shifting the bottleneck from autoregressive dependency to verification
- [ ] 43. Quantized inference on modern TPU: weights, activations, KV cache, and accuracy trade-offs

## Phase 6 — Mixture-of-Experts and sparse workloads

- [ ] 44. MoE routing: why all-to-all communication becomes first-class
- [ ] 45. Expert parallelism: mapping experts to chips and pods
- [ ] 46. Load imbalance: why theoretical FLOPs can disappear in sparse models
- [ ] 47. SparseCore evolution: embedding lookup, sparse compute, and communication
- [ ] 48. Capacity factor, token dropping, and hardware utilization
- [ ] 49. Dense versus sparse models: compute economics from chip to datacenter

## Phase 7 — TPU v5 family

- [ ] 50. TPU v5e: why cost-efficient training and serving justified a different design point
- [ ] 51. TPU v5p: large-pod dense training and high-bandwidth scale-up
- [ ] 52. v5e versus v5p: specialization inside one generation
- [ ] 53. v5 memory hierarchy and the balance between MXU throughput and HBM
- [ ] 54. v5 pod topology and collective performance
- [ ] 55. Why one accelerator SKU no longer optimizes every AI workload

## Phase 8 — Trillium / sixth generation

- [ ] 56. TPU v6e / Trillium: what changed relative to v5e
- [ ] 57. Trillium compute and memory balance: where the extra performance is spent
- [ ] 58. Trillium SparseCore: embedding-heavy recommendation and language workloads
- [ ] 59. Trillium 2D torus and 256-chip pod: when smaller scale-up domains can be efficient
- [ ] 60. Training and inference on one generation: where architecture converges and diverges

## Phase 9 — Ironwood / seventh generation

- [ ] 61. TPU7x Ironwood: the shift toward large-scale training, sampling, and decode-heavy inference
- [ ] 62. Ironwood package/chiplet organization: yield, bandwidth, and software-visible topology
- [ ] 63. Ironwood HBM capacity and bandwidth: what workloads consume it
- [ ] 64. 9,216-chip pod: how a 3D torus changes partitioning choices
- [ ] 65. Ironwood and MoE: communication pressure as a primary design constraint
- [ ] 66. Host offload and PCIe: why the accelerator boundary still matters
- [ ] 67. Reliability at Ironwood scale: unhealthy chips, topology awareness, and job continuity

## Phase 10 — Eighth generation: TPU 8t and TPU 8i

- [ ] 68. Why Google split generation eight into TPU 8t and TPU 8i
- [ ] 69. TPU 8t: training throughput, 9,600-chip superpod, and high-bandwidth memory pool
- [ ] 70. TPU 8i: inference/post-training specialization and 384 MB on-chip SRAM
- [ ] 71. Long-context KV cache on silicon: what 384 MB SRAM changes
- [ ] 72. Boardfly topology: reducing serving-network diameter and tail latency
- [ ] 73. Collectives Acceleration Engine: dedicated synchronization for autoregressive reasoning
- [ ] 74. TPU 8 ICI evolution: why scale-up bandwidth keeps increasing
- [ ] 75. Axion CPU integration: data preparation and orchestration as accelerator bottlenecks
- [ ] 76. Training versus post-training versus serving: why the hardware requirements have diverged
- [ ] 77. TPU v1 to TPU 8: how the bottleneck migrated from MACs to memory, network, and system latency

## Phase 11 — Packaging and silicon implementation

- [ ] 78. HBM packaging fundamentals for TPU-class accelerators
- [ ] 79. Interposer and package routing: bandwidth density versus cost and yield
- [ ] 80. Chiplets: reticle limits, yield economics, die-to-die bandwidth, and latency
- [ ] 81. Power delivery: why hundreds of kilowatts per rack begin at the package
- [ ] 82. Thermal path: die → package → cold plate → facility water loop
- [ ] 83. Clocking and voltage: frequency, efficiency, and thermal-density trade-offs
- [ ] 84. SRAM versus HBM versus off-package memory: latency/capacity/bandwidth hierarchy

## Phase 12 — Board, tray, rack, and host integration

- [ ] 85. TPU board anatomy: accelerator, HBM, power stages, host links, and management
- [ ] 86. Host CPU role: preprocessing, input pipeline, runtime, and failure handling
- [ ] 87. Tray/rack integration: signal integrity, power, cooling, and serviceability
- [ ] 88. Liquid cooling: why high-density AI racks cannot be understood as “just servers”
- [ ] 89. Rack-level power delivery and redundancy
- [ ] 90. Boot, health monitoring, firmware, and fleet management for TPU systems

## Phase 13 — Networking architecture

- [ ] 91. ICI versus datacenter network: two networks solving different scaling problems
- [ ] 92. Scale-up bandwidth versus scale-out bandwidth
- [ ] 93. Collective traffic matrices: why AI traffic differs from web-service traffic
- [ ] 94. Congestion and incast in distributed training
- [ ] 95. Optical interconnect: where optics enters TPU scale-up and scale-out
- [ ] 96. Network topology-aware placement: why scheduler decisions affect model FLOPs
- [ ] 97. Cross-pod training: when the DCN becomes part of the model architecture
- [ ] 98. Pathways: spanning many TPU slices and fault domains as one computation

## Phase 14 — Distributed training system

- [ ] 99. Data parallelism: gradients, all-reduce, and scaling efficiency
- [ ] 100. Tensor/model parallelism: splitting large matrix operations
- [ ] 101. Pipeline parallelism: bubbles, microbatches, and stage balance
- [ ] 102. Expert parallelism: sparse computation at cluster scale
- [ ] 103. Multi-dimensional parallelism: combining DP/TP/PP/EP
- [ ] 104. Checkpoint architecture: local storage, parallel file systems, and recovery time
- [ ] 105. Stragglers and failure recovery: why large jobs lose efficiency
- [ ] 106. Job scheduling and fragmentation: allocating TPU topology instead of just chip count

## Phase 15 — Inference and serving system

- [ ] 107. Tokens per second versus time-to-first-token versus inter-token latency
- [ ] 108. Serving SLOs: why P99 returns to center stage twenty years after TPU v1
- [ ] 109. Prefill/decode disaggregation: when separating phases helps
- [ ] 110. KV-cache placement across SRAM, HBM, and external storage
- [ ] 111. MoE serving: routing, hot experts, and network pressure
- [ ] 112. Autoscaling TPU inference: batching, admission control, and capacity headroom
- [ ] 113. Multi-tenant inference: isolation versus utilization
- [ ] 114. Reasoning models: why longer sequential decode changes hardware balance

## Phase 16 — Datacenter architecture

- [ ] 115. TPU Pod versus datacenter: where the accelerator system ends
- [ ] 116. AI datacenter power architecture: utility → substation → UPS → rack → package
- [ ] 117. Cooling architecture: water, CDU, cold plate, and heat rejection
- [ ] 118. Capacity planning: chips are useless without power, network, and cooling
- [ ] 119. Storage/input pipeline: keeping trillion-token training jobs fed
- [ ] 120. Datacenter failure domains and maintenance strategy
- [ ] 121. Useful training throughput per MW: the system-level efficiency metric

## Phase 17 — Cross-architecture comparisons

These articles compare mechanisms, not brand rankings.

- [ ] 122. TPU systolic/MXU versus NVIDIA Tensor Core execution models
- [ ] 123. TPU ICI versus NVLink/NVSwitch: scale-up design philosophies
- [ ] 124. TPU versus AWS Trainium: compiler and system co-design
- [ ] 125. TPU inference versus Inferentia / MTIA / Maia: workload specialization
- [ ] 126. HBM-heavy versus SRAM-heavy inference architectures
- [ ] 127. General-purpose programmability versus domain-specific efficiency
- [ ] 128. Why benchmark peak FLOPs rarely predicts end-to-end model performance

## Phase 18 — Synthesis and forward-looking system questions

- [ ] 129. The complete TPU bottleneck history: compute → memory → communication → latency
- [ ] 130. What determines TPU cost per trained token
- [ ] 131. What determines TPU cost per generated token
- [ ] 132. Why future accelerators may specialize by AI lifecycle stage
- [ ] 133. Memory wall after HBM: SRAM, CXL-like expansion, compression, and recomputation
- [ ] 134. Optical scale-up: when electrical links stop scaling economically
- [ ] 135. 3D integration: logic-on-memory and thermal constraints
- [ ] 136. Reliability at million-accelerator scale
- [ ] 137. Co-designing model architecture with physical topology
- [ ] 138. The TPU design loop: how each generation exposes the next bottleneck

## Daily selection policy

Choose the next article using this order:

1. Continue the conceptual dependency chain from the most recent article.
2. Prefer the earliest unchecked topic when it is a prerequisite for later topics.
3. Interleave history and cross-layer mechanisms after the foundation is established.
4. If Google publishes a major new TPU disclosure, temporarily prioritize it only when it materially changes the knowledge tree; then return to the roadmap.
5. Never skip prerequisite concepts merely to cover the newest product.
