#!/usr/bin/env python3
"""
Comprehensive integration tests for all database services
Tests: MongoDB connection, all repositories, services, and end-to-end workflows
"""

import asyncio
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any

sys.path.insert(0, '/Users/shivc/Documents/Workspace/JS/qna-ai-admin/ollama-server/scriptEdition/apiServer')

from db import MongoDBClient, RepositoryManager
from db.schemas import (
    AnalysisModel, ChatMessageModel, ExecutionModel, QueryType, RoleType
)
from services.chat_service import ChatHistoryService
from services.cache_service import CacheService
from services.analysis_persistence_service import AnalysisPersistenceService
from services.audit_service import AuditService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test-integration")


class ServiceIntegrationTester:
    def __init__(self):
        self.db_client = None
        self.repo_manager = None
        self.chat_service = None
        self.cache_service = None
        self.analysis_service = None
        self.audit_service = None
        self.test_results = []

    async def setup(self):
        """Initialize all services"""
        logger.info("=" * 80)
        logger.info("SETUP: Initializing MongoDB and services")
        logger.info("=" * 80)
        
        try:
            # Initialize MongoDB
            logger.info("📦 Connecting to MongoDB...")
            self.db_client = MongoDBClient()
            logger.info("✅ MongoDB client created")
            
            # Initialize repository manager
            logger.info("📦 Initializing repository manager...")
            self.repo_manager = RepositoryManager(self.db_client)
            await self.repo_manager.initialize()
            logger.info("✅ Repository manager initialized with indexes")
            
            # Initialize services
            logger.info("📦 Initializing services...")
            self.chat_service = ChatHistoryService(self.repo_manager)
            self.cache_service = CacheService(self.repo_manager)
            self.analysis_service = AnalysisPersistenceService(self.repo_manager)
            self.audit_service = AuditService(self.repo_manager)
            logger.info("✅ All services initialized")
            
            return True
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}")
            return False

    async def test_mongodb_connection(self):
        """Test 1: MongoDB connection and database access"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 1: MongoDB Connection")
        logger.info("=" * 80)
        
        test_name = "MongoDB Connection"
        try:
            # Test connection
            logger.info("Testing MongoDB connectivity...")
            db = self.db_client.db
            
            # Check collections
            logger.info("Checking collections...")
            collections = await db.list_collection_names()
            logger.info(f"✅ Available collections: {collections}")
            
            # Test write to a temp collection
            logger.info("Testing write operation...")
            test_doc = {"test": "connection", "timestamp": datetime.now()}
            result = await db.test_connection.insert_one(test_doc)
            logger.info(f"✅ Write test successful, ID: {result.inserted_id}")
            
            # Test read
            logger.info("Testing read operation...")
            read_doc = await db.test_connection.find_one({"_id": result.inserted_id})
            logger.info(f"✅ Read test successful: {read_doc}")
            
            # Cleanup
            await db.test_connection.delete_many({})
            logger.info("✅ Cleanup complete")
            
            self.test_results.append((test_name, True, "Connection successful"))
            return True
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            self.test_results.append((test_name, False, str(e)))
            return False

    async def test_chat_service(self):
        """Test 2: ChatHistoryService - session management and messaging"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 2: ChatHistoryService")
        logger.info("=" * 80)
        
        test_name = "ChatHistoryService"
        user_id = "test-user-001"
        
        try:
            # Test 2a: Create session
            logger.info("Test 2a: Creating chat session...")
            session_id = await self.chat_service.start_session(user_id, "Test Session")
            logger.info(f"✅ Session created: {session_id}")
            
            # Test 2b: Add user message
            logger.info("Test 2b: Adding user message...")
            message_id = await self.chat_service.add_user_message(
                session_id=session_id,
                user_id=user_id,
                question="What is market volatility?",
                query_type=QueryType.COMPLETE
            )
            logger.info(f"✅ User message added: {message_id}")
            
            # Test 2c: Verify message in DB
            logger.info("Test 2c: Retrieving user message from DB...")
            msg = await self.db_client.db.chat_messages.find_one({"messageId": message_id})
            assert msg is not None, "Message not found in DB"
            assert msg["content"] == "What is market volatility?"
            logger.info(f"✅ Message verified in DB: {msg.get('content')}")
            
            # Test 2d: Add assistant message with analysis
            logger.info("Test 2d: Adding assistant message with analysis...")
            analysis_model = AnalysisModel(
                userId=user_id,
                question="What is market volatility?",
                llm_response={
                    "status": "success",
                    "script_name": "test_script.py",
                    "analysis_description": "Market volatility analysis",
                    "execution": {
                        "script_name": "test_script.py",
                        "parameters": {"days": 30}
                    }
                },
                script_url="/tmp/test_script.py",
                script_size_bytes=0
            )
            
            assistant_msg_id = await self.chat_service.add_assistant_message_with_analysis(
                session_id=session_id,
                user_id=user_id,
                script="test_script.py",
                explanation="Here is the volatility analysis",
                analysis=analysis_model,
            )
            logger.info(f"✅ Assistant message with analysis added: {assistant_msg_id}")
            
            # Test 2e: Verify analysis reference
            logger.info("Test 2e: Verifying analysis reference in message...")
            asst_msg = await self.db_client.db.chat_messages.find_one({"messageId": assistant_msg_id})
            assert asst_msg is not None, "Assistant message not found"
            assert asst_msg.get("analysisId") is not None, "Analysis reference not found"
            logger.info(f"✅ Analysis reference verified: {asst_msg['analysisId']}")
            
            # Test 2f: Get conversation history
            logger.info("Test 2f: Retrieving conversation history...")
            history = await self.chat_service.get_conversation_history(session_id)
            logger.info(f"✅ Retrieved {len(history)} messages")
            assert len(history) >= 2, f"Expected at least 2 messages, got {len(history)}"
            logger.info(f"   Message 1: {history[0]['role']} - {history[0].get('content', 'N/A')[:50]}")
            logger.info(f"   Message 2: {history[1]['role']} - {history[1].get('content', 'N/A')[:50]}")
            
            # Test 2g: Get session context
            logger.info("Test 2g: Getting full session context...")
            context = await self.chat_service.get_session_context(session_id)
            logger.info(f"✅ Session context retrieved with {len(context.get('messages', []))} messages")
            
            # Test 2h: List user sessions
            logger.info("Test 2h: Listing user sessions...")
            sessions = await self.chat_service.list_sessions(user_id)
            logger.info(f"✅ Retrieved {len(sessions)} sessions for user")
            assert len(sessions) > 0, "No sessions found"
            
            self.test_results.append((test_name, True, "All chat operations successful"))
            return True
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results.append((test_name, False, str(e)))
            return False

    async def test_cache_service(self):
        """Test 3: CacheService - result caching with TTL"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 3: CacheService")
        logger.info("=" * 80)
        
        test_name = "CacheService"
        question = "What are the top 5 volatile stocks?"
        parameters = {"days": 30}
        result_data = {"stocks": ["AAPL", "MSFT", "TSLA"], "volatility": [45.2, 38.1, 52.3]}
        
        try:
            # Test 3a: Cache miss (should return None)
            logger.info("Test 3a: Testing cache miss...")
            cached = await self.cache_service.get_cached_result(question, parameters)
            assert cached is None, "Expected cache miss, but got result"
            logger.info("✅ Cache miss verified (no previous cache)")
            
            # Test 3b: Cache write
            logger.info("Test 3b: Writing to cache...")
            cache_id = await self.cache_service.cache_analysis_result(
                question=question,
                parameters=parameters,
                result=result_data,
                ttl_hours=24
            )
            logger.info(f"✅ Result cached: {cache_id}")
            
            # Test 3c: Verify in DB
            logger.info("Test 3c: Verifying cache entry in DB...")
            cache_doc = await self.db_client.db.cache.find_one({"cacheId": cache_id})
            assert cache_doc is not None, "Cache entry not found in DB"
            logger.info(f"✅ Cache entry verified in DB")
            
            # Test 3d: Cache hit
            logger.info("Test 3d: Testing cache hit...")
            cached_result = await self.cache_service.get_cached_result(question, parameters)
            assert cached_result is not None, "Expected cache hit, but got None"
            assert cached_result["stocks"] == ["AAPL", "MSFT", "TSLA"]
            logger.info(f"✅ Cache hit successful: Retrieved {len(cached_result['stocks'])} stocks")
            
            # Test 3e: Invalid cache (different parameters)
            logger.info("Test 3e: Testing cache miss with different parameters...")
            different_params = {"days": 60}
            cached_diff = await self.cache_service.get_cached_result(question, different_params)
            assert cached_diff is None, "Expected cache miss with different parameters"
            logger.info("✅ Different parameters correctly miss cache")
            
            self.test_results.append((test_name, True, "Caching operations successful"))
            return True
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results.append((test_name, False, str(e)))
            return False

    async def test_analysis_persistence_service(self):
        """Test 4: AnalysisPersistenceService - save, retrieve, search analyses"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 4: AnalysisPersistenceService")
        logger.info("=" * 80)
        
        test_name = "AnalysisPersistenceService"
        user_id = "test-user-002"
        
        try:
            # Test 4a: Create and save analysis
            logger.info("Test 4a: Creating analysis template...")
            analysis_id = await self.analysis_service.create_analysis(
                user_id=user_id,
                title="Portfolio Correlation Analysis",
                description="Analysis of correlations between portfolio assets",
                result={"correlations": {"AAPL": 0.85, "MSFT": 0.92}},
                parameters={"symbols": ["AAPL", "MSFT", "GOOGL"]},
                mcp_calls=["alpaca_correlation"],
                category="portfolio_analysis",
                script="correlation_analysis.py",
                data_sources=["alpaca"],
                tags=["portfolio", "correlation"]
            )
            logger.info(f"✅ Analysis created and saved: {analysis_id}")
            
            # Test 4b: Verify in DB
            logger.info("Test 4b: Verifying analysis in DB...")
            analysis_doc = await self.db_client.db.analyses.find_one({"analysisId": analysis_id})
            assert analysis_doc is not None, "Analysis not found in DB"
            assert analysis_doc["question"] == "Portfolio Correlation Analysis"
            logger.info(f"✅ Analysis verified in DB: {analysis_doc['question']}")
            
            # Test 4c: Get analysis by ID
            logger.info("Test 4c: Retrieving analysis by ID...")
            retrieved = await self.analysis_service.get_analysis(analysis_id)
            assert retrieved is not None, "Failed to retrieve analysis"
            logger.info(f"✅ Analysis retrieved: {retrieved.question if hasattr(retrieved, 'question') else 'Retrieved'}")
            
            # Test 4d: Get reusable analyses
            logger.info("Test 4d: Getting reusable analyses for user...")
            analyses = await self.analysis_service.get_reusable_analyses(user_id)
            logger.info(f"✅ Retrieved {len(analyses)} reusable analyses")
            assert len(analyses) > 0, "No reusable analyses found"
            
            # Test 4e: Get similar analyses (same category)
            logger.info("Test 4e: Getting similar analyses in category...")
            similar = await self.analysis_service.get_similar_analyses(
                user_id=user_id,
                category="portfolio_analysis"
            )
            logger.info(f"✅ Found {len(similar)} similar analyses in category")
            
            # Test 4f: Search analyses
            logger.info("Test 4f: Searching analyses...")
            search_results = await self.analysis_service.search_analyses(
                user_id=user_id,
                search_text="correlation"
            )
            logger.info(f"✅ Search found {len(search_results)} results")
            
            self.test_results.append((test_name, True, "Analysis persistence operations successful"))
            return True
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results.append((test_name, False, str(e)))
            return False

    async def test_audit_service(self):
        """Test 5: AuditService - execution logging and history"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 5: AuditService")
        logger.info("=" * 80)
        
        test_name = "AuditService"
        user_id = "test-user-003"
        session_id = "test-session-001"
        
        try:
            # Test 5a: Log execution start
            logger.info("Test 5a: Logging execution start...")
            execution_id = await self.audit_service.log_execution_start(
                user_id=user_id,
                session_id=session_id,
                message_id="msg-001",
                question="Calculate portfolio metrics",
                script="portfolio_metrics.py",
                parameters={"symbols": ["AAPL", "MSFT"]},
                mcp_calls=["alpaca_bars", "alpaca_stats"]
            )
            logger.info(f"✅ Execution logged: {execution_id}")
            
            # Test 5b: Verify in DB
            logger.info("Test 5b: Verifying execution in DB...")
            exec_doc = await self.db_client.db.executions.find_one({"executionId": execution_id})
            assert exec_doc is not None, "Execution not found in DB"
            assert exec_doc["status"] == "running"
            logger.info(f"✅ Execution verified in DB with status: {exec_doc['status']}")
            
            # Test 5c: Log execution complete
            logger.info("Test 5c: Logging execution completion...")
            result = await self.audit_service.log_execution_complete(
                execution_id=execution_id,
                result={"portfolio_return": 12.5, "sharpe_ratio": 1.8},
                execution_time_ms=2345,
                success=True
            )
            logger.info(f"✅ Execution completed: {result}")
            
            # Test 5d: Verify completion in DB
            logger.info("Test 5d: Verifying completion in DB...")
            completed_doc = await self.db_client.db.executions.find_one({"executionId": execution_id})
            assert completed_doc is not None, "Completed execution not found"
            assert completed_doc["status"] == "success"
            assert completed_doc["execution_time_ms"] == 2345
            logger.info(f"✅ Completion verified: status={completed_doc['status']}, time={completed_doc['execution_time_ms']}ms")
            
            # Test 5e: Get execution history
            logger.info("Test 5e: Getting execution history for session...")
            history = await self.audit_service.get_execution_history(session_id)
            logger.info(f"✅ Retrieved {len(history)} executions for session")
            assert len(history) > 0, "No execution history found"
            
            # Test 5f: Get user execution history
            logger.info("Test 5f: Getting execution history for user...")
            user_history = await self.audit_service.get_user_execution_history(user_id)
            logger.info(f"✅ Retrieved {len(user_history)} executions for user")
            
            self.test_results.append((test_name, True, "Audit operations successful"))
            return True
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results.append((test_name, False, str(e)))
            return False

    async def test_end_to_end_workflow(self):
        """Test 6: End-to-end workflow simulating actual usage"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST 6: End-to-End Workflow")
        logger.info("=" * 80)
        
        test_name = "End-to-End Workflow"
        user_id = "test-user-e2e"
        
        try:
            logger.info("Simulating complete user workflow...")
            
            # Step 1: Create new session
            logger.info("\n  Step 1: User starts new conversation")
            session_id = await self.chat_service.start_session(user_id, "Portfolio Analysis Session")
            logger.info(f"  ✅ Session created: {session_id}")
            
            # Step 2: User asks question
            logger.info("\n  Step 2: User asks question")
            question = "What is my portfolio volatility over 30 days?"
            msg_id = await self.chat_service.add_user_message(
                session_id=session_id,
                user_id=user_id,
                question=question
            )
            logger.info(f"  ✅ Question stored: {msg_id}")
            
            # Step 3: Check cache (miss)
            logger.info("\n  Step 3: Checking cache (expect miss)")
            cached = await self.cache_service.get_cached_result(question, {"session_id": session_id})
            assert cached is None, "Expected cache miss on first question"
            logger.info("  ✅ Cache miss confirmed")
            
            # Step 4: Generate analysis (simulate)
            logger.info("\n  Step 4: Generating analysis")
            analysis_result = {"volatility": 23.5, "days": 30}
            analysis_id = await self.analysis_service.create_analysis(
                user_id=user_id,
                title=question,
                description="30-day portfolio volatility analysis",
                result=analysis_result,
                parameters={"days": 30},
                mcp_calls=["alpaca_bars", "calculate_volatility"],
                category="portfolio_analysis"
            )
            logger.info(f"  ✅ Analysis generated and saved: {analysis_id}")
            
            # Step 5: Log execution
            logger.info("\n  Step 5: Logging execution")
            exec_id = await self.audit_service.log_execution_start(
                user_id=user_id,
                session_id=session_id,
                message_id=msg_id,
                question=question,
                script="volatility_calc.py",
                parameters={"days": 30},
                mcp_calls=["alpaca_bars", "calculate_volatility"]
            )
            logger.info(f"  ✅ Execution logged: {exec_id}")
            
            # Step 6: Add assistant response with analysis
            logger.info("\n  Step 6: Adding AI response with analysis")
            analysis_model = AnalysisModel(
                userId=user_id,
                question=question,
                llm_response={
                    "status": "success",
                    "script_name": "volatility_calc.py",
                    "analysis_description": "30-day portfolio volatility",
                    "execution": {
                        "script_name": "volatility_calc.py",
                        "parameters": {"days": 30}
                    }
                },
                script_url="/tmp/volatility_calc.py",
                script_size_bytes=0
            )
            
            response_id = await self.chat_service.add_assistant_message_with_analysis(
                session_id=session_id,
                user_id=user_id,
                script="volatility_calc.py",
                explanation="Your portfolio volatility over the past 30 days is 23.5%",
                analysis=analysis_model,
                execution_id=exec_id
            )
            logger.info(f"  ✅ Response stored with analysis: {response_id}")
            
            # Step 7: Complete execution
            logger.info("\n  Step 7: Completing execution")
            await self.audit_service.log_execution_complete(
                execution_id=exec_id,
                result=analysis_result,
                execution_time_ms=1234,
                success=True
            )
            logger.info("  ✅ Execution completed")
            
            # Step 8: Cache result
            logger.info("\n  Step 8: Caching result")
            cache_id = await self.cache_service.cache_analysis_result(
                question=question,
                parameters={"days": 30, "session_id": session_id},
                result={"response": "Your portfolio volatility is 23.5%", "data": analysis_result},
                analysis_id=analysis_id
            )
            logger.info(f"  ✅ Result cached: {cache_id}")
            
            # Step 9: Verify cache hit on same question
            logger.info("\n  Step 9: Verifying cache hit on same question")
            cached_result = await self.cache_service.get_cached_result(
                question,
                {"days": 30, "session_id": session_id}
            )
            assert cached_result is not None, "Expected cache hit"
            logger.info("  ✅ Cache hit verified - returning cached result")
            
            # Step 10: Get full conversation history
            logger.info("\n  Step 10: Retrieving full conversation")
            history = await self.chat_service.get_conversation_history(session_id)
            logger.info(f"  ✅ Retrieved {len(history)} messages in conversation")
            logger.info(f"     - User message: {history[0].get('content', 'N/A')[:60]}")
            logger.info(f"     - AI response: {history[1].get('content', 'N/A')[:60]}")
            
            # Step 11: Get execution history
            logger.info("\n  Step 11: Retrieving execution history")
            exec_history = await self.audit_service.get_execution_history(session_id)
            logger.info(f"  ✅ Retrieved {len(exec_history)} executions")
            logger.info(f"     - Execution time: {exec_history[0].execution_time_ms}ms")
            
            logger.info("\n✅ End-to-end workflow completed successfully")
            self.test_results.append((test_name, True, "Complete workflow successful"))
            return True
            
        except Exception as e:
            logger.error(f"❌ {test_name} failed: {e}")
            import traceback
            traceback.print_exc()
            self.test_results.append((test_name, False, str(e)))
            return False

    async def cleanup(self):
        """Clean up test data from MongoDB"""
        logger.info("\n" + "=" * 80)
        logger.info("CLEANUP: SKIPPING DATA DELETION FOR INSPECTION")
        logger.info("=" * 80)
        
        try:
            db = self.db_client.db
            
            # Count documents for inspection
            collections_to_check = ["chat_sessions", "chat_messages", "analyses", "executions", "cache"]
            logger.info("\n📊 Data in MongoDB (for inspection):")
            for coll in collections_to_check:
                count = await db[coll].count_documents({})
                logger.info(f"  - {coll}: {count} documents")
            
            logger.info("\n✅ Data preserved for inspection")
            
            if self.repo_manager:
                await self.repo_manager.shutdown()
                logger.info("✅ Repository manager shutdown")
                
        except Exception as e:
            logger.warning(f"⚠️ Cleanup error: {e}")

    def print_results(self):
        """Print summary of test results"""
        logger.info("\n" + "=" * 80)
        logger.info("TEST SUMMARY")
        logger.info("=" * 80)
        
        passed = sum(1 for _, success, _ in self.test_results if success)
        total = len(self.test_results)
        
        for test_name, success, message in self.test_results:
            status = "✅ PASS" if success else "❌ FAIL"
            logger.info(f"{status}: {test_name}")
            if not success:
                logger.info(f"    Error: {message}")
        
        logger.info("\n" + "-" * 80)
        logger.info(f"Results: {passed}/{total} tests passed")
        logger.info("=" * 80 + "\n")
        
        return passed == total

    async def run_all_tests(self):
        """Run complete test suite"""
        logger.info("🧪 STARTING INTEGRATION TEST SUITE\n")
        
        # Setup
        if not await self.setup():
            logger.error("❌ Setup failed, cannot run tests")
            return False
        
        # Run all tests
        tests = [
            self.test_mongodb_connection,
            self.test_chat_service,
            self.test_cache_service,
            self.test_analysis_persistence_service,
            self.test_audit_service,
            self.test_end_to_end_workflow,
        ]
        
        for test in tests:
            await test()
        
        # Cleanup
        await self.cleanup()
        
        # Print summary
        all_passed = self.print_results()
        
        return all_passed


async def main():
    tester = ServiceIntegrationTester()
    success = await tester.run_all_tests()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
