"""
FastAPI Server Setup and Configuration
"""

import logging
import uvicorn
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import sys
import os
import uuid
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.models import QuestionRequest, AnalysisResponse
from services.analysis import AnalysisService
from pydantic import BaseModel, Field
from services.search import SearchService
from services.chat_service import ChatHistoryService
from services.cache_service import CacheService
from services.analysis_persistence_service import AnalysisPersistenceService
from services.audit_service import AuditService
from services.execution_service import ExecutionService
from services.progress_service import progress_manager
from api.routes import APIRoutes
from api.progress_routes import router as progress_router
from api.session_routes import router as session_router
from db import MongoDBClient, RepositoryManager

logger = logging.getLogger("api-server")


class SessionRequest(BaseModel):
    user_id: str
    title: Optional[str] = None


class SessionResponse(BaseModel):
    session_id: str
    user_id: str


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    logger.info("🚀 Starting Financial Analysis Server...")
    
    try:
        # 1. MongoDB and repository layer (CRITICAL)
        logger.info("📦 Initializing MongoDB connection...")
        db_client = MongoDBClient()
        repo_manager = RepositoryManager(db_client)
        await repo_manager.initialize()
        logger.info("✅ MongoDB initialized")
        app.state.repo_manager = repo_manager
        
        # 2. Data persistence services (CRITICAL)
        logger.info("🔧 Initializing persistence services...")
        chat_history_service = ChatHistoryService(repo_manager)
        cache_service = CacheService(repo_manager)
        analysis_persistence_service = AnalysisPersistenceService(repo_manager)
        audit_service = AuditService(repo_manager)
        execution_service = ExecutionService(repo_manager)
        logger.info("✅ Persistence services initialized")
        
        # 3. Session manager (CRITICAL)
        logger.info("🔧 Initializing session manager...")
        from dialogue.conversation.session_manager import SessionManager
        session_manager = SessionManager(chat_history_service=chat_history_service)
        app.state.session_manager = session_manager
        logger.info("✅ Session manager initialized")
        
        # 4. Core services (CRITICAL)
        logger.info("🔧 Initializing core services...")
        analysis_service = AnalysisService()
        search_service = SearchService()
        logger.info("✅ Core services initialized")
        
        # 5. API routes (CRITICAL)
        logger.info("🔧 Initializing API routes...")
        logger.info("  → Creating APIRoutes instance...")
        api_routes = APIRoutes(
            analysis_service,
            search_service,
            chat_history_service,
            cache_service,
            analysis_persistence_service,
            audit_service,
            execution_service,
            session_manager=session_manager
        )
        logger.info("✅ API routes initialized successfully")
        
        # Store all in app state
        app.state.repo_manager = repo_manager
        app.state.chat_history_service = chat_history_service
        app.state.cache_service = cache_service
        app.state.analysis_persistence_service = analysis_persistence_service
        app.state.audit_service = audit_service
        app.state.execution_service = execution_service
        app.state.session_manager = session_manager
        app.state.analysis_service = analysis_service
        app.state.search_service = search_service
        app.state.api_routes = api_routes
        
        provider = analysis_service.llm_service.provider_type.upper()
        logger.info(f"✅ Server ready with {provider} provider")
        
    except Exception as e:
        logger.error(f"❌ FATAL: Server initialization failed: {e}")
        logger.error("❌ Cannot start server - check database, API keys, and dependencies")
        raise RuntimeError(f"Server initialization failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Financial Analysis Server...")
    await app.state.analysis_service.close_sessions()
    
    # Shutdown database
    if app.state.repo_manager:
        await app.state.repo_manager.shutdown()
    
    logger.info("✅ Shutdown complete")


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    app = FastAPI(
        title="Financial Analysis Server",
        description="Universal LLM service for financial analysis with MCP integration",
        version="1.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include progress streaming routes
    app.include_router(progress_router)
    
    # Include session routes
    app.include_router(session_router)
    
    # Session Management Routes (integrated with backend SessionManager)
    @app.post("/session/start", response_model=SessionResponse)
    async def start_session(request: SessionRequest):
        """Start a new session using backend SessionManager"""
        try:
            session_id = await app.state.session_manager.create_session(
                user_id=request.user_id,
                title=request.title
            )
            return SessionResponse(session_id=session_id, user_id=request.user_id)
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise HTTPException(status_code=500, detail="Failed to create session")
    
    @app.get("/session/{session_id}")
    async def get_session(session_id: str):
        """Get session details from backend"""
        try:
            store = await app.state.session_manager.get_session(session_id)
            
            # Get context summary
            context = store.get_context_summary() if store and hasattr(store, 'get_context_summary') else {}
            
            return {
                "session_id": session_id,
                "status": "active",
                "messages": store.turns if hasattr(store, 'turns') else [],
                "context_summary": context
            }
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            return {
                "session_id": session_id,
                "status": "error",
                "messages": [],
                "context_summary": {}
            }
    
    @app.post("/analyze", response_model=AnalysisResponse)
    async def analyze_question(request: QuestionRequest):
        """Analyze a financial question and generate tool calls without execution"""
        return await app.state.api_routes.analyze_question(request)
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return await app.state.api_routes.health_check()
    
    @app.get("/debug/mcp-tools")
    async def debug_mcp_tools():
        """Debug endpoint to check MCP tools"""
        return await app.state.api_routes.debug_mcp_tools()
    
    @app.get("/debug/system-prompt")
    async def debug_system_prompt():
        """Debug endpoint to check system prompt"""
        return await app.state.api_routes.debug_system_prompt()
    
    @app.get("/debug/test-tool-processing")
    async def test_tool_result_processing():
        """Test endpoint to verify tool result processing pipeline"""
        return await app.state.api_routes.test_tool_result_processing()
    
    @app.get("/models")
    async def list_models():
        """List available models for the current provider"""
        return await app.state.api_routes.list_models()
    
    @app.post("/conversation/confirm")
    async def confirm_expansion(session_id: str, confirmed: bool):
        """Handle user confirmation for query expansion"""
        return await app.state.api_routes.confirm_expansion(session_id, confirmed)
    
    @app.post("/clarification/{session_id}")
    async def handle_clarification_response(session_id: str, 
                                           user_response: str,
                                           original_query: str,
                                           expanded_query: str):
        """Handle user response to clarification prompt"""
        return await app.state.api_routes.handle_clarification_response(
            session_id=session_id,
            user_response=user_response,
            original_query=original_query,
            expanded_query=expanded_query
        )
    
    @app.get("/conversation/{session_id}/context")
    async def get_session_context(session_id: str):
        """Get conversation context for debugging"""
        return await app.state.api_routes.get_session_context(session_id)
    
    @app.get("/conversation/sessions")
    async def list_sessions():
        """List active conversation sessions"""
        return await app.state.api_routes.list_sessions()
    
    @app.get("/chat/{session_id}/history")
    async def get_chat_history(session_id: str):
        """Get chat history for a session"""
        return await app.state.api_routes.get_chat_history(session_id)
    
    @app.get("/user/{user_id}/sessions")
    async def get_user_sessions(user_id: str, limit: int = 50):
        """Get all sessions for a user"""
        return await app.state.api_routes.get_user_sessions(user_id, limit=limit)
    
    @app.get("/user/{user_id}/analyses")
    async def get_reusable_analyses(user_id: str):
        """Get all reusable analyses for a user"""
        return await app.state.api_routes.get_reusable_analyses(user_id)
    
    @app.get("/user/{user_id}/analyses/search")
    async def search_analyses(user_id: str, q: str, limit: int = 50):
        """Search analyses by title/description"""
        return await app.state.api_routes.search_analyses(user_id, q, limit=limit)
    
    @app.get("/session/{session_id}/executions")
    async def get_execution_history(session_id: str, limit: int = 100):
        """Get execution history for a session"""
        return await app.state.api_routes.get_execution_history(session_id, limit=limit)
    
    @app.post("/execute/{analysis_id}")
    async def execute_analysis(analysis_id: str, user_id: str, session_id: Optional[str] = None):
        """Execute an analysis script and populate results"""
        return await app.state.api_routes.execute_analysis(analysis_id, user_id, session_id)
    
    return app


def run_server(host: str = "0.0.0.0", port: int = 8010, reload: bool = False, debug: bool = False):
    """Run the FastAPI server"""
    # Configure logging
    # Configure logging based on debug flag
    log_level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if debug:
        logger.info("🐛 Debug mode enabled - detailed MCP call logging activated")
    
    # Create and run app
    app = create_app()
    
    logger.info(f"🌐 Starting server on http://{host}:{port}")
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=reload,
        log_config=None  # Use our own logging configuration
    )


