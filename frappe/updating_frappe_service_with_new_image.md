# 📘 How to Build, Ship, and Deploy a New Frappe Image with Updated Custom Apps (Without Affecting Existing Sites)

This guide explains how to **add or update custom apps (e.g. ERPNext)** in a Frappe Docker setup by:

* Building a new Docker image
* Exporting it as a tar archive
* Loading it on a server
* Restarting services safely (with scaling)
* Updating configuration correctly
  **without deleting volumes, sites, or databases**

This is the **recommended and supported approach** for production Frappe deployments.

---

## 🧠 Core Principle (Very Important)

> **Apps live in the Docker image**
> **Sites & data live in Docker volumes**

Because of this separation:

* You can safely change images
* Existing sites and databases remain untouched
* Apps can be installed on existing sites after restart

---

## 🏗️ PART 1 — Build a New Image with Updated Apps (Local Machine)

### 1️⃣ Define apps to include

Create or update `apps.json`:

```json
[
  {
    "url": "https://github.com/frappe/erpnext",
    "branch": "version-15"
  }
]
```

(Add any custom apps here as additional entries.)

---

### 2️⃣ Encode `apps.json` as Base64

```bash
export APPS_JSON_BASE64=$(base64 -w 0 apps.json)
```

Verify:

```bash
echo $APPS_JSON_BASE64
```

---

### 3️⃣ Build the new custom image

Use the **layered image** approach:

```bash
docker build \
  --build-arg=FRAPPE_PATH=https://github.com/frappe/frappe \
  --build-arg=FRAPPE_BRANCH=version-15 \
  --build-arg=APPS_JSON_BASE64=$APPS_JSON_BASE64 \
  --tag=customerp:15 \
  --file=images/layered/Containerfile .
```

✅ This image now contains:

* Frappe
* ERPNext
* Any custom apps you listed

---

### 4️⃣ Verify image contents (important)

```bash
docker run --rm customerp:15 ls apps
```

Expected output:

```
frappe
erpnext
```

If the app is not listed here, **do not proceed**.

---

## 📦 PART 2 — Export the Image for Server Deployment

Create a portable tar archive:

```bash
docker save -o frappe-images-erp.tar \
  customerp:15 \
  mariadb:11.8 \
  redis:6.2-alpine \
  traefik:v2.11
```

This tar file is **self-contained** and suitable for:

* Offline servers
* Air-gapped environments
* Disaster recovery

Copy it to the server:

```bash
scp frappe-images-erp.tar user@server:/path/to/frappe_docker/
```

---

## 🖥️ PART 3 — Load the Image on the Server

On the server:

```bash
docker load -i frappe-images-erp.tar
```

Verify:

```bash
docker image ls | grep customerp
```

---

## ⚙️ PART 4 — Update Configuration to Use the New Image

### 1️⃣ Edit `custom.env`

```bash
vi custom.env
```

Set:

```env
CUSTOM_IMAGE=customerp
CUSTOM_TAG=15
```

⚠️ Do **not** change:

* Volume names
* Database credentials
* Redis settings

---

### 2️⃣ Re-generate the composed file

```bash
docker compose --env-file custom.env -p frappe \
  -f compose.yaml \
  -f overrides/compose.mariadb.yaml \
  -f overrides/compose.redis.yaml \
  -f overrides/compose.noproxy.yaml \
  config > compose.custom.yaml
```

This ensures:

* Env changes are applied
* Image name is baked into the final compose file

---

## 🔻 PART 5 — Stop Services Safely

Stop all containers **without deleting volumes**:

```bash
docker compose -p frappe -f compose.custom.yaml down
```

Notes:

* This removes containers only
* Volumes (sites, DB, uploads) remain intact
* Scale information is reset (expected)

---

## 🔼 PART 6 — Start Services with Scaling Restored

If you previously ran multiple backend containers, you **must re-apply scaling**.

Example (2 backends):

```bash
docker compose -p frappe -f compose.custom.yaml up -d --scale backend=2
```

Verify:

```bash
docker compose -p frappe ps
```

Expected:

```
frappe-backend-1
frappe-backend-2
```

---

## 🧩 PART 7 — Install the New App on Existing Sites

Even though the app code exists in the image, it must be **installed per site**.

### 1️⃣ Enter a backend container

```bash
docker compose -p frappe exec backend bash
```

---

### 2️⃣ List sites

```bash
ls sites
```

Example:

```
site1.local
site2.local
common_site_config.json
```

---

### 3️⃣ Install app on each site

```bash
bench --site site1.local install-app erpnext
```

Repeat for all required sites.

This:

* Runs database migrations
* Applies patches
* Registers doctypes

---

### 4️⃣ Enable scheduler (required for ERPNext)

```bash
bench --site site1.local set-config enable_scheduler 1
bench restart
```

---

## 🌐 PART 8 — Access Verification

Depending on your setup:

* Use site name as hostname **OR**
* Set `FRAPPE_SITE_NAME_HEADER` in `custom.env`

Example:

```env
FRAPPE_SITE_NAME_HEADER=site1.local
```

Restart if changed:

```bash
docker compose up -d
```

---

## ❌ What NOT to Do (Critical Warnings)

| Action                                    | Why                     |
| ----------------------------------------- | ----------------------- |
| Delete Docker volumes                     | Data loss               |
| Run `bench get-app` in production         | Breaks immutability     |
| Modify containers manually                | Changes lost on restart |
| Mix image names (`custom` vs `customerp`) | App not found errors    |
| Skip `install-app`                        | ERPNext won’t work      |

---

## ✅ Final Checklist

| Item                       | Status |
| -------------------------- | ------ |
| New image built with apps  | ✅      |
| Image verified (`ls apps`) | ✅      |
| Image loaded on server     | ✅      |
| `custom.env` updated       | ✅      |
| Compose regenerated        | ✅      |
| Services restarted         | ✅      |
| Scaling restored           | ✅      |
| App installed on site      | ✅      |
| Scheduler enabled          | ✅      |

---

## 🧭 Summary

This workflow:

* Preserves **all existing sites**
* Preserves **databases and uploads**
* Allows **safe app upgrades**
* Is fully reproducible
* Works offline
* Matches Frappe Docker best practices

This is the **correct way** to manage apps in production Frappe environments.

