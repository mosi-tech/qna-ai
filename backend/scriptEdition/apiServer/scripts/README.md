# Database Scripts

Utility scripts for managing the MongoDB database.

## Scripts

### 1. seed_development_data.py
**Purpose:** Populate database with realistic sample data for development/testing

**Usage:**
```bash
python scripts/seed_development_data.py
```

**What It Creates:**
- 3 sample users (alice, bob, charlie)
- 3 chat sessions with multi-turn conversations
- 5 analysis records with results
- 5 execution records with timing data

**When to Use:**
- Local development and testing
- Feature development without manual setup
- API endpoint testing
- Quick demonstration

**Time to Run:** ~2-3 seconds

**Example Output:**
```
📝 Seeding users...
  ✓ Created user: alice_trader
  ✓ Created user: bob_investor
  ✓ Created user: charlie_analyst

💬 Seeding chat sessions and conversations...
  ✓ Created session: AAPL Technical Analysis (4 messages)
  ✓ Created session: Portfolio Correlation Analysis (2 messages)
  ✓ Created session: Market Volatility Research (4 messages)

📊 Seeding analyses...
  ✓ Created analysis: 30-Day AAPL Volatility
  ✓ Created analysis: Support/Resistance Levels
  ✓ Created analysis: Portfolio Correlation Matrix
  ✓ Created analysis: Portfolio Diversification Score
  ✓ Created analysis: Sector Volatility Comparison

⚙️  Seeding execution records...
  ✓ Created execution: What is AAPL's 30-day volatility?...
  ✓ Created execution: Compare AAPL volatility to SPY...
  ✓ Created execution: Calculate portfolio correlations...
  ✓ Created execution: Analyze portfolio diversification...
  ✓ Created execution: Compare sector volatility...

✅ SEEDING COMPLETE!
```

### 2. cleanup_database.py
**Purpose:** Clear all data from the database (DESTRUCTIVE)

**Usage:**
```bash
# Interactive (with confirmation prompt)
python scripts/cleanup_database.py

# Auto-confirm (use with caution!)
python scripts/cleanup_database.py --confirm
```

**What It Clears:**
- users
- chat_sessions
- chat_messages
- analyses
- executions
- saved_analyses
- audit_logs
- cache

**When to Use:**
- Reset database before re-seeding
- Clean up test data
- Fresh start for development
- Before deploying to production

**WARNING:** This is **IRREVERSIBLE**. All data will be permanently deleted.

**Time to Run:** ~1 second

**Example Output:**
```
⚠️  WARNING: This will DELETE ALL DATA from the database!
   This action is IRREVERSIBLE.

Type 'DELETE' to confirm: DELETE

🔌 Connecting to MongoDB...

🗑️  Clearing collections...

  ✓ users: deleted 3 documents
  ✓ chat_sessions: deleted 6 documents
  ✓ chat_messages: deleted 15 documents
  ✓ analyses: deleted 5 documents
  ✓ executions: deleted 5 documents
  ✓ saved_analyses: deleted 0 documents
  ✓ audit_logs: deleted 23 documents
  ✓ cache: deleted 0 documents

✅ CLEANUP COMPLETE: Deleted 57 total documents
```

---

## Common Workflows

### Fresh Development Setup
```bash
# 1. Clean database
python scripts/cleanup_database.py

# 2. Seed sample data
python scripts/seed_development_data.py

# 3. Start server
python server.py

# 4. Test endpoints with seeded data
curl http://localhost:8010/health
```

### Reset Between Test Runs
```bash
python scripts/cleanup_database.py --confirm
python scripts/seed_development_data.py
# Run tests
pytest test_endpoints_comprehensive.py
```

### Production-Like Environment
```bash
# Start with clean slate
python scripts/cleanup_database.py --confirm

# Start server (no sample data)
python server.py

# Users create data organically through API
curl -X POST http://localhost:8010/analyze \
  -H "Content-Type: application/json" \
  -d '{"question": "What is AAPL price?"}'
```

---

## Database State at Each Point

### After server startup (no seeding):
```
✓ MongoDB connected
✓ All indexes created
✓ 0 users
✓ 0 chat sessions
✓ 0 messages
✓ 0 analyses
Database ready for use (empty)
```

### After seed_development_data.py:
```
✓ 3 users
✓ 3 chat sessions
✓ 10 chat messages (actual conversation flow)
✓ 5 analyses
✓ 5 executions
✓ 28 audit log entries
Database ready for testing
```

### After cleanup_database.py:
```
✓ Back to: 0 users, 0 sessions, 0 messages
Indexes still present (not deleted)
Ready for fresh seeding
```

---

## Key Notes

### Indexes are NOT deleted by cleanup_database.py
- Indexes are created automatically on server startup
- Cleanup only clears DATA, not schema
- Safe to run cleanup multiple times

### Idempotent Operations
- Each script is safe to run multiple times
- No risk of double-creating data
- Can run seed script on already-seeded database (appends more data)

### Connection
- Scripts use same MongoDB connection as server
- Respects MONGODB_URI environment variable
- Defaults to: mongodb://localhost:27017

### Environment Variables
```bash
# Override default MongoDB connection
export MONGODB_URI=mongodb://user:pass@host:port
export MONGODB_DB_NAME=qna_ai_admin

# Then run scripts
python scripts/seed_development_data.py
```

---

## Troubleshooting

### "Connection refused" error
```
Error: Couldn't connect to MongoDB
Solution: Make sure MongoDB is running
  brew services start mongodb-community  (Mac)
  sudo service mongod start              (Linux)
  mongod                                 (Manual)
```

### "Database already exists" or duplicate data
```
Error: User already exists with email...
Solution: Run cleanup first
  python scripts/cleanup_database.py --confirm
  python scripts/seed_development_data.py
```

### Partial seeding failure
```
If seeding stops halfway through:
1. Check error message
2. Run cleanup_database.py --confirm
3. Run seed_development_data.py again
```

---

## No Manual Migration Scripts Needed

The database layer automatically:
- ✅ Creates all collections on first write
- ✅ Creates all indexes on server startup
- ✅ Validates schemas with Pydantic
- ✅ Handles data types automatically

Therefore:
- ❌ NO migration scripts needed
- ❌ NO schema version tracking needed
- ❌ NO manual CREATE TABLE statements needed

---

## Summary

| Action | Command | Time | Data Impact |
|--------|---------|------|------------|
| Seed sample data | `python scripts/seed_development_data.py` | ~2s | +44 documents |
| Clean database | `python scripts/cleanup_database.py` | ~1s | Delete all data |
| Clean + confirm | `python scripts/cleanup_database.py --confirm` | ~1s | Delete all data (no prompt) |
| View what's in DB | `python scripts/inspect_db.py` | ~1s | No changes |

**Start here:** `python scripts/seed_development_data.py`

