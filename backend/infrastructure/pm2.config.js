// Load environment variables from .env file in same directory
require('dotenv').config({ path: __dirname + '/.env' });

module.exports = {
  apps: [
    {
      name: 'ollama-script-server',
      script: './launcher/run-ollama-server.sh',
      interpreter: '/bin/bash',
      cwd: '.',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        NODE_ENV: 'development',
        PORT: 8010,
        // Choose your LLM provider: 'anthropic', 'openai', or 'ollama'
        LLM_PROVIDER: process.env.LLM_PROVIDER || 'openai',

        // Anthropic settings (when LLM_PROVIDER=anthropic)
        ANTHROPIC_API_KEY: process.env.ANTHROPIC_API_KEY || '',
        ANTHROPIC_MODEL: process.env.ANTHROPIC_MODEL || "claude-3-5-haiku-20241022",

        // OpenAI settings (including Ollama through OpenAI-compatible endpoint)
        OPENAI_API_KEY: process.env.OPENAI_API_KEY || 'ollama-local-key',
        OPENAI_MODEL: process.env.OPENAI_MODEL || 'llama3.2',
        OPENAI_BASE_URL: process.env.OPENAI_BASE_URL || 'http://localhost:11434/v1',

        // System prompt configuration
        SYSTEM_PROMPT_FILE: process.env.SYSTEM_PROMPT_FILE || 'system-prompt.txt',

        // Ollama settings (when LLM_PROVIDER=ollama - not yet implemented)
        OLLAMA_BASE_URL: process.env.OLLAMA_BASE_URL || 'http://localhost:11434',
        OLLAMA_MODEL: process.env.OLLAMA_MODEL || 'llama3.2',

        // Dev visibility: stream pre-queue steps (validation, intent, analyst)
        // to the SSE progress panel. Set false to silence in prod.
        PRE_QUEUE_PROGRESS_LOGS: process.env.PRE_QUEUE_PROGRESS_LOGS || 'true',

        // Development auth bypass (allows X-User-ID header for auth)
        ENV: process.env.ENV || 'development',

        // Call tracking (set TRACK_CALLS=true in infrastructure/.env to enable)
        TRACK_CALLS: process.env.TRACK_CALLS || 'false',
      },
      error_file: './logs/err.log',
      out_file: './logs/out.log',
      log_file: './logs/combined.log',
      time: true,
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },
    {
      name: 'analysis-queue-worker',
      script: './launcher/start-analysis-worker.sh',
      interpreter: '/bin/bash',
      cwd: '../executionServer',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        TRACK_CALLS: process.env.TRACK_CALLS || 'false',
      },
      error_file: './logs/analysis-worker/err.log',
      out_file: './logs/analysis-worker/out.log',
      log_file: './logs/analysis-worker/combined.log',
      time: true,
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    },
    {
      name: 'execution-queue-worker',
      script: './launcher/start-execution-worker.sh',
      interpreter: '/bin/bash',
      cwd: '../executionServer',
      instances: 1,
      autorestart: true,
      watch: false,
      max_memory_restart: '1G',
      env: {
        TRACK_CALLS: process.env.TRACK_CALLS || 'false',
      },
      error_file: './logs/execution-worker/err.log',
      out_file: './logs/execution-worker/out.log',
      log_file: './logs/execution-worker/combined.log',
      time: true,
      merge_logs: true,
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z'
    }
  ]
};