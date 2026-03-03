# Backend Resilience & UI Communication Fix Plan

> Generated: March 2, 2026  
> Based on critical architecture analysis of the full request lifecycle.

---

## Phase 1 — Single-Line/Trivial Fixes

These are all small, targeted changes. No architectural impact. Do these first.

### Fix #4 — `send_execution_queued` / `send_execution_failed` called without `session_id`

**File:** `backend/apiServer/api/routes.py` → `_submit_execution()`  
**Problem:** `send_execution_queued()` and `send_execution_failed(...)` rely on `worker_context.get_session_id()` which is empty in the API request handler. Events are fired into a void — the UI never learns execution was queued or failed.  
**Fix:** Replace the context-based calls with explicit `send_progress_event(session_id, {...})` calls.

---

### Fix #5 — `null` message_id returned on DB write failure

**File:** `backend/apiServer/api/routes.py` → `_create_response_with_message()`  
**Problem:** If `add_assistant_message` throws, `msg_id` stays `None`. The response returns `message_id: null`. The UI stores null as the SSE correlation ID, SSE events never match, spinner hangs forever.  
**Fix:** Raise (return 500) if message creation fails — this is a critical path. "Continue anyway" is wrong here.

---

### Fix #12 — Session lock TTL is 30 minutes

**File:** `backend/shared/locking/session_lock.py`  
**Problem:** If a worker crashes after acquiring a lock, the user is locked out for 30 minutes with no visibility.  
**Fix:** Change default `ttl_seconds` from `1800` → `300` (5 minutes).

---

### Fix #9 — 30s client timeout on LLM-backed chat endpoint

**File:** `frontend/src/lib/hooks/useChatAnalysis.ts`  
**Problem:** `api.client.post()` defaults to 30s timeout. Inline LLM calls (clarification, hybrid chat) can exceed this. With `retries: 0`, timeout = total failure.  
**Fix:** Set explicit `timeout: 90000` on the chat POST.

---

### Fix #8 — `loadSessionMessages` uses raw `fetch()`, no retry/timeout

**File:** `frontend/src/lib/hooks/useConversation.ts` → `loadSessionMessages()`  
**Problem:** Raw `fetch()` bypasses the `APIClient` — no exponential backoff, no normalized errors, no timeout. One transient 503 clears the entire session history from the UI.  
**Fix:** Replace `fetch()` with `api.client.get()`.

---

## Phase 2 — Backend Reliability

### Fix #2 — ProgressMonitor marks events processed regardless of delivery

