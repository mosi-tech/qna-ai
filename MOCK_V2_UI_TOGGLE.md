# Mock V1/V2 Toggle in AI Builder UI

## What Was Added

A new **"Decompose"** toggle button in the AI Builder header that allows you to switch between Mock V1 (single-shot planning) and Mock V2 (hierarchical decomposition) modes directly from the UI.

**Note**: Both modes still process **one user question at a time**. The difference is how that question is handled:
- **V1**: Plans dashboard blocks directly
- **V2**: Decomposes question into atomic sub-questions first

### UI Location

In the top header next to "Mock" and "Skip Cache" toggles:

```
┌─────────────────────────────────────────────────────────┐
│ ✦ AI Dashboard Builder                                  │
│                              Mock  Skip Cache  Decompose │
│                              ────  ──────────  ─────────│
│                               ☑️    ☑️          ☐        │
└─────────────────────────────────────────────────────────┘
```

## How It Works

### Behavior

- **Decompose toggle only appears when Mock is enabled** (conditional rendering)
- **Decompose toggle is purple** when enabled (vs amber for Mock, orange for Skip Cache)
- **Both V1 and V2 return same output format** (blocks + blocks_data)
- **Both still process ONE question** from the user

### State Management

```typescript
// BuilderApp.tsx
const [mockMode, setMockMode] = useState(true);          // Mock enable/disable
const [mockV2Mode, setMockV2Mode] = useState(false);     // V2 batch decomposition
const [skipReuse, setSkipReuse] = useState(true);        // Skip cache
```

### Execution Modes

| Mock | Decompose | Command | Behavior |
|------|-----------|---------|----------|
| ☐ | ☐ | (none) | Normal code generation path |
| ☑️ | ☐ | `--mock` | **V1**: Plan blocks from question + mock data |
| ☑️ | ☑️ | `--mock --mock-v2` | **V2**: Decompose to sub-Qs + mock data per sub-Q |

## Implementation Details

### Files Modified

1. **`frontend/apps/ai-builder/components/BuilderApp.tsx`**
   ```typescript
   // Added state
   const [mockV2Mode, setMockV2Mode] = useState(false);

   // Added to handleSend
   headlessResult = await runHeadlessPipeline(text, {
     useNoCode: true,
     mock: mockMode,
     mockV2: mockV2Mode,    // ← NEW
     skipReuse
   });

   // Added UI toggle (conditional on mockMode)
   {mockMode && (
     <label className="flex items-center gap-1.5...">
       <input
         type="checkbox"
         checked={mockV2Mode}
         onChange={(e) => setMockV2Mode(e.target.checked)}
       />
       <span>V2 (Batch)</span>
     </label>
   )}
   ```

2. **`frontend/apps/ai-builder/services/dashboardAI.ts`**
   ```typescript
   export async function runHeadlessPipeline(
     question: string,
     options: {
       useNoCode?: boolean;
       mock?: boolean;
       mockV2?: boolean;      // ← NEW
       skipReuse?: boolean;
     }
   )

   // Pass to API
   body: JSON.stringify({
     question,
     useNoCode: options.useNoCode ?? true,
     mock: options.mock ?? false,
     mockV2: options.mockV2 ?? false,  // ← NEW
     skipReuse: options.skipReuse ?? false
   })
   ```

3. **`frontend/apps/ai-builder/app/api/headless/run/route.ts`**
   ```typescript
   // Parse from request
   const { question, useNoCode, mock, mockV2, skipReuse } = body;

   // Add flag to args
   if (mockV2) {
     args.push('--mock-v2');
     console.log(`🎯 MOCK V2 (Batch Decomposition) ENABLED`);
   }
   ```

## Usage Guide

### Test V1 (Default Mock Mode)

1. Toggle **Mock** = ON
2. Toggle **V2** = OFF (or hidden since not enabled)
3. Ask a question: `"Show me my equity portfolio with holdings and daily P&L"`
4. **Expected**: UI Planner generates blocks in one shot, mock data generated together

### Test V2 (Batch Decomposition)

1. Toggle **Mock** = ON
2. Toggle **V2** = ON ← Now visible
3. Ask a question: `"Show me my equity portfolio with holdings and daily P&L"`
4. **Expected**: Question decomposed into 3 sub-questions, each gets mock data independently

### Switching Between Modes

You can toggle between V1 and V2 **without restarting** the app:

```
Question 1 (V1 mode) → Dashboard renders
[Toggle V2 ON]
Question 2 (V2 mode) → Dashboard renders with different decomposition
[Toggle V2 OFF]
Question 3 (V1 mode) → Back to single-shot mode
```

## Visual Design

### Toggle Styling

```css
/* Enabled state (purple for V2) */
.peer-checked:bg-purple-500

/* Disabled state (gray) */
.bg-slate-200 dark:bg-slate-700

/* Smooth transition */
.transition-colors

/* Indicator position */
.translate-x-4  /* when enabled */
/* default left (when disabled) */
```

### Conditional Display

