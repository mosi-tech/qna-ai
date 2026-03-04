import React from 'react';
import { LineChart02 } from '../../';

const data = [
    { date: 'Jan 02', price: 585.11 },
    { date: 'Jan 03', price: 582.74 },
    { date: 'Jan 06', price: 587.30 },
    { date: 'Jan 07', price: 590.48 },
    { date: 'Jan 08', price: 588.92 },
    { date: 'Jan 09', price: 584.61 },
    { date: 'Jan 10', price: 579.34 },
    { date: 'Jan 13', price: 583.20 },
    { date: 'Jan 14', price: 587.85 },
    { date: 'Jan 15', price: 592.41 },
    { date: 'Jan 16', price: 594.10 },
    { date: 'Jan 17', price: 590.03 },
    { date: 'Jan 21', price: 595.67 },
    { date: 'Jan 22', price: 598.14 },
    { date: 'Jan 23', price: 596.80 },
    { date: 'Jan 24', price: 601.35 },
    { date: 'Jan 27', price: 597.44 },
    { date: 'Jan 28', price: 600.92 },
    { date: 'Jan 29', price: 602.18 },
    { date: 'Jan 30', price: 598.55 },
    { date: 'Jan 31', price: 594.12 },
    { date: 'Feb 03', price: 589.76 },
    { date: 'Feb 04', price: 593.40 },
    { date: 'Feb 05', price: 597.84 },
    { date: 'Feb 06', price: 601.22 },
    { date: 'Feb 07', price: 604.50 },
    { date: 'Feb 10', price: 600.87 },
    { date: 'Feb 11', price: 598.34 },
    { date: 'Feb 12', price: 603.61 },
    { date: 'Feb 13', price: 606.12 },
    { date: 'Feb 14', price: 609.44 },
    { date: 'Feb 18', price: 605.72 },
    { date: 'Feb 19', price: 602.30 },
    { date: 'Feb 20', price: 598.18 },
    { date: 'Feb 21', price: 594.55 },
    { date: 'Feb 24', price: 597.88 },
    { date: 'Feb 25', price: 600.14 },
    { date: 'Feb 26', price: 598.67 },
    { date: 'Feb 27', price: 601.42 },
];

export const SpyYtdReturn = () => (
    <LineChart02
        data={data}
        categories={['price']}
        indexField="date"
        subtitle="SPDR S&P 500 ETF Trust (SPY)"
        value="$601.42"
        change="+$16.31 (+2.79%)"
        changeType="positive"
        periodLabel="YTD 2026"
        summary={[
            { name: 'Open (Jan 02)', value: '$585.11' },
            { name: '52W High', value: '$613.23' },
            { name: 'Avg Volume', value: '67.4M' },
            { name: 'YTD Low', value: '$579.34' },
            { name: 'YTD High', value: '$609.44' },
            { name: 'AUM', value: '$563.8B' },
        ]}
        valueFormatter={(v) => `$${v.toFixed(2)}`}
    />
);
