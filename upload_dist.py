#!/usr/bin/env python3
"""Upload du dossier dist/ vers le VPS"""

import paramiko
import os
from scp import SCPClient

VPS_HOST = '217.182.171.179'
VPS_USER = 'ubuntu'
VPS_PASSWORD = 'Pirouli2652148'

print("📦 Upload frontend dist/ vers VPS...")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté au VPS")

    # Supprimer ancien dist/
    stdin, stdout, stderr = ssh.exec_command("rm -rf /var/www/crm-ehc/frontend/dist")
    stdout.channel.recv_exit_status()
    print("✅ Ancien dist/ supprimé")

    # Upload avec SCP
    scp = SCPClient(ssh.get_transport())
    scp.put('/home/jokyjokeai/Desktop/Archive/crm-leads-papa/frontend/dist',
            remote_path='/var/www/crm-ehc/frontend/',
            recursive=True)
    scp.close()
    print("✅ dist/ uploadé avec succès")

    # Reload nginx
    stdin, stdout, stderr = ssh.exec_command("sudo systemctl reload nginx", get_pty=True)
    stdin.write(VPS_PASSWORD + '\n')
    stdin.flush()
    stdout.channel.recv_exit_status()
    print("✅ Nginx rechargé")

    print("\n" + "="*60)
    print("✅ FRONTEND DÉPLOYÉ !")
    print("="*60)
    print("\n🌐 Teste maintenant : http://crm-ehc.fr")
    print("👤 Login: admin / admin123\n")

except Exception as e:
    print(f"❌ ERREUR: {e}")
finally:
    ssh.close()
