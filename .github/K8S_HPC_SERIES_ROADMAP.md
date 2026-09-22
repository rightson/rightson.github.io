# Kubernetes / HPC Systems Technical Series Roadmap

> Internal editorial roadmap for the Kubernetes deep-dive series on rightson.github.io.
> This file is not a Jekyll post. Public posts must follow `AGENTS.md`.
> Last architecture boundary review: 2026-09-22.

## Objective

Build a coherent systems curriculum that starts from Kubernetes' distributed control-plane model and descends all the way to Linux kernel scheduling, cgroups, namespaces, virtual memory, page cache, block I/O, TCP/IP, RDMA, NIC queues, storage protocols, SAN/NFS, filesystems, NUMA and hardware topology, then climbs back up into large-scale distributed AI, EDA, IC design, foundry and HPC production systems.

The core dependency chain is:

`user intent / workload → Kubernetes API → controllers → scheduler → kubelet / CRI → OCI runtime → Linux kernel → CPU / memory / I/O / NIC / storage → rack / fabric / cluster → distributed application`

Every article must answer:

1. Why does this mechanism exist?
2. What lower-layer mechanism actually implements it?
3. Which bottleneck or failure mode does it solve?
4. Which performance, isolation, reliability, or operability trade-off does it create?
5. For AI / EDA / IC / Foundry / HPC, when is Kubernetes the right control plane, and when should Slurm / LSF / bare metal / VM / dedicated appliances remain in the path?

## Editorial constraints

- Read `AGENTS.md`, this roadmap and recent `_posts/` before writing.
- Minimum depth: at least a **5-minute read**; target roughly 2,500–4,500 Traditional Chinese characters excluding front matter/references. Deep kernel/network/storage topics may be much longer.
- Each post handles one primary topic but must explain the layers above and below it.
- At least one concrete example, trace, syscall path, packet path, queueing model, topology mapping, YAML-to-kernel mapping, or performance calculation.
- Prefer primary sources: Kubernetes docs/KEPs/source, Linux kernel docs/source, OCI/runc/containerd/CRI-O/CNI/CSI specs, IETF/RFC, IEEE, RDMA Consortium, NFS/SCSI/NVMe specifications, vendor architecture papers, peer-reviewed systems papers.
- Use 2–4 technically useful visuals where appropriate: architecture, sequence, data path, kernel path, topology, performance/queueing diagram, or comparison table.
- Every visual/table requires a caption and traceable source. Redrawn diagrams must say “依據 XXX 重繪/整理”.
- Separate public fact, reported experiment, and author inference.
- Never reduce HPC to “containers + autoscaling”. Explicitly account for topology, gang scheduling, license constraints, MPI collectives, RDMA, filesystem metadata, scratch I/O, NUMA, CPU pinning, hugepages, device locality, job preemption, checkpoint/restart and deterministic reproducibility.
- Mark an item `[x]` only after the public post is committed and the production page is verified.

## Current upstream boundary — 2026-09-22

Kubernetes v1.37 is the current release line. Important recent directions relevant to this series include:
- Workload-Aware Scheduling / PodGroup / gang scheduling moving toward first-class support.
- Dynamic Resource Allocation (DRA) becoming increasingly important for GPUs, NICs and other devices.
- cgroup v2-based Memory QoS and pod-level resource management.
- rootless node component work and deeper Linux user-namespace integration.

Primary references:
- https://kubernetes.io/docs/concepts/overview/components/
- https://kubernetes.io/blog/2026/09/08/kubernetes-v1-37-advancing-workload-aware-scheduling/
- https://kubernetes.io/blog/2026/09/03/kubernetes-v1-37-dra-updates/
- https://www.kernel.org/doc/html/latest/admin-guide/cgroup-v2.html

---

## Phase 1 — What Kubernetes actually is

- [ ] 001. Kubernetes is a distributed reconciliation control plane, not merely a container scheduler  
  Post committed and Pages deployed; live-page verification pending: `_posts/2026-09-22-kubernetes-control-plane-hpc-foundation.md`
