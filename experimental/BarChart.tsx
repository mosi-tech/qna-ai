import React from 'react';

type BarChartProps = {
  title?: string;
};

const sampleData = [
  { label: 'A', value: 30 },
  { label: 'B', value: 55 },
  { label: 'C', value: 15 },
  { label: 'D', value: 80 },
];

export default function BarChart({ title = 'Sample Bar Chart' }: BarChartProps) {
  const max = Math.max(...sampleData.map((d) => d.value));
  return (
    <div style={{ padding: 16 }}>
      <div style={{ fontWeight: 600, marginBottom: 8 }}>{title}</div>
      <div style={{ display: 'flex', alignItems: 'flex-end', height: 120, gap: 8 }}>
        {sampleData.map((d) => (
          <div key={d.label} style={{ textAlign: 'center', flex: 1 }}>
            <div
              style={{
                height: `${(d.value / max) * 100}%`,
                background: 'linear-gradient(180deg,#6EE7F9,#1EA7FD)',
                borderRadius: 4,
              }}
              title={`${d.label}: ${d.value}`}
            />
            <div style={{ fontSize: 12, marginTop: 6, color: '#555' }}>{d.label}</div>
          </div>
        ))}
      </div>
      <div style={{ marginTop: 8, fontSize: 12 }}>
        <span style={{ color: '#6b7280' }}>You might also ask:</span>{' '}
        <em>Can we sort this chart descending and highlight the top 2 bars?</em>
      </div>
    </div>
  );
}
