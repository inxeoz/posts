# Running Split VPNs on Linux

## Routing Specific Traffic via MotionPro (ArrayVPN) While Keeping Cloudflare WARP Enabled

Modern Linux systems often need to run **multiple VPNs at the same time**.

A very common real-world setup looks like this:

* 🌍 **Cloudflare WARP** for secure internet access
* 🏢 **Enterprise VPN (Array Networks / Ivanti MotionPro)** for internal company servers
* 🎯 Only **specific internal IPs** should go through the enterprise VPN
* ❌ WARP must remain enabled
* ❌ No full-tunnel conflicts

This article explains **exactly how to do that**, step by step, using **Linux routing and policy rules**.

---

## 🧠 What We’re Solving

We want:

| Traffic                          | Route           |
| -------------------------------- | --------------- |
| Internet                         | Cloudflare WARP |
| Internal server (`172.16.50.10`) | MotionPro VPN   |
| Everything else                  | Unchanged       |

---

## 🧩 Environment Overview

### VPNs

* **Enterprise VPN**: Array Networks / Ivanti MotionPro

  * CLI: `vpn_cmdline`
  * Tunnel interface: `tun0`
* **External VPN**: Cloudflare WARP

  * Interface: `CloudflareWARP`
  * Uses **policy routing**

### Target

* Internal SSH server:

  ```
  172.16.50.10
  ```

---

# Part 1: Connecting to ArrayVPN / MotionPro on Linux

## 🔌 Connecting to MotionPro Using `vpn_cmdline`

Many enterprise VPNs branded as **MotionPro**, **ArrayVPN**, or **Ivanti Secure Access** are powered by Array Networks.

On Linux, these are typically accessed using the `vpn_cmdline` client.

---

## 📦 Installation (Arch Linux example)

```bash
yay -S motionpro
```

Verify installation:

```bash
which vpn_cmdline
```

Expected output:

```
/usr/bin/vpn_cmdline
```

---

## ⚠️ Critical: Host Format Matters

`vpn_cmdline` expects:

```
<gateway_host>[/alias]
```

### ❌ Do NOT use

* `https://`
* Browser URLs
* `/login/index.html`
* `/prx/000/http/...`

### ✅ Correct examples

```text
vpn.example.com
vpn.example.com/employee
203.0.113.10
203.0.113.10/demo
```

---

## 🔐 Basic Connection Command

```bash
sudo vpn_cmdline \
  -h 203.0.113.10 \
  -u demo_user \
  -p 'your_password'
```

Successful output:

```
login successfully!
starting vpn......
connect successfully!
vpn is running...
```

---

## 🔑 Authentication Method (if required)

Some gateways require explicitly specifying the auth backend:

```bash
sudo vpn_cmdline \
  -h 203.0.113.10 \
  -u demo_user \
  -p 'your_password' \
  -m LDAP_METHOD
```

(Common values: `LDAP_METHOD`, `radius`, `local`.)

---

## 🔒 Safer Password Handling

Avoid putting passwords in shell history:

```bash
read -s VPN_PASS
sudo vpn_cmdline -h 203.0.113.10 -u demo_user -p "$VPN_PASS"
unset VPN_PASS
```

---

## 🌐 Verify VPN Tunnel

```bash
ip addr | grep tun0
```

Expected:

```
tun0 ... inet 192.168.x.x peer 1.1.1.1
```

This confirms:

* Tunnel exists
* VPN IP assigned
* L3 VPN is active

---

## 🛑 Disconnecting MotionPro

```bash
sudo vpn_cmdline --stop
```

---

# Part 2: Understanding the Routing Conflict

## 🔍 Why SSH Doesn’t Work Initially

Check how traffic to the internal server is routed:

```bash
ip route get 172.16.50.10
```

Problematic output:

```
172.16.50.10 via 1.1.1.1 dev CloudflareWARP src 172.16.0.2
```

This means:

* Cloudflare WARP captured the traffic
* MotionPro never sees the packets
* SSH hangs or times out

---

## 🧠 Why This Happens

Cloudflare WARP uses:

* Its **own routing table**
* **Policy routing** (`ip rule`)
* High-priority rules that override normal routes

Because of this:

* `ip route add` alone is **not enough**
* We must **override both routing and policy**

---

# Part 3: Routing a Specific IP Through MotionPro (Split VPN)

## ✅ Step 1: Replace the Route (Not Add)

```bash
sudo ip route replace 172.16.50.10/32 dev tun0
sudo ip route flush cache
```

Verify:

```bash
ip route get 172.16.50.10
```

Expected:

```
172.16.50.10 dev tun0 src 192.168.x.x
```

---

## 🔥 Step 2: Override WARP Policy Routing

Check policy rules:

```bash
ip rule
```

Typical output includes:

```
1000: from all lookup warp
```

---

## 🧨 Step 3: Add a Higher-Priority Policy Rule

```bash
sudo ip rule add to 172.16.50.10/32 lookup main priority 100
sudo ip route flush cache
```

Verify again:

```bash
ip route get 172.16.50.10
```

Now traffic flows through `tun0`.

---

## 🔐 Step 4: Test SSH

```bash
ssh demo_user@172.16.50.10
```

If it connects:

* Routing is correct
* VPN coexistence is successful

---

# Part 4: Optional Enhancements

## 🌐 Routing an Entire Subnet (If Allowed)

```bash
sudo ip route replace 172.16.0.0/12 dev tun0
sudo ip rule add to 172.16.0.0/12 lookup main priority 100
sudo ip route flush cache
```

---

## 🔁 Make It Persistent

```bash
sudo nano /usr/local/bin/motionpro-split-routing.sh
```

```bash
#!/bin/bash
ip route replace 172.16.50.10/32 dev tun0
ip rule add to 172.16.50.10/32 lookup main priority 100 || true
ip route flush cache
```

```bash
sudo chmod +x /usr/local/bin/motionpro-split-routing.sh
```

---

# 🧠 Key Takeaways

* Multiple VPNs **can coexist on Linux**
* Cloudflare WARP uses **policy routing**
* `/32` host routes are precise and safe
* `ip route replace` > `ip route add`
* `ip rule` enables deterministic control
* WARP never had to be disabled ✅

---

# ✅ Final Architecture

```
Internet traffic        → Cloudflare WARP
172.16.50.10 (SSH)      → MotionPro VPN (tun0)
Everything else         → unchanged
```

