
---
title: SSH to Virtual Machine via Port Forwarding and Bridge Networking
date: 2026-01-13T17:58:05+05:30
description: Guide for connecting to virtual machines via SSH using port forwarding and bridge networking on Linux with KVM/QEMU
permalink: posts/{{ title | slug }}/index.html
tags: [ssh, vm, kvm, virtualization, linux, networking]
---

## Method 1: Port Forwarding (The "Workaround")

If your VM is behind NAT (IP addresses like `10.0.2.15`), use Port Forwarding. This maps a port on your host (e.g., 2222) to the SSH port (22) on your VM.

### 1. Enable SSH on the Guest

Inside your VM (e.g., Rocky Linux, Ubuntu), ensure the SSH server is active:

* **Install:** `sudo dnf install openssh-server` (Rocky/Fedora) or `sudo apt install openssh-server` (Ubuntu).
* **Start:** `sudo systemctl enable --now sshd`.
* **Firewall:** `sudo firewall-cmd --permanent --add-service=ssh && sudo firewall-cmd --reload`.

### 2. Map the Port via the Host

On an Arch Linux host using GNOME Boxes/KVM, run this command while the VM is running:

```bash
virsh -c qemu:///session qemu-monitor-command VM_NAME --pretty '{"execute": "human-monitor-command", "arguments": {"command-line": "hostfwd_add tcp::2222-:22"}}'

```

*(Replace `VM_NAME` with your actual VM name)*.

### 3. Connect

Open your host terminal and type:

```bash
ssh username@localhost -p 2222

```

---

## Method 2: Bridge Networking (The "Direct" Way)

Bridge networking makes the VM appear as a separate physical machine on your network, giving it a reachable IP address like `192.168.122.x`.

### 1. Set the Network Source

1. Open **Virtual Machine Manager**.
2. Navigate to the VM's **NIC** settings.
3. Change **Network source** to `Virtual network 'default' : NAT` or a specific bridge like `virbr0`.

### 2. Identify the IP

Inside the VM, run:

```bash
ip a

```

Look for the `inet` address (e.g., `192.168.122.50`).

### 3. Connect

From your host terminal:

```bash
ssh username@192.168.122.50

```

---

## Pro-Tip: Simplify with SSH Config

Instead of remembering ports and IP addresses, create an SSH alias.

1. On your host, edit `~/.ssh/config`:
```text
Host myvm
    HostName localhost
    User inxeoz
    Port 2222

```


2. Now, simply type: **`ssh myvm`**.

---
