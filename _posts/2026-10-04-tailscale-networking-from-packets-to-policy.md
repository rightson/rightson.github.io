---
layout: post
title: "Tailscale 如何讓不同網路的電腦安全互連"
date: 2026-10-04 20:30:06 +0800
domain: networking
categories: networking
description: "從 IP 路由與 NAT 推導 Tailscale 的身分協調、WireGuard 加密、直連與中繼，追蹤 SSH、NAS 與出口節點的完整封包路徑，並以實驗拆解權限、回程路由與效能問題。"
takeaways:
  - who: "遠端開發者"
    value: "遠端開發者透過 Tailscale 的穩定位址、身分協調與自動路徑探索，可以跨越家用與行動網路連回主機，減少逐台設定公開入口的工作；實際速度仍受上傳頻寬、直連成功率與端點處理能力限制。"
  - who: "WireGuard"
    value: "WireGuard 負責節點間的加密與驗證，Tailscale 再補上登入、金鑰分發、NAT 穿透與規則管理，讓多人多機的維運更容易；採用者因此把部分網路管理工作移到身分系統與協調服務。"
  - who: "網路管理員"
    value: "網路管理員藉由 grants 限定哪些身分能連到哪些服務，再以 subnet router 接入既有設備；管理員同時承擔路由核准、回程、節點金鑰與權限更新的責任，廣泛允許規則會削弱隔離效果。"
  - who: "Tailscale"
    value: "Tailscale 的直連與中繼都在節點之間保留 WireGuard 加密，中繼服務承擔額外轉送成本；當流量經過 subnet router 或 exit node，隧道終點移到路由器，後段資料保護須由應用協定接續。"
---

人在外面，想從筆電連回家中的 Linux 主機。主機可以上網，筆電也可以上網，但把主機的 `192.168.50.20` 填進 SSH，連線卻沒有成功。兩台設備都有網際網路連線，仍然缺少一條可以互相找到、通過防火牆，而且知道對方身分的路徑。

家用路由器的設計原本很合理：多台設備共用一個對外位址，內部主機先發出請求，再讓回覆沿既有狀態回來。困難出現在需求改變時。主機要接受外面的連線，手機可能使用電信商的 CGNAT，筆電會切換 Wi-Fi，而雲端資源又有自己的網路規則。逐一配置 port forwarding、固定 IP 與 VPN gateway，會讓連線設定緊跟著實體網路變動。

