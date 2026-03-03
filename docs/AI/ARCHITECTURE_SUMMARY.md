# QnA AI Admin - Architecture Summary

## ✅ Complete Updated Architecture Document

The comprehensive system architecture has been documented at: `/docs/SYSTEM_ARCHITECTURE.md`

---

## System Overview

### 3-Service Architecture

```
USER QUESTION
       ↓
SCRIPT EDITION API SERVER (Port 8010)
  ├─ Context awareness & session management
  ├─ Query expansion detection
  └─ Message template formatting
       ↓
LLM PROVIDER (Anthropic/OpenAI/Ollama)
  ├─ PAI Pattern: Prompt as Interface
  ├─ Generates Python script from question
  └─ Returns code + explanation
       ↓
EXECUTION SERVER (Port 3002)
  ├─ Script validation (AST-based security)
  ├─ Timeout/resource limits
  └─ Calls MCP servers for data
       ↓
MCP SERVERS (3 Services)
  ├─ Financial Data (Port 3003)
  ├─ Analytics (Port 3004)
  └─ Validation (Port 3005)
       ↓
RESULT TO USER
```

---

## 1. Script Edition - API Server (Port 8010)

**Location**: `backend/scriptEdition/apiServer/`

**Key Features**:
- FastAPI-based request handler
- Session management via Redis
- Context awareness via dialogue/search modules
- Query expansion & relevance detection
- Multi-provider LLM support (Anthropic, OpenAI, Ollama)

**Endpoints**:
```
POST   /analyze                    - Generate Python script for question
GET    /health                     - Health check
GET    /conversation/{session_id}  - Get session context
POST   /conversation/confirm       - Confirm query expansion
```

---

## 2. MCP Servers (3 Total)

### Financial Data MCP Server (Port 3003)

**Structure**:
```
External APIs (Alpaca, EODHD)
         ↓
vendors/ (API wrappers - NOT directly exposed)
  ├── alpaca.py
  ├── eodhd.py
  └── mocks/
         ↓
schemas.py (Data standardization)
         ↓
financial_server.py (MCP Server)
```

**Key Principle**: Raw APIs are wrapped and standardized before exposure

**Tools**: Market data, trading account, fundamentals

### Analytics MCP Server (Port 3004)

**Structure**:
```
mcp-server/analytics/
  ├── indicators/ (Technical indicators: SMA, RSI, MACD, etc.)
  ├── risk/ (Sharpe, Sortino, VaR, Drawdown, etc.)
  ├── portfolio/ (Optimization, allocation, simulation)
  ├── performance/ (Return analysis, metrics)
  └── analytics_server.py (MCP Server)
```

**Libraries**: talib-binary, empyrical, PyPortfolioOpt, pandas, numpy

### Validation MCP Server (Port 3005)

**Responsibilities**:
- AST-based Python script validation
- Security scanning (no system calls, file I/O, etc.)
- MCP function verification
- Runtime estimation

---

## 3. Execution Server (Port 3002)

**Location**: `mcp-server/shared_script_executor.py`

**Process**:
1. Receive Python script from API Server
2. Validate syntax & security
3. Set up execution environment (inject MCP client)
4. Execute with timeout/memory limits
5. Handle errors gracefully
6. Cache results
7. Return to user

**Resource Limits**:
- Timeout: 30s default, 120s max
- Memory: 512MB default, 2GB max
- Blocked: OS calls, file I/O, direct network access

---

## 4. Data Storage

### Redis (Port 6379)
**Purpose**: Session management, caching, rate limiting

**Keys**:
- `sessions:{session_id}` - Conversation state (TTL 7d)
- `result:{hash}` - Execution cache (TTL 24h)
- `rate_limit:{user_id}:{endpoint}` - Rate limiting (TTL 1h)
- `mcp_tools:{server}` - Tool schema cache (TTL 1h)

### Persistent Database (SQL or NoSQL)
**Purpose**: User data, execution history, audit logs

**Entities** (Database-agnostic):
- User
- ChatSession
- ChatMessage
- Execution (audit trail)
- AuditLog
- ExecutionCache

**Implementation Options**:
- SQL: PostgreSQL, MySQL (use JSON columns)
- NoSQL: MongoDB, DynamoDB
- Hybrid: Different databases for different entities

