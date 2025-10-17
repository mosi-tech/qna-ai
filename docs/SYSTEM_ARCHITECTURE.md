# QnA AI Admin - Complete System Architecture

## Executive Summary

QnA AI Admin is a distributed financial analysis platform that accepts natural language questions from users, generates Python scripts to answer them using MCP (Model Context Protocol) servers, executes those scripts in a sandboxed environment, and returns formatted results to the UI.

The system follows a **PAI (Prompt as Interface)** pattern where the LLM acts as an orchestrator between user intent and backend capabilities.

---

## High-Level System Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                           USER                                  │
│                   (Next.js Frontend)                            │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ HTTP POST /analyze
                             │ { question, session_id, auto_expand }
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│            SCRIPT EDITION - API SERVER (Port 8010)             │
│                      (FastAPI Python)                           │
│                                                                  │
│  • Request validation & sanitization                            │
│  • Context awareness (via dialogue/search module)               │
│  • Session management (Redis)                                   │
│  • Query expansion & relevance detection                        │
│  • Message template formatting                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Context-enriched question
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│            LLM PROVIDER (Anthropic/OpenAI/Ollama)              │
│              (PAI - Prompt as Interface)                        │
│                                                                  │
│  • Receives question + MCP tools metadata                       │
│  • Generates Python script with tool calls                      │
│  • Returns code + explanation                                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Generated Python script
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│            EXECUTION SERVER (Port 3002)                         │
│              (Sandboxed Python Runtime)                         │
│                                                                  │
│  • Script syntax validation                                     │
│  • Security scanning (AST analysis)                             │
│  • Execute with resource limits (timeout, memory)               │
│  • Call MCP servers for data retrieval                          │
│  • Error handling & graceful degradation                        │
│  • Result formatting & caching                                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    ┌────────┼────────┐
                    ↓        ↓        ↓
    ┌─────────────────┐ ┌──────────────┐ ┌─────────────────┐
    │  MCP SERVERS    │ │  MCP SERVERS │ │  MCP SERVERS    │
    │                 │ │              │ │                 │
    │ • Financial     │ │ • Analytics  │ │ • Validation    │
    │   (Alpaca,      │ │   (Technical │ │   (Script       │
    │    EODHD)       │ │    Analysis) │ │    security)    │
    │                 │ │              │ │                 │
    └─────────────────┘ └──────────────┘ └─────────────────┘
                             │
                    ┌────────┴────────┐
                    ↓                 ↓
    ┌──────────────────────┐  ┌──────────────────┐
    │  External APIs       │  │  External Data   │
    │                      │  │                  │
    │ • Alpaca Trading     │  │ • Market Data    │
    │ • Alpaca Market      │  │ • Fundamentals   │
    │ • EODHD              │  │ • Historical     │
    │                      │  │                  │
    └──────────────────────┘  └──────────────────┘
                             │
                    Execution results + metadata
                             │
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                      RESULT FORMATTER                           │
│                                                                  │
│  • Structure results (JSON)                                    │
│  • Add descriptions & context                                   │
│  • Cache results (Redis)                                        │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             │ Formatted JSON response
                             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Next.js)                           │
