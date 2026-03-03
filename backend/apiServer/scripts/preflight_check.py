#!/usr/bin/env python3
"""
Pre-flight Check Script

Validates that all required services and dependencies are running before starting the API.
Run this before starting the server to ensure a smooth development experience.

Usage:
    python preflight_check.py
    python preflight_check.py --fix     # Attempt to fix missing services
    python preflight_check.py --verbose # Show detailed output
"""

import asyncio
import sys
import os
import argparse
from pathlib import Path

# Add backend root to Python path
backend_root = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, backend_root)

from shared.health.health_checker import HealthChecker, HealthStatus


async def main():
    """Run pre-flight checks"""
    parser = argparse.ArgumentParser(description="Pre-flight check for development environment")
    parser.add_argument("--fix", action="store_true", help="Attempt to auto-fix missing services")
    parser.add_argument("--verbose", action="store_true", help="Show detailed output")
    args = parser.parse_args()
    
    print("\n🚀 QnA-AI Development Environment - Pre-Flight Check")
    print("=" * 60)
    
    # Create health checker
    checker = HealthChecker()
    
    # Build config from environment
    config = {
        "mongo_url": os.getenv("MONGO_URL", "mongodb://localhost:27017"),
        "mongo_db_name": os.getenv("MONGO_DB_NAME", "qna_ai_admin"),
        "redis_url": os.getenv("REDIS_URL", "redis://localhost:6379"),
        "chromadb_url": os.getenv("CHROMADB_URL", "http://localhost:8050"),
        "llm_base_url": os.getenv("OPENAI_BASE_URL", "http://localhost:11434/v1"),
        "llm_model": os.getenv("OPENAI_MODEL", "llama3.2"),
    }
    
    if args.verbose:
        print("\n📋 Environment Configuration:")
        for key, value in config.items():
            print(f"  {key}: {value}")
    
    # Run all checks
    print("\n🏥 Running health checks...")
    print("-" * 60)
    
    health_status = await checker.run_all_checks(config)
    
    # Print summary
    print("\n" + "=" * 60)
    overall_status = health_status["status"]
    
    if overall_status == "healthy":
        print("✅ ALL SYSTEMS READY - You can start the server")
        print("\n   Starting the server:")
        print("   cd backend/apiServer && python server.py")
        return 0
    else:
        print(f"❌ SYSTEM NOT READY - {overall_status.upper()}")
        print("\n📋 Service Status:")
        
        unhealthy = []
        for service_name, service_info in health_status["services"].items():
            status = service_info["status"]
            required = service_info["required"]
            message = service_info["message"]
            
            icon = "✅" if status == "healthy" else "❌"
            required_tag = "[REQUIRED]" if required else "[OPTIONAL]"
            
            print(f"\n  {icon} {service_name} {required_tag}")
            print(f"     Status: {status}")
            if message:
                print(f"     Message: {message}")
            
            if status != "healthy" and required:
                unhealthy.append((service_name, message))
        
        # Provide helpful guidance
        print("\n" + "=" * 60)
        print("⚠️  REQUIRED SERVICES MISSING:")
        print("-" * 60)
        
        for service_name, message in unhealthy:
            print(f"\n❌ {service_name}")
            print(f"   Issue: {message}")
            
            # Provide specific fix instructions
            if service_name == "MongoDB":
                print("   Fix: Install MongoDB")
                print("   Option 1 (Docker): docker run -d -p 27017:27017 --name mongodb mongo:latest")
                print("   Option 2 (Brew):   brew install mongodb-community && brew services start mongodb-community")
                print("   Option 3 (Manual): https://docs.mongodb.com/manual/installation/")
            
            elif service_name == "Redis":
                print("   Fix: Install Redis")
                print("   Option 1 (Docker): docker run -d -p 6379:6379 --name redis redis:latest")
                print("   Option 2 (Brew):   brew install redis && brew services start redis")
                print("   Option 3 (Manual): https://redis.io/download")
            
            elif service_name == "ChromaDB":
                print("   Fix: Start ChromaDB")
                print("   Command: docker run -d -p 8050:8050 chromadb/chroma")
                print("   Note: ChromaDB requires Docker. Install Docker first if needed")
                print("   Docker: https://www.docker.com/products/docker-desktop")
            
            elif service_name == "LLM Service":
                print("   Fix: Start Ollama or configure OpenAI API")
                print("   Option 1 (Ollama):  ollama serve")
                print("   Option 2 (OpenAI): Set OPENAI_API_KEY and OPENAI_BASE_URL environment variables")
                print("   Ollama: https://ollama.ai")
        
        print("\n" + "=" * 60)
        print("📋 Quick Start Commands:")
        print("-" * 60)
        
        # Check what's missing and provide quick commands
        missing = [s for s, m in unhealthy]
        
        if "MongoDB" in missing and "Redis" in missing and "ChromaDB" in missing:
            print("\n# Start all services with Docker Compose:")
            print("cd backend/infrastructure")
            print("docker-compose up -d")
        else:
            print("\n# Start individual services:")
            if "MongoDB" in missing:
                print("docker run -d -p 27017:27017 --name mongodb mongo:latest")
            if "Redis" in missing:
                print("docker run -d -p 6379:6379 --name redis redis:latest")
            if "ChromaDB" in missing:
                print("docker run -d -p 8050:8050 chromadb/chroma")
            if "LLM Service" in missing:
                print("ollama serve")
        
        print("\n# Then run health check again:")
        print("python preflight_check.py")
        
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
