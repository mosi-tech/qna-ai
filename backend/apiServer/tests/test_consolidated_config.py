#!/usr/bin/env python3
"""
Test the new consolidated MCP tools configuration
"""

import asyncio
import logging
from llm.service import create_analysis_llm, create_context_llm, create_code_prompt_builder_llm, create_reuse_evaluator_llm
from llm.mcp_tools import _mcp_loader

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_consolidated_config():
    """Test the consolidated MCP configuration"""
    
    print("🧪 Testing Consolidated MCP Configuration")
    print("=" * 60)
    
    # Test 1: Direct service loading
    print("1️⃣ Testing direct service loading from consolidated config:")
    
    services = ["analysis", "context", "code-gen", "reuse-evaluator", "none", "nonexistent"]
    
    for service_name in services:
        try:
            tools = await _mcp_loader.load_tools_for_service(service_name)
            print(f"   {service_name:<15}: {len(tools):>3} tools")
            
            if tools and len(tools) <= 3:
                for tool in tools:
                    name = tool.get('function', {}).get('name', 'unknown')
                    print(f"     - {name}")
        except Exception as e:
            print(f"   {service_name:<15}: ❌ {e}")
    
    # Test 2: Service-specific LLM creation
    print(f"\n2️⃣ Testing service-specific LLM creation:")
    
    llm_services = [
        ("Analysis", create_analysis_llm),
        ("Context", create_context_llm),
        ("Code Gen", create_code_prompt_builder_llm),
        ("Reuse Evaluator", create_reuse_evaluator_llm)
    ]
    
    for service_name, service_creator in llm_services:
        try:
            service = service_creator()
            await service.ensure_tools_loaded()
            tools_count = len(service.default_tools)
            print(f"   {service_name:<15}: {tools_count:>3} tools")
            
            # Show sample tools
            if tools_count > 0:
                sample_tools = [tool.get('function', {}).get('name', 'unknown') 
                              for tool in service.default_tools[:2]]
                print(f"     Sample: {', '.join(sample_tools)}")
                
        except Exception as e:
            print(f"   {service_name:<15}: ❌ {e}")
    
    # Test 3: Verify tool filtering
    print(f"\n3️⃣ Testing tool filtering logic:")
    
    # Analysis should have financial + analytics tools
    analysis_service = create_analysis_llm()
    await analysis_service.ensure_tools_loaded()
    analysis_tools = [tool.get('function', {}).get('name', '') for tool in analysis_service.default_tools]
    
    has_financial = any('alpaca' in tool for tool in analysis_tools)
    has_analytics = any('calculate' in tool for tool in analysis_tools)
    has_validation = any('write_and_validate' in tool for tool in analysis_tools)
    
    print(f"   Analysis tools:")
    print(f"     Has financial tools: {'✅' if has_financial else '❌'}")
    print(f"     Has analytics tools: {'✅' if has_analytics else '❌'}")
    print(f"     Has validation tools: {'❌' if not has_validation else '⚠️'}")
    
    # Code-gen should only have validation tools
    code_gen_service = create_code_prompt_builder_llm()
    await code_gen_service.ensure_tools_loaded()
    code_gen_tools = [tool.get('function', {}).get('name', '') for tool in code_gen_service.default_tools]
    
    has_financial_cg = any('alpaca' in tool for tool in code_gen_tools)
    has_analytics_cg = any('calculate' in tool for tool in code_gen_tools)
    has_validation_cg = any('write_and_validate' in tool or 'read_file' in tool for tool in code_gen_tools)
    
    print(f"   Code-gen tools:")
    print(f"     Has financial tools: {'❌' if not has_financial_cg else '⚠️'}")
    print(f"     Has analytics tools: {'❌' if not has_analytics_cg else '⚠️'}")
    print(f"     Has validation tools: {'✅' if has_validation_cg else '❌'}")

if __name__ == "__main__":
    asyncio.run(test_consolidated_config())