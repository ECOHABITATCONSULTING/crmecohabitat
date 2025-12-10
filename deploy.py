#!/usr/bin/env python3
"""
Script de déploiement unique pour CRM Leads Papa
Usage: python3 deploy.py
"""

import paramiko
import os
import sys
from pathlib import Path

# Charger les credentials depuis .env.vps
def load_vps_config():
    env_file = Path(__file__).parent / '.env.vps'
    if not env_file.exists():
        print("❌ Fichier .env.vps introuvable!")
        print("\nCréez un fichier .env.vps avec:")
        print("VPS_HOST=217.182.171.179")
        print("VPS_USER=ubuntu")
        print("VPS_PASSWORD=Pirouli2652148")
        print("VPS_PROJECT_DIR=/var/www/crm-ehc")
        sys.exit(1)

    config = {}
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                key, value = line.split('=', 1)
                config[key] = value
    return config

def exec_cmd(ssh, cmd, desc="", use_sudo=False, password=None):
    """Exécuter une commande sur le VPS"""
    print(f"\n▶ {desc}")
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)

    if use_sudo and password:
        stdin.write(password + '\n')
        stdin.flush()

    output = stdout.read().decode()
    error = stderr.read().decode()

    if output:
        for line in output.split('\n')[:20]:  # Limiter l'affichage
            print(line)

    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"✅ {desc}")
    else:
        print(f"❌ Erreur: {desc}")
        if error:
            print(error)
    return exit_status

def main():
    config = load_vps_config()

    VPS_HOST = config['VPS_HOST']
    VPS_USER = config['VPS_USER']
    VPS_PASSWORD = config['VPS_PASSWORD']
    PROJECT_DIR = config['VPS_PROJECT_DIR']

    print("🚀 DÉPLOIEMENT CRM LEADS PAPA")
    print(f"📡 Host: {VPS_HOST}")
    print(f"📂 Project: {PROJECT_DIR}\n")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
        print("✅ Connexion SSH établie\n")

        # 1. Pull les derniers changements
        exec_cmd(ssh,
            f"cd {PROJECT_DIR} && git pull origin main",
            "1/8: Pull GitHub")

        # 2. Installer les dépendances backend
        exec_cmd(ssh,
            f"cd {PROJECT_DIR}/backend && npm install",
            "2/8: npm install backend")

        # 3. Installer les dépendances frontend
        exec_cmd(ssh,
            f"cd {PROJECT_DIR}/frontend && npm install",
            "3/8: npm install frontend")

        # 4. Supprimer l'ancien build
        exec_cmd(ssh,
            f"sudo rm -rf {PROJECT_DIR}/frontend/dist",
            "4/8: Suppression ancien build",
            use_sudo=True,
            password=VPS_PASSWORD)

        # 5. Build frontend
        exec_cmd(ssh,
            f"cd {PROJECT_DIR}/frontend && npm run build",
            "5/8: npm run build")

        # 6. Fix permissions
        exec_cmd(ssh,
            f"sudo chown -R www-data:www-data {PROJECT_DIR}/frontend/dist",
            "6/8: Fix permissions",
            use_sudo=True,
            password=VPS_PASSWORD)

        # 7. Redémarrer PM2
        exec_cmd(ssh,
            f"cd {PROJECT_DIR}/backend && pm2 restart crm-backend || pm2 start src/server.js --name crm-backend",
            "7/8: Redémarrage PM2")

        # 8. Reload Nginx
        exec_cmd(ssh,
            "sudo systemctl reload nginx",
            "8/8: Reload Nginx",
            use_sudo=True,
            password=VPS_PASSWORD)

        print("\n" + "="*60)
        print("✅ DÉPLOIEMENT TERMINÉ !")
        print("="*60)
        print("\n🌐 https://crm-ehc.fr")
        print("\n⚠️  VIDE LE CACHE NAVIGATEUR ! (Ctrl+Shift+R)")

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        ssh.close()

if __name__ == '__main__':
    main()
