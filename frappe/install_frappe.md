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
sudo systemctl status valkey
sudo ss -ltnp | grep valkey # checking on what ports the valkey(redis serves) serving

```

> LISTEN 0      511             127.0.0.1:6379       0.0.0.0:*    users:(("valkey-server",pid=946,fd=8))
> LISTEN 0      511                 [::1]:6379          [::]:*    users:(("valkey-server",pid=946,fd=9))

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



# update the common site config to match redis server port 


```bash
…/prob/sites ❯ cat common_site_config.json
{
 "background_workers": 1,
 "default_site": "frontend",
 "file_watcher_port": 6787,
 "frappe_user": "inxeoz",
 "gunicorn_workers": 17,
 "live_reload": true,
 "rebase_on_pull": false,
 "redis_cache": "redis://127.0.0.1:6379",
 "redis_queue": "redis://127.0.0.1:6379",
 "redis_socketio": "redis://127.0.0.1:6379",
 "restart_supervisor_on_update": false,
 "restart_systemd_on_update": false,
 "serve_default_site": true,
 "shallow_clone": true,
 "socketio_port": 9000,
 "use_redis_auth": false,
 "webserver_port": 8000
}

…/prob/sites ❯
```



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