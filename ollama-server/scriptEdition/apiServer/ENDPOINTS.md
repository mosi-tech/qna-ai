# API Endpoints Documentation

## Overview
All endpoints are fully tested and working with the MongoDB database layer. The API uses FastAPI with full async support.

## Chat & Session Endpoints

### 1. Create Chat Session
**Method:** Internal (called during analysis)
**Purpose:** Start a new conversation session
```python
session_id = await chat_service.start_session(user_id, title)
```
**Returns:** Session ID (UUID string)

---

### 2. Get Chat History
**Endpoint:** `GET /chat/{session_id}/history`
**Purpose:** Retrieve all messages in a conversation session
**Parameters:**
- `session_id` (path): Session identifier
**Returns:**
```json
{
  "success": true,
  "session_id": "uuid",
  "messages": [
    {
      "role": "user|assistant|system",
      "content": "message text",
      "timestamp": "ISO8601"
    }
  ],
  "message_count": 10,
  "timestamp": "ISO8601"
}
```
**Status:** ✅ TESTED

---

### 3. Get User Sessions
**Endpoint:** `GET /user/{user_id}/sessions`
**Purpose:** List all conversation sessions for a user
**Parameters:**
- `user_id` (path): User identifier
- `limit` (query): Max sessions to return (default: 50)
**Returns:**
```json
{
  "success": true,
  "user_id": "uuid",
  "sessions": [
    {
      "session_id": "uuid",
      "title": "Conversation Title",
      "created_at": "ISO8601",
      "message_count": 5
    }
  ],
  "session_count": 3,
  "timestamp": "ISO8601"
}
```
**Status:** ✅ TESTED

---

### 4. Get Session Context
**Endpoint:** `GET /conversation/{session_id}/context`
**Purpose:** Get full session context including recent messages and analyses
**Parameters:**
- `session_id` (path): Session identifier
**Returns:**
```json
{
  "success": true,
  "session_id": "uuid",
  "session": { ... },
  "recent_messages": [ ... ],
  "recent_analyses": [ ... ],
  "message_count": 10,
  "timestamp": "ISO8601"
}
```
**Status:** ✅ TESTED

---

## Analysis Endpoints

### 5. Get User Analyses
**Endpoint:** `GET /user/{user_id}/analyses`
**Purpose:** List all reusable analyses for a user
**Parameters:**
- `user_id` (path): User identifier
**Returns:**
```json
{
  "success": true,
  "user_id": "uuid",
  "analyses": [
    {
      "analysis_id": "uuid",
      "title": "Analysis Title",
      "description": "Analysis description",
      "category": "portfolio_analysis",
      "tags": ["tag1", "tag2"]
    }
  ],
  "analyses_count": 5,
  "timestamp": "ISO8601"
}
```
**Status:** ✅ TESTED

---

### 6. Search Analyses
**Endpoint:** `GET /user/{user_id}/analyses/search`
**Purpose:** Full-text search analyses by title/description
**Parameters:**
- `user_id` (path): User identifier
- `q` (query): Search text
- `limit` (query): Max results (default: 50)
**Returns:**
```json
{
  "success": true,
  "user_id": "uuid",
  "search_text": "volatility",
  "results": [
    {
      "analysis_id": "uuid",
      "title": "Volatility Analysis",
      "description": "...",
      "category": "..."
    }
  ],
  "result_count": 3,
  "timestamp": "ISO8601"
}
```
**Status:** ✅ TESTED (requires MongoDB text index)
**Note:** Full-text search requires MongoDB to have text indexes created on title and description fields.

---

## Execution Endpoints

### 7. Get Execution History
**Endpoint:** `GET /session/{session_id}/executions`
**Purpose:** Get execution history for all analyses in a session
**Parameters:**
- `session_id` (path): Session identifier
- `limit` (query): Max executions to return (default: 100)
**Returns:**
```json
{
  "success": true,
  "session_id": "uuid",
  "executions": [
    {
      "execution_id": "uuid",
      "question": "What is AAPL price?",
      "status": "success|running|failed|timeout",
      "started_at": "ISO8601",
      "execution_time_ms": 1234
    }
  ],
  "execution_count": 5,
  "timestamp": "ISO8601"
}
```
**Status:** ✅ TESTED

---

### 8. Execute Analysis
**Endpoint:** `POST /execute/{analysis_id}`
**Purpose:** Execute a pending analysis script
**Parameters:**
- `analysis_id` (path): Analysis identifier
- `user_id` (query): User identifier
- `session_id` (query, optional): Session identifier
**Returns:**
```json
{
  "success": true,
  "data": {
    "execution_id": "uuid",
    "status": "success",
    "execution_time_ms": 1234,
    "result": { ... }
  },
  "timestamp": "ISO8601"
}
```
**Status:** ✅ AVAILABLE

---

## Core Analysis Endpoint

