# 🐳 Run RHEL 9 in Docker (Offline-Friendly)  
  
**Goal:** Use RHEL 9 in Docker, save packages to your computer, and install them offline.  
  
---  
  
## 📦 Step 1: Create a Shared Folder  
This folder will store your RPM packages (works on both Docker and your computer):  
  
```bash  
sudo mkdir -p /srv/rhel-data  
sudo chmod 777 /srv/rhel-data  # Gives full access to Docker  
```  
  
---  
  
## 🐳 Step 2: Start RHEL 9 Container  
```bash  
docker run -d \  
  --name rhel9 \  
  -v /srv/rhel-data:/data \  # Connects host folder to container  
  registry.access.redhat.com/ubi9/ubi \  
  sleep infinity  # Keeps container running  
```  
  
**Why?** Containers stop when their main command finishes. `sleep infinity` keeps it alive.  
  
---  
  
## 🔑 Step 3: Get Inside the Container  
```bash  
docker exec -it rhel9 /bin/bash  
```  
  
You're now in the RHEL 9 environment!  
  
---  
  
## 📦 Step 4: Install Package Tools  
```bash  
# Install package manager tools  
dnf install -y dnf-plugins-core  
  
# Optional: Install 'clear' command (to clear the screen)  
dnf install -y ncurses  
```  
  
---  
  
## 📥 Step 5: Download RPMs (Online)  
**Option 1: Single Package**  
```bash  
dnf download --destdir=/data httpd  # Saves to /data folder  
```  
  
**Option 2: Package + Dependencies**  
```bash  
dnf download --resolve --destdir=/data httpd  # Gets all required packages  
```  
  
**Where are the RPMs?**  
- **Inside container:** `/data`  
- **On your computer:** `/srv/rhel-data`  
  
---  
  
## ⚠️ Normal Warning (Ignore Safely)  
You'll see:  
```  
This system is not registered with an entitlement server  
```  
This is normal for UBI images. No action needed!  
  
---  
  
## 🔧 Step 6: Install RPMs Offline  
**Method 1: Install All RPMs in Folder**  
```bash  
dnf install /data/*.rpm  
```  
  
**Method 2: Create a Local Repository (Recommended)**  
1. Generate repo metadata:  
   ```bash  
   dnf install -y createrepo_c  
   createrepo /data  
   ```  
2. Create repo config file (`/etc/yum.repos.d/local.repo`):  
   ```ini  
   [local]  
   name=Local Packages  
   baseurl=file:///data  
   enabled=1  
   gpgcheck=0  
   ```  
3. Install packages:  
   ```bash  
   dnf clean all  
   dnf install httpd  # Now uses your local repo!  
   ```  
  
---  
  
## ✅ Verify It Worked  
```bash  
httpd -v  # Should show version info  
```  
  
---  
  
## 🛑 Stop/Start Container  
```bash  
docker stop rhel9   # Stop when done  
docker start rhel9  # Restart later  
```  
  
---  
 
