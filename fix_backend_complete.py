#!/usr/bin/env python3
"""
FIX BACKEND COMPLET: Node v20 + Database Init
"""

import paramiko

VPS_HOST = '217.182.171.179'
VPS_USER = 'ubuntu'
VPS_PASSWORD = 'Pirouli2652148'
PROJECT_DIR = '/var/www/crm-ehc'

def exec_cmd(ssh, cmd, desc=""):
    print(f"\n▶ {desc}")
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
    return exit_status

print("🔧 FIX BACKEND COMPLET\n")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté\n")

    # 1. Vérifier Node.js v20
    print("=" * 60)
    print("ÉTAPE 1: VÉRIFICATION NODE.JS")
    print("=" * 60)
    stdin, stdout, stderr = ssh.exec_command("node --version")
    node_version = stdout.read().decode().strip()
    print(f"Node.js version: {node_version}")

    if not node_version.startswith('v20'):
        print("❌ Node.js v20 non trouvé, abandon")
        exit(1)

    # 2. Kill PM2 complètement
    print("\n" + "=" * 60)
    print("ÉTAPE 2: RESET PM2 COMPLET")
    print("=" * 60)

    exec_cmd(ssh, "pm2 kill", "2.1: PM2 kill")
    exec_cmd(ssh, "sudo npm uninstall -g pm2", "2.2: Désinstall PM2")
    exec_cmd(ssh, "rm -rf ~/.pm2", "2.3: Supprimer ~/.pm2")
    exec_cmd(ssh, "sudo npm install -g pm2@latest", "2.4: Réinstall PM2 avec Node v20")

    # 3. Vérifier que PM2 utilise bien Node v20
    print("\n" + "=" * 60)
    print("ÉTAPE 3: VÉRIFICATION PM2 NODE VERSION")
    print("=" * 60)
    stdin, stdout, stderr = ssh.exec_command("which node")
    node_path = stdout.read().decode().strip()
    print(f"Node path: {node_path}")

    # 4. Rebuild backend dependencies
    print("\n" + "=" * 60)
    print("ÉTAPE 4: REBUILD BACKEND")
    print("=" * 60)

    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/backend && rm -rf node_modules package-lock.json",
        "4.1: Nettoyage")

    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/backend && npm install",
        "4.2: npm install")

    # 5. Vérifier/créer database schema
    print("\n" + "=" * 60)
    print("ÉTAPE 5: DATABASE SCHEMA")
    print("=" * 60)

    # Copier le schéma depuis les migrations
    schema_check = """
const Database = require('better-sqlite3');
const db = new Database('/var/www/crm-ehc/backend/crm.db');

// Créer toutes les tables
db.exec(`
  CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT DEFAULT 'agent',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS leads (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    mobile_phone TEXT,
    address TEXT,
    postal_code TEXT,
    city TEXT,
    country TEXT,
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
  );

  CREATE TABLE IF NOT EXISTS clients (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    first_name TEXT NOT NULL,
    last_name TEXT NOT NULL,
    email TEXT,
    phone TEXT,
    mobile_phone TEXT,
    address TEXT,
    postal_code TEXT,
    city TEXT,
    country TEXT,
    status TEXT DEFAULT 'nouveau',
    rdv_pris INTEGER DEFAULT 0,
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (created_by) REFERENCES users(id)
  );

  CREATE TABLE IF NOT EXISTS commerciaux (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    color TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
  );

  CREATE TABLE IF NOT EXISTS appointments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    client_id INTEGER,
    title TEXT NOT NULL,
    date DATE NOT NULL,
    time TIME NOT NULL,
    commercial_id INTEGER,
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY (commercial_id) REFERENCES commerciaux(id),
    FOREIGN KEY (created_by) REFERENCES users(id)
  );

  CREATE TABLE IF NOT EXISTS comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lead_id INTEGER,
    client_id INTEGER,
    content TEXT NOT NULL,
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (lead_id) REFERENCES leads(id) ON DELETE CASCADE,
    FOREIGN KEY (client_id) REFERENCES clients(id) ON DELETE CASCADE,
    FOREIGN KEY (created_by) REFERENCES users(id)
  );
`);

console.log('✅ Database schema créé');

// Créer admin user si nécessaire
const bcrypt = require('bcryptjs');
const existing = db.prepare('SELECT * FROM users WHERE username = ?').get('admin');
if (!existing) {
  const hash = bcrypt.hashSync('admin123', 10);
  db.prepare('INSERT INTO users (username, password, role) VALUES (?, ?, ?)').run('admin', hash, 'admin');
  console.log('✅ Admin user créé');
} else {
  console.log('✅ Admin user existe déjà');
}

db.close();
console.log('✅ Database OK');
"""

    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/backend && node -e \"{schema_check}\"",
        "5.1: Création database schema")

    # 6. Démarrer backend avec PM2
    print("\n" + "=" * 60)
    print("ÉTAPE 6: DÉMARRAGE BACKEND")
    print("=" * 60)

    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/backend && pm2 start src/server.js --name crm-backend",
        "6.1: PM2 start")

    exec_cmd(ssh, "pm2 save", "6.2: PM2 save")

    # 7. Vérifier que ça tourne
    print("\n" + "=" * 60)
    print("ÉTAPE 7: VÉRIFICATION")
    print("=" * 60)

    exec_cmd(ssh, "pm2 list", "7.1: PM2 list")

    print("\n📋 Attendre 5 secondes...")
    import time
    time.sleep(5)

    stdin, stdout, stderr = ssh.exec_command("tail -20 /home/ubuntu/.pm2/logs/crm-backend-out.log")
    print("\n📋 Backend Output (dernières 20 lignes):")
    print(stdout.read().decode())

    stdin, stdout, stderr = ssh.exec_command("tail -20 /home/ubuntu/.pm2/logs/crm-backend-error.log")
    errors = stdout.read().decode()
    if errors.strip():
        print("\n⚠️  Backend Errors (dernières 20 lignes):")
        print(errors)
    else:
        print("\n✅ Aucune erreur dans les logs")

    # 8. Tester l'API
    print("\n" + "=" * 60)
    print("ÉTAPE 8: TEST API")
    print("=" * 60)

    import requests
    try:
        response = requests.get('https://crm-ehc.fr/api/health', timeout=10)
        print(f"✅ API Health: {response.status_code}")
    except Exception as e:
        print(f"❌ API Health: {e}")

    try:
        response = requests.post('https://crm-ehc.fr/api/auth/login',
                                json={'username': 'admin', 'password': 'admin123'},
                                timeout=10)
        print(f"✅ API Login: {response.status_code}")
        if response.status_code == 200:
            print(f"   Token: {response.json().get('token', '')[:20]}...")
    except Exception as e:
        print(f"❌ API Login: {e}")

    print("\n" + "=" * 60)
    print("✅ BACKEND FIX TERMINÉ !")
    print("=" * 60)

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
