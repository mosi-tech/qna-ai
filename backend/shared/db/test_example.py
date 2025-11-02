"""
Example: Using the database layer
This demonstrates the key workflows
"""

import asyncio
from datetime import datetime
from db.schemas import (
    UserModel,
    ChatSessionModel,
    ChatMessageModel,
    AnalysisModel,
    RoleType,
    QueryType,
)
from db.mongodb_client import MongoDBClient
from db.repositories import RepositoryManager


async def example_workflow():
    """
    Example workflow showing:
    1. User asks question
    2. System generates analysis
    3. Analysis stored with message (can be replayed without LLM)
    4. Analysis can be reused for similar questions
    """
    
    # Initialize database
    db = MongoDBClient()
    repo = RepositoryManager(db)
    await repo.initialize()
    
    try:
        # ====================================================================
        # STEP 1: Create user
        # ====================================================================
        user = UserModel(
            email="trader@example.com",
            username="john_trader",
            preferences={"timezone": "UTC", "theme": "dark"}
        )
        user_id = await db.create_user(user)
        print(f"✓ Created user: {user_id}")
        
        # ====================================================================
        # STEP 2: Start conversation session
        # ====================================================================
        session_id = await repo.chat.start_session(user_id, "Stock Analysis Session")
        print(f"✓ Created session: {session_id}")
        
        # ====================================================================
        # STEP 3: User asks question
        # ====================================================================
        question = "What are the top 5 most volatile stocks today?"
        await repo.chat.add_user_message(
            session_id=session_id,
            user_id=user_id,
            question=question,
            query_type=QueryType.COMPLETE
        )
        print(f"✓ Added user question")
        
        # ====================================================================
        # STEP 4: System generates analysis (this would come from LLM + MCP)
        # ====================================================================
        analysis = AnalysisModel(
            user_id=user_id,
            title="Top 5 Volatile Stocks",
            description="30-day volatility analysis of most active stocks",
            category="technical_analysis",
            
            # Result that gets displayed to user
            result={
                "description": "Analysis of top 5 most volatile stocks based on 30-day volatility",
                "body": [
                    {
                        "key": "rank_1",
                        "value": "NVDA",
                        "description": "NVIDIA - 45.2% volatility, 2.3M volume"
                    },
                    {
                        "key": "rank_2",
                        "value": "AMD",
                        "description": "Advanced Micro - 42.8% volatility, 1.8M volume"
                    },
                    {
                        "key": "rank_3",
                        "value": "TSLA",
                        "description": "Tesla - 38.5% volatility, 3.1M volume"
                    },
                    {
                        "key": "rank_4",
                        "value": "MSTR",
                        "description": "MicroStrategy - 52.1% volatility, 0.9M volume"
                    },
                    {
                        "key": "rank_5",
                        "value": "COIN",
                        "description": "Coinbase - 41.3% volatility, 1.2M volume"
                    },
                ]
            },
            
            # Parameters used to generate this analysis
            parameters={
                "lookback_days": 30,
                "limit": 5,
                "min_volume": 1000000
            },
            
            # MCP tools that were called
            mcp_calls=["alpaca_market_screener_most_actives", "calculate_volatility"],
            
            # The Python script that was executed
            generated_script="""
import pandas as pd
from mcp_client import alpaca, analytics

# Get most active stocks
actives = alpaca.screener_most_actives(limit=100)

# Fetch bars for each
volatilities = []
for symbol in actives['symbols']:
    bars = alpaca.market_stocks_bars(symbol, timeframe='1Day', limit=30)
    vol = analytics.calculate_volatility(bars['close'])
    volatilities.append((symbol, vol))

# Sort by volatility and return top 5
top_5 = sorted(volatilities, key=lambda x: x[1], reverse=True)[:5]
            """,
            
            data_sources=["Alpaca Market Data", "Technical Analysis Engine"],
            execution_time_ms=2345,
            tags=["volatility", "stock-screening", "top-5"],
            is_template=True,  # Save as reusable template
            similar_queries=[
                "What stocks have the highest volatility?",
                "Which stocks are most volatile?",
                "Show me volatile stocks"
            ]
        )
        
        print(f"✓ Generated analysis")
        
        # ====================================================================
        # STEP 5: Add assistant message WITH embedded analysis
        # THIS IS THE KEY FEATURE - analysis is stored in message
        # Can be replayed/reused without LLM regeneration
        # ====================================================================
        message_id = await repo.chat.add_assistant_message_with_analysis(
            session_id=session_id,
            user_id=user_id,
            script=analysis.generated_script,
            explanation="I analyzed the most active stocks and calculated their 30-day volatility...",
            analysis=analysis,  # FULL ANALYSIS EMBEDDED
            mcp_calls=analysis.mcp_calls,
        )
        print(f"✓ Added assistant message with embedded analysis")
        
        # ====================================================================
        # STEP 6: Save analysis as reusable template
        # ====================================================================
        saved = await repo.analysis.save_analysis(
            user_id=user_id,
            saved_name="Volatility Top 5 - 30 Day",
            analysis=analysis
        )
        print(f"✓ Saved analysis as template: {saved}")
        
        # ====================================================================
        # STEP 7: Cache the result for quick replay
        # ====================================================================
        await repo.cache.cache_analysis(
            question=question,
            parameters=analysis.parameters,
            result=analysis.result,
            analysis_id=message_id,
            ttl_hours=24
        )
        print(f"✓ Cached analysis result")
        
        # ====================================================================
        # STEP 8: Related question - can reuse analysis!
        # ====================================================================
        similar_question = "Which stocks are most volatile?"
        
        # Check cache first
        cached_result = await repo.cache.get_cached_analysis(
            similar_question,
            analysis.parameters
        )
        
        if cached_result:
            print(f"✓ Cache hit! Reusing analysis without LLM or execution")
            print(f"  Result: {cached_result}")
        else:
            # Check if existing analysis can be reused
            can_reuse = await repo.analysis.can_reuse_analysis(
                message_id,
                similar_question
            )
            
            if can_reuse:
                print(f"✓ Can reuse existing analysis without LLM")
        
        # ====================================================================
        # STEP 9: Retrieve conversation context for next turn
        # ====================================================================
        context = await repo.chat.get_session_with_context(session_id)
        print(f"✓ Retrieved session context")
        print(f"  Messages: {context['message_count']}")
        print(f"  Analyses: {len(context['recent_analyses'])}")
        
        # ====================================================================
        # STEP 10: Get conversation history (for LLM context)
        # ====================================================================
        history = await repo.chat.get_conversation_history(session_id)
        print(f"✓ Retrieved conversation history")
        for msg in history:
            print(f"  - {msg['role']}: {msg['content'][:50]}...")
        
        # ====================================================================
        # STEP 11: Get execution history (audit trail)
        # ====================================================================
        executions = await repo.execution.get_execution_history(session_id)
        print(f"✓ Retrieved execution history: {len(executions)} executions")
        
        # ====================================================================
        # STEP 12: Get all reusable analyses
        # ====================================================================
        reusable = await repo.analysis.get_reusable_analyses(user_id)
        print(f"✓ Retrieved reusable analyses: {len(reusable)} templates")
        for a in reusable:
            print(f"  - {a.title}")
        
        # ====================================================================
        # STEP 13: Search analyses
        # ====================================================================
        search_results = await repo.analysis.search_analyses(user_id, "volatility")
        print(f"✓ Search results for 'volatility': {len(search_results)} analyses")
        
        print("\n" + "="*70)
        print("✅ WORKFLOW COMPLETE")
        print("="*70)
        print(f"""
Key Features Demonstrated:
1. ✓ Embedded analysis in ChatMessage for quick replay
2. ✓ Reusable analysis templates (is_template=True)
3. ✓ Similar queries pre-computed for reuse detection
4. ✓ Analysis caching with parameters
5. ✓ Full audit trail of all operations
6. ✓ Session context with analysis references
7. ✓ Conversation history for LLM context
8. ✓ Search functionality
        """)
        
    finally:
        await repo.shutdown()


if __name__ == "__main__":
    asyncio.run(example_workflow())
