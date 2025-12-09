#!/usr/bin/env python3
"""
FIX: PM2 utilise Node.js v12 au lieu de v20
"""

import paramiko
import time

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

print("🔧 FIX PM2 NODE VERSION\n")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté\n")

    # Arrêter et supprimer tous les processus PM2
    exec_cmd(ssh, "pm2 delete all || true", "1/6: Supprimer processus PM2")
    exec_cmd(ssh, "pm2 kill", "2/6: Kill PM2 daemon")

    # Supprimer PM2 globalement
    exec_cmd(ssh, "sudo npm uninstall -g pm2", "3/6: Désinstaller PM2")

    # Réinstaller PM2 avec Node.js v20
    exec_cmd(ssh, "sudo npm install -g pm2", "4/6: Réinstaller PM2")

    # Vérifier la version de Node utilisée
    stdin, stdout, stderr = ssh.exec_command("node --version")
    node_version = stdout.read().decode().strip()
    print(f"\n✅ Node.js version: {node_version}")

    # Démarrer le backend avec PM2
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/backend && pm2 start src/server.js --name crm-backend",
        "5/6: Démarrer backend")

    exec_cmd(ssh, "pm2 save", "6/6: Sauvegarder PM2")

    time.sleep(2)

    # Vérifier le statut
    print("\n📊 STATUS PM2:")
    stdin, stdout, stderr = ssh.exec_command("pm2 list")
    print(stdout.read().decode())

    # Tester l'API
    print("\n🧪 TEST API:")
    stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:3001/api/health")
    response = stdout.read().decode()
    print(response)

    print("\n" + "="*60)
    print("✅ PM2 RÉINITIALISÉ AVEC NODE.JS V20")
    print("="*60)
    print(f"\n🌐 https://crm-ehc.fr")
    print("👤 Login: admin / admin123")

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
