

# How to Install Frappe Bench on Arch Linux

# 📦 1. Install System Dependencies

Begin with a full system update:

```bash
sudo pacman -Syu
```

Install all necessary packages:

```bash
sudo pacman -S \
    git python python-pip python-virtualenv \
    mariadb valkey \
    nodejs npm yarn \
    imagemagick wkhtmltopdf \
    cronie \
    base-devel gcc cmake make
```



```bash
sudo systemctl enable --now cronie
```

------

# 🗄️ 2. Configure MariaDB

Install MariaDB (if not already installed):

```bash
sudo pacman -S mariadb
```

Initialize the database files:

```bash
sudo mariadb-install-db --user=mysql --basedir=/usr --datadir=/var/lib/mysql
```

Start and enable MariaDB:

```bash
sudo systemctl enable --now mariadb
```

Secure the server:

```bash
sudo mysql_secure_installation
```

------

# 🔥 4. Start Valkey (Redis Replacement)

Arch Linux uses **Valkey** instead of Redis.

Start and enable it:

```bash
sudo systemctl enable --now valkey
```

Check that it’s running:

```bash
systemctl status valkey
```

------

# 🛠️ 5. Install Bench CLI

```
python -m venv env
```

```
source env/bin/activate
```



Install Frappe Bench through pip:

```bash
pip install frappe-bench
```

Verify:

```bash
bench --version
```

------

# 🏗️ 6. Initialize a New Bench

Create your bench environment:

```bash
bench init mybench
```

Enter it:

```bash
cd mybench
```

------

# 🏠 7. Create a New Frappe Site

Run:

```bash
bench new-site mysite.local
```

Enter MariaDB root password when asked.

------

# 🚀 8. Start the Development Server

```bash
bench use mysite.local #setting default
```

```
bench start
```

Now open:

```
http://localhost:8000
```

------

