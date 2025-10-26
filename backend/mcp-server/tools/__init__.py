"""
Retail Analysis Tools for MCP Server

Implementation of retail investor analysis tools based on retail-analysis-tools-registry.json
Each tool provides a specific analysis capability using existing analytics functions.
"""

from .tier_1_information import *

__all__ = [
    'TIER_1_TOOLS',
    'ALL_RETAIL_TOOLS'
]

# Consolidated registry of all retail tools (currently just Tier 1)
ALL_RETAIL_TOOLS = {
    **TIER_1_TOOLS
}