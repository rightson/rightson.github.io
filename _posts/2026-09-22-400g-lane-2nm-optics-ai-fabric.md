---
author: Scott Yo-Ru Chen
layout: post
title: "400G/lane 才是真正的拐點：2nm 光互連正在把 AI Fabric 推向 3.2T"
date: 2026-09-22 12:00:00 +0800
categories: networking optics ai-datacenter
---

今天真正值得注意的，不是「Marvell 做出 2nm optical DSP」這個製程新聞，而是 **400G/lane 正開始從實驗室能力走向可形成產品世代的技術基礎**。

如果這條路成立，下一代 AI Data Center 的變化不只是 1.6T optics 升成 3.2T。真正改變的是整個 network cost model：switch radix、front-panel density、SerDes power、optical reach，以及 pluggable、LPO、CPO 之間的邊界，都會重新洗牌。

## Why：AI Network 已經不是單純缺頻寬

AI cluster 的 networking 問題，本質上是三個限制同時逼近。

第一是 bandwidth density。102.4T switch ASIC 已經進入量產世代，單純增加 port 數量很快撞上 front panel、fiber count 與散熱限制。

第二是 power per bit。當 link 從 800G、1.6T 繼續往上，每個 port 的 DSP、SerDes、driver、TIA 都在吃 power budget。AI rack 本身已經被 XPU 與 HBM 吃掉大部分電力，network 不能再按照過去的比例擴張。

第三是 electrical reach。lane speed 越高，PCB trace 與 copper channel 的 insertion loss 越難處理。這也是為什麼 LPO、NPO、CPO 不再只是 optical packaging 的選項，而逐漸變成 system architecture 問題。

所以問題已經從：

> 怎樣做更快的 Ethernet？

變成：

> 怎樣在固定 power、thermal、panel area 下，把更多有效 bandwidth 搬進 XPU？

## How：400G/lane 為什麼比「3.2T」這個數字重要

Marvell 在 ECOC 2026 公布第一批 2nm optical interconnect demonstrations，其中最重要的是 400G/lane PAM4。

這不是第一次看到 400G/lane。Marvell 在 2025 年已經展示過完整 electrical-to-optical 400G/lane link，symbol rate 約 224 Gbaud。真正不同的是，這次把它推進到 2nm optical DSP 世代。

這代表重點開始從「能不能傳」轉向「能不能把 power per bit 壓到產品可接受範圍」。

今天主流高速 optics 正從 100G/lane 往 200G/lane 移動。若 400G/lane 成為下一代可部署 lane rate，在維持八條 optical lanes 的假設下：

    8 × 400G = 3.2T

這就是 3.2T pluggable 最直接的物理基礎。

但更大的意義是，同樣總頻寬所需要的 lane 數量可以下降。lane 越少，SerDes、光元件、fiber routing、package escape routing 的複雜度都有機會下降。

這才是 400G/lane 真正有價值的地方。

## 不只是 rack 內：Optical hierarchy 正在重新分層

Marvell 這次同時展示三種不同距離的 technology：

| Domain | Technology | Target reach |
|---|---|---|
| Data center / AI fabric | PAM4 | 約數百公尺 |
| Campus | O-band coherent-lite | 約 2–20 km |
| Data center interconnect | ZR / ZR+ coherent | 數十至數百公里以上 |

其中我認為 coherent-lite 特別值得注意。

過去 network architecture 常把 optics 粗略分成兩類：

    short reach PAM4
        ↓
    long reach coherent

但 AI data center 越蓋越大之後，中間多出了一個很實際的區域：**同一個 AI campus 內，不同 building 之間的 2–20 km。**

用傳統 IM-DD 很難一直往外延伸；直接使用完整 coherent 又可能在 cost、power、latency 上過度設計。

O-band coherent-lite 正是在填這個洞。

這代表未來 AI cluster 的 network boundary，可能不再等於 building boundary。

## Evidence：這次真正已經證明了什麼？

目前可以確認的是：

