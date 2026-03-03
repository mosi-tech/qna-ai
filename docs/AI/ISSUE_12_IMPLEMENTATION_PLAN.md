# Issue #12: Build mock-ux to Production UI Integration Layer

## Issue Requirements

From GitHub Issue #12:
> "Integrate mock-ux prototypes into main application:
> - Merge component designs
> - Adapt data flow to production backend
> - Test user interactions
> - Performance optimization
> - Mobile responsiveness"

## Current State Analysis

### frontend (Prototype - formerly mock-ux)
- **Location**: `/frontend`
- **Framework**: Next.js 15.5.3 (runs on port 3003)
- **Components**:
  - `ConversationalForm.tsx` - Chat interface
  - `AutocompleteInput.tsx` - Smart input with suggestions
  - `AnalysisPanel.tsx` - Results display
  - `Backtester.tsx` - Backtesting interface
  - `MockOutput.tsx` - Mock data display
  - `ParameterControl.tsx` - Parameter configuration

### Production Backend
- **Location**: `/backend/scriptEdition/apiServer`
- **Framework**: FastAPI (Python)
- **Endpoints**:
  - `POST /analyze_question` - Main analysis endpoint
  - `POST /search_with_context` - Context-aware search
  - `GET /session/<id>` - Session management
  - Uses ChatHistoryService for persistence
  - Uses SessionManager for state coordination

### Integration Gap

**Currently:**
- frontend: Standalone prototype with mock data
- Backend: Running independently
- No connection between UI and backend

**Needed:**
- Bridge between frontend UI and FastAPI backend
- Real API integration layer
- Session management in UI
- Error handling and loading states

## Implementation Strategy

### Phase 1: API Client Layer (Foundation)
**Goal**: Create reusable API client for frontend

**Tasks**:
1. Create `/frontend/src/lib/api/client.ts`
   - Base HTTP client with error handling
   - Auth token support (for future)
   - Request/response logging

2. Create API service modules:
   - `/frontend/src/lib/api/analysis.ts` - Analysis operations
   - `/frontend/src/lib/api/session.ts` - Session management
   - `/frontend/src/lib/api/types.ts` - Shared types

3. Environment configuration:
   - `.env.local.example` with backend URL
   - Support for dev/prod environments

### Phase 2: Component Integration (UI Adaptation)
**Goal**: Connect UI components to backend APIs

**Tasks**:
1. Update `ConversationalForm.tsx`
   - Connect to `POST /analyze_question`
   - Handle real API responses
   - Add loading/error states

2. Update `AutocompleteInput.tsx`
   - Use real search suggestions
   - Integrate with semantic search
   - Cache suggestions

3. Update `AnalysisPanel.tsx`
   - Display real analysis results
   - Format backend response data
   - Handle different response types

4. Add Session Management
   - Store session_id in localStorage
   - Persist conversation state
   - Resume sessions on page reload

### Phase 3: State Management (Data Flow)
**Goal**: Manage complex application state

**Tasks**:
1. Implement React Context for:
   - Session state (session_id, user_id)
   - Conversation history
   - UI state (loading, errors)
   - User preferences

2. Create custom hooks:
   - `useAnalysis()` - Manage analysis requests
   - `useSession()` - Manage session lifecycle
   - `useConversation()` - Track conversation history

3. Error Boundary components:
   - Graceful error handling
   - User-friendly messages
   - Retry mechanisms

### Phase 4: Performance Optimization
**Goal**: Ensure smooth, responsive UI

**Tasks**:
1. Code Splitting
   - Split by route (e.g., Backtester, Chat)
   - Split by component size
   - Lazy load heavy components

2. Data Optimization
   - API response caching
   - Debounce search input
   - Virtualize long lists

3. Build Optimization
   - Minimize bundle size
   - Remove unused CSS
   - Optimize images

4. Monitoring
   - Track API latency
   - Monitor error rates
   - Log performance metrics

### Phase 5: Mobile Responsiveness
**Goal**: Ensure mobile-first design

**Tasks**:
1. Responsive Layouts
   - Mobile chat interface (90% width)
   - Tablet two-column layout
   - Desktop full layout

2. Touch Optimization
   - Larger touch targets (48px min)
   - Mobile-friendly forms
   - Gesture support (swipe, pinch)

3. Mobile-specific Features
   - Sticky header/footer
   - Simplified controls
   - Mobile keyboard handling

### Phase 6: Testing
**Goal**: Ensure quality and reliability

**Tasks**:
1. Unit Tests
   - Test API client
   - Test custom hooks
   - Test components in isolation

2. Integration Tests
   - Test component interactions
   - Test API integration
   - Test error scenarios

3. E2E Tests
   - Test complete user flows
   - Test on multiple devices
   - Test offline scenarios

## Implementation Order

```
Phase 1 (Foundation - Week 1)
├─ API client layer
├─ Environment setup
└─ TypeScript types

Phase 2 (Integration - Week 2-3)
├─ Component API connections
├─ Session management
├─ Error handling
└─ Loading states

Phase 3 (State - Week 3-4)
├─ React Context
├─ Custom hooks
└─ Global state management

Phase 4 (Performance - Week 4-5)
├─ Code splitting
├─ Caching strategy
├─ Build optimization
└─ Monitoring

Phase 5 (Mobile - Week 5-6)
├─ Responsive design
├─ Touch optimization
└─ Mobile testing

Phase 6 (Testing - Week 6-7)
├─ Unit tests
├─ Integration tests
└─ E2E tests
```

