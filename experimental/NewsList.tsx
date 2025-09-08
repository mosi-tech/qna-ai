import React from 'react';

type NewsItem = {
  id: string;
  headline: string;
  author?: string;
  source?: string;
  url?: string;
  created_at?: string;
};

export default function NewsList({
  symbol = 'AAPL',
  latestPrice = { price: 229.51, changePct: 0.84 },
  items = [
    {
      id: 'n1',
      headline: 'Apple unveils new product lineup at fall event',
      source: 'ExampleWire',
      created_at: '2024-09-12T14:05:00Z',
      url: '#',
    },
    {
      id: 'n2',
      headline: 'Analyst raises AAPL price target on strong services growth',
      source: 'MarketDaily',
      created_at: '2024-09-12T11:42:00Z',
      url: '#',
    },
    {
      id: 'n3',
      headline: 'Supply chain checks point to resilient iPhone demand',
      source: 'TechNews',
      created_at: '2024-09-11T20:15:00Z',
      url: '#',
    },
  ],
  position,
}: {
  symbol?: string;
  latestPrice?: { price: number; changePct?: number };
  items?: NewsItem[];
  position?: { qty?: number; avg_entry_price?: number; market_value?: number };
}) {
  const trendColor = (latestPrice.changePct ?? 0) >= 0 ? '#059669' : '#b91c1c';
  return (
    <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, background: '#fff', overflow: 'hidden' }}>
      <div style={{ padding: 12, borderBottom: '1px solid #e5e7eb', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div style={{ fontWeight: 600 }}>News: {symbol}</div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          <div style={{ fontSize: 12 }}>
            <span style={{ color: '#6b7280', marginRight: 6 }}>Price:</span>
            <span style={{ fontWeight: 700 }}>${latestPrice.price.toFixed(2)}</span>
            {typeof latestPrice.changePct === 'number' && (
              <span style={{ marginLeft: 8, color: trendColor }}>
                {latestPrice.changePct >= 0 ? '▲' : '▼'} {Math.abs(latestPrice.changePct).toFixed(2)}%
              </span>
            )}
          </div>
        </div>
      </div>
      <div>
        {items.map((n) => (
          <a key={n.id} href={n.url || '#'} style={{ display: 'block', textDecoration: 'none', color: 'inherit', borderBottom: '1px solid #f3f4f6' }}>
            <div style={{ padding: 12 }}>
              <div style={{ fontWeight: 600 }}>{n.headline}</div>
              <div style={{ fontSize: 12, color: '#6b7280' }}>
                {n.source || '—'} {n.created_at ? '· ' + new Date(n.created_at).toLocaleString() : ''}
              </div>
            </div>
          </a>
        ))}
        {items.length === 0 && (
          <div style={{ padding: 12, color: '#6b7280' }}>No recent news.</div>
        )}
      </div>
      {position && (
        <div style={{ padding: '0 12px 12px', fontSize: 12, color: '#6b7280' }}>
          Position: {position.qty ?? '—'} shares
          {position.avg_entry_price ? ` @ $${Number(position.avg_entry_price).toLocaleString()}` : ''}
          {position.market_value ? ` · MV $${Number(position.market_value).toLocaleString()}` : ''}
        </div>
      )}
      <div style={{ padding: '0 12px 12px', fontSize: 12, color: '#6b7280' }}>
        Backed by Alpaca Market Data API: GET /v1beta1/news with query params (symbols, start, end, limit).
      </div>
      <div style={{ padding: '0 12px 12px', fontSize: 12 }}>
        <span style={{ color: '#6b7280' }}>You might also ask:</span>{' '}
        <em>How did {symbol} price move around these headlines over the last 24 hours?</em>
      </div>
    </div>
  );
}
