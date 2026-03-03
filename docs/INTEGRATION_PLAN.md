# Database Layer Integration Plan

## Current Architecture
```
server.py (lifespan, app factory)
├── AnalysisService (LLM interactions)
├── SearchService (Chroma similarity search)
└── APIRoutes (route handlers)
    ├── analyze_question()
    ├── health_check()
    ├── get_session_context()
    └── list_sessions()
```

## New Database Layer
```
db/
├── schemas.py (8 collections)
├── mongodb_client.py (async client)
└── repositories.py (4 repositories + manager)
```

## Integration Points

### 1. **Server Startup (server.py lifespan)**

**Current**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    analysis_service = AnalysisService()
    search_service = SearchService()
    app.state.analysis_service = analysis_service
    app.state.search_service = search_service
    api_routes = APIRoutes(analysis_service, search_service)
    app.state.api_routes = api_routes
    yield
    await analysis_service.close_sessions()
```

**Needed Changes**:
```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize existing services
    analysis_service = AnalysisService()
    search_service = SearchService()
    
    # Initialize database layer
    from db import RepositoryManager, MongoDBClient
    db_client = MongoDBClient()
    repo_manager = RepositoryManager(db_client)
    await repo_manager.initialize()  # Connect and create indexes
    
    # Store in app state
    app.state.analysis_service = analysis_service
    app.state.search_service = search_service
    app.state.repo_manager = repo_manager  # NEW
    
    api_routes = APIRoutes(analysis_service, search_service, repo_manager)  # PASS repo
    app.state.api_routes = api_routes
    
    yield
    
    # Cleanup
    await repo_manager.shutdown()  # NEW
    await analysis_service.close_sessions()
```

---

### 2. **APIRoutes Constructor**

**Current**:
```python
def __init__(self, analysis_service: AnalysisService, search_service: SearchService, 
             code_prompt_builder: CodePromptBuilderService = None, 
             reuse_evaluator: ReuseEvaluatorService = None):
    self.analysis_service = analysis_service
    self.search_service = search_service
```

**Needed Changes**:
```python
def __init__(self, analysis_service: AnalysisService, search_service: SearchService, 
             repo_manager: RepositoryManager = None,  # NEW
             code_prompt_builder: CodePromptBuilderService = None, 
             reuse_evaluator: ReuseEvaluatorService = None):
    self.analysis_service = analysis_service
    self.search_service = search_service
    self.repo = repo_manager  # NEW - for easy access
```

---

### 3. **Analyze Question Endpoint** (KEY INTEGRATION)

**Current Flow**:
```
User Question
  ↓
search_with_context() [Redis/Chroma]
  ↓
code_prompt_builder.create_code_prompt_messages()
  ↓
analysis_service.analyze_question() [LLM]
  ↓
Return Python code + explanation
```

**New Flow** (with database):
```
User Question
  ↓
repo.chat.add_user_message() [MongoDB]  ← SAVE TO DB
  ↓
search_with_context() [Redis/Chroma]
  ↓
code_prompt_builder.create_code_prompt_messages()
  ↓
analysis_service.analyze_question() [LLM]
  ↓
Create AnalysisModel from results
  ↓
repo.chat.add_assistant_message_with_analysis() [MongoDB]  ← SAVE WITH ANALYSIS
  ↓
repo.cache.cache_analysis() [MongoDB]  ← CACHE FOR REUSE
  ↓
