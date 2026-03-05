# Health Check & Readiness System

This document explains how to use the comprehensive health check system to ensure your development environment is ready before starting the API server.

## Quick Start

Before starting the API, always run:

```bash
cd backend/apiServer
python scripts/preflight_check.py
```

This will validate all required services and tell you exactly what's missing.

## Service Status Endpoints

Once the API is running, you can check health status via HTTP:

```bash
# Get detailed health status of all services
curl http://localhost:8010/health/status

# Readiness probe (returns 200 only if ready)
curl http://localhost:8010/health/ready

# Liveness probe (returns 200 if API is running)
curl http://localhost:8010/health/live
```

## Required vs Optional Services

### ✅ Required Services (Must be running)
These services are **essential** for the API to function properly:

1. **MongoDB** (port 27017)
   - Database for sessions, messages, chat history
   - Status: **Check your system**
   - Fix: Install MongoDB or start container
   ```bash
   docker run -d -p 27017:27017 --name mongodb mongo:latest
   ```

2. **Redis** (port 6379)
   - Cache for CSRF tokens, conversation state
   - Status: **✅ Running** (confirmed by preflight check)
   - Fix: If not running
   ```bash
   docker run -d -p 6379:6379 --name redis redis:latest
   ```

3. **ChromaDB** (port 8050)
   - Vector database for semantic search in analysis
   - Status: **❌ NOT Running** (needs to be started)
   - Fix: Install Python, then start with native CLI (no Docker needed!)
   ```bash
   pip install chromadb
   ./backend/infrastructure/start-chroma.sh
   ```

4. **LLM Service** (port 11434 for Ollama or OpenAI API)
   - Language model for analysis and chat
   - Status: **✅ Required** 
   - Install Ollama: Download from https://ollama.ai
   - Or use OpenAI: Set `OPENAI_API_KEY` and `OPENAI_BASE_URL` env vars
   ```bash
   # Start Ollama
   ollama serve
   ```

### 🟡 Optional Services (Nice to have)
These are informational and don't block startup:

- **Analysis Worker**: Background process for processing analysis jobs
  - Auto-starts via PM2 if configured
  - Requires ChromaDB to function

## Current System Status

Your development environment currently has:

| Service | Status | Port |
|---------|--------|------|
| MongoDB | ✅ Healthy | 27017 |
| Redis | ✅ Healthy | 6379 |
| ChromaDB | ❌ Missing | 8050 |
| LLM Service | ✅ Healthy | 11434 |
| API Server | ✅ Running | 8010 |

## Setup Workflow

### 1. Check Prerequisites
```bash
cd backend/apiServer
python scripts/preflight_check.py
```

**Expected output:**
- If status is "healthy" → Skip to step 4
- If status shows missing services → Continue to step 2

### 2. Install Missing Services

#### Option A: Docker Compose (Recommended - starts all at once)
```bash
cd backend/infrastructure
docker-compose up -d
```

#### Option B: Individual Docker Commands
```bash
# MongoDB
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Redis  
docker run -d -p 6379:6379 --name redis redis:latest

# ChromaDB
docker run -d -p 8050:8050 chromadb/chroma
```

#### Option C: Homebrew (macOS)
```bash
# MongoDB
brew install mongodb-community
brew services start mongodb-community

# Redis
brew install redis
brew services start redis
```

### 3. Verify Setup
```bash
python scripts/preflight_check.py
```

**Expected output:**
```
✅ ALL SYSTEMS READY - You can start the server
```

### 4. Start Backend Services
```bash
# Terminal 1: Process Manager
cd backend/infrastructure
pm2 start pm2.config.js

# Or manually start each:
cd backend/apiServer && python server.py          # API Server (port 8010)
cd backend/executionServer && python http_script_execution_server.py  # Execution Server (port 8013)
```

### 5. Start Frontend
```bash
# Terminal 2: Frontend
cd frontend
npm run dev
```

