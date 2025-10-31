#!/usr/bin/env python3
"""
Base Service Class

Provides standardized initialization for all service classes including:
- LLM service creation and management
- System prompt loading
- MCP tools configuration
- Logging setup
"""

import logging
import os
from abc import ABC, abstractmethod
from typing import Optional

from ..llm import LLMService

class BaseService(ABC):
    """Base class for all services with standardized initialization"""
    
    def __init__(self, llm_service: Optional[LLMService] = None, service_name: str = None):
        """
        Initialize base service with standardized components
        
        Args:
            llm_service: Optional LLM service instance
            service_name: Name of the service for logging and config
        """
        # Set service name for logging and config
        self.service_name = service_name or self.__class__.__name__.replace('Service', '').lower()
        
        # Initialize logger
        self.logger = logging.getLogger(self.service_name)
        
        # Create or use provided LLM service
        self.llm_service = llm_service or self._create_default_llm()
        
        # Load system prompt configuration
        self._load_system_prompt_config()
        
        # Initialize service-specific components
        self._initialize_service_specific()
        
        self.logger.info(f"🤖 Initialized {self.service_name} service with {self.llm_service.provider_type}")
    
    @abstractmethod
    def _create_default_llm(self) -> LLMService:
        """Create default LLM service for this service type - must be implemented by subclasses"""
        pass
    
    def _initialize_service_specific(self):
        """Override this method to add service-specific initialization"""
        pass
    
    def _load_system_prompt_config(self):
        """Load system prompt configuration with standardized path resolution"""
        # Allow service-specific prompt file override
        prompt_filename = self._get_system_prompt_filename()
        
        # Point to apiServer config directory from shared location
        self.system_prompt_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "..", "..", 
            "scriptEdition", "apiServer", "config", 
            prompt_filename
        )
        
        # Cache for system prompt
        self.system_prompt = None
        self.logger.info(f"📝 Using system prompt file: {prompt_filename}")
    
    def _get_system_prompt_filename(self) -> str:
        """
        Get system prompt filename for this service
        Override this method to customize the prompt file name
        """
        # Default pattern: system-prompt-{service_name}.txt
        return f"system-prompt-{self.service_name.replace('_', '-')}.txt"
    
    
    async def load_system_prompt(self) -> str:
        """Load the base system prompt from file"""
        try:
            self.logger.debug(f"Loading system prompt from: {self.system_prompt_path}")
            with open(self.system_prompt_path, 'r') as f:
                content = f.read().strip()
                self.logger.debug(f"System prompt loaded successfully ({len(content)} characters)")
                return content
        except Exception as e:
            self.logger.error(f"Failed to load system prompt from {self.system_prompt_path}: {e}")
            return self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt if file loading fails - override in subclasses"""
        return f"You are a helpful {self.service_name} assistant."
    
    async def get_system_prompt(self) -> str:
        """Get system prompt (cached)"""
        if self.system_prompt:
            return self.system_prompt
            
        self.system_prompt = await self.load_system_prompt()
        return self.system_prompt
    
    async def close_sessions(self):
        """Cleanup method for service shutdown - override in subclasses if needed"""
        self.logger.info(f"Closing {self.service_name} service sessions...")
        # Base cleanup logic can go here
        self.logger.info(f"Cleaned up {self.service_name} service")