**File:** `backend/apiServer/services/progress_monitor.py` → `_process_event()`  
**Problem:** `_mark_processed()` is called even when `ProgressStreamManager` has zero subscribers. Events are permanently gone before the client connects.  
**Fix:** Do not mark events processed based on delivery. Let the MongoDB TTL index handle cleanup. Events stay queryable for replay (#1).

---

### Fix #3 — No stale job reclaimer on worker startup

**File:** `backend/shared/queue/analysis_worker.py` → `_initialize_services()`  
**Problem:** If a worker crashes mid-analysis, the MongoDB job stays in `status: "processing"` forever. No background reclaimer exists.  
**Fix:** On startup, find any jobs stuck in `processing` for >10 minutes and reset them to `pending` (increment `retry_count`). Also release their session locks.

---

### Fix #7 — Next.js SSE proxy leaks backend connections + no AbortController

**File:** `frontend/src/app/api/progress/[sessionId]/route.ts`  
**Problem:** When the browser disconnects, the proxy's `fetch()` to the backend has no `AbortController`. The Python uvicorn worker slot leaks until the next heartbeat/timeout cycle. On Next.js dev, buffering can also delay SSE events by seconds.  
**Fix:** Wire `request.signal` to an `AbortController` passed to the backend `fetch()` call. Clean up `activeConnections` Map dead code.

---

### Fix #13 — Execution server unauthenticated, CORS `allow_origins=["*"]`

**File:** `backend/executionServer/http_script_execution_server.py`  
**Problem:** The execution server runs arbitrary Python scripts. It is reachable on port 8013 with no auth, from any process on the machine.  
**Fix:** Bind to `127.0.0.1` only. Validate a shared-secret header (`X-Execution-Token`) on every request. Generate the secret at startup and require it from `ExecutionService`.

---

## Phase 3 — Real Durability (Sprint Work)

### Fix #1 — SSE events are non-durable; no replay on reconnect

**Files:** `backend/apiServer/api/progress_routes.py`, `backend/apiServer/services/sse/progress_sse.py`  
**Problem:** `ProgressStreamManager` is pure in-memory. `get_events()` returns `[]`. If the browser disconnects for even 1 second, all events fired during that window are lost forever (ProgressMonitor already marked them processed). UI shows spinner indefinitely.  
**Fix:**
1. Send `id: {event_id}` on every SSE frame so browsers automatically send `Last-Event-ID` on reconnect.
2. On reconnect, read `Last-Event-ID` header and replay all MongoDB events with `timestamp > last_seen` before opening the live subscription.
3. Remove the "mark processed" behavior (see Fix #2) so events remain queryable until TTL expiry.

```python
# progress_routes.py skeleton
last_event_id = request.headers.get("Last-Event-ID")
if last_event_id:
    missed = await progress_event_queue.get_events_since_id(session_id, last_event_id)
    for event in missed:
        yield f"id: {event['event_id']}\ndata: {json.dumps(event)}\n\n"
# then subscribe to live events as before
```

---

### Fix #6 — No status poll fallback when SSE is dead

**Files:** `backend/apiServer/api/progress_routes.py` (new endpoint), frontend `useProgressStream.ts`  
**Problem:** There is no way to query the current status of a pending analysis. If SSE fails, the user must refresh and hope session history loads correctly.  
**Fix:**
1. Add `GET /sessions/{session_id}/messages/{message_id}/status` endpoint that reads `metadata.status` from MongoDB.
2. In `useProgressStream`, when `isConnected === false`, poll this endpoint every 3s as a fallback.

---

### Fix #11 — 5 competing completion conditions in `useProgressStream`

**File:** `frontend/src/lib/hooks/useProgressStream.ts`  
**Problem:** Completion is detected by 5 separate `if` blocks checking different event shapes and field locations (`data.status`, `data.details.status`, `data.type === 'analysis_complete'`, etc.). Any schema drift causes the UI to hang indefinitely.  
**Fix:**
1. Define one canonical completion event on the backend:
   ```json
   { "type": "analysis_complete", "status": "completed|failed", "message_id": "...", "session_id": "..." }
   ```
2. All workers emit this exact shape.
3. Collapse the frontend to one condition:
   ```typescript
   if (data.type === 'analysis_complete') {
     onAnalysisComplete(data.status === 'completed' ? 'completed' : 'failed', data);
   }
   ```

---

## Severity / Effort Matrix

| # | Issue | Severity | Effort | Phase |
|---|-------|----------|--------|-------|
| 4 | `session_id` missing in execution SSE calls | Critical | XS | 1 |
| 5 | `null` message_id on DB write failure | Critical | S | 1 |
| 12 | 30-min session lock TTL | High | XS | 1 |
| 9 | 30s timeout on LLM endpoint | High | XS | 1 |
| 8 | Raw `fetch` in `loadSessionMessages` | High | XS | 1 |
| 2 | ProgressMonitor marks events processed w/ 0 subscribers | Critical | S | 2 |
| 3 | No stale job reclaimer | High | S | 2 |
| 7 | SSE proxy connection leak | High | S | 2 |
| 13 | Execution server unauthenticated | High | S | 2 |
| 1 | SSE non-durable, no replay | Critical | M | 3 |
| 6 | No poll fallback when SSE dead | High | M | 3 |
| 11 | 5 competing completion conditions in UI | High | M | 3 |
