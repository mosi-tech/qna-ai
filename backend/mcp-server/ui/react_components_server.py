#!/usr/bin/env python3
"""
React Components MCP Server

Provides tools for selecting and configuring React insight components
for dynamic UI generation based on analysis results.
"""

import json
import logging
from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.server.stdio import stdio_server
from mcp.types import (
    CallToolRequest,
    CallToolResult,
    TextContent,
    Tool,
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("react-components-server")

# Initialize the MCP server
server = Server("react-components-server")

# Component metadata registry - matches our actual React components
COMPONENT_REGISTRY = {
    # Charts
    "BarChart": {
        "id": "BarChart",
        "category": "charts",
        "description": "Clean bar chart for comparing values across categories",
        "use_cases": ["Rankings", "category comparisons", "performance metrics", "distribution analysis"],
        "data_format": "Array of objects with label and value properties",
        "props_schema": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string"},
                            "value": {"type": "number"},
                            "color": {"type": "string", "optional": True}
                        },
                        "required": ["label", "value"]
                    }
                },
                "title": {"type": "string", "optional": True},
                "orientation": {"type": "string", "enum": ["horizontal", "vertical"], "default": "vertical"},
                "format": {"type": "string", "enum": ["number", "percentage", "currency"], "default": "number"},
                "color": {"type": "string", "enum": ["blue", "green", "purple", "orange"], "default": "blue"},
                "showValues": {"type": "boolean", "default": True}
            },
            "required": ["data"]
        },
        "layout_hints": ["third", "half", "full"],
        "height_hints": ["medium", "tall"],
        "best_for_data_types": ["numerical", "categorical", "rankings", "comparisons"]
    },
    
    "PieChart": {
        "id": "PieChart",
        "category": "charts", 
        "description": "Clean pie/donut chart for showing proportional data and distributions",
        "use_cases": ["Portfolio allocations", "category distributions", "market share", "composition analysis"],
        "data_format": "Array of objects with label, value, and optional color properties",
        "props_schema": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string"},
                            "value": {"type": "number"},
                            "color": {"type": "string", "optional": True}
                        },
                        "required": ["label", "value"]
                    }
                },
                "title": {"type": "string", "optional": True},
                "showLegend": {"type": "boolean", "default": True},
                "showPercentages": {"type": "boolean", "default": True},
                "innerRadius": {"type": "number", "default": 0},
                "colors": {"type": "string", "enum": ["default", "business", "tech", "finance"], "default": "default"}
            },
            "required": ["data"]
        },
        "layout_hints": ["half", "full"],
        "height_hints": ["medium", "tall"],
        "best_for_data_types": ["proportional", "categorical", "distributions", "allocations"]
    },
    
    "LineChart": {
        "id": "LineChart",
        "category": "charts",
        "description": "Clean line chart for time series data and trend visualization",
        "use_cases": ["Performance over time", "historical analysis", "trend tracking", "growth curves"],
        "data_format": "Array of objects with date/label and value properties, supports multiple series",
        "props_schema": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string"},
                            "date": {"type": "string", "format": "date", "optional": True},
                            "value": {"type": "number"}
                        },
                        "required": ["label", "value"]
                    }
                },
                "title": {"type": "string", "optional": True},
                "xAxisLabel": {"type": "string", "optional": True},
                "yAxisLabel": {"type": "string", "optional": True},
                "format": {"type": "string", "enum": ["number", "percentage", "currency"], "default": "number"},
                "showDots": {"type": "boolean", "default": True},
                "showArea": {"type": "boolean", "default": False},
                "colors": {"type": "string", "enum": ["default", "business", "tech", "finance"], "default": "default"}
            },
            "required": ["data"]
        },
        "layout_hints": ["half", "full"],
        "height_hints": ["medium", "tall"],
        "best_for_data_types": ["time_series", "trends", "historical", "sequential"]
    },
    
    "ScatterChart": {
        "id": "ScatterChart",
        "category": "charts",
        "description": "Clean scatter plot for exploring relationships between two variables",
        "use_cases": ["Correlation analysis", "risk vs return plots", "performance comparisons", "outlier detection"],
        "data_format": "Array of objects with x, y values and optional labels/colors",
        "props_schema": {
            "type": "object", 
            "properties": {
                "data": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "x": {"type": "number"},
                            "y": {"type": "number"},
                            "label": {"type": "string", "optional": True},
                            "color": {"type": "string", "optional": True},
                            "size": {"type": "number", "optional": True}
                        },
                        "required": ["x", "y"]
                    }
                },
                "title": {"type": "string", "optional": True},
                "xAxis": {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string"},
                        "format": {"type": "string", "enum": ["number", "percentage", "currency"], "default": "number"}
                    },
                    "required": ["label"]
                },
                "yAxis": {
                    "type": "object",
                    "properties": {
                        "label": {"type": "string"},
                        "format": {"type": "string", "enum": ["number", "percentage", "currency"], "default": "number"}
                    },
                    "required": ["label"]
                },
                "showTrendLine": {"type": "boolean", "default": False},
                "pointSize": {"type": "number", "default": 4},
                "colors": {"type": "string", "enum": ["default", "business", "tech", "finance"], "default": "default"}
            },
            "required": ["data", "xAxis", "yAxis"]
        },
        "layout_hints": ["half", "full"],
        "height_hints": ["medium", "tall"],
        "best_for_data_types": ["correlation", "scatter", "relationships", "two_variable"]
    },
    
    # Tables
    "RankingTable": {
        "id": "RankingTable",
        "category": "tables",
        "description": "Advanced ranking table with sorting, formatting, and performance indicators",
        "use_cases": ["Performance rankings", "leaderboards", "comparisons", "sorted data display"],
        "data_format": "Array of objects with consistent properties for ranking",
        "props_schema": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "array",
                    "items": {"type": "object"}
                },
                "title": {"type": "string", "optional": True},
                "columns": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "align": {"type": "string", "enum": ["left", "center", "right"], "default": "left"},
                            "format": {"type": "string", "enum": ["text", "number", "percentage", "currency", "badge"], "default": "text"}
                        },
                        "required": ["id", "name"]
                    }
                },
                "primaryColumn": {"type": "string", "optional": True}
            },
            "required": ["data", "columns"]
        },
        "layout_hints": ["half", "full"],
        "height_hints": ["medium", "tall"],
        "best_for_data_types": ["rankings", "tabular", "comparisons", "multi_column"]
    },
    
    "ComparisonTable": {
        "id": "ComparisonTable", 
        "category": "tables",
        "description": "Side-by-side comparison table for entities across multiple metrics",
        "use_cases": ["Performance comparisons", "before/after analysis", "multi-entity evaluation"],
        "data_format": "Entities and metrics with cross-tabulated data",
        "props_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "optional": True},
                "entities": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "shortName": {"type": "string", "optional": True},
                            "description": {"type": "string", "optional": True}
                        },
                        "required": ["id", "name"]
                    }
                },
                "metrics": {
                    "type": "array", 
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "format": {"type": "string", "enum": ["number", "percentage", "currency", "ratio"], "default": "number"}
                        },
                        "required": ["id", "name"]
                    }
                },
                "data": {"type": "object"},
                "showChange": {"type": "boolean", "default": False},
                "highlightBest": {"type": "boolean", "default": True}
            },
            "required": ["entities", "metrics", "data"]
        },
        "layout_hints": ["half", "full"],
        "height_hints": ["medium", "tall"],
        "best_for_data_types": ["comparisons", "cross_tabulated", "multi_entity", "metrics"]
    },
    
    "HeatmapTable": {
        "id": "HeatmapTable",
        "category": "tables",
        "description": "Heatmap visualization for matrix data with color-coded cells",
        "use_cases": ["Correlation matrices", "performance grids", "risk matrices", "cross-tabulated metrics"],
        "data_format": "2D array of numerical values with row/column labels",
        "props_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "optional": True},
                "data": {
                    "type": "array",
                    "items": {
                        "type": "array",
                        "items": {"type": "number"}
                    }
                },
                "rowLabels": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "columnLabels": {
                    "type": "array", 
                    "items": {"type": "string"}
                },
                "cellConfig": {
                    "type": "object",
                    "properties": {
                        "format": {"type": "string", "enum": ["number", "percentage", "currency"], "default": "number"},
                        "decimals": {"type": "number", "default": 2},
                        "colorScheme": {"type": "string", "enum": ["heatmap", "diverging", "sequential"], "default": "heatmap"}
                    }
                }
            },
            "required": ["data", "rowLabels", "columnLabels"]
        },
        "layout_hints": ["half", "full"],
        "height_hints": ["medium", "tall"],
        "best_for_data_types": ["matrix", "correlation", "heatmap", "grid"]
    },
    
    # Lists and Text
    "ExecutiveSummary": {
        "id": "ExecutiveSummary",
        "category": "lists",
        "description": "High-level executive summary with key findings and color-coded insights",
        "use_cases": ["Key findings", "executive overview", "main insights", "summary points"],
        "data_format": "Array of summary items with labels and color coding",
        "props_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "optional": True},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object", 
                        "properties": {
                            "label": {"type": "string"},
                            "text": {"type": "string"},
                            "color": {"type": "string", "enum": ["default", "blue", "green", "orange", "red"], "default": "default"}
                        },
                        "required": ["label", "text"]
                    }
                }
            },
            "required": ["items"]
        },
        "layout_hints": ["half", "full"],
        "height_hints": ["short", "medium"],
        "best_for_data_types": ["summary", "insights", "findings", "textual"]
    },
    
    "BulletList": {
        "id": "BulletList",
        "category": "lists", 
        "description": "Clean bullet point list for key insights and findings",
        "use_cases": ["Key insights", "bullet points", "simple lists", "highlights"],
        "data_format": "Array of strings or simple items",
        "props_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "optional": True},
                "items": {
                    "type": "array",
                    "items": {"type": "string"}
                }
            },
            "required": ["items"]
        },
        "layout_hints": ["third", "half"],
        "height_hints": ["short", "medium"],
        "best_for_data_types": ["simple_list", "textual", "insights"]
    },
    
    "RankedList": {
        "id": "RankedList",
        "category": "lists",
        "description": "Ranked list with performance indicators and change metrics",
        "use_cases": ["Top performers", "rankings", "leaderboards", "ordered lists"],
        "data_format": "Array of objects with ranking information",
        "props_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "optional": True},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "name": {"type": "string"},
                            "value": {"type": "string"},
                            "changeType": {"type": "string", "enum": ["positive", "negative", "neutral"], "optional": True}
                        },
                        "required": ["id", "name", "value"]
                    }
                },
                "maxItems": {"type": "number", "optional": True}
            },
            "required": ["items"]
        },
        "layout_hints": ["third", "half"],
        "height_hints": ["medium"],
        "best_for_data_types": ["rankings", "ordered", "performance"]
    },
    
    "CalloutList": {
        "id": "CalloutList",
        "category": "lists",
        "description": "Important callouts and alerts with type-based styling",
        "use_cases": ["Warnings", "important notes", "alerts", "highlighted information"],
        "data_format": "Array of callout items with types and content",
        "props_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "optional": True},
                "items": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "id": {"type": "string"},
                            "title": {"type": "string"},
                            "content": {"type": "string"},
                            "type": {"type": "string", "enum": ["info", "warning", "success", "error"], "default": "info"}
                        },
                        "required": ["id", "title", "content"]
                    }
                }
            },
            "required": ["items"]
        },
        "layout_hints": ["third", "half", "full"],
        "height_hints": ["medium"],
        "best_for_data_types": ["alerts", "callouts", "important_info"]
    },
    
    # Cards and Display
    "StatGroup": {
        "id": "StatGroup",
        "category": "cards",
        "description": "Group of key statistics with optional change indicators",
        "use_cases": ["KPI display", "summary metrics", "dashboard stats", "key numbers"],
        "data_format": "Array of statistics with values and optional change indicators",
        "props_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "optional": True},
                "stats": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "label": {"type": "string"},
                            "value": {"type": "string"},
                            "change": {"type": "number", "optional": True},
                            "format": {"type": "string", "enum": ["number", "percentage", "currency"], "default": "number"}
                        },
                        "required": ["label", "value"]
                    }
                }
            },
            "required": ["stats"]
        },
        "layout_hints": ["third", "half", "full"],
        "height_hints": ["short"],
        "best_for_data_types": ["statistics", "kpis", "metrics", "numerical"]
    },
    
    "SectionedInsightCard": {
        "id": "SectionedInsightCard",
        "category": "cards",
        "description": "Multi-section card for comprehensive analysis with different content types",
        "use_cases": ["Detailed analysis", "multi-part insights", "comprehensive reports"],
        "data_format": "Structured sections with titles and content arrays",
        "props_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "optional": True},
                "description": {"type": "string", "optional": True},
                "sections": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string"},
                            "content": {
                                "type": "array",
                                "items": {"type": "string"}
                            },
                            "type": {"type": "string", "enum": ["default", "highlight", "warning"], "default": "default"}
                        },
                        "required": ["title", "content"]
                    }
                }
            },
            "required": ["sections"]
        },
        "layout_hints": ["half", "full"],
        "height_hints": ["medium", "tall"],
        "best_for_data_types": ["sectioned", "comprehensive", "multi_part"]
    },
    
    # Text Components
    "SummaryConclusion": {
        "id": "SummaryConclusion",
        "category": "text",
        "description": "Comprehensive conclusion with findings, analysis, and next steps",
        "use_cases": ["Final analysis", "conclusions", "recommendations", "comprehensive summaries"],
        "data_format": "Structured conclusion with key findings and next steps",
        "props_schema": {
            "type": "object",
            "properties": {
                "title": {"type": "string", "optional": True},
                "keyFindings": {
                    "type": "array",
                    "items": {"type": "string"}
                },
                "conclusion": {"type": "string"},
                "nextSteps": {
                    "type": "array", 
                    "items": {"type": "string"},
                    "optional": True
                },
                "confidence": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"}
            },
            "required": ["keyFindings", "conclusion"]
        },
        "layout_hints": ["half", "full"],
        "height_hints": ["medium", "tall"],
        "best_for_data_types": ["conclusion", "summary", "recommendations", "textual"]
    }
}

