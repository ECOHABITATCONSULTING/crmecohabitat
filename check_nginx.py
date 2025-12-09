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
    print("1. TEST PORT 3001 (backend)")
    print("="*60)
    stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:3001/api/health || echo 'Backend unreachable'")
    print(stdout.read().decode())

    print("\n" + "="*60)
    print("2. PM2 STATUS")
    print("="*60)
    stdin, stdout, stderr = ssh.exec_command("pm2 list")
    print(stdout.read().decode())

    print("\n" + "="*60)
    print("3. PM2 LOGS (10 dernières lignes)")
    print("="*60)
    stdin, stdout, stderr = ssh.exec_command("pm2 logs crm-backend --lines 10 --nostream")
    print(stdout.read().decode())

    print("\n" + "="*60)
    print("4. NGINX CONFIG")
    print("="*60)
    stdin, stdout, stderr = ssh.exec_command("cat /etc/nginx/sites-available/crm-ehc.fr")
    print(stdout.read().decode())

    print("\n" + "="*60)
    print("5. NGINX ERROR LOGS")
    print("="*60)
    stdin, stdout, stderr = ssh.exec_command("sudo tail -20 /var/log/nginx/crm-ehc.fr_error.log", get_pty=True)
    stdin.write(VPS_PASSWORD + '\n')
    stdin.flush()
    print(stdout.read().decode())

except Exception as e:
    print(f"ERREUR: {e}")
finally:
    ssh.close()
