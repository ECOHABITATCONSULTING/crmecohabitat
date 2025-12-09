#!/usr/bin/env python3
"""
NETTOYAGE TOTAL + REBUILD (avec nouveau hash)
"""

import paramiko
import time

VPS_HOST = '217.182.171.179'
VPS_USER = 'ubuntu'
VPS_PASSWORD = 'Pirouli2652148'
PROJECT_DIR = '/var/www/crm-ehc'

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

print("🧹 CLEAN REBUILD FRONTEND\n")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté\n")

    # Supprimer TOUT (node_modules, dist, package-lock.json, cache npm)
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/frontend && rm -rf node_modules dist package-lock.json .vite node_modules/.cache",
        "1/6: Nettoyage total (node_modules + caches)")

    # Nettoyer le cache npm
    exec_cmd(ssh,
        "npm cache clean --force",
        "2/6: Nettoyage cache npm")

    # Réinstaller TOUT
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/frontend && npm install",
        "3/6: Réinstallation complète")

    # Rebuild avec nouveau hash
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/frontend && npm run build -- --force",
        "4/6: Build frontend (forced)")

    # Vérifier le nouveau hash
    print("\n📂 Nouveau build:")
    stdin, stdout, stderr = ssh.exec_command(f"ls -lh {PROJECT_DIR}/frontend/dist/assets/")
    print(stdout.read().decode())

    # Fix permissions
    exec_cmd(ssh,
        f"sudo chown -R www-data:www-data {PROJECT_DIR}/frontend/dist",
        "5/6: Fix permissions")

    # Reload Nginx + clear cache
    exec_cmd(ssh,
        "sudo systemctl reload nginx && sleep 1",
        "6/6: Reload Nginx")

    print("\n" + "="*60)
    print("✅ REBUILD TERMINÉ AVEC NOUVEAU HASH")
    print("="*60)
    print("\n🌐 https://crm-ehc.fr")
    print("\n⚠️  VIDE LE CACHE NAVIGATEUR (Ctrl+Shift+Delete)")
    print("   OU ouvre en navigation privée (Ctrl+Shift+N)")

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
