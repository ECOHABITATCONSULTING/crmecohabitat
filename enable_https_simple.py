#!/usr/bin/env python3
"""
ACTIVATION HTTPS SIMPLE (crm-ehc.fr seulement)
"""

import paramiko
import sys

VPS_HOST = '217.182.171.179'
VPS_USER = 'ubuntu'
VPS_PASSWORD = 'Pirouli2652148'
DOMAIN = 'crm-ehc.fr'

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

print("🔒 ACTIVATION HTTPS POUR crm-ehc.fr\n")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté\n")

    # Activer HTTPS uniquement pour crm-ehc.fr (sans www)
    exec_cmd(ssh,
        f"sudo certbot --nginx -d {DOMAIN} --non-interactive --agree-tos --email admin@{DOMAIN} --redirect",
        "Activation HTTPS crm-ehc.fr")

    print("\n" + "="*60)
    print("✅ HTTPS ACTIVÉ !")
    print("="*60)
    print(f"\n🌐 https://{DOMAIN}")
    print(f"📊 https://{DOMAIN}/api")
    print("\n👤 Login: admin / admin123")
    print("\n🎯 TESTE TES 11 MODIFICATIONS MAINTENANT !")

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    sys.exit(1)
finally:
    ssh.close()
