#!/usr/bin/env python3
"""
DEBUG NGINX
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

    # Nginx error log
    print("📋 Nginx Error Log (dernières 50 lignes):")
    stdin, stdout, stderr = ssh.exec_command("sudo tail -50 /var/log/nginx/crm-ehc.fr_error.log")
    stdin.write(VPS_PASSWORD + '\n')
    stdin.flush()
    errors = stdout.read().decode()
    if errors.strip():
        print(errors)
    else:
        print("✅ Aucune erreur")

    # Nginx access log
    print("\n📋 Nginx Access Log (dernières 20 lignes):")
    stdin, stdout, stderr = ssh.exec_command("sudo tail -20 /var/log/nginx/crm-ehc.fr_access.log")
    stdin.write(VPS_PASSWORD + '\n')
    stdin.flush()
    print(stdout.read().decode())

    # Test depuis le VPS vers API via HTTPS
    print("\n📊 Test depuis VPS:")
    stdin, stdout, stderr = ssh.exec_command("curl -k -s https://localhost/api/health")
    print(stdout.read().decode())

    # Check if backend is listening
    print("\n📊 Backend listening:")
    stdin, stdout, stderr = ssh.exec_command("sudo netstat -tlnp | grep 3001")
    stdin.write(VPS_PASSWORD + '\n')
    stdin.flush()
    print(stdout.read().decode())

    # Check Nginx is listening
    print("\n📊 Nginx listening:")
    stdin, stdout, stderr = ssh.exec_command("sudo netstat -tlnp | grep nginx")
    stdin.write(VPS_PASSWORD + '\n')
    stdin.flush()
    print(stdout.read().decode())

    # PM2 status
    print("\n📊 PM2 Status:")
    stdin, stdout, stderr = ssh.exec_command("pm2 list")
    print(stdout.read().decode())

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
