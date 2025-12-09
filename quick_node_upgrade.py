#!/usr/bin/env python3
"""
APPROCHE RAPIDE: Install Node.js 20 PAR-DESSUS v12
SANS supprimer l'ancien (évite apt autoremove lent)
"""

import paramiko
import sys
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

print("🚀 UPGRADE RAPIDE NODE.JS v20\n")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté\n")

    # Stop PM2
    exec_cmd(ssh, "pm2 stop all || true", "1/6: Stop PM2")

    # Install Node.js 20 (override v12)
    exec_cmd(ssh,
        "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -",
        "2/6: Setup NodeSource")

    exec_cmd(ssh,
        "sudo apt install -y --reinstall nodejs",
        "3/6: Install Node.js 20")

    # Verify
    stdin, stdout, stderr = ssh.exec_command("node --version")
    version = stdout.read().decode().strip()
    print(f"\n✅ Node.js: {version}\n")

    # Reinstall PM2
    exec_cmd(ssh, "sudo npm install -g pm2", "4/6: Install PM2")

    # Reinstall deps
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/backend && rm -rf node_modules && npm install --production",
        "5/6: Backend deps")

    # Start PM2
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/backend && pm2 start src/server.js --name crm-backend",
        "6/6: Start backend")

    time.sleep(2)
    exec_cmd(ssh, "pm2 list", "PM2 Status")

    print("\n" + "="*60)
    print("✅ TERMINÉ !")
    print(f"🌐 Test: http://crm-ehc.fr")
    print("="*60)

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    sys.exit(1)
finally:
    ssh.close()