if __name__ == "__main__":
    import os
    
    provider = os.getenv("LLM_PROVIDER", "anthropic").lower()
    
    print(f"🚀 Starting Universal LLM Script Generation Server ({provider.upper()})...")
    print("📁 Using modular architecture for better maintainability")
    print("🌐 Server will be available at: http://localhost:8010")
    print("📖 API Documentation at: http://localhost:8010/docs")
    print("\n🧪 To test the server, send a POST request to /analyze with:")
    print("   💬 Complete questions: {'question': 'What are my portfolio correlations?'}")
    print("   🔄 Contextual questions: {'question': 'what about QQQ to SPY', 'session_id': 'session-123'}")
    print("\n🆕 Conversation features:")
    print("   • Contextual queries (references previous questions)")
    print("   • Session management with auto-cleanup")
    print("   • Query expansion with confidence scoring")
    print("   • GET /conversation/sessions - list active sessions")
    print("   • GET /conversation/{session_id}/context - debug session")
    
    if provider == "anthropic":
        anthropic_model = os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-20241022")
        print(f"\n✅ Make sure you have:")
        print("   1. LLM_PROVIDER=anthropic (default)")
        print("   2. ANTHROPIC_API_KEY environment variable set")
        print(f"   3. Model: {anthropic_model} (set via ANTHROPIC_MODEL or default)")
    else:
        print(f"\n✅ Make sure you have:")
        print("   1. LLM_PROVIDER=ollama")
        print("   2. Ollama running: ollama serve")
        print("   3. OLLAMA_BASE_URL (default: http://localhost:11434)")
        print("   4. OLLAMA_MODEL (default: llama3.2)")
    
    print("\n🔧 Required MCP servers (must be running):")
    print("   - Financial server: mcp-server/financial_server.py")
    print("   - Analytics server: mcp-server/analytics_server.py") 
    print("   - Validation server: mcp-server/mcp_script_validation_server.py")
    
    print(f"\n🎯 This server will:")
    print("   - Connect to MCP servers for function discovery")
    print(f"   - Generate parameterized Python scripts using {provider.upper()}")
    print("   - Scripts will auto-validate using MCP validation server")
    print("   - Use OpenAI-compatible API for tool calling")
    print("   - Scripts ready for execution via HTTP execution server")
    
    print("\n📦 Modular Architecture:")
    print("   - models.py: Data schemas and validation")
    print("   - cache_manager.py: Anthropic prompt caching")
    print("   - mcp_integration.py: MCP client management")
    print("   - llm_service.py: Core LLM service logic")
    print("   - routes.py: API endpoint handlers")
    print("   - server.py: FastAPI app setup and lifecycle")
    
    print("\n" + "="*50)
    
    # Run the server
    run_server(host="0.0.0.0", port=8010, reload=False)