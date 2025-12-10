# Guide de Déploiement - CRM Leads Papa

## Prérequis

- Accès SSH au VPS
- Fichier `.env.vps` configuré (voir ci-dessous)
- Python 3 + paramiko installé

## Configuration .env.vps

Créez un fichier `.env.vps` à la racine du projet :

```env
VPS_HOST=217.182.171.179
VPS_USER=ubuntu
VPS_PASSWORD=votre_mot_de_passe
VPS_PROJECT_DIR=/var/www/crm-ehc
```

⚠️ **Ce fichier est gitignored pour la sécurité**

## Déploiement

### Déploiement automatique (recommandé)

```bash
python3 deploy.py
```

Ce script effectue automatiquement :
1. Pull des derniers changements depuis GitHub
2. Installation des dépendances (backend + frontend)
3. Build du frontend
4. Fix des permissions
5. Redémarrage PM2
6. Reload Nginx

### Déploiement manuel

Si vous préférez déployer manuellement :

```bash
# 1. Se connecter au VPS
ssh ubuntu@217.182.171.179

# 2. Aller dans le projet
cd /var/www/crm-ehc

# 3. Pull les changements
git pull origin main

# 4. Backend
cd backend
npm install
pm2 restart crm-backend

# 5. Frontend
cd ../frontend
npm install
npm run build
sudo chown -R www-data:www-data dist/

# 6. Nginx
sudo systemctl reload nginx
```

## Ports utilisés

- **Local (dev)**
  - Frontend : 3000
  - Backend : 5001

- **Production (VPS)**
  - Frontend : 80/443 (HTTPS)
  - Backend : 3001 (proxied par Nginx)

## Vérification post-déploiement

1. Ouvrir https://crm-ehc.fr
2. Vider le cache navigateur (Ctrl+Shift+R)
3. Tester la connexion avec un compte utilisateur
4. Vérifier les logs : `pm2 logs crm-backend`

## Rollback

En cas de problème :

```bash
# Sur le VPS
cd /var/www/crm-ehc
git log --oneline -5
git checkout <commit-precedent>
pm2 restart crm-backend
cd frontend && npm run build
sudo chown -R www-data:www-data dist/
```
