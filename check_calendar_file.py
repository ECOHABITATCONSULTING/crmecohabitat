#!/usr/bin/env python3
"""
VÉRIFICATION FICHIER CALENDAR.JSX
"""

import paramiko

VPS_HOST = '217.182.171.179'
VPS_USER = 'ubuntu'
VPS_PASSWORD = 'Pirouli2652148'
PROJECT_DIR = '/var/www/crm-ehc'

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté\n")

    # Lister les fichiers dans pages/
    print("📁 Contenu de frontend/src/pages/:")
    stdin, stdout, stderr = ssh.exec_command(f"ls -la {PROJECT_DIR}/frontend/src/pages/")
    print(stdout.read().decode())

    # Vérifier si Calendar.jsx existe
    print("\n🔍 Vérification Calendar.jsx:")
    stdin, stdout, stderr = ssh.exec_command(f"test -f {PROJECT_DIR}/frontend/src/pages/Calendar.jsx && echo 'EXISTE' || echo 'MANQUANT'")
    result = stdout.read().decode().strip()
    print(f"Calendar.jsx: {result}")

    if result == 'MANQUANT':
        print("\n❌ Le fichier Calendar.jsx est MANQUANT sur le VPS!")
        print("📤 Il faut pousser le code local vers le VPS")

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
finally:
    ssh.close()
