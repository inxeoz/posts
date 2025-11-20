---
title: Setup Frappe Containers
date: 2025-11-18
description: Docker commands for Frappe setup
permalink: posts/{{ title | slug }}/index.html
tags: [docker, frappe, setup]
---

docker run -d
--name mariadb
--network frappe-net
-e MYSQL_ROOT_PASSWORD=frappe
-e MYSQL_USER=frappe
-e MYSQL_PASSWORD=frappe
-e MYSQL_DATABASE=frappe
-v mariadb_data:/var/lib/mysql
-p 3307:3306
mariadb:10.6


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
