# Issue: Implement Async Analysis with Persistent Progress Logging

## Problem Statement

Currently, the analysis system has several UX and technical issues:
1. **Empty analysis components** render before execution results are available
2. **SSE connection loss** on page refresh loses all progress logs
3. **No prevention** of multiple concurrent analysis submissions
4. **Progress logs** exist only in memory via SSE
5. **User confusion** about analysis vs execution status

## Proposed Solution: Async Analysis with Message-Based Logging

### Core Architecture Changes

#### 1. Immediate Analysis Message Creation
- When user submits a question, immediately create analysis message with `"pending"` status
- This provides instant `messageId` for log tracking
- User sees analysis component immediately but in "processing" state

#### 2. Message-Based Progress Logging
- Add `logs` array field to chat messages in MongoDB
- Each log entry: `{message: str, timestamp: datetime, level: str, details: dict}`
- Update existing progress functions to append logs to message document
- SSE events include `messageId` for precise targeting

#### 3. Distributed Session Locking
- Use MongoDB/Redis for session locking (not in-memory)
- Supports multi-pod deployment
- Lock document: `{session_id, message_id, locked_at, expires_at}`

#### 4. Analysis Queue & Worker System
- Create separate analysis queue (like execution queue)
- Extract existing analysis logic into dedicated worker
- Analysis worker processes: context building → LLM call → script generation

## Implementation Plan

### Phase 1: Backend Infrastructure

#### 1.1 Enhanced Chat Message Schema
```python
# Add logs field to existing chat messages collection
{
  "_id": ObjectId,
  "session_id": str,
  "content": str,
  "message_type": str,  # "user", "analysis", "meaningless", etc.
  "timestamp": datetime,
  "logs": [  # NEW: Array of progress logs
    {
      "message": str,
      "timestamp": datetime, 
      "level": str,  # "info", "success", "warning", "error"
      "details": dict  # execution_id, status, results, etc.
    }
  ],
  "metadata": dict,
  # ... existing fields
}
```

#### 1.2 Enhanced Progress Service  
```python
class ProgressService:
    async def log_progress_to_message(self, message_id: str, 
                                     level: str, message: str, details: dict = None):
        # Append log to message.logs array in MongoDB
        log_entry = {
            "message": message,
            "timestamp": datetime.utcnow(),
            "level": level,
            "details": details or {}
        }
        
        await self.db.messages.update_one(
            {"_id": ObjectId(message_id)},
            {"$push": {"logs": log_entry}}
        )
        
        # Also emit via SSE with message_id
        await self.emit_sse(session_id, level, message, details={
            "message_id": message_id,
            **details
        })
```

#### 1.3 Distributed Session Locking (MongoDB-based)
```python
class DistributedSessionLock:
    def __init__(self, db):
        self.db = db
        self.collection = db.session_locks
    
    async def acquire_lock(self, session_id: str, message_id: str, ttl_seconds: int = 1800) -> bool:
        try:
            expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
            await self.collection.insert_one({
                "session_id": session_id,
                "message_id": message_id,
                "locked_at": datetime.utcnow(),
                "expires_at": expires_at
            })
            return True
        except DuplicateKeyError:
            # Session already locked
            return False
    
    async def release_lock(self, session_id: str):
        await self.collection.delete_one({"session_id": session_id})
    
    async def get_active_message(self, session_id: str) -> str:
        # Clean expired locks first
        await self.collection.delete_many({
            "expires_at": {"$lt": datetime.utcnow()}
        })
        
        lock = await self.collection.find_one({"session_id": session_id})
        return lock["message_id"] if lock else None
    
    async def extend_lock(self, session_id: str, ttl_seconds: int = 1800):
        expires_at = datetime.utcnow() + timedelta(seconds=ttl_seconds)
        await self.collection.update_one(
            {"session_id": session_id},
            {"$set": {"expires_at": expires_at}}
        )
```

