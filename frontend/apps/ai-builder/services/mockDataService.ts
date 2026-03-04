/**
 * mockDataService.ts
 *
 * Generates plausible mock data for any BlockSpec's data contract.
 * Simulates a per-block async API call with random latency (300-1200ms).
 */

import type { BlockSpec, DataContract } from './dashboardAI';

function rand(min: number, max: number): number {
    return Math.random() * (max - min) + min;
}
function randInt(min: number, max: number): number {
    return Math.floor(rand(min, max + 1));
}
function fmt(n: number, decimals = 2): number {
    return parseFloat(n.toFixed(decimals));
}

function walkSeries(steps: number, start: number, drift = 0.01, vol = 0.03): number[] {
    const out = [start];
    for (let i = 1; i < steps; i++) {
        out.push(fmt(out[i - 1] * (1 + drift + (Math.random() - 0.5) * 2 * vol)));
    }
    return out;
}

function dateRange(points: number, interval: 'month' | 'day' | 'hour' = 'month'): string[] {
    const dates: string[] = [];
    const base = new Date('2025-01-01');
    for (let i = 0; i < points; i++) {
        const d = new Date(base);
        if (interval === 'month') d.setMonth(base.getMonth() + i);
        else if (interval === 'day') d.setDate(base.getDate() + i);
        else d.setHours(base.getHours() + i);
        dates.push(
            interval === 'month'
                ? d.toLocaleString('default', { month: 'short', year: '2-digit' })
                : interval === 'day'
                    ? d.toISOString().slice(0, 10)
                    : `${String(d.getHours()).padStart(2, '0')}:00`,
        );
    }
    return dates;
}

const COMPANY_NAMES = [
    'Acme Corp', 'Vertex Capital', 'NovaTech', 'Meridian Ltd', 'Apex Partners',
    'Silverton Funds', 'Luminary Inc', 'Cascade Group', 'Skyline Holdings', 'Atlas Ventures',
];
const SYMBOLS = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'TSLA', 'META', 'JPM', 'GS', 'BAC'];
const STATUS_OPTIONS: Array<'ok' | 'warning' | 'error'> = ['ok', 'ok', 'ok', 'warning', 'error'];

function generateKpi(contract: DataContract) {
    const count = contract.points ?? 4;
    const domains = [
        { name: 'Total AUM', base: 4_200_000_000, suffix: 'M', multiplier: 1e-6, drift: 0.04 },
        { name: 'YTD Return', base: 12.4, suffix: '%', multiplier: 1, drift: 0.1 },
        { name: 'Sharpe Ratio', base: 1.82, suffix: '', multiplier: 1, drift: 0.05 },
        { name: 'Max Drawdown', base: -8.3, suffix: '%', multiplier: 1, drift: -0.05 },
        { name: 'Total Revenue', base: 2_400_000, suffix: 'M', multiplier: 1e-6, drift: 0.07 },
        { name: 'Gross Margin', base: 68.2, suffix: '%', multiplier: 1, drift: 0.03 },
        { name: 'Fill Rate', base: 97.4, suffix: '%', multiplier: 1, drift: 0.01 },
        { name: 'Daily P&L', base: 125_000, suffix: 'K', multiplier: 1e-3, drift: 0.2 },
    ];
    const desc = contract.description.toLowerCase();
    let pool = domains;
    if (desc.includes('revenue')) pool = domains.filter(d => d.name.toLowerCase().includes('revenue') || d.name.includes('Margin'));
    if (desc.includes('portfolio') || desc.includes('aum')) pool = domains.slice(0, 4);
    if (desc.includes('trading') || desc.includes('order')) pool = domains.slice(4);
    const picked = pool.slice(0, count);
    return {
        metrics: picked.map((d) => {
            const changeVal = fmt(d.base * d.drift);
            const changePct = fmt((changeVal / Math.abs(d.base)) * 100, 1);
            const isNeg = d.drift < 0;
            const display = d.multiplier !== 1
                ? `${d.suffix}${fmt(d.base * d.multiplier, 1)}`
                : `${fmt(d.base, 2)}${d.suffix}`;
            return {
                name: d.name,
                stat: display,
                change: `${isNeg ? '' : '+'}${changePct}%`,
                changeType: isNeg ? 'negative' : 'positive',
            };
        }),
        cols: count <= 2 ? count : count <= 4 ? 4 : 3,
    };
}

function generateTimeseries(contract: DataContract) {
    const points = contract.points ?? 12;
    const cats = contract.categories ?? ['Value'];
    const dates = dateRange(points, points <= 24 ? (points <= 30 ? 'day' : 'hour') : 'month');
    const series: Record<string, number[]> = {};
    cats.forEach((c) => { series[c] = walkSeries(points, rand(50, 500), rand(0.005, 0.015), rand(0.02, 0.05)); });
    const data = dates.map((date, i) => {
        const row: Record<string, unknown> = { date };
        cats.forEach((c) => (row[c] = series[c][i]));
        return row;
    });
    const summary = cats.map((c) => ({ name: c, value: series[c][series[c].length - 1] }));
    return { data, categories: cats, summary };
}