- [ ] 002. Desired state vs current state: why reconciliation loops scale operational intent
- [ ] 003. kube-apiserver: REST semantics, admission, storage, watches and the cluster's serialization point
- [ ] 004. etcd: Raft, quorum, linearizable reads, MVCC, watch and compaction
- [ ] 005. kube-controller-manager: level-triggered control loops and idempotency
- [ ] 006. kube-scheduler: queue → filter → score → reserve → permit → bind
- [ ] 007. kubelet: where declarative cluster intent becomes node-local process state
- [ ] 008. Node heartbeats, Leases, taints and the failure-detection problem
- [ ] 009. Pods: why Kubernetes schedules a resource-sharing envelope instead of individual processes
- [ ] 010. Deployments/ReplicaSets/StatefulSets/DaemonSets/Jobs: different control semantics
- [ ] 011. Why Kubernetes chose API objects and controllers over a monolithic orchestrator
- [ ] 012. What Kubernetes deliberately does not solve: distributed databases, MPI semantics, filesystems and application correctness

## Phase 2 — From Pod YAML to Linux processes

- [ ] 013. End-to-end Pod creation: kubectl → API server → etcd → scheduler → kubelet → CRI → runtime
- [ ] 014. OCI runtime spec: config.json, rootfs and lifecycle
- [ ] 015. containerd architecture: daemon, shim, snapshots and OCI runtime
- [ ] 016. runc: clone/unshare/setns/mount/pivot_root and exec
- [ ] 017. CRI: why Kubernetes stopped speaking Docker directly
- [ ] 018. Image layers and overlayfs: lowerdir/upperdir/workdir/merged
- [ ] 019. Copy-on-write: performance implications for compiler/EDA scratch-heavy workloads
- [ ] 020. PID namespace: process trees, init, orphan reaping and signals
- [ ] 021. Mount namespace: bind mounts, propagation and volume semantics
- [ ] 022. Network namespace: netns, veth pairs, loopback and routing tables
- [ ] 023. User namespace: UID/GID remapping and rootless execution
- [ ] 024. UTS/IPC/time namespaces and why some HPC workloads care

## Phase 3 — cgroups and Linux resource control

- [ ] 025. cgroup v2 hierarchy: the actual kernel substrate behind Kubernetes resource control
- [ ] 026. CPU requests/limits → cpu.weight/cpu.max: what Kubernetes really writes
- [ ] 027. CFS bandwidth control: quota/period, throttling and latency cliffs
- [ ] 028. CPU Manager static policy: exclusive CPUs, cpusets and HPC determinism
- [ ] 029. cpuset.cpus and cpuset.mems: CPU/NUMA locality from the kernel's point of view
- [ ] 030. Memory requests/limits → memory.low/high/max
- [ ] 031. Memory QoS, reclaim and why “limit” is not a reservation
- [ ] 032. Linux OOM killer, memcg OOM and Kubernetes OOMKilled
- [ ] 033. page cache accounting inside cgroups
- [ ] 034. io.max/io.weight: block I/O control and noisy-neighbor limits
- [ ] 035. PSI: cpu.pressure, memory.pressure and io.pressure as saturation signals
- [ ] 036. PIDs controller: fork bombs, process limits and EDA tool fan-out
- [ ] 037. HugeTLB controller and hugepages for high-performance workloads
- [ ] 038. cgroup freezer and checkpoint-related mechanisms

## Phase 4 — Linux CPU scheduling, NUMA and memory

- [ ] 039. Linux CFS/EEVDF scheduling and what a container actually competes for
- [ ] 040. runqueues, scheduler domains and load balancing
- [ ] 041. CPU affinity and cache locality
- [ ] 042. SMT/Hyper-Threading interference: why “1 CPU” is not a physical core
- [ ] 043. NUMA fundamentals: sockets, nodes, local/remote memory latency
- [ ] 044. Automatic NUMA balancing and why it can hurt deterministic HPC
- [ ] 045. Topology Manager: aligning CPU, memory and PCIe devices
- [ ] 046. Memory Manager: reserved memory and NUMA-aware allocation
- [ ] 047. virtual memory: mmap, page faults, anonymous vs file-backed pages
- [ ] 048. TLB, hugepages and page-table cost
- [ ] 049. transparent huge pages: when THP helps and when it creates tail latency
- [ ] 050. page cache and writeback: why “storage latency” often starts in memory
- [ ] 051. dirty pages, flusher threads and writeback throttling
- [ ] 052. mmap-heavy EDA applications and container memory accounting
- [ ] 053. memory bandwidth saturation: the bottleneck Kubernetes cannot schedule directly

## Phase 5 — Container networking down to the kernel

