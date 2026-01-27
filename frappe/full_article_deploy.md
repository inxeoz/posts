# 🚀 Deploying ERPNext (Frappe) with Docker in an Offline / Air-Gapped Environment

**From Local Setup to Server Deployment (Complete Guide)**

---

## 1. Why This Guide Exists

In many enterprise environments:

* Internet access is **restricted or completely blocked**
* Servers are accessible **only via SSH**
* Docker images must be **pre-approved**
* Production servers **cannot pull images from Docker Hub**

This guide shows how to:

* Build an **offline Docker image bundle (`.tar`)**
* Transfer it to a **remote server**
* Load and run **ERPNext (Frappe) fully offline**
* Operate **backend, database, and workers safely**
* Fix common real-world issues (ports, frontend crashes, networking)

Everything here is **battle-tested**.

---

## 2. Architecture Overview (What We’re Deploying)

ERPNext using Docker consists of **multiple containers**, not one:

| Service      | Purpose                    |
| ------------ | -------------------------- |
| frontend     | Nginx (public entry point) |
| backend      | Frappe / ERPNext app       |
| db           | MariaDB                    |
| redis-cache  | Cache                      |
| redis-queue  | Queue                      |
| websocket    | Socket.IO                  |
| scheduler    | Scheduled jobs             |
| queue-short  | Background workers         |
| queue-long   | Background workers         |
| configurator | Initial config             |
| create-site  | Site bootstrap             |

📌 **Only frontend is exposed publicly**
Everything else stays on the Docker network.

---

## 3. Prerequisites

### Local Machine (with Internet)

* Docker
* Docker Compose
* Git
* Enough disk space (~6–8 GB)

### Server (Offline / Restricted)

* Docker
* Docker Compose
* SSH access
* Firewall access to chosen port (e.g. 8081)

---

## 4. Fetch Frappe Docker Setup (Online Machine)

```bash
git clone https://github.com/frappe/frappe_docker
cd frappe_docker
```

This repo provides **production-grade Docker Compose definitions**.

---

## 5. Choose ERPNext Version

We used:

```text
frappe/erpnext:v15.93.2
```

**Important:**
Version mismatch between images causes silent failures. Always lock versions.

---

## 6. Docker Compose File (pwd.yml)

This is a **trimmed production-style compose** using official images.

Key points:

* One shared Docker network
* Volumes for persistence
* No internet dependency

👉 You already validated this file, so we **do not modify it further**.

---

## 7. Pull Required Images (Online Machine)

```bash
docker pull frappe/erpnext:v15.93.2
docker pull mariadb:10.6
docker pull redis:6.2-alpine
```

Verify:

```bash
docker images | egrep 'frappe|mariadb|redis'
```

---

## 8. Create Offline Docker Image Bundle (TAR)

This is the **most important step**.

```bash
docker save \
  frappe/erpnext:v15.93.2 \
  mariadb:10.6 \
  redis:6.2-alpine \
  -o frappe_pwd_v15_offline.tar
```

Result:

```
frappe_pwd_v15_offline.tar
```

✔ Single file
✔ Can be scanned, approved, transferred
✔ No internet required later

---

## 9. Transfer TAR to Server

From local machine:

```bash
scp frappe_pwd_v15_offline.tar root@SERVER_IP:/root/frappe_docker/
```

---

## 10. Load Images on Server (Offline)

SSH into server:

```bash
ssh root@SERVER_IP
cd frappe_docker
```

Load images:

```bash
docker load -i frappe_pwd_v15_offline.tar
```

Verify:

```bash
docker images | egrep 'frappe|mariadb|redis'
```

✅ Images are now available locally
❌ No Docker Hub access required

---

## 11. Start ERPNext Stack (Offline)

```bash
docker compose -f pwd.yml up -d --pull=never
```

Why `--pull=never`?

* Guarantees **zero internet usage**
* Prevents accidental image mismatch

---

## 12. Verify Containers

```bash
docker compose -f pwd.yml ps
```

You should see:

* backend → running
* db → healthy
* redis → running
* frontend → running
* workers → running

---

## 13. Create ERPNext Site

```bash
docker compose -f pwd.yml exec backend \
  bench new-site test.local \
  --admin-password admin \
  --db-root-password admin \
  --install-app erpnext
```

Confirm site exists:

```bash
docker compose -f pwd.yml exec backend ls sites
```

You should see:

```
test.local
```

---

## 14. Fix Frontend Restart Loop (Critical)

### Problem

Frontend keeps restarting with:

```
host not found in upstream "backend:8000"
```

### Root Causes

* Port already in use
* Network not recreated cleanly
* Backend container not resolvable

### Fix (Clean Reset)

```bash
docker compose -f pwd.yml down
docker compose -f pwd.yml up -d --pull=never
```

If port conflict exists:

```yaml
ports:
  - "8081:8080"
```

---

## 15. Access ERPNext from Browser

### From server host:

```bash
curl -H "Host: test.local" http://localhost:8081
```

### From your local machine:

```text
http://SERVER_IP:8081
```

✔ ERPNext login page should load

---

## 16. Firewall Configuration (Server)

Check open ports:

```bash
firewall-cmd --list-ports
```

Allow frontend port if needed:

```bash
firewall-cmd --add-port=8081/tcp --permanent
firewall-cmd --reload
```

⚠️ Do NOT expose:

* 3306 (MariaDB)
* 6379 (Redis)
* 8000 (backend)

---

## 17. Backend Operations (Day-to-Day Work)

### Enter backend container

```bash
docker compose -f pwd.yml exec backend bash
```

### Common commands

```bash
bench use test.local
bench migrate
bench clear-cache
bench console
bench restart
```

Exit:

```bash
exit
```

---

## 18. Database Access (Safe Way)

```bash
docker compose -f pwd.yml exec db mysql -uroot -p
```

Password:

```
admin
```

---

## 19. Logs & Debugging

```bash
docker compose -f pwd.yml logs frontend
docker compose -f pwd.yml logs backend
docker compose -f pwd.yml logs scheduler
docker compose -f pwd.yml logs queue-long
```

---

## 20. Golden Rules for Production

✅ Only frontend is public
✅ Backend accessed via SSH + docker exec
✅ DB & Redis stay private
✅ Images always version-locked
✅ Offline `.tar` is source of truth

❌ Never expose DB
❌ Never run bench on host
❌ Never `docker pull` in production

---

## 21. What You Achieved

✔ Fully offline ERPNext deployment
✔ Reproducible Docker images
✔ Secure networking
✔ Production-grade workflow
✔ Zero dependency on internet

This is **enterprise-level deployment**, not a demo.

---

## 22. Next Steps (Optional)

* Automated backups
* HTTPS via reverse proxy
* Zero-downtime upgrades
* Multi-site hosting
* Monitoring & alerts

