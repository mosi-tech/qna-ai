/**
 * dashboardAI.ts
 *
 * Calls the server-side /api/ollama proxy (which holds the API key securely).
 * Falls back to local mock specs when the proxy returns 503 (no key configured).
 */

// ─── Types (imported + re-exported from @ui-gen/base-ui — Phase 1) ──────────
// Canonical definitions live in apps/base-ui/src/blocks/types.ts.
import type {
    BlockCategory,
    DataContractType,
    DataContract,
    BlockSpec,
    DashboardSpec,
    BlockLoadState,
    BlockState,
} from '@ui-gen/base-ui';
export type { BlockCategory, DataContractType, DataContract, BlockSpec, DashboardSpec, BlockLoadState, BlockState };

// ─── System prompt ────────────────────────────────────────────────────────────

const SYSTEM_PROMPT = `You are a financial dashboard component planner.

Given a user's natural-language request, you respond ONLY with a valid JSON object (no markdown, no prose) describing the dashboard to build.

Available block IDs and their categories:
- kpi-cards: kpi-card-01 (metrics grid with inline change), kpi-card-03 (period comparison)
- line-charts: line-chart-01 (multi-series with summary), line-chart-03 (single series)
- bar-charts: bar-chart-01 (comparison toggle), bar-chart-05 (simple grouped)
- bar-lists: bar-list-01 (ranked bar list)
- donut-charts: donut-chart-01 (allocation donut)
- spark-charts: spark-chart-01 (multiple tickers/sparklines)
- tables: table-01 (generic sortable table)
- status-monitoring: tracker-01 (status tracker)

Data contract types:
- kpi: array of metric cards with stat + change
- timeseries: date-indexed rows, one column per series
- categorical: [{name, value}] pairs
- ranked-list: [{name, value}] ranked items
- table-rows: columns + rows of arbitrary records
- spark: parallel sparkline series per item
- tracker: array of status ticks

Output schema (JSON only, no other text):
{
  "title": "Dashboard title",
  "subtitle": "One-sentence description",
  "layout": "grid" | "wide",
  "blocks": [
    {
      "blockId": "<block-id>",
      "category": "<category>",
      "title": "Block title",
      "dataContract": {
        "type": "<contract-type>",
        "description": "what this data represents",
        "points": 12,
        "categories": ["Series A", "Series B"]
      }
    }
  ]
}

Rules:
- Include 3 to 7 blocks
- Always start with at least one kpi-cards block
- Pick blocks appropriate for the domain (finance, ops, portfolio, etc.)
- Do NOT include any text outside the JSON
`;

// ─── Internal helper ──────────────────────────────────────────────────────────

const MODEL = 'glm-4.7:cloud';

async function callOllama(messages: { role: string; content: string }[]): Promise<string> {
    const res = await fetch('/api/ollama', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ model: MODEL, stream: false, messages }),
    });

    if (res.status === 503) {
        // Server has no API key configured
        throw new Error('NO_API_KEY');
    }

    if (!res.ok) {
        const text = await res.text();
        throw new Error(`Ollama API returned ${res.status}: ${text}`);
    }

    const json = await res.json();
    return (
        json?.message?.content ??
        json?.choices?.[0]?.message?.content ??
        ''
    );
}

// ─── buildDashboardSpec ───────────────────────────────────────────────────────

export async function buildDashboardSpec(userPrompt: string): Promise<DashboardSpec> {
    let content: string;
    try {
        content = await callOllama([
            { role: 'system', content: SYSTEM_PROMPT },
            { role: 'user', content: userPrompt },
        ]);
    } catch (err: any) {
        if (err?.message === 'NO_API_KEY') {
            console.warn('[dashboardAI] No API key on server — using fallback mock');
            return fallbackSpec(userPrompt);
        }
        throw err;
    }

    const cleaned = content.replace(/```json\s*/gi, '').replace(/```\s*/g, '').trim();
    try {
        return JSON.parse(cleaned) as DashboardSpec;
    } catch {
        console.error('[dashboardAI] Failed to parse model response as JSON:', cleaned);
        throw new Error('Model returned invalid JSON — check server logs for raw response.');
    }
}

// ─── Suggestion generation ────────────────────────────────────────────────────

