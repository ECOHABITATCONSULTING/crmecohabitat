#!/usr/bin/env python3
"""
Script FINAL - Juste les commandes npm/PM2, AUCUNE installation système
Le repo est déjà cloné à /var/www/crm-ehc
"""

import paramiko
import sys

VPS_HOST = '217.182.171.179'
VPS_USER = 'ubuntu'
VPS_PASSWORD = 'Pirouli2652148'
DOMAIN = 'crm-ehc.fr'
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

print("🚀 DÉPLOIEMENT FINAL CRM (npm + PM2 uniquement)")
print(f"VPS: {VPS_HOST} | Domaine: {DOMAIN}\n")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté au VPS\n")

    # Fix permissions
    exec_cmd(ssh, f"sudo chown -R {VPS_USER}:{VPS_USER} {PROJECT_DIR}", "ÉTAPE 1/8: Fix permissions")

    # Backend .env
    backend_env = """NODE_ENV=production
PORT=3001
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production-2024
DATABASE_PATH=./data/database.sqlite
ALLOWED_ORIGINS=https://crm-ehc.fr,http://crm-ehc.fr"""

    exec_cmd(ssh, f"cd {PROJECT_DIR}/backend && echo '{backend_env}' > .env && cat .env", "ÉTAPE 2/8: Backend .env")

    # Backend npm install
    exec_cmd(ssh, f"cd {PROJECT_DIR}/backend && npm install --production", "ÉTAPE 3/8: Backend npm install")

    # Backend data directory
    exec_cmd(ssh, f"mkdir -p {PROJECT_DIR}/backend/data", "ÉTAPE 4/8: Create data directory")

    # Frontend .env
    exec_cmd(ssh, f"cd {PROJECT_DIR}/frontend && echo 'VITE_API_URL=https://{DOMAIN}/api' > .env && cat .env", "ÉTAPE 5/8: Frontend .env")

    # Frontend npm install
    exec_cmd(ssh, f"cd {PROJECT_DIR}/frontend && npm install", "ÉTAPE 6/8: Frontend npm install")

    # Frontend build
    exec_cmd(ssh, f"cd {PROJECT_DIR}/frontend && npm run build", "ÉTAPE 7/8: Frontend build")

    # PM2
    exec_cmd(ssh, "pm2 delete all || true", "Clean PM2")
    exec_cmd(ssh, f"cd {PROJECT_DIR}/backend && pm2 start src/server.js --name crm-backend", "ÉTAPE 8/8: PM2 start")
    exec_cmd(ssh, "pm2 save", "PM2 save")
    exec_cmd(ssh, "pm2 list", "PM2 status")

    # Nginx reload
    exec_cmd(ssh, "sudo systemctl reload nginx", "Nginx reload")

    print("\n" + "="*60)
    print("✅ DÉPLOIEMENT TERMINÉ !")
    print("="*60)
    print(f"""
🌐 URL: http://{DOMAIN}
📊 API: http://{DOMAIN}/api
👤 Login: admin / admin123

🔧 Commandes:
   pm2 logs crm-backend
   pm2 restart crm-backend

🎯 TESTE LES 11 MODIFICATIONS !
    """)

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    ssh.close()
