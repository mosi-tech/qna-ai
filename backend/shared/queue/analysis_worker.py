#!/usr/bin/env python3
"""
Analysis Queue Worker

Polls the analysis queue for pending analyses and processes them.
Extracts analysis logic from the API server to run asynchronously.
"""

import asyncio
import logging
import uuid
import sys
import os
from shared.queue.worker_context import set_context
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Add shared modules to path
from .analysis_queue import AnalysisQueueInterface
from .base_worker import BaseQueueWorker
from .progress_message import analysis_status_message, ProgressStatus
from ..services.progress_service import send_progress_event
from ..analyze import AnalysisService
from ..analyze import AnalysisPersistenceService
from ..analyze import ReuseEvaluator as ReuseEvaluatorService
from ..analyze import CodePromptBuilderService
# Import required services and pipeline
from ..analyze.services.analysis_pipeline import create_analysis_pipeline
from ..analyze.services.verification.verification_service import StandaloneVerificationService

from ..services.search import SearchService
from ..services.chat_service import ChatHistoryService
from ..services.cache_service import CacheService
from ..services.audit_service import AuditService
from ..db import RepositoryManager, MongoDBClient
from shared.services.session_manager import SessionManager

logger = logging.getLogger(__name__)

class AnalysisQueueWorker(BaseQueueWorker):
    """Worker that polls analysis queue and processes analysis requests"""
    
    def __init__(
        self, 
        queue: AnalysisQueueInterface,
        worker_id: Optional[str] = None,
        poll_interval: Optional[int] = None,
        max_concurrent_analyses: Optional[int] = None,
        max_retries: Optional[int] = None,
        retry_delay: Optional[int] = None
    ):
        # Configure settings from environment variables with fallbacks
        self.poll_interval = poll_interval or int(os.getenv("ANALYSIS_WORKER_POLL_INTERVAL", "5"))
        self.max_concurrent_analyses = max_concurrent_analyses or int(os.getenv("ANALYSIS_WORKER_MAX_CONCURRENT", "2"))
        self.max_retries = max_retries or int(os.getenv("ANALYSIS_WORKER_MAX_RETRIES", "3"))
        self.retry_delay = retry_delay or int(os.getenv("ANALYSIS_WORKER_RETRY_DELAY", "60"))
        
        super().__init__(
            queue=queue,
            worker_id=worker_id,
            poll_interval=self.poll_interval,
            max_concurrent_items=self.max_concurrent_analyses,
            worker_type="analysis_worker"
        )
        self.analysis_pipeline = None
        
        logger.info(f"🔧 Analysis Worker Config: poll_interval={self.poll_interval}s, "
                   f"max_concurrent={self.max_concurrent_analyses}, max_retries={self.max_retries}, "
                   f"retry_delay={self.retry_delay}s")
        
        # Log environment variable usage
        env_vars_used = [
            ("ANALYSIS_WORKER_POLL_INTERVAL", self.poll_interval),
            ("ANALYSIS_WORKER_MAX_CONCURRENT", self.max_concurrent_analyses), 
            ("ANALYSIS_WORKER_MAX_RETRIES", self.max_retries),
            ("ANALYSIS_WORKER_RETRY_DELAY", self.retry_delay)
        ]
        for env_var, value in env_vars_used:
            logger.debug(f"🔧 {env_var}={value} (from env: {os.getenv(env_var, 'NOT_SET')})")
    
    async def _initialize_services(self):
        """Initialize the full analysis pipeline with all required services"""
        try:
            logger.info("🔧 Initializing analysis pipeline...")

            # Initialize database connection
            db_client = MongoDBClient()
            await db_client.connect()  # Important: Connect first
            repo_manager = RepositoryManager(db_client)
            await repo_manager.initialize()

            # Reclaim any jobs that were stuck in 'processing' state due to a
            # previous worker crash. Must run before this worker starts polling.
            await self._reclaim_stale_jobs(db_client.db)
            
            # Create all required services
            analysis_service = AnalysisService()
            search_service = SearchService()
            chat_history_service = ChatHistoryService(repo_manager)
            cache_service = CacheService(repo_manager)
            analysis_persistence_service = AnalysisPersistenceService(repo_manager)
            reuse_evaluator = ReuseEvaluatorService()
            code_prompt_builder = CodePromptBuilderService()
            audit_service = AuditService(repo_manager)
            
            # Initialize verification service for reuse verification (Issue #117)
            verification_service = self._initialize_verification_service()
            
            # Create session manager for dialogue factory with Redis support
            try:
                from shared.services.redis_client import get_redis_client
                redis_client = await get_redis_client()
            except Exception:
                redis_client = None
            
            session_manager = SessionManager(
                chat_history_service=chat_history_service,
                redis_client=redis_client
            )
            
            # Create the complete analysis pipeline
            self.analysis_pipeline = create_analysis_pipeline(
                analysis_service=analysis_service,
                search_service=search_service,
                chat_history_service=chat_history_service,
                cache_service=cache_service,
                analysis_persistence_service=analysis_persistence_service,
                reuse_evaluator=reuse_evaluator,
                code_prompt_builder=code_prompt_builder,
                session_manager=session_manager,
                audit_service=audit_service,
                verification_service=verification_service  # Add verification service (Issue #117)
            )
            
            logger.info("✅ Analysis pipeline fully initialized with all services")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize analysis pipeline: {e}")
            raise  # Re-raise to stop worker startup
    
    async def _reclaim_stale_jobs(self, db, stale_after_minutes: int = 10):
        """
        On startup, reset any analysis jobs that were stuck in 'processing'
        state (left behind by a previous worker crash).

        Also releases the session locks held by those stale jobs so users
        are not locked out.
        """
        try:
            cutoff = datetime.utcnow() - timedelta(minutes=stale_after_minutes)
            queue_col = db.analysis_queue
            locks_col = db.session_locks

            # Find stale jobs before resetting so we can collect session_ids
            stale_cursor = queue_col.find({
                "status": "processing",
                "claimed_at": {"$lt": cutoff}
            })
            stale_jobs = await stale_cursor.to_list(length=100)

            if not stale_jobs:
                logger.info("✅ No stale analysis jobs found on startup")
                return

            stale_ids = [j["_id"] for j in stale_jobs]
            stale_sessions = [j["session_id"] for j in stale_jobs if j.get("session_id")]

            # Reset jobs to pending
            result = await queue_col.update_many(
                {"_id": {"$in": stale_ids}},
                {
                    "$set": {
                        "status": "pending",
                        "worker_id": None,
                        "claimed_at": None,
                        "updated_at": datetime.utcnow(),
                    },
                    "$inc": {"retry_count": 1}
                }
            )
            logger.warning(
                f"⚠️ Reclaimed {result.modified_count} stale analysis job(s) "
                f"(stuck >{ stale_after_minutes}min): "
                f"{[j.get('job_id') for j in stale_jobs]}"
            )

            # Release the session locks held by those stale jobs
            if stale_sessions:
                lock_result = await locks_col.delete_many(
                    {"session_id": {"$in": stale_sessions}}
                )
                if lock_result.deleted_count:
                    logger.warning(
                        f"🔓 Released {lock_result.deleted_count} stale session lock(s) "
                        f"for sessions: {stale_sessions}"
                    )

        except Exception as e:
            # Non-fatal — log and continue startup
            logger.error(f"❌ Failed to reclaim stale jobs on startup: {e}")

    def _initialize_verification_service(self) -> Optional[StandaloneVerificationService]:
        """
        Initialize verification service for reuse verification (GitHub Issue #117)
        
        Returns:
            StandaloneVerificationService instance or None if initialization fails
        """
        try:
            # Use a simple verification prompt template
            verification_prompt_template = "Before we proceed, I need to verify something important:\n\n**Question**: {question}\n\nPlease check if the script correctly answers the question."
            
            verification_service = StandaloneVerificationService(verification_prompt_template)
            
            # Check if any verification models are available
            available_services = len([s for s in verification_service.llm_services if s is not None])
            total_services = len(verification_service.llm_services)
            
            if available_services > 0:
                configs_summary = [f"{c['provider']}/{c['model']}" for c in verification_service.verification_configs]
                logger.info(f"✅ Verification service initialized for reuse verification: {available_services}/{total_services} services available")
                logger.debug(f"Verification configs: {configs_summary}")
                return verification_service
            else:
                logger.warning(f"⚠️ Verification service initialized but no LLM services available - reuse verification will be skipped")
                return None
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize verification service: {e}")
            return None  # Return None so pipeline can still work without verification
    
    async def _dequeue_item(self):
        """Dequeue an analysis from the queue"""
        return await self.queue.dequeue_analysis(self.worker_id)
    
    async def _process_item(self, item: Dict[str, Any]):
        """Process a single analysis (renamed from _process_analysis)"""
        return await self._process_analysis(item)
    
    async def _process_analysis(self, job: Dict[str, Any]):
        """Process a single analysis job using the fully initialized analysis pipeline"""
        job_id = job.get("job_id")
        session_id = job.get("session_id")
        message_id = job.get("message_id")
        user_question = job.get("user_question")
        
        try:
            logger.info(f"🔨 Processing analysis: {job_id}")
            
            # Check if pipeline is initialized
            if not self.analysis_pipeline:
                raise ValueError("Analysis pipeline not initialized")
            
            # Send SSE update when analysis starts
            if session_id:
                await send_progress_event(session_id, {
                    "message": "Analysis started",
                    "message_id": message_id,
                    "status": ProgressStatus.RUNNING
                })
                logger.info(f"📡 Sent SSE analysis start for job: {job_id}")
            
            # Prepare request data for the analysis pipeline
            request_data = {
                "question": user_question,
                "session_id": session_id,
                "message_id": message_id,  # Pass message_id for async logging
                "user_id": "worker",
                "enable_caching": True,
                "auto_expand": True,
                "model": None  # Use default model
            }
            
            # Run the complete analysis pipeline
            await send_progress_event(session_id, {
                "type": "analysis_progress",
                "job_id": job_id,
                "message_id": message_id,
                "status": "running",
                "message": "Running analysis pipeline",
                "level": "info",
                "log_to_message": True if message_id else False
            })
            logger.info(f"🤖 Running analysis pipeline for: {user_question[:100]}...")

            # Set worker context so pipeline step events (send_analysis_progress)
            # can resolve session_id and message_id without being passed explicitly.
            set_context(session_id=session_id, message_id=message_id)

            pipeline_result = await self.analysis_pipeline.analyze_question(request_data)
            
            # Check if analysis succeeded
            if not getattr(pipeline_result, "success", True):
                error_msg = getattr(pipeline_result, "error", "Analysis pipeline failed")
                internal_error = getattr(pipeline_result, "internal_error", "Unknown pipeline error")
                await send_progress_event(session_id, {
                    "type": "analysis_progress",
                    "job_id": job_id,
                    "message_id": message_id,
                    "status": "failed",
                    "message": f"Analysis failed: {error_msg}",
                    "level": "error",
                    "log_to_message": True if message_id else False,
                    "error": error_msg,
                    "internal_error": internal_error
                })
                # Knock: tell frontend the message is ready to fetch
                await send_progress_event(session_id, {
                    "type": "message_ready",
                    "message_id": message_id,
                    "status": "failed",
                    "response_type": None,
                    "error": error_msg,
                })
                raise ValueError(f"{error_msg}: {internal_error}")
            
            # Extract results from pipeline response
            pipeline_data = getattr(pipeline_result, "data", {})
            response_type = pipeline_data.get("response_type", "unknown") if isinstance(pipeline_data, dict) else "unknown"
            
            
            # Build final result for queue
            result = {
                "analysis_data": pipeline_data,
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat(),
                "response_type": response_type,
                "provider": getattr(pipeline_result, "provider", "pipeline"),
                "processing_time": getattr(pipeline_result, "processing_time", 0),
                "analysis_id": pipeline_data.get("analysis_id") if isinstance(pipeline_data, dict) else None,
                "execution_id": pipeline_data.get("execution_id") if isinstance(pipeline_data, dict) else None,
                "message_id": message_id,
                "content": pipeline_data.get("content", "Analysis completed successfully")
            }
            
            # Determine actual status based on response type from pipeline
            actual_status = "completed" if response_type in ["needs_clarification", "needs_confirmation"] else "pending"
            
            await send_progress_event(session_id, {
                "type": "analysis_progress",
                "job_id": job_id,
                "message_id": message_id,
                "status": actual_status,
                "message": "Analysis completed successfully",
                "level": "success",
                "log_to_message": True if message_id else False,
                "response_type": response_type,
                "analysis_id": result.get("analysis_id"),
                "execution_id": result.get("execution_id")
            })
            # Knock: tell frontend the message is ready to fetch from DB
            await send_progress_event(session_id, {
                "type": "message_ready",
                "message_id": message_id,
                "status": "completed",
                "response_type": response_type,
                "analysis_id": result.get("analysis_id"),
                "execution_id": result.get("execution_id"),
            })

            await self.queue.ack_analysis(job_id, result)
            logger.info(f"✅ Completed analysis: {job_id} (type: {response_type})")
            
        except Exception as e:
            logger.error(f"❌ Error processing analysis {job_id}: {e}")
            await send_progress_event(session_id, {
                "type": "analysis_progress",
                "job_id": job_id,
                "message_id": message_id,
                "status": "failed",
                "message": f"Analysis failed: {str(e)}",
                "level": "error",
                "log_to_message": True if message_id else False,
                "error": str(e)
            })
            # Knock: tell frontend the message is ready to fetch from DB
            await send_progress_event(session_id, {
                "type": "message_ready",
                "message_id": message_id,
                "status": "failed",
                "response_type": None,
                "error": str(e),
            })

            # Use configurable retry logic
            should_retry = hasattr(self, 'max_retries') and self.max_retries > 0
            await self.queue.nack_analysis(job_id, str(e), retry=should_retry)
    