---

## Request/Response Flow

### 1. User Submits Question
```json
POST /analyze
{
  "question": "What are the top 5 most volatile stocks?",
  "session_id": "sess_123...",
  "auto_expand": true
}
```

### 2. API Server Response (Python Code)
```json
{
  "success": true,
  "data": {
    "python_code": "import pandas...\n# MCP calls",
    "explanation": "Uses screener API to get active stocks...",
    "mcp_calls": ["alpaca_market_screener_most_actives", "calculate_volatility"],
    "execution_id": "exec_789..."
  }
}
```

### 3. Execution Server Response (Results)
```json
{
  "success": true,
  "result": {
    "description": "Top 5 most volatile stocks",
    "body": [
      {
        "key": "rank_1",
        "value": "NVDA",
        "description": "NVIDIA - Volatility: 45.2%"
      }
    ]
  },
  "execution_time_ms": 2345
}
```

---

## Security Model

### Input Validation
- Length limits
- Character whitelist
- Sanitization (SQL injection, XSS, command injection)

### Script Execution Sandbox
- AST-based syntax validation
- No system imports (os, subprocess, sys, etc.)
- No file operations (open, read, write)
- No direct network access
- Resource limits (timeout, memory, CPU)

### Credentials Management
- Environment variables for API keys
- Future: Vault integration (HashiCorp, AWS Secrets Manager)

---

## Configuration

**Key Environment Variables**:
```bash
# API Server
API_SERVER_PORT=8010
LLM_PROVIDER=anthropic  # or openai, ollama

# MCP Servers
FINANCIAL_MCP_URL=http://localhost:3003
ANALYTICS_MCP_URL=http://localhost:3004

# External APIs
ALPACA_API_KEY=...
ALPACA_SECRET_KEY=...
EODHD_API_KEY=...

# Database
REDIS_URL=redis://localhost:6379
DATABASE_URL=postgresql://...  # or mongodb://...

# Security
JWT_SECRET=...
RATE_LIMIT_REQUESTS_PER_HOUR=100
```

---

## Quick Start

### Development Environment
```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Start services (docker-compose)
docker-compose up -d

# Verify services
curl http://localhost:8010/health
curl http://localhost:3003/health
curl http://localhost:3004/health
```

### Example Request
```bash
curl -X POST http://localhost:8010/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is AAPL current price?",
    "session_id": "sess_123",
    "auto_expand": true
  }'
```

---

## Key Architectural Principles

1. **PAI Pattern**: LLM as orchestrator between user intent and backend capabilities
2. **Data Wrapping**: External APIs wrapped and standardized before exposure
3. **Sandboxing**: Script execution in restricted environment with validation
4. **Session Management**: Redis-backed conversation state
5. **Database-Agnostic**: Data model works with SQL or NoSQL
6. **Error Recovery**: Graceful degradation with helpful error messages
7. **Caching**: Multi-level caching (Redis for speed, persistent DB for audit trail)

---

## Related GitHub Issues

This architecture document supports:
- **#4**: Complete system architecture (THIS DOCUMENT)
- **#2-5**: Data persistence and context awareness
- **#6-12**: MCP integration and execution
- **#13-20**: API standards and security
- **#21-32**: Testing and DevOps

---

## Next Steps

1. ✅ **Architecture finalized** - Documented in SYSTEM_ARCHITECTURE.md
2. ⏳ **Docker setup** - Create docker-compose for all services (#29-30)
3. ⏳ **CI/CD pipeline** - GitHub Actions setup (#32)
4. ⏳ **Redis integration** - Chat history persistence (#2)
5. ⏳ **Database schema** - Implement abstraction layer (#3)
6. ⏳ **Context awareness** - Dialogue module enhancement (#4)
7. ⏳ **Testing** - Comprehensive test suite (#21-25)

---

## Document Location

**Full Architecture**: `/docs/SYSTEM_ARCHITECTURE.md` (1000+ lines)

**Covers**:
- System flow diagrams
- Component responsibilities
- Request/response contracts
- Security architecture
- Performance & optimization
- Deployment architecture
- Configuration & environment variables
- Error handling strategies
- Database-agnostic data model
- Quick start guide
