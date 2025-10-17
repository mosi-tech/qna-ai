#!/usr/bin/env python3
"""
Optional Development Data Seeder
Use this script to populate the database with sample data for development/testing
Run: python scripts/seed_development_data.py
"""

import asyncio
import sys
import logging
from datetime import datetime, timedelta
from typing import List

sys.path.insert(0, '/Users/shivc/Documents/Workspace/JS/qna-ai-admin/ollama-server/scriptEdition/apiServer')

from db import MongoDBClient, RepositoryManager
from db.schemas import (
    UserModel, ChatSessionModel, ChatMessageModel, 
    AnalysisModel, ExecutionModel, ExecutionStatus, 
    QueryType, RoleType, QuestionContext
)
from services.chat_service import ChatHistoryService
from services.analysis_persistence_service import AnalysisPersistenceService
from services.audit_service import AuditService

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("seeder")


class DevelopmentDataSeeder:
    def __init__(self):
        self.db_client = None
        self.repo_manager = None
        self.chat_service = None
        self.analysis_service = None
        self.audit_service = None

    async def initialize(self):
        """Initialize database connections"""
        logger.info("🔌 Connecting to MongoDB...")
        self.db_client = MongoDBClient()
        
        logger.info("📦 Initializing repository manager...")
        self.repo_manager = RepositoryManager(self.db_client)
        await self.repo_manager.initialize()
        
        self.chat_service = ChatHistoryService(self.repo_manager)
        self.analysis_service = AnalysisPersistenceService(self.repo_manager)
        self.audit_service = AuditService(self.repo_manager)
        
        logger.info("✅ Database initialized")

    async def seed_users(self) -> List[str]:
        """Create sample users"""
        logger.info("\n📝 Seeding users...")
        
        users_data = [
            {
                "email": "alice@example.com",
                "username": "alice_trader",
                "preferences": {"timezone": "UTC", "theme": "dark"}
            },
            {
                "email": "bob@example.com",
                "username": "bob_investor",
                "preferences": {"timezone": "EST", "theme": "light"}
            },
            {
                "email": "charlie@example.com",
                "username": "charlie_analyst",
                "preferences": {"timezone": "PST", "theme": "dark"}
            }
        ]
        
        user_ids = []
        for user_data in users_data:
            user = UserModel(**user_data)
            user_id = await self.repo_manager.db.create_user(user)
            user_ids.append(user_id)
            logger.info(f"  ✓ Created user: {user_data['username']}")
        
        return user_ids

    async def seed_sessions_and_conversations(self, user_ids: List[str]):
        """Create sample chat sessions with conversations"""
        logger.info("\n💬 Seeding chat sessions and conversations...")
        
        conversations = [
            {
                "user_id": user_ids[0],
                "title": "AAPL Technical Analysis",
                "description": "Analyzing AAPL price and volatility patterns",
                "messages": [
                    {
                        "role": "user",
                        "content": "What is AAPL's 30-day volatility?",
                        "question": "What is AAPL's 30-day volatility?"
                    },
                    {
                        "role": "assistant",
                        "content": "AAPL's 30-day volatility is approximately 25.3%. This indicates moderate price fluctuations."
                    },
                    {
                        "role": "user",
                        "content": "How does this compare to SPY?",
                        "question": "How does AAPL volatility compare to SPY?"
                    },
                    {
                        "role": "assistant",
                        "content": "SPY has a 30-day volatility of 18.7%, so AAPL is more volatile by about 6.6 percentage points."
                    }
                ]
            },
            {
                "user_id": user_ids[1],
                "title": "Portfolio Correlation Analysis",
                "description": "Studying correlations between portfolio holdings",
                "messages": [
                    {
                        "role": "user",
                        "content": "What are the correlations between AAPL, MSFT, and GOOGL?",
                        "question": "What are the correlations between AAPL, MSFT, and GOOGL?"
                    },
                    {
                        "role": "assistant",
                        "content": "AAPL-MSFT correlation: 0.82, AAPL-GOOGL correlation: 0.75, MSFT-GOOGL correlation: 0.88"
                    }
                ]
            },
            {
                "user_id": user_ids[2],
                "title": "Market Volatility Research",
                "description": "Comparing sector volatility metrics",
                "messages": [
                    {
                        "role": "user",
                        "content": "Which sector has the highest volatility?",
                        "question": "Which sector has the highest volatility?"
                    },
                    {
                        "role": "assistant",
                        "content": "Technology sector has the highest volatility at 28.5%, followed by Healthcare at 22.1%"
                    },
                    {
                        "role": "user",
                        "content": "What about Energy?",
                        "question": "What is Energy sector volatility?"
                    },
                    {
                        "role": "assistant",
                        "content": "Energy sector volatility is 24.3%, placing it third among major sectors."
                    }
                ]
            }
        ]
        
        for conv_data in conversations:
            user_id = conv_data["user_id"]
            
            # Create session
            session_id = await self.chat_service.start_session(
                user_id,
                conv_data["title"]
            )
            
            # Add messages
            for i, msg_data in enumerate(conv_data["messages"]):
                if msg_data["role"] == "user":
                    await self.chat_service.add_user_message(
                        session_id=session_id,
                        user_id=user_id,
                        question=msg_data.get("question", msg_data["content"]),
                        query_type=QueryType.COMPLETE if i == 0 else QueryType.CONTEXTUAL
                    )
                else:
                    await self.chat_service.add_assistant_message(
                        session_id=session_id,
                        user_id=user_id,
                        content=msg_data["content"]
                    )
            
            logger.info(f"  ✓ Created session: {conv_data['title']} ({len(conv_data['messages'])} messages)")

    async def seed_analyses(self, user_ids: List[str]):
        """Create sample analyses"""
        logger.info("\n📊 Seeding analyses...")
        
        analyses_data = [
            {
                "user_id": user_ids[0],
                "title": "30-Day AAPL Volatility",
                "description": "Technical analysis of AAPL volatility over 30 days",
                "category": "technical_analysis",
                "result": {"volatility": 25.3, "period_days": 30, "status": "stable"}
            },
            {
                "user_id": user_ids[0],
                "title": "Support/Resistance Levels",
                "description": "Key price levels for AAPL stock",
                "category": "technical_analysis",
                "result": {"support": 170, "resistance": 185, "pivot": 177.5}
            },
            {
                "user_id": user_ids[1],
                "title": "Portfolio Correlation Matrix",
                "description": "Correlation analysis of portfolio holdings",
                "category": "portfolio_analysis",
                "result": {
                    "correlations": {
                        "AAPL-MSFT": 0.82,
                        "AAPL-GOOGL": 0.75,
                        "MSFT-GOOGL": 0.88
                    }
                }
            },
            {
                "user_id": user_ids[1],
                "title": "Portfolio Diversification Score",
                "description": "Measuring portfolio diversification",
                "category": "portfolio_analysis",
                "result": {"diversification_score": 0.72, "risk_level": "moderate"}
            },
            {
                "user_id": user_ids[2],
                "title": "Sector Volatility Comparison",
                "description": "Comparing volatility across sectors",
                "category": "sector_analysis",
                "result": {
                    "sectors": {
                        "Technology": 28.5,
                        "Healthcare": 22.1,
                        "Energy": 24.3,
                        "Utilities": 18.2
                    }
                }
            }
        ]
        
        for analysis_data in analyses_data:
            await self.analysis_service.create_analysis(
                user_id=analysis_data["user_id"],
                title=analysis_data["title"],
                description=analysis_data["description"],
                result=analysis_data["result"],
                parameters={},
                mcp_calls=["alpaca_bars", "calculate_volatility"],
                category=analysis_data["category"],
                script="analysis.py",
                tags=["development", "sample"]
            )
            logger.info(f"  ✓ Created analysis: {analysis_data['title']}")

    async def seed_executions(self, user_ids: List[str]):
        """Create sample execution records"""
        logger.info("\n⚙️  Seeding execution records...")
        
        executions_data = [
            {
                "user_id": user_ids[0],
                "question": "What is AAPL's 30-day volatility?",
                "status": ExecutionStatus.SUCCESS,
                "time_ms": 1234
            },
            {
                "user_id": user_ids[0],
                "question": "Compare AAPL volatility to SPY",
                "status": ExecutionStatus.SUCCESS,
                "time_ms": 2156
            },
            {
                "user_id": user_ids[1],
                "question": "Calculate portfolio correlations",
                "status": ExecutionStatus.SUCCESS,
                "time_ms": 3421
            },
            {
                "user_id": user_ids[1],
                "question": "Analyze portfolio diversification",
                "status": ExecutionStatus.SUCCESS,
                "time_ms": 1876
            },
            {
                "user_id": user_ids[2],
                "question": "Compare sector volatility",
                "status": ExecutionStatus.SUCCESS,
                "time_ms": 2543
            }
        ]
        
        for exec_data in executions_data:
            # Create a dummy session and message for execution linking
            session_id = await self.chat_service.start_session(
                exec_data["user_id"],
                f"Execution session for {exec_data['question'][:50]}"
            )
            
            msg_id = await self.chat_service.add_user_message(
                session_id=session_id,
                user_id=exec_data["user_id"],
                question=exec_data["question"]
            )
            
            exec_id = await self.audit_service.log_execution_start(
                user_id=exec_data["user_id"],
                session_id=session_id,
                message_id=msg_id,
                question=exec_data["question"],
                script="analysis.py",
                parameters={},
                mcp_calls=["alpaca_bars"]
            )
            
            await self.audit_service.log_execution_complete(
                execution_id=exec_id,
                result={"status": "completed"},
                execution_time_ms=exec_data["time_ms"],
                success=True
            )
            
            logger.info(f"  ✓ Created execution: {exec_data['question'][:50]}...")

    async def shutdown(self):
        """Cleanup resources"""
        if self.repo_manager:
            await self.repo_manager.shutdown()
            logger.info("\n✅ Seeding complete! Database ready for use.")

    async def run(self):
        """Run complete seeding"""
        logger.info("=" * 80)
        logger.info("DEVELOPMENT DATA SEEDER")
        logger.info("=" * 80)
        
        try:
            await self.initialize()
            user_ids = await self.seed_users()
            await self.seed_sessions_and_conversations(user_ids)
            await self.seed_analyses(user_ids)
            await self.seed_executions(user_ids)
            
            logger.info("\n" + "=" * 80)
            logger.info("📊 SEEDING SUMMARY:")
            logger.info("=" * 80)
            logger.info(f"✓ Created {len(user_ids)} users")
            logger.info(f"✓ Created 3 chat sessions with conversations")
            logger.info(f"✓ Created 5 analysis records")
            logger.info(f"✓ Created 5 execution records")
            logger.info("\nYou can now:")
            logger.info("- Start the server: python server.py")
            logger.info("- Test endpoints with seeded data")
            logger.info("- Query using user IDs printed above")
            logger.info("=" * 80)
            
        except Exception as e:
            logger.error(f"❌ Seeding failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        finally:
            await self.shutdown()
        
        return True


async def main():
    seeder = DevelopmentDataSeeder()
    success = await seeder.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    asyncio.run(main())