# Layout configuration templates
LAYOUT_TEMPLATES = {
    "dashboard": {
        "description": "Dashboard layout with stats at top, main content in middle, summary at bottom",
        "pattern": [
            {"row": 0, "components": ["StatGroup"], "sizes": ["third", "third", "third"]},
            {"row": 1, "components": ["primary"], "sizes": ["full"]},
            {"row": 2, "components": ["supporting"], "sizes": ["half", "half"]}
        ]
    },
    "analysis": {
        "description": "Analysis layout with executive summary, main analysis, and conclusion",
        "pattern": [
            {"row": 0, "components": ["ExecutiveSummary"], "sizes": ["full"]},
            {"row": 1, "components": ["primary", "supporting"], "sizes": ["half", "half"]},
            {"row": 2, "components": ["SummaryConclusion"], "sizes": ["full"]}
        ]
    },
    "comparison": {
        "description": "Comparison layout focusing on side-by-side analysis",
        "pattern": [
            {"row": 0, "components": ["StatGroup"], "sizes": ["half", "half"]},
            {"row": 1, "components": ["primary"], "sizes": ["full"]},
            {"row": 2, "components": ["supporting"], "sizes": ["third", "third", "third"]}
        ]
    },
    "ranking": {
        "description": "Ranking layout with primary table and supporting visualizations",
        "pattern": [
            {"row": 0, "components": ["StatGroup", "ExecutiveSummary"], "sizes": ["third", "half"]},
            {"row": 1, "components": ["primary"], "sizes": ["full"]},
            {"row": 2, "components": ["supporting"], "sizes": ["half", "half"]}
        ]
    }
}

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List all available tools for React component selection and configuration."""
    
    tools = [
        Tool(
            name="list_available_components",
            description="Get metadata for all available React components including props schemas, use cases, and layout hints",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string", 
                        "description": "Filter by component category (charts, tables, lists, cards, text)",
                        "enum": ["charts", "tables", "lists", "cards", "text"]
                    },
                    "data_type": {
                        "type": "string",
                        "description": "Filter by best data type match",
                        "enum": ["numerical", "categorical", "rankings", "time_series", "proportional", "correlation", "textual"]
                    }
                }
            }
        ),
        Tool(
            name="get_component_schema", 
            description="Get detailed props schema and configuration for a specific React component",
            inputSchema={
                "type": "object",
                "properties": {
                    "component_name": {
                        "type": "string",
                        "description": "Name of the React component to get schema for"
                    }
                },
                "required": ["component_name"]
            }
        ),
        Tool(
            name="suggest_components_for_data",
            description="AI-powered component suggestions based on data structure and analysis type",
            inputSchema={
                "type": "object", 
                "properties": {
                    "data_structure": {
                        "type": "object",
                        "description": "Sample or description of the analysis data structure"
                    },
                    "analysis_type": {
                        "type": "string",
                        "description": "Type of analysis being performed",
                        "enum": ["ranking", "comparison", "correlation", "distribution", "time_series", "summary", "detailed_analysis"]
                    },
                    "question": {
                        "type": "string", 
                        "description": "Original user question to understand intent"
                    },
                    "max_components": {
                        "type": "number",
                        "description": "Maximum number of components to suggest (default: 5)",
                        "default": 5
                    }
                },
                "required": ["data_structure", "analysis_type", "question"]
            }
        ),
        Tool(
            name="generate_ui_configuration",
            description="Generate complete UI configuration with selected components, props, and responsive layout",
            inputSchema={
                "type": "object",
                "properties": {
                    "selected_components": {
                        "type": "array",
                        "items": {
                            "type": "object", 
                            "properties": {
                                "component_name": {"type": "string"},
                                "role": {"type": "string", "enum": ["primary", "supporting", "summary"]}
                            },
                            "required": ["component_name", "role"]
                        },
                        "description": "Components selected for the UI"
                    },
                    "data_mappings": {
                        "type": "object",
                        "description": "Mapping of analysis data to component props"
                    },
                    "layout_template": {
                        "type": "string",
                        "enum": ["dashboard", "analysis", "comparison", "ranking"],
                        "description": "Layout template to use",
                        "default": "dashboard"
                    }
                },
                "required": ["selected_components", "data_mappings"]
            }
        ),
        Tool(
            name="validate_component_props",
            description="Validate component props against schema and provide suggestions",
            inputSchema={
                "type": "object",
                "properties": {
                    "component_name": {
                        "type": "string", 
                        "description": "Name of the component to validate"
                    },
                    "props": {
                        "type": "object",
                        "description": "Props object to validate"
                    }
                },
                "required": ["component_name", "props"]
            }
        ),
        Tool(
            name="get_layout_templates",
            description="Get available layout templates and their configurations",
            inputSchema={
                "type": "object",
                "properties": {}
            }
        ),
        Tool(
            name="optimize_layout",
            description="Optimize component layout for responsive design and information hierarchy",
            inputSchema={
                "type": "object",
                "properties": {
                    "components": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "component_name": {"type": "string"},
                                "priority": {"type": "string", "enum": ["high", "medium", "low"]},
                                "content_type": {"type": "string", "enum": ["summary", "detail", "visualization"]}
                            }
                        },
                        "description": "Components to layout with priorities"
                    },
                    "target_audience": {
                        "type": "string",
                        "enum": ["executive", "analyst", "general"],
                        "description": "Target audience for layout optimization"
                    }
                },
                "required": ["components"]
            }
        )
    ]
    
    return tools

@server.call_tool()
async def handle_call_tool(request: CallToolRequest) -> CallToolResult:
    """Handle tool calls for React component operations."""
    
    try:
        if request.name == "list_available_components":
            return await _list_available_components(request.arguments or {})
        elif request.name == "get_component_schema":
            return await _get_component_schema(request.arguments or {})
        elif request.name == "suggest_components_for_data":
            return await _suggest_components_for_data(request.arguments or {})
        elif request.name == "generate_ui_configuration":
            return await _generate_ui_configuration(request.arguments or {})
        elif request.name == "validate_component_props":
            return await _validate_component_props(request.arguments or {})
        elif request.name == "get_layout_templates":
            return await _get_layout_templates(request.arguments or {})
        elif request.name == "optimize_layout":
            return await _optimize_layout(request.arguments or {})
        else:
            return CallToolResult(
                content=[TextContent(type="text", text=f"Unknown tool: {request.name}")]
            )
            
    except Exception as e:
        logger.error(f"Error handling tool call {request.name}: {str(e)}")
        return CallToolResult(
            content=[TextContent(type="text", text=f"Error: {str(e)}")]
        )

async def _list_available_components(args: Dict[str, Any]) -> CallToolResult:
    """List available React components with optional filtering."""
    
    category_filter = args.get("category")
    data_type_filter = args.get("data_type")
    
    filtered_components = []
    
    for comp_id, comp_meta in COMPONENT_REGISTRY.items():
        # Apply category filter
        if category_filter and comp_meta["category"] != category_filter:
            continue
            
        # Apply data type filter
        if data_type_filter and data_type_filter not in comp_meta["best_for_data_types"]:
            continue
            
        filtered_components.append({
            "id": comp_id,
            "category": comp_meta["category"],
            "description": comp_meta["description"],
            "use_cases": comp_meta["use_cases"],
            "data_format": comp_meta["data_format"],
            "layout_hints": comp_meta["layout_hints"],
            "height_hints": comp_meta["height_hints"],
            "best_for_data_types": comp_meta["best_for_data_types"]
        })
    
    result = {
        "components": filtered_components,
        "total_count": len(filtered_components),
        "filters_applied": {
            "category": category_filter,
            "data_type": data_type_filter
        }
    }
    
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(result, indent=2))]
    )

async def _get_component_schema(args: Dict[str, Any]) -> CallToolResult:
    """Get detailed schema for a specific component."""
    
    component_name = args.get("component_name")
    
    if not component_name or component_name not in COMPONENT_REGISTRY:
        available = list(COMPONENT_REGISTRY.keys())
        return CallToolResult(
            content=[TextContent(
                type="text", 
                text=f"Component '{component_name}' not found. Available: {available}"
            )]
        )
    
    component = COMPONENT_REGISTRY[component_name]
    
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(component, indent=2))]
    )

async def _suggest_components_for_data(args: Dict[str, Any]) -> CallToolResult:
    """Suggest optimal components based on data structure and analysis type."""
    
    data_structure = args.get("data_structure", {})
    analysis_type = args.get("analysis_type")
    question = args.get("question", "")
    max_components = args.get("max_components", 5)
    
    suggestions = []
    
    # Scoring system for component selection
    def score_component(comp_meta: Dict[str, Any]) -> float:
        score = 0.0
        
        # Analysis type matching
        analysis_weights = {
            "ranking": ["rankings", "comparisons", "tabular"],
            "comparison": ["comparisons", "cross_tabulated", "metrics"],
            "correlation": ["correlation", "scatter", "relationships"], 
            "distribution": ["proportional", "categorical", "distributions"],
            "time_series": ["time_series", "trends", "historical"],
            "summary": ["summary", "insights", "statistics"],
            "detailed_analysis": ["comprehensive", "sectioned", "detailed"]
        }
        
        if analysis_type in analysis_weights:
            for data_type in analysis_weights[analysis_type]:
                if data_type in comp_meta["best_for_data_types"]:
                    score += 2.0
        
        # Data structure analysis
        if isinstance(data_structure, dict):
            # Check for array data (good for charts/tables)
            if any(isinstance(v, list) for v in data_structure.values()):
                if comp_meta["category"] in ["charts", "tables"]:
                    score += 1.0
            
            # Check for numerical data
            has_numbers = any(
                isinstance(v, (int, float)) or 
                (isinstance(v, list) and v and isinstance(v[0], (int, float, dict)))
                for v in data_structure.values()
            )
            
            if has_numbers and comp_meta["category"] == "charts":
                score += 1.0
        
        # Question keyword matching
        question_lower = question.lower()
        keyword_matches = {
            "ranking": ["rank", "top", "best", "worst", "leading", "highest", "lowest"],
            "comparison": ["compare", "vs", "versus", "difference", "better", "worse"],
            "trend": ["trend", "over time", "historical", "growth", "decline"],
            "distribution": ["distribution", "allocation", "breakdown", "composition"],
            "correlation": ["relationship", "correlation", "related", "association"]
        }
        
        for match_type, keywords in keyword_matches.items():
            if any(keyword in question_lower for keyword in keywords):
                if match_type in comp_meta["best_for_data_types"]:
                    score += 1.5
        
        return score
    
    # Score all components
    component_scores = []
    for comp_id, comp_meta in COMPONENT_REGISTRY.items():
        score = score_component(comp_meta)
        if score > 0:
            component_scores.append({
                "component_id": comp_id,
                "score": score,
                "metadata": comp_meta
            })
    
    # Sort by score and take top suggestions
    component_scores.sort(key=lambda x: x["score"], reverse=True)
    top_suggestions = component_scores[:max_components]
    
    # Categorize suggestions
    primary_suggestion = top_suggestions[0] if top_suggestions else None
    supporting_suggestions = top_suggestions[1:4] if len(top_suggestions) > 1 else []
    summary_suggestions = [s for s in top_suggestions[4:] if s["metadata"]["category"] in ["text", "cards"]]
    
    result = {
        "analysis_type": analysis_type,
        "question": question,
        "recommendations": {
            "primary": {
                "component_id": primary_suggestion["component_id"],
                "score": primary_suggestion["score"],
                "reason": "Best match for primary data visualization",
                "role": "primary"
            } if primary_suggestion else None,
            "supporting": [
                {
                    "component_id": s["component_id"],
                    "score": s["score"],
                    "reason": "Provides additional context and detail",
                    "role": "supporting"
                }
                for s in supporting_suggestions
            ],
            "summary": [
                {
                    "component_id": s["component_id"], 
                    "score": s["score"],
                    "reason": "Summarizes insights and conclusions",
                    "role": "summary"
                }
                for s in summary_suggestions
            ]
        },
        "all_scored_components": [
            {
                "component_id": s["component_id"],
                "score": s["score"],
                "category": s["metadata"]["category"]
            }
            for s in component_scores
        ]
    }
    
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(result, indent=2))]
    )

async def _generate_ui_configuration(args: Dict[str, Any]) -> CallToolResult:
    """Generate complete UI configuration with layout and data mapping."""
    
    selected_components = args.get("selected_components", [])
    data_mappings = args.get("data_mappings", {})
    layout_template = args.get("layout_template", "dashboard")
    
    if not selected_components:
        return CallToolResult(
            content=[TextContent(type="text", text="Error: No components selected")]
        )
    
    # Generate component configurations
    ui_components = []
    
    for i, comp_selection in enumerate(selected_components):
        comp_name = comp_selection["component_name"]
        comp_role = comp_selection["role"]
        
        if comp_name not in COMPONENT_REGISTRY:
            continue
            
        comp_meta = COMPONENT_REGISTRY[comp_name]
        
        # Generate props from data mappings
        comp_props = {}
        
        # Map data based on component requirements
        if comp_name in data_mappings:
            comp_props.update(data_mappings[comp_name])
        
        # Add default props if not specified
        if "title" not in comp_props and comp_role == "primary":
            comp_props["title"] = f"Analysis Results"
        
        # Determine layout based on role and template
        if comp_role == "primary":
            size_hint = "full"
            height_hint = "tall"
        elif comp_role == "supporting":
            size_hint = "half" if len(selected_components) > 3 else "half"
            height_hint = "medium"
        else:  # summary
            size_hint = "full"
            height_hint = "medium"
        
        ui_components.append({
            "id": f"{comp_name}_{i}",
            "type": comp_name,
            "props": comp_props,
            "layout": {
                "size": size_hint,
                "height": height_hint,
                "priority": {"primary": 1, "supporting": 2, "summary": 3}[comp_role]
            },
            "role": comp_role
        })
    
    # Apply layout template
    template = LAYOUT_TEMPLATES.get(layout_template, LAYOUT_TEMPLATES["dashboard"])
    
    result = {
        "ui_configuration": {
            "components": ui_components,
            "layout": {
                "template": layout_template,
                "template_description": template["description"],
                "responsive": True,
                "grid_system": "3-column"
            },
            "metadata": {
                "generated_at": datetime.now().isoformat(),
                "total_components": len(ui_components),
                "primary_components": len([c for c in ui_components if c["role"] == "primary"]),
                "supporting_components": len([c for c in ui_components if c["role"] == "supporting"]),
                "summary_components": len([c for c in ui_components if c["role"] == "summary"])
            }
        }
    }
    
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(result, indent=2))]
    )

async def _validate_component_props(args: Dict[str, Any]) -> CallToolResult:
    """Validate component props against schema."""
    
    component_name = args.get("component_name")
    props = args.get("props", {})
    
    if component_name not in COMPONENT_REGISTRY:
        return CallToolResult(
            content=[TextContent(type="text", text=f"Component '{component_name}' not found")]
        )
    
    comp_meta = COMPONENT_REGISTRY[component_name]
    schema = comp_meta["props_schema"]
    
    validation_result = {
        "component_name": component_name,
        "is_valid": True,
        "errors": [],
        "warnings": [],
        "suggestions": []
    }
    
    # Basic validation (simplified - would use jsonschema in production)
    required_props = schema.get("properties", {})
    
    for prop_name, prop_schema in required_props.items():
        if prop_schema.get("required", False) and prop_name not in props:
            validation_result["errors"].append(f"Missing required prop: {prop_name}")
            validation_result["is_valid"] = False
    
    # Check data format
    if "data" in props:
        data = props["data"]
        expected_format = comp_meta["data_format"]
        
        if not isinstance(data, list):
            validation_result["errors"].append("Data should be an array")
            validation_result["is_valid"] = False
        elif data and isinstance(data, list):
            # Check first item structure for consistency
            first_item = data[0]
            if component_name == "BarChart":
                if not isinstance(first_item, dict) or "label" not in first_item or "value" not in first_item:
                    validation_result["warnings"].append("BarChart data should have 'label' and 'value' properties")
    
    # Add suggestions based on component best practices
    if component_name == "BarChart" and len(props.get("data", [])) > 10:
        validation_result["suggestions"].append("Consider using pagination or filtering for datasets with >10 items")
    
    if component_name == "PieChart" and len(props.get("data", [])) > 8:
        validation_result["suggestions"].append("Pie charts work best with 8 or fewer categories")
    
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(validation_result, indent=2))]
    )

async def _get_layout_templates(args: Dict[str, Any]) -> CallToolResult:
    """Get available layout templates."""
    
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(LAYOUT_TEMPLATES, indent=2))]
    )

async def _optimize_layout(args: Dict[str, Any]) -> CallToolResult:
    """Optimize component layout based on priorities and audience."""
    
    components = args.get("components", [])
    target_audience = args.get("target_audience", "general")
    
    if not components:
        return CallToolResult(
            content=[TextContent(type="text", text="Error: No components provided")]
        )
    
    # Sort components by priority and content type
    priority_order = {"high": 1, "medium": 2, "low": 3}
    
    sorted_components = sorted(
        components,
        key=lambda x: (
            priority_order.get(x.get("priority", "medium"), 2),
            {"summary": 1, "visualization": 2, "detail": 3}.get(x.get("content_type", "detail"), 3)
        )
    )
    
    # Generate layout based on audience
    if target_audience == "executive":
        # Executives prefer summary first, then key visualizations
        layout_suggestions = [
            {"component": comp["component_name"], "size": "full" if comp.get("content_type") == "summary" else "half"}
            for comp in sorted_components[:4]  # Limit for executive view
        ]
    elif target_audience == "analyst":
        # Analysts want detail and full data access
        layout_suggestions = [
            {"component": comp["component_name"], "size": "third" if comp.get("priority") == "low" else "half"}
            for comp in sorted_components
        ]
    else:  # general
        # Balanced approach
        layout_suggestions = [
            {"component": comp["component_name"], "size": "half"}
            for comp in sorted_components[:6]
        ]
    
    optimization_result = {
        "optimized_layout": layout_suggestions,
        "target_audience": target_audience,
        "optimization_notes": [
            f"Prioritized {target_audience} viewing preferences",
            f"Arranged {len(layout_suggestions)} components by priority",
            "Used responsive grid system for mobile compatibility"
        ]
    }
    
    return CallToolResult(
        content=[TextContent(type="text", text=json.dumps(optimization_result, indent=2))]
    )

async def main():
    """Run the React Components MCP server."""
    logger.info("Starting React Components MCP server")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="react-components-server",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())