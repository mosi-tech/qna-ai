# Phase 2: UI Component Integration - Analysis & Changes Required

## Executive Summary
The frontend UI is mostly experimental with mock data flows. Phase 2 requires replacing mock patterns with real API integration while maintaining the good UX patterns already established.

## Experimental Components Identified

### 1. **Mock Data Patterns** ❌
**Files affected:**
- `src/components/MockOutput.tsx` - Hardcoded mock metrics
- `src/app/page.tsx` - Simulated chat delays and typing
- `src/components/ConversationalForm.tsx` - Hardcoded analysis presets

**Issue:** Uses setTimeout/static data instead of real API calls
**Fix:** Replace with API calls to backend

### 2. **Hardcoded Message Flows**
**Files affected:**
- `src/app/page.tsx` (lines 63-152) - handleSendMessage
  - Artificial delays: 500ms, 1500ms, 2000ms
  - Fake state transitions: thinking → ai → analyzing → results
  - No actual analysis execution

**Issue:** Creating fake UX that doesn't reflect real backend behavior
**Fix:** Direct API call to `/analyze_question`, real response handling

### 3. **Fuzzy Matching Instead of API Search**
**Files affected:**
- `src/app/page.tsx` (lines 50-61) - findBestMatchingAnalysis
- `src/components/autocomplete/AutocompleteInput.tsx` - Hardcoded predictions

**Issue:** Client-side keyword matching instead of semantic search
**Fix:** Use real search API with embeddings

### 4. **Disconnected Services**
**Issue:** API client layer exists (`src/lib/api/`) but components don't use it
**Files affected:**
- All components call nothing, using only local state
- No API client imports in any component

**Fix:** Import and use `api` from `src/lib/api/index.ts`

### 5. **No Session Management**
**Files affected:**
- `src/app/page.tsx` - No session tracking
- No localStorage persistence
- No session context

**Fix:** Create SessionContext, use SessionService

### 6. **Isolated Component State**
**Issue:** Each component manages own state, no global app state
**Fix:** Create context providers for:
- Session (session_id, user_id)
- Conversation (message history, current question)
- UI (loading states, errors)

---

## Phase 2 Implementation Plan

### Step 1: Create Custom Hooks 
**Files to create:**
```
frontend/src/lib/hooks/
├── useAnalysis.ts         - Manage analysis requests & responses
├── useSession.ts          - Session lifecycle management
├── useConversation.ts     - Conversation history tracking
└── useErrorHandler.ts     - Consistent error handling
```

**useAnalysis Hook:**
- Takes question, manages loading/error states
- Calls api.analysis.analyzeQuestion()
- Returns: {data, loading, error, refetch}

**useSession Hook:**
- Manages session_id (localStorage persistence)
- Calls api.session.startSession() on mount
- Provides session context to components

**useConversation Hook:**
- Tracks message history
- Persists to localStorage
- Supports resume on page reload

### Step 2: Create React Context Providers
**Files to create:**
```
frontend/src/lib/context/
├── SessionContext.tsx       - Session state provider
├── ConversationContext.tsx  - Conversation history provider
├── UIContext.tsx           - Loading, error, notification state
└── providers.tsx           - Combined provider wrapper
```

**SessionContext:**
```typescript
interface SessionContextType {
  session_id: string | null;
  user_id: string | null;
  startNewSession: () => Promise<void>;
  endSession: () => Promise<void>;
}
```

**ConversationContext:**
```typescript
interface ConversationContextType {
  messages: ChatMessage[];
  addMessage: (msg: ChatMessage) => void;
  clearMessages: () => void;
  resumeSession: (sessionId: string) => Promise<void>;
}
```

### Step 3: Update Root Layout
**File:** `src/app/layout.tsx`
- Wrap with SessionProvider
- Wrap with ConversationProvider
- Add error boundary wrapper

### Step 4: Refactor Main Page Component
**File:** `src/app/page.tsx` - Key changes:
```typescript
export default function Home() {
  const { session_id } = useSession();
  const { messages, addMessage } = useConversation();
  const { analyzeQuestion, isLoading, error } = useAnalysis();

  const handleSendMessage = async (userMessage: string) => {
    // Real API call instead of mock delays
    const response = await analyzeQuestion({
      question: userMessage,
      session_id: session_id!,
    });
    
    // Directly use response data
    if (response.success) {
      addMessage({
        type: 'results',
        content: response.data.analysis_summary,
        data: response.data,
      });
    }
  };
}
```

**Remove:**
- All setTimeout artificial delays (lines 77, 91, 113, 140)
- Fake state transitions (thinking → ai → analyzing)
- findBestMatchingAnalysis() - use search API instead

### Step 5: Update Components to Use API

#### ConversationalForm.tsx
**Current:** Hardcoded presets
**Change to:**
```typescript
const { session_id } = useSession();
const { addMessage } = useConversation();
const { analyzeQuestion } = useAnalysis();

const handleSubmit = async (response: string) => {
  // Call real API with preset or custom config
  await analyzeQuestion({
    question: response,
    session_id: session_id!,
  });
};
```

#### AutocompleteInput.tsx
**Current:** Hardcoded keyword predictions
**Change to:**
```typescript
const { getSuggestions } = useAnalysis();

useEffect(() => {
  if (input.length > 2) {
    getSuggestions(input).then(setSuggestions);
  }
}, [input]);
```