function generateCategorical(contract: DataContract) {
    const cats = contract.categories ?? Array.from({ length: contract.points ?? 5 }, (_, i) => `Category ${i + 1}`);
    const total = 1000;
    const raw = cats.map(() => rand(50, 400));
    const sum = raw.reduce((a, b) => a + b, 0);
    return {
        data: cats.map((name, i) => ({
            name,
            value: fmt((raw[i] / sum) * total, 0),
            share: `${fmt((raw[i] / sum) * 100, 1)}%`,
        })),
    };
}

function generateRankedList(contract: DataContract) {
    const count = contract.points ?? 7;
    const names = contract.categories ?? COMPANY_NAMES.slice(0, count);
    const values = Array.from({ length: count }, () => randInt(50_000, 2_000_000));
    values.sort((a, b) => b - a);
    return { data: names.map((name, i) => ({ name, value: values[i] })) };
}

function generateTableRows(contract: DataContract) {
    const desc = contract.description.toLowerCase();
    const count = contract.points ?? 10;

    if (desc.includes('position') || desc.includes('holding')) {
        const columns = [
            { key: 'symbol', label: 'Symbol' }, { key: 'sector', label: 'Sector' },
            { key: 'weight', label: 'Weight %' }, { key: 'pnl', label: 'P&L' }, { key: 'status', label: 'Status' },
        ];
        const sectors = ['Technology', 'Finance', 'Healthcare', 'Consumer', 'Energy'];
        const rows = SYMBOLS.slice(0, count).map((sym) => ({
            symbol: sym, sector: sectors[randInt(0, sectors.length - 1)],
            weight: `${fmt(rand(1, 15), 1)}%`, pnl: `$${(randInt(-50000, 200000) / 1000).toFixed(1)}K`,
            status: Math.random() > 0.15 ? 'active' : 'inactive',
        }));
        return { columns, rows };
    }

    if (desc.includes('order')) {
        const columns = [
            { key: 'time', label: 'Time' }, { key: 'symbol', label: 'Symbol' }, { key: 'side', label: 'Side' },
            { key: 'qty', label: 'Qty' }, { key: 'price', label: 'Price' }, { key: 'status', label: 'Status' },
        ];
        const sides = ['Buy', 'Sell'];
        const statuses = ['executed', 'pending', 'rejected'];
        const rows = Array.from({ length: count }, (_, i) => ({
            time: `${String(9 + Math.floor(i / 3)).padStart(2, '0')}:${String((i * 13) % 60).padStart(2, '0')}`,
            symbol: SYMBOLS[randInt(0, SYMBOLS.length - 1)], side: sides[randInt(0, 1)],
            qty: randInt(100, 5000), price: `$${fmt(rand(50, 800))}`,
            status: statuses[Math.random() < 0.8 ? 0 : Math.random() < 0.5 ? 1 : 2],
        }));
        return { columns, rows };
    }

    const columns = [
        { key: 'name', label: 'Name' }, { key: 'value', label: 'Value' },
        { key: 'change', label: 'Change' }, { key: 'status', label: 'Status' },
    ];
    const rows = COMPANY_NAMES.slice(0, count).map((name) => ({
        name, value: `$${fmt(rand(100, 10000))}`,
        change: `${Math.random() > 0.5 ? '+' : '-'}${fmt(rand(0.5, 8), 1)}%`,
        status: Math.random() > 0.2 ? 'active' : 'inactive',
    }));
    return { columns, rows };
}

function generateSpark(contract: DataContract) {
    const seriesNames = contract.categories ?? SYMBOLS.slice(0, 5);
    const points = contract.points ?? 14;
    const dates = dateRange(points, 'day');
    const seriesData: Record<string, number[]> = {};
    seriesNames.forEach((s) => { seriesData[s] = walkSeries(points, rand(50, 500), rand(-0.005, 0.015), 0.02); });
    const data = dates.map((date, i) => {
        const row: Record<string, unknown> = { date };
        seriesNames.forEach((s) => (row[s] = seriesData[s][i]));
        return row;
    });
    const items = seriesNames.map((name) => {
        const series = seriesData[name];
        const first = series[0];
        const last = series[series.length - 1];
        const changePct = fmt(((last - first) / first) * 100, 2);
        return {
            id: name, name, dataKey: name, value: `$${fmt(last)}`,
            change: `${changePct >= 0 ? '+' : ''}${changePct}%`,
            changeType: changePct >= 0 ? 'positive' : 'negative',
        };
    });
    return { data, items };
}

function generateTracker(contract: DataContract) {
    const count = contract.points ?? 30;
    return { data: Array.from({ length: count }, () => ({ status: STATUS_OPTIONS[randInt(0, STATUS_OPTIONS.length - 1)] })) };
}

export async function fetchMockData(block: BlockSpec): Promise<Record<string, unknown>> {
    const delay = randInt(300, 1200);
    await new Promise((r) => setTimeout(r, delay));
    const { dataContract } = block;
    switch (dataContract.type) {
        case 'kpi': return generateKpi(dataContract);
        case 'timeseries': return generateTimeseries(dataContract);
        case 'categorical': return generateCategorical(dataContract);
        case 'ranked-list': return generateRankedList(dataContract);
        case 'table-rows': return generateTableRows(dataContract);
        case 'spark': return generateSpark(dataContract);
        case 'tracker': return generateTracker(dataContract);
        default: return {};
    }
}
