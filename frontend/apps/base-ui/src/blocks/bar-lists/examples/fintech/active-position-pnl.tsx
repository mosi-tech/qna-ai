import React from 'react';
import { BarList01 } from '../../';

const data = [
    { name: 'NVDA — Long 4,200 sh', value: 312_450 },
    { name: 'MSFT — Long 6,800 sh', value: 187_920 },
    { name: 'AMZN — Long 3,100 sh', value: 143_670 },
    { name: 'META — Long 2,500 sh', value: 119_250 },
    { name: 'AAPL — Long 7,200 sh', value: 94_320 },
    { name: 'GS — Long 1,400 sh', value: 71_540 },
    { name: 'JPM — Long 2,900 sh', value: 58_810 },
    { name: 'LLY — Long 880 sh', value: 44_130 },
    { name: 'TSLA — Long 1,600 sh', value: 22_960 },
    { name: 'BA — Long 1,100 sh', value: 8_470 },
];

export const ActivePositionPnl = () => (
    <BarList01
        title="Top Unrealized P&L Contributors"
        subtitle="Unrealized Gain — as of Feb 27, 2026"
        data={data}
        valueFormatter={(v) =>
            v >= 0
                ? `+$${(v / 1000).toFixed(1)}K`
                : `-$${(Math.abs(v) / 1000).toFixed(1)}K`
        }
    />
);