#### AnalysisPanel.tsx
**Current:** Shows MockOutput static data
**Change to:**
```typescript
export default function AnalysisPanel({ currentAnalysis }: AnalysisPanelProps) {
  if (!currentAnalysis?.data) {
    return <EmptyState />;
  }
  
  return (
    <div>
      <AnalysisResults data={currentAnalysis.data} />
    </div>
  );
}
```

#### MockOutput.tsx
**Current:** Hardcoded metrics by moduleKey
**Deprecate:** Remove this component entirely
**Replace with:** Generic ResultsDisplay component that renders API response

---

## Component Integration Map

### Current (Experimental) ❌
```
page.tsx (mock)
├── ChatInterface (mock)
│   └── ConversationalForm (hardcoded presets)
├── AnalysisPanel (mock)
│   └── MockOutput (hardcoded metrics)
└── CustomizationForm (disconnected)
```

### Target (Integrated) ✅
```
layout.tsx (Providers)
├── SessionProvider
├── ConversationProvider
└── UIProvider
    └── page.tsx (real API)
        ├── ChatInterface (useAnalysis)
        │   └── ConversationalForm (API presets)
        ├── AnalysisPanel (real data)
        │   └── ResultsDisplay (API response)
        └── CustomizationForm (API driven)
```

---

## Data Flow Changes

### Current (Mock) Flow ❌
```
User Input
  ↓
handleSendMessage (page.tsx)
  ↓
Simulate delays (500ms, 1500ms, 2000ms)
  ↓
Find matching module (fuzzy matching)
  ↓
Create fake messages (thinking → analyzing → results)
  ↓
Display MockOutput (hardcoded metrics)
```

### Target (Real API) Flow ✅
```
User Input
  ↓
handleSendMessage (useAnalysis hook)
  ↓
api.analysis.analyzeQuestion()
  ↓
Real backend processing
  ↓
Handle response (success/error)
  ↓
Store in ConversationContext
  ↓
Display ResultsDisplay (real data)
```

---

## API Integration Checklist

- [ ] **Session Management**
  - [ ] Start session on app load
  - [ ] Store session_id in context & localStorage
  - [ ] Pass session_id to all API calls
  - [ ] Resume session on page reload

- [ ] **Analysis Questions**
  - [ ] Replace mock API with real `/analyze_question` endpoint
  - [ ] Remove artificial delays
  - [ ] Handle real response format
  - [ ] Display actual analysis results

- [ ] **Search/Suggestions**
  - [ ] Replace hardcoded predictions with API search
  - [ ] Use semantic matching from backend
  - [ ] Cache suggestions in browser

- [ ] **Error Handling**
  - [ ] Wrap API calls in try-catch
  - [ ] Show user-friendly error messages
  - [ ] Implement retry logic for failed requests
  - [ ] Log errors with context

- [ ] **Loading States**
  - [ ] Show loading indicator during API calls
  - [ ] Disable inputs while processing
  - [ ] Display realistic timing (not fake delays)

- [ ] **Caching**
  - [ ] Cache analysis results in browser
  - [ ] Reuse results for identical questions
  - [ ] Invalidate cache when session ends

---

## Files to Create/Modify

### Create:
1. `src/lib/hooks/useAnalysis.ts`
2. `src/lib/hooks/useSession.ts`
3. `src/lib/hooks/useConversation.ts`
4. `src/lib/hooks/useErrorHandler.ts`
5. `src/lib/hooks/index.ts` (exports)
6. `src/lib/context/SessionContext.tsx`
7. `src/lib/context/ConversationContext.tsx`
8. `src/lib/context/UIContext.tsx`
9. `src/lib/context/providers.tsx`
10. `src/components/ResultsDisplay.tsx` (replaces MockOutput)
11. `src/components/ErrorBoundary.tsx`

### Modify:
1. `src/app/layout.tsx` - Add providers
2. `src/app/page.tsx` - Replace mock flow with real API
3. `src/components/ConversationalForm.tsx` - Use API
4. `src/components/chat/AnalysisPanel.tsx` - Use real data
5. `src/components/autocomplete/AutocompleteInput.tsx` - Real suggestions
6. `src/components/chat/ChatInterface.tsx` - Real message handling

### Remove/Deprecate:
1. `src/components/MockOutput.tsx` - Replace with ResultsDisplay
2. Artificial delays from page.tsx

---

## Success Criteria

✅ **Phase 2 Complete When:**
- [ ] All API calls use real backend endpoints
- [ ] Session management working (localStorage persistence)
- [ ] Message history persists across page reloads
- [ ] No artificial delays in UI
- [ ] Error handling displays user-friendly messages
- [ ] Loading states show during API calls
- [ ] All components use hooks & context
- [ ] No console errors or prop-drilling warnings
- [ ] Chat flow feels natural and responsive

---

## Timeline
- Hooks creation: 30-45 min
- Context setup: 30-45 min
- Component updates: 1-1.5 hours
- Testing & fixes: 30-45 min
- **Total: 2.5-3.5 hours**

---

## Next Steps
1. ✅ Analyze UI components (DONE)
2. Create hooks (`useAnalysis`, `useSession`, `useConversation`)
3. Create context providers
4. Update `src/app/layout.tsx` to use providers
5. Refactor `src/app/page.tsx` to use real API
6. Update individual components to use hooks
7. Test complete flow end-to-end
8. Commit changes with proper messages
