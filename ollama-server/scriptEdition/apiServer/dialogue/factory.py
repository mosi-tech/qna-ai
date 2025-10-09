#!/usr/bin/env python3
"""
Dialogue Factory - Creates dialogue system components with proper dependency injection
"""

from llm.service import LLMService
from search.library import AnalysisLibrary
from .context.service import create_context_service
from .conversation.session_manager import session_manager
from .context.classifier import create_query_classifier
from .context.expander import create_context_expander
from .search.context_aware import create_context_aware_search


class DialogueFactory:
    """Factory for creating dialogue system components with proper dependencies"""
    
    def __init__(self, llm_service: LLMService = None, analysis_library: AnalysisLibrary = None):
        self.analysis_library = analysis_library or AnalysisLibrary()
        
        # Create context service - use passed LLM service or create context-optimized one
        if llm_service:
            context_llm = llm_service  # Reuse passed LLM service
        else:
            from llm import create_context_llm
            context_llm = create_context_llm()  # Uses CONTEXT_LLM_PROVIDER or LLM_PROVIDER
        
        self.context_service = create_context_service(context_llm)
        
        # Create dialogue components with dependencies
        self.classifier = create_query_classifier(self.context_service)
        self.expander = create_context_expander(self.context_service, self.classifier)
        self.context_aware_search = create_context_aware_search(
            analysis_library=self.analysis_library,
            session_manager=session_manager,
            classifier=self.classifier,
            expander=self.expander
        )
    
    def get_context_aware_search(self):
        """Get the fully configured context-aware search"""
        return self.context_aware_search
    
    def get_session_manager(self):
        """Get the session manager"""
        return session_manager
    
    async def search_with_context(self, query: str, session_id: str = None, auto_expand: bool = True):
        """Convenience method for context-aware search"""
        return await self.context_aware_search.search_with_context(query, session_id, auto_expand)


# Global factory will be set by the main application
_dialogue_factory = None

def initialize_dialogue_factory(llm_service: LLMService = None, analysis_library: AnalysisLibrary = None):
    """Initialize global dialogue factory with dependencies"""
    global _dialogue_factory
    _dialogue_factory = DialogueFactory(llm_service, analysis_library)
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