- [ ] 054. Kubernetes network model: every Pod gets an IP — what that actually requires
- [ ] 055. CNI: ADD/DEL/CHECK lifecycle and network plugin contracts
- [ ] 056. veth → bridge → routing: the baseline Linux container packet path
- [ ] 057. Linux routing, FIB lookup, neighbor tables and ARP/ND
- [ ] 058. iptables datapath: netfilter hooks, conntrack and NAT
- [ ] 059. IPVS service load balancing
- [ ] 060. eBPF service datapath: hooks, maps, verifier, JIT and tail calls
- [ ] 061. XDP: processing before skb allocation
- [ ] 062. tc BPF: ingress/egress hooks and policy enforcement
- [ ] 063. kube-proxy versus eBPF replacement
- [ ] 064. overlay networking: VXLAN/Geneve encapsulation and MTU tax
- [ ] 065. underlay routed Pod networking: BGP and route distribution
- [ ] 066. Calico architecture: routing vs policy
- [ ] 067. Cilium architecture: eBPF identity, service and policy
- [ ] 068. NetworkPolicy: where Kubernetes intent meets kernel enforcement
- [ ] 069. conntrack scaling: hash tables, timeouts and failure modes
- [ ] 070. RSS/RPS/RFS/XPS: NIC receive queues and CPU placement
- [ ] 071. NAPI, softirq and packet processing under load
- [ ] 072. GRO/GSO/TSO/LRO offloads and container networking
- [ ] 073. TCP socket buffers, autotuning and bandwidth-delay product
- [ ] 074. TCP congestion control: CUBIC, BBR and datacenter implications
- [ ] 075. ECN/DCTCP concepts for east-west HPC/AI traffic
- [ ] 076. irqbalance, IRQ affinity and latency-sensitive nodes
- [ ] 077. Multus: multiple interfaces inside one Pod
- [ ] 078. SR-IOV CNI: VF passthrough, IOMMU and near-native latency
- [ ] 079. DPDK in Kubernetes: userspace networking and hugepages
- [ ] 080. SmartNIC/DPU offload and the changing node boundary

## Phase 6 — RDMA, RoCE and HPC communication

- [ ] 081. RDMA fundamentals: verbs, QP, CQ, MR and zero-copy
- [ ] 082. InfiniBand architecture: HCA, subnet manager and fabric
- [ ] 083. RoCEv2: RDMA semantics over Ethernet/UDP/IP
- [ ] 084. PFC, ECN and congestion control for loss-sensitive RDMA
- [ ] 085. GPUDirect RDMA and the PCIe/NIC/GPU data path
- [ ] 086. RDMA device plugin / DRA and Kubernetes resource allocation
- [ ] 087. SR-IOV + RDMA: VF placement, NUMA and topology alignment
- [ ] 088. MPI on Kubernetes: launcher, rank placement and network identity
- [ ] 089. NCCL collectives: rings, trees and topology sensitivity
- [ ] 090. UCX: transport selection across TCP/RDMA/shared memory
- [ ] 091. When TCP is enough and when RDMA changes the economics
- [ ] 092. Tail latency and jitter sources from userspace to NIC

## Phase 7 — Storage from VFS to SAN/NFS

- [ ] 093. Kubernetes volumes: lifecycle semantics before protocols
- [ ] 094. CSI architecture: controller service, node service and sidecars
- [ ] 095. Linux VFS: dentries, inodes, file descriptors and page cache
- [ ] 096. ext4/XFS local filesystems and container workloads
- [ ] 097. block layer: bio, request queues and blk-mq
- [ ] 098. NVMe: submission/completion queues and PCIe locality
- [ ] 099. NVMe-oF: TCP vs RDMA transports
- [ ] 100. SCSI stack and traditional SAN
- [ ] 101. Fibre Channel SAN: fabric, zoning, LUNs and multipath
- [ ] 102. iSCSI: SCSI over TCP and queueing implications
- [ ] 103. multipath I/O: availability versus latency variance
- [ ] 104. NFS architecture: client cache, RPC, metadata and locking
- [ ] 105. NFSv3 vs NFSv4 and HPC/EDA behavior
- [ ] 106. pNFS: metadata/data path separation
- [ ] 107. NFS over RDMA: what is actually accelerated
- [ ] 108. SMB/CIFS in mixed enterprise clusters
- [ ] 109. Ceph RBD/CephFS: object layer, CRUSH and replication
- [ ] 110. Lustre: MDS/MDT, OSS/OST and parallel I/O
- [ ] 111. IBM Spectrum Scale / GPFS concepts
- [ ] 112. BeeGFS: metadata/data striping for HPC
- [ ] 113. object storage: S3 semantics vs POSIX semantics
- [ ] 114. local NVMe scratch + remote durable storage: the two-tier pattern
- [ ] 115. metadata storms: why millions of EDA small files break shared filesystems
- [ ] 116. IOPS vs bandwidth vs latency: choosing storage for EDA versus AI
- [ ] 117. fsync, durability and distributed filesystem semantics
- [ ] 118. direct I/O vs buffered I/O
- [ ] 119. mmap + NFS/SAN: page faults, coherence and pathological workloads
- [ ] 120. CSI topology, volume binding and data locality

