import React, { useEffect, useMemo, useState } from 'react';
import { registryMap } from '../experimental/registry';

type Approval = { id: string; question: string; file: string; name: string };

export default function ExperimentalPage() {
  const [approved, setApproved] = useState<Approval[]>([]);
  const [experimental, setExperimental] = useState<{ id: string; question: string; name: string; file: string; description?: string; apis?: string[] }[]>([]);
  const [loading, setLoading] = useState(true);
  const [questions, setQuestions] = useState<Record<string, string>>({});
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [lastQuestion, setLastQuestion] = useState<string>('');

  useEffect(() => {
    let mounted = true;
    (async () => {
      try {
        const [apprRes, expRes] = await Promise.all([
          fetch('/api/approved'),
          fetch('/api/experimental'),
        ]);
        const apprJson = await apprRes.json();
        const expJson = await expRes.json();
        if (mounted) {
          setApproved(apprJson.approved || []);
          setExperimental(expJson.experimental || []);
        }
      } catch (e) {
        // ignore
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    try {
      const raw = typeof window !== 'undefined' ? window.localStorage.getItem('qna_messages') : null;
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed) && parsed.length > 0) {
          const last = parsed[parsed.length - 1];
          if (last && typeof last.text === 'string') setLastQuestion(last.text);
        }
      }
    } catch {}
  }, []);

  const approvedIds = useMemo(() => new Set(approved.map((a) => a.id)), [approved]);
  const unapproved = useMemo(() => experimental.filter((e) => !approvedIds.has(e.id)), [experimental, approvedIds]);
  const selected = useMemo(() => unapproved.find((e) => e.id === selectedId) || unapproved[0], [unapproved, selectedId]);

  const onApprove = async (id: string) => {
    const question = (questions[id] ?? selected?.question ?? '').trim();
    if (!question) return;
    try {
      const res = await fetch('/api/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id, question }),
      });
      const json = await res.json();
      if (Array.isArray(json.approved)) setApproved(json.approved);
      setQuestions((q) => ({ ...q, [id]: '' }));
    } catch (e) {}
  };

  return (
    <div style={{ height: '100vh', display: 'flex', fontFamily: 'Inter, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell' }}>
      <div style={{ width: '30%', borderRight: '1px solid #e5e7eb', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: 12, borderBottom: '1px solid #e5e7eb', fontWeight: 700 }}>Experimental</div>
        <div style={{ padding: 8, fontSize: 12, color: '#6b7280' }}>Latest question: {lastQuestion ? `"${lastQuestion}"` : '—'}</div>
        <div style={{ flex: 1, overflow: 'auto' }}>
          {loading ? (
            <div style={{ padding: 12 }}>Loading…</div>
          ) : unapproved.length === 0 ? (
            <div style={{ padding: 12, color: '#6b7280' }}>No experimental visuals.</div>
          ) : (
            unapproved.map((v) => (
              <button key={v.id} onClick={() => setSelectedId(v.id)} style={{ display: 'block', width: '100%', textAlign: 'left', padding: 12, border: 0, borderBottom: '1px solid #f3f4f6', background: (selected?.id === v.id) ? '#eef2ff' : 'transparent', cursor: 'pointer' }}>
                <div style={{ fontWeight: 600 }}>{v.name}</div>
                <div style={{ fontSize: 12, color: '#6b7280' }}>{v.description}</div>
              </button>
            ))
          )}
        </div>
      </div>
      <div style={{ width: '70%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: 12, borderBottom: '1px solid #e5e7eb', fontWeight: 700, display: 'flex', justifyContent: 'space-between' }}>
          <span>{selected ? selected.name : 'No selection'}</span>
          <a href="/approved" style={{ color: '#1d4ed8', fontSize: 14 }}>Go to Approved →</a>
        </div>
        <div style={{ flex: 1, overflow: 'auto', padding: 16, background: '#fafafa' }}>
          {!selected ? (
            <div style={{ color: '#6b7280' }}>Select a visual on the left.</div>
          ) : (
            <div style={{ background: '#fff', border: '1px solid #e5e7eb', borderRadius: 8 }}>
              <div style={{ padding: 12, borderBottom: '1px solid #e5e7eb', display: 'flex', gap: 8, alignItems: 'center' }}>
                <input
                  placeholder="Enter question linked to this visual"
                  value={questions[selected.id] ?? selected.question ?? ''}
                  onChange={(e) => setQuestions((q) => ({ ...q, [selected.id]: e.target.value }))}
                  style={{ flex: 1, padding: 10, border: '1px solid #e5e7eb', borderRadius: 6 }}
                />
                <a href={`/?preview=${encodeURIComponent(selected.id)}`} style={{ padding: '8px 10px', border: '1px solid #e5e7eb', borderRadius: 6, background: '#fff', color: '#1d4ed8', textDecoration: 'none' }}>Preview on Main</a>
                <button onClick={() => setQuestions((q) => ({ ...q, [selected!.id]: lastQuestion }))} disabled={!lastQuestion} style={{ padding: '8px 10px', border: '1px solid #e5e7eb', borderRadius: 6, background: '#fff', cursor: lastQuestion ? 'pointer' : 'not-allowed', color: lastQuestion ? '#111827' : '#9ca3af' }}>Use last question</button>
                <button onClick={() => onApprove(selected.id)} disabled={!((questions[selected.id] ?? selected.question ?? '').trim())} style={{ padding: '8px 10px', border: 0, borderRadius: 6, background: '#10b981', color: 'white', cursor: ((questions[selected.id] ?? selected.question ?? '').trim()) ? 'pointer' : 'not-allowed' }}>Move to Approved</button>
              </div>
              <div style={{ padding: 12 }}>
                {(() => {
                  const def = registryMap[selected.id];
                  const Comp: any = def?.Component as any;
                  return Comp ? (
                    <Comp position={(selected as any).position} />
                  ) : (
                    <div style={{ color: '#9ca3af' }}>Component not found</div>
                  );
                })()}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
