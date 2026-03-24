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
    DashboardRow,
    RowWidth,
    BlockLoadState,
    BlockState,
} from '@ui-gen/base-ui';
export type { BlockCategory, DataContractType, DataContract, BlockSpec, DashboardSpec, DashboardRow, RowWidth, BlockLoadState, BlockState };

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

// ─── Headless pipeline integration ─────────────────────────────────────────────

interface HeadlessBlock {
    block_id: string;
    title: string;
    status: string;
    has_result: boolean;
    data?: any;
    error?: string;
}

export interface HeadlessResult {
    question: string;
    cache_key: string;
    status: 'generated' | 'cached' | 'mock_generated' | 'mock_reused' | 'failed';
    analysis_id?: string;
    execution_id?: string;
    elapsed_s: number;
    total_elapsed_s: number;
    blocks: number;
    blocks_data?: HeadlessBlock[];
    dashboard_id?: string;
    plan_title?: string;
    error?: string;
    response_type?: string;
    mock_data_file?: string;
    similarity?: number;
    steps?: Array<{
        step: string;
        success: boolean;
        duration: number;
    }>;
    // Include original UI Planner blocks
    ui_blocks?: Array<{
        blockId: string;
        category: string;
        title: string;
        dataContract: any;
        sub_question?: string;
        canonical_params?: any;
    }>;
    // Row-based layout from updated UI Planner prompt
    rows?: Array<{
        role: string;
        columns: Array<{
            width: string;
            blockId: string;
            category?: string;
            title?: string;
        }>;
    }>;
    // Grid layout from orchestrator (legacy CreativeGrids)
    layout?: {
        templateId: string;
        slots: Record<string, any>;
    };
    // Legacy fields for compatibility
    cache_hits?: number;
    jobs_enqueued?: number;
    summary?: {
        total: number;
        complete: number;
        failed: number;
        pending: number;
    };
}

// Maps block types from backend to frontend block IDs
const BLOCK_TYPE_MAP: Record<string, string> = {
    'kpi-cards': 'kpi-card-01',
    'line-charts': 'line-chart-01',
    'bar-charts': 'bar-chart-01',
    'bar-lists': 'bar-list-01',
    'donut-charts': 'donut-chart-01',
    'spark-charts': 'spark-chart-01',
    'tables': 'table-01',
    'status-monitoring': 'tracker-01',
};

// Maps backend categories to frontend block categories
const CATEGORY_MAP: Record<string, BlockCategory> = {
    'price': 'kpi-cards',
    'trend': 'line-charts',
    'comparison': 'bar-charts',
    'ranking': 'bar-lists',
    'allocation': 'donut-charts',
    'history': 'line-charts',
    'watchlist': 'spark-charts',
    'table': 'tables',
    'status': 'status-monitoring',
};

function mapBackendToFrontend(backendCategory: string, title: string): { blockId: string; category: BlockCategory } {
    const normalized = backendCategory.toLowerCase().trim();
    const category = CATEGORY_MAP[normalized] || 'kpi-cards';
    const blockId = BLOCK_TYPE_MAP[category] || 'kpi-card-01';
    return { blockId, category };
}

interface PipelineError {
    error: string;
    details?: {
        exitCode?: number;
        step?: string;
        error?: string;
        lastLogs?: string[];
        parseError?: string;
    };
}

export async function runHeadlessPipeline(question: string, options: { useNoCode?: boolean; mock?: boolean; mockV2?: boolean; skipReuse?: boolean; mcpLive?: boolean } = {}): Promise<HeadlessResult> {
    const res = await fetch('/api/headless/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question, useNoCode: options.useNoCode ?? true, mock: options.mock ?? false, mockV2: options.mockV2 ?? false, skipReuse: options.skipReuse ?? false, mcpLive: options.mcpLive ?? false }),
    });

    if (!res.ok) {
        const errorBody = await res.json() as PipelineError;

        // Extract a user-friendly error message from the detailed response
        let userMessage = errorBody.error || 'Dashboard generation failed';

        if (errorBody.details) {
            const { step, error: detailError, parseError, exitCode } = errorBody.details;

            // Build a concise error message with key info only
            const parts: string[] = [];
            if (step && step !== 'Unknown') parts.push(`Step: ${step}`);
            if (detailError) parts.push(detailError);
            if (parseError) parts.push(parseError);
            if (exitCode) parts.push(`Exit code: ${exitCode}`);

            if (parts.length > 0) {
                userMessage = parts.join(' · ');
            }

            // Log full details for debugging but don't include in user message
            console.error('[HeadlessPipeline] Full error details:', errorBody.details);
        }

        throw new Error(userMessage);
    }

    return res.json() as Promise<HeadlessResult>;
}

// ─── Streaming pipeline ───────────────────────────────────────────────────────

export type StreamEvent =
    | { event: 'spec';  title: string; rows: any[]; blocks: any[]; elapsed_s: number }
    | { event: 'block'; blockId: string; data: Record<string, unknown> | null }
    | { event: 'done';  elapsed_s: number }
    | { event: 'error'; message: string };

/**
 * Streams the headless pipeline via SSE.
 * Yields events one by one: spec → block × N → done (or error).
 */
