"""
Audit Service - Handles execution logging and audit trails
"""

import logging
from typing import Optional, List, Dict, Any
from datetime import datetime

from db.repositories import RepositoryManager
from db.schemas import ExecutionModel

logger = logging.getLogger("audit-service")


class AuditService:
    """Service for logging executions and audit trails"""
    
    def __init__(self, repo_manager: RepositoryManager):
        self.repo = repo_manager
        self.execution_repo = repo_manager.execution
        self.logger = logger
    
    async def log_execution_start(
        self,
        user_id: str,
        session_id: str,
        message_id: str,
        question: str,
        script: str,
        parameters: Dict[str, Any],
        mcp_calls: List[str],
    ) -> str:
        """Log start of script execution"""
        try:
            execution_id = await self.execution_repo.log_execution(
                user_id=user_id,
                session_id=session_id,
                message_id=message_id,
                question=question,
                script=script,
                parameters=parameters,
                mcp_calls=mcp_calls,
            )
            
            self.logger.info(f"✓ Logged execution start: {execution_id}")
            return execution_id
        except Exception as e:
            self.logger.error(f"✗ Failed to log execution: {e}")
            raise
    
    async def log_execution_complete(
        self,
        execution_id: str,
        result: Dict[str, Any],
        execution_time_ms: int,
        success: bool = True,
        error: Optional[str] = None,
    ) -> bool:
        """Log completion of script execution"""
        try:
            result = await self.execution_repo.complete_execution(
                execution_id=execution_id,
                result=result,
                execution_time_ms=execution_time_ms,
                success=success,
                error=error,
            )
            
            status = "success" if success else "failed"
            self.logger.info(f"✓ Logged execution complete ({status}): {execution_id}")
            return result
        except Exception as e:
            self.logger.error(f"✗ Failed to log execution completion: {e}")
            return False
    
    async def get_execution_history(
        self,
        session_id: str,
        limit: int = 100
    ) -> List[ExecutionModel]:
        """Get execution history for session"""
        try:
            executions = await self.execution_repo.get_execution_history(
                session_id=session_id
            )
            self.logger.info(f"✓ Retrieved {len(executions)} executions for session")
            return executions
        except Exception as e:
            self.logger.error(f"✗ Failed to get execution history: {e}")
            return []
    
    async def get_user_execution_history(
        self,
        user_id: str,
        limit: int = 100
    ) -> List[ExecutionModel]:
        """Get execution history for user"""
        try:
            executions = await self.repo.db.db.executions.find(
                {"user_id": user_id}
            ).sort("started_at", -1).limit(limit).to_list(limit)
            
            result = [ExecutionModel(**doc) for doc in executions]
            self.logger.info(f"✓ Retrieved {len(result)} executions for user")
            return result
        except Exception as e:
            self.logger.error(f"✗ Failed to get user execution history: {e}")
            return []
