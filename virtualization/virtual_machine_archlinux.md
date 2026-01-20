---
title: Virtual Machine Arch Linux
date: 2026-01-09
description: Complete Arch Linux KVM installation guide
permalink: posts/{{ title | slug }}/index.html
tags: [kvm, archlinux, virtualization]
---

# Quick prerequisites — check your hardware

Confirm your CPU supports hardware virtualization (Intel VT-x or AMD-V):

```bash
# prints nonzero if VT-x/AMD-V present
egrep -c '(vmx|svm)' /proc/cpuinfo
# or a human readable line
lscpu | grep -i Virtualization
```

If the first command prints `0`, enter your BIOS/UEFI and enable virtualization. KVM needs those CPU flags to use hardware acceleration. ([ArchWiki][1])

---

# 2) Install the packages (KVM/QEMU + libvirt + virt-manager)

Run:

```bash
sudo pacman -Syu
sudo pacman -S qemu libvirt virt-manager virt-viewer edk2-ovmf dnsmasq vde2 bridge-utils openbsd-netcat
```

* `qemu` — the VM userspace (with KVM acceleration).
* `libvirt` — daemon + management API.
* `virt-manager` — GUI to create/manage VMs (optional; you can use `virt-install` CLI).
* `virt-viewer` — simple console viewer.
* `edk2-ovmf` — UEFI firmware for VMs (UEFI/OVMF support).
* `dnsmasq`, `vde2`, `bridge-utils` — networking helpers commonly used with libvirt. ([ArchWiki][2])

(If you prefer a minimal set, `qemu libvirt virt-install` is enough for headless installs; `virt-manager` is optional for GUI.)

---

# 3) Enable and start libvirt (the daemon)

Enable + start the libvirt service so libvirt can manage VMs:

```bash
# enable and start libvirt
sudo systemctl enable --now libvirtd.service
# check status
systemctl status libvirtd.service
```

On some setups you may also enable the socket unit:

```bash
sudo systemctl enable --now libvirtd.socket
```

After this the libvirt daemon should be running and accepting connections. ([ArchWiki][3])

---

# 4) Give your user permission to use libvirt (run virt-manager as non-root)

Add yourself to the `libvirt` group (members get passwordless access to the libvirt socket):

```bash
sudo usermod -aG libvirt $USER
# also add to kvm so low-level device access is allowed
sudo usermod -aG kvm $USER
```

Then **log out and log back in** (or `newgrp libvirt`) so group changes take effect. Confirm with:

```bash
id $USER
```

ArchWiki recommends using the `libvirt` group and setting proper unix socket permissions if you want non-root use. ([ArchWiki][3])

---

# 5) (Optional) Configure the default storage/network pools

libvirt usually creates a default storage pool and NAT network. Check and start them:

```bash
# list storage pools
virsh pool-list --all

# if default pool is missing, create/use a folder:
sudo mkdir -p /var/lib/libvirt/images
sudo chown libvirt-qemu:libvirt /var/lib/libvirt/images
# create+start+autostart a dir pool (example)
sudo virsh pool-define-as defaultdir dir --target /var/lib/libvirt/images
sudo virsh pool-start defaultdir
sudo virsh pool-autostart defaultdir
```

Check networks:

```bash
virsh net-list --all
# start & autostart default network if needed
sudo virsh net-start default
sudo virsh net-autostart default
```

(You can also create a storage directory under your home and point libvirt to it via virt-manager if you prefer user-scoped storage.)

---

# 6) Create a VM — two easy ways

## A) GUI (virt-manager) — easiest for desktops

1. Launch `virt-manager` from your desktop menu or run `virt-manager`.
2. Click **Create a new virtual machine**.
3. Follow the wizard: choose ISO image (local or URL), OS type, memory / CPUs, create a disk image, select UEFI (OVMF) or BIOS, and finish.
4. Start the VM and use the console in virt-manager.

Virt-manager uses libvirt/qemu under the hood and provides an easy interface. ([ArchWiki][4])

## B) CLI (virt-install) — example (UEFI + 20 GB disk, 4GB RAM)

```bash
sudo virt-install \
  --name ubuntu-22.04 \
  --ram 4096 \
  --vcpus 2 \
  --disk path=/var/lib/libvirt/images/ubuntu-22.04.qcow2,size=20 \
  --os-variant ubuntu22.04 \
  --cdrom /path/to/ubuntu-22.04-desktop-amd64.iso \
  --network network=default \
  --graphics spice \
  --boot uefi
```

If you want to explicitly point QEMU to OVMF firmware files (on Arch they come from `edk2-ovmf`), paths typically live under `/usr/share/edk2-ovmf` or `/usr/share/edk2/x64` depending on package version — virt-manager can select them automatically. ([archlinux.org][5])

---

# 7) Starting/stopping and management quick commands

* Start/stop VMs: `virsh start <vmname>` / `virsh shutdown <vmname>`
* List VMs: `virsh list --all`
* Console: `virt-viewer <vmname>` or use virt-manager GUI.
* Convert disk images: `qemu-img convert -O qcow2 original.img new.qcow2`

---

# 8) Troubleshooting / common gotchas

* If `/dev/kvm` is missing: kernel KVM modules may not be loaded or BIOS virtualization disabled. Check `lsmod | grep kvm` and `dmesg`. ([ArchWiki][2])
* UEFI/OVMF firmware: ensure `edk2-ovmf` is installed. Some Arch users report occasional regressions after upstream OVMF updates — if a VM stops booting after a host upgrade, check Arch news/bug reports or try older OVMF. ([archlinux.org][5])
* If virt-manager complains about permissions, re-check group membership (`libvirt`) and socket settings in `/etc/libvirt/libvirtd.conf` (see ArchWiki). ([Medium][6])

---

# 9) (Optional) If you prefer VirtualBox instead

If you’d rather use VirtualBox (easier for some desktop users):

```bash
sudo pacman -S virtualbox virtualbox-host-dkms linux-headers
# or use virtualbox-host-modules-arch if using the stock Arch kernel
```

Then enable the systemd service that VirtualBox provides (if any), add your user to `vboxusers` group, and use the VirtualBox GUI. Note: VirtualBox and KVM/QEMU can conflict if they try to use the same low-level virtualization features — pick one primary hypervisor. (VirtualBox is fine for casual desktop use but KVM is higher performance for Linux hosts.)
