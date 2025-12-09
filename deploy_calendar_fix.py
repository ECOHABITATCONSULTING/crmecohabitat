#!/usr/bin/env python3
"""
DÉPLOIEMENT DU FIX CALENDAR
"""

import paramiko

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

print("🔧 DÉPLOIEMENT DU FIX CALENDAR\n")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté\n")

    # Pull les changements
    exec_cmd(ssh,
        f"cd {PROJECT_DIR} && git pull origin main",
        "1/5: Pull GitHub")

    # Supprimer node_modules et dist pour forcer un rebuild propre
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/frontend && rm -rf node_modules dist .vite",
        "2/5: Nettoyage")

    # Réinstaller dépendances
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/frontend && npm install",
        "3/5: npm install")

    # Rebuild
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/frontend && npm run build",
        "4/5: npm run build")

    # Vérifier le nouveau hash
    print("\n📂 Nouveau build:")
    stdin, stdout, stderr = ssh.exec_command(f"ls -lh {PROJECT_DIR}/frontend/dist/assets/index-*.js")
    print(stdout.read().decode())

    # Fix permissions et reload nginx
    exec_cmd(ssh,
        f"sudo chown -R www-data:www-data {PROJECT_DIR}/frontend/dist && sudo systemctl reload nginx",
        "5/5: Permissions + Reload Nginx")

    print("\n" + "="*60)
    print("✅ DÉPLOIEMENT TERMINÉ !")
    print("="*60)
    print("\n🌐 https://crm-ehc.fr")
    print("👤 Login: admin / admin123")
    print("\n⚠️  VIDE LE CACHE NAVIGATEUR !")
    print("   Ctrl+Shift+R (hard refresh)")
    print("   OU navigation privée: Ctrl+Shift+N")

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
