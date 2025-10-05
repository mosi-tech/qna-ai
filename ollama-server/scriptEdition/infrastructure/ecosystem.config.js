// Load environment variables from .env file in same directory
require('dotenv').config({ path: __dirname + '/.env' });

module.exports = {
  apps: [
    {
      name: 'ollama-script-server',
      script: 'python3',
      args: '../apiServer/server.py',
      cwd: '/Users/shivc/Documents/Workspace/JS/qna-ai-admin/ollama-server/scriptEdition',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development',
        PORT: 8010,
        // Choose your LLM provider: 'anthropic' or 'ollama'
        LLM_PROVIDER: process.env.LLM_PROVIDER || 'anthropic',
        
        // Anthropic settings (when LLM_PROVIDER=anthropic)
        ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY || '',
        ANTHROPIC_MODEL: process.env.ANTHROPIC_MODEL || "claude-3-5-haiku-20241022",
        
        // Ollama settings (when LLM_PROVIDER=ollama)
        OLLAMA_BASE_URL: process.env.OLLAMA_BASE_URL || 'http://localhost:11434',
        OLLAMA_MODEL: process.env.OLLAMA_MODEL || 'qwen3:0.6b'
      },
      error_file: './logs/err.log',
      out_file: './logs/out.log',
      log_file: './logs/combined.log',
      time: true,
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },
    {
      name: 'script-execution-server',
      script: 'python3',
      args: 'http_script_execution_server.py',
      cwd: '/Users/shivc/Documents/Workspace/JS/qna-ai-admin/ollama-server/scriptEdition/executionServer',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development',
        PORT: 8013
      },
      error_file: './logs/err.log',
      out_file: './logs/out.log',
      log_file: './logs/combined.log',
      time: true,
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};