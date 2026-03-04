import React from 'react';
import { LineChart01 } from '../../';

// Question: What are the YTD cumulative total returns across major asset classes as of Feb 27, 2026?
// Block: line-chart-01 — Multi-series line chart with summary metrics

const data = [
    { date: 'Jan 02', 'US Equities': 0.0, 'EM Equities': 0.0, 'Intl Dev': 0.0, 'IG Credit': 0.0, 'HY Credit': 0.0 },
    { date: 'Jan 09', 'US Equities': 1.4, 'EM Equities': 2.1, 'Intl Dev': 1.8, 'IG Credit': 0.3, 'HY Credit': 0.6 },
    { date: 'Jan 16', 'US Equities': 3.2, 'EM Equities': 3.8, 'Intl Dev': 3.1, 'IG Credit': 0.5, 'HY Credit': 1.0 },
    { date: 'Jan 23', 'US Equities': 2.7, 'EM Equities': 4.5, 'Intl Dev': 4.0, 'IG Credit': 0.4, 'HY Credit': 0.9 },
    { date: 'Jan 30', 'US Equities': 4.1, 'EM Equities': 6.2, 'Intl Dev': 5.3, 'IG Credit': 0.7, 'HY Credit': 1.4 },
    { date: 'Feb 06', 'US Equities': 3.6, 'EM Equities': 7.0, 'Intl Dev': 6.1, 'IG Credit': 0.6, 'HY Credit': 1.3 },
    { date: 'Feb 13', 'US Equities': 5.0, 'EM Equities': 8.3, 'Intl Dev': 7.4, 'IG Credit': 0.9, 'HY Credit': 1.8 },
    { date: 'Feb 20', 'US Equities': 4.4, 'EM Equities': 9.1, 'Intl Dev': 8.2, 'IG Credit': 1.1, 'HY Credit': 2.0 },
    { date: 'Feb 27', 'US Equities': 5.8, 'EM Equities': 10.4, 'Intl Dev': 9.6, 'HY Credit': 2.2, 'IG Credit': 1.3 },
];

const valueFormatter = (value: number) => `${value > 0 ? '+' : ''}${value.toFixed(1)}%`;

export const AssetClassYtdReturns = () => (
    <LineChart01
        data={data}
        title="YTD Cumulative Total Returns by Asset Class — Feb 27, 2026"
        categories={['US Equities', 'EM Equities', 'Intl Dev', 'HY Credit', 'IG Credit']}
        colors={['blue', 'emerald', 'violet', 'orange', 'slate']}
        valueFormatter={valueFormatter}
        indexField="date"
        summary={[
            { name: 'US Equities (SPY)', value: 5.8 },
            { name: 'EM Equities (EEM)', value: 10.4 },
            { name: 'Intl Dev (EFA)', value: 9.6 },
            { name: 'HY Credit (HYG)', value: 2.2 },
            { name: 'IG Credit (AGG)', value: 1.3 },
        ]}
    />
);
