# ChromaDB Setup & Usage

Quick reference for running ChromaDB with persistent data storage.

## Installation

ChromaDB should already be installed. Verify:

```bash
pip list | grep chromadb
# or
chroma --version
```

If not installed:
```bash
pip install chromadb
```

## Starting ChromaDB

### Automatic (using provided script)
```bash
cd backend/infrastructure
./start-chroma.sh
```

This will:
- Create data directory: `backend/data/analysis_library_db`
- Start ChromaDB on port 8050
- Save logs to: `backend/data/analysis_library_db/chroma.log`
- Save process ID to: `backend/data/analysis_library_db/chroma.pid`

### Manual (direct command)
```bash
chroma run --path backend/data/analysis_library_db --port 8050
```

## Stopping ChromaDB

### Using provided script
```bash
cd backend/infrastructure
./stop-chroma.sh
```

### Manually
```bash
# Kill the process
kill $(cat backend/data/analysis_library_db/chroma.pid)

# Or force kill
kill -9 $(lsof -t -i :8050)
```

## Verifying ChromaDB is Running

```bash
# Check if port 8050 is listening
lsof -i :8050

# Test connection
curl http://localhost:8050/api/v1/heartbeat

# View logs
tail -f backend/data/analysis_library_db/chroma.log
```

## Persistent Data

All ChromaDB data is stored in:
- **Path**: `backend/data/analysis_library_db/`
- **Database file**: `chroma.sqlite3`
- **Collections**: Persist across restarts

To backup data:
```bash
cp -r backend/data/analysis_library_db ~/chroma-backup
```

To reset/clear data:
```bash
rm -rf backend/data/analysis_library_db
# Data directory will be recreated on next start
```

## Configuration

Environment variables (optional):

```bash
# Set custom port (default: 8050)
export CHROMA_PORT=8050

# Set custom host (default: localhost)
export CHROMA_HOST=localhost
```

## Troubleshooting

### Port 8050 already in use
```bash
# Find process using port
lsof -i :8050

# Kill it
kill -9 <PID>

# Or use a different port
chroma run --path backend/data/analysis_library_db --port 8051
```

### ChromaDB not responding
```bash
# Check if process is running
ps aux | grep chroma | grep -v grep

# Check logs
cat backend/data/analysis_library_db/chroma.log

# Restart
./stop-chroma.sh
./start-chroma.sh
```

### Database corrupted
```bash
# Backup old data (if needed)
mv backend/data/analysis_library_db backend/data/analysis_library_db.bak

# Start fresh
./start-chroma.sh
```

## Integration with API

The API auto-connects to ChromaDB at `localhost:8050`, configured in:
- `backend/shared/analyze/search/library.py`

Environment variables for custom location:
```bash
export CHROMA_HOST=localhost
export CHROMA_PORT=8050
```

## Full Development Stack

Start everything:

```bash
# Terminal 1: ChromaDB
cd backend/infrastructure
./start-chroma.sh

# Terminal 2: Backend API & Services  
cd backend/infrastructure
pm2 start ecosystem.config.js

# Terminal 3: Frontend
cd frontend
npm run dev
```

Then visit: http://localhost:3000

## Quick Commands Reference

| Task | Command |
|------|---------|
| Start ChromaDB | `./backend/infrastructure/start-chroma.sh` |
| Stop ChromaDB | `./backend/infrastructure/stop-chroma.sh` |
| Test ChromaDB | `curl http://localhost:8050/api/v1/heartbeat` |
| View logs | `tail -f backend/data/analysis_library_db/chroma.log` |
| Check process | `ps aux \| grep chroma` |
| Reset data | `rm -rf backend/data/analysis_library_db` |

## Next Steps

After starting ChromaDB:

1. Run health checks:
   ```bash
   python backend/apiServer/scripts/preflight_check.py
   ```

2. Start API server:
   ```bash
   cd backend/infrastructure
   pm2 start ecosystem.config.js
   ```

3. Verify all systems:
   ```bash
   curl http://localhost:8010/health/status | jq
   ```