1. Marvell 公布 2nm 400G/lane optical PAM4 demonstration，目標明確指向 3.2T connectivity。
2. 2nm Libra coherent DSP 已進行 800G ZR/ZR+ + MACsec live demonstration。
3. 1.6T ZR 與 1.6T O-band coherent-lite 也進入 2nm demonstration。
4. 另一條路線上，Marvell 已展示 102.4T CPO platform，以 200G/lane silicon photonics 整合 optics 與 switch silicon。

但這裡要非常小心。

**Demonstration 不等於 volume deployment。**

目前 Marvell 並沒有在這次公告中提供 400G/lane 2nm solution 的量產時間、實際 module power、BER/FEC margin、link budget 或 hyperscaler deployment data。

所以今天能下的結論是「technology trajectory 已經很清楚」，不是「3.2T 已經成熟」。

## What changes：Switch ASIC 之後，瓶頸正在往 optics 移

過去幾個 switch generation，我們習慣看 ASIC bandwidth：

    12.8T → 25.6T → 51.2T → 102.4T

但到了 102.4T 之後，單純做出更大的 switching fabric 已經不夠。

如果 front panel optics、electrical channel 與 power budget 接不住，ASIC 裡面的 bandwidth 根本出不來。

所以接下來幾代 network 的真正競爭可能變成：

    Switch ASIC
        +
    SerDes
        +
    Optical DSP / LPO / CPO
        +
    Silicon Photonics
        +
    Packaging / Cooling

這也解釋為什麼 Broadcom、NVIDIA、Marvell 都開始把 switch silicon 與 optical architecture 綁在一起談。

## My take

我的第一個判斷：**3.2T 不是重點，400G/lane 才是。**

3.2T 只是 aggregate bandwidth；400G/lane 才是決定 lane count、front-panel density、power 與 packaging complexity 的底層變數。

第二個判斷：**CPO 不會立刻吃掉 pluggable，但 CPO 的必要性會隨 switch bandwidth 上升。**

Pluggable 最大優勢仍然是 serviceability 與成熟 ecosystem。但當 electrical reach 與功耗惡化到某個臨界點，把 optics 拉近 ASIC 就不再只是效率優化，而是物理限制。

第三個判斷：**AI networking 的 L1 正重新變成 architecture 的一部分。**

以前 network engineer 可以把 optics 當成「選對 transceiver 就好」。

這個假設正在失效。

未來要理解 AI Fabric，不能只懂 ECMP、RDMA、congestion control、routing。SerDes、PAM4、FEC、coherent、CPO 與 optical power budget，會直接決定 L2/L3 以上能建出什麼 topology。

這也是我認為今天這個訊號真正重要的地方：

**AI Data Center Networking 正從 protocol-defined network，走向 physics-constrained network。**

---

## References

1. Marvell, “Industry-First 2nm Optical Technology Demos for AI Data Center Infrastructure at ECOC 2026,” Sep. 2026.  
   https://www.marvell.com/company/newsroom/marvell-industry-first-2nm-optical-technology-ai-data-center-infrastructure-ecoc-2026.html

2. Marvell, “Industry's First 400G/lane PAM4 Electrical-to-Optical Link Technology,” Mar. 2025.  
   https://investor.marvell.com/news-events/press-releases/detail/105/marvell-to-demonstrate-industrys-first-400glane-pam4-electrical-to-optical-link-technology-at-ofc-2025

3. Marvell, “Optical DSPs — Powering the Future of AI Infrastructure.”  
   https://www.marvell.com/solutions/data-center/optical-dsp.html

4. Marvell, “Aquila O-Band Coherent-Lite DSP for 800G/1.6T Optical Transceiver.”  
   https://www.marvell.com/products/coherent-lite-dsp.html

5. Marvell, “Co-packaged Optics: Powering the Next Wave of AI Data Center Innovation.”  
   https://www.marvell.com/blogs/co-packaged-optics-for-next-wave-ai-data-centers.html