│                                                                  │
│  • Display results                                              │
│  • Parameter adjustment UI                                      │
│  • Re-run capability                                            │
│  • Chat history                                                 │
│  • Real-time progress (WebSocket)                               │
└─────────────────────────────────────────────────────────────────┘
```

---

## Core System Components

### 1. **Script Edition - API Server** (Port: 8010)
**Purpose**: Central orchestrator for question analysis and script generation.

**Location**: `ollama-server/scriptEdition/apiServer/`

**Responsibilities**:
- Accept incoming questions via HTTP POST
- Validate & sanitize input
- Manage conversation sessions (Redis)
- Track conversation history via dialogue/search modules
- Detect duplicate/related questions (context awareness)
- Query expansion & relevance detection
- Format messages using templates
- Route to appropriate LLM provider
- Rate limiting & throttling
- Authentication & authorization (future)
- Audit logging

**Tech Stack**:
- Framework: FastAPI (Python)
- Session Storage: Redis (conversation state, cache)
- Data Storage: Database-agnostic (supports SQL/NoSQL via abstraction layer)
- Search: Chroma DB (semantic search via dialogue/search module)

**Key Endpoints**:
```
POST   /analyze                    - Submit question for analysis
GET    /health                     - Health check
GET    /models                     - List available models
POST   /conversation/confirm       - Confirm query expansion
GET    /conversation/{session_id}  - Get session context
GET    /conversation/sessions      - List active sessions
GET    /debug/mcp-tools            - Debug MCP tools (dev only)
GET    /debug/system-prompt        - Debug system prompt (dev only)
```

**Data Flow**:
1. User submits question with `session_id` and `auto_expand` flag
2. Server validates input (sanitization, length limits)
3. Fetches conversation context from Redis (session state)
4. Runs dialogue/search module for context awareness
   - Detects if question is duplicate/related to previous
   - Optionally expands query for clarity
5. Formats message using template
6. Sends to LLM provider with available MCP tools
7. Returns generated script to user

---

### 2. **LLM Provider** (Anthropic/OpenAI/Ollama)
**Purpose**: Generate Python scripts and explanations using PAI (Prompt as Interface) pattern.

**Supported Providers**:
- Anthropic Claude
- OpenAI GPT-4
- Ollama (local, can run via Docker)

**Location**: `ollama-server/scriptEdition/apiServer/llm/providers/`

**Responsibilities**:
- Load available MCP tools metadata dynamically
- Receive enriched question + conversation context
- Generate executable Python script that calls MCP tools
- Produce explanation of analysis approach
- Handle tool schema and parameter generation
- Manage context window (conversation history)

**Architecture Pattern: PAI (Prompt as Interface)**
- LLM receives structured system prompt with available MCP tools
- LLM generates Python code that uses MCP function calls
- LLM returns code + explanation ready for execution

**System Prompt Structure**:
```
[Base Instructions]
You are a financial analysis assistant. Given a question and available MCP tools,
generate:
1. Python code that executes the analysis
2. Clear explanation of the approach

[Available MCP Functions]
Financial Server Tools:
- alpaca_market_stocks_bars(symbol, timeframe, limit)
- alpaca_market_stocks_snapshots(symbols)
- eodhd_fundamentals(symbol)
- [... auto-discovered from MCP servers ...]

Analytics Server Tools:
- calculate_sma(prices, period)
- calculate_volatility(returns, period)
- [... auto-discovered from MCP servers ...]

[Output Format]
Return valid JSON with:
{
  "python_code": "...valid executable Python...",
  "explanation": "...step-by-step explanation...",
  "mcp_calls": ["function1", "function2", ...]
}

[Important Rules]
- Use ONLY the MCP functions listed above
- No hardcoded data
- Parameterize all inputs
- Return structured JSON results
```

**Output Examples**:
- Python Code: Script with MCP function calls, error handling, structured result formatting
- Explanation: "This analysis uses alpaca_market_stocks_bars to fetch 30-day OHLC data, then calculates volatility using daily returns"

---

### 3. **Execution Server** (Port: 3002)
**Purpose**: Sandboxed execution of generated Python scripts with MCP integration.

**Location**: `mcp-server/shared_script_executor.py`, `mcp-server/http_script_execution_server.py`

**Responsibilities**:
- Receive Python script from API Server
- Perform syntax validation (Python AST parsing)
- Security scanning:
  - Block system calls (os.system, subprocess)
  - Block file access (open, read, write)
  - Block network calls (requests, urllib without MCP)
  - Block dangerous imports
- Set up execution environment with timeout/memory limits
- Inject MCP client into execution context
- Execute script with exception handling
- Monitor resource usage (CPU, memory, time)
- Return structured results or errors
- Cache results (Redis)

**Validation Rules**:
```
BLOCKED:
- import os, subprocess, sys, shutil, socket, requests
- os.system, os.exec, subprocess.*
- open(), read(), write()
- __import__, eval, exec
- File system operations
- Direct network access

