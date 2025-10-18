# SessionManager & ConversationStore Integration Tests

## Overview

This document describes the comprehensive integration tests for SessionManager and ConversationStore with MongoDB.

## Architecture

### SessionManager (dialogue/conversation/session_manager.py)
- **Purpose**: Manages chat session lifecycle backed by MongoDB
- **No In-Memory Storage**: All sessions persisted in MongoDB via repo_manager
- **Key Methods**:
  - `create_session(user_id)` - Creates new session in MongoDB
  - `get_or_create_session(session_id)` - Gets existing or creates new session
  - `_get_session(session_id)` - Internal method to retrieve session (async)
  - `delete_session(session_id)` - Archive/delete session from MongoDB
  - `export_session(session_id)` - Export session data for debugging (async)

### ConversationStore (dialogue/conversation/store.py)
- **Purpose**: DB/cache interface for conversation data
- **MongoDB Backed**: Loads from MongoDB messages via `_populate_from_messages()`
- **Context Window**: Maintains last 10 turns for context (configurable)
- **Message Pairing**: User messages paired with assistant response summaries
- **Key Methods**:
  - `_populate_from_messages(db_messages)` - Converts MongoDB messages to ConversationTurn objects
  - `add_turn(user_query, query_type, analysis_summary, context_used)` - Add conversation turn
  - `get_last_turn()` - Get most recent conversation turn
  - `get_last_complete_turn()` - Get last complete (standalone) query turn
  - `get_context_summary()` - Get minimal context summary for LLM

### ConversationTurn (dialogue/conversation/store.py)
- **Purpose**: Represents single conversation exchange
- **Fields**:
  - `id`: Unique turn identifier
  - `timestamp`: When turn occurred
  - `user_query`: Original user input
  - `query_type`: COMPLETE, CONTEXTUAL, COMPARATIVE, or PARAMETER
  - `expanded_query`: LLM-expanded query if contextual
  - `analysis_summary`: Brief summary of analysis found
  - `context_used`: Whether context was used for expansion
  - `expansion_confidence`: Confidence score for expansion

## Data Flow

```
MongoDB Messages
    ↓
ChatRepository.get_conversation_history()
    ↓
Returns: List[Dict[role, content, timestamp]]
    ↓
SessionManager._get_session() creates ConversationStore
    ↓
ConversationStore._populate_from_messages()
    ↓
Pairs user messages with assistant responses
    ↓
Creates ConversationTurn objects (max 10)
    ↓
Store ready for ContextExpander/ContextAwareSearch
```

## Message Pairing Algorithm

The `_populate_from_messages()` method implements user/assistant message pairing:

```python
for each message:
    if role == "user":
        question = message.content
        analysis_summary = None
        
        # Look ahead for assistant response
        if next_message exists and role == "assistant":
            analysis_summary = next_message.content[:100]  # First 100 chars
        
        add_turn(question, analysis_summary)
```

### Edge Cases Handled:
1. **Unpaired User Messages**: User message without following assistant response → added with `analysis_summary = None`
2. **Orphan Assistant Messages**: Assistant response without preceding user → skipped
3. **Multiple Messages**: Correctly pairs user-assistant pairs in sequence
4. **Empty History**: Returns immediately if no messages

## Test Coverage

### 13 Comprehensive Tests

1. **Test 1: Create Session**
   - Tests creating new session in MongoDB
   - Verifies session_id is generated and returned

2. **Test 2: Get or Create Session (New)**
   - Tests creating fresh session when none exists
   - Verifies ConversationStore is properly initialized

3. **Test 3: Populate from Messages (User/Assistant Pairing)**
   - Tests message pairing algorithm
   - Verifies user queries paired with assistant response summaries
   - Validates query_type is set correctly

4. **Test 4: Context Window Trimming (Max 10 turns)**
   - Adds 15 turns to store
   - Verifies only last 10 turns retained
   - Checks oldest/newest turn preservation

5. **Test 5: Get Last Turn**
   - Tests retrieving most recent conversation turn
   - Handles empty store case

6. **Test 6: Get Last Complete Turn**
   - Tests finding last complete (standalone) query
   - Filters out contextual queries

7. **Test 7: Get Context Summary**
   - Tests minimal context summary generation
   - Verifies turn count, last query, history status

8. **Test 8: Retrieve Existing Session from MongoDB**
   - Creates session and adds messages
   - Uses SessionManager to retrieve existing session
   - Verifies ConversationStore populated from MongoDB

9. **Test 9: Delete Session**
   - Tests session deletion/archiving
   - Verifies session no longer retrievable after deletion