Tailscale 建立一層以設備身分為基礎的 IP 網路：設備保有相對穩定的虛擬位址，系統協調公鑰與權限，尋找可用的傳輸路徑，再用 WireGuard 保護兩端之間的封包。先看下面的情境圖；兩邊的私有位址只在各自網路有意義，教學要解決的是跨越這兩個網路的連線。[Tailscale 架構說明](https://tailscale.com/blog/how-tailscale-works)

![外出的筆電與家中主機分別位於不同 NAT 後方；兩個區域網路的私有位址沒有共同路由](/images/networking/2026-10-04/tailscale-background.svg)

圖 1：參考設計。公網位址使用文件保留範圍；實線表示各自已有的對外路徑，虛線表示尚待建立的跨網路連線。NAT 概念依據 [RFC 4787](https://www.rfc-editor.org/rfc/rfc4787)。

讀完後，應能自行解釋四件事：為何兩台設備可以直接互連、直連失敗時封包改走哪裡、授權與路由為何需要分開處理，以及連上之後速度由哪些因素決定。以下先建立最小網路模型，再逐步加入 Tailscale 的機制。

## 1. 能上網與能被別人連進來，是兩個不同的條件

IP 網路傳送封包，需要目的位址與路由。路由器根據目的位址選擇下一站；封包能到達服務，還需要通過沿途過濾規則、抵達正確 port，且程式確實在接收連線。

假設家中主機是 `192.168.50.20`，路由器 LAN 位址是 `192.168.50.1`。私有 IPv4 位址可以在不同家庭重複使用，因此網際網路無法只憑這個位址判斷你要去誰家。筆電所在的旅館甚至可能也有一台 `192.168.50.20`。私有位址的用途與範圍由 [RFC 1918](https://www.rfc-editor.org/rfc/rfc1918) 定義。

主機向外發送 UDP 封包時，NAT 可以把：

`192.168.50.20:41641 → 外部目的地`

改成：

`203.0.113.10:62001 → 外部目的地`

NAT 另外保存轉換紀錄，回覆抵達 `203.0.113.10:62001` 才能被轉回原來的主機。這裡的 `62001` 是假設分配結果，實際值由 NAT 決定。

此時要分開理解兩種行為：

| 行為 | 路由器決定什麼 | 對互連的影響 |
| --- | --- | --- |
| Mapping | 一個內部來源送到不同外部目的地，是否沿用同一個外部位址與 port | 決定探測到的外部入口能否拿給另一個 peer 使用 |
| Filtering | 外部哪些來源可以透過既有 mapping 送進來 | 決定知道入口之後，封包是否會被接收 |

2007 年的 [RFC 4787 §4–5](https://www.rfc-editor.org/rfc/rfc4787#section-4) 已經把 mapping 與 filtering 分開描述。這比只背「full-cone、symmetric NAT」更有助於推導連線成敗：同樣有 NAT，不同的轉換與過濾行為會產生不同結果。

先做一個小檢查：把 SSH port 從 22 改成 2222，會讓兩個私有網路突然擁有彼此的路由嗎？答案是否定的。port 指出主機上哪個服務要接收資料；IP 路由負責把封包送到那台主機。改 port 可以改變服務入口，尋路問題仍然存在。

## 2. 把設備的穩定位址與目前所在的位置分開

用郵件來類比，收件人的名字可以穩定，收件人今天在哪裡則會改變。網路也可以做相似分工：

- **Overlay 位址**：應用程式用來辨認遠端設備的虛擬 IP。
- **Underlay endpoint**：目前能在實體網路上接觸到該設備的 IP 與 port。
- **Cryptographic identity**：用公鑰識別 peer，並驗證資料確實來自持有對應私鑰的端點。

Tailscale 通常從 `100.64.0.0/10` 配發 IPv4 位址，另使用 `fd7a:115c:a1e0::/48` 的 IPv6 範圍。前者也是電信商 CGNAT 可使用的共享位址範圍，沒有全球唯一、可公開路由的意義；設備位址在其 Tailscale 管理脈絡中使用。[保留位址說明](https://tailscale.com/docs/reference/reserved-ip-addresses)

假設筆電的 Tailscale IP 是 `100.90.0.10`，家中主機是 `100.90.0.20`。應用程式可以一直連 `100.90.0.20`，底下的對外 endpoint 則從家用 Wi-Fi 的位址換成其他可用路徑。設備被移除、重新建立或重新配置，仍可能影響位址；「穩定」描述的是正常設備生命週期中的行為。

Overlay 在這裡是一個 Layer 3 IP 網路。兩台機器能互通 IP 封包，並沒有因此共用 Ethernet 廣播網域。依賴 LAN 廣播尋找設備的程式，需要另外設計發現機制。像 Wake-on-LAN 可以由遠端呼叫家中一台持續開機的 helper，再由 helper 在家中送出 Layer 2 封包。[Tailscale 的 WoL 技術說明](https://tailscale.com/blog/wake-on-lan-tailscale-upsnap)

**Tailnet** 是由 Tailscale 管理的網路集合與授權脈絡。加入同一個 tailnet，讓設備具備接受協調與規則的資格；每一條服務連線仍要符合設定的存取政策。

## 3. WireGuard 負責安全隧道，Tailscale 補齊網路的管理工作

先想像只有兩台固定位置的機器。你手動交換公鑰、指定彼此的 endpoint、設定隧道位址與路由，就能用 WireGuard 建立加密通訊。

設備增加後，工作會擴張：誰能加入、離職者怎麼移除、伺服器的位址改變怎麼處理、peer 公鑰怎麼更新、限制誰能碰資料庫，以及 NAT 後面怎麼找到入口。Tailscale 把這些事情組合成系統。

| 工作 | WireGuard 提供的基礎 | Tailscale 增加的機制 |
| --- | --- | --- |
| 保護節點間封包 | 加密、驗證、重放防護與 session key 更新 | 整合到 client 的傳輸路徑 |
| 識別 peer | peer 公鑰與允許的隧道 IP | 連接登入身分、設備資訊與 tags |
| 找到對方 | 可設定與更新 endpoint | 探測、協調與 NAT 穿透 |
| 維護多人多機 | 由外部配置管理 | 公鑰分發、設備管理與政策分發 |
| 沒有直接路徑 | 需要外部系統安排 | DERP 與已配置的 Peer Relay |

WireGuard 的 **Cryptokey Routing** 把 peer 公鑰與隧道 IP 範圍關聯起來：送出時依目的 IP 找 peer；接收時驗證這個 peer 是否能使用封包聲稱的來源 IP。這給隧道內的 IP 身分一個密碼學基礎。[WireGuard 技術概覽](https://www.wireguard.com/#cryptokey-routing)

其協定使用 Noise 型握手，透過 Curve25519 等機制建立金鑰材料，再以 ChaCha20-Poly1305 保護資料封包。長期公鑰協助確認 peer，實際資料加密使用協商出的對稱 session key；session key 會更新。因此，「用 peer 公鑰保護封包」是概念簡寫，完整機制包含握手與 session key。[WireGuard Protocol & Cryptography](https://www.wireguard.com/protocol/)

理解到這裡，可以把「隧道安全」與「管理便利」分開評估。只有少量、固定且可互達的設備，手動 WireGuard 很合理；多人、行動設備與複雜 NAT，則會增加自動協調的收益。

## 4. 協調服務保存網路關係，端點負責傳送資料

Tailscale 系統有兩種不同工作。

**Control plane** 管理哪些設備存在、設備的公鑰、可用 endpoint 與政策。**Data plane** 承載應用程式的封包。Tailscale 的 coordination server 參與前者；資料則在設備間直連，或經 relay 轉送。

2020 年 3 月 20 日的 [How Tailscale works](https://tailscale.com/blog/how-tailscale-works) 已經描述這種集中協調、分散傳送的架構。它使大量資料的轉送工作不必全部集中在登入服務上；2026 年的連線模型則再加入 tailnet 內配置的 Peer Relay。

![身分提供者與協調服務分發身分、公鑰及政策；筆電與主機透過直連或 relay 傳送 WireGuard 密文](/images/networking/2026-10-04/tailscale-control-data.svg)

圖 2：依據 [Tailscale 架構](https://tailscale.com/blog/how-tailscale-works) 與 [Connection types](https://tailscale.com/docs/reference/connection-types) 整理。橘線為控制資訊，藍線為資料；不同資料路徑是選項，圖中未表示它們同時承載同一筆流量。

一台新設備加入的過程，可以理解為以下因果鏈：

1. 設備建立本機金鑰，向協調服務表明設備身分。
2. 人透過 identity provider 完成登入，或由自動化使用適當的註冊憑證。
3. 協調服務把設備、身分與 node 公鑰建立關聯，依政策分發需要的 peer 資訊。
4. 兩端利用 peer 公鑰與路徑資訊，建立安全通訊。

Mesh 描述的是符合政策的設備可以建立彼此的資料路徑。若 n 台設備任意兩台都要互通，潛在 peer 配對有 n(n−1)/2 組；例如 100 台會有 4,950 組。這是假設完全互通的組合算例，實際只需承接政策與 workload 所需的關係。資料分散到端點，仍需要控制系統管理身分、公鑰與可見性。[Tailscale mesh 架構](https://tailscale.com/blog/how-tailscale-works)

這裡有幾種容易混淆的物件：

| 物件 | 主要用途 | 要如何理解 |
| --- | --- | --- |
| Machine key | 設備與協調服務的識別與安全通訊 | 說明哪個 client 安裝實例在聯絡控制系統 |
| Node key | 識別 tailnet 中的 node，參與 WireGuard 通訊 | 私鑰留在產生它的設備，公鑰由控制系統分發 |
| Auth key | 讓設備免互動登入加入網路 | 屬於註冊憑證，應當作 secret 管理 |
| Session key | 具體通訊 session 的對稱加密 | 從協定握手建立，生命週期不同於註冊憑證 |

Machine 與 node 的分工可見 [Tailscale identity](https://tailscale.com/docs/concepts/tailscale-identity) 與 [Node keys](https://tailscale.com/docs/concepts/node-keys)。Auth key 到期或被撤銷，已註冊的設備仍依自己的 node 授權狀態運作；移除已加入的設備要處理設備本身。[Auth keys](https://tailscale.com/docs/features/access-control/auth-keys)

這個差異在自動化尤其重要。把「停止新增設備」與「停止既有設備的存取」當成同一個動作，會留下權限管理缺口。

## 5. 追蹤一次 SSH，先分清內層封包與外層封包

假設兩端完成設定，筆電執行：

`ssh student@100.90.0.20`

在一般 Linux TUN 模式中，應用程式沿用 OS 的 socket 與 TCP/IP stack。系統把目的地屬於 Tailscale 路徑的 IP 封包交給虛擬介面，`tailscaled` 再進行隧道處理。即使 WireGuard 引擎在 userspace 執行，應用程式仍可使用一般 socket；這與後面介紹的無 TUN proxy 模式是兩種不同安排。[Userspace networking 的背景說明](https://tailscale.com/docs/concepts/userspace-networking)

如果容器或 serverless 環境沒有建立 TUN 的權限，Tailscale 還提供 `--tun=userspace-networking` 模式，以 SOCKS5／HTTP proxy 等介面讓應用接入。應用要使用相應代理配置；這種模式下，一般 OS 的 `ping` 與路由觀察方式也會不同。它適合受限環境，代價是應用與網路整合需要配合。[Userspace networking](https://tailscale.com/docs/concepts/userspace-networking)

以下只追蹤**穩態直連**的封包。具體介面名稱與 OS 整合方式會依平台而異。

| 觀察位置 | 可看到什麼 | 哪一層在做決定 |
| --- | --- | --- |
| 筆電的應用與 TUN 介面 | 內層 IP：`100.90.0.10 → 100.90.0.20`，TCP port 22 | OS 路由、應用 TCP |
| 筆電的實體網卡 | 外層 IP/UDP，內容包含 WireGuard 密文 | Tailscale 的 endpoint 選擇 |
| 家用 NAT 的 WAN | 對外位址與 NAT 分配的 UDP port | NAT mapping 與 filtering |
| 主機的 Tailscale 端 | 解密、驗證後的內層 IP 封包 | peer 驗證與 Tailscale 存取規則 |
| 主機的 SSH server | SSH 協定交換 | SSH 使用者登入與權限 |

**內層 TCP 與外層 UDP 可以同時成立。**SSH 的 TCP session 在 overlay 位址之間運作；UDP 負責承載加密後的隧道資料。封裝保留了原本 TCP 的可靠傳輸語意，UDP 外層本身沒有把 SSH 變成不可靠應用。

觀察 `tailscale0` 與實體網卡會看到不同內容。前者可能顯示解封裝後的 IP/TCP；後者主要顯示外層與密文。若 SSH 本身已加密，TUN 上看到的 SSH payload 仍受 SSH 保護；若傳送的是普通 HTTP，TUN 上就可能看到 HTTP 內容。封包擷取必須指定觀察位置，才有辦法解讀「看得到」代表什麼。

最小教學模型是：**應用選 overlay 目的地，隧道選 peer 與 underlay 路徑，接收端再把內層封包交給服務。**依據 [WireGuard 封裝流程](https://www.wireguard.com/#simple-network-interface)。

## 6. NAT 穿透是合作建立可回覆的狀態

要讓兩端直連，第一步是找出候選入口。設備可知道自己的 LAN 位址，也能向外部 STUN server 發出請求，取得對方觀察到的來源位址與 port。

假設 STUN 回覆筆電：

`你從 198.51.100.20:53000 出現。`

這提供一個外部觀察到的 endpoint。STUN 是探測工具，回覆本身沒有保證另一個 peer 的封包也能從這裡進來。[RFC 8489 §3](https://www.rfc-editor.org/rfc/rfc8489#section-3)

接著兩端透過協調與 discovery 通道交換候選入口，互相送出探測封包。在常見、對目的地變化較友善的 NAT 上，往 peer 發出的封包可以建立 mapping，並使回程 filtering 接受該 peer。

![兩個 NAT 後方的設備透過 STUN 發現外部入口，交換入口後互送 UDP 探測，再形成雙向可用路徑](/images/networking/2026-10-04/tailscale-nat-traversal.svg)

圖 3：NAT 穿透的最小教學模型。假設 mapping 可沿用、兩端允許 outbound UDP；先到但未被接收的 probe 可能被丟棄，後續 probe 才成功。依據 [How NAT traversal works](https://tailscale.com/blog/how-nat-traversal-works)；實際實作會探測多個候選 endpoint。

把這個過程分成三步比較清楚：

1. **知道入口**：取得 LAN、外部映射或其他候選 endpoint。
2. **製造可通行狀態**：兩端主動送出封包，讓 NAT 與 stateful firewall 建立相關狀態。
3. **驗證路徑**：收到 peer 的有效回應，再確認雙向通訊可用。

UDP 沒有 TCP 的 SYN 握手，但路由器仍會追蹤 UDP 的暫時狀態。Hole punching 就利用這些狀態；路徑閒置太久、網路切換或 NAT 重啟，都可能要求重新探測。

哪些環境會使事情變難？如果 NAT 對不同目的地產生不同的外部 port，從 STUN 得知的入口可能不適用於 peer。若兩邊都呈現難以預測的映射、封鎖 UDP，或過濾限制很嚴格，直連成功率就會下降。UPnP、NAT-PMP、PCP 在允許的環境能提供額外映射，但雙層 NAT 的最外層未必可被內部設備控制。Tailscale 的工程文章討論了這些組合與路徑探測。[NAT traversal](https://tailscale.com/blog/how-nat-traversal-works)

CGNAT 可以理解成家用 NAT 外面又多一層由電信商管理的轉換。它會增加限制，但是否直連仍須觀察 mapping、filtering、IPv6 與探測結果。相反地，有公開 IPv6 位址的兩端可能免除 IPv4 NAT 轉換，仍要讓防火牆允許必要流量。

本節的小檢查：STUN 有回覆，但 peer 仍然連不上，兩者是否矛盾？沒有矛盾。STUN 證明設備能向某個 server 發出請求並收到回覆；peer 連線測的是另一組來源、目的地與路由器狀態。

## 7. DERP 讓連線先可用，Peer Relay 提供另一條轉送路徑

直連探測需要時間，系統可以先使用已能接觸到的中繼路徑，讓應用開始通訊，再切換到更合適的路徑。

目前官方 [Connection types](https://tailscale.com/docs/reference/connection-types) 描述的順序是：先透過 DERP 建立中繼通訊與 discovery，嘗試升級成 direct；直連失敗時嘗試可用的 Peer Relay，否則維持 DERP，之後持續重新檢查。這要與「穩態偏好 direct、Peer Relay、DERP」分開理解。

| 穩態資料路徑 | 轉送者 | 條件 | 主要成本 |
| --- | --- | --- | --- |
| Direct | 兩個 WireGuard 端點彼此傳送 | 可建立可用 UDP 路徑 | 兩端 CPU、網路容量與封裝 |
| Peer Relay | 明確配置的 tailnet 內設備 | 兩端可達 relay，並具備相應授權 | relay 的位置、CPU、NIC 與轉送容量 |
| DERP | Tailscale 提供或配置的 DERP 服務 | 可建立 DERP 連線 | 繞路、共享容量與傳輸等待 |

DERP 是 **Designated Encrypted Relay for Packets**。它轉送已加密的 WireGuard 資料，沒有兩端的私鑰；所以 relay 的工作是搬運密文。它仍可觀察自己連線上的 endpoint、時序、資料量等中繼所需資訊。[DERP servers](https://tailscale.com/docs/reference/derp-servers)

DERP 常透過 TCP 443 上的 TLS 連線運作，這讓許多允許 HTTPS、限制 UDP 的環境仍有替代路徑。過濾、代理伺服器或其他網路限制也可能阻擋它。[Firewall ports](https://tailscale.com/docs/reference/faq/firewall-ports)

Peer Relay 由管理員明確配置，使用可到達的 UDP relay port 與應用 capability 授權；官方文件要求使用端 client 支援相關版本，並指出 1.86 起的支援。它可以讓轉送位置更接近 workload，但需要自行提供容量與維運。[Peer Relays](https://tailscale.com/docs/features/peer-relay)

這裡最容易混淆的是 relay 與 gateway。Relay 搬運兩端之間的密文；下一節的 subnet router 與 exit node 則會成為 WireGuard 隧道的端點，解開內層封包後再路由。兩者的信任與資料可見性不同。

## 8. 授權回答能不能連，路由回答往哪裡送

一條連線至少需要三個條件同時成立：

`可用路徑 ∧ 政策允許 ∧ 服務可接收`

找到直連路徑，只解決了第一項。服務成功登入，還需要應用本身的認證與權限。

Tailscale 目前建議新設定使用 **grants**；既有 ACL 語法仍受到支援。Grants 用來源、目的地與允許的網路／應用能力描述權限。[ACLs 與 grants 的關係](https://tailscale.com/docs/features/access-control/acls)

以下是隔離教學 tailnet 的完整政策範例。Alice、Bob 都是假設已加入的帳號；`group:lab` 中只有 Alice，Linux 主機由管理員指派 `tag:lab-server`，並在該主機上維持一般 OpenSSH 與示範 HTTP server。

```json
{
  "groups": {
    "group:lab": ["alice@example.com"]
  },
  "tagOwners": {
    "tag:lab-server": ["alice@example.com"]
  },
  "acls": [],
  "grants": [
    {
      "src": ["group:lab"],
      "dst": ["tag:lab-server"],
      "ip": ["tcp:22", "tcp:8000"]
    }
  ],
  "tests": [
    {
      "src": "alice@example.com",
      "proto": "tcp",
      "accept": ["tag:lab-server:22", "tag:lab-server:8000"],
      "deny": ["tag:lab-server:5432"]
    },
    {
      "src": "bob@example.com",
      "proto": "tcp",
      "deny": ["tag:lab-server:22", "tag:lab-server:8000"]
    }
  ]
}
```

`tagOwners` 控制誰能指派 tag；`grants` 控制誰能連入被標記的設備。這兩個權限分工要各自設計。伺服器使用 tag 身分，也有助於讓服務角色的管理跟人的筆電權限分開。[Tags](https://tailscale.com/docs/features/tags)

Grants 的允許集合會相加。若保留一條 `src: ["*"], dst: ["*"], ip: ["*"]` 的廣泛規則，再加一條只允許 22 的規則，原本的廣泛存取仍然存在。要縮小權限，要縮小或移除廣泛允許。[Grants syntax](https://tailscale.com/docs/reference/syntax/grants)

此外，**deny-by-default 的規則模型，與初建 tailnet 的預設政策是不同概念**。初建政策通常方便設備彼此通訊；教學範例用 `"acls": []` 明確移除舊式 ACL 的預設廣泛允許，只保留列出的 grants。實際使用前要讀取既有完整政策，避免在共用網路整份覆蓋其他人的規則。[ACL 預設行為](https://tailscale.com/docs/features/access-control/acls)

Policy tests 檢查預期的允許與拒絕關係（[官方測試範例](https://tailscale.com/docs/features/multiple-tailnets)），仍須在設備上測 TCP 連線，確認路徑與服務。允許 Alice 發起連線，正常回覆也能回來；讓主機主動發起新的反向連線，則是另一條授權關係。這與 stateful firewall 的連線方向概念相似。

## 9. NAS 沒裝 Tailscale，就讓一台設備替子網路路由

原本案例的 Linux 主機可以裝 client。現在加入一台 `192.168.50.30` 的 NAS，假設 NAS 沒有安裝 Tailscale。要讓外面的筆電存取它，可以把家中的 Linux 設備設為 **subnet router**。

這個 router 同時位於 tailnet 與家中 LAN，宣告自己可以轉送到某個 prefix，例如 `192.168.50.0/24`。管理端核准路由、client 接受需要的路由，政策允許目的位址與服務後，封包便能經由它抵達 NAS。

![三種資料路徑的加密終點比較；直接連節點在目標主機解密，subnet router 與 exit node 則在路由器結束 WireGuard 隧道](/images/networking/2026-10-04/tailscale-routing-termination.svg)

圖 4：依據 [Subnet routers](https://tailscale.com/docs/features/subnet-routers) 與 [Exit nodes](https://tailscale.com/docs/features/exit-nodes) 整理。藍線為 WireGuard；後段是否另有加密，由 HTTPS、SSH 等應用協定決定。圖示為邏輯路徑，省略中間 NAT 與 relay。

以下以獨立 Linux router 為示意，使用前先依發行版完成持久的 IP forwarding 與防火牆設定。IP forwarding 讓核心能轉送封包；路由宣告則告訴 tailnet 它願意承接哪個 prefix。

```bash
# 示範即時啟用 IPv4 forwarding；重開機後需持久設定。
sudo sysctl -w net.ipv4.ip_forward=1

# 宣告家中 LAN；此步之後還需要管理端核准。
sudo tailscale set --advertise-routes=192.168.50.0/24

# 在需要接受此路由的 Linux client 上操作。
sudo tailscale set --accept-routes=true
```

**宣告、核准、授權、client 使用路由，各自回答不同問題。**宣告表示 router 的意願；核准決定是否接受它的宣告；存取規則決定誰能去 NAS 的哪個 port；client 的路由設定決定實際封包送法。[Subnet router 設定流程](https://tailscale.com/docs/features/subnet-routers#set-up-a-subnet-router)

若只需要教學群組讀取 NAS 的 HTTPS，可在既有 `grants` 陣列加入以下物件。目的地指向 NAS 的實際 IP，而不是 router 的 Tailscale IP：

```json
{
  "src": ["group:lab"],
  "dst": ["192.168.50.30"],
  "ip": ["tcp:443"]
}
```

### 回程問題可以用來源位址推導

預設 subnet router 會對這類轉送進行 SNAT。假設 router 的 LAN 位址是 `192.168.50.2`，NAS 看到的來源就可能是 router，而不是筆電的 `100.90.0.10`。NAS 能直接回覆同 LAN 的 router，router 再依轉換狀態把回覆送回筆電。

若關閉 SNAT，NAS 可以看見原始來源，但它的路由表必須知道如何把這個來源範圍送回 subnet router。若 NAS 把回覆丟給不知道 tailnet 路由的預設 gateway，請求到得了、回覆卻回不去。SNAT 的便利性，換來後端對原始來源 IP 的可見性下降。[Disable SNAT 與 return route](https://tailscale.com/docs/features/subnet-routers#disable-snat)

教學中有四項值得逐一驗證：

- Linux router 本身能先連到 NAS，排除 LAN 路徑問題。
- 筆電確實把 NAS 的 IP 送往已核准的 subnet route。
- 存取規則允許的是 NAS 的目的 IP 與 port，授權 router 自己的 22 並不涵蓋 NAS。
- NAS 的回覆有一條回到筆電的路徑。

NAS 沒有成為 WireGuard 端點。因此，Tailscale 的加密到 subnet router 結束；router 到 NAS 這段，使用 HTTPS 或 SSH 才能由應用協定繼續保護內容。若後段是普通 HTTP，router 與 LAN 上相應的觀察點就可能接觸明文。

還有位址重疊問題：旅館 LAN 與家中都用 `192.168.50.0/24` 時，client 需要在相同目的範圍中選路。一般的 longest-prefix、policy routing 與 OS 整合方式會影響結果；長期可以重新規劃互不重疊的 prefix，或採專門的重疊網段方案，避免只靠猜測路由優先順序。

## 10. Exit node 改變上網出口，MagicDNS 改善名字解析

Subnet router 主要承接指定內部 prefix。**Exit node** 則讓 client 選擇把一般對外流量經某個 tailnet 設備送出，邏輯上涵蓋預設路由 `0.0.0.0/0` 與 `::/0`。平常僅安裝 Tailscale，公共網站的流量仍走原本的上網出口；要使用 exit node，需要宣告、管理端允許與 client 選用。[Exit nodes](https://tailscale.com/docs/features/exit-nodes)

若筆電選家中的 exit node，路徑就變成：

`筆電 → WireGuard → 家中 exit node → 公共網站`

網站通常看到家中對外出口位址。隧道在 exit node 結束，網站內容若使用 HTTPS，HTTPS 再保護 exit node 到網站的應用通訊。出口管理者仍可能觀察目的連線與流量特徵；出口選擇也會改變延遲、家中頻寬負擔與可用性。

**MagicDNS** 處理另一個問題：把 `home-linux` 或它的完整 tailnet 名稱解析成 Tailscale IP，減少記住數字位址的工作。每台設備上的本機 DNS 功能可以處理 tailnet 名稱；Quad100 `100.100.100.100` 是供本機使用的特殊服務位址。[MagicDNS](https://tailscale.com/docs/features/magicdns)、[Quad100](https://tailscale.com/docs/reference/reserved-ip-addresses)

這裡要把三個動作串起來：

`名字解析 → 選擇路由 → 建立與授權連線`

DNS 解析成功，提供了目的 IP；後續路由、政策與服務仍各自運作。相反地，用 IP 能連、用名稱失敗，優先檢查 DNS 與 search domain。Tailscale 的本機 DNS 設計可見 [MagicDNS 原理](https://tailscale.com/blog/magicdns-why-name)。

若需求是依網域名稱選擇 SaaS 或其他應用出口，還有 app connector：它利用指定網域的 DNS 資訊安排路由。這是將域名與轉送結合的功能，適合另行研究；理解前面的 subnet 與 exit 模型，才容易看懂它的差異。[App connector](https://tailscale.com/docs/features/app-connectors/how-to/setup)

## 11. SSH、Serve 與 Funnel 決定服務要怎麼被使用

現在回到開頭的 SSH。一般 **SSH over Tailscale** 是先透過 tailnet 抵達 OpenSSH，登入仍由 OpenSSH 的 key、帳號與設定處理。只要 TCP 22 被允許、sshd 有接收連線，就能使用原本的 SSH 流程。[Protect your SSH servers](https://tailscale.com/docs/reference/ssh-over-tailscale)

**Tailscale SSH** 則由 Tailscale 接管進入該設備 Tailscale IP 的 port 22，另用 tailnet 身分與 `ssh` 政策決定可登入哪些本機帳號。它需要啟用支援的 server，而且同時符合網路層授權與 SSH 授權。開放 TCP 22 的 grant，只完成其中一層。[Tailscale SSH](https://tailscale.com/docs/features/tailscale-ssh)

例如，只讓教學群組登入既有的 `student` 帳號，可以在前面的網路 grant 之外加入：

```json
"ssh": [
  {
    "action": "check",
    "src": ["group:lab"],
    "dst": ["tag:lab-server"],
    "users": ["student"],
    "checkPeriod": "1h"
  }
]
```

這是要加入既有 JSON 物件的欄位片段。`student` 必須已在 Linux 主機存在；`check` 讓連線需要依指定時間重新驗證身分。若只打算使用普通 OpenSSH，保留原有模式即可。

Web 服務又有兩個容易混淆的名字：

| 功能 | 誰能接觸服務入口 | 常見情境 |
| --- | --- | --- |
| Serve | 符合政策的 tailnet 設備 | 團隊的內部 dashboard、開發服務 |
| Funnel | 公共網際網路訪客 | 公開展示、外部 webhook |

Serve 可把本機服務以 tailnet 入口分享，並套用存取規則。[Serve](https://tailscale.com/docs/features/tailscale-serve)；Funnel 則提供公開入口，訪客無須先加入 tailnet，應用本身要處理需要的登入與存取限制。[Funnel](https://tailscale.com/docs/features/tailscale-funnel)

有一個直接的檢查方式：把服務交給「只拿到 URL、沒有 Tailscale 身分」的人測試。如果它應該是私有服務，該訪客就不應能透過公開網際網路直接打開。入口的設計，決定了後續授權需求。

## 12. 安全要沿著誰能解密、誰能授權來檢查

只問「有沒有加密」會漏掉系統的其他信任關係。把角色列出來，問題就清楚了。

| 角色 | 掌握或可能觀察的資訊 | 要管理的風險 |
| --- | --- | --- |
| Identity provider | 人的登入身分、驗證流程 | 帳號接管、停權與 MFA |
| Coordination server | 設備、公鑰、政策及協調所需 metadata | 加入授權、公鑰分發與政策正確性 |
| Relay | 它承接的密文、連線與流量特徵 | 可用性、容量與 metadata |
| WireGuard 端點 | 私鑰與解封裝後的 IP 封包 | 端點入侵、本機權限與服務暴露 |
| Subnet router／exit node | 解開的內層封包與後段轉送 | 路由器可信度與後段協定 |

Tailscale 私鑰留在節點，relay 無法直接解開既有兩端的 WireGuard 密文。然而，管理系統負責判斷哪些公鑰屬於被允許的設備，這仍然是一種信任。[Tailscale security](https://tailscale.com/security)

**Tailnet Lock** 加入由已信任節點簽署 node 公鑰的機制：peer 在接受新 node key 前驗證簽章，使控制服務單方面加入未簽署節點的能力受到限制。它採初始信任建立與後續簽署管理，管理員需要保管 signing nodes 與停用所需的 secrets。[Tailnet Lock](https://tailscale.com/docs/features/tailnet-lock)

這個機制改善的是節點金鑰接納的信任關係。它沒有接手端點修補、應用登入、所有政策正確性或網路可用性。被信任的設備遭入侵，攻擊者仍可能使用它已有的權限；把資料庫只開給需要的角色、限制服務 port，仍有實質作用。

Tailscale 政策由設備本機執行，可以使規則不必逐包去中心服務問答；走原本 LAN 或其他公開介面的流量，也要由相應主機防火牆與應用限制處理。[Local enforcement](https://tailscale.com/docs/features/access-control/acls)

因此，Zero Trust 在這個系統中的具體實踐，是用設備與身分描述存取、縮小允許範圍、維護設備狀態並控制加入資格。採用之後仍要選定政策與服務配置，才會形成你要的隔離。

## 13. 吞吐量先看路徑，再看最慢的那一段

「WireGuard 很快」不足以推算某次檔案傳輸的速度。完整路徑可能包含手機訊號、家中上傳、relay、端點 CPU 與 NAS 磁碟。每個元件都有容量上限。

用簡化模型描述長時間、大量傳輸：

`有效吞吐量 ≤ min(來源可用上傳、目的可用下載、各段路徑容量、端點處理能力)`

若走 relay，還要加入 relay 的可用轉送容量。若讀磁碟或寫 NAS，儲存與應用也會加入最低值。這是串聯系統的容量上限推導，實際值還會因封裝、競爭、丟包與 TCP 行為下降。

假設家中上傳 100 Mbit/s、外面下載 300 Mbit/s，忽略其他成本，家中送出的上限仍是 100 Mbit/s，也就是十進位約 12.5 MB/s。傳送十進位 10 GB 的資料至少需要：

`10 × 10⁹ bytes × 8 / (100 × 10⁶ bit/s) = 800 秒`

即 13 分 20 秒。這是假設算例，沒有包含實際加密、重傳、磁碟與協定成本；換更快的筆電也無法突破家中這個上傳上限。

延遲會透過 TCP 的在途資料影響吞吐量。假設 bottleneck 是 100 Mbit/s、RTT 80 ms，要填滿路徑需要約：

`BDP = 100 × 10⁶ × 0.08 = 8 × 10⁶ bit = 1 MB`

若可用的發送視窗只有 256 KB，暫忽略 loss 與其他限制，`window / RTT` 對應約 25.6 Mbit/s。這說明 relay 繞路增加 RTT，有時會降低傳輸速度，即使每段鏈路的名目頻寬沒有改變。[TCP window scaling 與高 BDP 路徑](https://www.rfc-editor.org/rfc/rfc7323)

DERP 的 TCP 傳輸還可能在丟包時等待補齊同一條外層 stream 的缺口，使後面的隧道資料等待；這是特定外層連線內的 head-of-line 行為。Peer Relay 與直連的 UDP 路徑避免了這一種外層 TCP 等待，內層應用自己的 TCP 順序限制仍存在。[DERP 傳輸背景](https://tailscale.com/blog/nat-traversal-improvements-pt3-looking-ahead)

小封包能過、大型傳輸停住，則值得檢查 MTU 與 PMTU。封裝要增加 header，外層還可能經過其他 tunnel。官方 TCP 排錯文件列出 Tailscale MTU 1280 的模型，並說明封包大小與 MSS 調整；實際仍應查看平台介面、路由與封包擷取結果。[TCP connection troubleshooting](https://tailscale.com/docs/reference/troubleshooting/network-configuration/tcp-connection-two-devices)

如果想繼續研究「同樣頻寬，為何不同順序與等待會影響完成時間」，可接著讀本站 [STORM 的 RNIC 排程]({% post_url 2026-09-27-storm-rdma-nic-scheduling %})。它處理資料中心的另一種場景，但同樣要求把路徑容量與排隊等待分開。

## 14. 五個實驗讓網路模型變得可觀察

以下實驗只在自己的兩台設備與獨立教學 tailnet 上進行。名稱 `home-linux`、帳號與位址都是示例；先依 [官方安裝指南](https://tailscale.com/docs/how-to/quickstart) 安裝 client，兩端完成登入。這些是可重現的操作設計，結果要由實際環境量測。

### 實驗 A — 用 IP 連，再用名字連

先套用第 8 節的最小政策，把 Alice 的筆電保留為個人身分、Linux 主機標為 `tag:lab-server`。兩端先查看：

```bash
tailscale version
tailscale ip -4
tailscale status
tailscale netcheck
```

在 Linux 主機準備只有示範文字的資料夾：

```bash
mkdir -p ~/tailscale-lab-public
printf 'tailscale lab\n' > ~/tailscale-lab-public/index.html
LAB_TS_IP=$(tailscale ip -4)
python3 -m http.server 8000 --bind "$LAB_TS_IP" --directory ~/tailscale-lab-public
```

這個服務只綁定該 Tailscale IP。在筆電開另一個 terminal，先連主機的實際 Tailscale IP，再用 MagicDNS 名稱：

```bash
curl --max-time 5 http://100.90.0.20:8000/
curl --max-time 5 http://home-linux:8000/
```

兩者都收到 `tailscale lab`，表示名稱與 TCP 服務這條路徑均成立。IP 成功、名稱失敗，優先查 DNS；兩者都失敗，再分查政策、路徑、binding 與防火牆。看到其他 HTTP 頁面，則要確認是否連到正確服務。

### 實驗 B — 同一個目的 IP，觀察不同實體路徑

讓筆電先用家中 Wi-Fi，再切到手機 hotspot，每次執行：

```bash
tailscale ping --c=10 home-linux
tailscale status
tailscale netcheck
```

記錄 Tailscale IP、連線型態、underlay endpoint 與 RTT。可能先出現 DERP，再升級 direct；已經有可用路徑時，未必每次都能看到初始化階段。

`netcheck` 的 UDP、映射與 relay latency 反映**該設備的網路探測**。它沒有測過每一組 peer，也沒有量測一條應用傳輸的 throughput。兩端同時保留結果，才能判斷是哪邊的環境變難。[Device connectivity](https://tailscale.com/docs/reference/device-connectivity)

### 實驗 C — 用不同層次的探測定位故障

```bash
tailscale ping home-linux
tailscale ping --tsmp home-linux
ping -c 3 100.90.0.20
curl --max-time 5 http://100.90.0.20:8000/
```

第一個測 Tailscale client 之間與傳輸路徑；TSMP 更深入到 WireGuard 層，但不經一般 host IP stack；普通 ping 測 OS 的 ICMP 路徑；curl 才實際測指定 TCP/HTTP 服務。不同工具涵蓋的層次，可對照 [官方 TCP 排錯說明](https://tailscale.com/docs/reference/troubleshooting/network-configuration/tcp-connection-two-devices)。

第 8 節的範例只允許指定 TCP ports，因此普通 ICMP ping 的結果也可能受到政策影響。不要為了「所有 ping 都綠燈」就擴大服務權限；應以預期的 TCP 服務成功為判定，再用各層探測縮小問題範圍。

在 Linux 主機再查：

```bash
ss -ltnp
ip address show tailscale0
```

如果程式只聽 `127.0.0.1:8000`，它在 loopback 接收連線。改成 Tailscale IP binding，或使用適當的 Serve 代理，才能讓這個路徑接到服務；「Tailscale 顯示 online」沒有啟動任何應用程式。

### 實驗 D — 用兩個身分驗證最小權限

Alice 的筆電連 TCP 8000 應成功；Bob 的獨立設備使用同一個目的位址測試，應無法取得頁面。Alice 測沒有允許的 TCP 5432，也應被拒絕。前面的 policy tests 先驗證授權預期，設備測試再驗證實際行為。

把這個結果與「同一台筆電切換身分」區分開來。設備登入身分、tag 與 policy selector 的變化，都可能改變它被套用的規則；實驗記錄要寫出是哪個 node、哪個身分、哪個目的 port。

### 實驗 E — 測網路吞吐量，再測檔案傳輸

如果兩端已安裝 iperf3，先在教學政策中暫時加入 `tcp:5201` 與 `udp:5201`，讓 iperf3 的控制與可能的測量通道有適當授權。在主機啟動：

```bash
iperf3 -s -B 100.90.0.20
```

筆電測試 TCP 正向與反向：

```bash
iperf3 -c 100.90.0.20 -t 20
iperf3 -c 100.90.0.20 -t 20 -R
```

記錄當時是 direct、peer relay 還是 DERP、兩端 CPU 使用率、Wi-Fi／有線環境、方向與 RTT。正向預設由筆電送，`-R` 則由主機送；下載 NAS 的情境通常更接近後者。接著再測檔案讀寫，才能看出儲存與應用加入的成本。[iperf3 官方操作文件](https://software.es.net/iperf/invoking.html)

完成後停止 HTTP 與 iperf3 的示範服務，移除暫加的測量 port 授權。測試資料與服務可被獨立清除，不需要改動正式應用。

### 把觀察整理成一張表

| 時間與網路 | 來源 node／身分 | 目的與服務 | 路徑型態 | RTT | 正向／反向 throughput | 結果與待查項 |
| --- | --- | --- | --- | --- | --- | --- |
| 家中 Wi-Fi | 實際填寫 | HTTP 8000 | 實際填寫 | ms | Mbit/s | DNS、binding、政策 |
| 手機 hotspot | 實際填寫 | iperf3 5201 | 實際填寫 | ms | Mbit/s | NAT、上傳、CPU |

這張表的用途，是把「有時候很慢」變成可比較的條件。每次改一個主要變因，才能把結果與機制連起來。

## 15. 壞掉的位置不同，處理方式也不同

排錯先分層，會比全部重裝更有效。

| 症狀 | 優先檢查 | 對應處理 |
| --- | --- | --- |
| 設備不在預期網路、登入失敗 | identity、tailnet、註冊與核准狀態 | 確認登入與設備授權 |
| IP 可連，名字失敗 | DNS、search domain、OS resolver | 核對 MagicDNS 與 client DNS 接受設定 |
| client 探測成功，HTTP 失敗 | grant、主機防火牆、binding、服務 | 測指定 port，確認 listen 位址 |
| 可用但長期 DERP，速度偏低 | UDP、兩端 NAT、relay 距離 | 查兩端 netcheck，再評估有線／IPv6／Peer Relay |
| NAS 收到請求但沒有回覆 | SNAT、return route、NAS gateway | 核對來源位址與回程 |
| 小請求成功，大傳輸卡住 | MTU、PMTU、loss、外層 tunnel | 分介面擷取，檢查 MSS 與丟包 |
| router 宣告還在但連不上 | router 狀態、node key、路由健康 | 處理到期與可用 router |

協調服務暫時故障時，設備上已保存的金鑰與規則，能讓許多既有通訊繼續運作；新增設備、政策更新、撤銷與金鑰更新會受影響，既有金鑰也可能逐漸到期。[Coordination server down](https://tailscale.com/docs/reference/coordination-server-down)

這可以推導出一個重要差異：控制服務停機，與 relay 或 subnet router 停機，影響的連線集合不同。Direct 通訊沒有經過 relay；經特定 subnet router 抵達 NAS 的流量，則直接依賴那台 router。系統可用性需要依實際資料路徑檢查。

路由節點的 key 到期時，Tailscale 可以保留路由設定卻使它不可達，以避免把原本應進入受管網路的流量導向其他網路。對長期運作的 connector，要安排金鑰生命週期與高可用性。[Expired connector keys](https://tailscale.com/docs/features/subnet-routers#expired-device-keys)

手機或筆電切換網路，Tailscale 會探索新的底層路徑。IP 身分的穩定可以減少上層重新配置，但切換仍可能有丟包或等待；TCP 是否維持、應用是否 timeout，需要由切換時間與應用容忍度一起決定。

## 16. 選 Tailscale、手動 WireGuard，或自管控制服務

用三個需求檢查選型：設備與身分改變多不多、網路入口可控程度、誰願意承擔維運。

| 方案 | 適合的條件 | 必須承擔的工作 |
| --- | --- | --- |
| 手動 WireGuard | 少量、固定 peer，有清楚路由與可達入口 | 自行管理公鑰、endpoint、路由、撤銷與穿透 |
| 集中式 VPN gateway | 資料需經集中檢查或既有 gateway 體系 | gateway 容量、HA、繞路與 client 維運 |
| Tailscale 託管協調 | 多人多機、行動設備、希望自動尋路 | identity、政策、設備與 connector 生命週期 |
| Headscale 自管控制服務 | 願意自行維運，希望掌握控制服務 | 服務、資料、升級、備份與相容性驗證 |

Headscale 是 Tailscale control server 的開源自管實作；專案定位與支援功能需依所使用版本確認。[Headscale FAQ](https://headscale.net/stable/about/faq/)；它接手控制服務，不會自動替你處理所有 NAT、relay 容量或應用權限。採用前應依 [功能清單](https://headscale.net/stable/about/features/) 檢查 client、policy 與所需功能的相容性。

對兩台可控的固定機器，手動 WireGuard 的少量設定可能已足夠。多人跨網路的維運則容易受益於 Tailscale 的集中協調；需要強制集中流量檢查的環境，仍要明確安排 gateway 與路由，不能只期待 mesh 自動滿足需求。

成本也要沿實際路徑計算。Direct 把加密與傳送負擔分散到端點；relay 增加中繼容量，subnet router 集中該 prefix 的轉送工作。採用者還會依賴 identity 與控制 API，政策遷移、裝置註冊與功能相容性就成為長期成本。方案、功能與價格可能變動，選型應以當時需求與 [官方方案](https://tailscale.com/pricing)核對，教學不以單一免費額度作結論。

推論：未來 12 個月，在持續加入人員、CI 工作與遠端設備的小型團隊中，以身分與 tag 維護存取，將比逐台維護 endpoint 更能壓低變更成本。這個推論可以驗證：記錄加入／移除設備所需時間、政策錯誤、relay 流量比例與 connector 故障。若設備幾乎不變、既有 VPN 已自動化，或大流量長期需要中繼，Tailscale 的管理收益可能不足以支付新增依賴與容量成本。

## 17. 回到起點，現在可以重建整條連線

外面的筆電要連家中主機，需要的承諾已經可以逐層描述：

1. 登入與設備註冊，建立 node 與 tailnet 的身分關係。
2. 公鑰、政策與可用 endpoint 分發，讓 peer 能辨識彼此。
3. NAT 探測或 relay，提供可實際傳送的底層路徑。
4. WireGuard，保護隧道兩端之間的內層 IP 封包。
5. 路由、grants、主機防火牆與應用，將資料交給被允許的服務。

對安裝 client 的兩台設備，加密終點在兩台設備。對 NAS 或公共網站，加密終點可能在 subnet router 或 exit node，之後由應用協定接續。對速度，先確認 direct 或 relay，再檢查每段頻寬、RTT、端點與儲存。

Tailscale 讓應用使用穩定位址與名稱，底下再協調身分、尋找路徑並套用授權。接下來最值得量測的問題很具體：**你的兩台設備，在常用的 Wi-Fi、行動網路與遠端環境中，各有多少時間直連，多少流量依賴中繼？**這個答案會同時影響效能、可用性與部署選擇。

### 理解檢查與解答

| 問題 | 解答 |
| --- | --- |
| 兩台都有 Tailscale IP，為何 HTTP 還可能失敗？ | IP 只提供 overlay 目的地；還要有路徑、授權、主機允許與服務 listen。 |
| TCP 應用能走 UDP 隧道嗎？ | 可以；TCP 在內層，UDP 承載 WireGuard 密文。 |
| STUN 回覆入口，為何 peer 還可能進不來？ | NAT 對 peer 的 mapping／filtering 可能不同，需實際雙向探測。 |
| DERP 能閱讀 SSH 或 HTTP 內容嗎？ | 正常節點間 WireGuard 密文由兩端解密；relay 仍能觀察中繼 metadata。 |
| 用 subnet router 連 HTTP NAS，後段受誰保護？ | WireGuard 到 router 結束；普通 HTTP 後段沒有應用加密，可改用 NAS HTTPS。 |
| 允許 TCP 22，會自動允許 Tailscale SSH 登入嗎？ | 還需啟用 server、SSH policy 與對應既有本機帳號；一般 OpenSSH 則用其原有認證。 |
| 刪除 auth key，就能移除已加入的設備嗎？ | 要處理設備與 node 的授權；auth key 主要處理加入資格。 |
| 新增一條更窄的 grant，會覆蓋原本廣泛 grant 嗎？ | Grants 的允許會聯集；縮小權限要修改廣泛規則。 |

### 常用名詞對照

| 名詞 | 在本教學中代表什麼 |
| --- | --- |
| Tailnet | 管理設備、身分與存取政策的網路脈絡 |
| Overlay | 應用使用的虛擬 IP 網路 |
| Underlay | 真正搬運密文的實體 IP 路徑 |
| Endpoint | 當下可接觸到 peer 的底層 IP 與 port |
| Coordination server | 分發設備、公鑰、路徑資訊與政策的控制服務 |
| NAT traversal | 探索映射、建立狀態與測試可互達路徑 |
| DERP | 轉送 WireGuard 密文的中繼服務 |
| Peer Relay | 明確配置在 tailnet 內的中繼設備 |
| Subnet router | 承接特定 prefix，轉送到沒有 client 的設備 |
| Exit node | 承接一般對外流量的出口設備 |
| Grant | 指定來源能使用目的地哪些網路或應用能力 |

## 證據範圍

技術行為依官方文件、WireGuard 協定與 IETF RFC 整理，版本可見範圍以 2026 年 10 月 4 日為準。早期 Tailscale 工程文章用來建立設計背景；2026 年的 connection types 與 Peer Relay 文件用來補齊目前路徑模型。文件標示的 Last validated 是文件驗證日期，不一律視為功能發布日期。

四張圖為教學示意，省略部分探測、金鑰交換與 OS 細節；公網位址使用文件保留範圍，overlay 位址為假設值。頻寬、BDP、視窗與傳輸時間全為假設算例，沒有宣稱是任何人的實測效能。實驗與 policy 範例已做文章靜態檢查，沒有在讀者的 tailnet、NAS 或電信網路實際執行，也沒有完成一套端到端 Tailscale 測試環境。

本篇不涵蓋完整 WireGuard 安全證明、所有 OS 的 policy routing、site-to-site 進階配置、重疊網段專門方案、全部企業產品與方案額度。Tailscale 不等同 Layer 2 bridge，不自動保證匿名上網，也不取代應用登入與主機安全。重疊網段、其他 VPN 共用、IPv6、OS DNS 行為與不同 client 版本，均可能改變具體配置與測試結果。

## 參考資料

### 網路與安全基礎

- [RFC 1918 — Address Allocation for Private Internets](https://www.rfc-editor.org/rfc/rfc1918)
- [RFC 4787 — NAT Behavioral Requirements for Unicast UDP，2007](https://www.rfc-editor.org/rfc/rfc4787)
- [RFC 8489 — Session Traversal Utilities for NAT，2018](https://www.rfc-editor.org/rfc/rfc8489)
- [RFC 7323 — TCP Extensions for High Performance，2014](https://www.rfc-editor.org/rfc/rfc7323)
- [WireGuard 技術概覽與 Cryptokey Routing](https://www.wireguard.com/)
- [WireGuard Protocol & Cryptography](https://www.wireguard.com/protocol/)

### 架構、路徑與身分

- [How Tailscale works，2020-03-20](https://tailscale.com/blog/how-tailscale-works)
- [How NAT traversal works](https://tailscale.com/blog/how-nat-traversal-works)
- [Connection types](https://tailscale.com/docs/reference/connection-types)
- [DERP servers](https://tailscale.com/docs/reference/derp-servers)
- [Tailscale Peer Relays](https://tailscale.com/docs/features/peer-relay)
- [Firewall ports](https://tailscale.com/docs/reference/faq/firewall-ports)
- [Device connectivity](https://tailscale.com/docs/reference/device-connectivity)
- [Tailscale identity](https://tailscale.com/docs/concepts/tailscale-identity)
- [Node keys](https://tailscale.com/docs/concepts/node-keys)
- [Auth keys](https://tailscale.com/docs/features/access-control/auth-keys)
- [Reserved IP addresses／Quad100](https://tailscale.com/docs/reference/reserved-ip-addresses)
- [Wake-on-LAN 與 Layer 2／3](https://tailscale.com/blog/wake-on-lan-tailscale-upsnap)

### 路由、存取與應用

- [Manage permissions using ACLs](https://tailscale.com/docs/features/access-control/acls)
- [Grants syntax](https://tailscale.com/docs/reference/syntax/grants)
- [Group devices with tags](https://tailscale.com/docs/features/tags)
- [Subnet routers](https://tailscale.com/docs/features/subnet-routers)
- [Exit nodes](https://tailscale.com/docs/features/exit-nodes)
- [MagicDNS](https://tailscale.com/docs/features/magicdns)
- [MagicDNS 原理](https://tailscale.com/blog/magicdns-why-name)
- [App connector 設定](https://tailscale.com/docs/features/app-connectors/how-to/setup)
- [SSH over Tailscale](https://tailscale.com/docs/reference/ssh-over-tailscale)
- [Tailscale SSH](https://tailscale.com/docs/features/tailscale-ssh)
- [Tailscale Serve](https://tailscale.com/docs/features/tailscale-serve)
- [Tailscale Funnel](https://tailscale.com/docs/features/tailscale-funnel)

### 運作與實驗

- [Userspace networking mode](https://tailscale.com/docs/concepts/userspace-networking)
- [Quickstart](https://tailscale.com/docs/how-to/quickstart)
- [Tailscale CLI](https://tailscale.com/docs/reference/tailscale-cli)
- [TCP connection troubleshooting](https://tailscale.com/docs/reference/troubleshooting/network-configuration/tcp-connection-two-devices)
- [Improving NAT traversal, part 3](https://tailscale.com/blog/nat-traversal-improvements-pt3-looking-ahead)
- [Coordination server down](https://tailscale.com/docs/reference/coordination-server-down)
- [Tailscale security](https://tailscale.com/security)
- [Tailnet Lock](https://tailscale.com/docs/features/tailnet-lock)
- [Headscale FAQ](https://headscale.net/stable/about/faq/)
- [Headscale features](https://headscale.net/stable/about/features/)
- [iperf3 官方操作文件](https://software.es.net/iperf/invoking.html)
- [Tailscale plans](https://tailscale.com/pricing)
- [Policy tests 範例](https://tailscale.com/docs/features/multiple-tailnets)