const SUGGESTION_POOL = [
    'Show me my equity portfolio with holdings, daily P&L, sector allocation and YTD performance',
    'Build an ETF dashboard with returns, expense ratios, tracking error and benchmark comparison',
    'Display a dividend income tracker with payment calendar, yield by holding and payout history',
    'Create a trade history dashboard with win rate, average gain/loss, holding period and strategy breakdown',
    'Show a stock watchlist dashboard with price alerts, 52-week range, volume trends and momentum indicators',
    'Build a retirement account dashboard with contribution tracking, asset allocation and projected balance',
    'Display an options portfolio dashboard with open positions, net premium, expiry timeline and Greeks summary',
    'Show a market movers dashboard with top gainers/losers, volume spikes and sector rotation heatmap',
    'Create a fundamental screener dashboard with P/E, EPS growth, analyst ratings and valuation multiples',
    'Build a technical analysis dashboard with RSI, MACD, Bollinger Bands and moving average signals',
    'Show a tax lot dashboard with cost basis, unrealised gains, holding period and wash sale flags',
    'Display a mutual fund comparison dashboard with NAV history, alpha, Sharpe ratio and category ranking',
];

function shuffleSample(arr: string[], n: number): string[] {
    const copy = [...arr];
    for (let i = copy.length - 1; i > 0; i--) {
        const j = Math.floor(Math.random() * (i + 1));
        [copy[i], copy[j]] = [copy[j], copy[i]];
    }
    return copy.slice(0, n);
}

const SUGGESTIONS_SYSTEM_PROMPT = `You are an AI dashboard builder for retail trading and retail investment platforms. Your job is to suggest realistic questions that self-directed investors, retail traders, or personal finance users would ask when building a portfolio monitoring or market analysis dashboard.

Each question must:
- Be grounded in real retail trading and investment workflows (equities, ETFs, mutual funds, options, dividends, watchlists, trade history, retirement accounts, tax lots, technical analysis, fundamental screening)
- Mention specific trading/investment concepts like: P&L, unrealised gains, cost basis, sector allocation, YTD returns, win rate, holding period, expense ratio, tracking error, dividend yield, ex-dividend date, RSI, MACD, Bollinger Bands, moving averages, volume, momentum, analyst ratings, P/E ratio, EPS growth, Sharpe ratio, alpha, beta, Greeks (delta/theta/vega), expiry, premium, wash sale, tax lot, benchmark, NAV, etc.
- Be phrased as a natural dashboard request (e.g. "Show me...", "Build a...", "Create a...", "Display...")
- Cover different trading/investment domains — do NOT repeat the same area twice

Return ONLY a JSON array of exactly 4 strings. No markdown, no explanation, no code fences.

Example output format:
["Show me my equity portfolio with holdings, daily P&L and sector allocation", "Build an ETF performance dashboard with returns, expense ratios and tracking error", "Display a dividend income calendar with yield by holding and upcoming ex-dates", "Create a trade history dashboard with win rate, average return and strategy breakdown"]`;

export async function generateSuggestions(): Promise<string[]> {
    try {
        const content = await callOllama([
            { role: 'system', content: SUGGESTIONS_SYSTEM_PROMPT },
            {
                role: 'user',
                content:
                    'Generate 4 new dashboard questions for different retail trading and retail investment workflows. Make them specific, varied and grounded in real trading and investment products.',
            },
        ]);

        const cleaned = content.replace(/```json\s*/gi, '').replace(/```\s*/g, '').trim();
        const parsed = JSON.parse(cleaned);
        if (Array.isArray(parsed) && parsed.length >= 1) {
            return (parsed as string[]).slice(0, 4);
        }
    } catch (err: any) {
        console.warn('[dashboardAI] generateSuggestions failed, using fallback:', err?.message);
    }

    return shuffleSample(SUGGESTION_POOL, 4);
}

// ─── Fallback spec (no API key) ───────────────────────────────────────────────

function fallbackSpec(prompt: string): DashboardSpec {
    const lower = prompt.toLowerCase();
    if (lower.includes('portfolio') || lower.includes('fund')) return PORTFOLIO_SPEC;
    if (lower.includes('revenue') || lower.includes('sales') || lower.includes('finance')) return REVENUE_SPEC;
    if (lower.includes('risk') || lower.includes('exposure')) return RISK_SPEC;
    if (lower.includes('trading') || lower.includes('order') || lower.includes('execution')) return TRADING_SPEC;
    return REVENUE_SPEC;
}

// ─── Pre-built fallback specs ─────────────────────────────────────────────────

