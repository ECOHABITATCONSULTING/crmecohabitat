#!/usr/bin/env python3
import paramiko

VPS_HOST = '217.182.171.179'
VPS_USER = 'ubuntu'
VPS_PASSWORD = 'Pirouli2652148'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)

    print("="*60)
    print("ERREUR COMPLÈTE")
    print("="*60)
    stdin, stdout, stderr = ssh.exec_command("tail -50 /home/ubuntu/.pm2/logs/crm-backend-error.log")
    print(stdout.read().decode())

except Exception as e:
    print(f"ERREUR: {e}")
finally:
    ssh.close()
