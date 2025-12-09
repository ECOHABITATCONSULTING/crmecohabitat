#!/usr/bin/env python3
"""
CRÉATION UTILISATEUR ADMIN
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

    print("👤 Création de l'utilisateur admin...\n")

    # Créer l'utilisateur admin avec bcrypt
    create_admin_script = """
const bcrypt = require('bcryptjs');
const db = require('./src/database');

// Supprimer l'ancien admin s'il existe
db.prepare('DELETE FROM users WHERE username = ?').run('admin');

// Créer le nouveau admin
const hash = bcrypt.hashSync('admin123', 10);
const result = db.prepare(
  'INSERT INTO users (username, password, role) VALUES (?, ?, ?)'
).run('admin', hash, 'admin');

console.log('✅ Utilisateur admin créé avec ID:', result.lastInsertRowid);

// Vérifier
const user = db.prepare('SELECT id, username, role FROM users WHERE username = ?').get('admin');
console.log('📋 Utilisateur vérifié:', JSON.stringify(user));
"""

    # Exécuter le script
    stdin, stdout, stderr = ssh.exec_command(
        f"cd {PROJECT_DIR}/backend && node -e \"{create_admin_script.replace(chr(10), ' ')}\""
    )

    print(stdout.read().decode())
    err = stderr.read().decode()
    if err and 'warn' not in err.lower():
        print("STDERR:", err)

    print("\n" + "="*60)
    print("✅ UTILISATEUR ADMIN CRÉÉ")
    print("="*60)
    print("\n🌐 https://crm-ehc.fr")
    print("\n👤 LOGIN:")
    print("   Username: admin")
    print("   Password: admin123")
    print("\n🎯 TESTE TES 11 MODIFICATIONS !")

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
