"""
FastAPI Server Setup and Configuration
"""

import logging
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from api.models import QuestionRequest, AnalysisResponse
from services.analysis import AnalysisService
from services.search import SearchService
from api.routes import APIRoutes

logger = logging.getLogger("api-server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🚀 Starting Financial Analysis Server...")
    
    # Initialize services
    analysis_service = AnalysisService()
    search_service = SearchService()
    app.state.analysis_service = analysis_service
    app.state.search_service = search_service
    
    # Initialize API routes with dependency injection
    api_routes = APIRoutes(analysis_service, search_service)
    app.state.api_routes = api_routes
    
    # Warm cache if provider supports it
    if analysis_service.cache_manager:
        logger.info("🔥 Warming cache...")
        try:
            await analysis_service.ensure_mcp_initialized()
            cache_success = await analysis_service.warm_cache(analysis_service.llm_service.default_model)
            if cache_success:
                logger.info("✅ Cache warming completed successfully")
            else:
                logger.warning("⚠️ Cache warming failed, continuing without cache")
        except Exception as e:
            logger.warning(f"⚠️ Cache warming error: {e}")
    
    logger.info(f"✅ Server ready with {analysis_service.llm_service.provider_type.upper()} provider")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Financial Analysis Server...")
    await analysis_service.close_sessions()
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
    
    # API Routes
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
    
    @app.get("/conversation/{session_id}/context")
    async def get_session_context(session_id: str):
        """Get conversation context for debugging"""
        return await app.state.api_routes.get_session_context(session_id)
    
    @app.get("/conversation/sessions")
    async def list_sessions():
        """List active conversation sessions"""
        return await app.state.api_routes.list_sessions()
    
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