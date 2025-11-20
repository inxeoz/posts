---
title: How To Restore
date: 2025-11-18
description: Complete Frappe database restoration guide
permalink: posts/{{ title | slug }}/index.html
tags: [frappe, database, restoration]
---

# How to Restore frappe_db_backup_utf8.sql

## Prerequisites
- Ubuntu/Debian system with Python 3.10+ and Node.js installed.
- MariaDB/MySQL installed and configured.
- Git installed.
- Access to sudo for system installations.

## Step 1: Install Frappe Bench
Install Frappe Bench (the development framework):
```bash
sudo apt update
sudo apt install python3-dev python3-pip python3-venv redis-server
pip3 install frappe-bench
```

## Step 2: Initialize Bench and Install Frappe
Create a new bench and install Frappe version 15.72.4:
```bash
bench init frappe-bench --frappe-branch version-15
cd frappe-bench
bench switch-to-branch version-15 frappe
bench update --patch
```

## Step 3: Install Required Apps
Install the specific app versions from the backup:

### ERPNext 15.67.0
```bash
bench get-app erpnext --branch version-15
bench switch-to-branch version-15 erpnext
```

### HRMS 15.47.5
```bash
bench get-app hrms --branch version-15
bench switch-to-branch version-15 hrms
```

### Healthcare 15.1.5
```bash
bench get-app healthcare --branch version-15
bench switch-to-branch version-15 healthcare
```

### Payments 0.0.1
```bash
bench get-app payments --branch version-15
```

### Non-Profit 0.0.1
```bash
bench get-app non_profit --branch develop
```

### Agriculture 0.0.1
```bash
bench get-app agriculture --branch develop
```

## Step 4: Create the Site
Create a new site with the same name as the backup:
```bash
bench new-site _5e5899d8398b5f7b
```

## Step 5: Install Apps on the Site
Install the apps on the site:
```bash
bench --site _5e5899d8398b5f7b install-app erpnext
bench --site _5e5899d8398b5f7b install-app hrms
bench --site _5e5899d8398b5f7b install-app healthcare
bench --site _5e5899d8398b5f7b install-app payments
bench --site _5e5899d8398b5f7b install-app non_profit
bench --site _5e5899d8398b5f7b install-app agriculture
```

## Step 6: Stop the Site (If Restoring Over Existing)
If restoring over an existing site, stop it first:
```bash
bench stop
```

## Step 7: Backup Current Database (Optional but Recommended)
Create a backup of the current database before restoration:
```bash
bench --site _5e5899d8398b5f7b backup
```

## Step 8: Restore the Database
Import the SQL dump file directly using bench:
```bash
bench --site _5e5899d8398b5f7b restore /path/to/frappe_db_backup_utf8.sql
```

Alternatively, manually via MySQL:
```bash
mysql -u [username] -p[password] _5e5899d8398b5f7b < /path/to/frappe_db_backup_utf8.sql
```

## Step 9: Restore File Attachments (If Applicable)
If you have a separate files backup (not included in this SQL dump), restore it:
```bash
cp -r /path/to/files_backup/* sites/_5e5899d8398b5f7b/public/files/
cp -r /path/to/private_files_backup/* sites/_5e5899d8398b5f7b/private/files/
```

## Step 10: Run Database Migrations
Update the database schema and run migrations:
```bash
bench --site _5e5899d8398b5f7b migrate
```

## Step 11: Clear Cache
Clear Frappe's cache:
```bash
bench --site _5e5899d8398b5f7b clear-cache
```

## Step 12: Start the Site
Start the Frappe site:
```bash
bench start
```

## Step 13: Verify Restoration
- Access the site at http://localhost:8000 or your configured URL.
- Check key data (users, companies, items, etc.).
- Run basic tests to ensure functionality.
- The backup includes 977 tables, with 301 containing data (file size: 22 MB, 43,539 lines).

## Troubleshooting
- **Version Mismatch**: Ensure all apps are installed with the correct versions as specified.
- **Permission Issues**: Ensure the MySQL user has sufficient privileges.
- **Import Errors**: Check MySQL error logs for specific issues.
- **Site Not Loading**: Run `bench doctor` to diagnose issues.


