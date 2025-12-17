# QnA-AI Quick Start Guide

## System Architecture

This application consists of:
- **Frontend**: Next.js React app (Port 3000)
- **API Server**: FastAPI backend (Port 8010)
- **Execution Server**: Python script executor (Port 8013)
- **MCP Servers**: Financial data, Analytics, Validation
- **Redis**: Session & cache storage
- **MongoDB**: Data persistence

## Prerequisites

- Python 3.8+
- Node.js 18+
- Redis (for caching)
- MongoDB (optional, for persistence)
- LLM Provider: Anthropic API key, OpenAI API key, or Ollama

## Step-by-Step Setup

### 1. Install Python Dependencies

```bash
# Install backend API server dependencies
cd backend/scriptEdition/apiServer
pip3 install -r requirements.txt

# Install shared dependencies
cd ../../shared
pip3 install -r requirements.txt

# Install MCP server dependencies
cd ../mcp-server
pip3 install -r requirements.txt

# Install execution server dependencies
cd ../scriptEdition/executionServer
pip3 install -r requirements.txt
```

### 2. Install Node.js Dependencies

```bash
# Install frontend dependencies
cd frontend
npm install

# Install PM2 for process management (optional)
cd ../backend/scriptEdition/infrastructure
npm install
```

### 3. Configure Environment Variables

Create `.env` file in `backend/scriptEdition/infrastructure/`:

```bash
cd backend/scriptEdition/infrastructure
cp .env.example .env
```

Edit `.env` with your configuration:

```bash
# Choose your LLM provider
LLM_PROVIDER=anthropic  # or openai, ollama

# Anthropic Configuration (if using Claude)
ANTHROPIC_API_KEY=your_api_key_here
ANTHROPIC_MODEL=claude-3-5-haiku-20241022

# OpenAI Configuration (if using GPT)
OPENAI_API_KEY=your_api_key_here
OPENAI_MODEL=gpt-4
OPENAI_BASE_URL=https://api.openai.com/v1

# Ollama Configuration (if using local LLM)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# Database Configuration
REDIS_URL=redis://localhost:6379
MONGODB_URI=mongodb://localhost:27017/qna-ai
```

### 4. Start Redis

```bash
# Start Redis server
redis-server
# Or run in background:
redis-server --daemonize yes
```

### 5. Start Backend Services

Option A: **Manual Start (Recommended for Testing)**

Terminal 1 - API Server:
```bash
cd backend/scriptEdition/apiServer
python3 server.py
# Should start on http://localhost:8010
```

Terminal 2 - Execution Server:
```bash
cd backend/scriptEdition/executionServer
python3 http_script_execution_server.py
# Should start on http://localhost:8013
```

Terminal 3 - MCP Servers:
```bash
cd backend/mcp-server
# Start financial MCP server
python3 financial_server.py
# Should start on port 3003
```

Option B: **PM2 (Production-like)**

```bash
cd backend/scriptEdition
pm2 start infrastructure/ecosystem.config.js
pm2 status
pm2 logs
```

### 6. Start Frontend

```bash
cd frontend
npm run dev
# Opens at http://localhost:3000
```

## Verify Installation

Check all services are running:

```bash
# API Server Health
curl http://localhost:8010/health

# Execution Server Health
curl http://localhost:8013/health

# Frontend
open http://localhost:3000
```

## Test the Application

1. Open browser to `http://localhost:3000`
2. Enter a financial question like "What is the current price of AAPL?"
3. The system should:
   - Generate Python code via LLM
   - Execute it on the execution server
   - Call MCP servers for data
   - Display results

## Common Issues

### Redis Not Running
```bash
redis-server --daemonize yes
```

### Port Already in Use
```bash
# Find process using port
lsof -i :8010
kill -9 <PID>
```

### Missing Python Packages
```bash
pip3 install fastapi uvicorn anthropic httpx pydantic
```

### LLM Provider Issues
- **Anthropic**: Verify API key in .env
- **Ollama**: Ensure `ollama serve` is running
- **OpenAI**: Verify API key and credits

## Architecture Ports

| Service | Port | Purpose |
|---------|------|---------|
| Frontend | 3000 | Next.js UI |
| API Server | 8010 | Main FastAPI backend |
| Execution Server | 8013 | Python script executor |
| Financial MCP | 3003 | Market data |
| Analytics MCP | 3004 | Technical analysis |
| Validation MCP | 3005 | Script validation |
| Redis | 6379 | Cache/Sessions |
| MongoDB | 27017 | Data persistence |

## Minimal Setup (No External Services)

If you want to run without external APIs:

1. Use Ollama (local LLM)
2. Use mock financial data
3. Skip MongoDB (uses in-memory)

```bash
# Start Ollama
ollama serve
ollama pull llama3.2

# Set .env
LLM_PROVIDER=ollama
OLLAMA_MODEL=llama3.2

# Run with mock data
cd backend/mcp-server
python3 financial_server_mock.py
```

## Development vs Production

**Development:**
- Use `npm run dev` for hot reload
- Run servers individually for debugging
- Use mock data when possible

**Production:**
- Use PM2 for process management
- Set up nginx reverse proxy
- Use environment-specific .env files
- Enable monitoring and logging

## Next Steps

- Review MVP issues: See GitHub issues labeled "mvp"
- Check architecture: `ARCHITECTURE_SUMMARY.md`
- Security setup: `SECURITY.md`
- System docs: `docs/SYSTEM_ARCHITECTURE.md`
