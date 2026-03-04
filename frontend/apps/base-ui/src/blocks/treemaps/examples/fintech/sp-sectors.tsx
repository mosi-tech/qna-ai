'use client';

import React from 'react';
import { Treemap01 } from '../../treemap-01';

const fmtBn = (v: number) => `$${v.toFixed(0)}B`;
const fmtChange = (v: number) => `${v >= 0 ? '+' : ''}${v.toFixed(2)}%`;

// S&P 500 sector market-cap weights (approximate, Feb 2026) — flat structure
const spSectors = [
    { name: 'Info Tech', value: 892, change: 1.42, group: 'S&P 500 Sector' },
    { name: 'Financials', value: 534, change: -0.83, group: 'S&P 500 Sector' },
    { name: 'Healthcare', value: 481, change: 0.21, group: 'S&P 500 Sector' },
    { name: 'Cons Disc', value: 412, change: -1.54, group: 'S&P 500 Sector' },
    { name: 'Comm Svcs', value: 389, change: 2.08, group: 'S&P 500 Sector' },
    { name: 'Industrials', value: 341, change: 0.37, group: 'S&P 500 Sector' },
    { name: 'Cons Staples', value: 289, change: -0.14, group: 'S&P 500 Sector' },
    { name: 'Energy', value: 264, change: 1.67, group: 'S&P 500 Sector' },
    { name: 'Utilities', value: 198, change: -0.62, group: 'S&P 500 Sector' },
    { name: 'Real Estate', value: 175, change: -0.91, group: 'S&P 500 Sector' },
    { name: 'Materials', value: 162, change: 0.53, group: 'S&P 500 Sector' },
];

export function SpSectorsExample() {
    return (
        <Treemap01
            data={spSectors}
            title="S&P 500 — Sector Market Cap"
            description="Feb 27, 2026 · Cell size = market cap ($B) · Color = daily change"
            colorMode="change"
            valueLabel="Mkt Cap"
            changeLabel="Daily Rtn"
            changeRange={3}
            height={360}
            valueFormatter={fmtBn}
            changeFormatter={fmtChange}
        />
    );
}
