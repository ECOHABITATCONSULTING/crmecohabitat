#!/usr/bin/env python3
"""
VÉRIFICATION DU COMMIT SUR LE VPS
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

    # Vérifier le commit actuel
    print("📋 COMMIT ACTUEL SUR LE VPS:")
    stdin, stdout, stderr = ssh.exec_command(f"cd {PROJECT_DIR} && git log --oneline -5")
    print(stdout.read().decode())

    # Vérifier le statut git
    print("\n📊 GIT STATUS:")
    stdin, stdout, stderr = ssh.exec_command(f"cd {PROJECT_DIR} && git status")
    print(stdout.read().decode())

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
finally:
    ssh.close()
