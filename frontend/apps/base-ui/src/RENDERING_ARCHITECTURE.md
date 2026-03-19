# finBlocks & Views Rendering Architecture

## Overview

```
User Question
    ↓
Question Classifier (intentClassifier.ts)
    ↓
View ID (e.g., "portfolio-daily-check")
    ↓
DashboardViewerPage (renders the view)
    ↓
Views (composes finBlocks)
    ↓
finBlocks (wraps Tremor blocks)
    ↓
Tremor Components (actual UI)
    ↓
Rendered Dashboard
```

## Component Hierarchy

### Level 1: Pages (Frontend Entry Points)
```
frontend/apps/base-ui/src/pages/
├── DashboardViewerPage.tsx    ← Main rendering page for all views
├── BuildProgressPage.tsx      ← Agent progress monitoring
└── [future pages]
```

### Level 2: Views (Dashboard Layouts)
```
frontend/apps/base-ui/src/views/pages/
├── portfolio/
│   ├── portfolio-daily-check.tsx          (composes 4 finBlocks)
│   ├── portfolio-performance-review.tsx   (composes 6 finBlocks)
│   └── ... (12 total)
├── stock_research/
│   ├── stock-quick-research.tsx
│   └── ... (12 total)
└── ... (11 categories, 105 total views)
```

**Each View:**
- Imports finBlocks it needs
- Arranges them in layout
- Handles data fetching orchestration
- Passes data to finBlocks

Example:
```tsx
import { PortfolioKpiSummary } from '@/finBlocks/components/portfolio/portfolio-kpi-summary';
import { HoldingsTable } from '@/finBlocks/components/portfolio/holdings-table';

export const PortfolioDailyCheck = ({ data }) => {
  return (
    <div className="space-y-6">
      <PortfolioKpiSummary data={data.kpiData} />
      <HoldingsTable data={data.holdingsData} />
      {/* ... more finBlocks */}
    </div>
  );
};
```

### Level 3: finBlocks (Financial Domain Wrappers)
```
frontend/apps/base-ui/src/finBlocks/components/
├── portfolio/
│   ├── portfolio-kpi-summary.tsx      (wraps KpiCard01)
│   ├── holdings-table.tsx             (wraps Table01)
│   ├── sector-allocation-donut.tsx    (wraps DonutChart01)
│   └── ... (12 total)
├── stock_research/
│   ├── stock-price-kpi.tsx
│   └── ... (12 total)
└── ... (11 categories, 110 total finBlocks)
```

**Each finBlock:**
- Imports ONE Tremor component by `blockCatalogRef`
- Accepts financial data matching `dataContract`
- Transforms to Tremor props
- Renders the Tremor component

Example:
```tsx
import { KpiCard01 } from '../../../blocks/kpi-cards/kpi-card-01';

export interface PortfolioKpiSummaryData {
  metrics: Array<{ name: string; stat: number; change: string; changeType: 'positive' | 'negative' }>;
  cols: number;
}

export const PortfolioKpiSummary = ({ data = SAMPLE_DATA }) => {
  return <KpiCard01 metrics={data.metrics} cols={data.cols} />;
};
```

### Level 4: Tremor Blocks (Generic UI Components)
```
frontend/apps/base-ui/src/blocks/
├── kpi-cards/
│   ├── kpi-card-01.tsx
│   ├── kpi-card-02.tsx
│   └── ... (5+ variants)
├── tables/
│   ├── table-01.tsx
│   └── ... (7+ variants)
├── line-charts/
│   ├── line-chart-01.tsx
│   └── ... (7+ variants)
└── ... (10 block types, 78+ total variants)
```

**Pure UI, no financial logic:**
- Tremor UI library components
- Fully tested and reusable
- Type-safe props
- Accessible, responsive design

## Data Flow

### Step 1: Question → Intent
```
User: "Show my portfolio"
         ↓ (intentClassifier.ts)
View ID: "portfolio-daily-check"
```

### Step 2: View → finBlocks
```
VIEWS_CATALOG:
{
  "viewId": "portfolio-daily-check",
  "finBlocks": [
    "portfolio-kpi-summary",
    "holdings-table",
    "sector-allocation-donut",
    "price-movements-spark"
  ]
}
```

### Step 3: Fetch Data via Orchestrator
```
mcpDispatcher.fetchViewData("portfolio-daily-check")
  ↓
Get MCP calls for this view:
  - get_account()
  - get_positions()
  - get_portfolio_history()
  - get_real_time_data()
  ↓
Execute all in parallel (3-5 seconds)
  ↓
DataMapper transforms MCP response:
  MCP: { account: { equity: 120000 }, positions: [...] }
  ↓ (map to finBlock contracts)
  Output: {
    "portfolio-kpi-summary": { metrics: [...] },
    "holdings-table": { rows: [...] },
    ...
  }
```

