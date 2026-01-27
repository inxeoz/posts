---
title: "\U0001F4D8 Complete Guide: Full Backup & Restore in Frappe / ERPNext (Production-Ready)"
date: '2026-01-23'
description: 'This article explains:'
permalink: posts/{{ title | slug }}/index.html
tags:
- automation
- backup
- bash
- database
- json
- rest
- restore
- script
categories:
- frappe
---



---
title: Complete Guide Full Backup & Restore in Frappe ERPNext
date: 2026-01-21
description: Production-ready backup and restore strategies for Frappe and ERPNext with best practices
permalink: posts/{{ title | slug }}/index.html
tags: [frappe, erpnext, backup, restore, database, production]
categories: ['frappe']
---

# 📘 Complete Guide: Full Backup & Restore in Frappe / ERPNext (Production-Ready)

This article explains:

* ✅ What a **full backup** really means in Frappe
* ✅ Which backups are **mandatory vs optional**
* ✅ How to **restore safely** (same site or new site)
* ⚠️ Common mistakes & production caveats
* 🧠 Best practices used in real production systems

---

## 1️⃣ What “Full Backup” Means in Frappe

A **true full backup** in Frappe consists of **site-level data**, not the entire bench by default.

### 🔹 Mandatory (Frappe-supported restore)

These are **required** for a complete site restore:

1. **Database**
2. **Public files**
3. **Private files**
4. **Site configuration**

### 🔹 Optional (Infrastructure / disaster recovery)

These are **not required** for restoring a site, but useful in some cases:

* Apps source code
* Bench config
* Logs
* Virtualenv

> ⚠️ Frappe’s official restore mechanism only understands **site-level backups**.

---

## 2️⃣ Mandatory Backup (Production – Recommended)

### ✅ Command: Full Site Backup (MUST DO)

```bash
bench --site yoursite.localhost backup --with-files
```

### 📂 What this creates

Location:

```
sites/yoursite.localhost/private/backups/
```

Files created:

| File                        | Purpose                                    |
| --------------------------- | ------------------------------------------ |
| `*-database.sql.gz`         | All data (DocTypes, users, transactions)   |
| `*-public-files.tar`        | Public attachments, images, website assets |
| `*-private-files.tar`       | Private files, reports, exports            |
| `*-site_config_backup.json` | DB creds, encryption keys                  |

👉 **This alone is sufficient to restore a site fully.**

---

## 3️⃣ Optional Backup (Bench / Disaster Snapshot)

### ⚠️ Optional – NOT required for normal restore

This is useful if:

* You want a **full server snapshot**
* You can’t reinstall apps easily
* You want rollback protection

### Optional command:

```bash
tar -czf frappe-bench-full-$(date +%F).tar.gz frappe-bench
```

✔ Includes apps
✔ Includes configs
✔ Includes everything

❌ Not used by `bench restore`

---

## 4️⃣ What You Should Back Up in Production (Summary)

| Item          | Mandatory | Why                    |
| ------------- | --------- | ---------------------- |
| Database      | ✅         | Core data              |
| Public files  | ✅         | Images, attachments    |
| Private files | ✅         | Confidential data      |
| Site config   | ✅         | Encryption & DB access |
| Apps code     | ❌         | Can be reinstalled     |
| Bench config  | ❌         | Re-creatable           |
| Logs          | ❌         | Not data               |

---

## 5️⃣ How to Restore a Site (Same Server / Same Name)

### ⚠️ Before restore

* Always restore from **bench root**
* App versions **must match or be newer**
* Restore must be **uninterrupted**

---

### Step 1: Drop existing site (if exists)

```bash
bench drop-site yoursite.localhost
```

---

### Step 2: Create empty site

```bash
bench new-site yoursite.localhost
```

---

### Step 3: Install required apps (IMPORTANT)

Example:

```bash
bench --site yoursite.localhost install-app erpnext
```

Install **all apps** that existed at backup time.

---

### Step 4: Restore database + files

```bash
bench --site yoursite.localhost restore \
  sites/yoursite.localhost/private/backups/xxxx-database.sql.gz \
  --with-public-files sites/yoursite.localhost/private/backups/xxxx-public-files.tar \
  --with-private-files sites/yoursite.localhost/private/backups/xxxx-private-files.tar
```

---

### Step 5: Migrate (MANDATORY)

```bash
bench --site yoursite.localhost migrate
bench restart
```

---

## 6️⃣ Restore Into a NEW Site (Cloning / Staging)

This is **fully supported**.

### Example: Restore `prod.localhost` → `staging.localhost`

```bash
bench new-site staging.localhost
bench --site staging.localhost install-app erpnext

bench --site staging.localhost restore \
  sites/prod.localhost/private/backups/xxxx-database.sql.gz \
  --with-public-files sites/prod.localhost/private/backups/xxxx-public-files.tar \
  --with-private-files sites/prod.localhost/private/backups/xxxx-private-files.tar
```

Then:

```bash
bench --site staging.localhost migrate
bench restart
```

---

## 7️⃣ What Is OPTIONAL During Restore?

| Item           | Optional | When                    |
| -------------- | -------- | ----------------------- |
| Public files   | ⚠️       | If you don’t have them  |
| Private files  | ⚠️       | If data is DB-only      |
| Bench snapshot | ❌        | Not used by restore     |
| Same site name | ❌        | Can restore to new site |

> ⚠️ If you don’t have a `public-files.tar`, **do not pass the flag**.

---

## 8️⃣ Common Production Caveats (VERY IMPORTANT)

### ❌ 1. Version mismatch

> Backup version **must be ≤ code version**

✔ Newer code restoring older backup → OK
❌ Older code restoring newer backup → risky

Always run:

```bash
bench migrate
```

---

### ❌ 2. Missing custom apps

Error:

```
ModuleNotFoundError: No module named 'customapp'
```

Fix:

* Install the app **OR**
* Recreate it with `bench new-app`

---

### ❌ 3. Interrupting restore (Ctrl+C)

This causes:

* Half-created DB
* Broken schema
* Scheduler errors

**Rule:**
👉 If restore fails → `bench drop-site` and retry cleanly

---

### ❌ 4. Running bench from wrong directory

Always run from:

```
frappe-bench/
```

Not from:

```
sites/
```

---

## 9️⃣ Production Best Practices (Battle-Tested)

### ✅ Always do this

* Backup **before migrate / update**
* Store backups **off-server**
* Test restore **once**
* Use `--with-files`

---

### ✅ Recommended automation

```bash
bench enable-scheduler
```

And sync:

```
sites/*/private/backups/
```

to:

* S3 / Wasabi
* rsync server
* Encrypted storage

---

## 🔐 Final Recommendation

After any successful restore or upgrade:

```bash
bench --site yoursite.localhost backup --with-files
```

This ensures your **next restore is painless**.

---

## 🧠 TL;DR

* **Mandatory backup** = site backup with files
* **Bench snapshot** = optional
* **Restore requires apps installed**
* **Never interrupt restore**
* **Always migrate**
* **Always test once**