## Key Architecture Decisions

### 1. API Client Architecture
```typescript
// Single client instance with configurations
const api = createClient({
  baseURL: process.env.NEXT_PUBLIC_API_URL,
  timeout: 30000,
  retries: 3,
});

// Service layer on top
const analysisService = createAnalysisService(api);
const sessionService = createSessionService(api);
```

### 2. State Management Pattern
```typescript
// Use Context API + Hooks pattern (no external libraries)
// Reasons:
// - Built into React
// - Suitable for this app's complexity
// - Avoids dependency bloat
// - Clear data flow

const [session, setSession] = useSession();
const [conversation, setConversation] = useConversation();
const [ui, setUI] = useUIState();
```

### 3. Error Handling Strategy
```typescript
// Unified error handling
type ErrorResponse = {
  success: false;
  error: string;
  details?: Record<string, any>;
  timestamp: string;
};

// Consistent error format across API
// Client-side error boundaries
// User-friendly error messages
```

### 4. Caching Strategy
```typescript
// Three-level caching:
1. Memory cache (in-memory, request-scoped)
2. Browser cache (localStorage, session-duration)
3. API caching (server-side, conversation-scoped)

// Cache invalidation rules:
- Session ends → Clear all
- New analysis → Clear old results
- User logout → Clear all
```

## File Structure (Target)

```
frontend/
├── src/
│   ├── app/
│   │   ├── page.tsx            ← Main chat interface
│   │   ├── layout.tsx
│   │   └── globals.css
│   ├── components/
│   │   ├── Chat/
│   │   │   ├── ConversationalForm.tsx
│   │   │   ├── AnalysisPanel.tsx
│   │   │   └── ChatContext.tsx
│   │   ├── Input/
│   │   │   ├── AutocompleteInput.tsx
│   │   │   └── useAutocomplete.ts
│   │   ├── ErrorBoundary.tsx
│   │   └── LoadingSpinner.tsx
│   ├── lib/
│   │   ├── api/
│   │   │   ├── client.ts       ← HTTP client
│   │   │   ├── analysis.ts     ← Analysis service
│   │   │   ├── session.ts      ← Session service
│   │   │   ├── types.ts        ← Shared types
│   │   │   └── errors.ts       ← Error handling
│   │   ├── hooks/
│   │   │   ├── useAnalysis.ts
│   │   │   ├── useSession.ts
│   │   │   └── useConversation.ts
│   │   ├── context/
│   │   │   ├── SessionContext.tsx
│   │   │   ├── ConversationContext.tsx
│   │   │   └── UIContext.tsx
│   │   └── utils/
│   │       ├── cache.ts
│   │       └── validation.ts
│   ├── .env.local.example
│   └── config.ts
├── package.json
└── tsconfig.json
```

## Backend API Assumptions

**Endpoint**: `POST /analyze_question`
```json
Request:
{
  "question": "What is AAPL volatility?",
  "session_id": "uuid-here",
  "user_id": "user-123",
  "enable_caching": true
}

Response:
{
  "success": true,
  "data": {
    "session_id": "uuid-here",
    "query_type": "complete",
    "original_query": "What is AAPL volatility?",
    "expanded_query": "...",
    "search_results": [...],
    "found_similar": true,
    "analysis_summary": "..."
  }
}
```

**Endpoint**: `GET /session/{session_id}`
```json
Response:
{
  "success": true,
  "data": {
    "session_id": "uuid-here",
    "messages": [...],
    "context_summary": {...}
  }
}
```

## Success Criteria

✅ **Phase 1 Complete**
- API client working with mock backend
- TypeScript types defined
- Environment configuration working

✅ **Phase 2 Complete**
- UI components connected to real APIs
- Session management working
- Error handling in place

✅ **Phase 3 Complete**
- Global state management implemented
- Complex interactions working
- Component reuse optimized

✅ **Phase 4 Complete**
- Bundle size < 500KB
- API response time < 2s
- UI interactions < 100ms

✅ **Phase 5 Complete**
- Mobile viewport working
- Touch interactions responsive
- Tested on 3+ device sizes

✅ **Phase 6 Complete**
- 80%+ test coverage
- All user flows tested
- No console errors

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| API incompatibility | Define interface early, mock API responses |
| Stale session data | Implement cache invalidation strategy |
| Large bundle | Implement code splitting and tree-shaking |
| Mobile lag | Profile and optimize with DevTools |
| Lost user data | Implement session persistence and recovery |

## Next Steps

1. **Immediate**: Review this plan with team
2. **Week 1**: Implement Phase 1 (API client)
3. **Weekly**: Demo progress to stakeholders
4. **Ongoing**: Monitor metrics and gather feedback

## References

- Backend API: `/backend/scriptEdition/apiServer/api/routes.py`
- ChatHistoryService: `/backend/scriptEdition/apiServer/services/chat_service.py`
- SessionManager: `/backend/scriptEdition/apiServer/dialogue/conversation/session_manager.py`
- Frontend Components: `/frontend/src/components/`
