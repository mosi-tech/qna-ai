module.exports = {
  apps: [{
    name: 'mcp-analytics-server',
    script: 'server.py',
    interpreter: 'python',
    cwd: '/Users/shivc/Documents/Workspace/JS/qna-ai-admin/mcp-analytics-server',
    instances: 1,
    autorestart: true,
    watch: ['analytics/', 'server.py'],
    watch_delay: 1000,
    ignore_watch: ['node_modules', '*.log', '__pycache__', '*.pyc'],
    max_memory_restart: '500M',
    env: {
      NODE_ENV: 'development'
    },
    error_file: './logs/err.log',
    out_file: './logs/out.log',
    log_file: './logs/combined.log',
    time: true,
    log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
    merge_logs: true
  }]
};