---
title: Cloudflare Tunnel
date: 2025-11-18
description: Complete Cloudflare Tunnel setup and troubleshooting
permalink: posts/{{ title | slug }}/index.html
tags: [cloudflare, tunnel, networking]
---


# ⭐ **Cloudflare Tunnel From Zero to Hero (2025 Edition)**

### **A Complete Guide to Installing, Configuring, Troubleshooting, and Running Cloudflare Tunnel — Even on Wi-Fi That Blocks It**

Cloudflare Tunnel (formerly Argo Tunnel) is one of the simplest, safest ways to expose private or local services to the public internet — **without port forwarding**, without opening firewall ports, and without revealing your server’s IP address.

But as networks get stricter, many users find Cloudflare Tunnel failing — especially on Wi-Fi networks in cafes, hotels, schools, or offices.
Cloudflare WARP solves this problem by routing Tunnel traffic safely over **HTTPS (443)**, a universally allowed port.

This “Zero to Hero” article takes you through everything:

1. **Understanding Cloudflare Tunnel**
2. **Installing tools on Linux**
3. **Creating and configuring tunnels**
4. **Understanding why some Wi-Fi blocks Tunnel traffic**
5. **Fixing blocked tunnel connections with Cloudflare WARP**
6. **Running tunnels in the background (systemd)**
7. **Testing, debugging, and best practices**

Whether you're exposing a dev server, a self-hosted app, ERPNext/Frappe, or a private admin panel — this guide gets you from nothing to production-ready.

---

# 🟦 **1. What Is Cloudflare Tunnel?**

Cloudflare Tunnel is a secure, outbound-only connection from your device to Cloudflare’s global network.

### ✔ You DO NOT need:

* Port forwarding
* Public IP
* Router changes
* Firewall modifications

### ✔ You get:

* Encrypted traffic
* Zero-trust access
* DDoS protection
* Global load balancing
* High availability (multiple connectors)

Cloudflared (the client) creates a secure connection from your machine to Cloudflare’s edge, then Cloudflare routes outside traffic to your local application.

---

# 🟦 **2. Install Cloudflare Tunnel (cloudflared)**

On **Arch Linux**:

```bash
sudo pacman -S cloudflared
```

On other distros:

```bash
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
sudo install cloudflared /usr/local/bin/
```

Verify:

```bash
cloudflared --version
```

---

# 🟦 **3. Login to Cloudflare**

```bash
cloudflared tunnel login
```

A browser opens → choose your domain → authorize.

This creates:

```
~/.cloudflared/cert.pem
```

---

# 🟦 **4. Create Your Tunnel**

```bash
cloudflared tunnel create my-tunnel
```

You get a UUID:

```
abcd1234-...-ef567890.json
```

Stored at:

```
~/.cloudflared/<UUID>.json
```

---

# 🟦 **5. Configure the Tunnel**

Create:

```bash
nano ~/.cloudflared/config.yml
```

Example:

```yaml
tunnel: <TUNNEL-UUID>
credentials-file: /home/<user>/.cloudflared/<TUNNEL-UUID>.json

protocol: http2
quic: off

ingress:
  - hostname: app.example.com
    service: http://localhost:8080

  - hostname: app2.example.com
    service: http://localhost:8081

  - service: http_status:404
```

Save and exit.

---

# 🟦 **6. Route Your Domain to the Tunnel**

Create DNS record automatically:

```bash
cloudflared tunnel route dns my-tunnel app.example.com
```

```bash
cloudflared tunnel route dns my-tunnel app2.example.com
```

Now visiting `https://app.example.com` will route through Cloudflare Tunnel → your device.

---

# 🟦 **7. Start the Tunnel**

```bash
cloudflared tunnel run my-tunnel
```

If logs show:

```
Registered tunnel connection
protocol=http2
location=...
```

You’re live.

---

# Run in background 

```

~/.cloudflared ❯ sudo cloudflared --config ~/.cloudflared/config.yml service install
[sudo] password for inxeoz:
2025-11-19T05:29:10Z INF Using Systemd
2025-11-19T05:29:15Z INF Linux service for cloudflared installed successfully

~/.cloudflared ❯ sudo systemctl start cloudflared
sudo systemctl enable cloudflared

~/.cloudflared ❯
```

# 🟥 **8. Why Cloudflare Tunnel Fails on Some Wi-Fi Networks**

Many users encounter:

```
dial tcp <ip>:7844: i/o timeout
failed to dial a quic connection
connection timeout
```

This happens because Cloudflare Tunnel normally connects via:

| Protocol | Port     | Purpose                    |
| -------- | -------- | -------------------------- |
| QUIC     | UDP/7844 | primary tunnel transport   |
| HTTP/2   | TCP/7844 | fallback if UDP is blocked |

**Many public or corporate networks block:**

* all UDP
* all non-standard ports
* ALL traffic on port **7844**

Even when you force HTTP/2:

```
protocol: http2
```

Cloudflared still uses **7844**, just over TCP.

If **7844 is blocked entirely**, Tunnel **always fails**.

---

# 🟦 **9. Real Fix: Use Cloudflare WARP to Tunnel Over Port 443**

Cloudflare WARP sends Cloudflare traffic through an encrypted WireGuard tunnel using **standard HTTPS port 443**.

✔ Works on any network
✔ No need to modify Wi-Fi or firewall
✔ Official Cloudflare-supported workaround
✔ 100% safe for legitimate Tunnel use

This is the full solution when ports needed by Tunnel are blocked.

---

# 🟩 **10. Install WARP on Arch Linux**

```bash
yay -S cloudflare-warp-bin
```

Enable the daemon:

```bash
sudo systemctl enable --now warp-svc.service
```

---

# 🟩 **11. Register WARP (2025 CLI syntax)**

```bash
warp-cli registration new
```

Verify:

```bash
warp-cli registration show
```

---

# 🟩 **12. Enable WARP Mode**

```bash
warp-cli mode set warp
```

Then:

```bash
warp-cli connect
```

Check status:

```bash
warp-cli status
```

You want:

```
Status: Connected
Network: healthy
```

Once WARP is connected, Cloudflare Tunnel traffic is safely routed through port 443.

---

# 🟩 **13. Run Cloudflare Tunnel With WARP Enabled**

Just run:

```bash
cloudflared tunnel run my-tunnel
```

Now you will see successful logs:

```
Registered tunnel connection
protocol=http2
```

No more 7844 errors.

---

# 🟦 **14. Run Cloudflare Tunnel in the Background (systemd)**

## **Option A — Built-in service (recommended)**

```bash
sudo cloudflared service install
sudo systemctl enable --now cloudflared
```

Cloudflare automatically uses `~/.cloudflared/config.yml`.

### Manage it:

Start:

```bash
sudo systemctl start cloudflared
```

Restart:

```bash
sudo systemctl restart cloudflared
```

Status:

```bash
systemctl status cloudflared
```

uninstall:

```bash
sudo cloudflared service uninstall
```

uninstall:

```bash
sudo cloudflared service uninstall
```
```
sudo rm /etc/cloudflared/config.yml
```
```
sudo systemctl daemon-reload
```


---

## **Option B — Custom per-tunnel service**

Create:

```bash
sudo nano /etc/systemd/system/cf-tunnel.service
```

Add:

```ini
[Unit]
Description=Cloudflare Tunnel
After=network.target

[Service]
User=<user>
ExecStart=/usr/bin/cloudflared tunnel run my-tunnel
Restart=always
RestartSec=5s

[Install]
WantedBy=multi-user.target
```

Enable:

```bash
sudo systemctl enable --now cf-tunnel
```

---

# 🟦 **15. Testing & Troubleshooting**

### Check logs:

```bash
journalctl -u cloudflared -f
```

### Check WARP status:

```bash
warp-cli status
```

### Check DNS record:

```bash
dig app.example.com
```

### Use Tunnel diagnostics:

```bash
cloudflared tunnel info my-tunnel
cloudflared tunnel list
```

---

# 🟩 **16. Best Practices**

✔ Use WARP on restrictive networks
✔ Use systemd for 24/7 tunnels
✔ Keep your tunnel UUID and credentials secure
✔ Use Access Policies if exposing admin systems
✔ Use HTTP/2 or WebSockets for better reliability

---

# 🟦 **17. Conclusion — From Zero to Hero**

By following this guide, you’ve gone through:

* Installing cloudflared
* Creating a secure Cloudflare Tunnel
* Routing a domain to your local application
* Understanding why some networks block Tunnel traffic
* Deploying Cloudflare WARP to bypass blocked ports safely
* Running your tunnel in the background using systemd

This setup is powerful enough for:

* Developers exposing localhost
* Self-hosters running apps at home
* ERPNext, Frappe, Home Assistant
* Remote dashboards and admin panels
* Production-grade zero trust deployments

You now have a **rock-solid, globally accessible, firewall-friendly Tunnel**, even on the strictest networks.

---