ALLOWED:
- MCP function calls (via injected mcp_client)
- pandas, numpy, scipy operations
- Basic Python: loops, conditionals, functions
- Math: math.*, operator.*
- JSON serialization
- Data transformations
```

**Execution Context Setup**:
```python
# Injected into execution environment
mcp_client = MCPClient(
    financial_server="http://localhost:3003",
    analytics_server="http://localhost:3004",
    validation_server="http://localhost:3005"
)

# Available in script for calling MCP tools
# Example: data = mcp_client.call("alpaca_market_stocks_bars", {"symbol": "AAPL", ...})
```

**Validation Output**:
```json
{
  "valid": true,
  "errors": [],
  "warnings": ["Long-running operation detected"],
  "security_score": 95,
  "estimated_runtime_ms": 1200,
  "mcp_calls": ["alpaca_market_stocks_bars", "calculate_sma"]
}
```

**Execution Output**:
```json
{
  "success": true,
  "result": {...execution result...},
  "execution_time_ms": 2345,
  "mcp_calls_made": [...],
  "errors": [],
  "warnings": []
}
```

---

### 4. **MCP Servers** (Ports: 3003-3005)

#### 4a. **Financial Data MCP Server** (Port: 3003)
**Location**: `mcp-server/financial_server.py`

**Purpose**: Provide access to financial data from external APIs via unified interface.

**Architecture**:
```
External APIs (Alpaca, EODHD)
        ↓
mcp-server/financial/vendors/ (API wrappers)
  ├── alpaca.py (Alpaca API integration)
  ├── eodhd.py (EODHD API integration)
  └── mocks/ (Mock data for testing)
        ↓
mcp-server/financial/schemas.py (Data standardization)
        ↓
mcp-server/financial_server.py (MCP Server)
```

**Data Wrapping Strategy**:
- Raw API responses are wrapped in standardized schemas
- Alpaca/EODHD are NOT directly exposed in MCP tools
- All data flows through transformation layer
- Vendor-specific differences are abstracted away

**Tools Available** (Standardized across vendors):
```
Market Data:
- alpaca_market_stocks_snapshots(symbols: list[str]) → dict
- alpaca_market_stocks_bars(symbol: str, timeframe: str, limit: int) → dict
- alpaca_market_crypto_snapshots(symbols: list[str]) → dict
- alpaca_market_news(symbols: list[str], limit: int) → dict
- alpaca_market_screener_most_actives(limit: int) → dict

Trading Account:
- alpaca_trading_account() → dict
- alpaca_trading_positions() → dict
- alpaca_trading_orders() → dict

Fundamentals (EODHD):
- eodhd_fundamentals(symbol: str) → dict
- eodhd_dividends(symbol: str, from_date: str, to_date: str) → dict
- eodhd_splits(symbol: str) → dict
```

**Data Transformation Pipeline**:
```
1. Call vendor API (Alpaca/EODHD)
2. Transform to standardized schema (schemas.py)
3. Add metadata (timestamp, source, rate limit info)
4. Cache in Redis
5. Return to caller
```

**Response Schema** (All responses standardized):
```json
{
  "status": "success|error",
  "data": {...vendor data...},
  "metadata": {
    "timestamp": "2025-10-17T12:00:00Z",
    "source": "alpaca|eodhd",
    "endpoint": "...",
    "rate_limit": {"remaining": 95, "reset_at": "..."}
  }
}
```

#### 4b. **Analytics MCP Server** (Port: 3004)
**Location**: `mcp-server/analytics_server.py`

**Purpose**: Technical analysis, risk metrics, and portfolio optimization.

**Architecture**:
```
mcp-server/analytics/
  ├── indicators/
  │   ├── technical.py (SMA, EMA, RSI, MACD, etc.)
  │   ├── momentum/ (Momentum indicators)
  │   ├── volatility/ (Volatility indicators)
  │   └── volume/ (Volume indicators)
  ├── risk/
  │   ├── metrics.py (VaR, Sharpe, Sortino, etc.)
  │   └── models.py (Risk models)
  ├── portfolio/
  │   ├── optimization.py (Portfolio weights optimization)
  │   ├── metrics.py (Portfolio performance metrics)
  │   ├── allocation.py (Asset allocation analysis)
  │   └── simulation.py (Backtesting/simulation)
  ├── performance/
  │   └── metrics.py (Return analysis, Drawdown, etc.)
  └── analytics_server.py (MCP Server)
