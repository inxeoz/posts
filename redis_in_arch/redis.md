---
title: Redis
date: '2026-01-23'
description: Checking Valkey (Redis) port on Arch Linux
permalink: posts/{{ title | slug }}/index.html
tags:
- redis
- valkey
- archlinux
categories:
- redis_in_arch
---

You can check which port **Valkey** is running on in several ways. Here are the easiest methods:

---

# ✅ **1. Check the Valkey configuration file**

Open the config file:

```bash
grep ^port /etc/valkey/valkey.conf
```

Typical output:

```
port 6379
```

If it's set to `0`, Valkey is configured **not** to listen on a TCP port.

---

# ✅ **2. Ask the running server using `valkey-cli`**

If Valkey is running, use:

```bash
valkey-cli CONFIG GET port
```

Expected output:

```
1) "port"
2) "6379"
```

This shows the **actual** port used at runtime (even if changed in memory).

---

# ✅ **3. Check systemd’s open ports**

```bash
sudo ss -tulpn | grep valkey
```

or:

```bash
sudo lsof -i -n -P | grep valkey
```

Typical output:

```
valkey-ser 1234 valkey  *:6379
```

---

# ✅ **4. View systemd service journal**

```bash
journalctl -u valkey | grep port
```

Valkey prints the listening port on startup.

---

# Quick check summary:

* **Config file**: `/etc/valkey/valkey.conf`
* **Default port**: `6379`
* **CLI command**: `valkey-cli CONFIG GET port`

---

If you want, I can help you check your specific system output — just paste it here.
