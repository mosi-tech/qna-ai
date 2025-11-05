"""
Message Status Constants

Tracks the lifecycle of analysis messages from creation through completion.
"""

class MessageStatus:
    """Constants for message status tracking throughout analysis lifecycle"""
    
    # Initial states
    PENDING = "pending"                    # Message created, analysis not started
    ANALYSIS_STARTED = "analysis_started" # Analysis pipeline started
    
    # Analysis completion states
    ANALYSIS_COMPLETED = "analysis_completed"  # Analysis generated, ready for execution
    ANALYSIS_FAILED = "analysis_failed"       # Analysis pipeline failed
    
    # Execution states  
    EXECUTION_QUEUED = "execution_queued"     # Execution submitted to queue
    EXECUTION_RUNNING = "execution_running"   # Execution in progress
    EXECUTION_COMPLETED = "execution_completed" # Execution finished successfully
    EXECUTION_FAILED = "execution_failed"    # Execution failed
    
    # Final states
    COMPLETED = "completed"                   # Everything finished successfully
    FAILED = "failed"                         # Final failure state
    
    @classmethod
    def is_pending_state(cls, status: str) -> bool:
        """Check if status indicates analysis/execution is still in progress"""
        return status in [
            cls.PENDING,
            cls.ANALYSIS_STARTED, 
            cls.EXECUTION_QUEUED,
            cls.EXECUTION_RUNNING
        ]
    
    @classmethod
    def is_failed_state(cls, status: str) -> bool:
        """Check if status indicates failure"""
        return status in [
            cls.ANALYSIS_FAILED,
            cls.EXECUTION_FAILED,
            cls.FAILED
        ]
    
    @classmethod
    def is_completed_state(cls, status: str) -> bool:
        """Check if status indicates successful completion"""
        return status in [
            cls.ANALYSIS_COMPLETED,
            cls.EXECUTION_COMPLETED,
            cls.COMPLETED
        ]
    
    @classmethod
    def is_execution_failed_state(cls, status: str) -> bool:
        """Check if execution status indicates failure"""
        # Handle both ExecutionStatus constants and MessageStatus constants
        return status in [
            "failed",        # ExecutionStatus.FAILED
            "timeout",       # ExecutionStatus.TIMEOUT
            cls.EXECUTION_FAILED,
            cls.FAILED
        ]
    
    @classmethod
    def is_execution_success_state(cls, status: str) -> bool:
        """Check if execution status indicates success"""
        # Handle both ExecutionStatus constants and MessageStatus constants
        return status in [
            "success",       # ExecutionStatus.SUCCESS
            "completed",     # General completed state
            cls.EXECUTION_COMPLETED,
            cls.COMPLETED
        ]
    
    @classmethod
    def is_execution_pending_state(cls, status: str) -> bool:
        """Check if execution status indicates in progress"""
        # Handle both ExecutionStatus constants and MessageStatus constants
        return status in [
            "pending",       # ExecutionStatus.PENDING
            "queued",        # General queued state
            "running",       # ExecutionStatus.RUNNING
            cls.EXECUTION_QUEUED,
            cls.EXECUTION_RUNNING
        ]