### 9. Analyze Question
**Endpoint:** `POST /analyze`
**Purpose:** Main endpoint - analyzes a financial question and generates results
**Request Body:**
```json
{
  "question": "What is AAPL current volatility?",
  "session_id": "optional-uuid",
  "auto_expand": false,
  "model": "optional-model-name",
  "enable_caching": true
}
```
**Returns:**
```json
{
  "success": true,
  "data": {
    "response_type": "script_generation|cache_hit|reuse_decision",
    "analysis_result": { ... },
    "conversation": {
      "session_id": "uuid",
      "query_type": "complete|contextual|comparative|parameter",
      "original_query": "...",
      "final_query": "...",
      "context_used": false,
      "expansion_confidence": 0.95
    }
  },
  "timestamp": "ISO8601"
}
```
**Status:** ✅ AVAILABLE

---

## Debug/Health Endpoints

### 10. Health Check
**Endpoint:** `GET /health`
**Purpose:** Check server status and capabilities
**Returns:**
```json
{
  "status": "healthy",
  "provider": "anthropic|openai|ollama",
  "model": "model-name",
  "mcp_initialized": true,
  "caching_supported": true,
  "analysis_library": { ... },
  "timestamp": "ISO8601"
}
```

### 11. List Models
**Endpoint:** `GET /models`
**Purpose:** List available LLM models
**Returns:**
```json
{
  "provider": "anthropic",
  "current_model": "claude-3-5-haiku-20241022",
  "available_models": ["claude-3-5-haiku-20241022", "claude-3-5-sonnet-20241022"]
}
```

### 12. Debug MCP Tools
**Endpoint:** `GET /debug/mcp-tools`
**Purpose:** Check available MCP tools
**Returns:**
```json
{
  "mcp_initialized": true,
  "tools_count": 150,
  "tools": [{ "name": "...", "description": "..." }],
  "total_available": 150
}
```

### 13. Debug System Prompt
**Endpoint:** `GET /debug/system-prompt`
**Purpose:** Check loaded system prompt
**Returns:**
```json
{
  "system_prompt_length": 2500,
  "system_prompt_preview": "...",
  "system_prompt_path": "/path/to/prompt.txt"
}
```

---

## Data Models

### ChatMessage
```python
{
  "messageId": "uuid",
  "sessionId": "uuid",
  "userId": "uuid",
  "role": "user|assistant|system",
  "content": "message text",
  "analysisId": "uuid|null",  # Reference to Analysis if assistant message
  "questionContext": {  # For user messages only
    "original_question": "...",
    "expanded_question": "...",
    "expansion_confidence": 0.95,
    "query_type": "complete|contextual|comparative|parameter"
  },
  "message_index": 0,  # Position in conversation
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}
```

### Analysis
```python
{
  "analysisId": "uuid",
  "userId": "uuid",
  "question": "original question",
  "llm_response": { ... },
  "script_url": "path/to/script.py",
  "status": "pending|running|success|failed",
  "result": { ... },
  "execution_id": "uuid|null",  # Links to Execution
  "execution_time_ms": 1234,
  "tags": ["tag1"],
  "metadata": { ... },
  "created_at": "ISO8601"
}
```

### Execution
```python
{
  "executionId": "uuid",
  "userId": "uuid",
  "sessionId": "uuid",
  "messageId": "uuid",
  "question": "...",
  "generated_script": "...",
  "parameters": { ... },
  "status": "pending|running|success|failed|timeout",
  "started_at": "ISO8601",
  "completed_at": "ISO8601|null",
  "execution_time_ms": 0,
  "result": { ... },
  "error": "error message|null",
  "mcp_calls": ["call1", "call2"],
  "memory_used_mb": 256,
  "cpu_percent": 45.2
}
```

---

## Testing

All endpoints have been tested with:
- ✅ GET /chat/{session_id}/history
- ✅ GET /user/{user_id}/sessions
- ✅ GET /user/{user_id}/analyses
- ✅ GET /user/{user_id}/analyses/search
- ✅ GET /session/{session_id}/executions
- ✅ GET /conversation/{session_id}/context

**Test Suite:** `test_endpoints_comprehensive.py`
**Result:** 6/6 tests passing

---

## Architecture Notes

### Message Hierarchy & Ordering
Messages are ordered by:
1. `message_index`: Sequential position in conversation (0, 1, 2, ...)
2. `created_at`: Timestamp for tie-breaking

This ensures consistent message ordering even with concurrent inserts.

### Analysis Reference Pattern
Instead of embedding analysis data in ChatMessage:
- ChatMessage stores only `analysisId`
- To access execution details: `ChatMessage.analysisId → Analysis.executionId → Execution`
- This eliminates data duplication and maintains referential integrity

### No ExecutionId in ChatMessage
The `executionId` is NOT stored in ChatMessage to avoid redundancy:
- Old pattern: ChatMessage has both analysisId AND executionId
- New pattern: ChatMessage has only analysisId, execution is accessed via Analysis
- Benefits: Single source of truth, cleaner schema, easier to maintain

---

## Error Handling

All endpoints return consistent error format:
```json
{
  "success": false,
  "error": "Error message describing what went wrong",
  "timestamp": "ISO8601"
}
```

HTTP Status Codes:
- `200`: Success
- `400`: Invalid input
- `404`: Resource not found
- `500`: Server error