#### 1.4 Analysis Queue System
```python
# New: shared/queue/analysis_queue.py
class AnalysisQueueInterface:
    async def enqueue_analysis(self, analysis_job: dict) -> str:
        # Queue analysis job: {session_id, message_id, user_question, context}
        
    async def dequeue_analysis(self, worker_id: str) -> Optional[dict]:
        # Get next analysis job for processing
        
    async def ack_analysis(self, job_id: str, result: dict):
        # Mark analysis complete with generated script
        
    async def nack_analysis(self, job_id: str, error: str, retry: bool = True):
        # Mark analysis failed

# New: shared/queue/analysis_worker.py  
class AnalysisQueueWorker:
    async def _process_analysis(self, job: dict):
        message_id = job["message_id"]
        
        # Log progress to message
        await progress_service.log_progress_to_message(
            message_id, "info", "Building context for analysis"
        )
        
        # Extract existing analysis logic:
        # 1. Context building (search, conversation history)
        # 2. LLM analysis call
        # 3. Script generation
        # 4. Save results to message
        
        await progress_service.log_progress_to_message(
            message_id, "success", "Analysis completed", 
            {"script_content": script, "analysis_data": analysis_result}
        )
```

#### 1.5 Modified Analysis Endpoint
```python
@router.post("/api/analysis")
async def analyze_question(request: AnalysisRequest):
    session_id = request.session_id
    user_question = request.question
    
    # 1. Check distributed session lock
    active_message_id = await session_lock.get_active_message(session_id)
    if active_message_id:
        raise HTTPException(409, f"Analysis in progress: {active_message_id}")
    
    try:
        # 2. Create user message
        user_message_id = await chat_service.add_user_message(
            session_id=session_id,
            content=user_question,
            message_type="user"
        )
        
        # 3. Create analysis message with pending status and empty logs
        analysis_message_id = await chat_service.add_analysis_message(
            session_id=session_id,
            content="Analysis in progress...",
            message_type="analysis", 
            status="pending",
            logs=[],  # Initialize empty logs array
            metadata={"user_message_id": user_message_id}
        )
        
        # 4. Acquire distributed lock
        lock_acquired = await session_lock.acquire_lock(session_id, analysis_message_id)
        if not lock_acquired:
            raise HTTPException(409, "Failed to acquire session lock")
        
        # 5. Log initial progress to message
        await progress_service.log_progress_to_message(
            analysis_message_id, "info", "Analysis queued for processing", 
            {"status": "pending"}
        )
        
        # 6. Queue analysis for worker processing
        await analysis_queue.enqueue_analysis({
            "session_id": session_id,
            "message_id": analysis_message_id,
            "user_question": user_question,
            "user_message_id": user_message_id
        })
        
        return {"message_id": analysis_message_id, "status": "pending"}
        
    except Exception as e:
        await session_lock.release_lock(session_id)
        raise
```

### Phase 2: Analysis Worker Implementation

#### 2.1 Extract Analysis Logic to Worker
```python
class AnalysisQueueWorker:
    async def _process_analysis(self, job: dict):
        message_id = job["message_id"]
        session_id = job["session_id"]
        user_question = job["user_question"]
        
        try:
            # Log analysis start
            await progress_service.log_progress_to_message(
                message_id, "info", "Analysis started"
            )
            
            # STEP 1: Extract existing context building logic
            await progress_service.log_progress_to_message(
                message_id, "info", "Building context for analysis"
            )
            context = await self._build_context(session_id, user_question)
            
            # STEP 2: Extract existing LLM analysis logic  
            await progress_service.log_progress_to_message(
                message_id, "info", "Analyzing question with LLM"
            )
            analysis_result = await self._analyze_with_llm(user_question, context)
            
            # STEP 3: Extract existing script generation logic
            await progress_service.log_progress_to_message(
                message_id, "info", "Generating analysis script"
            )
            script_content = await self._generate_script(analysis_result)
            
            # STEP 4: Save results and complete
            await self._complete_analysis(message_id, session_id, {
                "script_content": script_content,
                "analysis_data": analysis_result,
                "status": "completed"
            })
            
            await analysis_queue.ack_analysis(job["job_id"], analysis_result)
            
        except Exception as e:
            await progress_service.log_progress_to_message(
                message_id, "error", f"Analysis failed: {str(e)}"
            )
            await analysis_queue.nack_analysis(job["job_id"], str(e))
        finally:
            # Always release session lock
            await session_lock.release_lock(session_id)
    
    async def _build_context(self, session_id: str, question: str) -> dict:
        # Extract from existing AnalysisService.analyze()
        # - Conversation history
        # - Semantic search
        # - Context expansion
        pass
    
    async def _analyze_with_llm(self, question: str, context: dict) -> dict:
        # Extract from existing AnalysisService.analyze()
        # - LLM service call
        # - Analysis prompt building
        # - Response parsing
        pass
    
    async def _generate_script(self, analysis_result: dict) -> str:
        # Extract from existing AnalysisService.analyze()
        # - Script generation logic
        # - Parameter handling
        pass
    
    async def _complete_analysis(self, message_id: str, session_id: str, result: dict):
        # Update message with final results
        await chat_service.update_message(message_id, {
            "status": "completed",
            "metadata": {
                **result,
                "completed_at": datetime.utcnow()
            }
        })
        
        # Log completion
        await progress_service.log_progress_to_message(
            message_id, "success", "Analysis completed successfully",
            result
        )
```

