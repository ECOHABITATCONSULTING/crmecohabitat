#!/usr/bin/env python3
"""
INITIALISATION COMPLÈTE DE LA BASE DE DONNÉES
"""

import paramiko

VPS_HOST = '217.182.171.179'
VPS_USER = 'ubuntu'
VPS_PASSWORD = 'Pirouli2652148'
PROJECT_DIR = '/var/www/crm-ehc'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté\n")

    print("🗄️ Initialisation de la base de données...\n")

    # Vérifier si le script init-db.js existe
    stdin, stdout, stderr = ssh.exec_command(f"ls -la {PROJECT_DIR}/backend/init-db.js")
    print(stdout.read().decode())

    # Exécuter le script d'initialisation
    print("\n▶ Exécution de init-db.js...\n")
    stdin, stdout, stderr = ssh.exec_command(f"cd {PROJECT_DIR}/backend && node init-db.js")

    output = stdout.read().decode()
    print(output)

    err = stderr.read().decode()
    if err:
        print("STDERR:", err)

    # Vérifier les utilisateurs créés
    print("\n▶ Vérification des utilisateurs...\n")
    stdin, stdout, stderr = ssh.exec_command(
        f"sqlite3 {PROJECT_DIR}/backend/data/database.sqlite \"SELECT id, username, role FROM users;\""
    )

    users = stdout.read().decode()
    print("📋 Utilisateurs dans la base:")
    print(users if users else "❌ Aucun utilisateur trouvé")

    # Redémarrer le backend
    print("\n▶ Redémarrage du backend...\n")
    stdin, stdout, stderr = ssh.exec_command("pm2 restart crm-backend")
    print(stdout.read().decode())

    print("\n" + "="*60)
    print("✅ BASE DE DONNÉES INITIALISÉE")
    print("="*60)
    print("\n👤 LOGIN:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n🌐 https://crm-ehc.fr")

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
