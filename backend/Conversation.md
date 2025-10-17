Architecture Breakdown: LLM Usage, ChromaDB, and Code Organization

  Data Flow & Technology Stack

  User Input: "what about QQQ to SPY"
          ↓
  1. Query Classification (LLM) → QueryType.CONTEXTUAL_REFERENCE
          ↓
  2. Context Extraction (Memory) → Previous strategy pattern
          ↓
  3. Context Expansion (LLM) → Full expanded query
          ↓
  4. Similarity Search (ChromaDB) → Find similar analyses
          ↓
  5. Response Generation → Results + context metadata

  LLM Usage Points & Arguments

  1. Query Classification (QueryClassifier)

  # LLM Call: Classification
  llm_prompt = f"""
  Classify this financial query type:

  Query: "{user_input}"

  Types:
  - COMPLETE: Has all context (assets, strategy, thresholds)
  - CONTEXTUAL: Refers to previous context ("what about X to Y")
  - COMPARATIVE: Comparing to previous ("how does that compare")
  - PARAMETER: Changing parameters ("what if 3% instead")

  Return: COMPLETE|CONTEXTUAL|COMPARATIVE|PARAMETER
  """

  # Arguments: query_text
  # Output: QueryType enum

  2. Context Expansion (ContextExpander)

  # LLM Call: Strategy Pattern Extraction
  llm_prompt = f"""
  Extract the strategy pattern from this conversation:

  Previous Query: "{previous_query}"
  Previous Analysis: "{previous_analysis_summary}"

  Strategy Pattern:
  - Asset Pair: [FROM] → [TO]
  - Trigger: [CONDITION]
  - Action: [WHAT_HAPPENS]
  - Frequency: [WHEN]

  Return as JSON: {{"from_asset": "", "to_asset": "", "trigger": "", "action": "", "frequency": ""}}
  """

  # LLM Call: Query Expansion
  llm_prompt = f"""
  Expand this contextual query using the strategy pattern:

  Incomplete Query: "{contextual_query}"
  Strategy Pattern: {{"from_asset": "QQQ", "to_asset": "VOO", "trigger": "monthly return < -2%", "action": "rotate", "frequency": "monthly"}}
  New Assets: QQQ → SPY

  Generate complete question following the same pattern but with new assets.
  Keep the same trigger logic and frequency.

  Return only the expanded question.
  """

  # Arguments: contextual_query, strategy_pattern, new_assets
  # Output: expanded_full_question, confidence_score

  3. Confidence Scoring (ContextExpander)

  # LLM Call: Expansion Confidence
  llm_prompt = f"""
  Rate the confidence of this query expansion:

  Original: "{original_query}"
  Expanded: "{expanded_query}"
  Context Used: "{context_source}"

  Rate 0.0-1.0 based on:
  - Asset substitution clarity (0.3)
  - Strategy pattern match (0.4)
  - Logical consistency (0.3)

  Return only the numerical score.
  """

  # Arguments: original_query, expanded_query, context_source
  # Output: confidence_float (0.0-1.0)

  ChromaDB Usage Points

  1. Primary Analysis Storage (AnalysisLibrary)

  # ChromaDB Collection: "financial_analyses"
  collection.add(
      documents=[f"Question: {question}\nDescription: {docstring}\nFunction: {function_name}"],
      metadatas=[analysis_metadata],
      ids=[analysis_id]
  )

  # Usage: Store completed financial analyses
  # Embeddings: Ollama qwen3-embedding model

  2. Contextual Search (ContextAwareSearch)

  # ChromaDB Query: Find similar analyses for expanded query
  results = collection.query(
      query_texts=[expanded_query],
      n_results=top_k,
      include=["documents", "metadatas", "distances"]
  )

  # Usage: Search using expanded/complete queries
  # Input: Fully expanded question from LLM
  # Output: Similar financial analyses with similarity scores

  3. Conversation Pattern Storage (Future Enhancement)

  # ChromaDB Collection: "conversation_patterns"
  collection.add(
      documents=[f"Pattern: {strategy_pattern}\nContext: {conversation_context}"],
      metadatas=[pattern_metadata],
      ids=[pattern_id]
  )

  # Usage: Store and retrieve common conversation patterns
  # Embeddings: Strategy patterns for better context matching

  Recommended Code Organization

  Current Issue: search/ folder is too narrow for conversation management.

  Better Structure:
  dialogue/                          # Main conversation system
  ├── __init__.py
  ├── conversation/                   # Conversation management
  │   ├── __init__.py
  │   ├── store.py                   # ConversationStore, ConversationTurn
  │   ├── session_manager.py         # Session lifecycle
  │   └── history.py                 # Conversation history utils
  ├── context/                       # Context understanding
  │   ├── __init__.py
  │   ├── classifier.py              # QueryClassifier (LLM)
  │   ├── expander.py                # ContextExpander (LLM)
  │   └── patterns.py                # Strategy pattern extraction
  ├── confirmation/                  # User confirmation flow
  │   ├── __init__.py
  │   ├── handler.py                 # ConfirmationHandler
  │   └── prompts.py                 # Confirmation message templates
  ├── search/                        # Enhanced search (keep existing)
  │   ├── __init__.py
  │   ├── library.py                 # AnalysisLibrary (existing)
  │   ├── client.py                  # AnalysisLibraryClient (existing)
  │   └── context_aware.py           # ContextAwareSearch (new)
  └── llm/                          # LLM integration
      ├── __init__.py
      ├── client.py                  # LLM client (Ollama/OpenAI)
      ├── prompts.py                 # All LLM prompts
      └── utils.py                   # LLM response parsing

  tests/
  ├── test_conversation.py           # Conversation flow tests
  ├── test_context_expansion.py      # LLM context expansion
  ├── test_query_classification.py   # LLM query classification
  └── test_integration.py            # End-to-end dialogue tests

  Technology Usage Summary

  | Component            | Technology        | Purpose                  | Input/Output                           |
  |----------------------|-------------------|--------------------------|----------------------------------------|
  | Query Classification | LLM (Ollama)      | Detect query type        | str → QueryType                        |
  | Context Expansion    | LLM (Ollama)      | Generate full queries    | contextual_query, pattern → full_query |
  | Confidence Scoring   | LLM (Ollama)      | Rate expansion quality   | original, expanded → float             |
  | Pattern Storage      | Memory/Dict       | Store conversation turns | session_id → List[ConversationTurn]    |
  | Analysis Search      | ChromaDB          | Find similar analyses    | expanded_query → List[Analysis]        |
  | Pattern Matching     | ChromaDB (future) | Store strategy patterns  | pattern → List[Pattern]                |
  | Session Management   | Memory/Redis      | Manage user sessions     | session_id → ConversationStore         |

  Key Architectural Decisions

  1. LLM for Intelligence: Query understanding, context expansion, confidence scoring
  2. ChromaDB for Search: Financial analysis similarity search using embeddings
  3. Memory for Speed: Conversation history in-memory for fast access
  4. Modular Design: Separate concerns (conversation, context, search, LLM)
  5. Async Flow: LLM calls can be async for better performance

  This architecture clearly separates the "thinking" (LLM) from "searching" (ChromaDB) from "remembering" (conversation storage), making it easier to optimize and maintain each component
  independently.