#### 2.2 Execution Worker Enhancement
```python
# Update existing execution worker to also log to message
class ExecutionQueueWorker:
    async def _process_execution(self, execution: dict):
        execution_id = execution.get("execution_id")
        message_id = execution.get("message_id")  # NEW: from analysis message
        
        if message_id:
            # Log execution progress to original analysis message
            await progress_service.log_progress_to_message(
                message_id, "info", 
                "Script execution started", 
                {"execution_id": execution_id, "status": "running"}
            )
        
        # ... existing execution logic ...
        
        if success and message_id:
            # Log execution completion to analysis message
            await progress_service.log_progress_to_message(
                message_id, "success", "Script execution completed",
                {
                    "execution_id": execution_id,
                    "status": "completed", 
                    "results": result_output,
                    "markdown": markdown
                }
            )
```

### Phase 3: Frontend Implementation

#### 3.1 Enhanced Analysis Result Component
```typescript
interface AnalysisResultProps {
  messageId: string;
  sessionId: string;
  initialStatus: 'pending' | 'running' | 'completed' | 'failed';
  initialResults?: any;
}

export default function AnalysisResult({ messageId, sessionId, initialStatus, initialResults }: AnalysisResultProps) {
  const [status, setStatus] = useState(initialStatus);
  const [results, setResults] = useState(initialResults);
  const [progressLogs, setProgressLogs] = useState<ProgressLog[]>([]);
  
  // Subscribe to SSE events for this specific message
  const { logs: allLogs } = useProgressStream(sessionId);
  
  useEffect(() => {
    // Filter logs for this specific message
    const messageLogs = allLogs.filter(log => 
      log.details?.message_id === messageId
    );
    setProgressLogs(messageLogs);
    
    // Update status and results from latest log
    const latestLog = messageLogs[messageLogs.length - 1];
    if (latestLog?.details?.status) {
      setStatus(latestLog.details.status);
      if (latestLog.details.results) {
        setResults(latestLog.details.results);
      }
    }
  }, [allLogs, messageId]);
  
  // On component mount, fetch historical logs (for page refresh recovery)
  useEffect(() => {
    fetchMessageProgressLogs(messageId).then(setProgressLogs);
  }, [messageId]);
  
  return (
    <div className="analysis-result">
      {status === 'pending' || status === 'running' ? (
        <div className="progress-section">
          <div className="status-indicator">
            {status === 'pending' && <div className="pending">Analysis queued...</div>}
            {status === 'running' && <div className="running">Analysis in progress...</div>}
          </div>
          
          <div className="progress-logs">
            {progressLogs.map(log => (
              <div key={log.id} className={`log-entry ${log.level}`}>
                <span className="timestamp">{formatTime(log.timestamp)}</span>
                <span className="message">{log.message}</span>
              </div>
            ))}
          </div>
        </div>
      ) : (
        <div className="results-section">
          {/* Render completed results */}
          {results && <ResultsDisplay results={results} />}
        </div>
      )}
    </div>
  );
}
```

#### 3.2 Session State Management
```typescript
// In ChatInterface or session context
const [sessionAnalyzing, setSessionAnalyzing] = useState(false);
const [activeAnalysisMessageId, setActiveAnalysisMessageId] = useState<string | null>(null);

const handleSubmit = async (message: string) => {
  if (sessionAnalyzing) {
    alert("Please wait for current analysis to complete");
    return;
  }
  
  setSessionAnalyzing(true);
  try {
    const response = await fetch('/api/analysis', { ... });
    const { message_id } = await response.json();
    setActiveAnalysisMessageId(message_id);
    
    // Don't reset sessionAnalyzing here - wait for completion via SSE
  } catch (error) {
    if (error.status === 409) {
      alert("Analysis already in progress for this session");
    }
    setSessionAnalyzing(false);
  }
};

// Listen for completion via SSE
useEffect(() => {
  const completionLog = logs.find(log => 
    log.details?.message_id === activeAnalysisMessageId &&
    log.details?.status === 'completed'
  );
  
  if (completionLog) {
    setSessionAnalyzing(false);
    setActiveAnalysisMessageId(null);
  }
}, [logs, activeAnalysisMessageId]);

// Recovery on page refresh
useEffect(() => {
  if (sessionId) {
    checkSessionAnalysisStatus(sessionId).then(({ isAnalyzing, messageId }) => {
      setSessionAnalyzing(isAnalyzing);
      setActiveAnalysisMessageId(messageId);
    });
  }
}, [sessionId]);
```

