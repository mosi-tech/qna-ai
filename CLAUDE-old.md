# QnA AI Admin - Claude Developer Guide

## Project Overview
This is a Next.js prototype application that creates a QnA-driven visualization workflow for financial data. The app features a two-panel interface where users can ask investment/trading questions and preview corresponding data visualizations.

## Key Components
- **Left Panel (30%)**: QnA chat interface for investment questions
- **Right Panel (70%)**: Visual layer showing financial data visualizations
- **Data Storage**: JSON files (`data/experimental.json`, `data/approved.json`) for persistence
- **Visual Registry**: Components stored in `experimental/` directory with metadata

## Development Workflow

### Starting Development
```bash
npm install
npm run dev
# App runs at http://localhost:3000
```

### Build and Production
```bash
npm run build
npm run start
npm run lint
```

## Role-Based Interaction Pattern

### Phase 1: Retail Investor (Question Generation)
- Act as a retail investor asking relevant investment/trading questions
- Questions should be singular and not contain "add"
- Ensure questions are distinct from existing ones in `data/approved.json` and `data/experimental.json`
- **IMPORTANT**: Questions must be answerable using APIs listed in:
  - `alpaca.marketdata.spec.json`
  - `alpaca.trading.spec.json` 
  - `EODHD.spec.json`
- **CRITICAL**: Don't create questions that can't be answered using above specs
- All questions should be answerable either directly using the specs or through Python analysis based on data from specs

### **CRITICAL VALIDATION PROCESS:**
1. **Generate Initial Question**: Create a question you think can be answered using available APIs
2. **Create Workflow**: Generate detailed step-by-step workflow using specific API endpoints
3. **Validate Alignment**: Check if the workflow actually answers the specific question asked
4. **Iterate if Needed**: If workflow doesn't fully answer the question, adjust the question to match what the workflow can deliver
5. **Repeat**: Continue steps 2-4 until question and workflow are perfectly aligned

**Example Validation:**
- Question: "What stocks have the highest volatility?" 
- Workflow: Uses most-active stocks screener first
- Validation Issue: This answers "highest volatility among active stocks" not "highest volatility overall"
- Adjusted Question: "What actively traded stocks have the highest volatility over the past 30 days?"

- Write the question in the left panel

### Phase 2: Financial Advisor/Quant/Accountant (Solution Creation)
- Switch to advisor/quant/accountant or trading customer service role
- Create visual components or interactive tools to answer the question
- **IMPORTANT: Build professional, modern UI components using:**
  - **shadcn/ui** for high-quality UI components (buttons, cards, tables, etc.)
  - **visx or recharts** for data visualizations and charts
  - **Modern CSS/Tailwind** for styling
  - **Interactive elements** and smooth animations
  - **Professional color schemes** and typography
  - **Responsive design** patterns
- **Visuals should be visually appealing, production-ready, and follow modern UI/UX best practices**
- **Avoid basic HTML tables and simple divs - use proper component libraries**
- **Follow similar UI patterns and use same libraries as existing components**
- **Build on existing component patterns and structures**
- Options include:
  - Complete visual components (directly answering using API specs)
  - Interactive components allowing user exploration
  - Python-based code in `engine/` folder for data processing if needed

## Existing Visuals (Avoid Duplicating)
- Account Overview: Buying power, cash, top positions
- News (AAPL): Latest headlines for AAPL over 24h
- Forex USD/JPY: Latest mid prices and recent changes
- Bar Chart: Generic visualization for account data
- Stats Card: Summary metric cards with trends

## Available APIs
- **Alpaca Market Data** (`alpaca.marketdata.spec.json`): Stock pricing, options, crypto, forex, logos, corporate actions, screener, news
- **Alpaca Trading** (`alpaca.trading.spec.json`): Account management, positions, orders, portfolio management  
- **EODHD** (`EODHD.spec.json`): Additional financial data endpoints

## Adding New Visuals
1. Create component in `experimental/` (e.g., `MyVisual.tsx`)
   - **Follow existing UI patterns and component structures**
   - **Use same libraries and styling approaches as existing components**
2. Register in `experimental/registry.ts` with unique ID, name, file path
3. Add entry to **beginning** of `data/experimental.json` so it appears first on main screen
4. Entry metadata should include:
   - `id`, `name`, `file`, `question` (required)
   - `description`, `apis`, `followUp` (optional)
5. **New visuals automatically appear on main screen for approval/preview**

## Data Model Structure
```jsonc
{
  "id": "unique-id",
  "name": "Display Name",
  "file": "experimental/Component.tsx",
  "description": "Brief description",
  "question": "What question does this answer?",
  "apis": ["marketdata:/endpoint", "trading:/endpoint"],
  "followUp": ["Related question suggestions"],
  "workflow": [
    "Step 1: Get list of active stocks using /v1beta1/screener/stocks/most-actives",
    "Step 2: Fetch 30-day historical data using /v2/stocks/bars with timeframe=1Day",
    "Step 3: Calculate volatility metrics from OHLC data",
    "Step 4: Rank and display results"
  ]
}
```

**IMPORTANT**: The `workflow` field must contain a detailed step-by-step approach to get the required data using the available API specifications. Each step should specify the exact API endpoint, parameters, and data processing required.

## File Structure
- `pages/index.tsx`: Main QnA interface with auto-preview
- `pages/experimental.tsx`: Manage experimental visuals
- `pages/approved.tsx`: Manage approved visuals
- `pages/api/`: File-backed API routes (approve, unapprove, etc.)
- `experimental/`: Visual components and registry
- `data/`: JSON persistence files
- `engine/`: Python code for data processing (if needed)

## Development Notes
- No database - uses file-based JSON storage
- Visual components can accept optional props like `position`
- Promotion/demotion preserves all metadata between experimental and approved
- Server-side Alpaca API integration needed for production (keys in env)
- No authentication implemented - add before production deployment