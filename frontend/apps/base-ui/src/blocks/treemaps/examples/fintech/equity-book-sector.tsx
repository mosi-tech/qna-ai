'use client';

import React from 'react';
import { Treemap01 } from '../../treemap-01';

const fmtPct = (v: number) => `${v.toFixed(1)}%`;
const fmtChange = (v: number) => `${v >= 0 ? '+' : ''}${v.toFixed(2)}%`;

const equityBook = [
    {
        name: 'Technology',
        value: 34.2,
        children: [
            { name: 'NVDA', value: 8.4, change: 2.31, group: 'Technology' },
            { name: 'MSFT', value: 7.2, change: 0.85, group: 'Technology' },
            { name: 'AAPL', value: 6.8, change: -0.42, group: 'Technology' },
            { name: 'META', value: 5.1, change: 1.64, group: 'Technology' },
            { name: 'AMZN', value: 4.3, change: 0.21, group: 'Technology' },
            { name: 'GOOGL', value: 2.4, change: -0.17, group: 'Technology' },
        ],
    },
    {
        name: 'Financials',
        value: 18.7,
        children: [
            { name: 'JPM', value: 6.2, change: -1.23, group: 'Financials' },
            { name: 'GS', value: 4.8, change: -0.91, group: 'Financials' },
            { name: 'BAC', value: 4.1, change: -1.54, group: 'Financials' },
            { name: 'MS', value: 3.6, change: -0.63, group: 'Financials' },
        ],
    },
    {
        name: 'Healthcare',
        value: 12.4,
        children: [
            { name: 'LLY', value: 5.1, change: 3.74, group: 'Healthcare' },
            { name: 'UNH', value: 4.2, change: -2.18, group: 'Healthcare' },
            { name: 'ABBV', value: 3.1, change: 0.93, group: 'Healthcare' },
        ],
    },
    {
        name: 'Consumer',
        value: 10.8,
        children: [
            { name: 'TSLA', value: 3.8, change: -3.21, group: 'Consumer Disc.' },
            { name: 'AMZN', value: 4.6, change: 0.41, group: 'Consumer Disc.' },
            { name: 'NKE', value: 2.4, change: -0.87, group: 'Consumer Disc.' },
        ],
    },
    {
        name: 'Energy',
        value: 8.3,
        children: [
            { name: 'XOM', value: 3.9, change: 1.12, group: 'Energy' },
            { name: 'CVX', value: 2.8, change: 0.64, group: 'Energy' },
            { name: 'COP', value: 1.6, change: 0.38, group: 'Energy' },
        ],
    },
    {
        name: 'Industrials',
        value: 7.6,
        children: [
            { name: 'CAT', value: 3.4, change: -0.29, group: 'Industrials' },
            { name: 'GE', value: 2.4, change: 0.74, group: 'Industrials' },
            { name: 'HON', value: 1.8, change: -0.11, group: 'Industrials' },
        ],
    },
    {
        name: 'Other',
        value: 8.0,
        children: [
            { name: 'SPY', value: 4.2, change: -0.18, group: 'Other' },
            { name: 'TLT', value: 2.1, change: 0.33, group: 'Other' },
            { name: 'GLD', value: 1.7, change: 0.91, group: 'Other' },
        ],
    },
];

export function EquityBookSectorExample() {
    return (
        <Treemap01
            data={equityBook}
            title="Equity Book — Position Weights & Daily P&L"
            description="Feb 27, 2026 · Size = portfolio weight · Color = daily return"
            colorMode="change"
            valueFormatter={fmtPct}
            changeFormatter={fmtChange}
            valueLabel="Weight"
            changeLabel="Daily Rtn"
        />
    );
}