```

**Tools Available** (Industry-standard calculations):
```
Technical Indicators:
- calculate_sma(prices: list[float], period: int) → dict
- calculate_ema(prices: list[float], period: int) → dict
- calculate_rsi(prices: list[float], period: int) → dict
- calculate_macd(prices: list[float]) → dict
- calculate_bollinger_bands(prices: list[float], period: int) → dict
- calculate_atr(high: list, low: list, close: list, period: int) → dict

Risk Metrics:
- calculate_volatility(returns: list[float], period: int) → dict
- calculate_sharpe_ratio(returns: list[float], risk_free_rate: float) → dict
- calculate_sortino_ratio(returns: list[float], target_return: float) → dict
- calculate_max_drawdown(prices: list[float]) → dict
- calculate_var(returns: list[float], confidence: float) → dict

Portfolio Analysis:
- calculate_correlation_matrix(price_series: dict) → dict
- optimize_portfolio_weights(expected_returns: list, cov_matrix: list) → dict
- calculate_portfolio_metrics(weights: list, returns: dict) → dict

Signal Generation:
- detect_sma_crossover(prices: list[float], short_window: int, long_window: int) → dict
- detect_support_resistance(prices: list[float], lookback: int) → dict
```

**Libraries Used** (Industry Standard):
- `talib-binary` - Technical analysis indicators (proven TA calculations)
- `empyrical` - Risk and performance metrics (verified portfolio metrics)
- `PyPortfolioOpt` - Portfolio optimization (Modern Portfolio Theory)
- `pandas/numpy` - Data manipulation and numerical computation

#### 4c. **Validation MCP Server** (Port: 3005)
**Location**: `mcp-server/mcp_script_validation_server.py`

**Purpose**: Script validation before execution (integrated into Execution Server)

**Tools Available**:
```
- validate_python_script(code: str) → dict
  Returns: {valid: bool, errors: [], warnings: [], security_score: int}

- check_mcp_calls(code: str) → list[str]
  Returns: List of MCP functions referenced in script

- estimate_runtime(code: str) → int
  Returns: Estimated runtime in milliseconds
```

**Validation Logic** (AST-based analysis):
```python
# Built into Execution Server - validates before execution
1. Parse Python code into AST
2. Check for blocked imports/calls
3. Verify all MCP calls exist
4. Estimate runtime complexity
5. Return validation result
```

---

### 5. **Data Storage Layer**

#### 5a. **Redis** (Port: 6379)
**Purpose**: High-speed caching and session management.

**Storage Keys** (Database-agnostic):
```
# Chat sessions (key-value store)
sessions:{session_id} → TTL 7 days
{
  "session_id": "...",
  "user_id": "...",
  "messages": [...],
  "context": {...},
  "expanded_queries": [...],
  "last_activity": "..."
}

# Execution results cache
result:{hash(question+params)} → TTL 24 hours
{
  "result": {...},
  "timestamp": "...",
  "execution_time_ms": 1234
}

# Rate limiting (atomic counters)
rate_limit:{user_id}:{endpoint} → TTL 1 hour
count: incremented per request

# Context awareness (semantic search cache)
similar_questions:{question_hash} → TTL 7 days
[similar_question_ids]

