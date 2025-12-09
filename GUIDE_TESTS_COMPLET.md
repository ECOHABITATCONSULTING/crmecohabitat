# GUIDE DE TEST COMPLET - 11 MODIFICATIONS
**URL**: https://crm-ehc.fr
**Login**: admin / admin123
**Date**: 2025-12-09

---

## TEST 1: SYSTÈME COMMERCIAUX (15 min)

### Objectif
Vérifier le CRUD complet des commerciaux avec sélecteur de couleur

### Étapes

1. **Accès**
   - Connexion → Menu latéral → **Paramètres** → **Commerciaux**
   - ✅ La page s'affiche sans erreur console

2. **Création**
   - Cliquer **"+ Nouveau Commercial"**
   - Nom: `Sophie Martin`
   - Cliquer sur le carré de couleur → Choisir bleu `#3b82f6`
   - Cliquer **"Créer"**
   - ✅ Commercial apparaît dans la liste avec badge de couleur bleu

3. **Modification**
   - Cliquer **"Modifier"** sur Sophie Martin
   - Changer la couleur → Vert `#10b981`
   - Cliquer **"Enregistrer"**
   - ✅ Couleur mise à jour instantanément

4. **Création d'un 2ème commercial**
   - Créer `Marc Dubois` avec couleur orange `#f59e0b`
   - ✅ 2 commerciaux visibles dans la liste

5. **Tentative de suppression**
   - Cliquer **"Supprimer"** sur Sophie Martin
   - ✅ Confirmation demandée
   - Confirmer
   - ✅ Commercial supprimé (si aucun RDV assigné)

### Validation
- ✅ CRUD complet fonctionne
- ✅ Sélecteur de couleur type `<input type="color">` fonctionne
- ✅ Couleurs affichées correctement dans les badges
- ✅ Messages d'erreur si tentative de suppression avec RDV assignés

---

## TEST 2: IMPORT CSV ÉTENDU (10 min)

### Objectif
Vérifier l'import CSV avec les 9 champs (4 obligatoires + 5 optionnels)

### Préparation
Créer un fichier `test_leads.csv` :
```csv
first_name,last_name,email,phone,mobile_phone,address,postal_code,city,country
Jean,Dupont,jean.dupont@test.fr,0123456789,0612345678,123 Rue de Test,75001,Paris,France
Marie,Martin,marie.martin@test.fr,0145678901,0698765432,456 Avenue Test,69001,Lyon,France
Pierre,Bernard,pierre.bernard@test.fr,0198765432,,,,,
Sophie,Petit,,,0687654321,789 Boulevard Test,13001,Marseille,France
```

### Étapes

1. **Télécharger le template**
   - Aller sur **Leads** → Cliquer **"Importer CSV"**
   - Cliquer **"Télécharger template CSV"**
   - ✅ Fichier téléchargé contient les 9 colonnes

2. **Import du fichier test**
   - Cliquer **"Choisir fichier"** → Sélectionner `test_leads.csv`
   - Cliquer **"Importer"**
   - ✅ Message de succès: "4 leads importés"

3. **Vérification des données**
   - Dans la liste des leads, cliquer sur **Jean Dupont**
   - ✅ Tous les champs remplis:
     - Téléphone fixe: 0123456789
     - Téléphone mobile: 0612345678
     - Adresse complète: 123 Rue de Test
     - Code postal: 75001
     - Ville: Paris
     - Pays: France

4. **Vérification champs optionnels**
   - Cliquer sur **Pierre Bernard**
   - ✅ Seuls prénom, nom, email, phone remplis (autres vides)

5. **Test validation**
   - Créer un CSV sans `first_name`
   - Tenter import
   - ✅ Message d'erreur: "Colonnes manquantes: first_name"

### Validation
- ✅ Import avec 9 champs fonctionne
- ✅ Champs obligatoires: first_name, last_name, email, phone
- ✅ Champs optionnels: mobile_phone, address, postal_code, city, country
- ✅ Template téléchargeable contient toutes les colonnes

