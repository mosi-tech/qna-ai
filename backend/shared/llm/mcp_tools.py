#!/usr/bin/env python3
"""
Simplified MCP Tools Management
"""

import json
import logging
import os
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from  ..integrations.mcp.mcp_client import mcp_client, initialize_mcp_client

logger = logging.getLogger("mcp-tools")

@dataclass
class MCPToolsConfig:
    """Configuration for MCP tools loading"""
    enabled: bool = True
    servers: List[str] = None
    exclude_tools: List[str] = None
    cache_enabled: bool = False  # Default false
    cache_ttl: str = "short"     # Default short
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPToolsConfig':
        """Create config from dictionary"""
        return cls(
            enabled=data.get("enabled", True),
            servers=data.get("servers", []),
            exclude_tools=data.get("exclude_tools", []),
            cache_enabled=data.get("cache_enabled", False),
            cache_ttl=data.get("cache_ttl", "short")
        )

class SimplifiedMCPLoader:
    """Simplified MCP tools loader"""
    
    def __init__(self):
        self._mcp_initialized = {}  # Per-config initialization
    
    async def load_tools_for_service(self, service_name: str) -> List[Dict[str, Any]]:
        """Load MCP tools for a specific service"""
        
        # Load consolidated config file
        config_path = self._get_config_path("mcp-tools.json")
        if not os.path.exists(config_path):
            logger.error(f"❌ MCP config not found: {config_path}")
            return []
        
        with open(config_path, 'r') as f:
            config_data = json.load(f)
        
        # Get service-specific config
        service_configs = config_data.get("serviceConfigs", {})
        service_config_data = service_configs.get(service_name)
        
        if not service_config_data:
            logger.info(f"⚠️ No config for service '{service_name}', using default")
            service_config_data = config_data.get("defaultConfig", {})
        
        tools_config = MCPToolsConfig.from_dict(service_config_data)
        
        # Check if tools are disabled
        if not tools_config.enabled:
            logger.info(f"🚫 MCP tools disabled for service '{service_name}'")
            return []
        
        # Initialize MCP if needed
        config_key = f"service-{service_name}"
        if config_key not in self._mcp_initialized:
            await self._initialize_mcp_for_config(config_key, config_data)
        
        # Load tools with service-specific filtering
        return await self._load_tools_with_filtering(tools_config)
    
    def get_filtered_mcp_config(self, service_name: str) -> Optional[Dict[str, Any]]:
        """Get filtered MCP config for a specific service (for Claude Code CLI)"""
        config_path = self._get_config_path("mcp-tools.json")
        if not os.path.exists(config_path):
            logger.error(f"❌ MCP config not found: {config_path}")
            return None
        
        try:
            with open(config_path, 'r') as f:
                config_data = json.load(f)
            
            # Get service-specific config
            service_configs = config_data.get("serviceConfigs", {})
            service_config_data = service_configs.get(service_name)
            
            if not service_config_data:
                logger.info(f"⚠️ No config for service '{service_name}', using default")
                service_config_data = config_data.get("defaultConfig", {})
            
            tools_config = MCPToolsConfig.from_dict(service_config_data)
            
            # Create filtered config with only needed servers
            all_mcp_servers = config_data.get("mcpServers", {})
            allowed_servers = tools_config.servers or list(all_mcp_servers.keys())
            
            filtered_servers = {
                server_name: all_mcp_servers[server_name]
                for server_name in allowed_servers
                if server_name in all_mcp_servers
            }
            
            # Return filtered config for Claude Code CLI
            filtered_config = {
                "mcpServers": filtered_servers
            }
            
            logger.debug(f"Created filtered MCP config for '{service_name}' with servers: {list(filtered_servers.keys())}")
            return filtered_config
            
        except Exception as e:
            logger.error(f"❌ Failed to create filtered MCP config: {e}")
            return None
    
    async def load_tools_from_config(self, config_file: str) -> List[Dict[str, Any]]:
        """Legacy method - extract service name from config file"""
        if config_file == "mcp-tools.json":
            # Default config
            return await self.load_tools_for_service("default")
        elif config_file.endswith("-tools.json"):
            # Extract service name (e.g., "analysis-tools.json" -> "analysis")
            service_name = config_file.replace("-tools.json", "")
            return await self.load_tools_for_service(service_name)
        else:
            logger.error(f"❌ Unsupported config file format: {config_file}")
            return []
    
    def get_cache_ttl_seconds(self, cache_ttl: str) -> int:
        """Convert cache_ttl to seconds"""
        ttl_mapping = {
            "short": 300,    # 5 minutes
            "long": 1800     # 30 minutes  
        }
        return ttl_mapping.get(cache_ttl, 300)
    
    async def _initialize_mcp_for_config(self, config_key: str, config_data: Dict[str, Any]):
        """Initialize MCP for specific config"""
        try:
            await initialize_mcp_client(config_data)
            self._mcp_initialized[config_key] = True
            
            server_count = len(config_data.get("mcpServers", {}))
            logger.info(f"🔌 MCP initialized for {config_key} with {server_count} servers")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize MCP for {config_key}: {e}")
            self._mcp_initialized[config_key] = False
            raise
    
    async def _load_tools_with_filtering(self, tools_config: MCPToolsConfig) -> List[Dict[str, Any]]:
        """Load tools from MCP client with filtering"""
        if not mcp_client or not mcp_client.available_tools:
            logger.warning("⚠️ No MCP tools available")
            return []
        
        all_tools = []
        exclude_tools = tools_config.exclude_tools or []
        allowed_servers = tools_config.servers or []
        
        for tool_name, tool_schema in mcp_client.available_tools.items():
            # Apply server filtering (if specified)
            if allowed_servers and not self._tool_matches_servers(tool_name, allowed_servers):
                logger.debug(f"🚫 Tool {tool_name} not from allowed servers")
                continue
                
            # Apply exclusion filter
            if tool_name in exclude_tools:
                logger.debug(f"🚫 Excluding tool: {tool_name}")
                continue
            
            try:
                tool = {
                    "type": "function", 
                    "function": {
                        "name": tool_name,
                        "description": tool_schema.get("description", f"MCP tool: {tool_name}"),
                        "parameters": tool_schema.get("inputSchema", {})
                    }
                }
                all_tools.append(tool)
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to convert tool {tool_name}: {e}")
                continue
        
        excluded_count = len(exclude_tools)
        server_filter = f" from servers {allowed_servers}" if allowed_servers else ""
        logger.info(f"🔧 Loaded {len(all_tools)} MCP tools{server_filter} (excluded {excluded_count})")
        return all_tools
    
    def _tool_matches_servers(self, tool_name: str, servers: List[str]) -> bool:
        """Check if tool belongs to allowed servers"""
        # Simple heuristic: tool name prefixes match server names
        for server in servers:
            server_prefix = server.replace("-", "_").replace("server", "").replace("analysis", "").replace("engine", "")
            if any(prefix in tool_name.lower() for prefix in [
                server.replace("-", "_"), 
                server_prefix,
                "financial" if "financial" in server else "",
                "analytics" if "analytics" in server else "",
                "validation" if "validation" in server else ""
            ] if prefix):
                return True
        return False
    
    def _get_config_path(self, config_file: str) -> str:
        """Get full path to config file"""
        return os.path.join(
            os.path.dirname(os.path.abspath(__file__)),
            "..", "config", config_file
        )

# Global singleton
_mcp_loader = SimplifiedMCPLoader()

# Legacy function removed - use _mcp_loader.load_tools_for_service() directly