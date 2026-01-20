

---
title: Verifying Offline Frappe ERPNext and Fixing Frontend Issues
date: 2026-01-09
description: Complete guide for verifying and fixing offline Frappe ERPNext deployment issues
permalink: posts/{{ title | slug }}/index.html
tags: [frappe, erpnext, offline, docker, troubleshooting]
---

# 🟢 Verifying Offline Frappe/ERPNext Is Working (and Fixing Frontend Issues)

After loading Docker images from a `.tar` file and starting services with Docker Compose **without internet**, the final and most common hurdle is getting the **frontend (nginx)** container running correctly.

This section explains how to **diagnose, fix, and verify** a successful offline setup.

---

## ✅ Expected Healthy State

Run:

```bash
docker compose -f pwd.yml ps
```

A healthy system looks like this:

```text
backend        Up
db             Up (healthy)
redis-cache    Up
redis-queue    Up
queue-short    Up
queue-long     Up
scheduler      Up
websocket      Up
frontend       Up (port exposed)
```

Example:

```text
frappe_docker-frontend-1   Up   0.0.0.0:8081->8080/tcp
```

If **frontend is missing or restarting**, your site will not be accessible.

---

## ❌ Common Error: Frontend Restart Loop

Frontend logs may show:

```text
host not found in upstream "backend:8000"
```

Or Docker may fail with:

```text
failed to bind host port 0.0.0.0:8080: address already in use
```

### What this means

* Docker **could not bind port 8080** on the host
* Frontend container **never fully starts**
* Nginx cannot resolve `backend` because the container exits immediately

This is **not** a Frappe bug — it’s a Docker port conflict.

---

## ✅ Fix: Change Frontend Port (Recommended)

Edit `pwd.yml`:

```yaml
frontend:
  ports:
    - "8081:8080"
```

Why this works:

* `8080` is commonly already in use
* Internal nginx still listens on `8080`
* Host exposes `8081` instead

---

## 🔄 Restart Cleanly

```bash
docker compose -f pwd.yml down
docker compose -f pwd.yml up -d --pull=never
```

Then confirm:

```bash
docker compose -f pwd.yml ps
```

Frontend **must** be `Up`.

---

## 🌐 Accessing the Site (Important)

Frappe uses **host-based routing**.

If your site is named:

```text
test.local
```

You **must** send the `Host` header.

### CLI test

```bash
curl -H "Host: test.local" http://localhost:8081
```

Expected output:

```html
<title>Login</title>
```

---

## 🌍 Browser Access

Add to `/etc/hosts` (host machine):

```text
127.0.0.1 test.local
```

Then open:

```
http://test.local:8081
```

You should see the **ERPNext login page**.

---

## 🔎 Extra Verification Commands

### Confirm site exists

```bash
docker compose -f pwd.yml exec backend ls sites
```

Expected:

```text
test.local
```

### Confirm backend config

```bash
docker compose -f pwd.yml exec backend \
  cat sites/test.local/site_config.json
```

You should see:

```json
"db_host": "db"
```

---

## 🧠 Key Takeaways (Offline Deployments)

* Docker images **must be saved together**:

  * `frappe/erpnext`
  * `mariadb`
  * `redis`
* Use:

  ```bash
  docker compose up --pull=never
  ```
* Frontend issues are **almost always port conflicts**
* Backend running ≠ site accessible
* Frappe requires **Host headers**, even locally

---
