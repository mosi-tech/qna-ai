#!/usr/bin/env python3
"""
Message Formatter - Provider-specific message formatting for LLM conversations
Handles conversion of generic messages to provider-specific formats
"""

import logging
import os
from typing import Dict, List, Any, Optional
from enum import Enum

logger = logging.getLogger(__name__)


class ProviderType(Enum):
    """Supported LLM providers"""
    ANTHROPIC = "anthropic"
    OPENAI = "openai"
    OLLAMA = "ollama"


class MessageFormatter:
    """Format messages based on LLM provider requirements"""
    
    def __init__(self, provider_type: str):
        """Initialize formatter for specific provider"""
        self.provider_type = provider_type.lower()
        if self.provider_type == "anthropic":
            self.formatter = AnthropicMessageFormatter()
        elif self.provider_type == "openai":
            self.formatter = OpenAIMessageFormatter()
        elif self.provider_type == "ollama":
            self.formatter = OllamaMessageFormatter()
        else:
            raise ValueError(f"Unsupported provider: {provider_type}")
    
    def build_conversation(self, 
                          user_query: str, 
                          function_schemas: Dict[str, str], enable_caching: bool) -> Dict[str, Any]:
        """
        Build a conversation mode for script generation
        
        Args:
            user_query: The user's question/request
            function_schemas: Dict of function_name -> schema_documentation
            
        Returns:
            Dict with 'messages', 'system_prompt', etc. formatted for provider
        """
        return self.formatter.build_conversation(user_query, function_schemas, enable_caching)
    
    def build_system_prompt(self,
                           user_query: str,
                           function_schemas: Dict[str, str]) -> Dict[str, Any]:
        """
        Build system prompt mode messages for script generation
        
        Args:
            user_query: The user's question/request
            function_schemas: Dict of function_name -> schema_documentation
            
        Returns:
            Dict with provider-specific system prompt mode formatted messages
        """
        return self.formatter.build_system_prompt(user_query, function_schemas)
    
    def build_tool_simulation(self,
                            user_query: str,
                            function_schemas: Dict[str, str]) -> Dict[str, Any]:
        """
        Build tool simulation messages for script generation
        
        Args:
            user_query: The user's question/request
            function_schemas: Dict of function_name -> schema_documentation
            
        Returns:
            Dict with provider-specific simulated tool call messages
        """
        return self.formatter.build_tool_simulation(user_query, function_schemas)
    
    def format_assistant_response_with_tool_use(self,
                                                text: str,
                                                tool_name: str,
                                                tool_input: Dict[str, Any],
                                                tool_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Format an assistant response that includes a tool call
        
        Args:
            text: The assistant's text response
            tool_name: Name of the tool to call
            tool_input: Input parameters for the tool
            tool_id: Optional tool call ID
            
        Returns:
            Formatted message dict
        """
        return self.formatter.format_assistant_response_with_tool_use(text, tool_name, tool_input, tool_id)
    
    def create_verification_message(self, original_question: str, verification_prompt_template: str = "") -> Dict[str, Any]:
        """
        Create a verification message asking if the generated script answers the question
        
        Args:
            original_question: The original question that the script should answer
            verification_prompt_template: The verification prompt template from AnalysisService
            
        Returns:
            Formatted user message dict for verification
        """
        return self.formatter.create_verification_message(original_question, verification_prompt_template)


class BaseMessageFormatter:
    """Base message formatter interface"""
    
    def __init__(self):
        """Initialize base formatter"""
        pass
    
    def build_conversation(self, 
                          user_query: str, 
                          function_schemas: Dict[str, str], enable_caching: bool = False) -> Dict[str, Any]:
        raise NotImplementedError
    
    def build_system_prompt(self,
                           user_query: str,
                           function_schemas: Dict[str, str]) -> Dict[str, Any]:
        raise NotImplementedError
    
    def build_tool_simulation(self,
                            user_query: str,
                            function_schemas: Dict[str, str]) -> Dict[str, Any]:
        raise NotImplementedError
    
    def format_assistant_response_with_tool_use(self,
                                                text: str,
                                                tool_name: str,
                                                tool_input: Dict[str, Any],
                                                tool_id: Optional[str] = None) -> Dict[str, Any]:
        raise NotImplementedError
    
    def create_verification_message(self, original_question: str, verification_prompt_template: str = "") -> Dict[str, Any]:
        """Create a user message asking for verification that script answers the question"""
        raise NotImplementedError


class AnthropicMessageFormatter(BaseMessageFormatter):
    """Format messages for Anthropic Claude API"""
    
    def build_conversation(self, 
                          user_query: str, 
                          function_schemas: Dict[str, str], 
                          enable_caching: bool = False) -> Dict[str, Any]:
        """Build conversation in Anthropic format"""
        return self._build_conversation_mode(user_query, function_schemas, enable_caching)
    
    def _build_conversation_mode(self, user_query: str, function_schemas: Dict[str, str], enable_caching: bool) -> Dict[str, Any]:
        """Build multi-turn conversation with function documentation"""
        messages = []
        
        # query_message = f"Write a Python script to answer this question: {user_query}"
        # messages.append({
        #     "role": "user", 
        #     "content": [{"type": "text", "text": query_message}]
        # })
        
        assistant_response = f"""I'll analyze this question and identify the required functions. For this analysis, I need to use the following MCP functions:

{chr(10).join([f"- {func_name}" for func_name in function_schemas.keys()])}

Let me get the documentation for these functions one by one."""
        
        messages.append({
            "role": "assistant", 
            "content": [{"type": "text", "text": assistant_response}]
        })
        
        for i, (func_name, schema) in enumerate(function_schemas.items(), 1):
            assistant_request = f"Can you provide the documentation for the `{func_name}` function?"
            messages.append({
                "role": "assistant", 
                "content": [{"type": "text", "text": assistant_request}]
            })
            
            documentation_content = f"""Here is the documentation for `{func_name}`:

```
{schema}
```"""
            messages.append({
                "role": "user", 
                "content": [{"type": "text", "text": documentation_content}]
            })
        
        final_assistant_message = "Perfect! Now I have all the function documentation I need. I'll write the Python script using these functions."
        messages.append({
            "role": "assistant", 
            "content": [{"type": "text", "text": final_assistant_message}]
        })

        if enable_caching:
            messages[-1]["content"][0]["cache_control"] = {
                "type": "ephemeral",
                "ttl": "5m"
            }
        
        return {
            "mode": "conversation",
            "messages": messages,
            "message_count": len(messages)
        }
    
    def build_system_prompt(self, user_query: str, function_schemas: Dict[str, str]) -> Dict[str, Any]:
        """Build system prompt mode with all function docs in system prompt"""
        messages = []
        
        function_docs = []
        for func_name, schema in function_schemas.items():
            function_docs.append(f"## {func_name}")
            function_docs.append(schema)
            function_docs.append("")
        
        enhanced_system_prompt = f"""## Available MCP Functions

The following functions are available for your analysis:

{chr(10).join(function_docs)}

## Instructions

When writing the Python script:
1. Use only the functions documented above
2. Call functions using call_mcp_function()
3. Follow the parameter specifications exactly
4. Handle errors appropriately
5. Return structured results as JSON"""

        query_message = f"Write a Python script to answer this question: {user_query}"
        messages.append({
            "role": "user", 
            "content": [{"type": "text", "text": query_message}]
        })
        
        return {
            "mode": "system_prompt",
            "messages": messages,
            "system_prompt_extension": enhanced_system_prompt,
            "message_count": len(messages)
        }
    
    def build_tool_simulation(self,
                            user_query: str,
                            function_schemas: Dict[str, str]) -> Dict[str, Any]:
        """Build tool simulation messages with simulated MCP function calls for Anthropic"""
        import json
        
        messages = []
        
        query_message = f"Write a Python script to answer this question: {user_query}"
        messages.append({
            "role": "user",
            "content": [{"type": "text", "text": query_message}]
        })
        
        tool_calls = []
        call_ids = {}
        for func_name in function_schemas.keys():
            arguments = {"function_name": func_name}
            call_id = f"call_{func_name}"
            
            tool_call = {
                "type": "tool_use",
                "id": call_id,
                "name": "get_function_docstring",
                "input": arguments
            }
            tool_calls.append(tool_call)
            call_ids[func_name] = call_id
        
        assistant_message = {
            "role": "assistant",
            "content": [
                {"type": "text", "text": "I need to get documentation for the required functions first."},
                *tool_calls
            ]
        }
        messages.append(assistant_message)
        
        for func_name, schema in function_schemas.items():
            structured_result = {
                "success": True,
                "function_name": func_name,
                "original_name": func_name,
                "docstring": schema,
                "signature": f"{func_name}(**kwargs)",
                "module": "mcp_functions"
            }
            
            tool_result = {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": call_ids[func_name],
                        "content": json.dumps(structured_result, indent=2)
                    }
                ]
            }
            messages.append(tool_result)
        
        return {
            "mode": "tool_simulation",
            "messages": messages,
            "message_count": len(messages)
        }
    
    def format_assistant_response_with_tool_use(self,
                                                text: str,
                                                tool_name: str,
                                                tool_input: Dict[str, Any],
                                                tool_id: Optional[str] = None) -> Dict[str, Any]:
        """Format assistant message with Anthropic tool_use format"""
        
        import hashlib
        if not tool_id:
            hash_input = f"{tool_name}{str(tool_input)}"
            hash_val = hashlib.md5(hash_input.encode()).hexdigest()[:12]
            tool_id = f"toolu_{hash_val}_0"
        
        content = []
        
        if text:
            content.append({
                "type": "text",
                "text": text
            })
        
        content.append({
            "type": "tool_use",
            "id": tool_id,
            "name": tool_name,
            "input": tool_input
        })
        
        return {
            "role": "assistant",
            "content": content
        }
    
    def create_verification_message(self, original_question: str, verification_prompt_template: str = "") -> Dict[str, Any]:
        """Create a verification message for Anthropic format"""
        if not verification_prompt_template:
            verification_prompt_template = "Before we proceed, I need to verify something important:\n\n**Question**: {question}\n\nPlease check if the script correctly answers the question."
        
        verification_text = verification_prompt_template.format(question=original_question)
        
        return {
            "role": "user",
            "content": [{"type": "text", "text": verification_text}]
        }


class OpenAIMessageFormatter(BaseMessageFormatter):
    """Format messages for OpenAI API"""
    
    def build_conversation(self, 
                          user_query: str, 
                          function_schemas: Dict[str, str], enable_caching: bool = False) -> Dict[str, Any]:
        """Build conversation in OpenAI format with function documentation exchange"""
        messages = []
        
        # Start with assistant explaining what it will do
        assistant_response = f"""I'll analyze this question and identify the required functions. For this analysis, I need to use the following MCP functions:

{chr(10).join([f"- {func_name}" for func_name in function_schemas.keys()])}

Let me get the documentation for these functions one by one."""
        
        messages.append({
            "role": "assistant", 
            "content": assistant_response
        })
        
        # Exchange documentation for each function
        for i, (func_name, schema) in enumerate(function_schemas.items(), 1):
            assistant_request = f"Can you provide the documentation for the `{func_name}` function?"
            messages.append({
                "role": "assistant", 
                "content": assistant_request
            })
            
            documentation_content = f"""Here is the documentation for `{func_name}`:

```
{schema}
```"""
            messages.append({
                "role": "user", 
                "content": documentation_content
            })
        
        final_assistant_message = "Perfect! Now I have all the function documentation I need. I'll write the Python script using these functions."
        messages.append({
            "role": "assistant", 
            "content": final_assistant_message
        })
        
        return {
            "mode": "conversation",
            "messages": messages,
            "message_count": len(messages)
        }
    
    def build_system_prompt(self,
                           user_query: str,
                           function_schemas: Dict[str, str]) -> Dict[str, Any]:
        """Build system prompt mode for OpenAI with function docs in system message"""
        messages = []
        
        # Build function documentation
        function_docs = []
        for func_name, schema in function_schemas.items():
            function_docs.append(f"## {func_name}")
            function_docs.append(schema)
            function_docs.append("")
        
        enhanced_system_prompt = f"""## Available MCP Functions

The following functions are available for your analysis:

{chr(10).join(function_docs)}

## Instructions

When writing the Python script:
1. Use only the functions documented above
2. Call functions using call_mcp_function()
3. Follow the parameter specifications exactly
4. Handle errors appropriately
5. Return structured results as JSON"""

        # Add system message first
        messages.append({
            "role": "system",
            "content": enhanced_system_prompt
        })
        
        query_message = f"Write a Python script to answer this question: {user_query}"
        messages.append({
            "role": "user", 
            "content": query_message
        })
        
        return {
            "mode": "system_prompt",
            "messages": messages,
            "system_prompt_extension": enhanced_system_prompt,
            "message_count": len(messages)
        }
    
    def build_tool_simulation(self,
                            user_query: str,
                            function_schemas: Dict[str, str]) -> Dict[str, Any]:
        """Build tool simulation messages with simulated function calls for OpenAI"""
        import json
        
        messages = []
        
        query_message = f"Write a Python script to answer this question: {user_query}"
        messages.append({
            "role": "user",
            "content": query_message
        })
        
        # Build tool calls for function documentation
        tool_calls = []
        call_ids = {}
        for func_name in function_schemas.keys():
            arguments = {"function_name": func_name}
            call_id = f"call_{func_name}"
            
            tool_call = {
                "id": call_id,
                "type": "function",
                "function": {
                    "name": "get_function_docstring",
                    "arguments": json.dumps(arguments)
                }
            }
            tool_calls.append(tool_call)
            call_ids[func_name] = call_id
        
        assistant_message = {
            "role": "assistant",
            "content": "I need to get documentation for the required functions first.",
            "tool_calls": tool_calls
        }
        messages.append(assistant_message)
        
        # Add tool results
        for func_name, schema in function_schemas.items():
            structured_result = {
                "success": True,
                "function_name": func_name,
                "original_name": func_name,
                "docstring": schema,
                "signature": f"{func_name}(**kwargs)",
                "module": "mcp_functions"
            }
            
            tool_result = {
                "role": "tool",
                "tool_call_id": call_ids[func_name],
                "content": json.dumps(structured_result, indent=2)
            }
            messages.append(tool_result)
        
        return {
            "mode": "tool_simulation",
            "messages": messages,
            "message_count": len(messages)
        }
    
    def format_assistant_response_with_tool_use(self,
                                                text: str,
                                                tool_name: str,
                                                tool_input: Dict[str, Any],
                                                tool_id: Optional[str] = None) -> Dict[str, Any]:
        """Format assistant message with OpenAI tool_calls format"""
        import json
        import uuid
        
        if not tool_id:
            tool_id = f"call_{str(uuid.uuid4())[:8]}"
        
        content = text if text else ""
        
        return {
            "role": "assistant",
            "content": content,
            "tool_calls": [
                {
                    "id": tool_id,
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": json.dumps(tool_input)
                    }
                }
            ]
        }
    
    def create_verification_message(self, original_question: str, verification_prompt_template: str = "") -> Dict[str, Any]:
        """Create a verification message for OpenAI format"""
        if not verification_prompt_template:
            verification_prompt_template = "Before we proceed, I need to verify something important:\n\n**Question**: {question}\n\nPlease check if the script correctly answers the question."
        
        verification_text = verification_prompt_template.format(question=original_question)
        
        return {
            "role": "user",
            "content": verification_text
        }


class OllamaMessageFormatter(BaseMessageFormatter):
    """Format messages for Ollama API (OpenAI-compatible)"""
    
    def build_conversation(self, 
                          user_query: str, 
                          function_schemas: Dict[str, str], 
                          enable_caching: bool = False) -> Dict[str, Any]:
        """Build conversation in Ollama format with function documentation exchange"""
        messages = []
        
        # Start with assistant explaining what it will do
        assistant_response = f"""I'll analyze this question and identify the required functions. For this analysis, I need to use the following MCP functions:

{chr(10).join([f"- {func_name}" for func_name in function_schemas.keys()])}

Let me get the documentation for these functions one by one."""
        
        messages.append({
            "role": "assistant", 
            "content": assistant_response
        })
        
        # Exchange documentation for each function
        for i, (func_name, schema) in enumerate(function_schemas.items(), 1):
            assistant_request = f"Can you provide the documentation for the `{func_name}` function?"
            messages.append({
                "role": "assistant", 
                "content": assistant_request
            })
            
            documentation_content = f"""Here is the documentation for `{func_name}`:

```
{schema}
```"""
            messages.append({
                "role": "user", 
                "content": documentation_content
            })
        
        final_assistant_message = "Perfect! Now I have all the function documentation I need. I'll write the Python script using these functions."
        messages.append({
            "role": "assistant", 
            "content": final_assistant_message
        })
        
        return {
            "mode": "conversation",
            "messages": messages,
            "message_count": len(messages)
        }
    
    def build_system_prompt(self,
                           user_query: str,
                           function_schemas: Dict[str, str]) -> Dict[str, Any]:
        """Build system prompt mode for Ollama with function docs in system message"""
        messages = []
        
        # Build function documentation
        function_docs = []
        for func_name, schema in function_schemas.items():
            function_docs.append(f"## {func_name}")
            function_docs.append(schema)
            function_docs.append("")
        
        enhanced_system_prompt = f"""## Available MCP Functions

The following functions are available for your analysis:

{chr(10).join(function_docs)}

## Instructions

When writing the Python script:
1. Use only the functions documented above
2. Call functions using call_mcp_function()
3. Follow the parameter specifications exactly
4. Handle errors appropriately
5. Return structured results as JSON"""

        # Add system message first (Ollama supports system messages)
        messages.append({
            "role": "system",
            "content": enhanced_system_prompt
        })
        
        query_message = f"Write a Python script to answer this question: {user_query}"
        messages.append({
            "role": "user", 
            "content": query_message
        })
        
        return {
            "mode": "system_prompt",
            "messages": messages,
            "system_prompt_extension": enhanced_system_prompt,
            "message_count": len(messages)
        }
    
    def build_tool_simulation(self,
                            user_query: str,
                            function_schemas: Dict[str, str]) -> Dict[str, Any]:
        """Build tool simulation messages with simulated function calls for Ollama"""
        import json
        
        messages = []
        
        query_message = f"Write a Python script to answer this question: {user_query}"
        messages.append({
            "role": "user",
            "content": query_message
        })
        
        # Build tool calls for function documentation (OpenAI-compatible format)
        tool_calls = []
        call_ids = {}
        for func_name in function_schemas.keys():
            arguments = {"function_name": func_name}
            call_id = f"call_{func_name}"
            
            tool_call = {
                "id": call_id,
                "type": "function",
                "function": {
                    "name": "get_function_docstring",
                    "arguments": json.dumps(arguments)
                }
            }
            tool_calls.append(tool_call)
            call_ids[func_name] = call_id
        
        assistant_message = {
            "role": "assistant",
            "content": "I need to get documentation for the required functions first.",
            "tool_calls": tool_calls
        }
        messages.append(assistant_message)
        
        # Add tool results
        for func_name, schema in function_schemas.items():
            structured_result = {
                "success": True,
                "function_name": func_name,
                "original_name": func_name,
                "docstring": schema,
                "signature": f"{func_name}(**kwargs)",
                "module": "mcp_functions"
            }
            
            tool_result = {
                "role": "tool",
                "tool_call_id": call_ids[func_name],
                "content": json.dumps(structured_result, indent=2)
            }
            messages.append(tool_result)
        
        return {
            "mode": "tool_simulation",
            "messages": messages,
            "message_count": len(messages)
        }
    
    def format_assistant_response_with_tool_use(self,
                                                text: str,
                                                tool_name: str,
                                                tool_input: Dict[str, Any],
                                                tool_id: Optional[str] = None) -> Dict[str, Any]:
        """Format assistant message with tool calls for Ollama (OpenAI-compatible)"""
        import json
        import uuid
        
        if not tool_id:
            tool_id = f"call_{str(uuid.uuid4())[:8]}"
        
        content = text if text else ""
        
        return {
            "role": "assistant",
            "content": content,
            "tool_calls": [
                {
                    "id": tool_id,
                    "type": "function",
                    "function": {
                        "name": tool_name,
                        "arguments": json.dumps(tool_input)
                    }
                }
            ]
        }
    
    def create_verification_message(self, original_question: str, verification_prompt_template: str = "") -> Dict[str, Any]:
        """Create a verification message for Ollama format"""
        if not verification_prompt_template:
            verification_prompt_template = "Before we proceed, I need to verify something important:\n\n**Question**: {question}\n\nPlease check if the script correctly answers the question."
        
        verification_text = verification_prompt_template.format(question=original_question)
        
        return {
            "role": "user",
            "content": verification_text
        }


__all__ = ["MessageFormatter", "ProviderType", "AnthropicMessageFormatter", "OpenAIMessageFormatter", "OllamaMessageFormatter"]
