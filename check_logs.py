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
    print("PM2 STATUS")
    print("="*60)
    stdin, stdout, stderr = ssh.exec_command("pm2 list")
    print(stdout.read().decode())

    print("\n" + "="*60)
    print("PM2 LOGS (dernières 30 lignes)")
    print("="*60)
    stdin, stdout, stderr = ssh.exec_command("pm2 logs crm-backend --lines 30 --nostream")
    print(stdout.read().decode())

    print("\n" + "="*60)
    print("BACKEND PORT")
    print("="*60)
    stdin, stdout, stderr = ssh.exec_command("netstat -tlnp | grep 3001 || echo 'Port 3001 pas ouvert'")
    print(stdout.read().decode())

except Exception as e:
    print(f"ERREUR: {e}")
finally:
    ssh.close()