### Step 4: Render View
```
<PortfolioDailyCheck data={orchestratedData} />
  ↓
<PortfolioKpiSummary data={data['portfolio-kpi-summary']} />
  ↓
<KpiCard01 metrics={[...]} />
  ↓
HTML/CSS
```

## File Organization

```
frontend/apps/base-ui/src/
├── pages/
│   ├── DashboardViewerPage.tsx        ← Main rendering entry
│   ├── BuildProgressPage.tsx          ← Agent monitoring
│   └── index.ts
├── views/
│   ├── pages/                         ← View components (generated)
│   │   ├── portfolio/
│   │   ├── stock_research/
│   │   └── ... (11 categories)
│   ├── index.ts                       ← Exports all views
│   ├── viewRouter.ts                  ← Route mappings (generated)
│   └── VIEWS_CATALOG.json
├── finBlocks/
│   ├── components/                    ← finBlock components (generated)
│   │   ├── portfolio/
│   │   ├── stock_research/
│   │   └── ... (11 categories)
│   ├── index.ts                       ← Exports all finBlocks
│   ├── finBlockRegistry.ts            ← Runtime index (generated)
│   └── FINBLOCK_CATALOG.json
├── blocks/                            ← Generic Tremor blocks (existing)
│   ├── kpi-cards/
│   ├── tables/
│   ├── line-charts/
│   └── ... (10 types, 78 variants)
├── classifier/
│   ├── intentClassifier.ts            ← Question → view ID (generated)
│   ├── classifierTraining.json        ← Intent mappings (generated)
│   └── classifierTests.ts
└── ... (other UI files)
```

## Rendering Flow in Code

### 1. User asks question
```tsx
const question = "Show my portfolio";
```

### 2. Classify to view
```tsx
import { classifyQuestion } from '@/classifier/intentClassifier';

const result = await classifyQuestion(question);
// result = { viewId: "portfolio-daily-check", confidence: 0.95 }
```

### 3. Fetch data
```tsx
import { MCPDispatcher } from '@/services/mcpDispatcher';

const dispatcher = new MCPDispatcher();
const data = await dispatcher.fetchViewData('portfolio-daily-check');
// Returns: { "portfolio-kpi-summary": {...}, "holdings-table": {...}, ... }
```

### 4. Render view
```tsx
import { PortfolioDailyCheck } from '@/views/pages/portfolio/portfolio-daily-check';

return <PortfolioDailyCheck data={data} />;
```

## Rendering Pages Available

### 1. **DashboardViewerPage** (Current)
```
frontend/apps/base-ui/src/pages/DashboardViewerPage.tsx
```
- Accepts `viewId` prop
- Loads view definition from VIEWS_CATALOG
- Fetches data via MCPDispatcher
- Renders view with finBlocks
- Shows finBlock placeholders until generated

Usage:
```tsx
<DashboardViewerPage viewId="portfolio-daily-check" />
```

Route:
```
/dashboard/:viewId
/dashboard/portfolio-daily-check
/dashboard/stock-quick-research
```

### 2. **BuildProgressPage** (Exists)
```
frontend/apps/base-ui/src/pages/BuildProgressPage.tsx
```
- Real-time agent build progress
- Shows all 4 phases
- Category-level breakdown
- Agent status with last checkin

Route:
```
/build-progress
```

## What Gets Rendered Where

| Component | File | Renders Via |
|-----------|------|------------|
| **finBlocks** | `finBlocks/components/[cat]/[id].tsx` | Views (imported) |
| **Views** | `views/pages/[cat]/[id].tsx` | DashboardViewerPage (dynamic import) |
| **Pages** | `pages/*.tsx` | App routing (Next.js/routing config) |

## When Components Are Ready

After finblock-builder and view-builder agents complete:

✅ **Ready to render:**
- 110 finBlock wrappers exist
- 105 View components exist
- Intent classifier works
- MCP orchestrator works
- DashboardViewerPage ready to use

**Test rendering:**
```bash
# View a specific view
http://localhost:3000/dashboard/portfolio-daily-check

# Monitor build progress
http://localhost:3000/build-progress
```

## Next Steps

1. ✅ Create DashboardViewerPage (done)
2. ⏳ Run finblock-builder agent (generates 110 finBlock wrappers)
3. ⏳ Run view-builder agent (generates 105 View components)
4. ⏳ Test DashboardViewerPage rendering
5. ⏳ Integrate into main app routing

---

**Architecture Summary:**
- **finBlocks** = Financial domain wrappers around Tremor blocks
- **Views** = Layouts that compose multiple finBlocks
- **DashboardViewerPage** = Entry point that renders any view
- **Complete rendering** = Question → Classifier → View → finBlocks → Tremor → UI