## Phase 8 — Scheduling: from Pods to HPC jobs

- [ ] 121. Kubernetes scheduler framework internals
- [ ] 122. scheduling queues and backoff
- [ ] 123. predicates/filters: feasibility before optimization
- [ ] 124. scoring plugins and multi-objective placement
- [ ] 125. affinity, anti-affinity and topology spread
- [ ] 126. taints/tolerations and dedicated HPC pools
- [ ] 127. priorities and preemption
- [ ] 128. PodGroup / gang scheduling: why distributed jobs must start together
- [ ] 129. Workload-Aware Scheduling in Kubernetes v1.37
- [ ] 130. hierarchical queues and fair-share
- [ ] 131. Kueue architecture: admission before Pod scheduling
- [ ] 132. Volcano: batch/HPC scheduling extensions
- [ ] 133. Slurm architecture: slurmctld, slurmd, partitions and backfill
- [ ] 134. IBM Spectrum LSF architecture: queues, hosts, jobs and resource strings
- [ ] 135. Kubernetes vs Slurm vs LSF: control-plane semantics, not feature checklists
- [ ] 136. backfill scheduling and why it matters for expensive accelerators
- [ ] 137. reservations, quotas and project accounting
- [ ] 138. license-aware scheduling for EDA tools
- [ ] 139. topology-aware GPU/NIC/CPU placement
- [ ] 140. bin packing versus fragmentation
- [ ] 141. checkpoint-aware preemption
- [ ] 142. deadline scheduling and tape-out-critical workloads

## Phase 9 — Devices, GPUs, FPGAs and accelerators

- [ ] 143. Device Plugin API: how Kubernetes originally exposed GPUs
- [ ] 144. DRA architecture: ResourceClaim, DeviceClass and richer device allocation
- [ ] 145. NVIDIA GPU Operator: driver/runtime/device management
- [ ] 146. GPU MIG: hardware partitioning and scheduling
- [ ] 147. GPU time slicing versus MIG versus exclusive allocation
- [ ] 148. PCIe topology and peer-to-peer placement
- [ ] 149. NVLink/NVSwitch locality and scheduling
- [ ] 150. FPGA allocation and bitstream lifecycle
- [ ] 151. SmartNIC/DPU allocation
- [ ] 152. hugepages and pinned memory for devices
- [ ] 153. IOMMU, VFIO and device passthrough

## Phase 10 — Kubernetes controllers, operators and platform APIs

- [ ] 154. CRDs: extending the API without forking Kubernetes
- [ ] 155. controller-runtime: informer, cache, workqueue and reconcile
- [ ] 156. informers and watches: scaling event-driven controllers
- [ ] 157. workqueues: rate limiting, retries and eventual convergence
- [ ] 158. finalizers and deletion semantics
- [ ] 159. ownerReferences and garbage collection
- [ ] 160. status/conditions: building observable state machines
- [ ] 161. operators for stateful distributed systems
- [ ] 162. idempotency and crash recovery in controllers
- [ ] 163. control-plane backpressure and API rate limits
- [ ] 164. designing a domain-specific HPC/EDA API on top of Kubernetes

## Phase 11 — Distributed-systems foundations

- [ ] 165. consensus: Raft and etcd quorum
- [ ] 166. leases, heartbeats and failure detectors
- [ ] 167. linearizability, serializability and stale reads
- [ ] 168. idempotency and at-least-once delivery
- [ ] 169. level-triggered vs edge-triggered control
- [ ] 170. eventual consistency in controllers
- [ ] 171. leader election
- [ ] 172. distributed locks: why they are often overused
- [ ] 173. split brain and fencing
- [ ] 174. CAP theorem: useful boundaries and common misuse
- [ ] 175. queueing theory for cluster control planes
- [ ] 176. backpressure, admission control and overload collapse
- [ ] 177. retries, exponential backoff and retry storms
- [ ] 178. circuit breakers and bulkheads
- [ ] 179. clock skew, monotonic time and distributed deadlines
- [ ] 180. distributed tracing across control and data planes

