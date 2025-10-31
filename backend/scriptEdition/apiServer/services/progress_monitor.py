"""
Progress Monitor Service

Monitors progress events from the queue and broadcasts them via SSE.
This bridges the gap between queue-based worker communication and SSE client updates.
"""

import asyncio
import logging
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorDatabase, AsyncIOMotorCollection
from services.progress_service import (
    progress_manager, ProgressLevel,
    execution_queued, execution_running, execution_completed, execution_failed
)

logger = logging.getLogger("progress-monitor")


class ProgressMonitorService:
    """Monitors progress events from MongoDB and broadcasts via SSE"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.progress_events_collection: AsyncIOMotorCollection = db["progress_events"]
        self.running = False
        self.monitor_task: Optional[asyncio.Task] = None
        
    async def start(self):
        """Start monitoring progress events"""
        if self.running:
            logger.warning("Progress monitor already running")
            return
            
        self.running = True
        self.monitor_task = asyncio.create_task(self._monitor_loop())
        logger.info("✅ Progress monitor started")
        
    async def stop(self):
        """Stop monitoring progress events"""
        self.running = False
        if self.monitor_task:
            self.monitor_task.cancel()
            try:
                await self.monitor_task
            except asyncio.CancelledError:
                pass
        logger.info("✅ Progress monitor stopped")
        
    async def _monitor_loop(self):
        """Main monitoring loop"""
        try:
            logger.info("🔄 Progress monitor loop started")
            while self.running:
                try:
                    # Find unprocessed progress events
                    events = await self.progress_events_collection.find({
                        "processed": False
                    }).sort("timestamp", 1).limit(50).to_list(50)
                    
                    if events:
                        logger.info(f"📊 Found {len(events)} unprocessed progress events")
                    
                    for event in events:
                        await self._process_event(event)
                        
                    # Sleep for a short interval before checking again
                    await asyncio.sleep(0.5)  # Check every 500ms
                    
                except Exception as e:
                    logger.error(f"❌ Error in progress monitor loop: {e}")
                    await asyncio.sleep(5)  # Wait longer on error
                    
        except asyncio.CancelledError:
            logger.info("Progress monitor loop cancelled")
            raise
            
    async def _process_event(self, event: dict):
        """Process a single progress event and broadcast via SSE"""
        try:
            session_id = event.get("session_id")
            event_type = event.get("type")
            
            logger.info(f"🎯 Processing progress event: session={session_id}, type={event_type}, status={event.get('status')}")
            
            if not session_id:
                logger.warning(f"Progress event missing session_id: {event}")
                await self._mark_processed(event["_id"])
                return
                
            if event_type == "execution_status":
                await self._handle_execution_status(session_id, event)
            else:
                # Generic progress event
                await self._handle_generic_progress(session_id, event)
                
            # Mark event as processed
            await self._mark_processed(event["_id"])
            logger.info(f"✅ Successfully processed progress event for session {session_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to process progress event: {e}")
            # Still mark as processed to avoid infinite retry
            await self._mark_processed(event["_id"])
            
    async def _handle_execution_status(self, session_id: str, event: dict):
        """Handle execution status update events"""
        execution_id = event.get("execution_id")
        status = event.get("status")
        analysis_id = event.get("analysis_id")
        
        if not execution_id or not status:
            logger.warning(f"Invalid execution status event: {event}")
            return
            
        logger.info(f"📡 Broadcasting execution status {status} for {execution_id} via SSE")
        
        if status == "running":
            await execution_running(session_id, execution_id, analysis_id)
            logger.info(f"✅ Broadcast execution_running for {execution_id}")
        elif status == "completed":
            # Extract additional data for completion
            results = event.get("results")
            markdown = event.get("markdown")
            execution_time = event.get("execution_time")
            
            await execution_completed(
                session_id, execution_id, analysis_id,
                results=results,
                markdown=markdown,
                execution_time=execution_time
            )
            logger.info(f"✅ Broadcast execution_completed for {execution_id}")
        elif status == "failed":
            error_message = event.get("error")
            message = event.get("message", "")
            # Extract just the error part from the message
            if message.startswith("Analysis execution failed: "):
                error_message = message.replace("Analysis execution failed: ", "")
            elif message.startswith("Worker error: "):
                error_message = message.replace("Worker error: ", "")
                
            await execution_failed(
                session_id, execution_id,
                error_message=error_message,
                analysis_id=analysis_id
            )
            logger.info(f"✅ Broadcast execution_failed for {execution_id}")
        elif status == "queued":
            await execution_queued(session_id, execution_id, analysis_id)
            logger.info(f"✅ Broadcast execution_queued for {execution_id}")
        else:
            logger.warning(f"Unknown execution status: {status}")
            
    async def _handle_generic_progress(self, session_id: str, event: dict):
        """Handle generic progress events"""
        level_str = event.get("level", "info")
        message = event.get("message", "Progress update")
        
        # Convert level string to ProgressLevel enum
        try:
            level = ProgressLevel(level_str.lower())
        except ValueError:
            level = ProgressLevel.INFO
            
        # Extract optional fields
        step = event.get("step")
        total_steps = event.get("total_steps")
        details = {k: v for k, v in event.items() if k not in [
            "_id", "session_id", "timestamp", "processed", "type", "level", "message", "step", "total_steps"
        ]}
        
        await progress_manager.emit(
            session_id=session_id,
            level=level,
            message=message,
            step=step,
            total_steps=total_steps,
            details=details
        )
        
    async def _mark_processed(self, event_id):
        """Mark event as processed"""
        try:
            await self.progress_events_collection.update_one(
                {"_id": event_id},
                {"$set": {"processed": True}}
            )
        except Exception as e:
            logger.error(f"❌ Failed to mark event as processed: {e}")


# Global instance
_progress_monitor: Optional[ProgressMonitorService] = None


def get_progress_monitor() -> Optional[ProgressMonitorService]:
    """Get the global progress monitor instance"""
    return _progress_monitor


async def initialize_progress_monitor(db: AsyncIOMotorDatabase):
    """Initialize the global progress monitor"""
    global _progress_monitor
    if _progress_monitor is None:
        _progress_monitor = ProgressMonitorService(db)
        await _progress_monitor.start()
        logger.info("✅ Global progress monitor initialized and started")
    else:
        logger.warning("Progress monitor already initialized")


async def cleanup_progress_monitor():
    """Cleanup the global progress monitor"""
    global _progress_monitor
    if _progress_monitor:
        await _progress_monitor.stop()
        _progress_monitor = None
        logger.info("✅ Global progress monitor cleaned up")