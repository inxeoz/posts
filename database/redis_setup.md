---
title: Redis Setup
date: 2026-01-09
description: Redis troubleshooting for Frappe
permalink: posts/{{ title | slug }}/index.html
tags: [redis, frappe, troubleshooting]
---


# How to Fix Redis Connection Errors in Frappe / ERPNext

---

## 🔍 Understanding Redis in Frappe

Frappe uses **three Redis instances**, each serving a distinct purpose:

| Redis Role | Default Port | Purpose                                |
| ---------- | ------------ | -------------------------------------- |
| Cache      | 13000        | User settings, metadata, and cache     |
| Queue      | 11000        | Background jobs and async tasks        |
| SocketIO   | 12000        | Real-time event streaming (websockets) |

When any of these services are stopped or unreachable, Frappe throws connection errors during operations such as:

* App installations (e.g., HRMS, Healthcare)
* Background job execution
* Bench start/restart commands
* Login and session handling

---

## ⚠️ Common Error Example

Here’s what a typical Redis connection error looks like:

```
redis.exceptions.ConnectionError: Error 111 connecting to 127.0.0.1:13000. Connection refused.
```

This means the Frappe process tried to connect to Redis on `127.0.0.1` (localhost) but no Redis instance was listening on that port.

---

## 🧩 Step-by-Step Fix

### 1️⃣ Verify if Redis is Running

Run the following command to check if Redis is active:

```bash
ps aux | grep redis
```

If Redis isn’t listed, it’s not running. Depending on your environment, fix it using the appropriate method below.

---

## 🖥️ A. Fix Redis on a Local (Bare-Metal) Frappe Setup

### Step 1: Check Supervisor Status

Frappe uses **Supervisor** to manage Redis and other background services. Run:

```bash
sudo supervisorctl status
```

You should see something like:

```
frappe-bench-redis:redis-cache               RUNNING
frappe-bench-redis:redis-queue               RUNNING
frappe-bench-redis:redis-socketio            RUNNING
```

If any show `STOPPED` or `FATAL`, restart them:

```bash
sudo supervisorctl restart all
```

Or restart Redis individually:

```bash
sudo supervisorctl restart frappe-bench-redis:redis-cache
```

### Step 2: Restart the Bench

```bash
bench restart
```

This restarts all Frappe-related services, including Redis, workers, and SocketIO.

---

## 🐳 B. Fix Redis Inside Docker

In a **Dockerized Frappe setup**, Redis usually runs in separate containers. If you’re using a custom Docker environment and encounter connection errors, follow these steps.

### Step 1: Check if Redis Containers Exist

On the host machine:

```bash
docker ps | grep redis
```

If you don’t see any Redis containers (`redis-cache`, `redis-queue`, `redis-socketio`), create them manually.

### Step 2: Create Redis Containers

Run:

```bash
docker run -d \
  --name redis-cache \
  --network frappe-net \
  -p 13000:6379 \
  redis:6.2

docker run -d \
  --name redis-queue \
  --network frappe-net \
  -p 11000:6379 \
  redis:6.2

docker run -d \
  --name redis-socketio \
  --network frappe-net \
  -p 12000:6379 \
  redis:6.2
```

Make sure they appear when you run `docker ps`.

---

### Step 3: Update Frappe Configuration

Inside your app container (usually `frappe-python` or `makeit`), edit:

```bash
nano ~/frappe-bench/sites/common_site_config.json
```

Update the Redis settings:

```json
"redis_cache": "redis://redis-cache:6379",
"redis_queue": "redis://redis-queue:6379",
"redis_socketio": "redis://redis-socketio:6379",
```

Save and exit, then restart the bench:

```bash
bench restart
```

---

### Step 4: Verify Connectivity

From inside the container:

```bash
apt update && apt install redis-tools -y
redis-cli -h redis-cache ping
redis-cli -h redis-queue ping
redis-cli -h redis-socketio ping
```

Expected output:

```
PONG
```

If all three respond, Redis is working correctly.

---

## ⚙️ Optional: Check Redis Logs

You can inspect the Redis container logs for troubleshooting:

```bash
docker logs redis-cache
```

Or check Redis persistence and memory usage:

```bash
redis-cli -h redis-cache info memory
```

---

## 🚀 Final Step: Reinstall or Retry the App

Once Redis is back online and reachable, re-run your original command:

```bash
bench --site your_site_name install-app hrms
```

This should complete without any connection errors.

---

## 🧠 Pro Tips

* Always keep Redis containers on the **same Docker network** as Frappe and MariaDB.
* Avoid using `127.0.0.1` in Docker — use **container names** instead.
* Monitor Redis performance using:

  ```bash
  redis-cli -h redis-cache monitor
  ```
* If you’re using Docker Compose, you can define Redis services in your `docker-compose.yml` instead of running them manually.

---

## ✅ Summary

| Problem                                   | Cause                               | Solution                                                             |
| ----------------------------------------- | ----------------------------------- | -------------------------------------------------------------------- |
| `Error 111 connecting to 127.0.0.1:13000` | Redis not running or misconfigured  | Start Redis containers or services                                   |
| `Connection refused`                      | Wrong hostname in config            | Use container names (`redis-cache`, `redis-queue`, `redis-socketio`) |
| Redis processes missing                   | Supervisor not installed or running | Install and restart Supervisor                                       |
| Docker network issue                      | Containers not on same network      | Use `--network frappe-net` or Docker Compose                         |


