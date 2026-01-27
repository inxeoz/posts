---
title: Connecting to Array Networks VPN from Linux
date: '2026-01-27'
description: Policy-compliant method to access Array Networks SSL VPN from Linux using
  Android MotionPro and SOCKS proxy
permalink: posts/{{ title | slug }}/index.html
tags:
- vpn
- array-networks
- linux
- android
- socks-proxy
categories:
- networking
---

# Connecting to an Array Networks VPN from Linux using MotionPro (Android) + Termux + SOCKS Proxy

## Abstract

Array Networks SSL VPN deployments often enforce **MotionPro device identification (machineid / hardware ID)**, which blocks Linux and third-party VPN clients such as OpenConnect.
However, many organizations **allow mobile VPN access** via the official **MotionPro Android application**.

This article documents a **fully working, policy-compliant method** to access internal resources from a Linux host by:

- Using **MotionPro on Android** as the VPN endpoint
- Running **Termux + OpenSSH** on Android
- Exposing a **SOCKS5 proxy** over USB/Wi-Fi tethering
- Tunneling Linux traffic (SSH, curl, browsers, tools) through that proxy

No reverse engineering, no bypassing device checks, and no modification of the VPN infrastructure is required.

------

## Background: Why Linux Clients Fail with Array VPN

Array Networks SSL VPN gateways commonly enforce:

- **MotionPro-only Agent SSL VPN**
- **Hardware ID / machineid**
- **LDAP + device binding**

As a result:

- OpenConnect (even with `--protocol=array`) fails post-authentication
- Linux cannot generate a valid MotionPro hardware ID
- Authentication succeeds, but session creation fails (`internal error (11)`)

However, **mobile VPN access** often uses a *different device identification model* and is allowed.

------

## High-Level Architecture

```
Linux Host
   |
   | (SOCKS5)
   v
Android Phone (Termux)
   |
   | (MotionPro VPN)
   v
Array Networks SSL VPN
   |
   v
Internal Network / Servers
```

Key idea:

- Android becomes the **trusted VPN endpoint**
- Linux connects **through Android**, not directly to the VPN

------

## Requirements

### Hardware

- Android phone (Android 10+ recommended)
- Linux machine
- USB cable (USB tethering preferred)

### Software

- MotionPro (Android, from Play Store)
- Termux (Android)
- OpenSSH (Termux)
- Standard Linux tools (`ssh`, `curl`, `nc`)

------

## Step 1: Install and Connect MotionPro on Android

1. Install **MotionPro** from Google Play Store
2. Open MotionPro
3. Configure your Array VPN server:
   - Server: `https://<vpn-gateway>`
   - Username / Password / MFA as required
4. Connect successfully

✅ At this point, **the phone itself can access internal resources**

------

## Step 2: Install Termux and OpenSSH

1. Install **Termux** from Play Store or F-Droid

2. Open Termux

3. Update packages:

   ```bash
   pkg update && pkg upgrade
   ```

4. Install OpenSSH:

   ```bash
   pkg install openssh
   ```

------

## Step 3: Set a Termux Password (Required)

Termux SSH requires a password for localhost login:

```bash
passwd
```

Choose a password (this is local to Termux).

------

## Step 4: Start the SSH Daemon (Important Detail)

⚠️ **Termux cannot bind to port 22** (Android restriction).
It uses **port 8022**.

Start SSH daemon explicitly:

```bash
sshd -p 8022
```

Verify it’s running:

```bash
ps aux | grep sshd | grep -v grep
```

------

## Step 5: Start a SOCKS5 Proxy on Android

Run **this exact command** in Termux:

```bash
ssh -p 8022 -g -D 1080 -N localhost
```

### Explanation

- `-D 1080` → create SOCKS5 proxy on port 1080
- `-g` → allow remote connections (critical)
- `-N` → no shell, proxy only
- `localhost` → connects to Termux SSH server

⚠️ **Leave this process running**
Do not close Termux.

------

## Step 6: Prevent Android from Killing the Tunnel

On Android:

1. Settings → Apps → **Termux**
2. Battery:
   - Disable battery optimization
   - Set to **Unrestricted**
3. Do the same for **MotionPro**
4. Lock Termux in recent apps (optional but recommended)

This is critical for stability.

------

## Step 7: Enable USB Tethering (Recommended)

1. Connect Android phone to Linux via USB
2. Enable **USB tethering** on Android
3. On Linux, verify network:

```bash
ip route
```

Example:

```
default via 10.78.118.223 dev enp0s20f0u2
```

Here:

- `10.78.118.223` = Android phone IP
- `enp0s20f0u2` = USB tether interface

------

## Step 8: Configure SOCKS Proxy on Linux

Set proxy environment variables:

```bash
export ALL_PROXY=socks5://10.78.118.223:1080
export all_proxy=socks5h://10.78.118.223:1080
```

(`socks5h` ensures DNS is resolved through the proxy)

------

## Step 9: Verify the Proxy Works

Test with a public endpoint:

```bash
curl -v https://ifconfig.me
```

Expected behavior:

- Connection succeeds
- Output shows an IP (often mobile or corporate)

This confirms:

- SOCKS proxy is reachable
- Android → VPN path works

------

## Important Networking Note (Docker Conflict)

Many Linux systems have Docker networks like:

```
172.18.0.0/16 dev docker0
```

If your **internal network also uses 172.18.x.x**, then:

- Direct routing will **never work**
- `ping` and raw `ssh` will fail
- **SOCKS proxy is mandatory**

This is normal and expected.

------

## Step 10: SSH to Internal Hosts (Correct Way)

SSH **ignores proxy environment variables**.
You must explicitly configure it.

### One-off SSH command

```bash
ssh -o ProxyCommand="nc -x 10.78.118.223:1080 %h %p" root@172.18.210.49
```

On first connect, accept the host key.

If credentials are correct, you’ll land on:

```
[root@internal-host ~]#
```

🎉 You are inside the internal network.

------

## Step 11: Permanent SSH Configuration (Recommended)

Edit SSH config:

```bash
nano ~/.ssh/config
```

Add:

```sshconfig
Host corp-rhv
  HostName 172.18.210.49
  User root
  ProxyCommand nc -x 10.78.118.223:1080 %h %p
```

Now simply run:

```bash
ssh corp-rhv
```

------

## What Works Through This Setup

✅ SSH
✅ curl / wget
✅ Browsers (Firefox SOCKS proxy)
✅ Git / npm / pip (with proxy config)
✅ Databases and internal APIs
✅ ERP / internal dashboards

------

## What Does NOT Work (By Design)

❌ `ping`
❌ Raw routing
❌ Linux VPN clients (OpenConnect, etc.)
❌ Sharing Android VPN without proxy
❌ Reusing MotionPro hardware IDs

------

## Why This Method Is Safe and Compliant

- Uses **official MotionPro client**
- Uses **allowed mobile VPN access**
- No manipulation of VPN traffic
- No spoofing device identity
- No policy bypass

This is equivalent to:

> “Accessing internal resources from a mobile device, then forwarding traffic.”

------

## Stability Tips

- Keep Termux open
- Keep MotionPro connected
- Disable Android battery optimization
- Prefer USB tethering over Wi-Fi
- Optionally use `tmux` in Termux

------

