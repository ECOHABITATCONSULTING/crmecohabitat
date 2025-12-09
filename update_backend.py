#!/usr/bin/env python3
"""Pull les derniers changements et redémarre PM2"""

import paramiko

VPS_HOST = '217.182.171.179'
VPS_USER = 'ubuntu'
VPS_PASSWORD = 'Pirouli2652148'
PROJECT_DIR = '/var/www/crm-ehc'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté au VPS\n")

    # Git pull
    stdin, stdout, stderr = ssh.exec_command(f"cd {PROJECT_DIR} && git pull")
    print(stdout.read().decode())

    # Restart PM2
    stdin, stdout, stderr = ssh.exec_command("pm2 restart crm-backend")
    print(stdout.read().decode())

    # Check status
    stdin, stdout, stderr = ssh.exec_command("pm2 list")
    print(stdout.read().decode())

    print("\n✅ Backend mis à jour et redémarré !")

except Exception as e:
    print(f"❌ ERREUR: {e}")
finally:
    ssh.close()