> So at classification, whole history and new query would be sent to LLM?

⏺ No, that would be inefficient and expensive. Here's a more efficient approach:

  Smart Context Selection Strategy

  Classification Phase: Minimal Context

  # Query Classification - NO full history sent
  def classify_query(user_input: str, last_turn_only: ConversationTurn = None) -> QueryType:

      # Only send last exchange if available
      if last_turn_only:
          llm_prompt = f"""
          Previous question: "{last_turn_only.user_query}"
          Current input: "{user_input}"
          
          Is current input:
          A) COMPLETE - standalone question with all context
          B) CONTEXTUAL - refers to previous ("what about QQQ to SPY")
          C) COMPARATIVE - comparing ("how does that compare")
          D) PARAMETER - changing numbers ("what if 3% instead")
          
          Return: A|B|C|D
          """
      else:
          # First query in session - must be complete
          return QueryType.COMPLETE

  Context Expansion Phase: Targeted History

  # Context Expansion - Send relevant strategy pattern only
  def expand_contextual_query(query: str, conversation_history: List[ConversationTurn]) -> ExpandedQuery:

      # Extract strategy pattern from most recent complete analysis
      relevant_turn = find_most_recent_complete_analysis(conversation_history)

      if relevant_turn:
          strategy_pattern = extract_strategy_pattern(relevant_turn)

          llm_prompt = f"""
          Strategy Pattern from previous analysis:
          - Assets: {strategy_pattern.from_asset} → {strategy_pattern.to_asset}
          - Trigger: {strategy_pattern.trigger}
          - Action: {strategy_pattern.action}
          - Frequency: {strategy_pattern.frequency}
          
          New contextual query: "{query}"
          
          Apply the same strategy pattern but with new assets mentioned in the query.
          Return complete question following the pattern.
          """

  Efficient Context Selection Algorithm

  class ContextSelector:
      def get_relevant_context(self, query: str, history: List[ConversationTurn]) -> dict:
          """Smart context selection - not full history"""

          if not history:
              return {"context_type": "none"}

          # For classification: only last turn
          if self.is_classification_phase():
              return {
                  "context_type": "last_turn",
                  "data": history[-1] if history else None
              }

          # For expansion: find most relevant strategy
          if self.is_expansion_phase():
              relevant_turn = self.find_strategy_pattern(history)
              return {
                  "context_type": "strategy_pattern",
                  "data": self.extract_pattern(relevant_turn)
              }

          # For confirmation: minimal context
          return {"context_type": "minimal"}

      def find_strategy_pattern(self, history: List[ConversationTurn]) -> ConversationTurn:
          """Find the most recent complete analysis with clear strategy"""

          for turn in reversed(history):
              if (turn.search_results and
                  len(turn.search_results) > 0 and
                  not turn.context_used):  # Original complete question
                  return turn

          return history[-1] if history else None

  Context Limits & Token Management

  # Token limits per LLM call
  CONTEXT_LIMITS = {
      "classification": {
          "max_tokens": 200,
          "context": "last_turn_only"  # ~50-100 tokens
      },
      "expansion": {
          "max_tokens": 500,
          "context": "strategy_pattern_only"  # ~150-250 tokens
      },
      "confidence": {
          "max_tokens": 300,
          "context": "expansion_comparison_only"  # ~100-200 tokens
      }
  }

  Example Flow

  Conversation History:
  1. Turn 1: "What if I buy QQQ into VOO every month when rolling monthly return goes below -2%?"
  2. Turn 2: "How does that perform during bear markets?"
  3. Turn 3: "what about QQQ to SPY" ← Current query

  LLM Calls:

  1. Classification (Turn 3):
  # Only send: Turn 2 + Current query
  previous = "How does that perform during bear markets?"
  current = "what about QQQ to SPY"
  # LLM determines: CONTEXTUAL

  2. Expansion (Turn 3):
  # Only send: Strategy pattern from Turn 1 + Current query
  strategy_pattern = {
      "from_asset": "QQQ",
      "to_asset": "VOO",
      "trigger": "monthly return < -2%",
      "action": "rotate monthly"
  }
  current = "what about QQQ to SPY"
  # LLM generates: "What if I buy QQQ into SPY every month when rolling monthly return goes below -2%?"

  Benefits of This Approach

  1. Token Efficiency: 200-500 tokens vs 2000+ for full history
  2. Cost Reduction: ~75% fewer tokens per LLM call
  3. Faster Response: Smaller payloads = faster processing
  4. Better Focus: LLM gets exactly what it needs, not noise
  5. Scalable: Works with long conversation histories

  Fallback Strategy

  def get_context_with_fallback(self, query: str, history: List[ConversationTurn]) -> dict:
      """Progressive context expansion if needed"""

      # Try minimal context first
      minimal_context = self.get_minimal_context(history)
      confidence = self.llm_expand(query, minimal_context)

      if confidence < 0.5:
          # Expand to more context if confidence low
          expanded_context = self.get_expanded_context(history)
          return self.llm_expand(query, expanded_context)

      return minimal_context

  This approach is much more efficient while still providing the necessary context for accurate query understanding and expansion.
