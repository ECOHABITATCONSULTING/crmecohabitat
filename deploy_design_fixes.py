#!/usr/bin/env python3
"""
Script de déploiement avec optimisations VPS
Corrige les problèmes identifiés dans l'analyse
"""

import paramiko
import os
from dotenv import load_dotenv

# Charger les credentials VPS
load_dotenv('.env.vps')

VPS_HOST = os.getenv('VPS_HOST')
VPS_USER = os.getenv('VPS_USER')
VPS_PASSWORD = os.getenv('VPS_PASSWORD')
PROJECT_DIR = os.getenv('VPS_PROJECT_DIR')

def execute_command(ssh, command, description=""):
    """Exécute une commande SSH et affiche le résultat"""
    if description:
        print(f"\n🔧 {description}...")

    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode().strip()
    error = stderr.read().decode().strip()

    if error and 'warning' not in error.lower():
        print(f"⚠️  {error}")
    if output:
        print(f"✅ {output}")

    return output

def main():
    print("=" * 60)
    print("🚀 DÉPLOIEMENT AVEC OPTIMISATIONS VPS")
    print("=" * 60)

    # Connexion SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        print(f"\n🔌 Connexion à {VPS_HOST}...")
        ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
        print("✅ Connecté\n")

        # 1. Git pull
        execute_command(
            ssh,
            f"cd {PROJECT_DIR} && git pull origin main",
            "Récupération du code depuis GitHub"
        )

        # 2. NPM install backend
        execute_command(
            ssh,
            f"cd {PROJECT_DIR}/backend && npm install --production",
            "Installation des dépendances backend"
        )

        # 3. NPM install + build frontend
        execute_command(
            ssh,
            f"cd {PROJECT_DIR}/frontend && npm install && npm run build",
            "Build du frontend"
        )

        # 4. Vérifier et activer le mode WAL si nécessaire
        print("\n🗄️  Vérification de la base de données...")
        wal_check = execute_command(
            ssh,
            f'cd {PROJECT_DIR}/backend && node -e "const db=require(\'better-sqlite3\')(\'./database.db\');const mode=db.pragma(\'journal_mode\',{{simple:true}});console.log(mode);db.close();"',
            "Mode journal actuel"
        )

        if 'wal' not in wal_check.lower():
            execute_command(
                ssh,
                f'cd {PROJECT_DIR}/backend && node -e "const db=require(\'better-sqlite3\')(\'./database.db\');db.pragma(\'journal_mode = WAL\');console.log(\'WAL activé\');db.close();"',
                "Activation du mode WAL"
            )
        else:
            print("✅ Mode WAL déjà actif")

        # 5. Permissions
        execute_command(
            ssh,
            f"sudo chown -R ubuntu:ubuntu {PROJECT_DIR}",
            "Correction des permissions"
        )

        # 6. Restart PM2
        execute_command(
            ssh,
            "pm2 restart crm-backend",
            "Redémarrage du backend PM2"
        )

        # 7. PM2 save
        execute_command(
            ssh,
            "pm2 save",
            "Sauvegarde de la config PM2"
        )

        # 8. Reload Nginx
        execute_command(
            ssh,
            "sudo nginx -t && sudo systemctl reload nginx",
            "Rechargement de Nginx"
        )

        # 9. Vérification finale
        print("\n" + "=" * 60)
        print("📊 VÉRIFICATION FINALE")
        print("=" * 60)

        pm2_status = execute_command(
            ssh,
            "pm2 jlist | jq -r '.[0] | \"Status: \\(.pm2_env.status) | Memory: \\(.monit.memory / 1024 / 1024 | floor)MB | Restarts: \\(.pm2_env.restart_time)\"'",
            "Status PM2"
        )

        db_mode = execute_command(
            ssh,
            f'cd {PROJECT_DIR}/backend && node -e "const db=require(\'better-sqlite3\')(\'./database.db\');console.log(\'Journal mode:\', db.pragma(\'journal_mode\',{{simple:true}}));db.close();"',
            "Mode DB"
        )

        print("\n✅ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS!")
        print("=" * 60)
        print(f"🌐 Site accessible sur : https://crm-ehc.fr")
        print("=" * 60)

    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

    finally:
        ssh.close()

if __name__ == '__main__':
    main()