## Phase 12 — Observability from kernel to cluster

- [ ] 181. Kubernetes metrics/logs/traces and their blind spots
- [ ] 182. cAdvisor, CRI stats and cgroup counters
- [ ] 183. kube-state-metrics: desired state versus runtime state
- [ ] 184. Prometheus pull model and cardinality
- [ ] 185. histogram design for tail latency
- [ ] 186. OpenTelemetry traces through controllers and workloads
- [ ] 187. eBPF observability: kprobes, tracepoints, uprobes and ring buffers
- [ ] 188. perf: CPU sampling and flame graphs
- [ ] 189. ftrace and scheduler tracing
- [ ] 190. bpftrace for production diagnosis
- [ ] 191. PSI + cgroups as node pressure observability
- [ ] 192. block I/O tracing: biosnoop/biolatency concepts
- [ ] 193. TCP tracing: retransmits, RTT and socket queues
- [ ] 194. correlating EDA job slowdown with CPU/NUMA/storage/network signals

## Phase 13 — Reliability and failure engineering

- [ ] 195. control-plane HA: API servers, etcd quorum and failure domains
- [ ] 196. etcd backup/restore and disaster recovery
- [ ] 197. node failure: detection, eviction and rescheduling
- [ ] 198. graceful node shutdown
- [ ] 199. PodDisruptionBudget and maintenance
- [ ] 200. StatefulSet identity and ordered recovery
- [ ] 201. storage attach/detach failure modes
- [ ] 202. network partition scenarios
- [ ] 203. split-brain prevention for stateful systems
- [ ] 204. chaos testing versus controlled fault injection
- [ ] 205. checkpoint/restart for HPC jobs
- [ ] 206. MTTR versus recomputation cost in AI/EDA clusters

## Phase 14 — Security to the kernel boundary

- [ ] 207. authentication, authorization and admission
- [ ] 208. RBAC internals and authorization evaluation
- [ ] 209. service accounts and projected tokens
- [ ] 210. seccomp syscall filtering
- [ ] 211. Linux capabilities
- [ ] 212. SELinux/AppArmor confinement
- [ ] 213. user namespaces and rootless Kubernetes
- [ ] 214. privileged containers: what isolation is bypassed
- [ ] 215. supply-chain security: image provenance and signing
- [ ] 216. secrets: etcd encryption and node exposure
- [ ] 217. network segmentation for multi-tenant EDA/HPC
- [ ] 218. RDMA/SR-IOV isolation limits

## Phase 15 — AI training and inference on Kubernetes

- [ ] 219. Why AI clusters stress Kubernetes differently from web services
- [ ] 220. distributed training lifecycle: admission → gang schedule → topology → collectives
- [ ] 221. GPU/CPU/NIC/NUMA co-scheduling
- [ ] 222. Kubernetes + NCCL + RDMA data path
- [ ] 223. topology-aware placement for NVLink/RDMA fabrics
- [ ] 224. Kueue/PodGroup for large training jobs
- [ ] 225. checkpoint storage architecture for trillion-parameter training
- [ ] 226. local NVMe caching for datasets/checkpoints
- [ ] 227. inference serving: autoscaling versus accelerator saturation
- [ ] 228. prefill/decode disaggregation on Kubernetes
- [ ] 229. multi-tenant GPU inference
- [ ] 230. AI job preemption and checkpoint economics

## Phase 16 — EDA and IC design on Kubernetes

- [ ] 231. Why traditional EDA farms use LSF/Slurm and shared POSIX storage
- [ ] 232. EDA workload taxonomy: synthesis, APR, STA, DV, DFT and signoff
- [ ] 233. License servers as a first-class scheduling resource
- [ ] 234. millions of small files: metadata behavior of EDA flows
- [ ] 235. NFS/SAN/Lustre/BeeGFS trade-offs for EDA
- [ ] 236. local scratch + artifact promotion pattern
- [ ] 237. Tcl/Makefile/LSF flows mapped into Kubernetes Jobs
- [ ] 238. preserving deterministic tool environments with containers
- [ ] 239. CPU pinning/NUMA for place-and-route
- [ ] 240. memory-heavy STA/APR and memcg pitfalls
- [ ] 241. GUI/X11/VNC/code-server access to EDA containers
- [ ] 242. long-lived interactive engineering sessions vs batch Pods
- [ ] 243. tool daemon/licensing/network dependencies
- [ ] 244. checkpoint and restart around EDA stage boundaries
- [ ] 245. artifact lineage and immutable run metadata
- [ ] 246. K8s as control plane over existing LSF execution
- [ ] 247. hybrid migration: which EDA workloads should not move first
- [ ] 248. tape-out-critical reliability and priority isolation
- [ ] 249. multi-project/foundry PDK security boundaries
- [ ] 250. building an R2G control plane without replacing every execution backend

