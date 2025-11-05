# QnA AI Admin - Claude Developer Guide

## Project Overview
This is a distributed financial analysis platform that transforms natural language investment questions into executable Python code using AI. The system features a modern Next.js frontend with a sophisticated backend architecture that generates, validates, and executes financial analysis scripts in real-time.

### Core Architecture
- **Frontend**: Next.js 15 with TypeScript (Port 3003), featuring chat interfaces, progress tracking, and real-time analysis results
- **API Server**: FastAPI-based script generation server (Port 8010) with session management and context awareness  
- **Execution Server**: Sandboxed Python runtime (Port 3002) with security validation and resource limits
- **MCP Servers**: Model Context Protocol servers for financial data, analytics, and validation
- **Storage**: Redis for session/cache management, MongoDB for persistence, with async queue processing

### Key Features
- **Natural Language to Code**: AI-powered generation of Python analysis scripts from investment questions
- **Real-time Execution**: Sandboxed script execution with progress tracking and streaming results
- **Session Management**: Persistent chat sessions with context awareness and conversation history
- **Security**: AST-based validation, resource limits, and execution sandboxing
- **Async Processing**: Queue-based architecture for handling long-running analysis tasks

## Development Workflow

### Starting Development
```bash
# Frontend (Next.js)
cd frontend
npm install
npm run dev # Runs on http://localhost:3003

# Backend Services
cd backend/scriptEdition/apiServer
pip install -r requirements.txt
python server.py # API Server on port 8010

cd backend/executionServer  
python queue_worker.py # Execution Server on port 3002

# MCP Servers
cd backend/mcp-server
python financial_server.py # Port 3003
python analytics_server.py # Port 3004
```

### Build and Production
```bash
npm run build
npm run start
npm run lint
```

## Role-Based Interaction Pattern

### Phase 1: Retail Investor (Question Generation)
- Act as a retail investor asking relevant investment/trading questions
- Questions should be singular and not contain "add"
- Ensure questions are distinct from existing ones in `data/approved.json` and `data/experimental.json`
- **IMPORTANT**: Questions must be answerable using APIs listed in:
  - `alpaca.marketdata.spec.json`
  - `alpaca.trading.spec.json` 
  - `EODHD.spec.json`
- **CRITICAL**: Don't create questions that can't be answered using above specs
- All questions should be answerable either directly using the specs or through Python analysis based on data from specs

### **CRITICAL VALIDATION PROCESS:**
1. **Generate Initial Question**: Create a question you think can be answered using available APIs
2. **Create Workflow**: Generate detailed step-by-step workflow using specific API endpoints
3. **Validate Alignment**: Check if the workflow actually answers the specific question asked
4. **Iterate if Needed**: If workflow doesn't fully answer the question, adjust the question to match what the workflow can deliver
5. **Repeat**: Continue steps 2-4 until question and workflow are perfectly aligned

**Example Validation:**
- Question: "What stocks have the highest volatility?" 
- Workflow: Uses most-active stocks screener first
- Validation Issue: This answers "highest volatility among active stocks" not "highest volatility overall"
- Adjusted Question: "What actively traded stocks have the highest volatility over the past 30 days?"

- Write the question in the left panel

### Phase 2: Financial Advisor/Quant/Accountant (JSON Output Creation)
- Switch to advisor/quant/accountant or trading customer service role
- Create well-formatted JSON outputs following the required structure:
  - Top-level `description`: Explains what the entire analysis represents and its purpose
  - `body` array: Contains individual data points in {key, value, description} format
- Each data point should include:
  - `key`: Unique identifier for the metric
  - `value`: The actual calculated or retrieved data
  - `description`: Clear explanation of what it represents, how it was calculated, and why it matters
- Output should directly answer the specific question asked in language retail investors can understand



## Available APIs
- **Alpaca Market Data** (`alpaca.marketdata.spec.json`): Stock pricing, options, crypto, forex, logos, corporate actions, screener, news
- **Alpaca Trading** (`alpaca.trading.spec.json`): Account management, positions, orders, portfolio management  
- **EODHD** (`EODHD.spec.json`): Additional financial data endpoints

## Current System Architecture

### Request Flow
```
User Question (Frontend) 
    ↓
API Server (Port 8010) - Context awareness, session management
    ↓  
LLM Provider (Anthropic/OpenAI/Ollama) - Code generation
    ↓
Execution Server (Port 3002) - Script validation & execution
    ↓
MCP Servers (Financial Data + Analytics) - Data retrieval & processing
    ↓
Results (JSON) → Frontend Display
```

### Core Components

#### Script Edition API Server (`backend/scriptEdition/apiServer/`)
- **FastAPI-based** request handler with async processing
- **Session Management** via Redis for conversation continuity
- **Context Awareness** with dialogue/search modules for question expansion
- **Multi-provider LLM Support** (Anthropic, OpenAI, Ollama)
- **Progress Tracking** with Server-Sent Events (SSE) for real-time updates

