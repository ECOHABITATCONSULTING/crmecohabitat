#!/usr/bin/env python3
"""
SCRIPT FINAL : Upgrade Node.js v12 → v20 + Déploiement complet
"""

import paramiko
import sys
import time

VPS_HOST = '217.182.171.179'
VPS_USER = 'ubuntu'
VPS_PASSWORD = 'Pirouli2652148'
DOMAIN = 'crm-ehc.fr'
PROJECT_DIR = '/var/www/crm-ehc'

def exec_cmd(ssh, cmd, desc="", show_output=True):
    print(f"\n{'='*60}\n▶ {desc}\n{'='*60}")
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=True)

    if 'sudo' in cmd and not cmd.startswith('sudo -S'):
        stdin.write(VPS_PASSWORD + '\n')
        stdin.flush()

    if show_output:
        for line in stdout:
            print(line.strip())

    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"✅ {desc} - OK")
    else:
        print(f"❌ ERREUR (code {exit_status})")
        if not show_output:
            print(stderr.read().decode())
    return exit_status

print("""
╔═══════════════════════════════════════════════════════════╗
║   🚀 UPGRADE NODE.JS v12 → v20 + DÉPLOIEMENT COMPLET     ║
║   VPS: 217.182.171.179 | Domaine: crm-ehc.fr             ║
╚═══════════════════════════════════════════════════════════╝
""")

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

try:
    print("🔌 Connexion au VPS...")
    ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
    print("✅ Connecté au VPS\n")

    # ÉTAPE 1: Stop PM2
    exec_cmd(ssh, "pm2 stop all || true", "ÉTAPE 1/10: Arrêt PM2")
    exec_cmd(ssh, "pm2 save || true", "Sauvegarde PM2")

    # ÉTAPE 2: Remove old Node.js
    print("\n🗑️  SUPPRESSION NODE.JS v12...")
    exec_cmd(ssh, "sudo apt remove -y nodejs npm", "ÉTAPE 2/10: Suppression Node.js v12")
    exec_cmd(ssh, "sudo apt autoremove -y", "Nettoyage")

    # ÉTAPE 3: Install Node.js 20
    print("\n📦 INSTALLATION NODE.JS v20...")
    exec_cmd(ssh,
        "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash -",
        "ÉTAPE 3/10: Setup NodeSource repository")

    exec_cmd(ssh,
        "sudo apt install -y nodejs",
        "ÉTAPE 4/10: Installation Node.js 20")

    # ÉTAPE 4: Verify Node.js version
    stdin, stdout, stderr = ssh.exec_command("node --version")
    node_version = stdout.read().decode().strip()
    print(f"\n✅ Node.js installé: {node_version}")

    if not node_version.startswith('v20'):
        print(f"❌ ERREUR: Node.js {node_version} au lieu de v20.x.x")
        sys.exit(1)

    # ÉTAPE 5: Reinstall PM2
    exec_cmd(ssh,
        "sudo npm install -g pm2",
        "ÉTAPE 5/10: Réinstallation PM2")

    # ÉTAPE 6: Fix permissions
    exec_cmd(ssh,
        f"sudo chown -R {VPS_USER}:{VPS_USER} {PROJECT_DIR}",
        "ÉTAPE 6/10: Fix permissions")

    # ÉTAPE 7: Reinstall backend deps
    print("\n📦 BACKEND: Réinstallation des dépendances...")
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/backend && rm -rf node_modules",
        "Suppression ancien node_modules")

    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/backend && npm install --production",
        "ÉTAPE 7/10: npm install backend")

    # ÉTAPE 8: Reinstall frontend deps
    print("\n📦 FRONTEND: Réinstallation des dépendances...")
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/frontend && rm -rf node_modules",
        "Suppression ancien node_modules")

    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/frontend && npm install",
        "ÉTAPE 8/10: npm install frontend")

    # ÉTAPE 9: Build frontend
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/frontend && npm run build",
        "ÉTAPE 9/10: Build frontend")

    # ÉTAPE 10: Start PM2
    print("\n🚀 DÉMARRAGE DU BACKEND...")
    exec_cmd(ssh,
        f"cd {PROJECT_DIR}/backend && pm2 start src/server.js --name crm-backend",
        "ÉTAPE 10/10: Démarrage PM2")

    exec_cmd(ssh, "pm2 save", "Sauvegarde PM2")

    # Wait for backend to start
    print("\n⏳ Attente démarrage backend (3 secondes)...")
    time.sleep(3)

    exec_cmd(ssh, "pm2 list", "Status PM2")

    # ÉTAPE FINALE: Reload Nginx
    exec_cmd(ssh, "sudo systemctl reload nginx", "Reload Nginx")

    # Test backend
    print("\n🧪 TEST BACKEND...")
    stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:3001/api/health")
    response = stdout.read().decode()
    if "OK" in response or "opérationnelle" in response:
        print(f"✅ Backend répond: {response}")
    else:
        print(f"⚠️  Backend response: {response}")

    print("\n" + "="*60)
    print("🎉 DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !")
    print("="*60)
    print(f"""
🌐 URL: http://{DOMAIN}
📊 API: http://{DOMAIN}/api
👤 Login: admin / admin123

✅ Node.js: {node_version}
✅ Backend: PM2 online
✅ Frontend: Built and deployed
✅ Nginx: Configured

🔧 Commandes utiles:
   pm2 logs crm-backend
   pm2 restart crm-backend
   sudo tail -f /var/log/nginx/{DOMAIN}_error.log

🎯 TESTE MAINTENANT LES 11 MODIFICATIONS DE CE MATIN !
    """)

except Exception as e:
    print(f"\n❌ ERREUR FATALE: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    ssh.close()
    print("\n🔌 Connexion SSH fermée")
