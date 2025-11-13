#!/usr/bin/env python3
"""
Dialogue Factory - Creates dialogue system components with proper dependency injection
"""

# Import shared services
import sys
import os
shared_path = os.path.join(os.path.dirname(__file__), '..', '..', '..')
sys.path.insert(0, shared_path)
from shared.llm.service import LLMService
from ..search.library import AnalysisLibrary
from .context.service import create_context_service
from ...services.session_manager import SessionManager
from .context.classifier import create_query_classifier
from .context.expander import create_context_expander
from .search.context_aware import create_context_aware_search


class DialogueFactory:
    """Factory for creating dialogue system components with proper dependencies"""
    
    def __init__(self, llm_service: LLMService = None, analysis_library: AnalysisLibrary = None, 
                 chat_history_service = None, session_manager: SessionManager = None):
        self.analysis_library = analysis_library or AnalysisLibrary()
        self.chat_history_service = chat_history_service
        
        # Use provided session manager or create new one
        # Session manager should be created in server.py and passed here
        if session_manager:
            self.session_manager = session_manager
        else:
            # Fallback: create local instance if not provided
            # Note: This fallback skips Redis to avoid async complexity
            self.session_manager = SessionManager(
                chat_history_service=chat_history_service,
                redis_client=None
            )
        
        # Create context service - use passed LLM service or create context-optimized one
        if llm_service:
            context_llm = llm_service  # Reuse passed LLM service
        else:
            from shared.llm import create_context_llm
            context_llm = create_context_llm()  # Uses CONTEXT_LLM_PROVIDER or LLM_PROVIDER
        
        self.context_service = create_context_service(context_llm)
        
        # Create dialogue components with dependencies
        self.classifier = create_query_classifier(self.context_service)
        self.expander = create_context_expander(self.context_service)
        self.context_aware_search = create_context_aware_search(
            analysis_library=self.analysis_library,
            session_manager=self.session_manager,
            classifier=self.classifier,
            expander=self.expander,
            llm_service=context_llm
        )
    
    def get_context_aware_search(self):
        """Get the fully configured context-aware search"""
        return self.context_aware_search
    
    def get_session_manager(self):
        """Get the session manager"""
        return self.session_manager
    
    async def search_with_context(self, query: str, session_id: str = None, auto_expand: bool = True):
        """Convenience method for context-aware search"""
        return await self.context_aware_search.search_with_context(query, session_id, auto_expand)


# Global factory will be set by the main application
_dialogue_factory = None

def initialize_dialogue_factory(llm_service: LLMService = None, analysis_library: AnalysisLibrary = None, 
                               chat_history_service = None, session_manager: SessionManager = None):
    """Initialize global dialogue factory with dependencies
    
    Args:
        llm_service: LLM service for context expansion
        analysis_library: Semantic search library for analysis lookup
        chat_history_service: ChatHistoryService for persistence
        session_manager: SessionManager instance (should be created in server.py)
    """
    global _dialogue_factory
    _dialogue_factory = DialogueFactory(llm_service, analysis_library, chat_history_service, session_manager)
    return _dialogue_factory

def get_dialogue_factory() -> DialogueFactory:
    """Get the initialized dialogue factory"""
    if _dialogue_factory is None:
        raise RuntimeError("Dialogue factory not initialized. Call initialize_dialogue_factory() first.")
    return _dialogue_factory

# Convenience functions that use the global factory
async def search_with_context(query: str, session_id: str = None, auto_expand: bool = True):
    """Context-aware search using global factory"""
    factory = get_dialogue_factory()
    return await factory.search_with_context(query, session_id, auto_expand)

def get_session_manager():
    """Get session manager using global factory"""
    factory = get_dialogue_factory()
    return factory.get_session_manager()