---

## TEST 3: CALENDRIER + ATTRIBUTION COMMERCIAL (20 min)

### Objectif
Vérifier l'attribution des commerciaux aux RDV, les couleurs, filtres et drag-drop

### Étapes

1. **Création RDV avec commercial**
   - Aller sur **Agenda**
   - Cliquer **"+ Nouveau RDV"**
   - Titre: `RDV Sophie Test`
   - Date: Demain
   - Heure: 14:00
   - Lead/Client: Sélectionner un lead existant
   - **Commercial**: Sélectionner `Marc Dubois` (orange)
   - Cliquer **"Créer"**
   - ✅ RDV apparaît sur le calendrier avec **couleur orange** de Marc

2. **Création RDV sans commercial**
   - Créer un 2ème RDV
   - Ne pas assigner de commercial
   - ✅ RDV apparaît avec **couleur grise par défaut**

3. **Filtre par commercial**
   - En haut du calendrier, dropdown **"Filtrer par commercial"**
   - Sélectionner **"Marc Dubois"**
   - ✅ Seuls les RDV de Marc visibles (orange)
   - Sélectionner **"Tous"**
   - ✅ Tous les RDV réapparaissent

4. **Horaires étendus 8h-22h**
   - Scroller le calendrier
   - ✅ Plage horaire affichée: 08:00 → 22:00 (pas 9h-18h)

5. **Drag & Drop**
   - Glisser-déposer un RDV vers un autre jour/heure
   - ✅ RDV se déplace
   - Rafraîchir la page
   - ✅ Changement sauvegardé

6. **Modification RDV**
   - Cliquer sur un RDV dans le calendrier
   - Changer le commercial assigné
   - ✅ Couleur du RDV change instantanément

### Validation
- ✅ Dropdown commercial dans formulaire RDV
- ✅ Couleurs des RDV selon commercial assigné
- ✅ Filtre par commercial fonctionne
- ✅ Horaires 8h-22h (pas 9h-18h)
- ✅ Drag & Drop sauvegarde les changements
- ✅ RDV sans commercial = gris par défaut

---

## TEST 4: RDV PRIS + AUTO-STATUS (15 min)

### Objectif
Vérifier la checkbox "RDV pris" et la mise à jour automatique du statut

### Étapes

1. **Créer un client test**
   - Aller sur **Clients** → **"+ Nouveau Client"**
   - Prénom: `Test RDV`
   - Nom: `Pris`
   - Email: `test@rdv.fr`
   - Téléphone: 0123456789
   - Statut: **Contacté**
   - ✅ Client créé avec statut "Contacté"

2. **Cocher "RDV pris"**
   - Cliquer sur le client **Test RDV Pris**
   - Onglet **"Informations"**
   - ✅ Checkbox **"RDV pris"** visible en dessous du statut
   - Cocher la checkbox
   - ✅ Badge du statut passe automatiquement à **"RDV Pris"** (orange)

3. **Décocher "RDV pris"**
   - Décocher la checkbox
   - ✅ Statut reste "RDV Pris" (ne redescend PAS)
   - ✅ Checkbox décochée

4. **Progression normale du statut**
   - Changer manuellement le statut → **"Devis Envoyé"**
   - ✅ Statut passe à "Devis Envoyé"
   - ✅ Checkbox "RDV pris" reste décochée

5. **Test sur lead converti**
   - Créer un lead avec statut initial
   - Le convertir en client
   - Cocher "RDV pris"
   - ✅ Fonctionne également sur clients convertis

### Validation
- ✅ Checkbox "RDV pris" visible dans modal client
- ✅ Cocher → statut passe automatiquement à "rdv_pris"
- ✅ Décocher → statut ne change pas (reste rdv_pris)
- ✅ Logique: checkbox sert juste à faire passer à rdv_pris
- ✅ Progression du statut continue normalement après

---

## TEST 5: PERMISSIONS AGENTS (10 min)

### Objectif
Vérifier que les agents voient tout mais ne modifient que leurs propres leads/clients

