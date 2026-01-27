---
title: Docker Network
date: '2026-01-27'
description: Docker networking fundamentals
permalink: posts/{{ title | slug }}/index.html
tags:
- docker
- networking
categories:
- docker
---

# How to Create and Manage Docker Networks

---

## 🔹 What Is a Docker Network?

A **Docker network** is a virtual layer that connects containers. By default, Docker provides some basic network types:

| Network Type | Description                                                                                              |
| ------------ | -------------------------------------------------------------------------------------------------------- |
| **bridge**   | Default network for standalone containers. Containers can talk to each other by name on the same bridge. |
| **host**     | Shares the host machine’s network directly (no isolation).                                               |
| **none**     | Disables networking for the container.                                                                   |
| **overlay**  | Enables communication between containers across multiple Docker hosts (used in Swarm mode).              |
| **macvlan**  | Assigns a MAC address to containers, making them appear as physical devices on your LAN.                 |

---

## ⚙️ Step 1: Check Existing Docker Networks

Before creating one, you can see what’s already available:

```bash
docker network ls
```

Example output:

```
NETWORK ID     NAME          DRIVER    SCOPE
a1b2c3d4e5f6   bridge        bridge    local
b2c3d4e5f6a7   host          host      local
c3d4e5f6a7b8   none          null      local
```

---

## ⚙️ Step 2: Create a Custom Network

You can create your own bridge network using the `docker network create` command.

### **Linux or macOS**

```bash
docker network create frappe-net
```

### **Windows (PowerShell or CMD)**

Same command works:

```powershell
docker network create frappe-net
```

Output:

```
c9a2f3b8a7e9f48b1c3d0a57a9832d6c8e3d0b23b7b5f6a0d2a3f4c5a6e7b8c9
```

This creates a new **user-defined bridge network** named `frappe-net`.

---

## ⚙️ Step 3: Connect Containers to the Network

When you run a container, you can attach it to your network using `--network`.

Example:

```bash
docker run -d --name mariadb --network frappe-net -e MYSQL_ROOT_PASSWORD=frappe mariadb:10.6
```

Then run another container on the same network:

```bash
docker run -d --name frappe --network frappe-net -p 8080:8000 frappe/erpnext
```

Now, the `frappe` container can access the database container simply by its **container name** (`mariadb`) — no need for IP addresses.

---

## ⚙️ Step 4: Inspect a Docker Network

You can view detailed information (like connected containers, IP ranges, etc.) using:

```bash
docker network inspect frappe-net
```

Example output (simplified):

```json
[
  {
    "Name": "frappe-net",
    "Driver": "bridge",
    "Containers": {
      "f1e2d3c4b5a6": {
        "Name": "mariadb",
        "IPv4Address": "172.18.0.2/16"
      },
      "a7b8c9d0e1f2": {
        "Name": "frappe",
        "IPv4Address": "172.18.0.3/16"
      }
    }
  }
]
```

---

## ⚙️ Step 5: Disconnect and Reconnect Containers

To disconnect a container from a network:

```bash
docker network disconnect frappe-net mariadb
```

To reconnect it:

```bash
docker network connect frappe-net mariadb
```

---

## ⚙️ Step 6: Remove Unused Networks

To remove a specific network:

```bash
docker network rm frappe-net
```

To prune (remove all unused networks):

```bash
docker network prune
```

*(You’ll be asked for confirmation.)*

---

## 🧠 Tips for Managing Docker Networks

* ✅ Use **named networks** (like `frappe-net`) for multi-container apps.
* ✅ Avoid exposing ports publicly when containers can talk over an internal network.
* ✅ Combine networks with **Docker Compose** for easier configuration.
* ✅ Always **inspect** your networks to debug connection issues.

---

## ⚙️ Optional: Use Docker Compose for Networks

Here’s a quick example of defining a custom network in `docker-compose.yml`:

```yaml
version: "3.9"

services:
  mariadb:
    image: mariadb:10.6
    environment:
      MYSQL_ROOT_PASSWORD: frappe
      MYSQL_USER: frappe
      MYSQL_PASSWORD: frappe
      MYSQL_DATABASE: frappe
    volumes:
      - mariadb_data:/var/lib/mysql
    networks:
      - frappe-net

  frappe:
    image: frappe/erpnext
    ports:
      - "8080:8000"
    networks:
      - frappe-net

volumes:
  mariadb_data:

networks:
  frappe-net:
    driver: bridge
```

Then run:

```bash
docker-compose up -d
```

This automatically creates and manages your custom `frappe-net` network.

---

## 🧩 Summary

| Task                 | Command                                        |
| -------------------- | ---------------------------------------------- |
| List networks        | `docker network ls`                            |
| Create network       | `docker network create <name>`                 |
| Inspect network      | `docker network inspect <name>`                |
| Connect container    | `docker network connect <name> <container>`    |
| Disconnect container | `docker network disconnect <name> <container>` |
| Remove network       | `docker network rm <name>`                     |
| Remove unused        | `docker network prune`                         |

---

#

---