# Worker entry point for standalone execution
async def main():
    """Main entry point for analysis worker"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    logger.info("🚀 Starting Analysis Queue Worker...")
    
    try:
        # Initialize database connection and queue
        logger.info("🔧 Initializing database and queue...")
        
        # Import required components for initialization
        from .analysis_queue import initialize_analysis_queue, get_analysis_queue
        from .progress_event_queue import initialize_progress_event_queue, get_progress_event_queue
        
        # Import database components
        from shared.db import MongoDBClient, RepositoryManager
        
        # Initialize MongoDB connection for the queue
        db_client = MongoDBClient()
        await db_client.connect()  # Connect first
        repo_manager = RepositoryManager(db_client)
        await repo_manager.initialize()
        db = db_client.db  # Use the database from client, not repo_manager
        
        # Initialize progress event queue first
        initialize_progress_event_queue(db)
        
        # Initialize analysis queue with database and progress event queue
        initialize_analysis_queue(db)
        queue = get_analysis_queue()
        
        logger.info("✅ Database and queue initialized successfully")
        
        # Create and start worker
        worker = AnalysisQueueWorker(queue)
        
        try:
            await worker.start()
        finally:
            # Cleanup database connection
            try:
                if hasattr(db_client, 'client') and db_client.client:
                    db_client.client.close()
                    logger.info("✅ Database connection closed")
            except Exception as cleanup_error:
                logger.warning(f"⚠️ Error closing database connection: {cleanup_error}")
        
    except KeyboardInterrupt:
        logger.info("🛑 Analysis worker stopped by user")
    except Exception as e:
        logger.error(f"❌ Analysis worker failed: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())