"""
Analysis Persistence Service - Handles analysis storage and retrieval
"""

import logging
from typing import Optional, List, Dict, Any

from db.repositories import RepositoryManager
from db.schemas import AnalysisModel

logger = logging.getLogger("analysis-persistence-service")


class AnalysisPersistenceService:
    """Service for managing analysis persistence and reusability"""
    
    def __init__(self, repo_manager: RepositoryManager):
        self.repo = repo_manager
        self.analysis_repo = repo_manager.analysis
        self.logger = logger
    
    async def create_analysis(
        self,
        user_id: str,
        title: str,
        description: str,
        result: Dict[str, Any],
        parameters: Dict[str, Any],
        mcp_calls: List[str],
        category: str,
        script: Optional[str] = None,
        execution_time_ms: int = 0,
        data_sources: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
    ) -> str:
        """Create and save a new analysis as reusable template"""
        try:
            analysis_id = await self.analysis_repo.create_and_save_analysis(
                user_id=user_id,
                title=title,
                description=description,
                result=result,
                parameters=parameters,
                mcp_calls=mcp_calls,
                category=category,
                script=script,
                execution_time_ms=execution_time_ms,
                data_sources=data_sources,
                tags=tags,
            )
            
            self.logger.info(f"✓ Created analysis: {analysis_id}")
            return analysis_id
        except Exception as e:
            self.logger.error(f"✗ Failed to create analysis: {e}")
            raise
    
    async def get_analysis(self, analysis_id: str) -> Optional[AnalysisModel]:
        """Get analysis by ID"""
        try:
            analysis = await self.repo.db.get_analysis(analysis_id)
            return analysis
        except Exception as e:
            self.logger.error(f"✗ Failed to get analysis: {e}")
            return None
    
    async def get_similar_analyses(
        self,
        user_id: str,
        category: str,
        limit: int = 10
    ) -> List[AnalysisModel]:
        """Get similar analyses in same category"""
        try:
            analyses = await self.analysis_repo.get_similar_analyses(
                user_id=user_id,
                category=category,
                limit=limit
            )
            self.logger.info(f"✓ Retrieved {len(analyses)} similar analyses")
            return analyses
        except Exception as e:
            self.logger.error(f"✗ Failed to get similar analyses: {e}")
            return []
    
    async def get_reusable_analyses(self, user_id: str) -> List[AnalysisModel]:
        """Get all analyses that can be reused as templates"""
        try:
            analyses = await self.analysis_repo.get_reusable_analyses(user_id)
            self.logger.info(f"✓ Retrieved {len(analyses)} reusable analyses")
            return analyses
        except Exception as e:
            self.logger.error(f"✗ Failed to get reusable analyses: {e}")
            return []
    
    async def can_reuse_analysis(
        self,
        analysis_id: str,
        new_question: str
    ) -> bool:
        """Check if analysis can be reused for new question"""
        try:
            can_reuse = await self.analysis_repo.can_reuse_analysis(
                analysis_id=analysis_id,
                new_question=new_question
            )
            
            if can_reuse:
                self.logger.info(f"✓ Can reuse analysis: {analysis_id}")
            else:
                self.logger.info(f"✗ Cannot reuse analysis: {analysis_id}")
            
            return can_reuse
        except Exception as e:
            self.logger.error(f"✗ Failed to check reuse: {e}")
            return False
    
    async def search_analyses(
        self,
        user_id: str,
        search_text: str,
        limit: int = 50
    ) -> List[AnalysisModel]:
        """Search analyses by title/description"""
        try:
            analyses = await self.repo.db.search_analyses(
                user_id=user_id,
                search_text=search_text,
                limit=limit
            )
            self.logger.info(f"✓ Found {len(analyses)} matching analyses")
            return analyses
        except Exception as e:
            self.logger.error(f"✗ Failed to search analyses: {e}")
            return []
    
    async def mark_analysis_used(self, analysis_id: str) -> bool:
        """Update last_used_at timestamp"""
        try:
            result = await self.repo.db.mark_analysis_used(analysis_id)
            self.logger.info(f"✓ Marked analysis as used: {analysis_id}")
            return result
        except Exception as e:
            self.logger.error(f"✗ Failed to mark analysis as used: {e}")
            return False
