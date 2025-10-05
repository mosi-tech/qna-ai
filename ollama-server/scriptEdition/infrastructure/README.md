# Infrastructure & Deployment

This folder contains all deployment, configuration, and infrastructure files for the Financial Analysis Server.

## Files

### Configuration Files
- **`.env`** - Environment variables for production deployment
- **`.env.example`** - Template for environment variables
- **`package.json`** - Node.js dependencies for PM2 and dotenv
- **`package-lock.json`** - Dependency lock file

### Deployment Scripts
- **`ecosystem.config.js`** - PM2 process manager configuration
- **`run-ollama-server.sh`** - Shell script to start server with environment setup
- **`restart-servers.sh`** - Restart all PM2 processes
- **`start-script-server.sh`** - Start script server
- **`switch-llm.sh`** - Switch between LLM providers
- **`test-tool-calling.sh`** - Test tool calling functionality

## Deployment Instructions

### 1. Environment Setup
```bash
# Copy environment template
cp infrastructure/.env.example infrastructure/.env

# Edit with your actual API keys
nano infrastructure/.env
```

### 2. Install Dependencies
```bash
# Install Node.js dependencies for PM2 (from scriptEdition directory)
cd infrastructure && npm install && cd ..

# Install Python dependencies for the application
pip install -r apiServer/requirements.txt
```

### 3. Production Deployment (PM2)
```bash
# Start with PM2 from the scriptEdition directory
pm2 start infrastructure/ecosystem.config.js

# Monitor processes
pm2 status
pm2 logs
```

### 4. Development Mode
```bash
# Run from the scriptEdition directory
./infrastructure/run-ollama-server.sh
```

### 5. Direct Python
```bash
# Run directly from the scriptEdition directory
python apiServer/server.py
```

## Configuration

### Environment Variables (.env)
- `LLM_PROVIDER` - Either "anthropic" or "ollama"
- `ANTHROPIC_API_KEY` - Your Anthropic API key (if using Anthropic)
- `ANTHROPIC_MODEL` - Anthropic model to use
- `OLLAMA_BASE_URL` - Ollama server URL (if using Ollama)
- `OLLAMA_MODEL` - Ollama model to use

### PM2 Configuration (ecosystem.config.js)
- Automatically loads environment variables from `.env`
- Configures logging to `../logs/` directory
- Sets up auto-restart and memory limits
- Runs both the main server and execution server

## Architecture

```
scriptEdition/
├── infrastructure/          # All deployment files
│   ├── .env                # Environment variables (hidden)
│   ├── .env.example        # Environment template (hidden)
│   ├── ecosystem.config.js # PM2 configuration
│   ├── package.json        # Node.js dependencies
│   ├── node_modules/       # Node.js dependencies (installed here)
│   ├── run-ollama-server.sh # Development startup script
│   └── ...                 # Other deployment scripts
├── apiServer/              # Application code
│   ├── server.py           # Main entry point
│   ├── requirements.txt    # Python dependencies
│   └── ...                 # Application modules
└── executionServer/        # Script execution service
    └── ...
```

This separation keeps deployment concerns separate from application logic while maintaining a clean, organized structure.