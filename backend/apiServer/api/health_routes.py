"""
Health Check Routes

Provides health check endpoints for monitoring service readiness.
"""

from fastapi import APIRouter, HTTPException
from shared.health.health_checker import HealthChecker
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/health", tags=["health"])

# Global health checker instance
_health_checker: HealthChecker = None


async def initialize_health_checker(config: dict = None):
    """Initialize the health checker with current config"""
    global _health_checker
    _health_checker = HealthChecker()
    await _health_checker.run_all_checks(config)
    return _health_checker


@router.get("/status")
async def get_health_status():
    """Get current health status of all services"""
    if not _health_checker:
        raise HTTPException(status_code=503, detail="Health checker not initialized")
    
    return _health_checker.to_dict()


@router.get("/ready")
async def readiness_check():
    """Readiness check - returns 200 only if system is ready for requests"""
    if not _health_checker:
        raise HTTPException(status_code=503, detail="Health checker not initialized")
    
    if not _health_checker.is_ready():
        status = _health_checker.to_dict()
        raise HTTPException(status_code=503, detail=f"Service not ready: {status}")
    
    return {"ready": True, "status": "all systems operational"}


@router.get("/live")
async def liveness_check():
    """Liveness check - returns 200 if API is running (not necessarily ready)"""
    return {"alive": True}
