---
title: Fixing ERPNext / Frappe Error
date: '2026-01-23'
description: '* **OS**: RHEL (private / offline)'
permalink: posts/{{ title | slug }}/index.html
tags:
- bash
- database
- docker
- json
- mysql
- networking
- rest
- script
- ssh
categories:
- frappe
---



---
title: Fixing ERPNext Frappe Database Access Denied Error
date: 2026-01-21
description: Troubleshooting and fixing pymysql operational access denied errors in Frappe ERPNext
permalink: posts/{{ title | slug }}/index.html
tags: [frappe, erpnext, database, troubleshooting, mysql]
categories: ['frappe']
---

# Fixing ERPNext / Frappe Error

## `pymysql.err.OperationalError: (1045) Access denied for user`

### Environment

* **OS**: RHEL (private / offline)
* **Deployment**: Docker Compose
* **Stack**: Frappe + ERPNext + MariaDB
* **Setup**: Multi-site (`s1`, `s2`, `s3`) with **separate MariaDB containers**
* **Access**: SSH only (production)

---

## 🔴 The Problem

While installing ERPNext on a new site:

```bash
bench --site s3.inxeoz.com install-app erpnext
```

The installation failed with:

```text
pymysql.err.OperationalError: (1045,
"Access denied for user 's3_db'@'172.21.0.9' (using password: YES)")
```

ERPNext could not connect to the database.

---

## 🟡 Impact Analysis

* ❌ ERPNext installation blocked
* ❌ Only **one site (`s3`) affected**
* ✅ Other sites (`s1`, `s2`) working
* ✅ No data loss
* ✅ No service outage

This is a **database authentication issue**, not an ERPNext bug.

---

## 🧠 Root Cause (Important)

MariaDB user `s3_db` existed, but it was **bound to a single Docker IP**:

```text
's3_db'@'172.21.0.8'
```

Meanwhile, the Frappe backend container connected from:

```text
172.21.0.9
```

Docker assigns IPs dynamically.
MariaDB treats each IP as a **different host**.

➡️ Result: **Access denied**, even with the correct password.

---

## 🔍 Verification Steps (Read-Only, Safe)

### 1️⃣ Check site database configuration

Inside backend container:

```bash
cat sites/s3.inxeoz.com/site_config.json
```

Example output:

```json
{
  "db_host": "mariadb-s3",
  "db_name": "s3_db",
  "db_password": "hsWcj7II1yEoSqZC",
  "db_type": "mariadb"
}
```

---

### 2️⃣ Identify the correct MariaDB container

On the host:

```bash
docker ps
```

Relevant output:

```text
mariadb-s3   mariadb:11.8   Up
```

⚠️ **Container name matters**
`mariadb-s3` ≠ `mariadb_s3`

---

## 🛠️ Safe Fix (No Restarts, No Data Loss)

### ⚠️ Preconditions

* You are on the Docker host
* You know the **MariaDB root password**
* You do **not** restart containers

---

### 3️⃣ Enter the MariaDB container

```bash
docker exec -it mariadb-s3 mariadb -u root -p
```

---

### 4️⃣ Inspect the existing user (read-only)

```sql
SELECT Host, User FROM mysql.user WHERE User='s3_db';
```

Output:

```text
+------------+-------+
| Host       | User  |
+------------+-------+
| 172.21.0.8 | s3_db |
+------------+-------+
```

✅ Confirms the problem: user restricted to one IP.

---

### 5️⃣ Create a wildcard user (correct approach)

```sql
CREATE USER 's3_db'@'%' IDENTIFIED BY 'hsWcj7II1yEoSqZC';
```

Why `%`?

* Docker IPs change
* Containers must connect from **any host**

---

### 6️⃣ Grant database privileges

```sql
GRANT ALL PRIVILEGES ON s3_db.* TO 's3_db'@'%';
FLUSH PRIVILEGES;
```

---

### 7️⃣ (Optional) Remove the IP-locked user

This prevents future confusion.

```sql
DROP USER 's3_db'@'172.21.0.8';
FLUSH PRIVILEGES;
```

⚠️ Safe **only because `%` user already exists**

---

## ✅ Mandatory Verification (Do NOT Skip)

Exit MariaDB:

```sql
EXIT;
```

Test login **exactly like Frappe does**:

```bash
docker exec -it mariadb-s3 mariadb -u s3_db -p s3_db
```

Expected result:

```text
MariaDB [s3_db]>
```

If this fails → stop and fix DB first.

---

## 🚀 Final Step: Install ERPNext

Enter backend container:

```bash
docker compose -p frappe exec backend bash
```

Run:

```bash
bench --site s3.inxeoz.com install-app erpnext
```

This should now complete successfully.

---

## ✅ Post-Install Verification

```bash
bench --site s3.inxeoz.com list-apps
```

Expected:

```text
frappe
erpnext
```

---

## ❌ What NOT To Do (Production Rules)

* ❌ Do NOT bind DB users to Docker IPs
* ❌ Do NOT use `'user'@'localhost'`
* ❌ Do NOT delete databases
* ❌ Do NOT recreate the site
* ❌ Do NOT restart MariaDB or Docker
* ❌ Do NOT guess passwords

---

## 🧠 Key Lessons (Critical)

### ✅ Correct pattern for Docker + Frappe

```sql
'user'@'%'
```

### ❌ Incorrect patterns

```sql
'user'@'172.21.x.x'
'user'@'localhost'
```

Docker networking **is not stable**.
MariaDB authentication **must be flexible**.

---

## 📌 Quick Checklist for Future Sites

Before installing apps:

* [ ] `site_config.json` exists
* [ ] MariaDB container running
* [ ] DB user exists as `'user'@'%'`
* [ ] Manual DB login test passes
* [ ] No container restarts done

If all are true → ERPNext will install.

