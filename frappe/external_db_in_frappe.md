---
title: Creating a New MariaDB Container for a Frappe Site
date: '2026-01-23'
description: Guide for attaching a new Frappe site to a separate MariaDB container
  with DB isolation
permalink: posts/{{ title | slug }}/index.html
tags:
- frappe
- mariadb
- docker
- database
categories:
- frappe
---

# 📘 Creating a New MariaDB Container for a Frappe Site

### (and avoiding the 200 / 500 alternating error)

This article explains **why**, **how**, and **what to restart** when you want to attach a **new Frappe site to a separate MariaDB container** on the **same server**, without internet access.

---

## 🧭 Use Case

* One server (offline, SSH only)
* Docker + Docker Compose
* Existing Frappe stack already running
* Need **hard DB isolation** for a new site (e.g. `s3.inxeoz.com`)
* Want to avoid random **200 / 500 alternating errors**

---

## ✅ Preconditions (DO NOT SKIP)

Before starting, confirm:

* ✔ Docker is installed and working
* ✔ Frappe stack is already running via Docker Compose
* ✔ You are **not modifying existing sites**
* ✔ You have **SSH access** to the server
* ✔ You understand this adds **operational complexity**
* ✔ This is intentional isolation (not accidental)

---

## ⚠️ Risk Level

**Medium**

Why:

* New database server
* New site creation
* Requires worker reload

Safe because:

* No existing DB is touched
* Fully reversible
* No network / SSH changes

---

## 🧠 Important Facts (Read This First)

* **One MariaDB container can host many sites** (default, recommended)
* Using **multiple MariaDB containers** is:

  * valid
  * advanced
  * heavier to maintain
* Frappe **binds a site to a DB host at creation time**
* Frappe **caches DB connections in workers**
* In scaled setups, **workers must be restarted** after site creation

---

## 🗂️ Architecture After This Setup

```
frappe-db-1   → s1.inxeoz.com
frappe-db-1   → s2.inxeoz.com
mariadb-s3    → s3.inxeoz.com
```

Traefik / Nginx remain unchanged.

---

## 1️⃣ Create a New MariaDB Container (Standalone)

Create a **new compose file** (no overrides):

📄 `third_db.compose.yaml`

```yaml
version: "3.8"

services:
  mariadb_s3:
    image: mariadb:11.8
    container_name: mariadb-s3
    restart: unless-stopped
    environment:
      MARIADB_ROOT_PASSWORD: s3rootpass
    volumes:
      - mariadb_s3_data:/var/lib/mysql
    networks:
      - frappe_default

volumes:
  mariadb_s3_data:

networks:
  frappe_default:
    external: true
```

### Why this works

* Uses **existing Docker network**
* No port exposure
* Separate volume
* No impact on existing DB

---

## 2️⃣ Start the New DB Container

```bash
docker compose -f third_db.compose.yaml up -d
```

Verify:

```bash
docker ps | grep mariadb
```

You should see:

```
frappe-db-1
mariadb-s3
```

---

## 3️⃣ Create the New Frappe Site (Attach DB at Creation)

⚠️ **Do NOT create DB manually**
Let Frappe do it (cleaner, safer).

```bash
docker compose -p frappe exec backend \
  bench new-site s3.inxeoz.com \
  --db-host mariadb_s3 \
  --db-name s3_db \
  --db-root-password s3rootpass \
  --admin-password 0000
```

### What Frappe does automatically

* Connects to `mariadb_s3`
* Creates `s3_db`
* Creates site-specific DB user
* Writes `site_config.json`
* Creates all tables

---

## 4️⃣ Verify DB Binding (Read-Only)

### From Frappe side

```bash
docker compose -p frappe exec backend \
  cat sites/s3.inxeoz.com/site_config.json
```

You must see:

```
"db_host": "mariadb_s3"
"db_name": "s3_db"
```

### From MariaDB side

```bash
docker exec -it mariadb-s3 \
  mariadb -uroot -p -e "SHOW DATABASES;"
```

You must see:

```
s3_db
```

---

## 5️⃣ Why You May See Alternating 200 / 500 Errors

### Symptom

```bash
curl -H "Host: s3.inxeoz.com" http://127.0.0.1
```

* First request → Login page
* Second request → 500 error
* Alternates randomly

### Root Cause (Very Important)

* You have **multiple Frappe workers**
* Site was created **while workers were running**
* Some workers still hold **stale DB connection state**
* Load balancer rotates requests → inconsistent behavior

This is **expected** in scaled Frappe setups.

---

## 6️⃣ The CORRECT Fix (Safe & Minimal)

Restart **all Frappe application workers**
⚠️ **NOT databases, NOT nginx, NOT Traefik**

```bash
docker compose -p frappe restart \
  backend websocket queue-short queue-long scheduler
```

### What this does

* Reloads all Python workers
* Clears DB connection pools
* Syncs site → DB mapping everywhere

Downtime: **a few seconds**

---

## 7️⃣ Final Verification

Run multiple times:

```bash
curl -H "Host: s3.inxeoz.com" http://127.0.0.1 | head -5
```

Expected:

* Login page every time
* No 500 errors

---

## 🚫 What NOT To Do

* ❌ Do NOT restart MariaDB containers
* ❌ Do NOT restart nginx blindly
* ❌ Do NOT reboot the server
* ❌ Do NOT recreate the site
* ❌ Do NOT edit `site_config.json` manually
* ❌ Do NOT expose DB ports

---

## 🧠 Key Rules to Remember

1. **Bind DB at site creation**
2. **Let Frappe create DB if root access exists**
3. **Restart all Frappe workers after new site**
4. **One transient 500 is normal; repeated is not**
5. **Databases must live on the same server in offline setups**
