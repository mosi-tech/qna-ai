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
from llm.cache import ProviderCacheManager

logger = logging.getLogger("analysis-service-simplified")

class AnalysisService:
    """Simplified financial question analysis service using Claude Code CLI"""
    
    def __init__(self, llm_service: Optional[LLMService] = None):
        # Use provided LLM service or create default analysis LLM
        self.llm_service = llm_service or create_analysis_llm()
        
        # Load QnA-specific system prompt
        self._load_system_prompt_config()
        
        # Initialize cache manager
        self.cache_manager = ProviderCacheManager(self.llm_service.provider, enable_caching=True)
        
        # Track MCP initialization
        self.mcp_initialized = True  # Simplified - assume always available
        
        logger.info(f"🤖 Initialized Simplified Analysis service with {self.llm_service.provider_type}")
    
    def _load_system_prompt_config(self):
        """Load system prompt configuration for QnA analysis"""
        prompt_filename = os.getenv("SYSTEM_PROMPT_FILE", "system-prompt-searchfirst.txt")
        self.system_prompt_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "..", 
            "config", 
            prompt_filename
        )
        self.system_prompt = None  # Cache for system prompt
    
    async def get_system_prompt(self) -> str:
        """Get system prompt content"""
        if self.system_prompt is None:
            try:
                with open(self.system_prompt_path, 'r', encoding='utf-8') as f:
                    self.system_prompt = f.read()
                logger.info(f"📄 Loaded system prompt from {self.system_prompt_path}")
            except Exception as e:
                logger.error(f"❌ Failed to load system prompt: {e}")
                self.system_prompt = "You are a financial analysis assistant."
        
        return self.system_prompt
    
    def get_mcp_tools(self) -> List[Dict[str, Any]]:
        """Get MCP tools - optional since CLI usage is controlled by environment variable"""
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
            
            logger.info(f"🤔 Analyzing question (CLI controlled by USE_CLAUDE_CODE_CLI env var): {question[:100]}...")
            
            # Get system prompt and set up provider
            system_prompt = await self.get_system_prompt()
            mcp_tools = self.get_mcp_tools()
            
            # Set system prompt and tools on provider (CLI usage controlled by env var)
            self.llm_service.provider.set_system_prompt(system_prompt)
            self.llm_service.provider.set_tools(mcp_tools)
            
            # Create simple message structure
            messages = [
                {
                    "role": "user",
                    "content": question
                }
            ]
            
            # Make request - this will route to Claude Code CLI automatically
            result = await self.llm_service.make_request(
                messages=messages,
                model=model,
                enable_caching=enable_caching
            )
            
            if result["success"]:
                # Extract Claude Code CLI result
                response_content = result.get("content", "")
                
                # Check if this is a Claude Code CLI response
                provider_name = result.get("provider", "")
                is_cli_response = "cli" in provider_name.lower()
                
                # Format response based on type
                if is_cli_response:
                    logger.info("✅ Question analyzed successfully using Claude Code CLI")
                    
                    # Extract script information if available (Claude Code CLI generates scripts)
                    script_info = self._extract_script_info_from_cli_response(result)
                    
                    return {
                        "success": True,
                        "data": {
                            "question": question,
                            "provider": result["provider"],
                            "model": model,
                            "response_type": "claude_code_analysis",
                            "analysis_result": {
                                "content": response_content,
                                "script_generated": script_info["has_script"],
                                "script_path": script_info.get("script_path"),
                                "execution_successful": script_info.get("execution_successful", False)
                            }
                        },
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    # Regular API response
                    logger.info("✅ Question analyzed successfully using regular API")
                    return {
                        "success": True,
                        "data": {
                            "question": question,
                            "provider": result["provider"],
                            "model": model,
                            "response_type": "api_response",
                            "analysis_result": {
                                "content": response_content
                            }
                        },
                        "timestamp": datetime.now().isoformat()
                    }
            else:
                logger.error(f"❌ Question analysis failed: {result.get('error')}")
                return {
                    "success": False,
                    "data": {
                        "question": question,
                        "error": result.get("error", "Unknown error"),
                        "provider": result.get("provider", self.llm_service.provider_type),
                        "timestamp": datetime.now().isoformat()
                    }
                }
                
        except Exception as e:
            logger.error(f"❌ Analysis error: {e}")
            return {
                "success": False,
                "data": {
                    "question": question,
                    "error": str(e),
                    "provider": self.llm_service.provider_type,
                    "timestamp": datetime.now().isoformat()
                }
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
            logger.error(f"Error extracting script info: {e}")
            return {"has_script": False}
    
    async def warm_cache(self, model: str) -> bool:
        """Warm cache - simplified version (no pre-warming needed for CLI)"""
        logger.info("📄 Cache warming not needed for simplified analysis service")
        return True
    
    async def close_sessions(self):
        """Close sessions - simplified version (no sessions to manage)"""
        logger.info("🔒 No sessions to close in simplified analysis service")
        pass