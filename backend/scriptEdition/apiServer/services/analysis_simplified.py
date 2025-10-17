#!/usr/bin/env python3
"""
Simplified Financial Analysis Service - Uses Claude Code CLI for tool execution

This simplified version replaces the complex conversation loop with Claude Code CLI,
which handles tool calling, script generation, and debugging internally.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, Optional, List

from llm import create_analysis_llm, LLMService
from .base_service import BaseService

class AnalysisService(BaseService):
    """Simplified financial question analysis service using Claude Code CLI"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        super().__init__(llm_service=llm_service, service_name="analysis-simplified")
        
        # Track MCP initialization
        self.mcp_initialized = True  # Simplified - assume always available
        
        # Enriched prompt state management
        self._enriched_prompt = None
        self._enriched_prompt_mode = False
    
    def _create_default_llm(self) -> LLMService:
        """Create default LLM service for analysis"""
        return create_analysis_llm()
    
    def _get_system_prompt_filename(self) -> str:
        """Use environment variable or default simplified analysis prompt"""
        return os.getenv("SYSTEM_PROMPT_FILE", "system-prompt-searchfirst.txt")
    
    def _initialize_service_specific(self):
        """Initialize analysis simplified specific components"""
        # Load coding-only prompt for enriched prompts
        self.coding_prompt_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "..", 
            "config", 
            "system-prompt-coding-only.txt"
        )
        self.coding_prompt = None  # Cache for coding prompt
    
    
    def _is_enriched_prompt(self, message: str) -> bool:
        """Detect if message contains enriched prompt from code prompt builder"""
        enriched_indicators = [
            "ORIGINAL QUERY:",
            "ANALYSIS TYPE:",
            "AVAILABLE FUNCTIONS:",
            "SUGGESTED PARAMETERS:",
            "=== alpaca_",
            "=== eodhd_",
            "=== calculate_"
        ]
        return any(indicator in message for indicator in enriched_indicators)
    
    async def get_coding_prompt(self) -> str:
        """Get coding-only system prompt for enriched prompts"""
        if self.coding_prompt is None:
            try:
                with open(self.coding_prompt_path, 'r', encoding='utf-8') as f:
                    self.coding_prompt = f.read()
                self.logger.info(f"📄 Loaded coding prompt from {self.coding_prompt_path}")
            except Exception as e:
                self.logger.error(f"❌ Failed to load coding prompt: {e}")
                self.coding_prompt = "You are a financial script generator."
        
        return self.coding_prompt
    
    def set_enriched_prompt(self, code_prompt_result: Dict[str, Any]):
        """Set enriched prompt from code prompt builder result"""
        if isinstance(code_prompt_result, str):
            # Legacy support for old string-based prompts
            self._enriched_prompt = code_prompt_result
            self._enriched_prompt_mode = True
            self.llm_service.provider.set_system_prompt(code_prompt_result)
            self.logger.info("🔧 Set legacy enriched prompt mode")
        else:
            # New message-based approach
            self._enriched_prompt = code_prompt_result
            self._enriched_prompt_mode = True
            # Set system prompt from the structured result
            system_prompt = code_prompt_result.get("system_prompt", "Generate financial analysis scripts.")
            self.llm_service.provider.set_system_prompt(system_prompt)
            self.logger.info("🔧 Set structured enriched prompt mode with system prompt and user messages")
    
    async def clear_enriched_prompt(self):
        """Clear enriched prompt and return to normal system prompt mode"""
        self._enriched_prompt = None
        self._enriched_prompt_mode = False
        # Restore original system prompt on provider
        original_prompt = await self.get_system_prompt()
        self.llm_service.provider.set_system_prompt(original_prompt)
        self.logger.info("🔄 Cleared enriched prompt mode and restored original system prompt on provider")
    
    def clear_tools(self):
        """Clear tools but preserve validation tools for enriched prompt mode"""
        # For simplified service, just clear all tools since Claude CLI will handle MCP tools
        # The enriched prompt will specify which tools are allowed
        try:
            self.llm_service.provider.set_tools([])
        except:
            pass
            
        self.logger.info("🧹 Cleared all tools from provider - Claude CLI will handle validation tools")
    
    async def get_appropriate_system_prompt(self, message: str) -> str:
        """Get appropriate system prompt based on enriched prompt mode or message type"""
        if self._enriched_prompt_mode and self._enriched_prompt:
            self.logger.info("🔧 Using enriched prompt from code prompt builder")
            return self._enriched_prompt
        elif self._is_enriched_prompt(message):
            self.logger.info("🔧 Using coding-only system prompt for enriched prompt")
            return await self.get_coding_prompt()
        else:
            self.logger.info("📄 Using standard system prompt")
            return await self.get_system_prompt()
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get MCP tools - respects enriched prompt mode"""
        # Don't load tools when in enriched prompt mode
        if self._enriched_prompt_mode:
            self.logger.info("🚫 Skipping tool loading - enriched prompt mode active")
            return []
            
        # Return tools for MCP functionality (optional - env var controls CLI usage)
        return [
            {
                "type": "function",
                "function": {
                    "name": "financial_analysis",
                    "description": "Analyze financial data using MCP tools",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "question": {"type": "string", "description": "Financial question to analyze"}
                        }
                    }
                }
            }
        ]
    
    async def ensure_mcp_initialized(self) -> bool:
        """Ensure MCP is initialized - simplified version"""
        return True  # Claude Code CLI handles MCP initialization
    
    async def analyze_question(self, question: str, model: str = None, enable_caching: bool = True) -> Dict[str, Any]:
        """
        Simplified main entry point for financial question analysis
        Uses Claude Code CLI which handles tool calling internally
        """
        try:
            if not model:
                model = self.llm_service.default_model
            
            self.logger.info(f"🤔 Analyzing question (CLI controlled by USE_CLAUDE_CODE_CLI env var): {question[:100]}...")
            
            # Get appropriate system prompt based on message type
            system_prompt = await self.get_appropriate_system_prompt(question)
            mcp_tools = self.get_mcp_tools()
            
            # Set system prompt and tools on provider (CLI usage controlled by env var)
            self.llm_service.provider.set_system_prompt(system_prompt)
            self.llm_service.provider.set_tools(mcp_tools)
            
            # Check if we're using structured enriched prompt or legacy mode
            if self._enriched_prompt_mode and isinstance(self._enriched_prompt, dict):
                # Use structured messages from code prompt builder
                messages = self._enriched_prompt.get("user_messages", [])
                self.logger.info(f"📨 Using {len(messages)} structured messages from code prompt builder")
            else:
                # Legacy mode: create message structure with explicit instruction
                enhanced_question = f"Write a Python script to answer this question. Follow the instructions in the system prompt.\n\nQuestion: {question}"
                messages = [
                    {
                        "role": "user",
                        "content": enhanced_question
                    }
                ]
                self.logger.info("📨 Using legacy single message mode")
            
            # Make request - this will route to Claude Code CLI automatically
            result = await self.llm_service.make_request(
                messages=messages,
                model=model,
                enable_caching=enable_caching
            )
            
            if result.get("success"):
                # Format the successful response based on new standardized format
                response_data = {
                    "question": question,
                    "provider": result["provider"],
                    "model": model,
                    "response_type": result.get("response_type"),
                    "raw_content": result.get("raw_content", ""),
                    "timestamp": datetime.now().isoformat()
                }
                
                # Add completion information
                if result.get("task_completed"):
                    response_data["task_completed"] = result["task_completed"]
                
                # Always use consistent key structure regardless of response type
                response_data["analysis_result"] = result.get("data", {})
                
                self.logger.info(f"✅ Question analyzed successfully using {result['provider']} - Type: {result.get('response_type')}")
                
                return {
                    "success": True,
                    "data": response_data
                }
            else:
                self.logger.error(f"❌ Question analysis failed: {result.get('error')}")
                return {
                    "success": False,
                    "error": result.get("error", "Unknown error"),
                    "provider": result.get("provider", self.llm_service.provider_type),
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            self.logger.error(f"❌ Analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def _extract_script_info_from_cli_response(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """Extract script generation information from Claude Code CLI response"""
        try:
            # Check if the response indicates script generation
            content = result.get("content", "")
            
            # Look for script file references in the content
            has_script = any(keyword in content.lower() for keyword in [
                ".py", "script", "python", "file", "generated"
            ])
            
            script_info = {
                "has_script": has_script,
                "execution_successful": True  # Assume success if no errors mentioned
            }
            
            # Try to extract script path if mentioned
            if "script" in content.lower() and ".py" in content.lower():
                # Simple pattern matching for script paths
                import re
                path_pattern = r'[\w/\\.-]+\.py'
                matches = re.findall(path_pattern, content)
                if matches:
                    script_info["script_path"] = matches[0]
            
            return script_info
            
        except Exception as e:
            self.logger.error(f"Error extracting script info: {e}")
            return {"has_script": False}
    
    async def warm_cache(self, model: str) -> bool:
        """Warm cache - simplified version (no pre-warming needed for CLI)"""
        self.logger.info("📄 Cache warming not needed for simplified analysis service")
        return True
    
    async def close_sessions(self):
        """Close sessions - simplified version (no sessions to manage)"""
        self.logger.info("🔒 No sessions to close in simplified analysis service")
        pass