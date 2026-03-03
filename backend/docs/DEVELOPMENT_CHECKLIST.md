# Development Environment Checklist

A quick reference for ensuring all pieces are running before accepting API requests.

## 🚀 Before You Start Development

### Step 1: Run Health Check (2 minutes)
```bash
cd backend/apiServer
python scripts/preflight_check.py
```

Expected output:
```
✅ ALL SYSTEMS READY - You can start the server
```

If you see ❌ services, see "Fixing Missing Services" below.

---

## ✅ Current Status

| Service | Port | Status | Start Command |
|---------|------|--------|----------------|
| **MongoDB** | 27017 | ✅ Running | `docker run -d -p 27017:27017 mongo` |
| **Redis** | 6379 | ✅ Running | `docker run -d -p 6379:6379 redis` |
| **ChromaDB** | 8050 | ❌ **MISSING** | `./backend/infrastructure/start-chroma.sh` |
| **LLM Service** | 11434 | ✅ Running | `ollama serve` |
| **API Server** | 8010 | On demand | `python backend/apiServer/server.py` |
| **Frontend** | 3000 | On demand | `npm run dev` (from frontend) |

---

## 🔧 Setup Instructions (First Time Only)

### Option 1: Individual Services (Recommended - No Docker Needed!)
```bash
# MongoDB
docker run -d -p 27017:27017 mongo:latest

# Redis
docker run -d -p 6379:6379 redis:latest

# ChromaDB (Native - No Docker Required!)
./backend/infrastructure/start-chroma.sh

# LLM (Ollama)
ollama serve  # In separate terminal
```

### Option 2: Docker Compose (if you prefer Docker)
```bash
cd backend/infrastructure
docker-compose up -d
cd ..
```

### Step 2: Verify Setup
```bash
python backend/apiServer/scripts/preflight_check.py
```

Expected: ✅ ALL SYSTEMS READY

---

## 📋 Daily Startup Sequence

### Terminal 1: Backend Services
```bash
cd backend/infrastructure
pm2 start ecosystem.config.js
```

Starts:
- 🚀 API Server (port 8010)
- 🚀 Execution Server (port 8013)
- 🚀 Analysis Queue Worker

Monitor:
```bash
pm2 logs          # View all logs
pm2 monit        # Real-time monitoring
pm2 status       # Service status
```

### Terminal 2: Frontend
```bash
cd frontend
npm run dev
```

Opens: http://localhost:3000

### Terminal 3: LLM Service (if using Ollama)
```bash
ollama serve
```

---

## 🏥 Health Check Endpoints

Once API is running, check health:

```bash
# Detailed status
curl http://localhost:8010/health/status

# Is system ready? (200 = ready, 503 = not ready)
curl http://localhost:8010/health/ready

# Is API alive? (200 = yes)
curl http://localhost:8010/health/live
```

---

## ⚠️ Common Issues

### Issue: "Analysis jobs not processing"
**Cause:** ChromaDB not running
```bash
docker run -d -p 8050:8050 chromadb/chroma
pm2 restart analysis-queue-worker
```

### Issue: "Connection refused on port 27017"
**Cause:** MongoDB not running
```bash
docker run -d -p 27017:27017 mongo:latest
```

### Issue: "CSRF token validation failed"
**Status:** Currently disabled for debugging. Run:
```bash
curl -X POST http://localhost:8010/sessions/{id}/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "test"}'
```

### Issue: "Workers keep crashing"
See logs:
```bash
pm2 logs analysis-queue-worker
pm2 logs script-execution-server
pm2 logs ollama-script-server
```

---

## 📊 What's Running Now

```
╭─────────────────────────────────────────────╮
│  DEVELOPMENT ENVIRONMENT STATUS             │
├─────────────────────────────────────────────┤
│                                             │
│  DATABASE TIER:                             │
│  ✅ MongoDB      (localhost:27017)          │
│  ✅ Redis        (localhost:6379)           │
│  ❌ ChromaDB     (localhost:8050) NEEDS FIX │
│                                             │
│  SERVICES:                                  │
│  ✅ LLM Service  (localhost:11434)          │
│  🔲 API Server   (localhost:8010)  PAUSED   │
│  🔲 Frontend     (localhost:3000)   PAUSED  │
│  🔲 Analysis Worker                PAUSED   │
│                                             │
│  NEXT: Run preflight_check.py then start    │
│                                             │
╰─────────────────────────────────────────────╯
```

---

## 🎯 API Request Flow

When you make an API request:

1. **Request arrives** → API Server validates CSRF token (currently disabled)
2. **Create session** → Stored in MongoDB  
3. **Send chat message** → Stored, ResponseStreamed to client
4. **Trigger analysis** → Job queued to MongoDB analysis_queue
5. **Analysis worker** → Picks up job, runs LLM + ChromaDB
6. **Results saved** → Back to MongoDB, progress streamed to client

For this to work:
- ✅ API must be running
- ✅ MongoDB must be running (jobs stored here)
- ✅ Redis must be running (CSRF tokens, cache)
- ✅ ChromaDB must be running (analysis pipeline)
- ✅ LLM Service must be running (analysis processing)

---

## 🔍 Debugging

### View all service logs
```bash
pm2 logs
```

### Watch specific service
```bash
pm2 logs ollama-script-server --lines 100 --follow
```

### Check health of all services
```bash
python backend/apiServer/scripts/preflight_check.py --verbose
```

### Check API is responding
```bash
curl http://localhost:8010/health/live
```

### Check analysis queue (MongoDB)
```bash
python backend/apiServer/scripts/debug_analysis_queue.py
```

---

## 📚 Documentation

- [Health Check Guide](./HEALTH_CHECK_GUIDE.md) - Detailed health check info
- [System Architecture](./docs/SYSTEM_ARCHITECTURE.md) - Complete system design
- [Setup Issues](./docs/README.md) - Troubleshooting guide

---

## ⚡ Quick Commands Reference

```bash
# Check everything is ready
python backend/apiServer/scripts/preflight_check.py

# Start all services
cd backend/infrastructure && pm2 start ecosystem.config.js

# View service status
pm2 status

# Restart API if it breaks
pm2 restart ollama-script-server

# Tail all logs
pm2 logs

# Stop services
pm2 stop all

# View analysis queue jobs
python backend/apiServer/scripts/debug_analysis_queue.py

# Test API health
curl http://localhost:8010/health/ready
```

---

**⚠️ IMPORTANT:** Always run health check before reporting bugs!
```bash
python backend/apiServer/scripts/preflight_check.py
```
