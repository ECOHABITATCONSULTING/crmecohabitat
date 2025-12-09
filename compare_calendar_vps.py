#!/usr/bin/env python3
"""
COMPARAISON DU FICHIER CALENDAR.JSX
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

    # Vérifier la dernière ligne du Calendar.jsx sur le VPS
    print("📄 DERNIÈRES LIGNES DE Calendar.jsx SUR LE VPS:")
    stdin, stdout, stderr = ssh.exec_command(f"tail -10 {PROJECT_DIR}/frontend/src/pages/Calendar.jsx")
    print(stdout.read().decode())

    # Vérifier si export default est présent
    print("\n🔍 RECHERCHE 'export default Calendar':")
    stdin, stdout, stderr = ssh.exec_command(f"grep -n 'export default Calendar' {PROJECT_DIR}/frontend/src/pages/Calendar.jsx")
    result = stdout.read().decode()
    print(result if result else "❌ EXPORT DEFAULT MANQUANT!")

    # Compter les lignes
    print("\n📊 NOMBRE DE LIGNES:")
    stdin, stdout, stderr = ssh.exec_command(f"wc -l {PROJECT_DIR}/frontend/src/pages/Calendar.jsx")
    print(stdout.read().decode())

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
finally:
    ssh.close()
