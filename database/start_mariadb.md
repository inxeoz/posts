docker run -d \
  --name mariadb \
  --network frappe-net \
  -e MYSQL_ROOT_PASSWORD=frappe \
  -e MYSQL_USER=frappe \
  -e MYSQL_PASSWORD=frappe \
  -e MYSQL_DATABASE=frappe \
  -v mariadb_data:/var/lib/mysql \
  -p 3307:3306 \
  mariadb:10.6
