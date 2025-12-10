module.exports = {
  apps: [{
    name: 'crm-backend',
    script: './server.js',
    instances: 1,
    exec_mode: 'fork',

    // Performance optimizations
    max_memory_restart: '500M',
    max_restarts: 10,
    min_uptime: '10s',
    restart_delay: 4000,
    kill_timeout: 5000,

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

    // Graceful shutdown
    listen_timeout: 3000,
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
