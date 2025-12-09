#!/usr/bin/env python3
"""
FIX NGINX CONFIGURATION
"""

import paramiko

VPS_HOST = '217.182.171.179'
VPS_USER = 'ubuntu'
VPS_PASSWORD = 'Pirouli2652148'
DOMAIN = 'crm-ehc.fr'

def exec_cmd(ssh, cmd, desc=""):
    print(f"\n▶ {desc}")
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)

    if 'sudo' in cmd:
        stdin.write(VPS_PASSWORD + '\n')
        stdin.flush()

    output = ""
    for line in stdout:
        print(line.strip())
        output += line

    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"✅ {desc}")
    else:
        print(f"❌ Erreur: {desc}")
    return exit_status, output

print("🔧 FIX NGINX CONFIGURATION\n")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté\n")

    # Vérifier config Nginx actuelle
    print("📋 Configuration Nginx actuelle:")
    stdin, stdout, stderr = ssh.exec_command(f"sudo cat /etc/nginx/sites-available/{DOMAIN}")
    stdin.write(VPS_PASSWORD + '\n')
    stdin.flush()
    current_config = stdout.read().decode()
    print(current_config)

    # Créer nouvelle config Nginx optimisée
    nginx_config = f"""server {{
    listen 80;
    server_name {DOMAIN};

    # Redirect HTTP to HTTPS
    return 301 https://$host$request_uri;
}}

server {{
    listen 443 ssl http2;
    server_name {DOMAIN};

    # SSL Certificate
    ssl_certificate /etc/letsencrypt/live/{DOMAIN}/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/{DOMAIN}/privkey.pem;
    include /etc/letsencrypt/options-ssl-nginx.conf;
    ssl_dhparam /etc/letsencrypt/ssl-dhparams.pem;

    # Security headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend - React App
    location / {{
        root /var/www/crm-ehc/frontend/dist;
        try_files $uri $uri/ /index.html;
        index index.html;
    }}

    # Backend API
    location /api/ {{
        proxy_pass http://localhost:3001/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}

    # Static assets caching
    location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
        root /var/www/crm-ehc/frontend/dist;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }}
}}
"""

    print("\n" + "=" * 60)
    print("NOUVELLE CONFIGURATION NGINX")
    print("=" * 60)
    print(nginx_config)

    # Écrire la nouvelle config
    exec_cmd(ssh,
        f"sudo tee /etc/nginx/sites-available/{DOMAIN} > /dev/null <<'EOF'\n{nginx_config}\nEOF",
        "Écriture nouvelle config")

    # Tester la config Nginx
    status, output = exec_cmd(ssh, "sudo nginx -t", "Test config Nginx")

    if status == 0:
        # Recharger Nginx
        exec_cmd(ssh, "sudo systemctl reload nginx", "Reload Nginx")
        exec_cmd(ssh, "sudo systemctl status nginx --no-pager", "Status Nginx")

        print("\n" + "=" * 60)
        print("✅ NGINX CONFIGURÉ !")
        print("=" * 60)
        print(f"\n🌐 Test: https://{DOMAIN}")
        print("\n⏳ Attente de 3 secondes...")

        import time
        time.sleep(3)

        print("\n📊 Test API externe:")
        import requests
        try:
            response = requests.get(f'https://{DOMAIN}/api/health', timeout=10)
            print(f"✅ API Health: {response.status_code}")
            print(f"   Response: {response.json()}")
        except Exception as e:
            print(f"❌ API Health: {e}")
    else:
        print("\n❌ Config Nginx invalide, changements annulés")

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
