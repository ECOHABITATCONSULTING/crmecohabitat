#!/usr/bin/env python3
"""
VÉRIFICATION LOGS BACKEND
"""

import paramiko

VPS_HOST = '217.182.171.179'
VPS_USER = 'ubuntu'
VPS_PASSWORD = 'Pirouli2652148'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté\n")

    print("📋 LOGS PM2 (dernières 50 lignes):\n")
    print("="*60)
    stdin, stdout, stderr = ssh.exec_command("pm2 logs crm-backend --lines 50 --nostream")
    print(stdout.read().decode())

    print("\n" + "="*60)
    print("📊 STATUS PM2:\n")
    stdin, stdout, stderr = ssh.exec_command("pm2 status")
    print(stdout.read().decode())

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
finally:
    ssh.close()
