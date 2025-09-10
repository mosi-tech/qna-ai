import React from 'react';

type DataPoint = { key: string; value: any; description: string };
type JsonData = { description?: string; body?: DataPoint[] };

export default function JsonCard({ data }: { data: JsonData }) {
  if (!data) return <div style={{ color: '#9ca3af' }}>No data</div>;
  return (
    <div style={{ background: '#fff', borderRadius: 8, border: '1px solid #e5e7eb' }}>
      {data.description && (
        <div style={{ padding: 16, borderBottom: '1px solid #e5e7eb' }}>
          <h4 style={{ margin: 0, marginBottom: 8, fontSize: 16, fontWeight: 600 }}>Analysis Overview</h4>
          <p style={{ margin: 0, fontSize: 14, color: '#6b7280', lineHeight: 1.5 }}>{data.description}</p>
        </div>
      )}
      <div style={{ padding: 16 }}>
        <h4 style={{ margin: 0, marginBottom: 12, fontSize: 16, fontWeight: 600 }}>Data Points</h4>
        <div style={{ display: 'grid', gap: 12 }}>
          {data.body?.map((item, idx) => (
            <div key={idx} style={{ padding: 12, background: '#f8f9fa', borderRadius: 6, border: '1px solid #e5e7eb' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 4 }}>
                <strong style={{ fontSize: 14, color: '#374151' }}>{item.key}</strong>
                <span style={{ fontSize: 14, fontWeight: 600, color: '#059669' }}>{String(item.value)}</span>
              </div>
              <p style={{ margin: 0, fontSize: 13, color: '#6b7280', lineHeight: 1.4 }}>{item.description}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