The V2 toggle only renders when Mock is enabled:

```tsx
{mockMode && (
  <label>
    {/* V2 toggle UI */}
  </label>
)}
```

This prevents confusion and clarifies that V2 is a variant of Mock mode.

## Testing Checklist

- [ ] **Toggle visibility**: Decompose toggle only shows when Mock is ON
- [ ] **Toggle colors**: Mock=amber, Decompose=purple, Skip Cache=orange
- [ ] **V1 mode**: Ask question with Decompose OFF, verify direct block planning
- [ ] **V2 mode**: Ask question with Decompose ON, verify question decomposition
- [ ] **Switch modes**: Toggle Decompose between requests, verify both work
- [ ] **Data rendering**: Both modes show data correctly in dashboard
- [ ] **Server logs**: Check `--mock-v2` flag in logs when Decompose enabled
- [ ] **Performance**: V1 and V2 have reasonable response times

## Browser Console Logging

When V2 is enabled, you'll see in the server logs:

```
[2026-03-18T22:31:14] [headless/run] POST received: {
  question: "Which sectors...",
  useNoCode: true,
  mock: true,
  mockV2: true,              ← V2 enabled
  skipReuse: true
}

[2026-03-18T22:31:14] [headless/run] 🎯 MOCK V2 (Batch Decomposition) ENABLED

[2026-03-18T22:31:14] [headless/run] Executing orchestrator with args:
  --question "Which sectors..." --mock --mock-v2 --skip-enhancement
```

## Troubleshooting

### V2 toggle doesn't appear

**Check**: Is Mock toggle enabled?
- V2 toggle only shows when `mockMode === true`
- Toggle Mock ON first, then V2 will appear

### V2 toggle doesn't work

**Check**: Browser dev console for errors
```javascript
// Should see this in network request
{ question: "...", mock: true, mockV2: true, ... }
```

### Different results between V1 and V2

This is **expected and normal**:
- V1: LLM decomposes in one shot → consistent structure, may miss nuances
- V2: LLM decomposes into sub-Qs → more detailed, different decomposition each time (LLM variance)

Both return same format, just decomposed differently.

### Performance difference

**V2 may be slower** due to extra LLM decomposition step:
- V1: ~1-2 seconds
- V2: ~60-100 seconds (includes batch decomposition LLM call)

This is fine for testing/development. Production should use real data generation.

## Future Enhancements

1. **Save/compare results**: Add button to compare V1 vs V2 side-by-side
2. **Toggle indicator**: Show which version generated the current dashboard
3. **Detailed metrics**: Display decomposition count, timing per sub-Q
4. **Export decomposition**: Download the sub-questions JSON

## Code Changes Summary

| File | Changes | Purpose |
|------|---------|---------|
| BuilderApp.tsx | +1 state var, +1 UI toggle, +1 param | UI toggle and state |
| dashboardAI.ts | +1 type param, +1 JSON field | API call with mockV2 |
| route.ts | +3 lines | Parse mockV2, add --mock-v2 flag, logging |

**Total**: ~15 lines of code added
**Complexity**: Low (simple conditional rendering + flag passing)
**Impact**: Zero breaking changes, fully backward compatible

---

## Working Example

### Step 1: Enable Toggles
```
Mock:        ☑️  (ON)
Decompose:   ☑️  (ON)  ← Now visible (breaks question into sub-Qs)
Skip Cache:  ☑️  (ON)
```

### Step 2: Ask Question
```
User: "Which sectors in my portfolio are performing best?"
```

### Step 3: Backend Processing
```
Step 1: UI Planner Batch V2
  ↓
  Decompose into:
  - Sub-Q1: "What is sector allocation?"
  - Sub-Q2: "What is each sector's performance?"
  - Sub-Q3: "Which sectors rank highest?"

Step 2: Mock V2 Generator
  ↓
  Generate mock data for each sub-Q:
  - Donut chart: 33% A, 17% B, 19% C, 31% D
  - Bar chart: A:37%, B:87%, C:55%, D:40%
  - Bar list: Ranked top 5 sectors
```

### Step 4: Dashboard Renders
```
┌─────────────────────────────────────────┐
│ Portfolio Sector Performance             │
├─────────────────────────────────────────┤
│                                         │
│  ◯ Sector Allocation (Donut)           │
│  A:33% B:17% C:19% D:31%               │
│                                         │
│  📊 Sector Performance Returns (Bar)    │
│  B: 87% │████████░░                     │
│  A: 37% │███░░░░░░░                     │
│  C: 55% │█████░░░░░                     │
│  D: 40% │████░░░░░░                     │
│                                         │
│  🏆 Top Performing Sectors (List)       │
│  1. Item A: 49.3%                       │
│  2. Item E: 46.9%                       │
│  3. Item B: 41.7%                       │
│  4. Item C: 34.5%                       │
│  5. Item D: 18.6%                       │
│                                         │
└─────────────────────────────────────────┘
```

Perfect! V1/V2 toggle is ready to use! 🎉
