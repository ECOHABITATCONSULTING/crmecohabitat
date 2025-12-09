#!/usr/bin/env python3
"""
QUICK API TEST VIA SSH
"""

import paramiko
import time

VPS_HOST = '217.182.171.179'
VPS_USER = 'ubuntu'
VPS_PASSWORD = 'Pirouli2652148'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté\n")

    # Test local API from VPS
    print("📊 Test API localhost depuis le VPS:")
    stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:3001/api/health")
    print(stdout.read().decode())

    print("\n📊 Test login localhost:")
    stdin, stdout, stderr = ssh.exec_command("curl -s -X POST http://localhost:3001/api/auth/login -H 'Content-Type: application/json' -d '{\"username\":\"admin\",\"password\":\"admin123\"}'")
    print(stdout.read().decode())

    print("\n\n📊 PM2 Status:")
    stdin, stdout, stderr = ssh.exec_command("pm2 list")
    print(stdout.read().decode())

    print("\n📋 Error logs (10 dernières lignes):")
    stdin, stdout, stderr = ssh.exec_command("tail -10 /home/ubuntu/.pm2/logs/crm-backend-error.log")
    errors = stdout.read().decode()
    if errors.strip():
        print(errors)
    else:
        print("✅ Aucune erreur")

    print("\n📋 Output logs (10 dernières lignes):")
    stdin, stdout, stderr = ssh.exec_command("tail -10 /home/ubuntu/.pm2/logs/crm-backend-out.log")
    print(stdout.read().decode())

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
