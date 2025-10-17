# Services Integration Guide

## Overview
This document describes the complete integration of the database persistence layer (MongoDB) with the FastAPI server through a multi-layer service architecture.

## Architecture Layers

### 1. Database Layer (`db/`)
- **MongoDBClient**: Async MongoDB connection management
- **Repositories**: Data access abstractions (ChatRepository, AnalysisRepository, ExecutionRepository, CacheRepository)
- **RepositoryManager**: Unified access point for all repositories
- **Schemas**: Pydantic models for type-safe data validation (8 collections)

### 2. Service Layer (`services/`)
Wraps repository operations with business logic and error handling:

- **ChatHistoryService**: Manages chat sessions and messages
  - `start_session()` - Create new conversation
  - `add_user_message()` - Store user queries
  - `add_assistant_message_with_analysis()` - Store AI responses with embedded analysis
  - `get_conversation_history()` - Retrieve chat context for LLM

- **CacheService**: Manages analysis result caching
  - `get_cached_result()` - Check cache before processing
  - `cache_analysis_result()` - Store results with TTL
  - `invalidate_analysis_cache()` - Clear cache when needed

- **AnalysisPersistenceService**: Manages analysis storage and reuse
  - `create_analysis()` - Save analysis as reusable template
  - `get_similar_analyses()` - Find related analyses
  - `can_reuse_analysis()` - Check if analysis applies to new question
  - `search_analyses()` - Full-text search

- **AuditService**: Tracks execution history
  - `log_execution_start()` - Record execution start
  - `log_execution_complete()` - Record execution result
  - `get_execution_history()` - Retrieve session/user execution logs

### 3. API Routes Layer (`api/routes.py`)
Orchestrates services and implements business workflows:

#### Updated `analyze_question()` Workflow
```
Step 0:   Initialize/retrieve session
Step 0.5: Add user message to chat history
Step 1:   Check cache for existing results
Step 2:   Context-aware query expansion
Step 3:   Similar analysis search
Step 4:   Main analysis generation (LLM)
Step 6:   Save analysis (search service + MongoDB)
Step 6b:  Persist to MongoDB (if available)
Step 7:   Add assistant message with embedded analysis
Step 8:   Build enhanced response
Step 9:   Cache final result
```

#### New Route Handlers
- `get_chat_history(session_id)` - Retrieve all messages in a session
- `get_user_sessions(user_id, limit)` - List all sessions for user
- `get_reusable_analyses(user_id)` - Get all saved analysis templates
- `search_analyses(user_id, search_text, limit)` - Search analyses
- `get_execution_history(session_id, limit)` - Get execution logs

### 4. Server Layer (`server.py`)
Manages application lifecycle and dependency injection:

```python
# Lifespan management
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Initialize MongoDB and services
    db_client = MongoDBClient()
    repo_manager = RepositoryManager(db_client)
    await repo_manager.initialize()
    
    # Create service instances
    chat_history_service = ChatHistoryService(repo_manager)
    cache_service = CacheService(repo_manager)
    analysis_persistence_service = AnalysisPersistenceService(repo_manager)
    audit_service = AuditService(repo_manager)
    
    # Initialize API routes with all services
    api_routes = APIRoutes(
        analysis_service,
        search_service,
        chat_history_service,
        cache_service,
        analysis_persistence_service,
        audit_service
    )
    
    yield
    
    # Shutdown: Clean up resources
    await repo_manager.shutdown()
```

## Data Flow

### Question Analysis Flow
```
User Request (with user_id, session_id)
    ↓
[Step 0-0.5] Chat History Service: Create session + store user message
    ↓
[Step 1] Cache Service: Check for existing result (cache hit = fast return)
    ↓
[Step 2-4] LLM Analysis: Context expansion + similarity search + generation
    ↓
[Step 6-6b] Analysis Persistence: Save to both search service & MongoDB
    ↓
[Step 7] Chat History Service: Store assistant message + embedded AnalysisModel
    ↓
[Step 7] Audit Service: Log execution details
    ↓
[Step 9] Cache Service: Store result for future queries
    ↓
Response to User (with session_id, analysis_id, cached flag)
```