### 6. Monitor Services
```bash
# View all services
pm2 status

# View logs
pm2 logs

# View specific service
pm2 logs ollama-script-server

# Monitor in real-time
pm2 monit
```

## Health Check API Examples

### Check Overall Status
```bash
curl -s http://localhost:8010/health/status | jq .
```

**Response:**
```json
{
  "status": "degraded",
  "services": {
    "MongoDB": {
      "status": "healthy",
      "message": "Connected to qna_ai_admin",
      "latency_ms": 2.5,
      "required": true
    },
    "RedisDB": {
      "status": "healthy",
      "message": "Cache connected",
      "latency_ms": 1.1,
      "required": true
    },
    "ChromaDB": {
      "status": "unhealthy",
      "message": "Connection failed: Cannot connect to host",
      "latency_ms": 0,
      "required": true
    },
    "LLM Service": {
      "status": "healthy",
      "message": "Connected (list)",
      "latency_ms": 2.7,
      "required": true
    },
    "Analysis Worker": {
      "status": "healthy",
      "message": "No active workers (may be idle)",
      "latency_ms": 0,
      "required": false
    }
  }
}
```

### Check Readiness
```bash
curl -s http://localhost:8010/health/ready
```

**Response if ready (HTTP 200):**
```json
{
  "ready": true,
  "status": "all systems operational"
}
```

**Response if not ready (HTTP 503):**
```json
{
  "detail": "Service not ready: ..."
}
```

### Check Liveness
```bash
curl -s http://localhost:8010/health/live
```

**Response (HTTP 200):**
```json
{
  "alive": true
}
```

## Troubleshooting

### Issue: "Cannot connect to MongoDB"
**Solution:**
```bash
# Check if MongoDB is running
docker ps | grep mongodb

# If not, start it
docker run -d -p 27017:27017 --name mongodb mongo:latest

# Or with Homebrew
brew services start mongodb-community
```

### Issue: "Cannot connect to ChromaDB"
**Solution:**
```bash
# ChromaDB runs natively (no Docker needed!)
# Start with the provided script:
./backend/infrastructure/start-chroma.sh

# Or manually:
chroma run --path backend/data/analysis_library_db --port 8050

# Verify it's running
curl http://localhost:8050/api/v1/heartbeat
```

### Issue: "Analysis jobs stuck in queue"
**Solution:**
1. Check ChromaDB is running (analysis worker needs it)
2. Check analysis worker is running:
   ```bash
   pm2 status | grep analysis
   ```
3. View worker logs:
   ```bash
   pm2 logs analysis-queue-worker
   ```

### Issue: "Port already in use"
**Solution:**
```bash
# Find process using port 27017 (MongoDB)
lsof -i :27017

# Or use Docker with custom port
docker run -d -p 27018:27017 --name mongodb mongo:latest
```

## Environment Variables

Key configuration (`.env` file in `backend/apiServer`):

```env
# MongoDB
MONGO_URL=mongodb://localhost:27017
MONGO_DB_NAME=qna_ai_admin

# Redis
REDIS_URL=redis://localhost:6379

# ChromaDB
CHROMADB_URL=http://localhost:8050

# LLM (Ollama)
OPENAI_BASE_URL=http://localhost:11434/v1
OPENAI_MODEL=llama3.2

# LLM (OpenAI)
# OPENAI_API_KEY=your-api-key
# OPENAI_BASE_URL=https://api.openai.com/v1
# OPENAI_MODEL=gpt-4
```

## Next Steps

1. ✅ Run preflight check
2. ✅ Fix any missing services
3. ✅ Verify all green
4. ✅ Start backend & frontend
5. ✅ Open http://localhost:3000 (frontend)
6. ✅ API available at http://localhost:8010

For detailed architecture, see [SYSTEM_ARCHITECTURE.md](../../docs/SYSTEM_ARCHITECTURE.md)
