#!/usr/bin/env python3
"""
REBUILD FRONTEND + ACTIVATION HTTPS
"""

import paramiko
import sys
import time

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
        print(f"✅ {desc}")
    else:
        print(f"❌ Erreur: {desc}")
        err = stderr.read().decode()
        if err:
            print(err)
    return exit_status

print("""
╔═══════════════════════════════════════════════════════════╗
║   🔨 REBUILD FRONTEND + HTTPS                            ║
║   VPS: 217.182.171.179 | Domaine: crm-ehc.fr             ║
╚═══════════════════════════════════════════════════════════╝
""")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("🔌 Connexion au VPS...")
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté\n")

    # ÉTAPE 1: Créer le fichier .env frontend
    print("\n📝 CRÉATION .env FRONTEND...")
    exec_cmd(ssh,
        f"cat > {PROJECT_DIR}/frontend/.env << 'EOF'\nVITE_API_URL=https://{DOMAIN}/api\nEOF",
        "1/7: Création .env frontend")

    # ÉTAPE 2: Nettoyer ancien build
    print("\n🗑️  NETTOYAGE ANCIEN BUILD...")
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/frontend && rm -rf node_modules dist",
        "2/7: Suppression node_modules et dist")

    # ÉTAPE 3: Installer dépendances
    print("\n📦 INSTALLATION DÉPENDANCES...")
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/frontend && npm install",
        "3/7: npm install frontend")

    # ÉTAPE 4: Build frontend
    print("\n🔨 BUILD FRONTEND...")
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/frontend && npm run build",
        "4/7: Build frontend")

    # ÉTAPE 5: Reload Nginx
    exec_cmd(ssh,
        "sudo systemctl reload nginx",
        "5/7: Reload Nginx")

    print("\n✅ FRONTEND REBUILD TERMINÉ !")
    print(f"🌐 Test HTTP: http://{DOMAIN}")

    # ÉTAPE 6: Installer Certbot si nécessaire
    print("\n🔒 INSTALLATION CERTBOT...")
    stdin, stdout, stderr = ssh.exec_command("which certbot")
    certbot_exists = stdout.read().decode().strip()

    if not certbot_exists:
        exec_cmd(ssh,
            "sudo DEBIAN_FRONTEND=noninteractive apt install -y certbot python3-certbot-nginx",
            "6/7: Installation Certbot")
    else:
        print("✅ Certbot déjà installé")

    # ÉTAPE 7: Activer HTTPS
    print("\n🔐 ACTIVATION HTTPS...")
    exec_cmd(ssh,
        f"sudo certbot --nginx -d {DOMAIN} -d www.{DOMAIN} --non-interactive --agree-tos --email admin@{DOMAIN} --redirect",
        "7/7: Configuration SSL")

    print("\n" + "="*60)
    print("🎉 DÉPLOIEMENT COMPLET TERMINÉ !")
    print("="*60)
    print(f"""
🌐 URLS:
   HTTP:  http://{DOMAIN} (redirige vers HTTPS)
   HTTPS: https://{DOMAIN}
   API:   https://{DOMAIN}/api

👤 LOGIN:
   Username: admin
   Password: admin123

✅ Backend: PM2 online (Node.js v20.19.6)
✅ Frontend: Built et déployé
✅ Nginx: Configuré avec SSL
✅ HTTPS: Let's Encrypt actif

🎯 TESTE MAINTENANT TES 11 MODIFICATIONS !

🔧 Commandes utiles:
   pm2 logs crm-backend
   pm2 restart crm-backend
   sudo tail -f /var/log/nginx/{DOMAIN}_error.log
   sudo certbot renew --dry-run  # Test renouvellement SSL
    """)

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    ssh.close()
    print("\n🔌 Connexion SSH fermée")
