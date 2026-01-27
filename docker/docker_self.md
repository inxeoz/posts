---
title: Docker Self
date: '2026-01-27'
description: Advanced Docker system management
permalink: posts/{{ title | slug }}/index.html
tags:
- docker
- system
- management
categories:
- docker
---

# Mastering Docker: Building, Managing, and Maintaining Your Own Systems

---

## 🚀 1. Understanding Docker Basics

Before diving into management, let’s recap what Docker is built around:

| Concept       | Description                                             |
| ------------- | ------------------------------------------------------- |
| **Image**     | A read-only template (like an OS snapshot).             |
| **Container** | A running instance of an image — like a lightweight VM. |
| **Volume**    | Persistent storage shared between host and container.   |
| **Network**   | Virtual bridges for communication between containers.   |

---

## 🧩 2. Creating Your Own System (Container)

To start an Ubuntu-based system:

```bash
docker run -it --name myubuntu ubuntu:22.04 bash
```

### What this does:

* `-it`: Interactive terminal mode
* `--name myubuntu`: Gives your container a friendly name
* `ubuntu:22.04`: Uses the official Ubuntu image
* `bash`: Starts a shell inside it

Inside, you can use `apt install`, create files, and modify configurations — just like a real Linux system.

Example:

```bash
apt update && apt install nano curl
echo "Hello Docker!" > /root/test.txt
```

---

## 💾 3. Keeping Your Container Persistent

By default, when you `exit`, the container stops — but doesn’t vanish.

To reopen the same environment:

```bash
docker start -ai myubuntu
```

That command:

* **Starts** the container (`start`)
* **Attaches** you to it (`-ai`)

You’ll find all your files and configurations just as you left them.

To view *all* containers (even stopped ones):

```bash
docker ps -a
```

---

## 🧱 4. Saving Your Custom System as a New Image

Once you’ve customized your container, you can **snapshot** it into a new image:

```bash
docker commit myubuntu myubuntu:stable
```

Now you can spin up new containers based on your saved configuration:

```bash
docker run -it myubuntu:stable bash
```

It’s your personal system image — preinstalled with everything you need.

---

## 📁 5. Using Volumes for Data Persistence

If you want your data to live *outside* the container (so it survives even if the container is deleted):

```bash
docker run -it -v ~/dockerdata:/root --name myubuntu ubuntu:22.04 bash
```

This command mounts your host folder `~/dockerdata` into the container’s `/root` directory.

Now anything you save in `/root` is also available on your host system.

---

## 🔄 6. Managing Containers Efficiently

Here are your key Docker management commands:

| Task                          | Command                       |
| ----------------------------- | ----------------------------- |
| List running containers       | `docker ps`                   |
| List all containers           | `docker ps -a`                |
| Stop a container              | `docker stop <name>`          |
| Start a container             | `docker start <name>`         |
| Remove a container            | `docker rm <name>`            |
| Remove all stopped containers | `docker container prune`      |
| View logs                     | `docker logs <name>`          |
| Enter a running container     | `docker exec -it <name> bash` |

---

## 🧠 7. Pro Tip: Create a Reusable Alias

You can create a shortcut for your personal Docker VM. Add this line to your `.bashrc` or `.zshrc`:

```bash
alias ubuntuvm='docker start -ai myubuntu || docker run -it --name myubuntu ubuntu:22.04 bash'
```

Then just type:

```bash
ubuntuvm
```

and Docker will:

* Reopen your saved container if it exists, or
* Create it if it doesn’t.

Instant Linux sandbox — every time.

---

## 🧹 8. Cleaning and Maintenance

Over time, unused images and stopped containers can fill up space. Clean them up safely:

```bash
# Remove stopped containers
docker container prune

# Remove unused images
docker image prune

# Remove unused volumes
docker volume prune
```

Or do it all in one go:

```bash
docker system prune -a
```

*(Warning: this removes everything not currently running!)*

---

## ⚙️ 9. Advanced: Docker Compose for Multi-Service Systems

If you want to run multiple services (like a web app + database + cache), use **Docker Compose**.

Example `docker-compose.yml`:

```yaml
version: "3"
services:
  web:
    image: nginx:latest
    ports:
      - "8080:80"
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: secret
```

Then run:

```bash
docker compose up -d
```

You now have a complete multi-container system — manageable with a single command.

---

## 🧰 10. Backups and Version Control

You can **export and import** containers or images:

```bash
# Export container to a tar file
docker export myubuntu > myubuntu.tar

# Import it later
cat myubuntu.tar | docker import - myubuntu:backup
```

This makes your system fully portable — share it, back it up, or migrate to another machine.

---



---
