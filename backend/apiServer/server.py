"""
FastAPI Server Setup and Configuration
"""

import logging
import uvicorn
from contextlib import asynccontextmanager
from typing import Optional
from fastapi import FastAPI, HTTPException, Depends, Response, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
        
from dotenv import load_dotenv

import sys
import os
import json

# Load environment variables from .env file
load_dotenv()

# Add backend root to Python path so imports like 'from shared...' work
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from api.models import QuestionRequest, AnalysisResponse
from shared.analyze.services.analysis_service import AnalysisService
from pydantic import BaseModel, Field
from shared.services.search import SearchService
from shared.services.chat_service import ChatHistoryService
from shared.services.cache_service import CacheService
from shared.analyze.services.analysis_persistence_service import AnalysisPersistenceService
from shared.services.audit_service import AuditService
from services.execution_service import ExecutionService
from services.sse import progress_sse_manager
from services.progress_monitor import initialize_progress_monitor, cleanup_progress_monitor
from api.routes import APIRoutes
from api.execution_routes import ExecutionRoutes
from api.auth import UserContext, require_authenticated_user, get_optional_user
from api.progress_routes import router as progress_router
from api.session_routes import router as session_router
from api.analysis_routes import router as analysis_router
from api.dashboard_routes import router as dashboard_router
from shared.db import MongoDBClient, RepositoryManager
from shared.services.session_manager import SessionManager
from shared.locking import initialize_session_lock
from shared.queue.analysis_queue import initialize_analysis_queue
from shared.health.health_checker import HealthChecker
from api.health_routes import router as health_router, initialize_health_checker

logger = logging.getLogger("api-server")


