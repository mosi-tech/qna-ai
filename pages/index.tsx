import React, { useEffect, useMemo, useState } from 'react';
import { useRouter } from 'next/router';
import { registryMap } from '../experimental/registry';

type Message = { id: string; text: string; at: number };

export default function Home() {
  const router = useRouter();
  type Approval = { id: string; question: string; file: string; name: string; apis?: string[] };
  const [approved, setApproved] = useState<Approval[]>([]);
  const [experimental, setExperimental] = useState<{ id: string; question: string; name: string; file: string; description?: string; apis?: string[]; position?: any }[]>([]);
  const [loading, setLoading] = useState(true);
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');

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
        // ignore for now
      } finally {
        if (mounted) setLoading(false);
      }
    })();
    return () => {
      mounted = false;
    };
  }, []);

  // Load persisted messages (from prior sessions) and persist on change
  useEffect(() => {
    try {
      const raw = typeof window !== 'undefined' ? window.localStorage.getItem('qna_messages') : null;
      if (raw) {
        const parsed = JSON.parse(raw);
        if (Array.isArray(parsed)) setMessages(parsed);
      }
    } catch {}
  }, []);

  useEffect(() => {
    try {
      if (typeof window !== 'undefined') {
        window.localStorage.setItem('qna_messages', JSON.stringify(messages));
      }
    } catch {}
  }, [messages]);

  // Seed a starter question if none exists
  useEffect(() => {
    if (messages.length === 0) {
      const starter: Message = {
        id: Math.random().toString(36).slice(2),
        text: 'What is my current buying power, cash balance, and which open positions are my largest by market value?',
        at: Date.now(),
      };
      setMessages([starter]);
    }
    // run only once after initial messages load
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Preview mode via query param ?preview=<visualId>
  const queryPreviewId = typeof router.query.preview === 'string' ? router.query.preview : null;
  const defaultPreviewId = useMemo(() => (experimental.length > 0 ? experimental[0].id : null), [experimental]);
  const previewId = queryPreviewId || defaultPreviewId;
  const previewDef = previewId ? registryMap[previewId] : null;
  const previewMeta = previewId ? experimental.find((e) => e.id === previewId) : null;
  const isPreviewApproved = !!(previewId && approved.some((a) => a.id === previewId));
  const lastQuestion = useMemo(() => (messages.length ? messages[messages.length - 1].text : ''), [messages]);
  const [previewQuestion, setPreviewQuestion] = useState<string>('');
  const [jsonData, setJsonData] = useState<any>(null);
  const [jsonLoading, setJsonLoading] = useState(false);

  useEffect(() => {
    if (!previewId) return;
    // Prefer experimental-saved question; fallback to last chat question
    const exp = experimental.find((e) => e.id === previewId);
    setPreviewQuestion(exp?.question || lastQuestion || '');
  }, [previewId, lastQuestion, experimental]);

  // Load JSON data for preview
  useEffect(() => {
    // If a Component exists for preview, skip fetching JSON
    if (!previewDef?.file && !previewMeta?.file) {
      setJsonData(null);
      setJsonLoading(false);
      return;
    }
    const hasComponent = (previewDef as any)?.Component;
    if (hasComponent) {
      setJsonData(null);
      setJsonLoading(false);
      return;
    }

    setJsonLoading(true);
    const file = (previewDef as any)?.file || (previewMeta as any)?.file;
    fetch(`/api/json?file=${encodeURIComponent(file)}`)
      .then(res => res.json())
      .then(data => {
        setJsonData(data);
        setJsonLoading(false);
      })
      .catch(err => {
        console.error('Failed to load JSON:', err);
        setJsonData(null);
        setJsonLoading(false);
      });
  }, [previewDef]);

  const approveFromPreview = async () => {
    if (!previewId) return;
    try {
      const meta = experimental.find((e) => e.id === previewId);
      const q = (previewQuestion || meta?.question || '').trim();
      const res = await fetch('/api/approve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: previewId, question: q }),
      });
      const json = await res.json();
      if (!res.ok) {
        console.error('Approve failed:', json?.error || res.statusText);
        return;
      }
      if (Array.isArray(json.approved)) setApproved(json.approved);
      
      // Refresh experimental list after approval
      const expRes = await fetch('/api/experimental');
      const expJson = await expRes.json();
      if (Array.isArray(expJson.experimental)) setExperimental(expJson.experimental);
      
      router.replace('/', undefined, { shallow: true });
    } catch {}
  };

  const ignoreFromPreview = async () => {
    if (!previewId) return;
    try {
      const res = await fetch('/api/ignore', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id: previewId }),
      });
      const json = await res.json();
      if (Array.isArray(json.experimental)) setExperimental(json.experimental);
      router.replace('/', undefined, { shallow: true });
    } catch {}
  };

  const approvedIds = useMemo(() => new Set(approved.map((a) => a.id)), [approved]);

  const unapprove = async (id: string) => {
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

  // No approval on this page; experimental moved to dedicated page

  const onSend = () => {
    if (!input.trim()) return;
    setMessages((m) => [
      ...m,
      { id: Math.random().toString(36).slice(2), text: input.trim(), at: Date.now() },
    ]);
    setInput('');
  };

  return (
    <div style={{ height: '100vh', display: 'flex', fontFamily: 'Inter, system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell' }}>
      {/* Left Panel */}
      <div
        style={{
          width: '30%',
          borderRight: '1px solid #e5e7eb',
          display: 'flex',
          flexDirection: 'column',
        }}
      >
        <div style={{ padding: 12, borderBottom: '1px solid #e5e7eb' }}>
          <div style={{ fontWeight: 600 }}>QnA</div>
          <div style={{ marginTop: 6, fontSize: 12, color: '#6b7280' }}>
            Ask a trading/investment question answerable via Alpaca Market Data/Trading APIs.
            Then approve a matching visual in <a href="/experimental" style={{ color: '#1d4ed8' }}>Experimental</a>.
          </div>
        </div>

        {/* Messages area */}
        <div style={{ flex: 1, padding: 12, overflow: 'auto' }}>
          {messages.length === 0 ? (
            <div style={{ color: '#6b7280', fontSize: 14 }}>Start chatting below…</div>
          ) : (
            messages.map((m) => (
              <div key={m.id} style={{ marginBottom: 8 }}>
                <div style={{ fontSize: 12, color: '#6b7280' }}>
                  {new Date(m.at).toLocaleTimeString()}
                </div>
                <div
                  style={{
                    display: 'inline-block',
                    padding: '8px 10px',
                    borderRadius: 8,
                    background: '#f3f4f6',
                  }}
                >
                  {m.text}
                </div>
              </div>
            ))
          )}
        </div>

        {/* Input at bottom */}
        <div style={{ padding: 12, borderTop: '1px solid #e5e7eb' }}>
          <div style={{ display: 'flex', gap: 8 }}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type a message"
              onKeyDown={(e) => e.key === 'Enter' && onSend()}
              style={{ flex: 1, padding: 10, border: '1px solid #e5e7eb', borderRadius: 8 }}
            />
            <button
              onClick={onSend}
              style={{
                padding: '10px 14px',
                background: '#1d4ed8',
                color: 'white',
                border: 0,
                borderRadius: 8,
                cursor: 'pointer',
              }}
            >
              Send
            </button>
          </div>
        </div>
      </div>

      {/* Right Panel */}
      <div style={{ width: '70%', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: 12, borderBottom: '1px solid #e5e7eb', fontWeight: 600, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <span>Visual Layer - Preview & Approve</span>
          <div style={{ display: 'flex', gap: 12 }}>
            <a href="/approved" style={{ fontSize: 14, color: '#1d4ed8' }}>Approved ({approved.length})</a>
            <a href="/experimental" style={{ fontSize: 14, color: '#1d4ed8' }}>Experimental →</a>
            <a href="/validation" style={{ fontSize: 14, color: '#1d4ed8' }}>Validation</a>
          </div>
        </div>

        {/* Experimental preview for approval - approved visuals moved to /approved page */}
        <div style={{ flex: 1, padding: 16, overflow: 'auto', background: '#fafafa' }}>
          {/* Preview mode card */}
          {previewDef && !isPreviewApproved && (
            <div style={{ marginBottom: 16, border: '1px dashed #93c5fd', background: '#eff6ff', borderRadius: 8 }}>
              <div style={{ padding: 10, borderBottom: '1px dashed #bfdbfe', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontWeight: 700, color: '#1e40af' }}>Preview (not approved)</div>
                  <div style={{ fontSize: 12, color: '#1d4ed8' }}>{previewDef.name}</div>
                </div>
                <div style={{ display: 'flex', gap: 8 }}>
                  {/* No explicit dismiss needed since preview shows by default for first experimental */}
                </div>
              </div>
              <div style={{ padding: 10, background: '#fff' }}>
                {previewQuestion && (
                  <div style={{ marginBottom: 12, fontSize: 12, color: '#374151' }}>Q: {previewQuestion}</div>
                )}
                {(() => {
                  const meta = experimental.find((e) => e.id === previewId);
                  const pos = meta?.position;
                  if (!pos) return null;
                  return (
                    <div style={{ marginBottom: 8, fontSize: 12, color: '#6b7280' }}>
                      Position: {pos.qty ?? '—'} shares{pos.avg_entry_price ? ` @ $${Number(pos.avg_entry_price).toLocaleString()}` : ''}
                    </div>
                  );
                })()}
                <div style={{ display: 'flex', gap: 8, marginBottom: 12 }}>
                  <button onClick={approveFromPreview} style={{ padding: '8px 10px', border: 0, borderRadius: 6, background: '#10b981', color: 'white', cursor: 'pointer' }}>Move to Approved</button>
                  <button onClick={ignoreFromPreview} style={{ padding: '8px 10px', border: 0, borderRadius: 6, background: '#ef4444', color: 'white', cursor: 'pointer' }}>Ignore</button>
                </div>
                {(() => {
                  const def = previewDef as any;
                  const Comp = def?.Component as any;
                  if (Comp) return <Comp />;
                  if (jsonLoading) return <div>Loading JSON data...</div>;
                  if (!jsonData) return <div>Failed to load data</div>;
                  return (
                    <div style={{ background: '#fff', borderRadius: 8, border: '1px solid #e5e7eb' }}>
                      {jsonData.description && (
                        <div style={{ padding: 16, borderBottom: '1px solid #e5e7eb' }}>
                          <h4 style={{ margin: 0, marginBottom: 8, fontSize: 16, fontWeight: 600 }}>Analysis Overview</h4>
                          <p style={{ margin: 0, fontSize: 14, color: '#6b7280', lineHeight: 1.5 }}>
                            {jsonData.description}
                          </p>
                        </div>
                      )}
                      <div style={{ padding: 16 }}>
                        <h4 style={{ margin: 0, marginBottom: 12, fontSize: 16, fontWeight: 600 }}>Data Points</h4>
                        <div style={{ display: 'grid', gap: 12 }}>
                          {jsonData.body?.map((item: any, idx: number) => (
                            <div key={idx} style={{ padding: 12, background: '#f8f9fa', borderRadius: 6, border: '1px solid #e5e7eb' }}>
                              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: 4 }}>
                                <strong style={{ fontSize: 14, color: '#374151' }}>{item.key}</strong>
                                <span style={{ fontSize: 14, fontWeight: 600, color: '#059669' }}>{String(item.value)}</span>
                              </div>
                              <p style={{ margin: 0, fontSize: 13, color: '#6b7280', lineHeight: 1.4 }}>
                                {item.description}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  );
                })()}
              </div>
            </div>
          )}

          {loading ? (
            <div>Loading…</div>
          ) : experimental.length === 0 ? (
            <div style={{ color: '#6b7280', textAlign: 'center', padding: 32 }}>
              <div style={{ fontSize: 16, marginBottom: 8 }}>No experimental visuals to preview</div>
              <div style={{ fontSize: 14, marginBottom: 16 }}>Create new experimental visuals to see them here for approval.</div>
              {approved.length > 0 && (
                <div style={{ marginTop: 16 }}>
                  <a 
                    href="/approved" 
                    style={{ 
                      color: '#1d4ed8', 
                      textDecoration: 'none',
                      padding: '8px 16px',
                      border: '1px solid #1d4ed8',
                      borderRadius: 6,
                      fontSize: 14
                    }}
                  >
                    View {approved.length} Approved Visual{approved.length !== 1 ? 's' : ''} →
                  </a>
                </div>
              )}
            </div>
          ) : null}
        </div>
      </div>
    </div>
  );
}
