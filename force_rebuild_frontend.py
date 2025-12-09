#!/usr/bin/env python3
"""
FORCE REBUILD FRONTEND (avec nettoyage complet)
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

print("🔨 FORCE REBUILD FRONTEND\n")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté\n")

    # Vérifier le contenu actuel du dossier frontend
    print("📁 Vérification dossier frontend:")
    stdin, stdout, stderr = ssh.exec_command(f"ls -la {PROJECT_DIR}/frontend/")
    print(stdout.read().decode())

    # Supprimer TOUT (node_modules, dist, .vite cache)
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/frontend && rm -rf node_modules dist .vite",
        "1/5: Nettoyage complet")

    # Vérifier le fichier .env
    print("\n📝 Vérification .env:")
    stdin, stdout, stderr = ssh.exec_command(f"cat {PROJECT_DIR}/frontend/.env")
    env_content = stdout.read().decode()
    print(env_content if env_content else "❌ .env manquant")

    if not env_content:
        exec_cmd(ssh,
            f"echo 'VITE_API_URL=https://crm-ehc.fr/api' > {PROJECT_DIR}/frontend/.env",
            "Création .env")

    # Installer dépendances
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/frontend && npm install",
        "2/5: npm install")

    # Build avec verbose
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/frontend && npm run build",
        "3/5: npm run build")

    # Vérifier que dist/ existe
    print("\n📂 Vérification dist/:")
    stdin, stdout, stderr = ssh.exec_command(f"ls -lh {PROJECT_DIR}/frontend/dist/")
    print(stdout.read().decode())

    # Vérifier les permissions
    exec_cmd(ssh,
        f"sudo chown -R www-data:www-data {PROJECT_DIR}/frontend/dist",
        "4/5: Fix permissions")

    # Reload Nginx avec cache clear
    exec_cmd(ssh,
        "sudo systemctl reload nginx",
        "5/5: Reload Nginx")

    print("\n" + "="*60)
    print("✅ FRONTEND REBUILD TERMINÉ")
    print("="*60)
    print("\n🌐 https://crm-ehc.fr")
    print("\n⚠️  IMPORTANT: Vide le cache de ton navigateur:")
    print("   - Chrome/Edge: Ctrl+Shift+Delete")
    print("   - Firefox: Ctrl+Shift+Delete")
    print("   - Ou ouvre en navigation privée: Ctrl+Shift+N")

except Exception as e:
    print(f"\n❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()
finally:
    ssh.close()
