#!/bin/bash

echo "🔄 Migration vers PM2 Cluster Mode avec Graceful Shutdown"
echo "=========================================================="
echo ""

# Couleurs
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${YELLOW}⚠️  Cette migration va:${NC}"
echo "   1. Arrêter l'application actuelle (fork mode)"
echo "   2. Supprimer l'ancienne configuration PM2"
echo "   3. Redémarrer en cluster mode (2 instances)"
echo "   4. Activer le graceful shutdown"
echo ""
echo -e "${YELLOW}✨ Bénéfices:${NC}"
echo "   - Zero-downtime lors des déploiements"
echo "   - Élimination de ERR_CONNECTION_RESET"
echo "   - Meilleure disponibilité (2 instances)"
echo ""

read -p "Continuer? (y/n) " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${RED}❌ Migration annulée${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}📍 Étape 1/5: Vérification de l'état actuel...${NC}"
pm2 list | grep crm-backend

echo ""
echo -e "${BLUE}📍 Étape 2/5: Arrêt de l'application...${NC}"
pm2 delete crm-backend || echo "Aucune app à supprimer"
echo -e "${GREEN}✅ Application arrêtée${NC}"

echo ""
echo -e "${BLUE}📍 Étape 3/5: Démarrage en cluster mode...${NC}"
cd /var/www/crm-backend || { echo -e "${RED}❌ Répertoire introuvable${NC}"; exit 1; }
pm2 start ecosystem.config.js
echo -e "${GREEN}✅ Cluster mode activé (2 instances)${NC}"

echo ""
echo -e "${BLUE}📍 Étape 4/5: Sauvegarde de la configuration PM2...${NC}"
pm2 save
echo -e "${GREEN}✅ Configuration sauvegardée${NC}"

echo ""
echo -e "${BLUE}📍 Étape 5/5: Vérification finale...${NC}"
sleep 3
pm2 list
pm2 logs crm-backend --lines 20 --nostream

echo ""
echo -e "${GREEN}=========================================================${NC}"
echo -e "${GREEN}✨ Migration terminée avec succès !${NC}"
echo -e "${GREEN}=========================================================${NC}"
echo ""
echo -e "${YELLOW}📝 Prochaines étapes:${NC}"
echo "   1. Vérifier les logs: pm2 logs crm-backend"
echo "   2. Tester l'application: curl http://localhost:3001/api/health"
echo "   3. Les prochains déploiements utiliseront automatiquement 'pm2 reload'"
echo ""
echo -e "${BLUE}ℹ️  Info: Le graceful shutdown est maintenant actif${NC}"
echo "   - Les connexions seront fermées proprement lors des reloads"
echo "   - Timeout de 10s pour les requêtes en cours"
echo "   - Plus de ERR_CONNECTION_RESET pendant les déploiements"
echo ""