#### 3.3 Recovery API Endpoint
```python
@router.get("/api/sessions/{session_id}/analysis-status")
async def get_session_analysis_status(session_id: str):
    active_message_id = analysis_lock.get_active_message(session_id)
    
    if active_message_id:
        # Get latest progress
        logs = await progress_service.get_message_progress_logs(active_message_id)
        latest_status = "pending"
        if logs:
            latest_status = logs[-1].get("details", {}).get("status", "pending")
        
        return {
            "isAnalyzing": latest_status in ["pending", "running"],
            "messageId": active_message_id,
            "status": latest_status,
            "progressLogs": logs
        }
    
    return {"isAnalyzing": False, "messageId": None}
```

### Phase 4: Database Migrations

#### 4.1 Progress Logs Collection
```python
# Migration script
async def create_progress_logs_collection():
    # Create collection with TTL index
    await db.progress_logs.create_index(
        "created_at", 
        expireAfterSeconds=24*60*60  # 24 hours
    )
    
    # Create compound index for efficient queries
    await db.progress_logs.create_index([
        ("session_id", 1),
        ("message_id", 1),
        ("timestamp", 1)
    ])
```

## Benefits

### User Experience
1. **No empty components** - analysis shows progress immediately
2. **Page refresh recovery** - progress logs persist and restore
3. **Clear feedback** - users know when analysis is running
4. **Prevents confusion** - only one analysis per session

### Technical Benefits
1. **Persistent progress** - logs survive connection drops
2. **Precise targeting** - logs linked to specific messages
3. **Clean recovery** - easy to restore state after refresh
4. **Scalable logging** - TTL auto-cleanup prevents bloat

### Phase 4: Database & Infrastructure

#### 4.1 MongoDB Schema Updates
```python
# Migration script: Add logs field to existing messages
await db.messages.update_many(
    {"logs": {"$exists": False}},
    {"$set": {"logs": []}}
)

# Create session_locks collection with unique index
await db.session_locks.create_index(
    "session_id", 
    unique=True
)

# Create TTL index for auto-expiring locks
await db.session_locks.create_index(
    "expires_at", 
    expireAfterSeconds=0
)
```

#### 4.2 Analysis Worker Startup
```bash
# New: start_analysis_worker.sh
#!/bin/bash
cd "$(dirname "$0")"
source .env
export PYTHONPATH="${PYTHONPATH}:$(pwd)/../../shared"
python -m shared.queue.analysis_worker
```

## Implementation Timeline

- **Week 1**: Backend infrastructure (progress service, locking, analysis queue/worker)
- **Week 2**: Extract analysis logic from service to worker
- **Week 3**: Frontend component updates and recovery logic  
- **Week 4**: Testing, error handling, and polish

## Getting Started

### Phase 1 Implementation Steps:

1. **Add logs field to message schema**
2. **Create distributed session locking** 
3. **Build analysis queue system** (copy from execution queue)
4. **Extract analysis logic to worker**
5. **Update progress service** to write to message.logs
6. **Modify analysis endpoint** to use queue instead of direct processing
7. **Update frontend** to read logs from message and handle page refresh recovery

## Testing Strategy

1. **Unit tests** for progress service and locking mechanism
2. **Integration tests** for SSE + database coordination
3. **E2E tests** for page refresh recovery scenarios
4. **Load tests** for concurrent session handling

## Risks & Mitigations

1. **Risk**: Database growth from progress logs
   **Mitigation**: TTL indexes for auto-cleanup

2. **Risk**: Memory leaks in session locks
   **Mitigation**: Periodic cleanup job for stale locks

3. **Risk**: SSE connection issues
   **Mitigation**: Robust reconnection and polling fallback

## Success Criteria

- [ ] Users can refresh page during analysis without losing progress
- [ ] No empty/meaningless analysis components shown
- [ ] Multiple submissions prevented with clear feedback
- [ ] Progress logs persist across browser sessions
- [ ] Clean recovery from any connection failures