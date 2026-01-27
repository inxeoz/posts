---
title: Fix Redis In Common Site
date: '2026-01-27'
description: Redis configuration for Frappe
permalink: posts/{{ title | slug }}/index.html
tags:
- redis
- frappe
- configuration
categories:
- database
---

"redis_cache": "redis://redis-cache:6379",
"redis_queue": "redis://redis-queue:6379",
"redis_socketio": "redis://redis-socketio:6379",
