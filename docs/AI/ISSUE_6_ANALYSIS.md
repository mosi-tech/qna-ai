# Issue #6: Integrate Conversation History with Ollama-Server PAI Endpoint

## 📋 Issue Summary

**GitHub Issue #6 (OPEN)**
- **Title:** Integrate conversation history with backend PAI endpoint
- **Priority:** High
- **Labels:** backend, database, high-priority
- **Status:** Not started

**Requirements:**
1. Connect chat history system to backend
2. Pass conversation context to PAI
3. Manage context window limits
4. Track question-answer relationships
5. Handle context pruning for long conversations

---

## 🔍 What is This Issue About?

### Current State (Before This Issue)
- ✅ Chat history stored in MongoDB (Issue #7 - Just completed)
- ✅ Message ordering with timestamps
- ✅ User context and metadata
- ✅ Analysis results linked to questions
- ❌ Chat history NOT being used by Ollama-server
- ❌ Conversation context NOT passed to LLM
- ❌ No context window management

### What Needs to Happen
Connect the **MongoDB chat history layer** (Issue #7) with the **Ollama-server LLM endpoint** so that:

1. **User asks question** → System retrieves conversation history from MongoDB
2. **Context is formatted** → Prepare previous Q&A for LLM context
3. **Context is passed to LLM** → Send conversation context + new question to Ollama
4. **Context limits enforced** → Respect token/context window limits
5. **Long conversations pruned** → Remove old messages when context gets too long
6. **Relationships tracked** → Link all messages in conversation for analytics

---

## 🏗️ Architecture Overview

### Current Flow (Without Integration)
```
User Question
    ↓
Analysis Service (LLM analysis)
    ↓
Response
    ↓
NO CONTEXT AWARENESS
```

### Target Flow (With Integration - Issue #6)
```
User Question
    ↓
Retrieve Conversation History (MongoDB)
    ↓
Format Context Window
    ↓
Apply Context Pruning Rules
    ↓
LLM Call with Context
    ├─ System Prompt
    ├─ Conversation History (last N messages)
    ├─ Current Question
    └─ Context Metadata
    ↓
Enhanced Response (context-aware)
    ↓
Save to Chat History
```

---

## 🎯 Key Concepts

### 1. **PAI Endpoint**
- **PAI** likely means "Prompt Analysis Interface" or similar API endpoint
- It's the Ollama-server endpoint that accepts:
  - System prompt
  - Conversation history
  - Current user message
  - Context metadata

### 2. **Conversation Context**
```json
{
  "sessionId": "session-123",
  "messages": [
    {
      "role": "user",
      "content": "What is AAPL volatility?"
    },
    {
      "role": "assistant",
      "content": "AAPL's 30-day volatility is 25.3%"
    },
    {
      "role": "user",
      "content": "How does that compare to SPY?"
    }
  ]
}
```

### 3. **Context Window Management**
- **Token Limit:** LLM models have max token limits (e.g., 4K, 8K, 32K)
- **Context Usage:**
  - System prompt: ~500-1000 tokens
  - Conversation history: Variable (5-1000 tokens)
  - Current question: ~100-200 tokens
  - Available for response: Remainder
  
**Example with 4K token limit:**
```
Total Budget: 4,096 tokens
Used:
  - System Prompt: 800 tokens
  - History: 1,200 tokens
  - Current Q: 150 tokens
  - Reserved for response: 1,946 tokens
```

### 4. **Context Pruning**
When conversation gets too long, remove old messages intelligently:

```python
# Example: Keep only last 5 meaningful exchanges
if total_tokens > context_limit:
    # Remove oldest message
    # But keep analysis summaries
    # Keep at least recent 3 exchanges
```

### 5. **Question-Answer Relationships**
Track in database:
```json
{
  "messageId": "msg-123",
  "sessionId": "session-456",
  "relatedMessages": ["msg-120", "msg-121"],
  "followsFrom": "msg-120",
  "initiatesAnalysis": "analysis-789"
}
```

---

## 📊 Implementation Plan

### Phase 1: Analysis & Design (1-2 hours)
- [ ] Examine backend PAI endpoint implementation
- [ ] Understand current context passing mechanism
- [ ] Design context window calculation
- [ ] Design pruning strategy
- [ ] Define data structures for context passing

### Phase 2: Core Integration (2-3 hours)
- [ ] Create `ContextWindowManager` service
  - Calculate available tokens
  - Track context usage
  - Implement pruning logic
- [ ] Create `ConversationContextFormatter` service
  - Convert MongoDB messages to LLM format
  - Apply context limits
  - Add relationship metadata
- [ ] Update `ChatHistoryService` to track relationships
- [ ] Modify API routes to use context

### Phase 3: Ollama Integration (2-3 hours)
- [ ] Update ollama provider to accept conversation context
- [ ] Modify PAI endpoint to pass context
- [ ] Handle context in system prompt
- [ ] Test with Ollama running
- [ ] Validate context is being used

### Phase 4: Testing & Optimization (1-2 hours)
- [ ] Write unit tests for context manager
- [ ] Write integration tests (DB → LLM → Response)
- [ ] Test context pruning with long conversations
- [ ] Test token limit enforcement
- [ ] Performance benchmarking

### Phase 5: Documentation & Polish (1 hour)
- [ ] Document context window strategy
- [ ] Document pruning algorithm
- [ ] Add usage examples
- [ ] Update API documentation

---

## 📁 Files to Create/Modify

### New Files to Create
1. **`services/context_window_manager.py`**
   - Context window calculation
   - Token counting
   - Pruning strategies
   
2. **`services/conversation_context_formatter.py`**
   - Format messages for LLM
   - Apply context limits
   - Add metadata

3. **`tests/test_context_window.py`**
   - Unit tests for context manager
   
4. **`tests/test_conversation_context_integration.py`**
   - Integration tests (DB → LLM)

### Files to Modify
1. **`db/schemas.py`** (Issue #7)
   - Add `relatedMessages` field to ChatMessage
   - Add `followsFrom` field to track relationships

2. **`db/repositories.py`** (Issue #7)
   - Add method to get conversation context
   - Add method to track message relationships

3. **`services/chat_service.py`** (Issue #7)
   - Use context window manager
   - Format context for LLM

4. **`llm/providers/ollama.py`**
   - Accept conversation context parameter
   - Pass context to PAI endpoint
   - Handle context in system prompt

5. **`api/routes.py`**
   - Retrieve conversation history
   - Pass to analysis endpoint
   - Include context in LLM call

6. **`server.py`**
   - Initialize context window manager
   - Pass to services

---

## 🔧 Technical Details

### Context Window Manager Pseudocode
```python
class ContextWindowManager:
    def __init__(self, context_limit: int = 4000):
        self.context_limit = context_limit
    
    def estimate_tokens(self, text: str) -> int:
        """Estimate tokens using LLM tokenizer"""
        # Simple: ~4 chars per token (can be improved)
        return len(text) // 4
    
    def prepare_context(self, messages: List[ChatMessage], 
                       new_question: str, 
                       system_prompt: str) -> Dict:
        """
        Prepare context for LLM:
        1. Count system prompt tokens
        2. Count new question tokens
        3. Calculate available tokens for history
        4. Prune messages to fit
        5. Return formatted context
        """
        pass
    
    def prune_messages(self, messages: List[ChatMessage], 
                      max_tokens: int) -> List[ChatMessage]:
        """
        Intelligently remove old messages:
        - Keep at least 3 recent messages
        - Remove oldest first
        - Stop when under token limit
        """
        pass
```

### Conversation Context Structure
```python
@dataclass
class ConversationContext:
    sessionId: str
    messages: List[Dict]  # [{"role": "user/assistant", "content": "..."}]
    totalTokens: int
    pruned: bool
    prunedCount: int
    availableTokens: int
    
    def to_messages_param(self) -> List[Dict]:
        """Format for OpenAI-compatible API"""
        return self.messages
```

### Integration Point in Ollama Provider
```python
async def analyze_with_context(
    self, 
    question: str,
    conversation_context: ConversationContext,  # NEW
    system_prompt: str
) -> Dict:
    """
    Call Ollama with conversation context
    
    Format:
    - System: [system_prompt]
    - Messages: [conversation_context.messages]
    - Current: question
    """
    messages = [
        {"role": "system", "content": system_prompt},
        *conversation_context.messages,
        {"role": "user", "content": question}
    ]
    
    response = await ollama_client.chat(
        model=self.model,
        messages=messages,
        # ... other params
    )
    
    return response
```

---

## 🧪 Testing Strategy

### Unit Tests
```python
# Test 1: Token estimation
def test_token_estimation():
    manager = ContextWindowManager()
    tokens = manager.estimate_tokens("Hello world")
    assert tokens > 0

# Test 2: Context pruning
def test_prune_to_limit():
    messages = [create_test_message() for _ in range(10)]
    pruned = manager.prune_messages(messages, max_tokens=500)
    assert estimate_tokens(pruned) <= 500

# Test 3: Context preparation
def test_prepare_context():
    context = manager.prepare_context(
        messages=test_messages,
        new_question="How many?",
        system_prompt="You are helpful"
    )
    assert context.totalTokens <= 4000
```

### Integration Tests
```python
# Test 1: End-to-end with MongoDB
async def test_conversation_with_history():
    # 1. Create session
    session_id = await chat_service.start_session(user_id)
    
    # 2. Add first question
    await chat_service.add_user_message(session_id, "What is AAPL?")
    
    # 3. Add response
    await chat_service.add_assistant_message(session_id, "AAPL is Apple Inc.")
    
    # 4. Add follow-up question
    await chat_service.add_user_message(session_id, "What's the price?")
    
    # 5. Get context (should include history)
    context = await context_manager.get_conversation_context(session_id)
    
    # 6. Verify history is included
    assert len(context.messages) == 4  # system + 3 user/assistant
    assert "AAPL" in str(context.messages)

# Test 2: Context pruning with real LLM
async def test_ollama_with_long_conversation():
    # Create 50-message conversation
    for i in range(50):
        await chat_service.add_user_message(...)
    
    # Get context (should prune)
    context = await context_manager.get_conversation_context(session_id)
    
    # Verify pruned
    assert context.pruned == True
    assert context.prunedCount > 40
    
    # Verify Ollama still works
    response = await ollama.analyze_with_context(
        question="Latest?",
        conversation_context=context
    )
    assert response.success
```

---

## 📈 Expected Outcomes

### Before Integration
```
User: "What is AAPL volatility?"
LLM Response: Analysis (no context)

User: "How about SPY?"
LLM Response: Analysis (no context - doesn't know SPY was compared to AAPL)
```

### After Integration
```
User: "What is AAPL volatility?"
LLM Response: AAPL volatility is 25.3%

User: "How about SPY?"
LLM Response: SPY volatility is 18.7%
(LLM knows SPY is being compared to AAPL from history)

User: "Which is more volatile?"
LLM Response: AAPL at 25.3% is more volatile than SPY at 18.7%
(LLM has full conversation context)
```

---

## 📚 Resources & Files to Review

### To Understand Current System
1. **`Conversation.md`** - Architecture overview
2. **`db/schemas.py`** - Chat message structure
3. **`llm/providers/ollama.py`** - Ollama integration
4. **`api/routes.py`** - Current API flow

### References
- Ollama documentation: https://ollama.ai/library
- Token counting: OpenAI tiktoken library
- Context window best practices

---

## ✅ Success Criteria

- [ ] Conversation history passed to Ollama PAI endpoint
- [ ] Context window limits enforced (no token overflow)
- [ ] Long conversations pruned intelligently
- [ ] Message relationships tracked in database
- [ ] All tests passing (12+ tests)
- [ ] Integration test proves context-aware responses work
- [ ] Documentation complete with examples
- [ ] No breaking changes to existing APIs

---

## 🚀 Ready to Start?

**Estimated Total Time:** 8-11 hours
**Complexity:** Medium (builds on Issue #7)
**Risk Level:** Low (non-breaking changes)
**Blocking Issues:** None (Issue #7 is done)

**Next Step:** Examine ollama.py provider and PAI endpoint to understand current implementation

