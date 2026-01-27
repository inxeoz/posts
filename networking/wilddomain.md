---
title: How to Safely Set Up Wildcard Domain Resolution on Linux
date: '2026-01-23'
description: Safe wildcard domain resolution setup using systemd-resolved and dnsmasq
  without breaking system DNS
permalink: posts/{{ title | slug }}/index.html
tags:
- dns
- wildcard
- linux
- systemd
- dnsmasq
categories:
- networking
---

Here is the **final polished article**, now including a clean, complete **"How to Remove Wildcard Domain Resolution"** section.
This version is publication-ready.


---

# 📝 **How to Safely Set Up Wildcard Domain Resolution on Linux Without Breaking Your System**

### *(Modern systemd-resolved + dnsmasq Split DNS Method)*

Local development environments often need custom domains like:

```
http://myapp.test
http://api.test
http://backend.internal.test
```

But achieving wildcard resolution (i.e., `*.test → 127.0.0.1`) is tricky.
Most tutorials break DNS by:

* Overwriting `/etc/resolv.conf`
* Disabling systemd-resolved
* Hijacking port 53
* Interfering with libvirt DNS
* Using `.local` (reserved for mDNS)

This article walks you through **the correct, safe, reversible approach** that works on:

* Arch Linux & Omarchy Linux
* Fedora
* Ubuntu
* Manjaro
* Any Linux using **systemd-resolved**

---

# 🎯 **Goal**

We want:

```
*.test → 127.0.0.1
```

**WITHOUT breaking:**

* system DNS
* VPN DNS
* libvirt/QEMU DNS
* systemd-resolved
* Network connectivity

The solution must be:

* wildcard-capable
* isolated
* non-conflicting
* 100% reversible

---

# 🏆 The Best Method

# **Use dnsmasq on a separate port + systemd-resolved split DNS routing**

This gives:

✔ Full wildcard `.test` support
✔ No conflict with system services
✔ systemd-resolved remains fully functional
✔ No broken networking
✔ Fully reversible
✔ No changes to `/etc/resolv.conf`
✔ No touching port 53

This is how enterprise VPN clients and container systems (Podman, LXD, Kubernetes) implement split DNS.

---

# 🛠️ Step 1 — Create a dedicated dnsmasq instance on port 5353

Create config directory:

```bash
sudo mkdir -p /etc/dnsmasq.d-test
sudo nano /etc/dnsmasq.d-test/test.conf
```

Add:

```ini
# dnsmasq for .test wildcard resolution
port=5353
bind-interfaces
listen-address=127.0.0.1

# Wildcard domain rule
address=/.test/127.0.0.1
```

This ensures dnsmasq **never conflicts** with system services.

---

# 🛠️ Step 2 — Create a systemd service for this dnsmasq

```bash
sudo nano /etc/systemd/system/dnsmasq-test.service
```

Add:

```ini
[Unit]
Description=Dnsmasq Instance for .test Wildcard Resolution
After=network.target

[Service]
ExecStart=/usr/bin/dnsmasq --keep-in-foreground --conf-dir=/etc/dnsmasq.d-test
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

Enable & start:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now dnsmasq-test
```

Test:

```bash
systemctl status dnsmasq-test
```

---

# 🧪 Step 3 — Verify dnsmasq answers `.test` queries

```bash
dig @127.0.0.1 -p 5353 hello.test
```

Should return:

```
hello.test.  0  IN A  127.0.0.1
```

---

# 🛠️ Step 4 — Configure systemd-resolved split DNS

```bash
sudo mkdir -p /etc/systemd/resolved.conf.d
sudo nano /etc/systemd/resolved.conf.d/10-test-domain.conf
```

Add:

```ini
[Resolve]
DNS=127.0.0.1:5353
Domains=~test
```

Meaning:

* Only `.test` domains go to dnsmasq-test
* All other domains go through your normal DNS

Reload:

```bash
sudo systemctl restart systemd-resolved
```

---

# 🧪 Step 5 — Test wildcard resolution

```bash
resolvectl query hello.test
resolvectl query anything.test
resolvectl query backend.internal.test
```

You should always get:

```
127.0.0.1
```

Test in browser:

```
http://myapp.test
```

This now resolves cleanly without modifying `/etc/hosts`.

---

# 🤓 Why This Works (Deep Explanation)

systemd-resolved acts as the system DNS interceptor.
When you add:

```
Domains=~test
DNS=127.0.0.1:5353
```

You instruct resolved to:

> Forward ONLY `.test` queries to dnsmasq-test,
> and ignore upstream DNS servers for these queries.

dnsmasq-test uses:

```
address=/.test/127.0.0.1
```

So *any* `.test` domain — regardless of subdomain depth — returns `127.0.0.1`.

This results in:

| Domain           | Resolver     | Output    |
| ---------------- | ------------ | --------- |
| hello.test       | dnsmasq-test | 127.0.0.1 |
| api.backend.test | dnsmasq-test | 127.0.0.1 |
| google.com       | upstream DNS | real IP   |
| archlinux.org    | upstream DNS | real IP   |

No conflict.
No breakage.
No override of system functions.

---

# 🗑️ **How to Completely Remove Wildcard .test Configuration**

*(100% rollback, safe)*

### 1️⃣ Remove dnsmasq-test config & disable service

```bash
sudo systemctl disable --now dnsmasq-test
sudo rm -r /etc/dnsmasq.d-test
sudo rm /etc/systemd/system/dnsmasq-test.service
```

Reload systemd:

```bash
sudo systemctl daemon-reload
```

---

### 2️⃣ Remove split-DNS rule from systemd-resolved

```bash
sudo rm /etc/systemd/resolved.conf.d/10-test-domain.conf
```

Restart resolver:

```bash
sudo systemctl restart systemd-resolved
```

---

### 3️⃣ Verify cleanup

```bash
resolvectl domain
resolvectl dns
```

Ensure `.test` no longer appears in routing.

---

### 4️⃣ Test:

```bash
resolvectl query hello.test
```

Should now return:

```
Failed to resolve …
```

Wildcard setup removed successfully.

---

# 🎉 Final Thoughts

This method is:

* modern
* robust
* systemd-compatible
* container-friendly
* VPN-friendly
* zero-conflict
* wildcard-capable
* fully reversible

It's the **safest way on modern Linux** to get `.test` (or `.dev`, `.lab`, `.localtest`) wildcard DNS resolution — perfect for:

* Frappe
* Docker
* local microservices
* FM (Frappe Manager)
* web dev environments
* custom proxies

---

If you want, I can also extend this article to cover:

✔ Multiple wildcard domains (`*.dev`, `*.localtest`, `*.sandbox`)
✔ How to set up HTTPS for `.test` using mkcert
✔ Using CoreDNS instead of dnsmasq
✔ Using this setup with Docker Compose or FM

Just tell me what you want!
