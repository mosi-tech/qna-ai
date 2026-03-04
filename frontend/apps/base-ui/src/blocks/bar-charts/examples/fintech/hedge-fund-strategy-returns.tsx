import React from 'react';
import { BarChart03 } from '../../';
import type { BarChartDataItem } from '../../bar-chart-03';

const data: BarChartDataItem[] = [
    { strategy: 'Global Macro', 'YTD 2026': 312, 'YTD 2025': 445 },
    { strategy: 'Long/Short Eq.', 'YTD 2026': 587, 'YTD 2025': 412 },
    { strategy: 'Event Driven', 'YTD 2026': 234, 'YTD 2025': 389 },
    { strategy: 'Merger Arb', 'YTD 2026': 178, 'YTD 2025': 156 },
    { strategy: 'Distressed', 'YTD 2026': -89, 'YTD 2025': 267 },
    { strategy: 'CTA / Trend', 'YTD 2026': 421, 'YTD 2025': 198 },
    { strategy: 'Convertible Arb', 'YTD 2026': 145, 'YTD 2025': 331 },
    { strategy: 'Multi-Strategy', 'YTD 2026': 356, 'YTD 2025': 384 },
];

const summary = [
    {
        label: 'YTD 2026',
        value: '+268 bps avg',
        color: 'bg-blue-500 dark:bg-blue-500',
        change: '+12% vs prior YTD',
    },
    {
        label: 'YTD 2025',
        value: '+320 bps avg',
        color: 'bg-cyan-500 dark:bg-cyan-500',
    },
];

export const HedgeFundStrategyReturns = () => (
    <BarChart03
        data={data}
        indexField="strategy"
        title="Hedge Fund Strategy Returns — YTD 2026 vs YTD 2025"
        description="Illustrative data. Gross return in basis points as of Feb 27, 2026."
        categories={['YTD 2026', 'YTD 2025']}
        colors={['blue', 'cyan']}
        summary={summary}
        valueFormatter={(v) => `${v > 0 ? '+' : ''}${v}bps`}
    />
);