## Phase 17 — Foundry / semiconductor HPC

- [ ] 251. Foundry HPC workload taxonomy: OPC, lithography simulation, extraction, TCAD, verification
- [ ] 252. embarrassingly parallel vs tightly coupled semiconductor workloads
- [ ] 253. massive shared filesystem metadata and namespace design
- [ ] 254. petabyte-scale scratch and lifecycle management
- [ ] 255. MPI/RDMA workloads in semiconductor simulation
- [ ] 256. NUMA and memory-bandwidth-dominated simulation
- [ ] 257. proprietary license scheduling
- [ ] 258. sensitive PDK/data isolation in multi-tenant clusters
- [ ] 259. air-gapped/on-prem Kubernetes constraints
- [ ] 260. Kubernetes over bare metal with deterministic networking/storage
- [ ] 261. coexistence with Slurm/LSF in foundry environments
- [ ] 262. capacity planning for deadline-driven tape-out workloads

## Phase 18 — Bare-metal cluster architecture

- [ ] 263. bare metal vs VM for HPC Kubernetes
- [ ] 264. PXE/provisioning lifecycle and immutable node images
- [ ] 265. firmware/BIOS settings for performance determinism
- [ ] 266. NUMA, PCIe switches and accelerator topology
- [ ] 267. rack-level network design
- [ ] 268. leaf-spine Ethernet for Kubernetes/HPC
- [ ] 269. InfiniBand fabric alongside Ethernet control plane
- [ ] 270. storage network separation
- [ ] 271. BMC/Redfish and node lifecycle automation
- [ ] 272. hardware failure domains and rack-aware scheduling

## Phase 19 — Scale, performance and control-plane limits

- [ ] 273. Kubernetes scale limits: what actually saturates first
- [ ] 274. API Priority and Fairness
- [ ] 275. watch fan-out and informer cache pressure
- [ ] 276. etcd write amplification and object size
- [ ] 277. scheduler throughput and queue latency
- [ ] 278. kubelet scalability: pods per node and housekeeping
- [ ] 279. image distribution at thousands of nodes
- [ ] 280. DNS scaling and CoreDNS failure modes
- [ ] 281. service/EndpointSlice scaling
- [ ] 282. network policy rule explosion
- [ ] 283. cluster sharding vs giant clusters
- [ ] 284. multi-cluster placement and federation
- [ ] 285. control-plane SLOs for HPC submission bursts

## Phase 20 — Economics and architectural synthesis

- [ ] 286. utilization vs determinism: why maximum packing can reduce HPC throughput
- [ ] 287. compute utilization is not application throughput
- [ ] 288. storage/network contention as hidden scheduling dimensions
- [ ] 289. control plane vs data plane: where Kubernetes should stop
- [ ] 290. when Kubernetes should orchestrate Slurm/LSF instead of replacing them
- [ ] 291. when VMs are still the better isolation boundary
- [ ] 292. when bare metal is required
- [ ] 293. platform abstraction vs performance transparency
- [ ] 294. designing an HPC platform around evidence, not “cloud native” ideology
- [ ] 295. AI vs EDA vs Foundry: why one scheduler policy cannot optimize all three
- [ ] 296. the complete path: YAML → controller → scheduler → kubelet → kernel → NIC/storage → distributed job
- [ ] 297. building a semiconductor-scale compute control plane
- [ ] 298. the future: workload-aware scheduling, DRA, topology, eBPF and composable accelerators

## Daily selection policy

1. Start with Phase 1 and follow conceptual prerequisites. If an item already has a public post path or matching `_posts/` article, do not rewrite it even if live-page verification is still pending; continue to the next unwritten topic.
2. Interleave abstraction-level articles with low-level mechanism articles once fundamentals exist.
3. Before a deep applied AI/EDA/Foundry article, ensure the required kernel/network/storage/scheduler prerequisites are already covered or explicitly linked.
4. If a major Kubernetes/kernel/storage/network release materially changes the architecture, insert a new roadmap item rather than silently rewriting history.
5. Never present Kubernetes as inherently superior to Slurm/LSF/VM/bare metal. Compare based on workload semantics and mechanism.
