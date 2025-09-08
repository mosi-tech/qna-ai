import React from 'react';

type Position = {
  symbol: string;
  qty: number;
  market_value: number;
  avg_entry_price?: number;
  unrealized_pl?: number;
};

type Account = {
  buying_power: number;
  cash: number;
  portfolio_value: number;
};

export default function AccountOverview({
  account = { buying_power: 245432.61, cash: 122086.5, portfolio_value: 123346.11 },
  positions = [
    { symbol: 'AAPL', qty: 20, market_value: 3850.2, avg_entry_price: 180.5, unrealized_pl: 120.4 },
    { symbol: 'MSFT', qty: 10, market_value: 3525.1, avg_entry_price: 335.2, unrealized_pl: -40.7 },
    { symbol: 'NVDA', qty: 5, market_value: 2478.0, avg_entry_price: 450.0, unrealized_pl: 75.0 },
  ],
}: {
  account?: Account;
  positions?: Position[];
}) {
  const sorted = [...positions].sort((a, b) => b.market_value - a.market_value).slice(0, 5);
  return (
    <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 12 }}>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 12 }}>
        <Metric label="Buying Power" value={account.buying_power} />
        <Metric label="Cash" value={account.cash} />
        <Metric label="Portfolio Value" value={account.portfolio_value} />
      </div>
      <div style={{ border: '1px solid #e5e7eb', borderRadius: 8, overflow: 'hidden', background: '#fff' }}>
        <div style={{ padding: 10, borderBottom: '1px solid #e5e7eb', fontWeight: 600 }}>Top Positions by Market Value</div>
        <table style={{ width: '100%', borderCollapse: 'collapse' }}>
          <thead>
            <tr style={{ background: '#f9fafb', textAlign: 'left' }}>
              <Th>Symbol</Th>
              <Th>Qty</Th>
              <Th>Market Value</Th>
              <Th>Avg Entry</Th>
              <Th>Unrealized P/L</Th>
            </tr>
          </thead>
          <tbody>
            {sorted.map((p) => (
              <tr key={p.symbol}>
                <Td>{p.symbol}</Td>
                <Td>{p.qty}</Td>
                <Td>${p.market_value.toLocaleString()}</Td>
                <Td>{p.avg_entry_price ? `$${p.avg_entry_price.toLocaleString()}` : '—'}</Td>
                <Td style={{ color: (p.unrealized_pl || 0) >= 0 ? '#059669' : '#b91c1c' }}>
                  {p.unrealized_pl !== undefined ? `$${p.unrealized_pl.toLocaleString()}` : '—'}
                </Td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <div style={{ fontSize: 12, color: '#6b7280' }}>
        Data can be fetched from Alpaca Trading API: GET /v2/account and GET /v2/positions.
      </div>
      <div style={{ fontSize: 12 }}>
        <span style={{ color: '#6b7280' }}>You might also ask:</span>{' '}
        <em>What is my unrealized P/L by position over the past week?</em>
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div style={{ padding: 12, border: '1px solid #e5e7eb', borderRadius: 8, background: '#fff' }}>
      <div style={{ fontSize: 12, color: '#6b7280' }}>{label}</div>
      <div style={{ fontSize: 20, fontWeight: 700 }}>${value.toLocaleString()}</div>
    </div>
  );
}

function Th({ children }: { children: React.ReactNode }) {
  return <th style={{ padding: 8, fontSize: 12, color: '#374151', borderBottom: '1px solid #e5e7eb' }}>{children}</th>;
}

function Td({ children }: { children: React.ReactNode }) {
  return <td style={{ padding: 8, borderBottom: '1px solid #f3f4f6' }}>{children}</td>;
}