10. **Test 10: SessionManager with Repo Manager**
    - Tests SessionManager properly initialized with repo_manager
    - Verifies session creation and store initialization

11. **Test 11: Message Pairing Edge Cases**
    - Tests unpaired user messages (no assistant response)
    - Tests orphan assistant messages (no preceding user)
    - Validates edge case handling

12. **Test 12: Store Serialization**
    - Tests serialization to dict
    - Tests deserialization from dict
    - Verifies round-trip data preservation

13. **Test 13: Conversation Turn Serialization**
    - Tests individual turn serialization
    - Tests turn deserialization
    - Validates query_type enum preservation

## Running Tests

### Standalone Test Suite
```bash
cd /Users/shivc/Documents/Workspace/JS/qna-ai-admin/backend/scriptEdition/apiServer
python tests/test_session_store_integration.py
```

Output shows all 13 tests with detailed progress:
```
✓ Test 1: Create Session
  ✓ Session created: [UUID]

✓ Test 2: Get or Create Session (New)
  ✓ New session created: [UUID]
  ✓ ConversationStore initialized

... (more tests)

🎉 ALL TESTS PASSED! ✅
✅ SessionManager properly initialized with MongoDB
✅ ConversationStore correctly populates from messages
✅ Message pairing and context window working
✅ Serialization/deserialization functional
```

### With Mock Repository
Tests use MockRepoManager to simulate MongoDB without actual database:
- MockMongoDBClient: Simulates MongoDB operations
- MockChatRepository: Simulates ChatRepository interface
- Allows testing in isolation without MongoDB running

## Integration Points

### Usage in ContextAwareSearch
```python
# Step 1: Get or create session
session_id, conversation = await self.session_manager.get_or_create_session(session_id)

# Step 2: Use conversation history for context
conversation_turns = conversation.turns

# Step 3: Expand contextual queries
expansion_result = await self.expander.expand_query(query, conversation_turns)

# Step 4: Add new turn to conversation
turn = conversation.add_turn(
    user_query=query,
    query_type=query_type,
    analysis_summary=analysis_summary,
    context_used=expansion_confidence > threshold
)
```

### Usage in API Routes
```python
from dialogue import search_with_context

result = await search_with_context(
    query="what about QQQ to SPY",
    session_id=session_id,
    auto_expand=True
)
```

## Key Improvements Over Previous Design

1. **No In-Memory Storage**: Sessions backed by MongoDB, eliminates memory bloat
2. **Simplified Data Flow**: Direct MongoDB → ConversationStore conversion
3. **Non-Async Population**: `_populate_from_messages()` is synchronous, efficient
4. **Clear Separation of Concerns**:
   - SessionManager: CRUD operations
   - ConversationStore: DB interface
   - ContextExpander: Question expansion
   - ContextAwareSearch: Orchestration

5. **Message Pairing**: Automatically pairs user/assistant messages for context
6. **Context Window Trimming**: Automatic memory management (last 10 turns)

## Future Enhancements

1. **Redis Caching**: Add optional Redis cache layer in SessionManager
2. **Session Metadata**: Store session creation time, user preferences
3. **Conversation Analytics**: Track conversation patterns, query types
4. **Persistence**: Async message writing to MongoDB during conversation
5. **Session Recovery**: Graceful handling of interrupted sessions

## Testing Checklist

- ✅ SessionManager creation and initialization
- ✅ ConversationStore population from MongoDB messages
- ✅ Message pairing algorithm (user + assistant response)
- ✅ Context window trimming (max 10 turns)
- ✅ Context summary generation
- ✅ Serialization/deserialization
- ✅ Edge case handling (unpaired messages, orphan responses)
- ✅ Session retrieval from MongoDB
- ✅ Session deletion/archiving
- ✅ Error handling when session not found
- ✅ Conversation history management
- ✅ Turn classification (COMPLETE, CONTEXTUAL, etc.)

## Debugging Tips

### Enable Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Inspect Conversation Store
```python
# Get store
store = await session_manager._get_session(session_id)

# Inspect turns
for turn in store.turns:
    print(f"Query: {turn.user_query}")
    print(f"Type: {turn.query_type.value}")
    print(f"Analysis: {turn.analysis_summary}")
    print()

# Get context summary
summary = store.get_context_summary()
print(f"Has history: {summary['has_history']}")
print(f"Turn count: {summary['turn_count']}")
print(f"Last query: {summary['last_query']}")
```

### Export Session for Analysis
```python
session_dict = await session_manager.export_session(session_id)
print(f"Session JSON: {json.dumps(session_dict, indent=2)}")
```