Return to user
```

**Code Changes Required**:

```python
async def analyze_question(self, request: QuestionRequest) -> AnalysisResponse:
    # Get or create session
    session_id = request.session_id or await self.repo.chat.start_session(
        user_id=request.user_id,  # Need to get from request
        title=f"Analysis: {request.question[:50]}"
    )
    
    # SAVE USER MESSAGE
    await self.repo.chat.add_user_message(
        session_id=session_id,
        user_id=request.user_id,
        question=request.question,
        query_type=context_result.get('query_type', QueryType.COMPLETE)
    )
    
    # ... existing code for context, search, code generation ...
    
    # When result is ready, CREATE ANALYSIS MODEL
    analysis = AnalysisModel(
        user_id=request.user_id,
        title=f"Analysis: {request.question[:50]}",
        description=result['explanation'],
        result=result['result'],
        parameters=result.get('parameters', {}),
        mcp_calls=result['mcp_calls'],
        generated_script=result['python_code'],
        category="user_query",
        data_sources=["LLM-Generated", "MCP Servers"],
        tags=context_result.get('tags', []),
        is_template=True  # Save as reusable
    )
    
    # SAVE ASSISTANT MESSAGE WITH ANALYSIS
    message_id = await self.repo.chat.add_assistant_message_with_analysis(
        session_id=session_id,
        user_id=request.user_id,
        script=result['python_code'],
        explanation=result['explanation'],
        analysis=analysis,
        mcp_calls=result['mcp_calls']
    )
    
    # CACHE FOR REUSE
    cache_key_params = {
        'lookback_days': result.get('parameters', {}).get('lookback_days'),
        'limit': result.get('parameters', {}).get('limit')
    }
    await self.repo.cache.cache_analysis(
        question=request.question,
        parameters=cache_key_params,
        result=analysis.result,
        analysis_id=analysis.id,
        ttl_hours=24
    )
    
    return AnalysisResponse(
        success=True,
        data={
            'message_id': message_id,
            'session_id': session_id,
            'analysis_id': analysis.id,
            **result
        },
        timestamp=datetime.now().isoformat()
    )
```

---

### 4. **Get Session Context Endpoint**

**Current**:
```python
async def get_session_context(self, session_id: str):
    return context  # From dialogue/search module
```

**Updated**:
```python
async def get_session_context(self, session_id: str):
    # Get from MongoDB instead of Redis
    context = await self.repo.chat.get_session_with_context(session_id)
    return context
```

---

### 5. **List Sessions Endpoint**

**Current**:
```python
async def list_sessions(self):
    # From dialogue module
```

**Updated**:
```python
async def list_sessions(self, user_id: str):
    # Get from MongoDB
    sessions = await self.repo.chat.list_sessions(user_id)
    return [s.dict() for s in sessions]
```

---

## Implementation Steps

### Phase 1: Server Integration
1. Update `server.py` lifespan to initialize `RepositoryManager`
2. Pass `repo_manager` to `APIRoutes`
3. Add database connection/disconnection logging

### Phase 2: Route Integration
1. Update `APIRoutes.__init__()` to accept `repo_manager`
2. Add `user_id` extraction from request (JWT/auth context)
3. Update `analyze_question()` to save messages + analysis to MongoDB

### Phase 3: Caching Integration
1. Check cache before running expensive queries
2. Return cached results when available
3. Cache analysis results after execution

### Phase 4: Conversation Context
1. Update `get_session_context()` to use MongoDB
2. Update `list_sessions()` to use MongoDB
3. Add conversation history retrieval

### Phase 5: Testing
1. Unit tests for repository layer
2. Integration tests with actual MongoDB
3. End-to-end flow testing

---

## Key Decisions

### User ID Management
- Need to extract `user_id` from:
  - JWT token (if auth enabled)
  - Request header
  - Or generate temporary ID for anonymous users

### Session ID Management
- If not provided in request, create new session
- Store session_id in response for client to use in subsequent requests
- Support anonymous sessions with temporary IDs

### Analysis Reuse
- Check cache first (fastest)
- Check MongoDB for similar templates (if cache miss)
- Generate new analysis if no suitable match

### Error Handling
- Database connection errors should be non-blocking
- Fall back to existing services if database is unavailable
- Log database errors but don't fail requests

---

## Files to Modify

1. `server.py` - Startup/shutdown, pass repo to routes
2. `api/routes.py` - Add repo_manager, integrate save/cache logic
3. `api/models.py` - Add user_id to QuestionRequest (optional)

## Files Already Created

1. `db/__init__.py` - Module exports
2. `db/schemas.py` - 8 MongoDB collections
3. `db/mongodb_client.py` - Async MongoDB client
4. `db/repositories.py` - Repository pattern
5. `db/README.md` - Documentation

---

## Environment Variables

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=qna_ai_admin
```

## Deployment Checklist

- [ ] MongoDB service running (local or Atlas)
- [ ] Environment variables set
- [ ] Database indexes created automatically (on app startup)
- [ ] All services can communicate with MongoDB
- [ ] Fallback logic if database unavailable
- [ ] Monitoring/alerting for database errors