const PORTFOLIO_SPEC: DashboardSpec = {
    title: 'Portfolio Overview',
    subtitle: 'Key performance indicators, allocation breakdown, and holding price history',
    layout: 'grid',
    blocks: [
        {
            blockId: 'kpi-card-01', category: 'kpi-cards', title: 'Portfolio KPIs',
            dataContract: { type: 'kpi', description: 'AUM, return YTD, Sharpe ratio, drawdown', points: 4 },
        },
        {
            blockId: 'donut-chart-01', category: 'donut-charts', title: 'Asset Allocation',
            dataContract: { type: 'categorical', description: 'Portfolio allocation by asset class', points: 5, categories: ['Equities', 'Bonds', 'Alternatives', 'Cash', 'Real Estate'] },
        },
        {
            blockId: 'line-chart-01', category: 'line-charts', title: 'NAV History',
            dataContract: { type: 'timeseries', description: 'Monthly net asset value vs benchmark', points: 12, categories: ['Portfolio', 'Benchmark'] },
        },
        {
            blockId: 'spark-chart-01', category: 'spark-charts', title: 'Top Holdings',
            dataContract: { type: 'spark', description: 'Price sparklines for top 5 holdings', points: 14, categories: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA'] },
        },
        {
            blockId: 'table-01', category: 'tables', title: 'Position Detail',
            dataContract: { type: 'table-rows', description: 'Individual position P&L, weight, and sector', points: 10 },
        },
    ],
};

const REVENUE_SPEC: DashboardSpec = {
    title: 'Revenue Dashboard',
    subtitle: 'Monthly revenue trends, segment breakdown, and top contributors',
    layout: 'grid',
    blocks: [
        {
            blockId: 'kpi-card-01', category: 'kpi-cards', title: 'Revenue KPIs',
            dataContract: { type: 'kpi', description: 'Total revenue, MoM growth, gross margin, ARR', points: 4 },
        },
        {
            blockId: 'bar-chart-01', category: 'bar-charts', title: 'Monthly Revenue vs Prior Year',
            dataContract: { type: 'timeseries', description: 'Monthly revenue comparison current vs prior year', points: 12, categories: ['This Year', 'Last Year'] },
        },
        {
            blockId: 'donut-chart-01', category: 'donut-charts', title: 'Revenue by Segment',
            dataContract: { type: 'categorical', description: 'Revenue split by business segment', points: 4, categories: ['SaaS', 'Services', 'Licensing', 'Other'] },
        },
        {
            blockId: 'bar-list-01', category: 'bar-lists', title: 'Top Accounts by Revenue',
            dataContract: { type: 'ranked-list', description: 'Top 7 accounts ranked by total revenue', points: 7 },
        },
        {
            blockId: 'line-chart-01', category: 'line-charts', title: 'ARR Growth',
            dataContract: { type: 'timeseries', description: 'Monthly ARR and churn over last 12 months', points: 12, categories: ['ARR', 'Churn'] },
        },
    ],
};

const RISK_SPEC: DashboardSpec = {
    title: 'Risk & Exposure Monitor',
    subtitle: 'VaR, concentration risk, and stress test results',
    layout: 'grid',
    blocks: [
        {
            blockId: 'kpi-card-01', category: 'kpi-cards', title: 'Risk KPIs',
            dataContract: { type: 'kpi', description: 'VaR (95%), CVaR, beta, correlations', points: 4 },
        },
        {
            blockId: 'bar-chart-05', category: 'bar-charts', title: 'Sector Exposure',
            dataContract: { type: 'categorical', description: 'Portfolio exposure by sector (%)', points: 8, categories: ['Exposure %'] },
        },
        {
            blockId: 'line-chart-01', category: 'line-charts', title: 'Rolling VaR',
            dataContract: { type: 'timeseries', description: '30-day rolling VaR (95% and 99%)', points: 30, categories: ['VaR 95%', 'VaR 99%'] },
        },
        {
            blockId: 'tracker-01', category: 'status-monitoring', title: 'Limit Utilisation',
            dataContract: { type: 'tracker', description: 'Daily breaches/ok status for risk limits over last 30 days', points: 30 },
        },
    ],
};

const TRADING_SPEC: DashboardSpec = {
    title: 'Trading Execution Dashboard',
    subtitle: 'Order flow, fill rates, and P&L by strategy',
    layout: 'grid',
    blocks: [
        {
            blockId: 'kpi-card-01', category: 'kpi-cards', title: 'Trading KPIs',
            dataContract: { type: 'kpi', description: 'Total orders, fill rate, slippage, daily P&L', points: 4 },
        },
        {
            blockId: 'line-chart-01', category: 'line-charts', title: 'Intraday P&L',
            dataContract: { type: 'timeseries', description: 'Intraday cumulative P&L by strategy', points: 24, categories: ['Strategy A', 'Strategy B', 'Total'] },
        },
        {
            blockId: 'bar-list-01', category: 'bar-lists', title: 'P&L by Strategy',
            dataContract: { type: 'ranked-list', description: 'Strategies ranked by P&L today', points: 6 },
        },
        {
            blockId: 'table-01', category: 'tables', title: 'Recent Orders',
            dataContract: { type: 'table-rows', description: 'Last 20 orders with status, symbol, qty, price', points: 20 },
        },
    ],
};
