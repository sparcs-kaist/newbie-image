USERS = ["Alice", "Bob", "Charlie"]
DOCKERPATH = "./newbie"
NGINXPATH = "./nginx"
MYSQLPASSWD = ''
PASSLENGTH = 32
PORTRANGE = (17000, 20000)

PRINTINFO = """===
User: {user}
Password: {passwd}
SSH Port: {port22}
Web Port: {port3000}
API Port: {port8000}
"""

NGINXCONF = """
server {{
    server_name {domain};

    location / {{
        proxy_pass http://localhost:{port}/;
        proxy_set_header        Host               ${{host}};
        proxy_set_header        X-Real-IP          ${{remote_addr}};
        proxy_set_header        X-Forwarded-For    ${{proxy_add_x_forwarded_for}};
        proxy_set_header        X-Forwarded-Host   ${{host}}:443;
        proxy_set_header        X-Forwarded-Server ${{host}};
        proxy_set_header        X-Forwarded-Port   443;
        proxy_set_header        X-Forwarded-Proto  https;
        proxy_set_header        X-NginX-Proxy      true;

        # For Websocket
        proxy_http_version 1.1;
        proxy_set_header        Upgrade            ${{http_upgrade}};
        proxy_set_header        Connection         "Upgrade";

        proxy_redirect off;
    }}

    listen 443 ssl;
    listen [::]:443 ssl;
    include /etc/nginx/snippets/ssl.conf;
}}
server {{
    if ($host = {domain}) {{
        return 301 https://$host$request_uri;
    }}

    server_name {domain};

    listen 80;
    listen [::]:80;
    return 404;
}}
"""
