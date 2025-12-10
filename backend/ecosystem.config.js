module.exports = {
  apps: [{
    name: 'crm-backend',
    script: './server.js',
    instances: 2,              // CHANGÉ: 2 instances pour zero-downtime
    exec_mode: 'cluster',      // CHANGÉ: cluster mode au lieu de fork

    // Performance optimizations
    max_memory_restart: '500M',
    max_restarts: 10,
    min_uptime: '10s',
    restart_delay: 4000,
    kill_timeout: 10000,       // CHANGÉ: 10s pour graceful shutdown

    // Logging
    error_file: '/home/ubuntu/.pm2/logs/crm-backend-error.log',
    out_file: '/home/ubuntu/.pm2/logs/crm-backend-out.log',
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',

    // Environment
    env: {
      NODE_ENV: 'production',
      PORT: 3001
    },

    // Auto-restart on file changes (disabled in production)
    watch: false,

    // Graceful shutdown - CRITIQUE pour cluster mode
    wait_ready: true,          // AJOUTÉ: attend signal 'ready' avant de considérer l'app démarrée
    listen_timeout: 3000,      // Timeout pour écouter le port
    shutdown_with_message: false,

    // Exponential backoff restart delay
    exp_backoff_restart_delay: 100,

    // Advanced PM2 features
    autorestart: true,
    cron_restart: '0 3 * * *', // Restart every day at 3am

    // Node.js args
    node_args: '--max-old-space-size=512'
  }]
};
