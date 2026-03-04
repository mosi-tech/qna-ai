import React from 'react';
import { BarChart01 } from '../../';
import type { BarChartDataItem } from '../../bar-chart-01';

const data: BarChartDataItem[] = [
    { date: 'Jan 25', 'FY 2025': 4_820_000, 'FY 2024': 3_110_000 },
    { date: 'Feb 25', 'FY 2025': 6_340_000, 'FY 2024': 5_220_000 },
    { date: 'Mar 25', 'FY 2025': -1_250_000, 'FY 2024': 4_780_000 },
    { date: 'Apr 25', 'FY 2025': 7_890_000, 'FY 2024': 2_950_000 },
    { date: 'May 25', 'FY 2025': 5_410_000, 'FY 2024': -980_000 },
    { date: 'Jun 25', 'FY 2025': 3_670_000, 'FY 2024': 6_120_000 },
    { date: 'Jul 25', 'FY 2025': 8_230_000, 'FY 2024': 5_870_000 },
    { date: 'Aug 25', 'FY 2025': -2_410_000, 'FY 2024': -1_560_000 },
    { date: 'Sep 25', 'FY 2025': 4_100_000, 'FY 2024': 3_340_000 },
    { date: 'Oct 25', 'FY 2025': 9_560_000, 'FY 2024': 4_450_000 },
    { date: 'Nov 25', 'FY 2025': 6_780_000, 'FY 2024': 7_230_000 },
    { date: 'Dec 25', 'FY 2025': 5_940_000, 'FY 2024': 3_890_000 },
];

const valueFormatter = (value: number) =>
    new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        notation: 'compact',
        compactDisplay: 'short',
        maximumFractionDigits: 1,
        signDisplay: 'exceptZero',
    }).format(value);

export const FundMonthlyPnl = () => (
    <BarChart01
        data={data}
        title="Apex Capital Multi-Asset Fund — Monthly P&L"
        description="Realized monthly P&L (USD) for the $500M multi-asset fund, as of Dec 31, 2025. Illustrative data."
        indexField="date"
        defaultCategories={['FY 2025']}
        comparisonCategories={['FY 2024', 'FY 2025']}
        defaultColors={['blue']}
        comparisonColors={['cyan', 'blue']}
        comparisonLabel="Show 2024 comparison"
        valueFormatter={valueFormatter}
    />
);
