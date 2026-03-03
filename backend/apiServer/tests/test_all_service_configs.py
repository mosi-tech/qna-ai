#!/usr/bin/env python3
"""
Test all service-specific MCP configurations
"""

import asyncio
import logging
from llm.service import (
    create_analysis_llm, 
    create_context_llm, 
    create_code_prompt_builder_llm, 
    create_reuse_evaluator_llm
)

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_all_service_configs():
    """Test all service-specific MCP configurations"""
    
    print("🧪 Testing All Service-Specific MCP Configurations")
    print("=" * 70)
    
    services = [
        ("Analysis", create_analysis_llm, "analysis-tools.json"),
        ("Context", create_context_llm, "context-tools.json"), 
        ("Code Gen", create_code_prompt_builder_llm, "code-gen-tools.json"),
        ("Reuse Evaluator", create_reuse_evaluator_llm, "reuse-evaluator-tools.json")
    ]
    
    for service_name, service_creator, expected_config in services:
        print(f"\n🔧 Testing {service_name} Service:")
        
        try:
            # Create service
            service = service_creator()
            print(f"   ✅ Service created")
            print(f"   Provider: {service.provider_type}")
            print(f"   Model: {service.default_model}")
            
            # Check config file resolution
            config_file = service.config.get_mcp_config_file()
            print(f"   Config file: {config_file}")
            print(f"   Expected: {expected_config}")
            
            if config_file == expected_config:
                print(f"   ✅ Config matches expected")
            else:
                print(f"   ⚠️ Config mismatch!")
            
            # Load tools
            await service.ensure_tools_loaded()
            tools_count = len(service.default_tools)
            print(f"   Tools loaded: {tools_count}")
            
            if tools_count > 0:
                print(f"   Sample tools:")
                for tool in service.default_tools[:3]:
                    name = tool.get('function', {}).get('name', 'unknown')
                    print(f"     - {name}")
            else:
                print(f"   ⚠️ No tools loaded")
                
        except Exception as e:
            print(f"   ❌ Failed: {e}")
    
    print(f"\n📊 Service Tool Counts Summary:")
    print(f"=" * 50)
    
    for service_name, service_creator, _ in services:
        try:
            service = service_creator()
            await service.ensure_tools_loaded()
            tools_count = len(service.default_tools)
            print(f"   {service_name:<15}: {tools_count:>3} tools")
        except Exception as e:
            print(f"   {service_name:<15}: ❌ {e}")

if __name__ == "__main__":
    asyncio.run(test_all_service_configs())