# MCP tool schemas (cache)
mcp_tools:{server_name} → TTL 1 hour
[tool_definitions]
```

#### 5b. **Persistent Database** (SQL or NoSQL)
**Purpose**: Long-term storage of user data, execution history, audit logs.

**Location**: Database-agnostic abstraction layer (to be implemented)

**Data Entities** (Database-agnostic schema):

```
User Entity:
{
  id: String (unique identifier),
  email: String (unique),
  created_at: DateTime,
  updated_at: DateTime,
  metadata: Object (flexible user data)
}

ChatSession Entity:
{
  id: String (unique identifier),
  user_id: String (reference to User),
  title: String,
  created_at: DateTime,
  updated_at: DateTime,
  metadata: Object
}

ChatMessage Entity:
{
  id: String (unique identifier),
  session_id: String (reference to ChatSession),
  role: String ('user', 'assistant', 'system'),
  content: String,
  metadata: Object (MCP calls made, execution time, etc.),
  created_at: DateTime,
  
  Indexes:
  - (session_id, created_at) for conversation retrieval
}

Execution Entity (Audit Trail):
{
  id: String (unique identifier),
  user_id: String (reference to User),
  session_id: String (reference to ChatSession),
  question: String,
  generated_script: String,
  status: String ('pending', 'running', 'success', 'failed'),
  result: Object (execution output),
  error: String (if failed),
  execution_time_ms: Number,
  started_at: DateTime,
  completed_at: DateTime,
  mcp_calls: Array[String],
  created_at: DateTime,
  
  Indexes:
  - (user_id, created_at) for user history
  - (session_id, created_at) for session execution history
  - (status) for execution tracking
}

AuditLog Entity:
{
  id: String (unique identifier),
  user_id: String (reference to User),
  action: String (question_submitted, script_generated, execution_started, etc.),
  resource_type: String (question, execution, session),
  resource_id: String,
  changes: Object (what changed),
  ip_address: String,
  user_agent: String,
  created_at: DateTime,
  
  Indexes:
  - (user_id, created_at) for user audit trail
  - (action) for action tracking
}

