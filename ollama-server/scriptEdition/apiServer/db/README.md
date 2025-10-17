# MongoDB Database Layer

Comprehensive MongoDB-based persistence layer for chat history, analyses, and audit logging.

## Architecture

```
schemas.py
├── UserModel
├── ChatSessionModel
├── ChatMessageModel (stores embedded AnalysisModel)
├── AnalysisModel (reusable analysis templates)
├── ExecutionModel (audit trail)
├── SavedAnalysisModel (saved templates)
├── AuditLogModel
└── CacheModel

mongodb_client.py
└── MongoDBClient (low-level CRUD operations)

repositories.py
├── ChatRepository (conversation workflows)
├── AnalysisRepository (analysis management)
├── ExecutionRepository (execution tracking)
├── CacheRepository (result caching)
└── RepositoryManager (unified access)
```

## Collections

### 1. users
User accounts and profiles.

```javascript
{
  _id: ObjectId,
  email: String (unique),
  username: String,
  created_at: DateTime,
  updated_at: DateTime,
  last_login: DateTime,
  preferences: Object,           // User settings
  metadata: Object
}
```

### 2. chat_sessions
Conversation sessions grouping multiple messages.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  title: String,
  description: String,
  message_count: Number,
  analysis_ids: [ObjectId],      // References to analyses in this session
  context_summary: Object,
  created_at: DateTime,
  updated_at: DateTime,
  last_message_at: DateTime,
  is_archived: Boolean,
  is_favorited: Boolean,
  tags: [String],
  metadata: Object
}
```

### 3. chat_messages
Individual messages with **embedded analysis storage** (KEY FEATURE).

```javascript
{
  _id: ObjectId,
  session_id: ObjectId,
  user_id: ObjectId,
  role: String,                  // "user", "assistant", "system"
  content: String,
  
  // ANALYSIS STORAGE - Full analysis object embedded
  analysis: {
    _id: ObjectId,
    title: String,
    description: String,
    result: {
      description: String,
      body: [
        { key: String, value: Any, description: String },
        ...
      ]
    },
    parameters: Object,           // Original parameters
    mcp_calls: [String],
    generated_script: String,
    execution_time_ms: Number,
    data_sources: [String],
    ...
  },
  analysis_id: ObjectId,         // Also reference for lookups
  
  // Query metadata
  query_type: String,            // "complete", "contextual", etc.
  original_question: String,
  expanded_question: String,
  expansion_confidence: Float,
  
  // Script metadata
  generated_script: String,
  script_explanation: String,
  mcp_calls: [String],
  
  // Execution metadata
  execution_id: ObjectId,
  execution_status: String,
  execution_time_ms: Number,
  execution_error: String,
  
  created_at: DateTime,
  updated_at: DateTime,
  message_index: Number,
  metadata: Object
}
```

### 4. analyses
Standalone analyses that can be reused without LLM regeneration.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  title: String,
  description: String,
  category: String,
  
  result: {
    description: String,
    body: [
      { key: String, value: Any, description: String },
      ...
    ]
  },
  
  parameters: Object,            // Inputs used
  mcp_calls: [String],
  generated_script: String,
  execution_time_ms: Number,
  data_sources: [String],
  
  version: Number,
  is_template: Boolean,          // Can be reused?
  similar_queries: [String],     // Questions that can use this
  
  created_at: DateTime,
  updated_at: DateTime,
  last_used_at: DateTime,
  
  tags: [String],
  metadata: Object
}
```

### 5. executions
Audit trail of all script executions.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  session_id: ObjectId,
  message_id: ObjectId,
  
  question: String,
  generated_script: String,
  parameters: Object,
  
  status: String,                // "pending", "running", "success", "failed"
  started_at: DateTime,
  completed_at: DateTime,
  execution_time_ms: Number,
  
  result: Object,
  error: String,
  warnings: [String],
  
  mcp_calls: [String],
  mcp_errors: Object,
  
  memory_used_mb: Float,
  cpu_percent: Float,
  
  cache_hit: Boolean,
  cache_key: String,
  
  metadata: Object
}
```

### 6. saved_analyses
User's saved reusable analyses.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  analysis_id: ObjectId,
  
  saved_name: String,
  description: String,
  
  usage_count: Number,
  last_used_at: DateTime,
  
  is_template: Boolean,
  template_variables: Object,    // Which params can change?
  
  created_at: DateTime,
  updated_at: DateTime,
  
  tags: [String],
  category: String
}
```

### 7. audit_logs
System audit trail for compliance.

