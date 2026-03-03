#!/usr/bin/env python3
"""
Comprehensive Health Check System

Validates all required services and dependencies before API starts serving requests.
"""

import asyncio
import logging
from typing import Dict, Any, List
from dataclasses import dataclass, asdict
from enum import Enum
import aiohttp
import motor.motor_asyncio

logger = logging.getLogger("health-checker")


class HealthStatus(str, Enum):
    """Health check status enumeration"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    DEGRADED = "degraded"
    UNKNOWN = "unknown"


@dataclass
class ServiceHealth:
    """Individual service health status"""
    name: str
    status: HealthStatus
    message: str
    latency_ms: float = 0.0
    required: bool = True  # If false, service is optional


class HealthChecker:
    """Comprehensive health checker for all services"""
    
    def __init__(self):
        self.services: Dict[str, ServiceHealth] = {}
        self.overall_status = HealthStatus.UNKNOWN
    
    async def check_mongodb(self, mongo_url: str = "mongodb://localhost:27017", db_name: str = "qna_ai_admin") -> ServiceHealth:
        """Check MongoDB connectivity"""
        try:
            import time
            start = time.time()
            
            # Use the correct Motor class name
            client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
            await client.admin.command('ping')
            
            # Check if database exists
            db = client[db_name]
            await db.command('ping')
            
            latency = (time.time() - start) * 1000
            
            return ServiceHealth(
                name="MongoDB",
                status=HealthStatus.HEALTHY,
                message=f"Connected to {db_name}",
                latency_ms=latency,
                required=True
            )
        except Exception as e:
            return ServiceHealth(
                name="MongoDB",
                status=HealthStatus.UNHEALTHY,
                message=f"Connection failed: {str(e)}",
                required=True
            )
    
    async def check_redis(self, redis_url: str = "redis://localhost:6379") -> ServiceHealth:
        """Check Redis connectivity"""
        try:
            import time
            import redis.asyncio
            
            start = time.time()
            
            redis_client = await redis.asyncio.from_url(redis_url)
            result = await redis_client.ping()
            
            latency = (time.time() - start) * 1000
            
            await redis_client.close()
            
            return ServiceHealth(
                name="Redis",
                status=HealthStatus.HEALTHY,
                message="Cache connected",
                latency_ms=latency,
                required=True
            )
        except Exception as e:
            return ServiceHealth(
                name="Redis",
                status=HealthStatus.UNHEALTHY,
                message=f"Connection failed: {str(e)}",
                required=True
            )
    
    async def check_chromadb(self, chromadb_url: str = "http://localhost:8050") -> ServiceHealth:
        """Check ChromaDB connectivity"""
        try:
            import time
            
            start = time.time()
            
            async with aiohttp.ClientSession() as session:
                # Try v2 API first (latest), fall back to checking if port responds
                async with session.get(f"{chromadb_url}/docs", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    # /docs redirects (303) if server is running, that's fine
                    if resp.status in [200, 303]:
                        latency = (time.time() - start) * 1000
                        return ServiceHealth(
                            name="ChromaDB",
                            status=HealthStatus.HEALTHY,
                            message="Vector DB connected",
                            latency_ms=latency,
                            required=True  # Required for analysis pipeline
                        )
                    else:
                        return ServiceHealth(
                            name="ChromaDB",
                            status=HealthStatus.UNHEALTHY,
                            message=f"Unexpected status: {resp.status}",
                            required=True
                        )
        except asyncio.TimeoutError:
            return ServiceHealth(
                name="ChromaDB",
                status=HealthStatus.UNHEALTHY,
                message="Connection timeout - make sure ChromaDB is running on port 8050",
                required=True
            )
        except Exception as e:
            return ServiceHealth(
                name="ChromaDB",
                status=HealthStatus.UNHEALTHY,
                message=f"Connection failed: {str(e)}",
                required=True
            )
    
    async def check_llm_service(self, base_url: str = "http://localhost:11434/v1", model: str = "llama3.2") -> ServiceHealth:
        """Check LLM service (Ollama or OpenAI-compatible)"""
        try:
            import time
            
            start = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{base_url}/models", timeout=aiohttp.ClientTimeout(total=5)) as resp:
                    if resp.status == 200:
                        latency = (time.time() - start) * 1000
                        data = await resp.json()
                        return ServiceHealth(
                            name="LLM Service",
                            status=HealthStatus.HEALTHY,
                            message=f"Connected ({data.get('object', 'unknown')})",
                            latency_ms=latency,
                            required=True
                        )
                    else:
                        return ServiceHealth(
                            name="LLM Service",
                            status=HealthStatus.UNHEALTHY,
                            message=f"Unexpected status: {resp.status}",
                            required=True
                        )
        except asyncio.TimeoutError:
            return ServiceHealth(
                name="LLM Service",
                status=HealthStatus.UNHEALTHY,
                message="Connection timeout - make sure LLM service is running",
                required=True
            )
        except Exception as e:
            return ServiceHealth(
                name="LLM Service",
                status=HealthStatus.UNHEALTHY,
                message=f"Connection failed: {str(e)}",
                required=True
            )
    
    async def check_analysis_worker(self, mongo_url: str = "mongodb://localhost:27017", db_name: str = "qna_ai_admin") -> ServiceHealth:
        """Check if analysis worker process is running by checking MongoDB activity"""
        try:
            # Use the correct Motor class name
            client = motor.motor_asyncio.AsyncIOMotorClient(mongo_url)
            db = client[db_name]
            
            # Check if any worker claims exist in progress
            worker_claims = await db.worker_claims.count_documents({"status": "active"})
            
            # This is just informational - worker might not always be active
            message = f"Worker claims found" if worker_claims > 0 else "No active workers (may be idle)"
            
            return ServiceHealth(
                name="Analysis Worker",
                status=HealthStatus.HEALTHY if worker_claims >= 0 else HealthStatus.DEGRADED,
                message=message,
                required=False  # Optional - worker starts on demand
            )
        except Exception as e:
            return ServiceHealth(
                name="Analysis Worker",
                status=HealthStatus.UNKNOWN,
                message=f"Could not check: {str(e)}",
                required=False
            )
    
    async def run_all_checks(self, config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Run all health checks in parallel"""
        if config is None:
            config = {}
        
        logger.info("🏥 Starting comprehensive health checks...")
        
        # Run all checks in parallel
        checks = [
            self.check_mongodb(
                config.get("mongo_url", "mongodb://localhost:27017"),
                config.get("mongo_db_name", "qna_ai_admin")
            ),
            self.check_redis(config.get("redis_url", "redis://localhost:6379")),
            self.check_chromadb(config.get("chromadb_url", "http://localhost:8050")),
            self.check_llm_service(
                config.get("llm_base_url", "http://localhost:11434/v1"),
                config.get("llm_model", "llama3.2")
            ),
            self.check_analysis_worker(
                config.get("mongo_url", "mongodb://localhost:27017"),
                config.get("mongo_db_name", "qna_ai_admin")
            ),
        ]
        
        results = await asyncio.gather(*checks)
        
        # Process results
        self.services = {s.name: s for s in results}
        
        # Determine overall status
        required_healthy = all(
            s.status == HealthStatus.HEALTHY 
            for s in results 
            if s.required
        )
        
        if required_healthy:
            self.overall_status = HealthStatus.HEALTHY
        else:
            unhealthy_services = [s.name for s in results if s.required and s.status != HealthStatus.HEALTHY]
            logger.error(f"❌ Required services unhealthy: {', '.join(unhealthy_services)}")
            self.overall_status = HealthStatus.UNHEALTHY
        
        # Log results
        for service in results:
            icon = "✅" if service.status == HealthStatus.HEALTHY else "❌" if service.status == HealthStatus.UNHEALTHY else "⚠️"
            latency_str = f" ({service.latency_ms:.1f}ms)" if service.latency_ms > 0 else ""
            required_str = " [REQUIRED]" if service.required else " [OPTIONAL]"
            logger.info(f"{icon} {service.name}: {service.status.value}{latency_str}{required_str}")
            if service.message:
                logger.info(f"   └─ {service.message}")
        
        return self.to_dict()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API response"""
        return {
            "status": self.overall_status.value,
            "services": {
                name: {
                    "status": service.status.value,
                    "message": service.message,
                    "latency_ms": service.latency_ms,
                    "required": service.required
                }
                for name, service in self.services.items()
            }
        }
    
    def is_ready(self) -> bool:
        """Check if system is ready to accept requests"""
        if not self.services:
            return False
        
        required_services = [s for s in self.services.values() if s.required]
        return all(s.status == HealthStatus.HEALTHY for s in required_services)