ExecutionCache Entity:
{
  id: String (unique identifier),
  question_hash: String (hash of question + parameters),
  user_id: String,
  result: Object (cached result),
  execution_id: String (reference to Execution),
  created_at: DateTime,
  expires_at: DateTime (TTL: 24 hours),
  hit_count: Number,
  
  Indexes:
  - (question_hash, expires_at) for cache lookup
}
```

**Implementation Options**:
- **SQL**: PostgreSQL, MySQL, etc. (use JSON columns for flexible data)
- **NoSQL**: MongoDB, DynamoDB, etc. (native document storage)
- **Hybrid**: Use both for different entities (e.g., SQL for core, NoSQL for flexible metadata)

---

## Request/Response Contracts

### API Request Format (POST /analyze)
```json
{
  "question": "What are the top 5 most volatile stocks today?",
  "session_id": "sess_123...",
  "auto_expand": true
}
```

### API Response Format (Success)
```json
{
  "success": true,
  "data": {
    "python_code": "import pandas as pd\nfrom mcp_client import ...\n\n# Code that calls MCP functions",
    "explanation": "This analysis retrieves the most active stocks using alpaca screener API, fetches 30-day historical bars, calculates volatility from daily returns, then returns top 5 by volatility.",
    "mcp_calls": ["alpaca_market_screener_most_actives", "alpaca_market_stocks_bars", "calculate_volatility"],
    "execution_id": "exec_789...",
    "session_id": "sess_123..."
  },
  "timestamp": "2025-10-17T12:00:00Z",
  "status": "success"
}
```

### Execution Server Request Format (POST to /execute)
```json
{
  "script": "import pandas...\n# Python code from LLM",
  "execution_id": "exec_789...",
  "timeout_seconds": 30,
  "max_memory_mb": 512
}
```

### Execution Server Response Format (Success)
```json
{
  "success": true,
  "execution_id": "exec_789...",
  "timestamp": "2025-10-17T12:00:00Z",
  "execution_time_ms": 2345,
  "result": {
    "description": "Top 5 most volatile stocks based on 30-day volatility",
    "body": [
      {
        "key": "rank_1",
        "value": "NVDA",
        "description": "NVIDIA - Volatility: 45.2%, Volume: 2.3M shares"
      },
      ...
    ]
  },
  "metadata": {
    "data_sources": ["Alpaca Market Data"],
    "mcp_calls_made": ["alpaca_market_screener_most_actives", "alpaca_market_stocks_bars", "calculate_volatility"],
    "cache_hit": false
  }
}
```

### Execution Server Response Format (Error)
```json
{
  "success": false,
  "execution_id": "exec_789...",
  "error": {
    "code": "EXECUTION_TIMEOUT",
    "message": "Script execution exceeded 30 second limit",
    "details": {
      "timeout_seconds": 30,
      "steps_completed": 2,
      "last_step": "Calculating volatility for 100 symbols"
    }
  },
  "recovery_suggestions": [
    "Try with fewer symbols",
    "Increase timeout to 60 seconds",
    "Simplify the analysis"
  ],
  "timestamp": "2025-10-17T12:00:00Z"
}
```

### Conversation Context Response Format (GET /conversation/{session_id}/context)
```json
{
  "success": true,
  "session_id": "sess_123...",
  "context": {
    "messages": [
      {
        "role": "user",
        "content": "What is AAPL's current price?",
        "created_at": "2025-10-17T11:00:00Z"
      },
      {
        "role": "assistant",
        "content": "The current price is $224.50...",
        "created_at": "2025-10-17T11:00:05Z"
      }
    ],
    "expanded_queries": [
      {
        "original": "What is AAPL's current price?",
        "expanded": "What is the current price of AAPL stock along with bid-ask spread and volume?",
        "confidence": 0.95
      }
    ],
    "similar_previous_questions": [
      {
        "question": "Show me QQQ price",
        "similarity_score": 0.72,
        "session_id": "sess_456...",
        "timestamp": "2025-10-16T15:00:00Z"
      }
    ]
  },
  "timestamp": "2025-10-17T12:00:00Z"
}
```

---

## Security Architecture

### Authentication & Authorization
```
Flow:
1. User logs in (OAuth 2.0 / JWT)
2. API server validates token
3. Generate session ID (stored in Redis)
4. All requests include session_id in headers
5. Session expires after TTL (default 24 hours)

Headers:
Authorization: Bearer {jwt_token}
X-Session-ID: sess_123...
X-User-ID: user_456...
```

### Input Validation & Sanitization
```
1. Length limits (questions max 1000 chars)
2. Character whitelist (alphanumeric, basic punctuation)
3. SQL injection prevention (parameterized queries)
4. Command injection prevention (no shell execution)
5. XSS prevention (HTML escaping)
6. Rate limiting (10 requests/min per user)
```

### Script Execution Sandbox
```
1. Script validation (security scan before execution)
2. Restricted Python environment:
   - No system imports (os, sys, subprocess)
   - No file I/O
   - No network calls
   - Only MCP-provided functions
3. Resource limits:
   - CPU: 1 core per execution
   - Memory: 512MB default, 2GB max
   - Timeout: 30s default, 120s max
4. No root/elevated privileges
```

### Credentials Management
```
Environment Variables (`.env`):
ALPACA_API_KEY=pk_...
ALPACA_SECRET_KEY=sk_...
EODHD_API_KEY=...
OPENAI_API_KEY=...
JWT_SECRET=...
REDIS_URL=redis://...
DATABASE_URL=postgresql://...

Vault Integration (Production):
- HashiCorp Vault for secret rotation
- AWS Secrets Manager alternative
- Automatic key rotation every 90 days
```

---

## Error Handling Strategy

### Error Hierarchy
```
1. Validation Error (4xx)
   - Invalid question format
   - Missing parameters
   - Rate limit exceeded

2. Execution Error (5xx)
   - MCP server unavailable
   - Script timeout
   - Resource limit exceeded

3. Data Error (5xx)
   - API rate limit hit
   - API temporary failure
   - Insufficient data

4. System Error (5xx)
   - Database connection error
   - Redis connection error
   - Internal server error