```javascript
{
  _id: ObjectId,
  user_id: ObjectId,
  
  action: String,                // e.g., "question_submitted"
  resource_type: String,         // "message", "execution", "analysis"
  resource_id: ObjectId,
  
  before: Object,
  after: Object,
  changes: Object,
  
  ip_address: String,
  user_agent: String,
  
  success: Boolean,
  error_message: String,
  
  created_at: DateTime,
  metadata: Object
}
```

### 8. cache
Query result caching with TTL.

```javascript
{
  _id: ObjectId,
  cache_key: String,             // SHA256 hash
  result: Object,                // Cached result
  analysis_id: ObjectId,         // Reference to source
  
  hit_count: Number,
  created_at: DateTime,
  expires_at: DateTime,          // TTL index
  last_used_at: DateTime
}
```

## Usage Examples

### 1. Add User Message with Generated Analysis

```python
# Create analysis
analysis = AnalysisModel(
    user_id="user_123",
    title="AAPL Volatility Analysis",
    description="30-day volatility calculation",
    result={
        "description": "Top 5 volatile stocks",
        "body": [
            {"key": "rank_1", "value": "NVDA", "description": "45.2% volatility"}
        ]
    },
    parameters={"lookback_days": 30},
    mcp_calls=["calculate_volatility"],
    category="technical_analysis",
)

# Add message with embedded analysis (KEY WORKFLOW)
message_id = await repo.chat.add_assistant_message_with_analysis(
    session_id="sess_123",
    user_id="user_123",
    script="# Python code...",
    explanation="Analyzed AAPL volatility...",
    analysis=analysis,
    mcp_calls=["calculate_volatility"],
)
```

### 2. Reuse Analysis Without LLM

```python
# Get reusable analyses
analyses = await repo.analysis.get_reusable_analyses(user_id)

# Check if can reuse
can_reuse = await repo.analysis.can_reuse_analysis(analysis_id, "new question")

if can_reuse:
    # Execute saved analysis with new parameters
    # No LLM needed!
    pass
```

### 3. Cache Query Results

```python
# Check cache before running expensive query
cached = await repo.cache.get_cached_analysis(question, parameters)

if cached:
    return cached  # Return cached result immediately
else:
    # Run analysis...
    result = await run_analysis(question, parameters)
    
    # Cache for next time
    await repo.cache.cache_analysis(question, parameters, result)
    
    return result
```

### 4. Get Full Conversation Context

```python
context = await repo.chat.get_session_with_context(session_id)
# {
#   "session": {...},
#   "recent_messages": [...],
#   "recent_analyses": [
#     {"id": "...", "title": "AAPL Volatility", "timestamp": "..."}
#   ]
# }
```

## Environment Variables

```bash
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=qna_ai_admin
```

## Indexes

All collections have proper indexes for:
- Fast user lookups (email unique index)
- Session retrieval by user + date
- Message ordering within sessions
- Analysis search (full-text index)
- Audit log querying (user + action + date)
- Cache cleanup (TTL index on expires_at)

## Key Features

✅ **Embedded Analysis Storage**: Analyses stored in ChatMessage for quick replay
✅ **Reusable Templates**: Save analyses and reuse without LLM
✅ **Full Audit Trail**: Track all operations
✅ **Caching Layer**: Hash-based result caching with TTL
✅ **Flexible Metadata**: JSON fields for extensibility
✅ **TTL Indexes**: Auto-cleanup of expired cache
✅ **Full-Text Search**: Search analyses by title/description
✅ **Repository Pattern**: Clean data access layer

## Installation

```bash
pip install -r requirements.txt
```

## Integration with API Server

```python
from db import MongoDBClient, RepositoryManager

# In server startup
db_client = MongoDBClient()
repo_manager = RepositoryManager(db_client)

await repo_manager.initialize()

# Use in routes
@app.post("/analyze")
async def analyze(request: QuestionRequest):
    # Add user message
    await repo_manager.chat.add_user_message(
        session_id=request.session_id,
        user_id=user_id,
        question=request.question,
    )
    
    # ... generate analysis ...
    
    # Add assistant message with analysis
    await repo_manager.chat.add_assistant_message_with_analysis(
        session_id=request.session_id,
        user_id=user_id,
        script=generated_script,
        explanation=explanation,
        analysis=analysis_object,
        mcp_calls=mcp_calls,
    )
```

## Performance Considerations

- Embedded analyses in messages for fast retrieval
- Separate analyses collection for bulk operations
- Cache with 24-hour TTL by default
- Indexes on all common queries
- TTL index auto-cleanup of cache
- Full-text index for search

## Future Enhancements

- Sharding for large deployments
- Read replicas for analytics queries
- Change streams for real-time updates
- Archive collection for old data