class SessionRequest(BaseModel):
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
        
        logger.info("🔧 Initializing progress monitor...")
        await initialize_progress_monitor(db_client.db)
        logger.info("✅ Progress monitor initialized")
        
        # Initialize distributed session locking
        logger.info("🔧 Initializing session locking...")
        
        await initialize_session_lock(db_client.db)
        logger.info("✅ Session locking initialized")
        
        # Initialize progress event queue (needed for real-time progress updates)
        logger.info("🔧 Initializing progress event queue...")
        from shared.queue.progress_event_queue import initialize_progress_event_queue
        initialize_progress_event_queue(db_client.db)
        logger.info("✅ Progress event queue initialized")
        
        # Initialize analysis queue
        logger.info("🔧 Initializing analysis queue...")
        initialize_analysis_queue(db_client.db)
        logger.info("✅ Analysis queue initialized")

        # Dashboard orchestrator (Phase 7)
        logger.info("🔧 Initializing dashboard orchestrator...")
        try:
            from shared.queue.analysis_queue import get_analysis_queue
            from shared.services.ui_planner import create_ui_planner
            from shared.services.block_cache_service import create_block_cache_service
            from shared.services.dashboard_orchestrator import create_dashboard_orchestrator

            _ui_planner  = create_ui_planner()
            _block_cache = create_block_cache_service(repo_manager.dashboard)
            _dash_orch   = create_dashboard_orchestrator(
                repo_manager=repo_manager,
                analysis_queue=get_analysis_queue(),
                ui_planner=_ui_planner,
                block_cache=_block_cache,
            )
            app.state.dashboard_orch = _dash_orch
            logger.info("✅ Dashboard orchestrator initialized")
        except Exception as _orch_err:
            logger.warning("⚠️ Dashboard orchestrator failed to initialize: %s", _orch_err)
            app.state.dashboard_orch = None
        
        # 3. Redis client for ConversationStore
        logger.info("🔧 Initializing Redis client...")
        try:
            from shared.services.redis_client import get_redis_client
            redis_client = await get_redis_client()
            if redis_client:
                logger.info("✅ Redis client initialized for ConversationStore")
            else:
                logger.warning("⚠️ Redis client unavailable - ConversationStore will use DB-only mode")
        except Exception as e:
            logger.warning(f"⚠️ Redis client initialization failed: {e}")
            redis_client = None
        
        # 4. Session manager (CRITICAL)
        logger.info("🔧 Initializing session manager...")
        
        session_manager = SessionManager(
            chat_history_service=chat_history_service,
            redis_client=redis_client
        )
        app.state.session_manager = session_manager
        logger.info("✅ Session manager initialized with Redis support")
        
        # 5. API routes (CRITICAL)
        logger.info("🔧 Initializing API routes...")
        logger.info("  → Creating APIRoutes instance...")
        api_routes = APIRoutes(
            chat_history_service=chat_history_service,
            cache_service=cache_service,
            analysis_persistence_service=analysis_persistence_service,
            audit_service=audit_service,
            execution_service=execution_service,
            session_manager=session_manager,
            analysis_pipeline_service=None  # Analysis is handled by queue worker
        )
        logger.info("  → Creating ExecutionRoutes instance...")
        execution_routes = ExecutionRoutes()
        logger.info("✅ API routes initialized successfully")
        
        # 6. Run comprehensive health checks (non-blocking - warns but doesn't fail startup)
        logger.info("🏥 Running comprehensive health checks...")
        try:
            health_config = {
                "mongo_url": os.getenv("MONGO_URL", "mongodb://localhost:27017"),
                "mongo_db_name": os.getenv("MONGO_DB_NAME", "qna_ai_admin"),
                "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
                "chromadb_url": os.getenv("CHROMADB_URL", "http://localhost:8050"),
                "llm_base_url": os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1"),
                "llm_model": os.getenv("OPENAI_MODEL", "llama3.2"),
            }
            health_checker = await initialize_health_checker(health_config)
            app.state.health_checker = health_checker
            
            if health_checker.is_ready():
                logger.info("✅ All critical services ready - API accepting requests")
            else:
                unhealthy = [
                    s.name for s in health_checker.services.values() 
                    if s.required and s.status.value != "healthy"
                ]
                logger.error(f"⚠️ CRITICAL: These required services are unavailable: {', '.join(unhealthy)}")
                logger.error("⚠️ API will start but may fail on feature requests that depend on these services")
                logger.error("⚠️ Check /health/status for details")
        except Exception as e:
            logger.error(f"❌ Health check failed: {e}")
            # Don't block startup - health checks are informational
        
        # Store all in app state
        app.state.repo_manager = repo_manager
        app.state.chat_history_service = chat_history_service
        app.state.cache_service = cache_service
        app.state.analysis_persistence_service = analysis_persistence_service
        app.state.audit_service = audit_service
        app.state.execution_service = execution_service
        app.state.session_manager = session_manager
        app.state.api_routes = api_routes
        app.state.execution_routes = execution_routes
        
    except Exception as e:
        logger.error(f"❌ FATAL: Server initialization failed: {e}")
        logger.error("❌ Cannot start server - check database, API keys, and dependencies")
        raise RuntimeError(f"Server initialization failed: {e}")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Financial Analysis Server...")
    await cleanup_progress_monitor()
    
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
    
    # Add CORS middleware (applied before session)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Add session middleware LAST (will be applied first due to reverse order)
    app.add_middleware(
        SessionMiddleware,
        secret_key=os.getenv("SESSION_SECRET_KEY", "your-secret-key-change-in-production"),
        max_age=3600,  # 1 hour
    )
    
    # Include health check routes (MUST be before other routes)
    app.include_router(health_router)
    
    # Include progress streaming routes
    app.include_router(progress_router)
    
    # Include session routes
    app.include_router(session_router)
    
    # Include analysis routes
    app.include_router(analysis_router)

    # Include dashboard routes (Phase 7)
    app.include_router(dashboard_router)

    # Session Management Routes (integrated with backend SessionManager)
    @app.post("/session/start", response_model=SessionResponse)
    async def start_session(
        request: SessionRequest,
        user_context: UserContext = Depends(require_authenticated_user)
    ):
        """Start a new session using backend SessionManager"""
        try:
            # Use authenticated user's ID instead of request user_id
            session_id = await app.state.session_manager.create_session(
                user_id=user_context.user_id,
                title=request.title
            )
            return SessionResponse(session_id=session_id, user_id=user_context.user_id)
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise HTTPException(status_code=500, detail="Failed to create session")
    
    @app.get("/session/{session_id}")
    async def get_session(
        session_id: str,
        user_context: UserContext = Depends(require_authenticated_user)
    ):
        """Get session details from backend"""
        try:
            store = await app.state.session_manager.get_session(session_id)
            
            # Get basic context - legacy method removed, use SimplifiedFinancialContextManager for rich context
            context = {
                "message_count": len(store.messages) if hasattr(store, 'messages') else 0,
                "has_history": bool(store and hasattr(store, 'messages') and store.messages)
            }
            
            return {
                "session_id": session_id,
                "status": "active",
                "messages": [msg.to_dict() for msg in store.messages] if hasattr(store, 'messages') else [],
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
    async def analyze_question(
        request: QuestionRequest,
        user_context: UserContext = Depends(require_authenticated_user)
    ):
        """Analyze a financial question and generate tool calls without execution"""
        # Add user context to the request for logging and audit
        request.user_id = user_context.user_id
        return await app.state.api_routes.analyze_question(request)
    
    @app.post("/analyze-simple", response_model=AnalysisResponse)
    async def analyze_question_simple(request: QuestionRequest):
        """SIMPLE VERSION - Analyze question without session locking for debugging"""
        return await app.state.api_routes.analyze_question_simple(request)
    
    @app.post("/sessions/{session_id}/chat", response_model=AnalysisResponse)
    async def chat_with_analysis(
        session_id: str,
        request: QuestionRequest,
        user_context: UserContext = Depends(require_authenticated_user)
    ):
        """
        Hybrid chat + analysis endpoint (GitHub Issue #122)
        
        Intelligent routing between:
        - Educational financial chat responses
        - Analysis suggestions and confirmations  
        - Direct analysis execution when needed
        """
        # Add user context to the request for personalization and audit
        request.user_id = user_context.user_id
        # Set session_id from URL path (more RESTful than request body)
        request.session_id = session_id
        return await app.state.api_routes.chat_with_analysis(request)
    
    @app.post("/test-immediate")
    async def test_immediate(request: QuestionRequest):
        """ULTRA SIMPLE - Immediate response with no database calls"""
        response_data = {
            "success": True,
            "data": {
                "message": f"Received: {request.question}",
                "session_id": request.session_id,
                "timestamp": "immediate"
            }
        }
        
        # Force connection close to prevent connection pooling issues
        response = Response(
            content=json.dumps(response_data),
            media_type="application/json",
            headers={"Connection": "close"}
        )
        return response
    
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
    
    # Execution Queue Routes (Secured)
    @app.get("/execution/{execution_id}/status")
    async def get_execution_status(
        execution_id: str, 
        user_context: UserContext = Depends(require_authenticated_user)
    ):
        """Get the status of an execution (requires authentication)"""
        return await app.state.execution_routes.get_execution_status(execution_id, user_context)
    
    @app.get("/execution/{execution_id}/logs")
    async def get_execution_logs(
        execution_id: str, 
        user_context: UserContext = Depends(require_authenticated_user)
    ):
        """Get the logs for an execution (requires authentication)"""
        return await app.state.execution_routes.get_execution_logs(execution_id, user_context)
    
    
    @app.get("/user/executions")
    async def get_my_executions(
        limit: int = 50, 
        status: Optional[str] = None,
        user_context: UserContext = Depends(require_authenticated_user)
    ):
        """Get all executions for the authenticated user"""
        return await app.state.execution_routes.get_user_executions(user_context, limit=limit, status_filter=status)
    
    @app.get("/session/{session_id}/executions")
    async def get_session_executions(
        session_id: str, 
        limit: int = 50, 
        status: Optional[str] = None,
        user_context: UserContext = Depends(require_authenticated_user)
    ):
        """Get all executions for a specific session (user must own the executions)"""
        return await app.state.execution_routes.get_session_executions(session_id, user_context, limit=limit, status_filter=status)
    
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
    
    
    @app.get("/user/sessions")
    async def get_user_sessions(
        limit: int = 50,
        user_context: UserContext = Depends(require_authenticated_user)
    ):
        """Get all sessions for the authenticated user"""
        return await app.state.api_routes.get_user_sessions(user_context.user_id, limit=limit)
    
    @app.get("/user/analyses")
    async def get_reusable_analyses(
        user_context: UserContext = Depends(require_authenticated_user)
    ):
        """Get all reusable analyses for the authenticated user"""
        return await app.state.api_routes.get_reusable_analyses(user_context.user_id)
    
    @app.get("/user/analyses/search")
    async def search_analyses(
        q: str, 
        limit: int = 50,
        user_context: UserContext = Depends(require_authenticated_user)
    ):
        """Search analyses by title/description for the authenticated user"""
        return await app.state.api_routes.search_analyses(user_context.user_id, q, limit=limit)
    
    @app.get("/session/{session_id}/executions")
    async def get_execution_history(session_id: str, limit: int = 100):
        """Get execution history for a session"""
        return await app.state.api_routes.get_execution_history(session_id, limit=limit)
    
    @app.post("/execute/{analysis_id}")
    async def execute_analysis(
        analysis_id: str, 
        session_id: Optional[str] = None,
        user_context: UserContext = Depends(require_authenticated_user)
    ):
        """Execute an analysis script and populate results"""
        return await app.state.api_routes.execute_analysis(analysis_id, user_context.user_id, session_id)
    
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
        log_config=None,  # Use our own logging configuration
        workers=1,  # Single worker but with more connections
        limit_concurrency=100,  # Allow more concurrent connections
        limit_max_requests=1000,  # Allow more requests before restart
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