```

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "EXECUTION_TIMEOUT",
    "message": "Script execution exceeded 30 second limit",
    "details": {
      "timeout_seconds": 30,
      "steps_completed": 2,
      "last_step": "Calculating volatility for 100 symbols"
    }
  },
  "recovery_suggestions": [
    "Try with fewer symbols",
    "Increase timeout to 60 seconds",
    "Simplify the analysis"
  ],
  "timestamp": "2025-10-17T12:00:00Z",
  "request_id": "req_123..."
}
```

---

## Performance & Optimization

### Caching Strategy
```
Level 1: Redis (milliseconds)
- Query results (TTL: 24h)
- Session data (TTL: 7d)
- API rate limit state (TTL: 1h)
- Frequent MCP calls (TTL: 1h)

Level 2: PostgreSQL (persistent)
- Execution history
- User data
- Audit logs

Cache Invalidation:
- Result cache: Time-based (24h TTL)
- Rate limit: Per-request increment
- Session: On logout or timeout
- Manual: Admin invalidation endpoint
```

### Query Optimization
```
Database:
- Index on (user_id, created_at) for chat history
- Index on (status) for execution tracking
- Pagination: 50 items per page default
- Query timeout: 5 seconds

API Rate Limiting:
- Per-user: 100 requests/hour
- Per-endpoint: 1000 requests/hour global
- Burst allowance: 10 requests/second
- Backoff strategy: Exponential (1s, 2s, 4s...)
```

### Monitoring & Observability
```
Structured Logging (JSON):
{
  "timestamp": "2025-10-17T12:00:00Z",
  "level": "INFO",
  "service": "api-server",
  "request_id": "req_123...",
  "user_id": "user_456...",
  "action": "question_submitted",
  "duration_ms": 234,
  "status": "success",
  "metadata": {...}
}

Metrics:
- Request latency (p50, p95, p99)
- Execution time (p50, p95, p99)
- Error rate (%)
- Cache hit ratio (%)
- MCP server availability (%)
- Database query time (p95)

Tracing:
- Trace ID generation (UUID per request)
- Span creation at each service boundary
- Latency tracking per span
- Error context in traces
```

---

## Deployment Architecture

### Development Environment
```
docker-compose setup:
- API Server (Port 3001)
- Ollama (Port 11434)
- Execution Server (Port 3002)
- Financial MCP (Port 3003)
- Analytics MCP (Port 3004)
- Validation MCP (Port 3005)
- Redis (Port 6379)
- PostgreSQL (Port 5432)
- Frontend (Port 3000)

Services can be run locally with:
docker-compose up -d
```

### Staging/Production Deployment
```
Architecture:
- Load Balancer (Nginx/HAProxy)
- API Server (3+ instances, auto-scaling)
- Ollama Server (2+ instances for HA)
- Execution Servers (5+ instances, queue-based)
- MCP Servers (3+ instances each)
- Redis Cluster (3+ nodes, master-replica)
- PostgreSQL (Primary + Replica, automated failover)

Deployment Pipeline:
1. Build & test (CI/CD)
2. Blue-green deployment
3. Health checks
4. Gradual traffic shift
5. Rollback capability
```

### High Availability
```
- Load balancer with health checks
- Database replication with automatic failover
- Redis cluster with Sentinel
- Circuit breakers for external APIs
- Graceful degradation (cached results on error)
- Rate limiting to prevent overload
```

---

## Future Enhancements & Roadmap

### Phase 1: Foundation (Current)
- ✅ Basic PAI pattern implementation
- ✅ MCP server integration
- ✅ Script execution
- ⏳ Redis persistence
- ⏳ Chat history tracking

### Phase 2: Robustness (Weeks 2-4)
- ⏳ Context awareness engine (duplicate detection)
- ⏳ Advanced error handling & recovery
- ⏳ Monitoring & alerting
- ⏳ Comprehensive testing

