#!/usr/bin/env node
/**
 * Script de nettoyage de la base de données pour production
 * Usage: node clean_database.js [path_to_database]
 */

const Database = require('better-sqlite3');
const path = require('path');
const fs = require('fs');
const readline = require('readline');

// Accepter le chemin en argument ou utiliser le chemin par défaut
const DB_PATH = process.argv[2] || path.join(__dirname, 'database.db');

// Interface pour confirmation
const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

console.log('\n🧹 NETTOYAGE DE LA BASE DE DONNÉES POUR PRODUCTION');
console.log('==================================================');
console.log('\n⚠️  ATTENTION : Ce script va:');
console.log('  - Supprimer TOUS les utilisateurs sauf \'admin\'');
console.log('  - Supprimer TOUS les leads');
console.log('  - Supprimer TOUS les clients');
console.log('  - Supprimer TOUS les commentaires');
console.log('  - Supprimer TOUS les rendez-vous');
console.log('  - Supprimer TOUTES les notes de dimensionnement');
console.log('');

function question(query) {
  return new Promise(resolve => rl.question(query, resolve));
}

async function main() {
  // Vérifier que la base existe
  if (!fs.existsSync(DB_PATH)) {
    console.error('❌ Base de données introuvable:', DB_PATH);
    process.exit(1);
  }

  // Demander confirmation
  const answer = await question('Êtes-vous sûr de vouloir continuer ? (oui/non) : ');

  if (answer.toLowerCase() !== 'oui') {
    console.log('❌ Opération annulée');
    rl.close();
    process.exit(0);
  }

  rl.close();

  // Créer un backup
  const backupPath = `${DB_PATH}.backup.${Date.now()}`;
  console.log('\n📦 Création du backup:', backupPath);
  fs.copyFileSync(DB_PATH, backupPath);
  console.log('✅ Backup créé\n');

  // Ouvrir la base
  const db = new Database(DB_PATH);

  try {
    console.log('🧹 Nettoyage en cours...\n');

    // Désactiver les foreign keys temporairement
    db.pragma('foreign_keys = OFF');

    // Compter avant suppression
    const beforeCounts = {
      users: db.prepare('SELECT COUNT(*) as count FROM users').get().count,
      leads: db.prepare('SELECT COUNT(*) as count FROM leads').get().count,
      clients: db.prepare('SELECT COUNT(*) as count FROM clients').get().count,
      comments: db.prepare('SELECT COUNT(*) as count FROM comments').get().count,
      appointments: db.prepare('SELECT COUNT(*) as count FROM appointments').get().count,
    };

    console.log('📊 Avant nettoyage:');
    console.log(`  - Utilisateurs: ${beforeCounts.users}`);
    console.log(`  - Leads: ${beforeCounts.leads}`);
    console.log(`  - Clients: ${beforeCounts.clients}`);
    console.log(`  - Commentaires: ${beforeCounts.comments}`);
    console.log(`  - Rendez-vous: ${beforeCounts.appointments}\n`);

    // Supprimer dans l'ordre (à cause des foreign keys)
    db.prepare('DELETE FROM dimensioning_notes').run();
    db.prepare('DELETE FROM appointments').run();

    try {
      db.prepare('DELETE FROM client_appointments').run();
    } catch (e) {
      // Table peut ne pas exister
    }

    db.prepare('DELETE FROM comments').run();
    db.prepare('DELETE FROM client_comments').run();
    db.prepare('DELETE FROM clients').run();
    db.prepare('DELETE FROM leads').run();
    db.prepare('DELETE FROM users WHERE username != ?').run('admin');

    // Réinitialiser les compteurs auto-increment
    const tables = ['leads', 'clients', 'comments', 'client_comments', 'appointments', 'client_appointments', 'dimensioning_notes'];
    for (const table of tables) {
      db.prepare('DELETE FROM sqlite_sequence WHERE name = ?').run(table);
    }

    // Réactiver les foreign keys
    db.pragma('foreign_keys = ON');

    // Vérifications
    console.log('✅ Nettoyage terminé\n');
    console.log('=== UTILISATEURS RESTANTS ===');
    const users = db.prepare('SELECT id, username, role FROM users').all();
    users.forEach(u => console.log(`  ${u.id} | ${u.username} | ${u.role}`));

    console.log('\n=== COMPTAGE FINAL ===');
    const afterCounts = {
      users: db.prepare('SELECT COUNT(*) as count FROM users').get().count,
      leads: db.prepare('SELECT COUNT(*) as count FROM leads').get().count,
      clients: db.prepare('SELECT COUNT(*) as count FROM clients').get().count,
      comments: db.prepare('SELECT COUNT(*) as count FROM comments').get().count,
      appointments: db.prepare('SELECT COUNT(*) as count FROM appointments').get().count,
    };

    console.log(`  - Utilisateurs: ${afterCounts.users}`);
    console.log(`  - Leads: ${afterCounts.leads}`);
    console.log(`  - Clients: ${afterCounts.clients}`);
    console.log(`  - Commentaires: ${afterCounts.comments}`);
    console.log(`  - Rendez-vous: ${afterCounts.appointments}`);

    console.log('\n================================================');
    console.log('✅ BASE DE DONNÉES NETTOYÉE AVEC SUCCÈS !');
    console.log('================================================\n');
    console.log('📦 Backup disponible:', backupPath);
    console.log('\nPour restaurer le backup en cas de problème:');
    console.log(`  cp ${backupPath} ${DB_PATH}\n`);

  } catch (error) {
    console.error('\n❌ Erreur lors du nettoyage:', error.message);
    console.log('\n🔄 Restauration du backup...');
    db.close();
    fs.copyFileSync(backupPath, DB_PATH);
    console.log('✅ Backup restauré');
    process.exit(1);
  } finally {
    db.close();
  }
}

main().catch(console.error);
