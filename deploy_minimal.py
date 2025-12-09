#!/usr/bin/env python3
"""
Script de déploiement MINIMAL - Installation rapide sans bloat
"""

import paramiko
import sys

# Configuration
VPS_HOST = '217.182.171.179'
VPS_USER = 'ubuntu'
VPS_PASSWORD = 'Pirouli2652148'
DOMAIN = 'crm-ehc.fr'
GIT_REPO = 'https://github.com/ECOHABITATCONSULTING/crmecohabitat.git'
PROJECT_DIR = '/var/www/crm-ehc'

def exec_cmd(ssh, cmd, desc=""):
    print(f"\n{'='*60}\n▶ {desc}\n{'='*60}")
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)

    if 'sudo' in cmd:
        stdin.write(VPS_PASSWORD + '\n')
        stdin.flush()

    for line in stdout:
        print(line.strip())

    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"✅ {desc} - OK")
    else:
        print(f"❌ ERREUR (code {exit_status})")
    return exit_status

print("🚀 DÉPLOIEMENT MINIMAL CRM")
print(f"VPS: {VPS_HOST} | Domaine: {DOMAIN}\n")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté au VPS\n")

    # Check si nodejs/npm existent déjà
    exec_cmd(ssh, "node --version || echo 'Node.js pas installé'", "Check Node.js")
    exec_cmd(ssh, "nginx -v || echo 'Nginx pas installé'", "Check Nginx")

    # Installation UNIQUEMENT si manquant
    exec_cmd(ssh,
        "command -v node || (curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt install -y nodejs)",
        "ÉTAPE 1: Install Node.js 20 (si absent)")

    exec_cmd(ssh,
        "command -v nginx || sudo apt install -y nginx --no-install-recommends",
        "ÉTAPE 2: Install Nginx (si absent)")

    exec_cmd(ssh,
        "command -v pm2 || sudo npm install -g pm2",
        "ÉTAPE 3: Install PM2 (si absent)")

    # Nettoyage
    exec_cmd(ssh, "pm2 delete all || true", "ÉTAPE 4: Arrêt PM2")
    exec_cmd(ssh, f"sudo rm -rf {PROJECT_DIR}", "Suppression ancien projet")
    exec_cmd(ssh, "sudo mkdir -p /var/www", "Création /var/www")

    # Clone
    exec_cmd(ssh, f"sudo git clone {GIT_REPO} {PROJECT_DIR}", "ÉTAPE 5: Clone GitHub")
    exec_cmd(ssh, f"sudo chown -R {VPS_USER}:{VPS_USER} {PROJECT_DIR}", "Fix permissions")

    # Backend
    backend_env = """NODE_ENV=production
PORT=3001
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production-2024
DATABASE_PATH=./data/database.sqlite
ALLOWED_ORIGINS=https://crm-ehc.fr,http://crm-ehc.fr
"""
    exec_cmd(ssh, f"cd {PROJECT_DIR}/backend && echo '{backend_env}' > .env", "ÉTAPE 6: Config backend .env")
    exec_cmd(ssh, f"cd {PROJECT_DIR}/backend && npm install --production", "Install backend deps")
    exec_cmd(ssh, f"mkdir -p {PROJECT_DIR}/backend/data", "Création data/")

    # Frontend
    frontend_env = "VITE_API_URL=https://crm-ehc.fr/api\n"
    exec_cmd(ssh, f"cd {PROJECT_DIR}/frontend && echo '{frontend_env}' > .env", "ÉTAPE 7: Config frontend .env")
    exec_cmd(ssh, f"cd {PROJECT_DIR}/frontend && npm install", "Install frontend deps")
    exec_cmd(ssh, f"cd {PROJECT_DIR}/frontend && npm run build", "Build frontend")

    # Nginx
    nginx_config = f"""server {{
    listen 80;
    server_name {DOMAIN} www.{DOMAIN};
    client_max_body_size 10M;

    location / {{
        root {PROJECT_DIR}/frontend/dist;
        try_files $uri $uri/ /index.html;
    }}

    location /api {{
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }}

    access_log /var/log/nginx/{DOMAIN}_access.log;
    error_log /var/log/nginx/{DOMAIN}_error.log;
}}
"""
    exec_cmd(ssh, f"sudo bash -c 'cat > /etc/nginx/sites-available/{DOMAIN} << \"EOF\"\n{nginx_config}\nEOF'", "ÉTAPE 8: Config Nginx")
    exec_cmd(ssh, "sudo rm -f /etc/nginx/sites-enabled/default", "Désactivation default")
    exec_cmd(ssh, f"sudo ln -sf /etc/nginx/sites-available/{DOMAIN} /etc/nginx/sites-enabled/", "Activation config")
    exec_cmd(ssh, "sudo nginx -t", "Test Nginx")
    exec_cmd(ssh, "sudo systemctl reload nginx", "Reload Nginx")

    # PM2
    exec_cmd(ssh, f"cd {PROJECT_DIR}/backend && pm2 start src/server.js --name crm-backend", "ÉTAPE 9: Start PM2")
    exec_cmd(ssh, "pm2 save", "Save PM2")
    exec_cmd(ssh, "pm2 list", "Status PM2")

    print("\n" + "="*60)
    print("✅ DÉPLOIEMENT TERMINÉ !")
    print("="*60)
    print(f"""
🌐 URL: http://{DOMAIN}
📊 Backend: http://{DOMAIN}/api
👤 Login: admin / admin123

🔧 Commandes utiles:
   pm2 logs crm-backend
   pm2 restart crm-backend
   sudo tail -f /var/log/nginx/{DOMAIN}_*.log
    """)

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    ssh.close()

if __name__ == "__main__":
    main()