### Étapes

1. **Créer un utilisateur agent**
   - Se connecter en **admin**
   - Aller sur **Paramètres** → **Utilisateurs**
   - Cliquer **"+ Nouvel Utilisateur"**
   - Username: `agent_test`
   - Password: `test123`
   - Rôle: **Agent**
   - ✅ Agent créé

2. **Créer des données en admin**
   - Créer un lead: `Lead Admin`
   - Créer un client: `Client Admin`
   - Se déconnecter

3. **Connexion en agent**
   - Login: `agent_test` / `test123`
   - ✅ Connexion réussie

4. **Vérifier accès lecture**
   - Aller sur **Leads**
   - ✅ `Lead Admin` visible dans la liste
   - Aller sur **Clients**
   - ✅ `Client Admin` visible

5. **Tenter modification lead admin**
   - Cliquer sur `Lead Admin`
   - Tenter de modifier le nom
   - Cliquer **"Enregistrer"**
   - ✅ Erreur: "Non autorisé" ou modification refusée

6. **Créer son propre lead**
   - Créer un lead: `Lead Agent Test`
   - ✅ Lead créé
   - Modifier ce lead
   - ✅ Modification autorisée

7. **Vérifier restrictions menu**
   - ✅ Menu **"Commerciaux"** NON visible (admin only)
   - ✅ Menu **"Utilisateurs"** NON visible (admin only)
   - ✅ Menus disponibles: Dashboard, Leads, Clients, Agenda

### Validation
- ✅ Agents voient tous les leads/clients (lecture globale)
- ✅ Agents ne peuvent modifier QUE leurs propres créations
- ✅ Pas d'accès aux menus admin (Commerciaux, Utilisateurs)
- ✅ Messages d'erreur clairs si tentative modification non autorisée

---

## TEST 6: ANALYTICS + RDV PRIS (10 min)

### Objectif
Vérifier que la métrique "RDV Pris" apparaît partout (dashboard, funnel, export)

### Étapes

1. **Dashboard - Cartes de métriques**
   - Se connecter en **admin**
   - Aller sur **Dashboard**
   - ✅ 4 cartes visibles:
     - Total Leads (bleu)
     - Total Clients (vert)
     - **RDV Pris** (orange) ← NOUVELLE MÉTRIQUE
     - Perdus (rouge)
   - ✅ Nombre de RDV Pris = nombre de clients avec statut "rdv_pris"

2. **Funnel de conversion**
   - Scroller vers le bas du dashboard
   - ✅ Graphique en entonnoir visible
   - ✅ Étapes affichées:
     1. Leads
     2. Contactés
     3. **RDV Pris** ← NOUVELLE ÉTAPE
     4. Devis Envoyé
     5. Clients (Gagnés)
   - ✅ Nombres cohérents avec les données

3. **Filtre période**
   - Changer le filtre de période: **"Ce mois"** → **"Cette semaine"**
   - ✅ Métriques se mettent à jour
   - ✅ RDV Pris compte uniquement ceux de la semaine

4. **Export Excel**
   - Cliquer sur **"Exporter en Excel"**
   - Ouvrir le fichier téléchargé
   - ✅ Feuille "Statistiques" contient la ligne **"RDV Pris"**
   - ✅ Feuille "Leads" avec toutes les colonnes
   - ✅ Feuille "Clients" avec colonne `rdv_pris` (0 ou 1)

5. **Performance agents**
   - Section "Performance par agent"
   - ✅ Colonne **"RDV Pris"** visible pour chaque agent
   - ✅ Total = somme des RDV pris de tous les agents

### Validation
- ✅ Carte "RDV Pris" sur dashboard (orange, icône calendrier)
- ✅ Étape "RDV Pris" dans le funnel de conversion
- ✅ Filtre période affecte le comptage RDV Pris
- ✅ Export Excel inclut métrique RDV Pris
- ✅ Performance agents inclut colonne RDV Pris

---

