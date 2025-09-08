import React from 'react';

type Point = { t: string; mp: number };

export default function ForexRatesCard({
  pair = 'USDJPY',
  latest = { mp: 127.779, t: '2022-05-20T05:38:41.311530885Z' },
  history = [
    { t: '2022-01-03T00:01:00Z', mp: 115.144 },
    { t: '2022-01-03T00:02:00Z', mp: 115.138 },
    { t: '2022-01-03T00:03:00Z', mp: 115.131 },
    { t: '2022-01-03T00:04:00Z', mp: 115.160 },
    { t: '2022-01-03T00:05:00Z', mp: 115.120 },
  ],
}: {
  pair?: string;
  latest?: { mp: number; t: string };
  history?: Point[];
}) {
  const values = history.map((p) => p.mp);
  const min = Math.min(...values);
  const max = Math.max(...values);
  const w = 280;
  const h = 80;
  const pad = 6;
  const scaleX = (i: number) => pad + (i * (w - pad * 2)) / Math.max(1, history.length - 1);
  const scaleY = (v: number) => pad + (h - pad * 2) * (1 - (v - min) / Math.max(1e-6, max - min));
  const path = history
    .map((p, i) => `${i === 0 ? 'M' : 'L'} ${scaleX(i).toFixed(2)} ${scaleY(p.mp).toFixed(2)}`)
    .join(' ');

  const change = values.length > 1 ? ((values[values.length - 1] - values[0]) / values[0]) * 100 : 0;
  const color = change >= 0 ? '#059669' : '#b91c1c';

  return (
    <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, background: '#fff', overflow: 'hidden' }}>
      <div style={{ padding: 12, borderBottom: '1px solid #e5e7eb', display: 'flex', justifyContent: 'space-between' }}>
        <div style={{ fontWeight: 600 }}>Forex: {pair}</div>
        <div style={{ fontSize: 12, color: '#6b7280' }}>Latest mp: {latest.mp}</div>
      </div>
      <div style={{ padding: 12, display: 'flex', alignItems: 'center', gap: 16 }}>
        <svg width={w} height={h} viewBox={`0 0 ${w} ${h}`}>
          <path d={path} fill="none" stroke={color} strokeWidth={2} />
        </svg>
        <div>
          <div style={{ fontSize: 12, color: '#6b7280' }}>Change</div>
          <div style={{ fontWeight: 700, color }}>{change.toFixed(2)}%</div>
        </div>
      </div>
      <div style={{ padding: '0 12px 12px', fontSize: 12, color: '#6b7280' }}>
        Backed by Alpaca Market Data API: GET /v1beta1/forex/latest/rates and GET /v1beta1/forex/rates
      </div>
      <div style={{ padding: '0 12px 12px', fontSize: 12 }}>
        <span style={{ color: '#6b7280' }}>You might also ask:</span>{' '}
        <em>Show historical USD/JPY over the past month with moving averages.</em>
      </div>
    </div>
  );
}
