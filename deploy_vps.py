#!/usr/bin/env python3
"""
Script de déploiement complet du CRM sur VPS
Utilise Paramiko pour se connecter et installer tout le projet
"""

import paramiko
import time
import sys

# Configuration VPS
VPS_HOST = '217.182.171.179'
VPS_USER = 'ubuntu'
VPS_PASSWORD = 'Pirouli2652148'
DOMAIN = 'crm-ehc.fr'
GIT_REPO = 'https://github.com/ECOHABITATCONSULTING/crmecohabitat.git'
PROJECT_DIR = '/var/www/crm-ehc'

def execute_command(ssh, command, description="", wait_for_output=True):
    """Execute une commande SSH et affiche le résultat"""
    print(f"\n{'='*60}")
    print(f"▶ {description if description else command}")
    print(f"{'='*60}")

    stdin, stdout, stderr = ssh.exec_command(command, get_pty=True)

    if wait_for_output:
        # Envoyer le mot de passe si nécessaire pour sudo
        if 'sudo' in command:
            stdin.write(VPS_PASSWORD + '\n')
            stdin.flush()

        # Lire la sortie en temps réel
        for line in stdout:
            print(line.strip())

        # Afficher les erreurs s'il y en a
        errors = stderr.read().decode('utf-8')
        if errors:
            print(f"⚠️  Warnings/Errors: {errors}")

    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        print(f"✅ {description if description else 'Commande'} terminée avec succès")
    else:
        print(f"❌ Erreur (code {exit_status})")

    return exit_status

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║   🚀 DÉPLOIEMENT CRM ECO HABITAT CONSULTING              ║
    ║   VPS: 217.182.171.179                                    ║
    ║   Domaine: crm-ehc.fr                                     ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Connexion SSH
    print("🔌 Connexion au VPS...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(VPS_HOST, username=VPS_USER, password=VPS_PASSWORD, timeout=10)
        print("✅ Connecté au VPS avec succès !\n")
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        sys.exit(1)

    try:
        # ÉTAPE 1: Mise à jour du système
        execute_command(ssh,
            "sudo apt update && sudo apt upgrade -y",
            "ÉTAPE 1/10: Mise à jour du système")

        # ÉTAPE 2: Installation des dépendances système
        execute_command(ssh,
            "sudo apt install -y git curl nginx certbot python3-certbot-nginx",
            "ÉTAPE 2/10: Installation Git, Nginx, Certbot")

        # ÉTAPE 3: Installation de Node.js 20.x
        execute_command(ssh,
            "curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -",
            "ÉTAPE 3/10: Ajout du repository Node.js 20")

        execute_command(ssh,
            "sudo apt install -y nodejs",
            "Installation de Node.js et npm")

        # Vérification des versions
        execute_command(ssh, "node --version", "Vérification version Node.js")
        execute_command(ssh, "npm --version", "Vérification version npm")

        # ÉTAPE 4: Installation de PM2
        execute_command(ssh,
            "sudo npm install -g pm2",
            "ÉTAPE 4/10: Installation de PM2")

        # ÉTAPE 5: Arrêt et suppression de l'ancien projet si existe
        print("\nÉTAPE 5/10: Nettoyage de l'ancien projet")
        execute_command(ssh, "pm2 delete all || true", "Arrêt des processus PM2")
        execute_command(ssh, f"sudo rm -rf {PROJECT_DIR}", "Suppression ancien répertoire")
        execute_command(ssh, "sudo mkdir -p /var/www", "Création répertoire /var/www")

        # ÉTAPE 6: Clone du projet
        execute_command(ssh,
            f"sudo git clone {GIT_REPO} {PROJECT_DIR}",
            "ÉTAPE 6/10: Clone du projet GitHub")

        execute_command(ssh,
            f"sudo chown -R {VPS_USER}:{VPS_USER} {PROJECT_DIR}",
            "Configuration des permissions")

        # ÉTAPE 7: Configuration du Backend
        print("\nÉTAPE 7/10: Configuration et installation du Backend")

        # Créer le fichier .env pour le backend
        env_content = """NODE_ENV=production
PORT=3001
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production-2024
DATABASE_PATH=./data/database.sqlite
ALLOWED_ORIGINS=https://crm-ehc.fr,http://crm-ehc.fr
"""

        execute_command(ssh,
            f"cd {PROJECT_DIR}/backend && echo '{env_content}' > .env",
            "Création du fichier .env backend")

        execute_command(ssh,
            f"cd {PROJECT_DIR}/backend && npm install --production",
            "Installation des dépendances backend")

        # Créer le répertoire data
        execute_command(ssh,
            f"mkdir -p {PROJECT_DIR}/backend/data",
            "Création du répertoire data")

        # ÉTAPE 8: Configuration du Frontend
        print("\nÉTAPE 8/10: Configuration et build du Frontend")

        # Créer le fichier .env pour le frontend
        frontend_env = """VITE_API_URL=https://crm-ehc.fr/api
"""

        execute_command(ssh,
            f"cd {PROJECT_DIR}/frontend && echo '{frontend_env}' > .env",
            "Création du fichier .env frontend")

        execute_command(ssh,
            f"cd {PROJECT_DIR}/frontend && npm install",
            "Installation des dépendances frontend")

        execute_command(ssh,
            f"cd {PROJECT_DIR}/frontend && npm run build",
            "Build du frontend React")

        # ÉTAPE 9: Configuration Nginx
        print("\nÉTAPE 9/10: Configuration Nginx")

        nginx_config = f"""server {{
    listen 80;
    server_name {DOMAIN} www.{DOMAIN};

    # Limite de taille pour upload
    client_max_body_size 10M;

    # Frontend - Servir les fichiers statiques
    location / {{
        root {PROJECT_DIR}/frontend/dist;
        try_files $uri $uri/ /index.html;

        # Cache pour les assets
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {{
            expires 1y;
            add_header Cache-Control "public, immutable";
        }}
    }}

    # Backend API
    location /api {{
        proxy_pass http://localhost:3001;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }}

    # Logs
    access_log /var/log/nginx/{DOMAIN}_access.log;
    error_log /var/log/nginx/{DOMAIN}_error.log;
}}
"""

        # Créer le fichier de configuration Nginx
        execute_command(ssh,
            f"sudo bash -c 'cat > /etc/nginx/sites-available/{DOMAIN} << \"EOF\"\n{nginx_config}\nEOF'",
            "Création de la configuration Nginx")

        # Supprimer la config par défaut et activer la nôtre
        execute_command(ssh,
            f"sudo rm -f /etc/nginx/sites-enabled/default",
            "Suppression de la config Nginx par défaut")

        execute_command(ssh,
            f"sudo ln -sf /etc/nginx/sites-available/{DOMAIN} /etc/nginx/sites-enabled/",
            "Activation de la configuration Nginx")

        # Test et reload Nginx
        execute_command(ssh,
            "sudo nginx -t",
            "Test de la configuration Nginx")

        execute_command(ssh,
            "sudo systemctl reload nginx",
            "Rechargement de Nginx")

        # ÉTAPE 10: Démarrage avec PM2
        print("\nÉTAPE 10/10: Démarrage du backend avec PM2")

        execute_command(ssh,
            f"cd {PROJECT_DIR}/backend && pm2 start src/server.js --name crm-backend",
            "Démarrage du backend")

        execute_command(ssh,
            "pm2 save",
            "Sauvegarde de la configuration PM2")

        execute_command(ssh,
            "pm2 startup",
            "Configuration du démarrage automatique")

        # Récupérer la commande de startup et l'exécuter
        stdin, stdout, stderr = ssh.exec_command("pm2 startup")
        startup_output = stdout.read().decode('utf-8')

        # Chercher la ligne de commande sudo dans la sortie
        for line in startup_output.split('\n'):
            if line.strip().startswith('sudo env'):
                print(f"\n⚙️  Exécution de la commande de startup: {line.strip()}")
                execute_command(ssh, line.strip(), "Configuration startup PM2")
                break

        execute_command(ssh,
            "pm2 list",
            "État des processus PM2")

        # BONUS: Configuration SSL avec Certbot (optionnel)
        print("\n" + "="*60)
        print("🔒 CONFIGURATION SSL (Optionnel)")
        print("="*60)
        print(f"""
Pour activer HTTPS avec Let's Encrypt, exécute cette commande depuis le VPS:

sudo certbot --nginx -d {DOMAIN} -d www.{DOMAIN}

Certbot configurera automatiquement Nginx pour HTTPS.
        """)

        # Affichage des informations finales
        print("\n" + "="*60)
        print("✅ DÉPLOIEMENT TERMINÉ AVEC SUCCÈS !")
        print("="*60)
        print(f"""
📋 RÉCAPITULATIF:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌐 URLs:
   - Frontend: http://{DOMAIN}
   - Backend API: http://{DOMAIN}/api
   - IP directe: http://{VPS_HOST}

📁 Chemins sur le serveur:
   - Projet: {PROJECT_DIR}
   - Backend: {PROJECT_DIR}/backend
   - Frontend build: {PROJECT_DIR}/frontend/dist
   - Base de données: {PROJECT_DIR}/backend/data/database.sqlite

🔧 Commandes utiles:
   - Voir les logs backend: pm2 logs crm-backend
   - Redémarrer backend: pm2 restart crm-backend
   - Arrêter backend: pm2 stop crm-backend
   - Status PM2: pm2 status
   - Logs Nginx: sudo tail -f /var/log/nginx/{DOMAIN}_*.log

🔄 Pour mettre à jour le projet:
   cd {PROJECT_DIR}
   git pull
   cd backend && npm install && pm2 restart crm-backend
   cd ../frontend && npm install && npm run build

⚠️  IMPORTANT - Première connexion:
   1. Accède à http://{DOMAIN}
   2. L'admin par défaut est créé automatiquement:
      - Username: admin
      - Password: admin123
   3. CHANGE CE MOT DE PASSE immédiatement !

🔒 Pour activer HTTPS:
   sudo certbot --nginx -d {DOMAIN} -d www.{DOMAIN}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        """)

    except Exception as e:
        print(f"\n❌ ERREUR PENDANT LE DÉPLOIEMENT: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    finally:
        ssh.close()
        print("\n🔌 Connexion SSH fermée")

if __name__ == "__main__":
    main()
