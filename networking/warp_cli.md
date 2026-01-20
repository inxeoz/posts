
---
title: Cloudflare WARP CLI Split-Tunneling Guide
date: 2026-01-15
description: Key notes and commands for Cloudflare WARP CLI split-tunneling behavior, verification, and routing configuration
permalink: posts/{{ title | slug }}/index.html
tags: [cloudflare, warp, vpn, networking, cli, split-tunnel]
---

# 📌 Cloudflare WARP (`warp-cli`) Split-Tunneling — Key Notes

---

## 🧠 Core facts (most important)

* Your `warp-cli` version:

  * Uses **exclude-mode split tunneling by default**
  * **Does NOT support** `--exclude`, `exclude`, or CIDR flags in `tunnel ip add`
  * Accepts **single IPs only**, not `/32`
* **Local network override is blocked** by policy (Zero Trust / org-managed)
* Split tunneling is enforced via:

  * **Policy routing**
  * **Firewall rules**
  * **WARP daemon** (not just `ip route`)

---

## 🎯 Routing behavior (final result)

| Traffic type             | Route                     |
| ------------------------ | ------------------------- |
| Public internet          | ✅ via **WARP**            |
| Private IPs (10/172/192) | ❌ bypass WARP             |
| `localhost / 127.0.0.1`  | ❌ never goes through WARP |
| Excluded public IPs      | ❌ bypass WARP             |

---

## ✅ Commands that WORK (copy-paste safe)

### Set WARP mode

```bash
warp-cli mode warp
```

---

### Connect / reconnect

```bash
warp-cli connect
warp-cli disconnect
```

---

### Add IP exclusions (exclude mode)

```bash
warp-cli tunnel ip add 103.86.26.3
warp-cli tunnel ip add 172.18.210.49
```

📌 These IPs will **bypass WARP**

---

### View split-tunnel configuration (MOST IMPORTANT)

```bash
warp-cli tunnel dump
```

Look for:

* `Excluded:` list
* Your custom IPs present

---

### Check connection state

```bash
warp-cli status
```

---

## ❌ Commands that do NOT work (by design)

```bash
warp-cli split-tunnel ...
warp-cli tunnel ip add exclude ...
warp-cli tunnel ip add <ip>/32
warp-cli override local-network enable
warp-cli override local-network allow   # blocked by policy
```

Reason:

* New CLI syntax
* Org / Zero Trust policy restrictions

---

## 🔍 Verification commands (kernel-level truth)

### See routing decision for a specific IP

```bash
ip route get 103.86.26.3
```

Expected:

* Normal NIC (`eth0` / `wlan0`)
* ❌ not `warp0`

---

### Test normal public IP

```bash
ip route get 1.1.1.1
```

Expected:

* `dev warp0`

---

### View routing tables

```bash
ip route
ip rule show
ip route show table all
```

---

## 🧪 Traffic proof (optional)

```bash
sudo tcpdump -i warp0 host 103.86.26.3
```

Should show **no traffic**.

---

## 🌐 URL vs routing (important concept)

Routing only cares about:

```
https://103.86.26.3/...
```

Everything after the IP:

```
/prx/000/http/localhost/login/index.html
```

➡ **Application layer**, irrelevant to routing.

---

## 🧠 Why `warp-cli tunnel dump` looks long / duplicated

It includes:

* RFC1918 private ranges
* Multicast & link-local ranges
* IPv6 equivalents
* Cloudflare control-plane IPs
* Your manual exclusions

Duplicates are **normal and harmless**.

---

## 🚦 Policy reality (no workaround)

If you see:

```bash
Error: Operation not authorized in this context
```

It means:

* You are on **Zero Trust / org-managed WARP**
* Local-network override is **admin-controlled**
* CLI **cannot bypass policy**

---
