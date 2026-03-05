# ChromaDB Native Setup (No Docker!)

We've created a simple native ChromaDB setup that requires **zero Docker knowledge**. Just run a bash script!

## Quick Start (30 seconds)

### 1. Install ChromaDB (one-time)
```bash
pip install chromadb
```

### 2. Start ChromaDB
```bash
cd backend/infrastructure
./start-chroma.sh
```

That's it! ChromaDB is now running on port 8050 with persistent storage in `backend/data/analysis_library_db`.

---

## Files Created

### 1. **start-chroma.sh** 
Located: `backend/infrastructure/start-chroma.sh`

What it does:
- ✅ Creates persistent data directory
- ✅ Starts ChromaDB server
- ✅ Saves process ID for later cleanup
- ✅ Redirects logs to `analysis_library_db/chroma.log`
- ✅ Waits for server to be ready
- ✅ Tests connection automatically

### 2. **stop-chroma.sh**
Located: `backend/infrastructure/stop-chroma.sh`

What it does:
- ✅ Stops ChromaDB gracefully
- ✅ Reads PID from saved file
- ✅ Falls back to port-based detection
- ✅ Cleans up .pid file

### 3. **CHROMADB_SETUP.md**
Complete reference guide with all commands and troubleshooting.

---

## How It Works

### Data Persistence
```
backend/
  └─ data/
      └─ analysis_library_db/
          ├─ chroma.sqlite3          ← Your persistent database
          ├─ chroma.log              ← Server logs
          ├─ chroma.pid              ← Process ID
          └─ [collection folders]
```

Data survives across restarts. Delete the directory to reset.

### Environment Variables (Optional)
```bash
export CHROMA_HOST=localhost     # Default
export CHROMA_PORT=8050          # Default
```

---

## Integration Points

### Library Code
File: `backend/shared/analyze/search/library.py`

Automatically connects to ChromaDB at `localhost:8050`:
```python
self.client = chromadb.HttpClient(
    host=chroma_host,
    port=chroma_port,
    settings=Settings(anonymized_telemetry=False)
)
```

### Health Checker
File: `backend/shared/health/health_checker.py`

Validates ChromaDB is running during startup:
```bash
python backend/apiServer/scripts/preflight_check.py
```

---

## Daily Workflow

### Terminal 1: Start ChromaDB (keep running)
```bash
cd backend/infrastructure
./start-chroma.sh
# Output: ChromaDB Server is running (PID: 12345)
```

### Terminal 2: Start Backend Services
```bash
cd backend/infrastructure
pm2 start pm2.config.js
```

### Terminal 3: Start Frontend
```bash
cd frontend
npm run dev
```

Visit: http://localhost:3000

---

## Stopping Everything

### Stop ChromaDB
```bash
cd backend/infrastructure
./stop-chroma.sh
```

### Stop Backend/Frontend
```bash
pm2 stop all        # Stop API servers
# Ctrl+C in frontend terminal
```

---

## Verification

### Is ChromaDB running?
```bash
curl http://localhost:8050/api/v1/heartbeat
# Should return heartbeat number
```

### Check full system health
```bash
python backend/apiServer/scripts/preflight_check.py
```

### View ChromaDB logs
```bash
tail -f backend/data/analysis_library_db/chroma.log
```

---

## Why Native ChromaDB?

✅ **No Docker needed** - One less tool to install
✅ **Simpler to debug** - Logs in plain files, process is visible
✅ **Lightweight** - Runs directly on your machine
✅ **Persistent** - Data survives restarts
✅ **Fast startup** - No container overhead
❌ **Multi-machine** - Only works on localhost (fine for dev)

---

## What Changed From Docker Version

| Aspect | Before (Docker) | Now (Native) |
|--------|---|---|
| Installation | Docker Desktop required | pip install chromadb |
| Start command | `docker run ...` (complex) | `./start-chroma.sh` (simple) |
| Data location | Inside Docker volume | `backend/data/analysis_library_db/` |
| Logs | `docker logs chromadb` | `backend/data/analysis_library_db/chroma.log` |
| Stop command | `docker stop chromadb` | `./stop-chroma.sh` |
| Persistence | ✅ Yes | ✅ Yes |
| Debugging | Harder | Easier |

---

## Troubleshooting

### ChromaDB won't start
1. Check if port 8050 is free: `lsof -i :8050`
2. Check logs: `cat backend/data/analysis_library_db/chroma.log`
3. Try manual start: `chroma run --path backend/data/analysis_library_db --port 8050`

### Connection refused errors
- Wait 3-5 seconds - ChromaDB takes time to start
- Check `curl http://localhost:8050/api/v1/heartbeat` returns a number
- Verify port 8050 isn't used by another service

### Data corruption
- Stop ChromaDB: `./stop-chroma.sh`
- Backup data: `mv backend/data/analysis_library_db backend/data/analysis_library_db.bak`
- Start fresh: `./start-chroma.sh`

---

## Next Steps

1. ✅ Scripts created
2. ✅ Documentation updated
3. 🔲 Test it: `./start-chroma.sh`
4. 🔲 Run health check: `python backend/apiServer/scripts/preflight_check.py`
5. 🔲 Start full stack and verify all working

See [DEVELOPMENT_CHECKLIST.md](./DEVELOPMENT_CHECKLIST.md) for complete workflow.
