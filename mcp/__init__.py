"""
Unified MCP Architecture for Financial Analysis

This package contains:
- mcp.financial: Financial data server (Alpaca, EODHD APIs)  
- mcp.analytics: Analytics server (technical analysis, portfolio optimization)
- mcp.tools: Retail analysis tools (using both financial + analytics)
- financial_server.py: Standalone MCP financial server
- analytics_server.py: Standalone MCP analytics server

Each component can run as separate MCP servers or be used together.
Real financial data → Analytics calculations → Retail insights
"""

__version__ = "2.0.0"
__author__ = "MCP Financial Analytics Team"

# Import main components
from . import financial
from . import analytics  
from . import tools