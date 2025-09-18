"""
Technical Analysis Compatibility Module

Provides compatibility interface for MCP server
Uses optimized analytics engine with talib-binary and empyrical
"""

from .main import analytics_engine


def get_all_functions():
    """Get all function names - compatibility with old MCP server interface."""
    return analytics_engine.get_all_function_names()


def get_function_categories():
    """Get function categories - compatibility with old MCP server interface."""
    functions = analytics_engine.list_functions()
    categories = {}
    
    for category, func_list in functions.items():
        categories[category] = {
            "functions": func_list,
            "count": len(func_list)
        }
    
    return categories


def get_function_count():
    """Get function counts - compatibility with old MCP server interface."""
    return analytics_engine.get_function_count()


# Export all functions for compatibility
__all__ = ['get_all_functions', 'get_function_categories', 'get_function_count']