### Analysis Reuse Flow
```
New User Question
    ↓
Analysis Persistence Service: Find similar analyses
    ↓
Can we reuse? → YES: Return cached analysis directly
              → NO: Generate new analysis
```

## HTTP Endpoints

### Analysis & Conversation
- `POST /analyze` - Analyze financial question (main endpoint)
- `GET /conversation/sessions` - List active sessions
- `GET /conversation/{session_id}/context` - Get session context

### Chat History (NEW)
- `GET /chat/{session_id}/history` - Get all messages in session
- `GET /user/{user_id}/sessions` - List all user sessions
- `GET /session/{session_id}/executions` - Get execution history

### Analysis Management (NEW)
- `GET /user/{user_id}/analyses` - List reusable analyses
- `GET /user/{user_id}/analyses/search?q=text` - Search analyses

## Graceful Degradation

If MongoDB is unavailable:
1. Services are initialized as `None`
2. Routes check if service exists before calling
3. Warnings logged, but requests don't fail
4. Server continues with file-based storage only

```python
try:
    # Initialize MongoDB
    db_client = MongoDBClient()
except Exception as e:
    logger.warning("MongoDB failed, continuing without persistence")
    db_client = None  # Services will be None
    # Server continues working without chat history/caching
```

## Configuration

### Environment Variables
```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB=financial_analysis
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=your-key-here
```

### MongoDB Collections
1. **users** - User accounts and metadata
2. **chat_sessions** - Conversation sessions
3. **chat_messages** - Messages with embedded AnalysisModel
4. **analyses** - Reusable analysis templates
5. **executions** - Execution logs and audit trail
6. **saved_analyses** - Saved analyses with metadata
7. **audit_logs** - Detailed audit logs
8. **cache** - Result cache with TTL

## Key Features

### 1. Embedded Analysis Storage
- Complete AnalysisModel stored directly in ChatMessage
- No need to re-query DB for analysis details
- Full analysis available for direct replay

### 2. Analysis Reuse
- Similar query detection
- Reuse evaluation before LLM call
- Template-based analysis with parameters

### 3. Result Caching
- TTL-based cache (24 hours default)
- Both successful and failed results cached
- Cache invalidation on analysis modification

### 4. Audit Trail
- Complete execution history
- User action tracking
- Performance metrics (execution time)

### 5. Conversation Context
- Full message history for LLM context
- Query expansion confidence scores
- Multi-turn query handling

## Testing the Integration

### 1. Start MongoDB
```bash
docker run -d -p 27017:27017 mongo:latest
```

### 2. Start the server
```bash
python server.py
```

### 3. Test analysis with persistence
```bash
curl -X POST http://localhost:8010/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is market volatility?",
    "user_id": "user-123",
    "session_id": "session-456"
  }'
```

### 4. Check chat history
```bash
curl http://localhost:8010/chat/session-456/history
```

### 5. Get user sessions
```bash
curl http://localhost:8010/user/user-123/sessions
```

## Error Handling

All services include:
- Try-catch blocks for graceful error handling
- Logging at appropriate levels (info/warning/error)
- Non-blocking failures (e.g., cache failures don't fail request)
- Fallback behavior (e.g., generate new analysis if reuse fails)

## Performance Considerations

1. **Caching**: Reduces LLM calls for repeated queries
2. **Embedded Analysis**: No extra DB lookups needed in chat
3. **Async/Await**: Non-blocking I/O throughout
4. **TTL Indexes**: MongoDB automatically cleans up old cache
5. **Lazy Loading**: Analyses loaded only when needed

## Future Enhancements

1. **Real-time Updates**: WebSocket support for live chat
2. **Advanced Analytics**: User behavior tracking and analytics
3. **Parameter Optimization**: Automatic parameter suggestion
4. **Model Comparison**: A/B testing different LLM models
5. **Advanced Search**: Semantic search with embeddings
6. **Batch Operations**: Process multiple analyses efficiently