### Phase 3: Performance (Weeks 5-8)
- ⏳ Query optimization
- ⏳ Advanced caching strategies
- ⏳ Load testing & optimization
- ⏳ Performance benchmarking

### Phase 4: Enterprise (Weeks 9+)
- ⏳ Advanced authentication (SAML, SSO)
- ⏳ Fine-grained access control
- ⏳ Audit compliance
- ⏳ Multi-tenancy support
- ⏳ Analytics & usage tracking

---

## Configuration & Environment Variables

```bash
# API Server
API_SERVER_PORT=3001
API_SERVER_HOST=0.0.0.0
CORS_ORIGINS=http://localhost:3000,https://example.com
REQUEST_TIMEOUT_MS=30000
MAX_REQUEST_SIZE_MB=10

# LLM / Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=gpt-oss:20b
LLM_TIMEOUT_SECONDS=60
CONVERSATION_CONTEXT_WINDOW=8000

# Execution Server
EXECUTION_SERVER_PORT=3002
EXECUTION_TIMEOUT_SECONDS=30
MAX_EXECUTION_MEMORY_MB=512
SCRIPT_ISOLATION=true

# MCP Servers
FINANCIAL_MCP_URL=http://localhost:3003
ANALYTICS_MCP_URL=http://localhost:3004
VALIDATION_MCP_URL=http://localhost:3005

# External APIs
ALPACA_API_KEY=pk_...
ALPACA_SECRET_KEY=sk_...
EODHD_API_KEY=...

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/qna_ai
DATABASE_POOL_SIZE=10
DATABASE_TIMEOUT_SECONDS=5

# Redis
REDIS_URL=redis://localhost:6379
REDIS_TTL_SECONDS=86400
REDIS_KEY_PREFIX=qna_ai:

# Security
JWT_SECRET=...
JWT_EXPIRES_IN_HOURS=24
RATE_LIMIT_REQUESTS_PER_HOUR=100
RATE_LIMIT_REQUESTS_PER_SECOND=10

# Logging
LOG_LEVEL=INFO
LOG_FORMAT=json
SENTRY_DSN=...

# Features
ENABLE_RESULT_CACHING=true
ENABLE_CONTEXT_AWARENESS=true
ENABLE_AUDIT_LOGGING=true
```

---

## Related Issues & Implementation Roadmap

This architecture document supports the following GitHub issues:

**Core Architecture**: #4
**Data Persistence**: #2, #3, #5
**MCP Integration**: #6, #7
**Execution**: #8, #9
**API Standards**: #13
**Error Handling**: #14
**Caching**: #15
**Security**: #17-20
**Testing**: #21-25
**DevOps**: #26-35
**Documentation**: #39-41

---

## Quick Start

### Start Development Environment
```bash
# Install dependencies
npm install
pip install -r requirements.txt

# Start services (docker-compose)
docker-compose up -d

# Run migrations
npm run migrate

# Start frontend
npm run dev

# Start API server
python mcp-server/api_server.py

# Verify all services
curl http://localhost:3001/health
curl http://localhost:3002/health
curl http://localhost:3003/health
```

### Example Request
```bash
curl -X POST http://localhost:3001/api/analyze \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer {token}" \
  -d '{
    "question": "What is the current price of AAPL?",
    "context": {
      "session_id": "...",
      "user_id": "..."
    }
  }'
```

---

## Glossary

- **PAI**: Prompt as Interface - Using LLM as orchestrator between user intent and backend capabilities
- **MCP**: Model Context Protocol - Standardized protocol for LLM tool integration
- **Schema**: Data structure definition
- **Workflow**: Step-by-step process to answer a question
- **Execution Plan**: Python script to be executed
- **Context Awareness**: Detecting duplicate/related questions
- **TTL**: Time To Live - Cache expiration time
- **Circuit Breaker**: Pattern to prevent cascading failures
- **Blue-Green Deployment**: Two identical production environments for zero-downtime updates

---

**Document Version**: 1.0
**Last Updated**: 2025-10-17
**Status**: Complete for Phase 1 (Basic Architecture)
