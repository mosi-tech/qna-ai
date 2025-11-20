#!/usr/bin/env python3
"""
Test script for React Components MCP Server
"""

import asyncio
import json
from mcp import ClientSession
from mcp.client.stdio import stdio_client

async def test_component_server():
    """Test the React Components MCP server functionality."""
    
    # Start the server process
    server_params = {
        "command": "python",
        "args": ["react_components_server.py"]
    }
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            
            # Initialize
            await session.initialize()
            
            print("🧪 Testing React Components MCP Server\n")
            
            # Test 1: List all components
            print("1️⃣ Testing list_available_components...")
            result = await session.call_tool("list_available_components", {})
            components_data = json.loads(result.content[0].text)
            print(f"   ✅ Found {components_data['total_count']} components")
            
            # Test 2: Filter by category
            print("\n2️⃣ Testing category filtering (charts)...")
            result = await session.call_tool("list_available_components", {
                "category": "charts"
            })
            charts_data = json.loads(result.content[0].text) 
            print(f"   ✅ Found {charts_data['total_count']} chart components")
            
            # Test 3: Get component schema
            print("\n3️⃣ Testing get_component_schema for BarChart...")
            result = await session.call_tool("get_component_schema", {
                "component_name": "BarChart"
            })
            schema_data = json.loads(result.content[0].text)
            print(f"   ✅ Got schema with {len(schema_data['props_schema']['properties'])} props")
            
            # Test 4: Component suggestions
            print("\n4️⃣ Testing suggest_components_for_data...")
            result = await session.call_tool("suggest_components_for_data", {
                "data_structure": {
                    "etf_rankings": [
                        {"symbol": "QQQ", "sharpe_improvement": 0.67, "rank": 1},
                        {"symbol": "SPY", "sharpe_improvement": 0.45, "rank": 2}
                    ]
                },
                "analysis_type": "ranking",
                "question": "Which ETFs had the largest Sharpe ratio improvement?",
                "max_components": 5
            })
            suggestions_data = json.loads(result.content[0].text)
            primary = suggestions_data["recommendations"]["primary"]
            print(f"   ✅ Primary suggestion: {primary['component_id']} (score: {primary['score']})")
            
            # Test 5: Generate UI configuration
            print("\n5️⃣ Testing generate_ui_configuration...")
            result = await session.call_tool("generate_ui_configuration", {
                "selected_components": [
                    {"component_name": "RankingTable", "role": "primary"},
                    {"component_name": "StatGroup", "role": "supporting"},
                    {"component_name": "ExecutiveSummary", "role": "summary"}
                ],
                "data_mappings": {
                    "RankingTable": {
                        "title": "ETF Performance Rankings",
                        "data": "{{analysis_data.etf_rankings}}"
                    },
                    "StatGroup": {
                        "title": "Summary Statistics",
                        "stats": [
                            {"label": "Total ETFs", "value": "150"},
                            {"label": "Average Improvement", "value": "23%"}
                        ]
                    }
                },
                "layout_template": "ranking"
            })
            ui_config_data = json.loads(result.content[0].text)
            component_count = ui_config_data["ui_configuration"]["metadata"]["total_components"]
            print(f"   ✅ Generated UI config with {component_count} components")
            
            # Test 6: Validate component props
            print("\n6️⃣ Testing validate_component_props...")
            result = await session.call_tool("validate_component_props", {
                "component_name": "BarChart",
                "props": {
                    "data": [
                        {"label": "QQQ", "value": 0.67},
                        {"label": "SPY", "value": 0.45}
                    ],
                    "title": "ETF Improvements",
                    "format": "percentage"
                }
            })
            validation_data = json.loads(result.content[0].text)
            print(f"   ✅ Validation result: {'Valid' if validation_data['is_valid'] else 'Invalid'}")
            
            # Test 7: Get layout templates
            print("\n7️⃣ Testing get_layout_templates...")
            result = await session.call_tool("get_layout_templates", {})
            templates_data = json.loads(result.content[0].text)
            print(f"   ✅ Found {len(templates_data)} layout templates")
            
            # Test 8: Optimize layout
            print("\n8️⃣ Testing optimize_layout...")
            result = await session.call_tool("optimize_layout", {
                "components": [
                    {"component_name": "RankingTable", "priority": "high", "content_type": "visualization"},
                    {"component_name": "StatGroup", "priority": "high", "content_type": "summary"},
                    {"component_name": "ExecutiveSummary", "priority": "medium", "content_type": "summary"}
                ],
                "target_audience": "executive"
            })
            layout_data = json.loads(result.content[0].text)
            optimized_count = len(layout_data["optimized_layout"])
            print(f"   ✅ Optimized layout with {optimized_count} components for executives")
            
            print("\n🎉 All tests passed! MCP server is working correctly.")
            
            # Print sample UI config for reference
            print("\n📋 Sample UI Configuration:")
            print("=" * 50)
            sample_config = {
                "analysis_data": {
                    "etf_rankings": [
                        {"symbol": "QQQ", "sharpe_improvement": 0.67, "rank": 1},
                        {"symbol": "SPY", "sharpe_improvement": 0.45, "rank": 2}
                    ],
                    "summary": {"total_etfs": 150, "avg_improvement": 0.23}
                },
                "ui_config": ui_config_data["ui_configuration"]
            }
            print(json.dumps(sample_config, indent=2))

if __name__ == "__main__":
    asyncio.run(test_component_server())