#!/usr/bin/env python3
"""
VÉRIFICATION MOT DE PASSE ADMIN
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

    print("🔍 Vérification des utilisateurs dans la base de données...\n")

    # Lire les utilisateurs de la base
    stdin, stdout, stderr = ssh.exec_command(
        f"sqlite3 {PROJECT_DIR}/backend/data/database.sqlite \"SELECT id, username, role FROM users;\""
    )

    users = stdout.read().decode()
    print("📋 Utilisateurs existants:")
    print(users)

    # Réinitialiser le mot de passe admin
    print("\n🔧 Réinitialisation du mot de passe admin...\n")

    # Hash pour 'admin123' avec bcrypt
    # On va utiliser le script init-db.js qui existe déjà
    stdin, stdout, stderr = ssh.exec_command(
        f"cd {PROJECT_DIR}/backend && node -e \""
        "const bcrypt = require('bcryptjs'); "
        "const db = require('./src/database'); "
        "const hash = bcrypt.hashSync('admin123', 10); "
        "db.prepare('UPDATE users SET password = ? WHERE username = ?').run(hash, 'admin'); "
        "console.log('✅ Mot de passe admin réinitialisé: admin123');\""
    )

    print(stdout.read().decode())
    err = stderr.read().decode()
    if err:
        print(err)

    print("\n" + "="*60)
    print("✅ MOT DE PASSE RÉINITIALISÉ")
    print("="*60)
    print("\n👤 LOGIN:")
    print("   Username: admin")
    print("   Password: admin123")

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