#### Execution Engine (`backend/executionServer/`)  
- **Sandboxed Python Runtime** with AST-based security validation
- **Resource Limits** (timeout, memory, CPU constraints)
- **Queue-based Processing** for handling concurrent analysis requests
- **MCP Integration** for accessing financial data and analytics tools

#### MCP Financial & Analytics Servers (`backend/mcp-server/`)
- **Financial Server**: Market data, trading account, fundamentals (Alpaca, EODHD APIs)
- **Analytics Server**: Technical indicators, risk metrics, portfolio optimization
- **Industry Libraries**: talib-binary, empyrical, PyPortfolioOpt for proven calculations
- **Real Data Integration**: All tools use actual financial data (no mock data)

## Adding New JSON Outputs
1. Create JSON file in `experimental/` (e.g., `MyOutput.json`)
   - **Include descriptive field explanations for each data point**
   - **Structure data to directly answer the specific question**
   - **Add metadata fields explaining data sources and calculations**
2. Register in `experimental/registry.ts` with unique ID, name, file path
3. Add entry to **beginning** of `data/experimental.json` so it appears first on main screen
4. Entry metadata should include:
   - `id`, `name`, `file`, `question` (required)
   - `description`, `apis`, `followUp`, `output` (optional)
5. **New JSON outputs automatically appear on main screen for approval/preview**

## Data Model Structure
```jsonc
{
  "id": "unique-id",
  "name": "Display Name",
  "file": "experimental/Component.json",
  "description": "Brief description",
  "question": "What question does this answer?",
  "apis": ["marketdata:/endpoint", "trading:/endpoint"],
  "followUp": ["Related question suggestions"],
  "workflow": [
    "Step 1: Get list of active stocks using /v1beta1/screener/stocks/most-actives",
    "Step 2: Fetch 30-day historical data using /v2/stocks/bars with timeframe=1Day",
    "Step 3: Calculate volatility metrics from OHLC data",
    "Step 4: Rank and display results"
  ]
}
```

## JSON Output Structure
All JSON output files must follow this structure:
```jsonc
{
  "description": "Overall explanation of what this JSON output represents, its purpose, and how it answers the specific question asked. Should be written for retail investors to easily understand.",
  "body": [
    {
      "key": "unique_identifier_for_data_point",
      "value": "actual_data_value_or_calculation_result", 
      "description": "Clear explanation of what this specific data point represents, how it was calculated, and why it matters to the investor"
    },
    {
      "key": "another_data_point",
      "value": 42.5,
      "description": "Another data point with its explanation and context"
    }
    // ... more data points as needed
  ]
}
```

**IMPORTANT**: The `workflow` field must contain a detailed step-by-step approach to get the required data using the available API specifications. Each step should specify the exact API endpoint, parameters, and data processing required.

### Workflow Format (Required)
- Represent each step as an object of the form: `{ "type": "fetch|engine|compute", "description": "Step N: ...", "function": "mcp_function_name" }`.
- Use `type: "fetch"` for network/API calls and include the exact endpoint and parameters. Set `function` to the MCP financial server tool name (e.g., "alpaca-market_stocks-bars").
- Use `type: "engine"` when Python processing is required (clearly state inputs, outputs, and calculations performed). Set `function` to the MCP analytics server tool name (e.g., "calculate_daily_returns", "calculate_rolling_volatility").
- Use `type: "compute"` for lightweight, in-app calculations that do not require Python. Set `function` to "client_compute" for local processing.

## Project Structure
```
├── frontend/                    # Next.js 15 frontend application  
│   ├── src/app/                # App router pages (chat, analysis, backtester)
│   ├── src/components/         # React components (chat, progress, analysis)  
│   └── src/lib/               # Utilities, context, hooks, API client
├── backend/
│   ├── scriptEdition/         # Main API server & execution infrastructure
│   │   ├── apiServer/         # FastAPI server (Port 8010)
│   │   ├── executionServer/   # Script execution worker (Port 3002)  
│   │   └── infrastructure/    # Process management & deployment scripts
│   ├── mcp-server/           # MCP servers for financial data & analytics
│   │   ├── financial/        # Financial data server functions
│   │   ├── analytics/        # Technical analysis & portfolio tools
│   │   └── scripts/          # Generated analysis scripts cache
│   └── shared/               # Common utilities & services
│       ├── analyze/          # Analysis pipeline & code generation
│       ├── db/              # Database repositories & schemas  
│       ├── queue/           # Async processing queues & workers
│       └── services/        # Core business logic services
└── specs/                   # API specifications (Alpaca, EODHD)
```

## Development Notes
- **Database**: Redis for caching/sessions, MongoDB for persistence (async processing)
- **Security**: AST validation, sandboxed execution, resource limits
- **LLM Support**: Anthropic Claude, OpenAI GPT, local Ollama models
- **Real-time**: WebSocket/SSE for progress tracking and live results
- **Production Ready**: Containerized services, queue-based scaling, comprehensive logging
