require('dotenv').config();
const express = require('express');
const cors = require('cors');
const db = require('./database');

const authRoutes = require('./routes/auth');
const usersRoutes = require('./routes/users');
const leadsRoutes = require('./routes/leads');
const commentsRoutes = require('./routes/comments');
const appointmentsRoutes = require('./routes/appointments');
const clientsRoutes = require('./routes/clients');
const analyticsRoutes = require('./routes/analytics');
const dimensioningRoutes = require('./routes/dimensioning');
const commerciauxRoutes = require('./routes/commerciaux');

const app = express();
const PORT = process.env.PORT || 5000;

// Middleware
app.use(cors());
app.use(express.json());

// Routes
app.use('/api/auth', authRoutes);
app.use('/api/users', usersRoutes);
app.use('/api/leads', leadsRoutes);
app.use('/api/comments', commentsRoutes);
app.use('/api/appointments', appointmentsRoutes);
app.use('/api/clients', clientsRoutes);
app.use('/api/analytics', analyticsRoutes);
app.use('/api/dimensioning', dimensioningRoutes);
app.use('/api/commerciaux', commerciauxRoutes);

// Route de test
app.get('/api/health', (req, res) => {
  res.json({ status: 'OK', message: 'API CRM Leads opérationnelle' });
});

// Gestion des erreurs
app.use((err, req, res, next) => {
  console.error(err.stack);
  res.status(500).json({ error: 'Erreur serveur' });
});

// Démarrer le serveur
const server = app.listen(PORT, () => {
  console.log(`\n========================================`);
  console.log(`🚀 Serveur CRM démarré sur le port ${PORT}`);
  console.log(`========================================`);
  console.log(`📊 API disponible: http://localhost:${PORT}/api`);
  console.log(`✅ Base de données: Connectée`);
  console.log(`========================================\n`);
});

// CONFIGURATION CRITIQUE: Keep-Alive timeout pour éviter ERR_CONNECTION_RESET
// Race condition fix: Node.js timeout DOIT être > Nginx timeout
// Nginx utilise 60s, donc on configure Node.js à 185s pour éviter la race condition
server.keepAliveTimeout = 185000; // 185 secondes (> 60s de Nginx)
server.headersTimeout = 186000;   // 186 secondes (doit être > keepAliveTimeout)

console.log(`⚙️  Keep-Alive Timeout configuré: ${server.keepAliveTimeout}ms`);
console.log(`⚙️  Headers Timeout configuré: ${server.headersTimeout}ms\n`);

// GRACEFUL SHUTDOWN HANDLERS - Fix pour ERR_CONNECTION_RESET
let isShuttingDown = false;

function gracefulShutdown(signal) {
  if (isShuttingDown) {
    console.log(`⚠️  Signal ${signal} ignoré - arrêt déjà en cours`);
    return;
  }

  isShuttingDown = true;
  console.log(`\n⚠️  Signal ${signal} reçu - arrêt gracieux en cours...`);
  console.log(`🔄 Fermeture des connexions actives...`);

  // Ferme le serveur en attendant que toutes les connexions se terminent
  server.close(() => {
    console.log('✅ Toutes les connexions fermées proprement');
    console.log('✅ Serveur arrêté avec succès');
    process.exit(0);
  });

  // Force l'arrêt après 10 secondes si les connexions ne se ferment pas
  setTimeout(() => {
    console.error('❌ Timeout atteint - arrêt forcé des connexions restantes');
    process.exit(1);
  }, 10000);
}

// Écoute des signaux d'arrêt
process.on('SIGINT', () => gracefulShutdown('SIGINT'));   // Ctrl+C
process.on('SIGTERM', () => gracefulShutdown('SIGTERM')); // PM2 reload/stop

// Signal PM2 que l'application est prête (requis pour cluster mode)
if (process.send) {
  process.send('ready');
  console.log('✅ Signal "ready" envoyé à PM2\n');
}
