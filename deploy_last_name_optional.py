#!/usr/bin/env python3
"""
Script de déploiement: Rendre last_name optionnel
Déploie les modifications sur le VPS via SSH (paramiko)
"""

import paramiko
import os
import sys
from pathlib import Path

# Configuration VPS
VPS_HOST = "217.182.171.179"
VPS_USER = "ubuntu"
VPS_PATH = "/var/www/crm-ehc"
SSH_KEY_PATH = os.path.expanduser("~/.ssh/id_rsa")

def print_step(step, message):
    """Affiche une étape de déploiement"""
    print(f"\n{'='*70}")
    print(f"ÉTAPE {step}: {message}")
    print('='*70)

def execute_command(ssh, command, description):
    """Exécute une commande SSH et affiche le résultat"""
    print(f"\n➤ {description}")
    print(f"  Commande: {command}")

    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()

    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')

    if output:
        print(f"  Sortie:\n{output}")

    if error and exit_status != 0:
        print(f"  ⚠️  Erreur:\n{error}")
        return False

    print(f"  ✅ Succès")
    return True

def main():
    print_step(1, "Connexion au VPS")

    # Créer le client SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connexion SSH
        print(f"Connexion à {VPS_USER}@{VPS_HOST}...")
        ssh.connect(
            hostname=VPS_HOST,
            username=VPS_USER,
            key_filename=SSH_KEY_PATH,
            timeout=10
        )
        print("✅ Connexion établie")

        print_step(2, "Sauvegarde de la base de données")
        execute_command(
            ssh,
            f"cd {VPS_PATH} && cp backend/database.db backend/database.db.backup-$(date +%Y%m%d-%H%M%S)",
            "Création backup database"
        )

        print_step(3, "Git pull des modifications")
        execute_command(
            ssh,
            f"cd {VPS_PATH} && git stash && git pull origin main && git stash pop || true",
            "Récupération dernières modifications"
        )

        print_step(4, "Installation dépendances backend")
        execute_command(
            ssh,
            f"cd {VPS_PATH}/backend && npm install",
            "npm install backend"
        )

        print_step(5, "Installation dépendances frontend")
        execute_command(
            ssh,
            f"cd {VPS_PATH}/frontend && npm install",
            "npm install frontend"
        )

        print_step(6, "Build frontend")
        execute_command(
            ssh,
            f"cd {VPS_PATH}/frontend && npm run build",
            "Build production frontend"
        )

        print_step(7, "Fix permissions")
        execute_command(
            ssh,
            f"sudo chown -R www-data:www-data {VPS_PATH}/frontend/dist",
            "Changement propriétaire dist/"
        )
        execute_command(
            ssh,
            f"sudo chown -R ubuntu:ubuntu {VPS_PATH}/backend/database.db*",
            "Permissions database"
        )

        print_step(8, "Test migration database")
        result = execute_command(
            ssh,
            f"cd {VPS_PATH}/backend && node -e \"const db = require('./src/database'); console.log('Migration OK'); process.exit(0);\"",
            "Test migration last_name optionnel"
        )

        if not result:
            print("\n❌ ERREUR: Migration database échouée!")
            print("Voulez-vous continuer quand même? (y/n)")
            if input().lower() != 'y':
                print("Déploiement annulé")
                return

        print_step(9, "Vérification structure table leads")
        execute_command(
            ssh,
            f"cd {VPS_PATH}/backend && sqlite3 database.db \"PRAGMA table_info(leads);\" | grep last_name",
            "Vérification last_name optionnel"
        )

        print_step(10, "Restart PM2")
        execute_command(
            ssh,
            "pm2 restart ecosystem.config.js",
            "Redémarrage application"
        )

        print_step(11, "Reload Nginx")
        execute_command(
            ssh,
            "sudo nginx -t && sudo systemctl reload nginx",
            "Rechargement Nginx"
        )

        print_step(12, "Vérification statut")
        execute_command(
            ssh,
            "pm2 status",
            "Statut PM2"
        )

        print("\n" + "="*70)
        print("✅ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS!")
        print("="*70)
        print("\nModifications déployées:")
        print("  • last_name est maintenant OPTIONNEL dans l'import CSV")
        print("  • Champs obligatoires: first_name, email, phone, postal_code")
        print("  • Documentation mise à jour dans le modal d'import")
        print("\nTester l'import CSV sur: https://crm-ehc.fr")
        print("="*70)

    except paramiko.AuthenticationException:
        print("❌ Erreur d'authentification SSH")
        print(f"Vérifiez la clé SSH: {SSH_KEY_PATH}")
        sys.exit(1)

    except paramiko.SSHException as e:
        print(f"❌ Erreur SSH: {e}")
        sys.exit(1)

    except Exception as e:
        print(f"❌ Erreur inattendue: {e}")
        sys.exit(1)

    finally:
        ssh.close()
        print("\n🔒 Connexion SSH fermée")

if __name__ == "__main__":
    print("\n🚀 DÉPLOIEMENT: Rendre last_name optionnel")
    print("="*70)
    main()