## TEST 7: COHÉRENCE DESIGN & RESPONSIVE (10 min)

### Objectif
Vérifier que le design est cohérent, français, et responsive

### Étapes

1. **Console navigateur**
   - Ouvrir DevTools (F12)
   - Onglet **Console**
   - Naviguer sur toutes les pages
   - ✅ Aucune erreur rouge
   - ✅ Aucun warning "Calendar is not defined"

2. **Textes en français**
   - Parcourir:
     - Dashboard
     - Leads
     - Clients
     - Agenda
     - Paramètres
   - ✅ Tous les textes en français
   - ✅ Pas de textes en anglais (sauf URLs API)

3. **Responsive - Mobile**
   - DevTools → Toggle device toolbar (Ctrl+Shift+M)
   - Sélectionner **"iPhone 12 Pro"**
   - ✅ Menu latéral se transforme en hamburger
   - ✅ Tableaux scrollables horizontalement
   - ✅ Formulaires adaptés (pleine largeur)
   - ✅ Calendrier responsive (vue jour sur mobile)

4. **Responsive - Tablette**
   - Sélectionner **"iPad"**
   - ✅ Layout adapté (colonnes)
   - ✅ Navigation fluide

5. **Couleurs commerciaux cohérentes**
   - Créer un RDV avec commercial "Marc Dubois" (orange)
   - ✅ Badge commercial orange dans la liste des RDV
   - ✅ Événement calendrier orange
   - ✅ Dropdown commercial montre la couleur

6. **Icônes lucide-react**
   - Vérifier toutes les pages
   - ✅ Icône **Calendrier** (agenda) s'affiche correctement
   - ✅ Pas d'icônes manquantes ou cassées
   - ✅ Toutes les icônes lucide-react chargées

### Validation
- ✅ Aucune erreur console
- ✅ Textes 100% français
- ✅ Responsive mobile/tablette fonctionne
- ✅ Couleurs commerciaux cohérentes partout
- ✅ Icônes lucide-react correctes (dont CalendarIcon)
- ✅ UX fluide et professionnelle

---

## RÉCAPITULATIF FINAL

### Modifications testées (11 au total)

| # | Modification | Statut |
|---|--------------|--------|
| 1 | Système Commerciaux (CRUD + couleurs) | ⬜ À tester |
| 2 | Import CSV étendu (9 champs) | ⬜ À tester |
| 3 | Attribution commercial aux RDV | ⬜ À tester |
| 4 | RDV Pris (checkbox + auto-status) | ⬜ À tester |
| 5 | Consolidation table appointments | ⬜ Testé (implicite) |
| 6 | Permissions agents (voir tout, modifier sien) | ⬜ À tester |
| 7 | Champs étendus leads (5 nouveaux) | ⬜ À tester |
| 8 | Horaires calendrier 8h-22h | ⬜ À tester |
| 9 | Filtre commercial calendrier | ⬜ À tester |
| 10 | Analytics RDV Pris (dashboard + export) | ⬜ À tester |
| 11 | Fix Calendar/CalendarIcon (lucide-react) | ⬜ À tester |

### Commandes de vérification

```bash
# Vérifier backend logs
ssh ubuntu@217.182.171.179
pm2 logs crm-backend --lines 50

# Vérifier base de données
cd /var/www/crm-ehc/backend
sqlite3 crm.db "SELECT COUNT(*) FROM commerciaux;"
sqlite3 crm.db "PRAGMA table_info(clients);" | grep rdv_pris
sqlite3 crm.db "PRAGMA table_info(appointments);" | grep commercial_id

# Vérifier Nginx logs
sudo tail -f /var/log/nginx/crm-ehc.fr_access.log
```

---

## CONCLUSION

Une fois tous les tests effectués, marquer les cases ✅ et signaler les bugs éventuels.

**Temps total estimé**: ~1h30
**Ordre recommandé**: 1 → 2 → 3 → 4 → 6 → 7 → 5
**Priorité haute**: Tests 1, 3, 4 (fonctionnalités client principales)
