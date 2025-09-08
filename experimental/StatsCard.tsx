import React from 'react';

type Stat = { label: string; value: string | number; trend?: 'up' | 'down' };

const defaultStats: Stat[] = [
  { label: 'Users', value: 1289, trend: 'up' },
  { label: 'Sessions', value: 4732, trend: 'up' },
  { label: 'Errors', value: 12, trend: 'down' },
];

export default function StatsCard({ stats = defaultStats }: { stats?: Stat[] }) {
  return (
    <div
      style={{
        border: '1px solid #e5e7eb',
        borderRadius: 8,
        padding: 16,
        background: '#fff',
        boxShadow: '0 1px 2px rgba(0,0,0,0.05)',
      }}
    >
      <div style={{ fontWeight: 600, marginBottom: 12 }}>Key Metrics</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        {stats.map((s) => (
          <div key={s.label} style={{ padding: 12, background: '#f9fafb', borderRadius: 6 }}>
            <div style={{ fontSize: 12, color: '#6b7280' }}>{s.label}</div>
            <div style={{ fontSize: 20, fontWeight: 700 }}>{s.value}</div>
            {s.trend && (
              <div style={{ fontSize: 12, color: s.trend === 'up' ? '#059669' : '#b91c1c' }}>
                {s.trend === 'up' ? '▲' : '▼'} {s.trend === 'up' ? 'Improving' : 'Declining'}
              </div>
            )}
          </div>
        ))}
      </div>
      <div style={{ marginTop: 8, fontSize: 12 }}>
        <span style={{ color: '#6b7280' }}>You might also ask:</span>{' '}
        <em>Can we break down sessions by device or region?</em>
      </div>
    </div>
  );
}
