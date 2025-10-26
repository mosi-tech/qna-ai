"""
Cache Service - Handles query result caching for performance
"""

import logging
from typing import Optional, Dict, Any

from db.repositories import RepositoryManager

logger = logging.getLogger("cache-service")


class CacheService:
    """Service for caching analysis results"""
    
    def __init__(self, repo_manager: RepositoryManager):
        self.repo = repo_manager
        self.cache_repo = repo_manager.cache
        self.logger = logger
    
    async def get_cached_result(
        self,
        question: str,
        parameters: Dict[str, Any],
    ) -> Optional[Dict[str, Any]]:
        """Get cached analysis result if available"""
        try:
            result = await self.cache_repo.get_cached_analysis(question, parameters)
            
            if result:
                self.logger.info("✓ Cache hit - returning cached result")
                return result
            else:
                self.logger.info("✗ Cache miss - will generate new analysis")
                return None
                
        except Exception as e:
            self.logger.warning(f"⚠ Cache retrieval failed: {e}")
            return None  # Don't fail request on cache error
    
    async def cache_analysis_result(
        self,
        question: str,
        parameters: Dict[str, Any],
        result: Dict[str, Any],
        analysis_id: Optional[str] = None,
        ttl_hours: int = 24,
    ) -> Optional[str]:
        """Cache an analysis result"""
        try:
            cache_id = await self.cache_repo.cache_analysis(
                question=question,
                parameters=parameters,
                result=result,
                analysis_id=analysis_id,
                ttl_hours=ttl_hours,
            )
            
            self.logger.info(f"✓ Cached analysis result: {cache_id}")
            return cache_id
            
        except Exception as e:
            self.logger.error(f"✗ Failed to cache result: {e}")
            # Don't fail the request on cache write error
            return None
    
    async def invalidate_analysis_cache(self, analysis_id: str) -> None:
        """Invalidate cache for specific analysis"""
        try:
            await self.cache_repo.invalidate_analysis_cache(analysis_id)
            self.logger.info(f"✓ Invalidated cache for analysis: {analysis_id}")
        except Exception as e:
            self.logger.error(f"✗ Failed to invalidate cache: {e}")
    
    async def get_cached_message(
        self,
        question: str,
        user_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get cached assistant message for a question (user_id for cross-session reuse)"""
        try:
            # Cache key includes user_id not session_id so it can be reused across sessions
            parameters = {"user_id": user_id}
            result = await self.cache_repo.get_cached_analysis(question, parameters)
            
            if result and "message_data" in result:
                self.logger.info("✓ Cache hit - returning cached message")
                return result["message_data"]
            else:
                self.logger.info("✗ Cache miss - will generate new analysis and message")
                return None
                
        except Exception as e:
            self.logger.warning(f"⚠ Message cache retrieval failed: {e}")
            return None
    
    async def cache_assistant_message(
        self,
        question: str,
        user_id: str,
        message_data: Dict[str, Any],
        ttl_hours: int = 24,
    ) -> Optional[str]:
        """Cache an assistant message for future reuse"""
        try:
            # Cache the message with user_id so it can be reused across sessions
            parameters = {"user_id": user_id}
            cache_id = await self.cache_repo.cache_analysis(
                question=question,
                parameters=parameters,
                result={"message_data": message_data},
                analysis_id=message_data.get("analysis_id"),
                ttl_hours=ttl_hours,
            )
            
            self.logger.info(f"✓ Cached assistant message: {cache_id}")
            return cache_id
            
        except Exception as e:
            self.logger.error(f"✗ Failed to cache message: {e}")
            return None
