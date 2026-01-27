# 🧾 **Working with KVM Virtual Machines and Creating Networks (NAT, Isolated, Bridged) + Hosting a Local Repository Server**

KVM (Kernel-based Virtual Machine) combined with `libvirt` and `virt-manager` provides a powerful and flexible virtualization platform for Linux users. One of the most important aspects of virtualization is **networking** — giving VMs internet, isolating them, or letting them behave like physical machines on your LAN.

This article explains:

* How KVM networking works
* How to create different network types
* How to connect VMs to them
* How to host a local repository server and register VMs with it

---

# **1. Understanding KVM/libvirt Networking**

KVM uses **libvirt** to create and manage software-defined networks. These show up as virtual bridges (e.g., `virbr0`, `virbr1`, `virbr3`).

There are **three primary network types**:

### **1. NAT Network (Default Mode)**

* VM gets internet access
* VM can access host
* But host **cannot** connect to VM directly
* VM sits behind NAT like a home router

Bridge: `virbr0`
Good for: **General-purpose VMs**

---

### **2. Isolated Network**

* No internet
* Only communication **within the isolated network**
* VM can access host, host can access VM
* Offline labs, secure internal networks

Good for: **Offline repositories, training labs, secure testing**

---

### **3. Bridged Network (Direct LAN Access)**

* VM behaves like a physical machine on the LAN
* Gets IP from your WiFi/router
* Other LAN devices can reach VM

Good for: **Servers, shared environments**

---

# **2. Creating Networks in libvirt**

Networks are defined using XML files and created with `virsh`.

---

## **A. Creating a NAT Network with Internet Access**

Create NAT network named `natnet`:

```bash
cat <<EOF | sudo tee /tmp/natnet.xml
<network>
  <name>natnet</name>
  <forward mode='nat'/>
  <bridge name='virbr10' stp='off' delay='0'/>
  <ip address='192.168.250.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='192.168.250.100' end='192.168.250.200'/>
    </dhcp>
  </ip>
</network>
EOF
```

Load & activate:

```bash
sudo virsh net-define /tmp/natnet.xml
sudo virsh net-start natnet
sudo virsh net-autostart natnet
```

Check:

```bash
sudo virsh net-list --all
```

---

## **B. Creating an Isolated Network**

```bash
cat <<EOF | sudo tee /tmp/isolated.xml
<network>
  <name>isolatedlab</name>
  <bridge name='virbr20'/>
  <ip address='192.168.200.1' netmask='255.255.255.0'>
    <dhcp>
      <range start='192.168.200.100' end='192.168.200.200'/>
    </dhcp>
  </ip>
</network>
EOF
```

Enable:

```bash
sudo virsh net-define /tmp/isolated.xml
sudo virsh net-start isolatedlab
sudo virsh net-autostart isolatedlab
```

---

## **C. Creating a Bridged Network (LAN VM IP)**

> Note: Bridging over WiFi sometimes requires macvtap instead of a true bridge.

Example bridged XML:

```bash
cat <<EOF | sudo tee /tmp/br0.xml
<network>
  <name>hostbridge</name>
  <forward mode='bridge'/>
  <bridge name='br0'/>
</network>
EOF
```

Enable:

```bash
sudo virsh net-define /tmp/br0.xml
sudo virsh net-start hostbridge
sudo virsh net-autostart hostbridge
```

---

# **3. Assigning Networks to VMs (virt-manager)**

Open **virt-manager → VM → Shut Down → NIC → Network source**:

✔ NAT → **natnet**
✔ Isolated → **isolatedlab**
✔ Bridged → **hostbridge**

Select **Device model: virtio** for best performance.

Start VM, get DHCP:

```bash
sudo dhclient enp1s0
```

---

# **4. Hosting a Local Offline Repository Server**

Many enterprise labs require **offline YUM/DNF repositories**. You can host one on the **host** using Apache.

---

## **A. Install Apache**

```bash
sudo dnf install -y httpd
sudo systemctl enable --now httpd
```

---

## **B. Create a repo directory and extract ISO**

Mount RHEL ISO:

```bash
sudo mkdir /mnt/rheliso
sudo mount -o loop RHEL8.iso /mnt/rheliso
```

Copy content to web directory:

```bash
sudo mkdir -p /var/www/html/rhel8
sudo cp -r /mnt/rheliso/* /var/www/html/rhel8/
sudo restorecon -Rv /var/www/html
```

Test:

```
curl http://localhost/rhel8/
```

---

# **5. Making the Repo Reachable from VMs**

If VM is on NAT network `natnet`:

Host IP = `192.168.250.1`
VM IP = something like `192.168.250.100`

Inside VM test connectivity:

```bash
ping 192.168.250.1
curl http://192.168.250.1/rhel8/
```

It should show the directory listing.

---

# **6. Creating a Local YUM Repository File**

Inside VM:

```bash
sudo tee /etc/yum.repos.d/rhel8-local.repo <<EOF
[BaseOS]
name=RHEL 8 BaseOS Local
baseurl=http://192.168.250.1/rhel8/BaseOS
enabled=1
gpgcheck=0

[AppStream]
name=RHEL 8 AppStream Local
baseurl=http://192.168.250.1/rhel8/AppStream
enabled=1
gpgcheck=0
EOF
```

Save → Clean cache:

```bash
sudo dnf clean all
sudo dnf makecache
```

Now you can install packages **offline** from your host server:

```bash
sudo dnf install httpd
sudo dnf install tmux
```

---

# **7. Summary**

### ✔ NAT network

VM gets internet, can reach host repo.

### ✔ Isolated network

VM cannot reach internet, good for labs.

### ✔ Bridged network

VM gets IP on LAN like physical machine.

### ✔ Apache repo server

Host serves `/var/www/html/rhel8/` → VM uses it as offline repo.

### ✔ VM registers to repo using `.repo` file

---


