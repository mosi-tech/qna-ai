import React, { useEffect, useMemo, useState } from 'react';
import { registryMap } from '../experimental/registry';

type Approval = { id: string; question: string; file: string; name: string };

export default function ApprovedPage() {
  const [approved, setApproved] = useState<Approval[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const res = await fetch('/api/approved');
        const json = await res.json();
        if (mounted) setApproved(json.approved || []);
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  const moveToExperimental = async (id: string) => {
    try {
      const res = await fetch('/api/unapprove', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id }),
      });
      const json = await res.json();
      if (Array.isArray(json.approved)) setApproved(json.approved);
    } catch {}
  };

  const selected = useMemo(() => approved.find((a) => a.id === selectedId) || approved[0], [approved, selectedId]);

  return (
    <div style={{ height: '100vh', display: 'flex', fontFamily: 'Inter, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell' }}>
      {/* Left list */}
      <div style={{ width: '30%', borderRight: '1px solid #e5e7eb', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: 12, borderBottom: '1px solid #e5e7eb', fontWeight: 700 }}>Approved</div>
        <div style={{ flex: 1, overflow: 'auto' }}>
          {loading ? (
            <div style={{ padding: 12 }}>Loading…</div>
          ) : approved.length === 0 ? (
            <div style={{ padding: 12, color: '#6b7280' }}>No approved visuals.</div>
          ) : (
            approved.map((a) => (
              <button key={a.id} onClick={() => setSelectedId(a.id)} style={{ display: 'block', width: '100%', textAlign: 'left', padding: 12, border: 0, borderBottom: '1px solid #f3f4f6', background: (selected?.id === a.id) ? '#eef2ff' : 'transparent', cursor: 'pointer' }}>
                <div style={{ fontWeight: 600 }}>{a.name}</div>
                <div style={{ fontSize: 12, color: '#6b7280' }}>{a.file}</div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Right detail */}
      <div style={{ width: '70%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: 12, borderBottom: '1px solid #e5e7eb', fontWeight: 700, display: 'flex', justifyContent: 'space-between' }}>
          <span>{selected ? selected.name : 'No selection'}</span>
          <a href="/experimental" style={{ color: '#1d4ed8', fontSize: 14 }}>Go to Experimental →</a>
        </div>
        <div style={{ flex: 1, overflow: 'auto', padding: 16, background: '#fafafa' }}>
          {!selected ? (
            <div style={{ color: '#6b7280' }}>Select a visual on the left.</div>
          ) : (
            <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 8 }}>
              <div style={{ padding: 12, borderBottom: '1px solid #e5e7eb', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 600 }}>{selected.name}</div>
                  <div style={{ fontSize: 12, color: '#6b7280' }}>{selected.file}</div>
                  {selected.question && <div style={{ marginTop: 4 }}>Q: {selected.question}</div>}
                </div>
                <button onClick={() => moveToExperimental(selected.id)} style={{ padding: '8px 10px', border: '1px solid #e5e7eb', borderRadius: 6, background: '#fff', cursor: 'pointer' }}>
                  Move to Experimental
                </button>
              </div>
              <div style={{ padding: 12 }}>
                {(() => {
                  const Def = registryMap[selected.id];
                  const Comp = Def?.Component;
                  return Comp ? <Comp /> : <div style={{ color: '#9ca3af' }}>Component not found</div>;
                })()}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