export async function* runHeadlessPipelineStream(
    question: string,
    options: { mock?: boolean; mockV2?: boolean; skipReuse?: boolean; mcpLive?: boolean; blockDelay?: number } = {},
): AsyncGenerator<StreamEvent> {
    const res = await fetch('/api/headless/stream', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            question,
            mock:       options.mock       ?? true,
            mockV2:     options.mockV2     ?? false,
            skipReuse:  options.skipReuse  ?? true,
            mcpLive:    options.mcpLive    ?? false,
            blockDelay: options.blockDelay ?? 300,
        }),
    });

    if (!res.ok || !res.body) throw new Error('Stream request failed');

    const reader  = res.body.getReader();
    const decoder = new TextDecoder();
    let   buf     = '';

    while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        buf += decoder.decode(value, { stream: true });

        // SSE lines are delimited by \n\n
        const parts = buf.split('\n\n');
        buf = parts.pop() ?? '';

        for (const part of parts) {
            const line = part.trim();
            if (!line.startsWith('data:')) continue;
            try {
                yield JSON.parse(line.slice(5).trim()) as StreamEvent;
            } catch { /* ignore malformed chunks */ }
        }
    }
}

// ─── Convert headless result to DashboardSpec ─────────────────────────────────────

function inferContractType(category: BlockCategory): DataContractType {
    if (category === 'line-charts') return 'timeseries';
    if (category === 'bar-lists') return 'ranked-list';
    if (category === 'donut-charts') return 'categorical';
    if (category === 'spark-charts') return 'spark';
    if (category === 'tables') return 'table-rows';
    if (category === 'status-monitoring') return 'tracker';
    return 'kpi';
}

export function headlessResultToSpec(result: HeadlessResult): DashboardSpec {
    // ── If the backend returned rows (new UI Planner format) ──────────────────
    if (result.rows && result.rows.length > 0) {
        // Flatten rows → blocks for BlockState creation in BuilderApp
        const blocks: BlockSpec[] = [];
        const rows: DashboardRow[] = [];

        for (const row of result.rows) {
            const rowColumns: DashboardRow['columns'] = [];

            for (const col of row.columns) {
                // Find matching ui_block for full metadata
                const uiBlock = result.ui_blocks?.find((b) => b.blockId === col.blockId);
                const category = (col.category || uiBlock?.category || 'kpi-cards') as BlockCategory;
                const contractType = inferContractType(category);
                const description = uiBlock?.dataContract?.description || col.title || col.blockId;

                // Only add to blocks if not already present (blockIds can theoretically repeat)
                if (!blocks.find((b) => b.blockId === col.blockId)) {
                    blocks.push({
                        blockId: col.blockId,
                        category,
                        title: col.title || uiBlock?.title || col.blockId,
                        subtitle: (col as any).subtitle || uiBlock?.subtitle,
                        dataContract: {
                            type: contractType,
                            description,
                            points: uiBlock?.dataContract?.points || (contractType === 'timeseries' ? 12 : contractType === 'spark' ? 14 : 5),
                            categories: contractType === 'timeseries' ? ['Value'] : undefined,
                        },
                        sub_question: uiBlock?.sub_question,
                        canonical_params: uiBlock?.canonical_params,
                    });
                }

                rowColumns.push({ width: col.width as RowWidth, blockId: col.blockId });
            }

            rows.push({ role: row.role as DashboardRow['role'], columns: rowColumns });
        }

        return {
            title: result.plan_title || 'Dashboard',
            subtitle: `Generated in ${result.elapsed_s.toFixed(1)}s${result.status === 'cached' ? ' (cached)' : ''}`,
            layout: 'grid',
            blocks,
            rows,
        };
    }

    // ── Legacy flat blocks path (old UI Planner format) ───────────────────────
    const uiBlocks = result.ui_blocks || [];

    const blocks: BlockSpec[] = uiBlocks.map((uiBlock) => {
        const blockId = uiBlock.blockId;
        const category = uiBlock.category as BlockCategory;
        const contractType = inferContractType(category);
        const description = uiBlock.dataContract?.description || uiBlock.title;

        return {
            blockId,
            category,
            title: uiBlock.title,
            subtitle: uiBlock.subtitle,
            dataContract: {
                type: contractType,
                description,
                points: uiBlock.dataContract?.points || (contractType === 'timeseries' ? 12 : contractType === 'spark' ? 14 : 5),
                categories: contractType === 'timeseries' ? ['Value'] : undefined,
            },
        };
    });

    // Extract grid layout if available from orchestrator (legacy CreativeGrids)
    let gridTemplate: any = null;
    let gridSlots: Record<string, string> = {};

    if (result.layout?.templateId) {
        gridTemplate = result.layout.templateId;
        if (result.layout.slots) {
            Object.entries(result.layout.slots).forEach(([slotId, slotConfig]: [string, any]) => {
                if (slotConfig?.blockId) {
                    gridSlots[slotId] = slotConfig.blockId;
                }
            });
        }
    }

    return {
        title: result.plan_title || 'Dashboard',
        subtitle: `Generated in ${result.elapsed_s.toFixed(1)}s${result.status === 'cached' ? ' (cached)' : ''}`,
        layout: 'grid',
        blocks,
        gridTemplate,
        gridSlots,
    };
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
