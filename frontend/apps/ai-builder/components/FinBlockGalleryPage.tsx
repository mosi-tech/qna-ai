/**
 * FinBlock Gallery Page
 * Complete showcase of all 110 finBlocks with live previews
 */

'use client';

import React, { useState, useMemo } from 'react';

interface FinBlockItem {
  id: string;
  name: string;
  category: string;
  description: string;
  samplePreview: React.ReactNode;
}

const MetricCard = ({ label, value, change, isPositive }: any) => (
  <div className="bg-white dark:bg-slate-700 p-3 rounded border border-slate-200 dark:border-slate-600">
    <div className="text-xs text-gray-600 dark:text-gray-300 mb-1">{label}</div>
    <div className="text-lg font-bold text-gray-900 dark:text-white">{value}</div>
    {change && <div className={`text-xs ${isPositive ? 'text-green-600 dark:text-green-400' : 'text-red-600 dark:text-red-400'}`}>{change}</div>}
  </div>
);

const FINBLOCKS: FinBlockItem[] = [
  // PORTFOLIO (12)
  {
    id: 'portfolio-kpi-summary',
    name: 'Portfolio KPI Summary',
    category: 'portfolio',
    description: 'Overview of key portfolio metrics',
    samplePreview: (
      <div className="grid grid-cols-4 gap-3">
        <MetricCard label="Portfolio Value" value="$120,505" change="+2.3%" isPositive={true} />
        <MetricCard label="Total P&L" value="$8,505" change="+7.6%" isPositive={true} />
        <MetricCard label="YTD Return" value="12.3%" change="+1.2%" isPositive={true} />
        <MetricCard label="Sharpe Ratio" value="1.85" change="+0.15" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'holdings-table',
    name: 'Holdings Table',
    category: 'portfolio',
    description: 'Detailed holdings breakdown',
    samplePreview: (
      <div className="text-sm overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-200 dark:border-slate-600">
              <th className="text-left py-2 px-2 font-semibold text-gray-700 dark:text-gray-300">Symbol</th>
              <th className="text-right py-2 px-2 font-semibold">Shares</th>
              <th className="text-right py-2 px-2 font-semibold">Price</th>
              <th className="text-right py-2 px-2 font-semibold">Value</th>
              <th className="text-right py-2 px-2 font-semibold">%</th>
            </tr>
          </thead>
          <tbody className="text-xs">
            <tr className="border-b"><td className="py-1 px-2">AAPL</td><td className="text-right">50</td><td className="text-right">$189.95</td><td className="text-right">$9,497</td><td className="text-right">7.9%</td></tr>
            <tr className="border-b"><td className="py-1 px-2">MSFT</td><td className="text-right">30</td><td className="text-right">$424.55</td><td className="text-right">$12,736</td><td className="text-right">10.6%</td></tr>
            <tr><td className="py-1 px-2">GOOGL</td><td className="text-right">25</td><td className="text-right">$152.30</td><td className="text-right">$3,807</td><td className="text-right">3.2%</td></tr>
          </tbody>
        </table>
      </div>
    ),
  },
  {
    id: 'sector-allocation-donut',
    name: 'Sector Allocation',
    category: 'portfolio',
    description: 'Sector distribution visualization',
    samplePreview: (
      <div className="flex items-center gap-6">
        <div className="w-32 h-32 rounded-full border-8 border-blue-500" style={{backgroundImage: 'conic-gradient(blue 0deg 108deg, green 108deg 180deg, orange 180deg 252deg, red 252deg 360deg)'}} />
        <div className="text-xs space-y-1">
          <div><span className="inline-block w-3 h-3 bg-blue-500 mr-2 rounded"></span>Technology 30%</div>
          <div><span className="inline-block w-3 h-3 bg-green-500 mr-2 rounded"></span>Healthcare 20%</div>
          <div><span className="inline-block w-3 h-3 bg-orange-500 mr-2 rounded"></span>Finance 20%</div>
          <div><span className="inline-block w-3 h-3 bg-red-500 mr-2 rounded"></span>Other 30%</div>
        </div>
      </div>
    ),
  },
  {
    id: 'asset-class-allocation',
    name: 'Asset Class Allocation',
    category: 'portfolio',
    description: 'Asset class breakdown',
    samplePreview: (
      <div className="space-y-2">
        {[{name: 'Stocks', pct: 65}, {name: 'Bonds', pct: 25}, {name: 'Cash', pct: 10}].map(a => (
          <div key={a.name} className="flex items-center gap-2">
            <div className="w-20 text-xs font-medium">{a.name}</div>
            <div className="flex-1 bg-slate-200 dark:bg-slate-600 h-5 rounded overflow-hidden">
              <div className="bg-blue-500 h-full flex items-center justify-end pr-2 text-xs text-white font-bold" style={{width: `${a.pct}%`}}>{a.pct}%</div>
            </div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'portfolio-performance-vs-benchmark',
    name: 'Performance vs Benchmark',
    category: 'portfolio',
    description: 'Returns comparison',
    samplePreview: (
      <div className="flex items-end gap-4 h-32">
        {[{name: '1Y', port: 12.3, bench: 10.2}, {name: '3Y', port: 8.5, bench: 7.2}, {name: '5Y', port: 9.8, bench: 8.1}].map(p => (
          <div key={p.name} className="flex-1 flex flex-col items-center gap-1">
            <div className="flex gap-1 items-end h-20">
              <div className="bg-blue-500 rounded-t" style={{width: '10px', height: `${p.port * 1.5}px`}}></div>
              <div className="bg-gray-400 rounded-t" style={{width: '10px', height: `${p.bench * 1.5}px`}}></div>
            </div>
            <div className="text-xs font-bold">{p.name}</div>
          </div>
        ))}
        <div className="text-xs"><span className="inline-block w-3 h-3 bg-blue-500 mr-1"></span>Portfolio <span className="inline-block w-3 h-3 bg-gray-400 mr-1 ml-2"></span>Benchmark</div>
      </div>
    ),
  },
  {
    id: 'price-movements-spark',
    name: 'Price Movements',
    category: 'portfolio',
    description: 'Sparkline price trends',
    samplePreview: (
      <div className="space-y-2 text-sm">
        {['AAPL', 'MSFT', 'GOOGL'].map(sym => (
          <div key={sym} className="flex items-center gap-3">
            <div className="w-12 font-mono text-xs font-bold">{sym}</div>
            <svg width="100" height="20" className="flex-1">
              <polyline points="0,15 10,12 20,14 30,8 40,10 50,5 60,8 70,6 80,9 90,4 100,7" fill="none" stroke="rgb(59,130,246)" strokeWidth="1.5"/>
            </svg>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'top-bottom-performers',
    name: 'Top/Bottom Performers',
    category: 'portfolio',
    description: 'Best and worst performers',
    samplePreview: (
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div>
          <div className="font-semibold text-green-600 dark:text-green-400 mb-2">Top Performers</div>
          <div className="space-y-1"><div>NVDA +45.2%</div><div>TSLA +38.5%</div><div>AMD +32.1%</div></div>
        </div>
        <div>
          <div className="font-semibold text-red-600 dark:text-red-400 mb-2">Worst Performers</div>
          <div className="space-y-1"><div>GE -15.3%</div><div>F -12.8%</div><div>BAC -8.5%</div></div>
        </div>
      </div>
    ),
  },
  {
    id: 'monthly-returns-bar',
    name: 'Monthly Returns',
    category: 'portfolio',
    description: 'Monthly return distribution',
    samplePreview: (
      <div className="flex items-end gap-2 h-28">
        {['J', 'F', 'M', 'A', 'M', 'J', 'J', 'A', 'S', 'O', 'N', 'D'].map((m, i) => (
          <div key={m} className="flex-1 flex flex-col items-center gap-1">
            <div className={`w-full rounded-t ${[2.1, -1.5, 3.2, 1.8, -0.5, 2.3, 4.1, 1.2, -2.3, 3.5, 1.9, 2.1][i] > 0 ? 'bg-green-500' : 'bg-red-500'}`} style={{height: `${Math.abs([2.1, -1.5, 3.2, 1.8, -0.5, 2.3, 4.1, 1.2, -2.3, 3.5, 1.9, 2.1][i]) * 10}px`}}></div>
            <div className="text-xs font-bold">{m}</div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'concentration-by-holding',
    name: 'Concentration Analysis',
    category: 'portfolio',
    description: 'Position concentration risk',
    samplePreview: (
      <div className="space-y-2 text-sm">
        {[{pos: 'Top 10%', pct: 35}, {pos: '11-25%', pct: 28}, {pos: '26-50%', pct: 22}, {pos: '51%+', pct: 15}].map(c => (
          <div key={c.pos} className="flex items-center gap-2">
            <div className="w-16 text-xs">{c.pos}</div>
            <div className="flex-1 bg-slate-200 dark:bg-slate-600 h-4 rounded" style={{background: `linear-gradient(90deg, rgb(59,130,246) ${c.pct}%, rgb(203,213,225) ${c.pct}%)`}}></div>
            <div className="w-12 text-right text-xs font-bold">{c.pct}%</div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'portfolio-turnover-table',
    name: 'Portfolio Turnover',
    category: 'portfolio',
    description: 'Trading activity analysis',
    samplePreview: (
      <div className="text-xs space-y-1">
        <div className="grid grid-cols-4 gap-2 font-semibold border-b pb-1">
          <div>Period</div><div className="text-right">Turnover</div><div className="text-right">Trades</div><div className="text-right">Cost</div>
        </div>
        {[{p: 'YTD', t: '45%', tr: '23', c: '$1,250'}, {p: '1Y', t: '52%', tr: '31', c: '$2,100'}, {p: '3Y', t: '38%', tr: '22', c: '$1,850'}].map(r => (
          <div key={r.p} className="grid grid-cols-4 gap-2">
            <div>{r.p}</div><div className="text-right">{r.t}</div><div className="text-right">{r.tr}</div><div className="text-right">{r.c}</div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'dividend-summary-kpi',
    name: 'Dividend Summary',
    category: 'portfolio',
    description: 'Dividend income overview',
    samplePreview: (
      <div className="grid grid-cols-4 gap-3">
        <MetricCard label="Annual Dividend" value="$4,825" change="+3.2%" isPositive={true} />
        <MetricCard label="Yield" value="4.0%" change="+0.1%" isPositive={true} />
        <MetricCard label="Next Payment" value="$402" change="Mar 15" isPositive={true} />
        <MetricCard label="Payout Ratio" value="35%" change="Healthy" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'portfolio-risk-summary',
    name: 'Portfolio Risk Summary',
    category: 'portfolio',
    description: 'Risk metrics overview',
    samplePreview: (
      <div className="grid grid-cols-4 gap-3">
        <MetricCard label="Volatility" value="18.5%" change="Normal" isPositive={true} />
        <MetricCard label="Max Drawdown" value="-12.5%" change="5Y" isPositive={false} />
        <MetricCard label="Beta" value="1.05" change="Market" isPositive={true} />
        <MetricCard label="VaR (95%)" value="$8.5k" change="Daily" isPositive={false} />
      </div>
    ),
  },

  // STOCK RESEARCH (12)
  {
    id: 'stock-price-kpi',
    name: 'Stock Price KPI',
    category: 'stock_research',
    description: 'Current price and change',
    samplePreview: (
      <div className="grid grid-cols-3 gap-4">
        <MetricCard label="AAPL" value="$189.95" change="+2.1%" isPositive={true} />
        <MetricCard label="MSFT" value="$424.55" change="-0.4%" isPositive={false} />
        <MetricCard label="GOOGL" value="$152.30" change="+1.8%" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'price-history-with-ma',
    name: 'Price History with MA',
    category: 'stock_research',
    description: 'Historical price with moving averages',
    samplePreview: (
      <svg width="100%" height="100" viewBox="0 0 300 100">
        <polyline points="0,60 30,50 60,45 90,40 120,35 150,30 180,35 210,40 240,45 270,50 300,55" fill="none" stroke="rgb(59,130,246)" strokeWidth="2"/>
        <polyline points="0,55 30,52 60,50 90,48 120,47 150,48 180,50 210,52 240,54 270,55 300,56" fill="none" stroke="rgb(107,114,128)" strokeWidth="2" strokeDasharray="5,5"/>
        <line x1="0" y1="80" x2="300" y2="80" stroke="rgb(226,232,240)" strokeWidth="1"/>
      </svg>
    ),
  },
  {
    id: 'fundamental-metrics-list',
    name: 'Fundamental Metrics',
    category: 'stock_research',
    description: 'Key fundamental ratios',
    samplePreview: (
      <div className="grid grid-cols-2 gap-2 text-xs">
        {[{name: 'P/E', val: '28.5'}, {name: 'PEG', val: '1.2'}, {name: 'Debt/Equity', val: '0.45'}, {name: 'ROE', val: '22%'}, {name: 'Div Yield', val: '0.6%'}, {name: 'FCF', val: '$85.2B'}].map(m => (
          <div key={m.name} className="flex justify-between">
            <span className="text-gray-600 dark:text-gray-300">{m.name}</span>
            <span className="font-bold">{m.val}</span>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'earnings-history-table',
    name: 'Earnings History',
    category: 'stock_research',
    description: 'Historical earnings data',
    samplePreview: (
      <div className="text-xs space-y-1">
        <div className="grid grid-cols-4 gap-2 font-semibold border-b pb-1">
          <div>Quarter</div><div className="text-right">EPS</div><div className="text-right">Revenue</div><div className="text-right">Beat</div>
        </div>
        {[{q: 'Q4 24', eps: '$2.18', rev: '$89.5B', beat: '✓'}, {q: 'Q3 24', eps: '$2.12', rev: '$88.3B', beat: '✓'}, {q: 'Q2 24', eps: '$1.97', rev: '$85.8B', beat: '✓'}].map(e => (
          <div key={e.q} className="grid grid-cols-4 gap-2">
            <div>{e.q}</div><div className="text-right">{e.eps}</div><div className="text-right">{e.rev}</div><div className="text-right text-green-600">{e.beat}</div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'analyst-ratings-bar',
    name: 'Analyst Ratings',
    category: 'stock_research',
    description: 'Analyst consensus',
    samplePreview: (
      <div className="space-y-2">
        {[{rating: 'Buy', count: 28, color: 'bg-green-500'}, {rating: 'Hold', count: 8, color: 'bg-yellow-500'}, {rating: 'Sell', count: 2, color: 'bg-red-500'}].map(r => (
          <div key={r.rating} className="flex items-center gap-2">
            <div className="w-12 text-xs font-medium">{r.rating}</div>
            <div className="flex-1 bg-slate-200 dark:bg-slate-600 h-4 rounded overflow-hidden">
              <div className={`${r.color} h-full flex items-center justify-end pr-2 text-xs text-white`} style={{width: `${r.count * 2}%`}}>{r.count}</div>
            </div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'dividend-history-line',
    name: 'Dividend History',
    category: 'stock_research',
    description: 'Historical dividend trends',
    samplePreview: (
      <svg width="100%" height="80" viewBox="0 0 300 80">
        <polyline points="0,70 30,65 60,60 90,55 120,50 150,45 180,40 210,35 240,30 270,25 300,20" fill="none" stroke="rgb(34,197,94)" strokeWidth="2"/>
        <circle cx="300" cy="20" r="3" fill="rgb(34,197,94)"/>
      </svg>
    ),
  },
  {
    id: 'valuation-comparison',
    name: 'Valuation Comparison',
    category: 'stock_research',
    description: 'Valuation vs peers',
    samplePreview: (
      <div className="text-xs space-y-2">
        <div className="grid grid-cols-3 gap-2 font-semibold border-b pb-1">
          <div>Company</div><div className="text-right">P/E</div><div className="text-right">vs Sector</div>
        </div>
        {[{co: 'AAPL', pe: '28.5', vs: '+5.2%'}, {co: 'Sector Avg', pe: '27.1', vs: '-'}, {co: 'Industry', pe: '24.8', vs: '-8.5%'}].map(v => (
          <div key={v.co} className="grid grid-cols-3 gap-2">
            <div>{v.co}</div><div className="text-right">{v.pe}</div><div className={`text-right ${v.vs.includes('-') ? 'text-red-600' : 'text-green-600'}`}>{v.vs}</div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'insider-transactions-table',
    name: 'Insider Transactions',
    category: 'stock_research',
    description: 'Insider trading activity',
    samplePreview: (
      <div className="text-xs space-y-1">
        <div className="grid grid-cols-4 gap-2 font-semibold border-b pb-1">
          <div>Insider</div><div className="text-right">Type</div><div className="text-right">Shares</div><div className="text-right">Value</div>
        </div>
        {[{ins: 'CEO', type: 'Buy', sh: '5,000', val: '$950K'}, {ins: 'CFO', type: 'Buy', sh: '2,500', val: '$475K'}, {ins: 'Director', type: 'Sell', sh: '10,000', val: '$1.9M'}].map(t => (
          <div key={t.ins} className="grid grid-cols-4 gap-2">
            <div>{t.ins}</div><div className={t.type === 'Buy' ? 'text-green-600' : 'text-red-600'}>{t.type}</div><div className="text-right">{t.sh}</div><div className="text-right">{t.val}</div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'technical-indicators-kpi',
    name: 'Technical Indicators',
    category: 'stock_research',
    description: 'Technical analysis metrics',
    samplePreview: (
      <div className="grid grid-cols-4 gap-3 text-xs">
        <MetricCard label="RSI" value="65" change="Neutral" isPositive={true} />
        <MetricCard label="MACD" value="Bullish" change="Cross" isPositive={true} />
        <MetricCard label="50MA" value="Above" change="Trend+" isPositive={true} />
        <MetricCard label="Support" value="$185" change="Near" isPositive={false} />
      </div>
    ),
  },
  {
    id: 'volume-trend-bar',
    name: 'Volume Trend',
    category: 'stock_research',
    description: 'Trading volume analysis',
    samplePreview: (
      <div className="flex items-end gap-1 h-24">
        {[45, 52, 38, 62, 48, 71, 55, 68, 42, 75].map((v, i) => (
          <div key={i} className="flex-1 bg-blue-500 rounded-t" style={{height: `${v / 75 * 100}%`, opacity: 0.7 + (i / 10) * 0.3}}></div>
        ))}
      </div>
    ),
  },
  {
    id: 'growth-metrics-comparison',
    name: 'Growth Metrics',
    category: 'stock_research',
    description: 'Growth rates comparison',
    samplePreview: (
      <div className="grid grid-cols-2 gap-4 text-sm">
        <div><div className="font-semibold mb-2">Revenue Growth</div><div className="space-y-1 text-xs"><div>1Y: 12.3%</div><div>3Y: 18.5%</div><div>5Y: 15.2%</div></div></div>
        <div><div className="font-semibold mb-2">EPS Growth</div><div className="space-y-1 text-xs"><div>1Y: 14.2%</div><div>3Y: 22.1%</div><div>5Y: 19.8%</div></div></div>
      </div>
    ),
  },

  // ETF ANALYSIS (10)
  {
    id: 'etf-comparison-metrics',
    name: 'ETF Comparison',
    category: 'etf_analysis',
    description: 'ETF comparison metrics',
    samplePreview: (
      <div className="text-xs overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b"><th className="text-left py-1">ETF</th><th className="text-right">1Y</th><th className="text-right">ER</th><th className="text-right">AUM</th></tr>
          </thead>
          <tbody>
            {[{n: 'SPY', r: '18.5%', e: '0.03%', a: '$425B'}, {n: 'VOO', r: '18.3%', e: '0.03%', a: '$285B'}, {n: 'IVV', r: '18.2%', e: '0.04%', a: '$215B'}].map(t => (
              <tr key={t.n} className="border-b"><td>{t.n}</td><td className="text-right text-green-600">{t.r}</td><td className="text-right">{t.e}</td><td className="text-right">{t.a}</td></tr>
            ))}
          </tbody>
        </table>
      </div>
    ),
  },
  {
    id: 'etf-performance-line',
    name: 'ETF Performance',
    category: 'etf_analysis',
    description: 'ETF return trends',
    samplePreview: (
      <svg width="100%" height="80" viewBox="0 0 300 80">
        <polyline points="0,60 30,50 60,45 90,40 120,35 150,30 180,35 210,40 240,45 270,50 300,55" fill="none" stroke="rgb(59,130,246)" strokeWidth="2"/>
      </svg>
    ),
  },
  {
    id: 'etf-sector-allocation',
    name: 'ETF Sector Allocation',
    category: 'etf_analysis',
    description: 'Sector distribution',
    samplePreview: (
      <div className="space-y-1 text-xs">
        {[{s: 'Tech', p: 28}, {s: 'Health', p: 15}, {s: 'Fin', p: 12}, {s: 'Cons', p: 9}, {s: 'Other', p: 36}].map(x => (
          <div key={x.s} className="flex items-center gap-2"><div className="w-12">{x.s}</div><div className="flex-1 bg-slate-200 h-3 rounded" style={{background: `linear-gradient(90deg, rgb(59,130,246) ${x.p}%, rgb(203,213,225) ${x.p}%)`}}></div><div className="w-8 text-right">{x.p}%</div></div>
        ))}
      </div>
    ),
  },
  {
    id: 'etf-top-holdings',
    name: 'ETF Top Holdings',
    category: 'etf_analysis',
    description: 'Top holdings list',
    samplePreview: (
      <div className="text-xs space-y-1">
        {[{t: 'AAPL', w: '7.2%'}, {t: 'MSFT', w: '6.5%'}, {t: 'GOOGL', w: '3.9%'}, {t: 'AMZN', w: '3.2%'}, {t: 'NVDA', w: '2.8%'}].map(h => (
          <div key={h.t} className="flex justify-between"><span>{h.t}</span><span className="font-bold">{h.w}</span></div>
        ))}
      </div>
    ),
  },
  {
    id: 'etf-risk-metrics',
    name: 'ETF Risk Metrics',
    category: 'etf_analysis',
    description: 'Risk analysis',
    samplePreview: (
      <div className="grid grid-cols-2 gap-3 text-xs">
        <MetricCard label="Volatility" value="15.2%" change="Normal" isPositive={true} />
        <MetricCard label="Max DD" value="-18.5%" change="2022" isPositive={false} />
        <MetricCard label="Sharpe" value="1.35" change="Good" isPositive={true} />
        <MetricCard label="Beta" value="1.00" change="Market" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'etf-dividend-yield-trend',
    name: 'ETF Dividend Yield Trend',
    category: 'etf_analysis',
    description: 'Dividend yield analysis',
    samplePreview: (
      <svg width="100%" height="70" viewBox="0 0 300 70">
        <polyline points="0,40 30,38 60,35 90,33 120,31 150,30 180,32 210,35 240,38 270,40 300,42" fill="none" stroke="rgb(34,197,94)" strokeWidth="2"/>
        <text x="10" y="60" fontSize="12" fill="currentColor">Yield trending +0.15%</text>
      </svg>
    ),
  },
  {
    id: 'etf-overlap-analysis',
    name: 'ETF Overlap Analysis',
    category: 'etf_analysis',
    description: 'Portfolio overlap detection',
    samplePreview: (
      <div className="text-xs space-y-1">
        <div className="font-semibold mb-2">ETF Overlap Matrix</div>
        {[{pair: 'SPY vs VOO', overlap: '96.2%'}, {pair: 'SPY vs IWM', overlap: '25.3%'}, {pair: 'QQQ vs IWM', overlap: '18.5%'}].map(o => (
          <div key={o.pair} className="flex justify-between"><span>{o.pair}</span><span className="font-bold">{o.overlap}</span></div>
        ))}
      </div>
    ),
  },
  {
    id: 'etf-expense-ratio-impact',
    name: 'ETF Expense Impact',
    category: 'etf_analysis',
    description: 'Fee impact analysis',
    samplePreview: (
      <div className="text-xs space-y-2">
        <div className="font-semibold">10-Year Fee Impact ($10K invested)</div>
        <div className="space-y-1">
          {[{etf: '0.03% ER (SPY)', impact: '$309'}, {etf: '0.20% ER', impact: '$2,050'}, {etf: '0.75% ER', impact: '$7,560'}].map(f => (
            <div key={f.etf} className="flex justify-between"><span>{f.etf}</span><span className="font-bold">{f.impact}</span></div>
          ))}
        </div>
      </div>
    ),
  },
  {
    id: 'etf-geographic-exposure',
    name: 'ETF Geographic Exposure',
    category: 'etf_analysis',
    description: 'Geographic diversification',
    samplePreview: (
      <div className="space-y-1 text-xs">
        {[{region: 'USA', pct: 65}, {region: 'Europe', pct: 18}, {region: 'Asia', pct: 15}, {region: 'Other', pct: 2}].map(g => (
          <div key={g.region} className="flex items-center gap-2"><div className="w-14">{g.region}</div><div className="flex-1 bg-slate-200 h-3 rounded" style={{background: `linear-gradient(90deg, rgb(59,130,246) ${g.pct}%, rgb(203,213,225) ${g.pct}%)`}}></div><div className="w-8 text-right">{g.pct}%</div></div>
        ))}
      </div>
    ),
  },
  {
    id: 'etf-tax-efficiency',
    name: 'ETF Tax Efficiency',
    category: 'etf_analysis',
    description: 'Tax efficiency metrics',
    samplePreview: (
      <div className="grid grid-cols-2 gap-3 text-xs">
        <MetricCard label="Tax Efficiency" value="92%" change="Excellent" isPositive={true} />
        <MetricCard label="Annual Dist" value="0.8%" change="Low" isPositive={true} />
        <MetricCard label="Turnover" value="12%" change="Passive" isPositive={true} />
        <MetricCard label="Tax Loss" value="N/A" change="Efficient" isPositive={true} />
      </div>
    ),
  },

  // RISK MANAGEMENT (11)
  {
    id: 'risk-metrics-kpi',
    name: 'Risk Metrics KPI',
    category: 'risk_management',
    description: 'Key risk metrics',
    samplePreview: (
      <div className="grid grid-cols-4 gap-3">
        <MetricCard label="Volatility" value="18.5%" change="Normal" isPositive={true} />
        <MetricCard label="Max DD" value="-12.5%" change="5Y" isPositive={false} />
        <MetricCard label="VaR (95%)" value="$8.5k" change="Daily" isPositive={false} />
        <MetricCard label="Sharpe" value="1.45" change="Good" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'volatility-by-holding',
    name: 'Volatility by Holding',
    category: 'risk_management',
    description: 'Volatility breakdown',
    samplePreview: (
      <div className="space-y-2 text-xs">
        {[{hold: 'AAPL', vol: '28.5%'}, {hold: 'MSFT', vol: '22.1%'}, {hold: 'GOOGL', vol: '18.3%'}, {hold: 'BRK.B', vol: '15.2%'}].map(v => (
          <div key={v.hold} className="flex items-center gap-2"><div className="w-16">{v.hold}</div><div className="flex-1 bg-slate-200 h-3 rounded" style={{background: `linear-gradient(90deg, rgb(249,115,22) ${parseFloat(v.vol) / 30 * 100}%, rgb(203,213,225) ${parseFloat(v.vol) / 30 * 100}%)`}}></div><div className="w-12 text-right">{v.vol}</div></div>
        ))}
      </div>
    ),
  },
  {
    id: 'concentration-risk',
    name: 'Concentration Risk',
    category: 'risk_management',
    description: 'Concentration analysis',
    samplePreview: (
      <div className="grid grid-cols-2 gap-3 text-xs">
        <MetricCard label="HHI Index" value="0.082" change="Moderate" isPositive={true} />
        <MetricCard label="Top 10" value="35.2%" change="Reasonable" isPositive={true} />
        <MetricCard label="Top 50" value="82.5%" change="Concentrated" isPositive={false} />
        <MetricCard label="Diversified" value="Yes" change="Good" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'correlation-matrix',
    name: 'Correlation Matrix',
    category: 'risk_management',
    description: 'Asset correlations',
    samplePreview: (
      <div className="text-xs grid gap-2">
        <div className="grid grid-cols-4 gap-1 font-semibold">
          <div></div><div>SPY</div><div>BND</div><div>GLD</div>
        </div>
        {[{asset: 'SPY', corr: ['1.00', '0.12', '-0.15']}, {asset: 'BND', corr: ['0.12', '1.00', '0.08']}, {asset: 'GLD', corr: ['-0.15', '0.08', '1.00']}].map(r => (
          <div key={r.asset} className="grid grid-cols-4 gap-1">
            <div className="font-semibold">{r.asset}</div>
            {r.corr.map((c, i) => (
              <div key={i} className={`text-center ${Math.abs(parseFloat(c)) > 0.5 ? 'bg-red-100 dark:bg-red-900' : 'bg-green-100 dark:bg-green-900'} rounded px-1`}>{c}</div>
            ))}
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'drawdown-history',
    name: 'Drawdown History',
    category: 'risk_management',
    description: 'Drawdown visualization',
    samplePreview: (
      <svg width="100%" height="80" viewBox="0 0 300 80">
        <rect width="300" height="80" fill="rgb(241,245,249)"/>
        <polyline points="0,30 30,28 60,32 90,25 120,35 150,28 180,32 210,26 240,30 270,29 300,31" fill="none" stroke="rgb(59,130,246)" strokeWidth="2"/>
        <text x="10" y="70" fontSize="11" fill="currentColor">Max Drawdown: -12.5%</text>
      </svg>
    ),
  },
  {
    id: 'var-by-scenario',
    name: 'VaR by Scenario',
    category: 'risk_management',
    description: 'Value at risk scenarios',
    samplePreview: (
      <div className="space-y-2 text-xs">
        {[{scenario: 'Normal (95%)', var: '$8,500'}, {scenario: 'Stress (99%)', var: '$15,200'}, {scenario: '2008 Crisis', var: '$32,800'}, {scenario: 'COVID Crash', var: '$28,500'}].map(s => (
          <div key={s.scenario} className="flex justify-between"><span>{s.scenario}</span><span className="font-bold text-red-600">{s.var}</span></div>
        ))}
      </div>
    ),
  },
  {
    id: 'beta-analysis',
    name: 'Beta Analysis',
    category: 'risk_management',
    description: 'Systematic risk analysis',
    samplePreview: (
      <div className="grid grid-cols-2 gap-3 text-xs">
        <MetricCard label="Portfolio Beta" value="1.05" change="Market" isPositive={true} />
        <MetricCard label="Correlation" value="0.95" change="High" isPositive={true} />
        <MetricCard label="Alpha" value="+0.85%" change="/Year" isPositive={true} />
        <MetricCard label="Tracking Error" value="2.3%" change="Deviation" isPositive={false} />
      </div>
    ),
  },
  {
    id: 'downside-risk-analysis',
    name: 'Downside Risk Analysis',
    category: 'risk_management',
    description: 'Downside risk metrics',
    samplePreview: (
      <div className="grid grid-cols-2 gap-3 text-xs">
        <MetricCard label="Downside Dev" value="8.2%" change="Low" isPositive={true} />
        <MetricCard label="Sortino Ratio" value="1.82" change="Excellent" isPositive={true} />
        <MetricCard label="Upside/Down" value="1.85" change="Good" isPositive={true} />
        <MetricCard label="Omega Ratio" value="1.45" change="Favorable" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'sector-risk-exposure',
    name: 'Sector Risk Exposure',
    category: 'risk_management',
    description: 'Sector risk breakdown',
    samplePreview: (
      <div className="space-y-1 text-xs">
        {[{sector: 'Tech', beta: 1.15}, {sector: 'Health', beta: 0.95}, {sector: 'Finance', beta: 1.05}, {sector: 'Energy', beta: 1.25}, {sector: 'Utilities', beta: 0.80}].map(s => (
          <div key={s.sector} className="flex items-center gap-2"><div className="w-16">{s.sector}</div><div className="flex-1 bg-slate-200 h-3 rounded" style={{background: `linear-gradient(90deg, rgb(249,115,22) ${s.beta * 25}%, rgb(203,213,225) ${s.beta * 25}%)`}}></div><div className="w-8 text-right">β {s.beta}</div></div>
        ))}
      </div>
    ),
  },
  {
    id: 'stress-test-results',
    name: 'Stress Test Results',
    category: 'risk_management',
    description: 'Stress test scenarios',
    samplePreview: (
      <div className="text-xs space-y-2">
        <div className="font-semibold">Portfolio Loss Under Stress</div>
        {[{event: 'Market -10%', loss: '-9.8%'}, {event: 'Market -20%', loss: '-18.5%'}, {event: 'Rates +2%', loss: '-3.2%'}, {event: 'VIX +50%', loss: '-12.1%'}].map(t => (
          <div key={t.event} className="flex justify-between"><span>{t.event}</span><span className="font-bold text-red-600">{t.loss}</span></div>
        ))}
      </div>
    ),
  },
  {
    id: 'risk-limits-monitoring',
    name: 'Risk Limits Monitoring',
    category: 'risk_management',
    description: 'Risk limit tracking',
    samplePreview: (
      <div className="space-y-2 text-xs">
        {[{limit: 'Volatility', current: '18.5%', max: '20%', status: '✓'}, {limit: 'Drawdown', current: '-12.5%', max: '-15%', status: '✓'}, {limit: 'Beta', current: '1.05', max: '1.10', status: '✓'}, {limit: 'Concentration', current: '35.2%', max: '40%', status: '✓'}].map(l => (
          <div key={l.limit} className="flex items-center justify-between">
            <span>{l.limit}</span>
            <div className="flex gap-2 items-center">
              <span className="text-right w-12">{l.current}</span>
              <span className="text-gray-400">/</span>
              <span className="w-12">{l.max}</span>
              <span className="text-green-600">{l.status}</span>
            </div>
          </div>
        ))}
      </div>
    ),
  },

  // PERFORMANCE (11)
  {
    id: 'annual-returns-bar',
    name: 'Annual Returns',
    category: 'performance',
    description: 'Yearly return breakdown',
    samplePreview: (
      <div className="flex items-end gap-2 h-32">
        {[{y: '2019', r: 8.5}, {y: '2020', r: 18.2}, {y: '2021', r: 12.1}, {y: '2022', r: -8.3}, {y: '2023', r: 22.5}, {y: '2024', r: 12.3}].map(x => (
          <div key={x.y} className="flex-1 flex flex-col items-center gap-1"><div className={`w-full rounded-t ${x.r > 0 ? 'bg-green-500' : 'bg-red-500'}`} style={{height: `${Math.abs(x.r) * 3}px`}}></div><div className="text-xs font-bold">{x.y}</div></div>
        ))}
      </div>
    ),
  },
  {
    id: 'return-distribution',
    name: 'Return Distribution',
    category: 'performance',
    description: 'Return distribution analysis',
    samplePreview: (
      <svg width="100%" height="80" viewBox="0 0 300 80">
        <path d="M 30 70 Q 80 20, 150 15 Q 220 20, 270 70" fill="rgb(226,232,240)" stroke="rgb(59,130,246)" strokeWidth="2"/>
        <line x1="150" y1="15" x2="150" y2="70" stroke="rgb(249,115,22)" strokeWidth="2" strokeDasharray="5,5"/>
        <text x="10" y="70" fontSize="11" fill="currentColor">Returns: Normal Distribution</text>
      </svg>
    ),
  },
  {
    id: 'win-rate-metrics',
    name: 'Win Rate Metrics',
    category: 'performance',
    description: 'Win rate statistics',
    samplePreview: (
      <div className="grid grid-cols-2 gap-3 text-xs">
        <MetricCard label="Win Rate" value="62.3%" change="Good" isPositive={true} />
        <MetricCard label="Positive Days" value="158" change="/252" isPositive={true} />
        <MetricCard label="Profit Factor" value="1.85" change="Strong" isPositive={true} />
        <MetricCard label="Avg Win" value="$425" change="vs -$280" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'risk-adjusted-returns',
    name: 'Risk-Adjusted Returns',
    category: 'performance',
    description: 'Sharpe, Sortino, Calmar',
    samplePreview: (
      <div className="grid grid-cols-3 gap-3 text-xs">
        <MetricCard label="Sharpe" value="1.45" change="Good" isPositive={true} />
        <MetricCard label="Sortino" value="1.82" change="Excellent" isPositive={true} />
        <MetricCard label="Calmar" value="0.98" change="Decent" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'attribution-analysis',
    name: 'Attribution Analysis',
    category: 'performance',
    description: 'Return attribution',
    samplePreview: (
      <div className="space-y-2 text-xs">
        <div className="font-semibold mb-2">Return Attribution (12.3%)</div>
        {[{source: 'Stock Selection', contrib: '+4.2%'}, {source: 'Sector Allocation', contrib: '+2.1%'}, {source: 'Asset Allocation', contrib: '+1.5%'}, {source: 'Other', contrib: '+4.5%'}].map(a => (
          <div key={a.source} className="flex justify-between"><span>{a.source}</span><span className="font-bold text-green-600">{a.contrib}</span></div>
        ))}
      </div>
    ),
  },
  {
    id: 'upside-downside-capture',
    name: 'Upside/Downside Capture',
    category: 'performance',
    description: 'Capture ratios',
    samplePreview: (
      <div className="space-y-2 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-20">Upside Cap</div>
          <div className="flex-1 bg-green-500 h-4 rounded" style={{width: '105%'}}></div>
          <div className="w-12 text-right">105%</div>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-20">Downside Cap</div>
          <div className="flex-1 bg-blue-500 h-4 rounded" style={{width: '85%'}}></div>
          <div className="w-12 text-right">85%</div>
        </div>
      </div>
    ),
  },
  {
    id: 'rolling-returns',
    name: 'Rolling Returns',
    category: 'performance',
    description: 'Rolling return analysis',
    samplePreview: (
      <svg width="100%" height="80" viewBox="0 0 300 80">
        <polyline points="0,50 20,45 40,42 60,40 80,38 100,36 120,35 140,36 160,38 180,40 200,42 220,45 240,48 260,50 280,52 300,54" fill="none" stroke="rgb(59,130,246)" strokeWidth="2" opacity="0.7"/>
        <polyline points="0,55 20,50 40,46 60,43 80,42 100,42 120,44 140,47 160,50 180,52 200,54 220,56 240,57 260,58 280,59 300,60" fill="none" stroke="rgb(34,197,94)" strokeWidth="2"/>
        <text x="10" y="70" fontSize="11" fill="currentColor">3Y Rolling Returns trending up</text>
      </svg>
    ),
  },
  {
    id: 'best-worst-periods',
    name: 'Best/Worst Periods',
    category: 'performance',
    description: 'Performance extremes',
    samplePreview: (
      <div className="grid grid-cols-2 gap-4 text-xs">
        <div><div className="font-semibold text-green-600 mb-2">Best Periods</div><div className="space-y-1"><div>+22.5% (2023)</div><div>+18.2% (2020)</div><div>+12.1% (2021)</div></div></div>
        <div><div className="font-semibold text-red-600 mb-2">Worst Periods</div><div className="space-y-1"><div>-8.3% (2022)</div><div>-3.2% (COVID)</div><div>-2.1% (2018)</div></div></div>
      </div>
    ),
  },
  {
    id: 'alpha-generation',
    name: 'Alpha Generation',
    category: 'performance',
    description: 'Excess return analysis',
    samplePreview: (
      <div className="grid grid-cols-2 gap-3 text-xs">
        <MetricCard label="Annual Alpha" value="+0.85%" change="/Year" isPositive={true} />
        <MetricCard label="Consistency" value="68%" change="Good" isPositive={true} />
        <MetricCard label="Significance" value="p=0.042" change="Likely" isPositive={true} />
        <MetricCard label="Source" value="Stock Pick" change="Skill" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'returns-vs-goals',
    name: 'Returns vs Goals',
    category: 'performance',
    description: 'Goal tracking',
    samplePreview: (
      <div className="space-y-2 text-xs">
        {[{goal: 'Retirement 2035', actual: '8.5%', target: '7.0%', status: '✓'}, {goal: 'College Fund', actual: '6.2%', target: '6.0%', status: '✓'}, {goal: 'General Wealth', actual: '12.3%', target: '8.0%', status: '✓✓'}].map(g => (
          <div key={g.goal} className="flex justify-between">
            <span>{g.goal}</span>
            <div className="flex gap-4 items-center">
              <span className="text-right w-16">{g.actual} vs {g.target}</span>
              <span className="text-green-600">{g.status}</span>
            </div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'time-weighted-returns',
    name: 'Time-Weighted Returns',
    category: 'performance',
    description: 'TWR calculation',
    samplePreview: (
      <div className="text-xs space-y-2">
        <div className="font-semibold">Time-Weighted vs Money-Weighted</div>
        {[{period: '1Y TWR', val: '12.3%'}, {period: '1Y MWR', val: '10.8%'}, {period: 'Difference', val: '+1.5%'}, {period: 'Cash Flow Impact', val: 'Significant'}].map(t => (
          <div key={t.period} className="flex justify-between"><span>{t.period}</span><span className="font-bold">{t.val}</span></div>
        ))}
      </div>
    ),
  },

  // INCOME (9)
  {
    id: 'dividend-income-kpi',
    name: 'Dividend Income KPI',
    category: 'income',
    description: 'Income overview',
    samplePreview: (
      <div className="grid grid-cols-4 gap-3">
        <MetricCard label="Annual Div" value="$4,825" change="+3.2%" isPositive={true} />
        <MetricCard label="Yield" value="4.0%" change="+0.1%" isPositive={true} />
        <MetricCard label="Next Payment" value="$402" change="Mar 15" isPositive={true} />
        <MetricCard label="Frequency" value="Monthly" change="Stable" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'dividend-payers-table',
    name: 'Dividend Payers',
    category: 'income',
    description: 'Dividend payers list',
    samplePreview: (
      <div className="text-xs space-y-1">
        <div className="grid grid-cols-4 gap-2 font-semibold border-b pb-1">
          <div>Stock</div><div className="text-right">Dividend</div><div className="text-right">Yield</div><div className="text-right">Growth</div>
        </div>
        {[{s: 'JNJ', d: '$3.48', y: '3.1%', g: '5.2%'}, {s: 'KO', d: '$1.84', y: '3.5%', g: '3.8%'}, {s: 'PG', d: '$3.48', y: '2.3%', g: '6.1%'}].map(r => (
          <div key={r.s} className="grid grid-cols-4 gap-2"><div>{r.s}</div><div className="text-right">{r.d}</div><div className="text-right">{r.y}</div><div className="text-right text-green-600">{r.g}</div></div>
        ))}
      </div>
    ),
  },
  {
    id: 'monthly-dividend-trend',
    name: 'Monthly Dividend Trend',
    category: 'income',
    description: 'Income trend over time',
    samplePreview: (
      <svg width="100%" height="80" viewBox="0 0 300 80">
        <polyline points="0,60 25,55 50,52 75,50 100,48 125,46 150,45 175,46 200,48 225,50 250,52 275,55 300,58" fill="none" stroke="rgb(34,197,94)" strokeWidth="2"/>
        <text x="10" y="70" fontSize="11" fill="currentColor">Monthly dividend trending up</text>
      </svg>
    ),
  },
  {
    id: 'top-dividend-yielders',
    name: 'Top Dividend Yielders',
    category: 'income',
    description: 'Highest yield holdings',
    samplePreview: (
      <div className="text-xs space-y-1">
        {[{stock: 'O (Realty)', yield: '3.8%'}, {stock: 'T (AT&T)', yield: '6.2%'}, {stock: 'VZ (Verizon)', yield: '6.8%'}, {stock: 'PEP (Pepsi)', yield: '2.9%'}, {stock: 'JNJ', yield: '3.1%'}].map(t => (
          <div key={t.stock} className="flex justify-between"><span>{t.stock}</span><span className="font-bold text-green-600">{t.yield}</span></div>
        ))}
      </div>
    ),
  },
  {
    id: 'dividend-growth-analysis',
    name: 'Dividend Growth Analysis',
    category: 'income',
    description: 'Growth rate analysis',
    samplePreview: (
      <div className="space-y-2 text-xs">
        {[{period: '1Y Growth', val: '+3.2%'}, {period: '3Y CAGR', val: '+4.1%'}, {period: '5Y CAGR', val: '+4.8%'}, {period: '10Y CAGR', val: '+5.2%'}].map(g => (
          <div key={g.period} className="flex justify-between"><span>{g.period}</span><span className="font-bold text-green-600">{g.val}</span></div>
        ))}
      </div>
    ),
  },
  {
    id: 'sector-dividend-yield',
    name: 'Sector Dividend Yield',
    category: 'income',
    description: 'Sector yield breakdown',
    samplePreview: (
      <div className="space-y-1 text-xs">
        {[{sect: 'Utilities', yld: '3.8%'}, {sect: 'Telecom', yld: '4.5%'}, {sect: 'REITs', yld: '3.6%'}, {sect: 'Finance', yld: '3.2%'}, {sect: 'Energy', yld: '4.1%'}].map(s => (
          <div key={s.sect} className="flex items-center gap-2"><div className="w-14">{s.sect}</div><div className="flex-1 bg-slate-200 h-3 rounded" style={{width: '100%', background: `linear-gradient(90deg, rgb(34,197,94) ${parseFloat(s.yld) * 10}%, rgb(203,213,225) ${parseFloat(s.yld) * 10}%)`}}></div><div className="w-10 text-right">{s.yld}</div></div>
        ))}
      </div>
    ),
  },
  {
    id: 'dividend-coverage-ratio',
    name: 'Dividend Coverage Ratio',
    category: 'income',
    description: 'Coverage analysis',
    samplePreview: (
      <div className="grid grid-cols-2 gap-3 text-xs">
        <MetricCard label="Payout Ratio" value="35%" change="Healthy" isPositive={true} />
        <MetricCard label="Coverage Ratio" value="2.85x" change="Safe" isPositive={true} />
        <MetricCard label="FCF Coverage" value="1.45x" change="Sustainable" isPositive={true} />
        <MetricCard label="Trend" value="Rising" change="Positive" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'income-vs-expenses',
    name: 'Income vs Expenses',
    category: 'income',
    description: 'Income vs fees',
    samplePreview: (
      <div className="space-y-2 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-20">Dividend Inc</div>
          <div className="flex-1 bg-green-500 h-4 rounded" style={{width: '80%'}}></div>
          <div className="w-16">$4,825</div>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-20">Advisory Fees</div>
          <div className="flex-1 bg-red-500 h-4 rounded" style={{width: '5%'}}></div>
          <div className="w-16">-$300</div>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-20">Net Income</div>
          <div className="flex-1 bg-blue-500 h-4 rounded" style={{width: '75%'}}></div>
          <div className="w-16">$4,525</div>
        </div>
      </div>
    ),
  },
  {
    id: 'distribution-calendar',
    name: 'Distribution Calendar',
    category: 'income',
    description: 'Upcoming distributions',
    samplePreview: (
      <div className="text-xs space-y-1">
        <div className="font-semibold mb-2">Next 90 Days</div>
        {[{date: 'Mar 15', amt: '$402', stocks: '8 holdings'}, {date: 'Apr 10', amt: '$385', stocks: '6 holdings'}, {date: 'May 8', amt: '$428', stocks: '9 holdings'}].map(d => (
          <div key={d.date} className="flex justify-between"><span>{d.date}</span><span className="text-right"><span className="font-bold">{d.amt}</span> ({d.stocks})</span></div>
        ))}
      </div>
    ),
  },

  // SECTOR (9)
  {
    id: 'sector-performance-bar',
    name: 'Sector Performance',
    category: 'sector',
    description: 'Sector returns',
    samplePreview: (
      <div className="space-y-2 text-xs">
        {[{s: 'Technology', v: 18.5}, {s: 'Healthcare', v: 12.3}, {s: 'Finance', v: 9.8}, {s: 'Energy', v: 5.2}, {s: 'Consumer', v: 3.1}].map(x => (
          <div key={x.s} className="flex items-center gap-2"><div className="w-20">{x.s}</div><div className="flex-1 bg-slate-200 h-3 rounded" style={{background: `linear-gradient(90deg, rgb(34,197,94) ${x.v / 20 * 100}%, rgb(203,213,225) ${x.v / 20 * 100}%)`}}></div><div className="w-12 text-right text-green-600">+{x.v}%</div></div>
        ))}
      </div>
    ),
  },
  {
    id: 'sector-holdings-table',
    name: 'Sector Holdings',
    category: 'sector',
    description: 'Holdings by sector',
    samplePreview: (
      <div className="text-xs space-y-1">
        <div className="grid grid-cols-3 gap-2 font-semibold border-b pb-1">
          <div>Sector</div><div className="text-right">Holdings</div><div className="text-right">Value</div>
        </div>
        {[{s: 'Technology', h: '8', v: '$42.5K'}, {s: 'Healthcare', h: '5', v: '$28.3K'}, {s: 'Finance', h: '6', v: '$25.8K'}].map(h => (
          <div key={h.s} className="grid grid-cols-3 gap-2"><div>{h.s}</div><div className="text-right">{h.h}</div><div className="text-right">{h.v}</div></div>
        ))}
      </div>
    ),
  },
  {
    id: 'sector-volatility-comparison',
    name: 'Sector Volatility',
    category: 'sector',
    description: 'Volatility by sector',
    samplePreview: (
      <div className="space-y-1 text-xs">
        {[{s: 'Tech', vol: 22.1}, {s: 'Energy', vol: 28.5}, {s: 'Utils', vol: 12.3}, {s: 'Finance', vol: 18.5}, {s: 'Cons', vol: 14.2}].map(v => (
          <div key={v.s} className="flex items-center gap-2"><div className="w-12">{v.s}</div><div className="flex-1 bg-slate-200 h-3 rounded" style={{background: `linear-gradient(90deg, rgb(249,115,22) ${v.vol / 30 * 100}%, rgb(203,213,225) ${v.vol / 30 * 100}%)`}}></div><div className="w-12 text-right">{v.vol}%</div></div>
        ))}
      </div>
    ),
  },
  {
    id: 'sector-valuation-metrics',
    name: 'Sector Valuation',
    category: 'sector',
    description: 'Valuation by sector',
    samplePreview: (
      <div className="text-xs space-y-1">
        <div className="grid grid-cols-3 gap-2 font-semibold border-b pb-1">
          <div>Sector</div><div className="text-right">P/E</div><div className="text-right">P/B</div>
        </div>
        {[{s: 'Tech', pe: '28.5', pb: '5.2'}, {s: 'Financ', pe: '12.3', pb: '1.8'}, {s: 'Util', pe: '18.2', pb: '2.1'}].map(v => (
          <div key={v.s} className="grid grid-cols-3 gap-2"><div>{v.s}</div><div className="text-right">{v.pe}</div><div className="text-right">{v.pb}</div></div>
        ))}
      </div>
    ),
  },
  {
    id: 'sector-rotation-signals',
    name: 'Sector Rotation Signals',
    category: 'sector',
    description: 'Rotation analysis',
    samplePreview: (
      <div className="text-xs space-y-1">
        <div className="font-semibold mb-2">Current Rotation Signals</div>
        {[{signal: 'Growth → Value', confidence: 'High'}, {signal: 'Cyclical → Defensive', confidence: 'Medium'}, {signal: 'Continue Tech', confidence: 'High'}, {signal: 'Emerging Markets', confidence: 'Low'}].map(s => (
          <div key={s.signal} className="flex justify-between"><span>{s.signal}</span><span className={`font-bold ${s.confidence === 'High' ? 'text-green-600' : 'text-yellow-600'}`}>{s.confidence}</span></div>
        ))}
      </div>
    ),
  },
  {
    id: 'sector-correlation',
    name: 'Sector Correlation',
    category: 'sector',
    description: 'Correlation matrix',
    samplePreview: (
      <div className="text-xs grid gap-1">
        <div className="grid grid-cols-4 gap-1 font-semibold text-center">
          <div></div><div>Tech</div><div>Fin</div><div>Utils</div>
        </div>
        {[{s: 'Tech', v: ['1.00', '0.45', '-0.12']}, {s: 'Fin', v: ['0.45', '1.00', '0.08']}, {s: 'Utils', v: ['-0.12', '0.08', '1.00']}].map(r => (
          <div key={r.s} className="grid grid-cols-4 gap-1">
            <div className="font-semibold">{r.s}</div>
            {r.v.map((c, i) => <div key={i} className="text-center text-xs">{c}</div>)}
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'economic-cycle-positioning',
    name: 'Economic Cycle Positioning',
    category: 'sector',
    description: 'Cycle analysis',
    samplePreview: (
      <div className="text-xs space-y-2">
        <div className="font-semibold mb-2">Current Cycle Phase: Mid-Expansion</div>
        {[{phase: 'Growth (Now)', heavy: ['Tech', 'Finance']}, {phase: 'Late Cycle', heavy: ['Energy', 'Materials']}, {phase: 'Recession Risk', heavy: ['Utilities']}].map(c => (
          <div key={c.phase} className="flex gap-2">
            <div className="w-28">{c.phase}</div>
            <div className="text-xs">{c.heavy.join(', ')}</div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'sector-rebalancing-recommendation',
    name: 'Rebalancing Recommendation',
    category: 'sector',
    description: 'Rebalance advice',
    samplePreview: (
      <div className="text-xs space-y-2">
        <div className="font-semibold mb-2">Recommended Rebalancing</div>
        {[{sector: 'Technology', from: '35%', to: '30%', action: 'Trim'}, {sector: 'Energy', from: '5%', to: '10%', action: 'Add'}, {sector: 'Healthcare', from: '15%', to: '17%', action: 'Add'}].map(r => (
          <div key={r.sector} className="flex justify-between text-xs">
            <span>{r.sector}</span>
            <span className="text-gray-500">{r.from} → {r.to}</span>
            <span className={r.action === 'Trim' ? 'text-red-600' : 'text-green-600'}>{r.action}</span>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'sector-dividend-composition',
    name: 'Sector Dividend Composition',
    category: 'sector',
    description: 'Dividend breakdown',
    samplePreview: (
      <div className="space-y-1 text-xs">
        <div className="font-semibold mb-2">Dividend by Sector</div>
        {[{s: 'Utilities', div: '38%'}, {s: 'Finance', div: '28%'}, {s: 'Tech', div: '18%'}, {s: 'Consumer', div: '12%'}, {s: 'Other', div: '4%'}].map(x => (
          <div key={x.s} className="flex items-center gap-2"><div className="w-16">{x.s}</div><div className="flex-1 bg-slate-200 h-3 rounded" style={{background: `linear-gradient(90deg, rgb(34,197,94) ${parseFloat(x.div)}%, rgb(203,213,225) ${parseFloat(x.div)}%)`}}></div><div className="w-8 text-right">{x.div}</div></div>
        ))}
      </div>
    ),
  },

  // TECHNICAL (8)
  {
    id: 'rsi-overbought-oversold',
    name: 'RSI Overbought/Oversold',
    category: 'technical',
    description: 'RSI levels',
    samplePreview: (
      <svg width="100%" height="80" viewBox="0 0 300 80">
        <rect y="0" height="20" width="300" fill="rgb(239,68,68)" opacity="0.2"/>
        <line x1="0" y1="20" x2="300" y2="20" stroke="rgb(239,68,68)" strokeWidth="1"/>
        <rect y="20" height="40" width="300" fill="rgb(34,197,94)" opacity="0.2"/>
        <line x1="0" y1="60" x2="300" y2="60" stroke="rgb(59,130,246)" strokeWidth="1"/>
        <rect y="60" height="20" width="300" fill="rgb(239,68,68)" opacity="0.2"/>
        <polyline points="0,55 30,48 60,42 90,38 120,36 150,35 180,38 210,42 240,48 270,54 300,58" fill="none" stroke="rgb(59,130,246)" strokeWidth="2"/>
        <text x="10" y="75" fontSize="10" fill="currentColor">RSI: 45 (Neutral)</text>
      </svg>
    ),
  },
  {
    id: 'macd-crossover-signals',
    name: 'MACD Crossover Signals',
    category: 'technical',
    description: 'MACD signals',
    samplePreview: (
      <svg width="100%" height="80" viewBox="0 0 300 80">
        <line x1="0" y1="40" x2="300" y2="40" stroke="rgb(203,213,225)" strokeWidth="1"/>
        <polyline points="0,50 30,45 60,40 90,35 120,32 150,30 180,32 210,35 240,40 270,45 300,50" fill="none" stroke="rgb(59,130,246)" strokeWidth="2"/>
        <polyline points="0,48 30,46 60,42 90,37 120,33 150,31 180,33 210,37 240,42 270,46 300,48" fill="none" stroke="rgb(107,114,128)" strokeWidth="2" strokeDasharray="5,5"/>
        <text x="10" y="70" fontSize="10" fill="currentColor">Bullish - Below Signal</text>
      </svg>
    ),
  },
  {
    id: 'moving-average-crossover',
    name: 'Moving Average Crossover',
    category: 'technical',
    description: 'MA crossover',
    samplePreview: (
      <svg width="100%" height="80" viewBox="0 0 300 80">
        <polyline points="0,50 30,48 60,46 90,44 120,42 150,40 180,38 210,36 240,34 270,32 300,30" fill="none" stroke="rgb(59,130,246)" strokeWidth="2"/>
        <polyline points="0,55 30,54 60,52 90,50 120,48 150,46 180,44 210,42 240,40 270,38 300,36" fill="none" stroke="rgb(107,114,128)" strokeWidth="2" strokeDasharray="5,5"/>
        <circle cx="150" cy="43" r="4" fill="rgb(34,197,94)" opacity="0.5"/>
        <text x="10" y="70" fontSize="10" fill="currentColor">Golden Cross - Bullish</text>
      </svg>
    ),
  },
  {
    id: 'bollinger-band-squeeze',
    name: 'Bollinger Band Squeeze',
    category: 'technical',
    description: 'BB analysis',
    samplePreview: (
      <svg width="100%" height="80" viewBox="0 0 300 80">
        <polyline points="0,50 30,48 60,46 90,44 120,42 150,40 180,42 210,44 240,46 270,48 300,50" fill="none" stroke="rgb(59,130,246)" strokeWidth="2"/>
        <polyline points="0,45 30,42 60,39 90,36 120,33 150,30 180,33 210,36 240,39 270,42 300,45" fill="none" stroke="rgb(156,163,175)" strokeWidth="1" strokeDasharray="2,2"/>
        <polyline points="0,55 30,54 60,53 90,52 120,51 150,50 180,51 210,52 220,53 270,54 300,55" fill="none" stroke="rgb(156,163,175)" strokeWidth="1" strokeDasharray="2,2"/>
        <text x="10" y="70" fontSize="10" fill="currentColor">Squeeze active - Breakout coming</text>
      </svg>
    ),
  },
  {
    id: 'support-resistance-levels',
    name: 'Support/Resistance Levels',
    category: 'technical',
    description: 'Price levels',
    samplePreview: (
      <svg width="100%" height="80" viewBox="0 0 300 80">
        <polyline points="0,50 30,48 60,46 90,44 120,42 150,40 180,42 210,44 240,46 270,48 300,50" fill="none" stroke="rgb(59,130,246)" strokeWidth="2"/>
        <line x1="0" y1="30" x2="300" y2="30" stroke="rgb(239,68,68)" strokeWidth="1" strokeDasharray="5,5"/>
        <line x1="0" y1="60" x2="300" y2="60" stroke="rgb(34,197,94)" strokeWidth="1" strokeDasharray="5,5"/>
        <text x="10" y="25" fontSize="10" fill="rgb(239,68,68)">Resistance $195</text>
        <text x="10" y="75" fontSize="10" fill="rgb(34,197,94)">Support $180</text>
      </svg>
    ),
  },
  {
    id: 'volume-trend-technical',
    name: 'Volume Trend',
    category: 'technical',
    description: 'Volume analysis',
    samplePreview: (
      <svg width="100%" height="80" viewBox="0 0 300 80">
        <polyline points="0,40 30,35 60,30 90,28 120,25 150,24 180,26 210,30 240,35 270,40 300,45" fill="none" stroke="rgb(59,130,246)" strokeWidth="2"/>
        {Array.from({length: 10}).map((_, i) => (
          <rect key={i} x={i * 30} y={60 + Math.random() * 15} width="20" height={Math.random() * 15} fill="rgb(156,163,175)" opacity="0.5"/>
        ))}
        <text x="10" y="75" fontSize="10" fill="currentColor">Volume declining - Caution</text>
      </svg>
    ),
  },
  {
    id: 'pattern-recognition',
    name: 'Pattern Recognition',
    category: 'technical',
    description: 'Chart patterns',
    samplePreview: (
      <div className="text-xs space-y-1">
        <div className="font-semibold mb-2">Detected Patterns</div>
        {[{pattern: 'Cup & Handle', confidence: '85%', bias: 'Bullish'}, {pattern: 'Flag', confidence: '72%', bias: 'Continuation'}, {pattern: 'Double Top', confidence: '45%', bias: 'Bearish'}].map(p => (
          <div key={p.pattern} className="flex justify-between"><span>{p.pattern}</span><span className="text-right"><span className="font-bold">{p.confidence}</span> {p.bias}</span></div>
        ))}
      </div>
    ),
  },
  {
    id: 'trend-strength-indicator',
    name: 'Trend Strength Indicator',
    category: 'technical',
    description: 'Trend analysis',
    samplePreview: (
      <div className="grid grid-cols-2 gap-3 text-xs">
        <MetricCard label="Trend" value="Strong Up" change="ADX 45" isPositive={true} />
        <MetricCard label="Direction" value="Bullish" change="All MA Up" isPositive={true} />
        <MetricCard label="Momentum" value="Positive" change="+15% 3M" isPositive={true} />
        <MetricCard label="Confidence" value="High" change="85%" isPositive={true} />
      </div>
    ),
  },

  // FUNDAMENTAL (8)
  {
    id: 'earnings-per-share',
    name: 'Earnings Per Share',
    category: 'fundamental',
    description: 'EPS analysis',
    samplePreview: (
      <div className="text-xs space-y-2">
        <div className="grid grid-cols-2 gap-2">
          <MetricCard label="Trailing EPS" value="$6.18" change="+12.3%" isPositive={true} />
          <MetricCard label="Forward EPS" value="$6.85" change="Est 2024" isPositive={true} />
          <MetricCard label="EPS Growth" value="14.2%" change="1Y" isPositive={true} />
          <MetricCard label="Beat Rate" value="80%" change="4/5 QTR" isPositive={true} />
        </div>
      </div>
    ),
  },
  {
    id: 'price-to-earnings-ratio',
    name: 'Price to Earnings Ratio',
    category: 'fundamental',
    description: 'P/E ratio',
    samplePreview: (
      <div className="grid grid-cols-2 gap-3 text-xs">
        <MetricCard label="Trailing P/E" value="28.5" change="vs 26.1" isPositive={false} />
        <MetricCard label="Forward P/E" value="25.2" change="vs 26.1" isPositive={true} />
        <MetricCard label="Sector Avg" value="27.1" change="Higher" isPositive={false} />
        <MetricCard label="Fair Value" value="$220" change="Current $190" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'debt-to-equity-ratio',
    name: 'Debt to Equity Ratio',
    category: 'fundamental',
    description: 'Leverage analysis',
    samplePreview: (
      <div className="grid grid-cols-2 gap-3 text-xs">
        <MetricCard label="Debt/Equity" value="0.45" change="Conservative" isPositive={true} />
        <MetricCard label="Current Ratio" value="2.15" change="Healthy" isPositive={true} />
        <MetricCard label="Interest Cover" value="12.5x" change="Safe" isPositive={true} />
        <MetricCard label="Net Debt" value="$15B" change="Manageable" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'free-cash-flow-trend',
    name: 'Free Cash Flow Trend',
    category: 'fundamental',
    description: 'FCF analysis',
    samplePreview: (
      <svg width="100%" height="80" viewBox="0 0 300 80">
        <polyline points="0,60 30,55 60,50 90,45 120,40 150,35 180,38 210,42 240,48 270,55 300,60" fill="none" stroke="rgb(34,197,94)" strokeWidth="2"/>
        <text x="10" y="20" fontSize="12" fill="currentColor" fontWeight="bold">FCF: $85.2B</text>
        <text x="10" y="35" fontSize="11" fill="currentColor">3Y Trend: +12.5% CAGR</text>
      </svg>
    ),
  },
  {
    id: 'roe-profit-margin',
    name: 'ROE & Profit Margin',
    category: 'fundamental',
    description: 'Profitability metrics',
    samplePreview: (
      <div className="grid grid-cols-2 gap-3 text-xs">
        <MetricCard label="ROE" value="22.5%" change="Strong" isPositive={true} />
        <MetricCard label="ROIC" value="18.2%" change="Good" isPositive={true} />
        <MetricCard label="Gross Margin" value="44.2%" change="+1.2%" isPositive={true} />
        <MetricCard label="Net Margin" value="24.8%" change="Stable" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'dividend-payout-ratio',
    name: 'Dividend Payout Ratio',
    category: 'fundamental',
    description: 'Payout analysis',
    samplePreview: (
      <div className="space-y-2 text-xs">
        <div className="flex items-center gap-2">
          <div className="w-24">Payout Ratio</div>
          <div className="flex-1 bg-slate-200 h-4 rounded" style={{background: `linear-gradient(90deg, rgb(59,130,246) 35%, rgb(203,213,225) 35%)`}}></div>
          <div className="w-12 text-right">35%</div>
        </div>
        <div className="text-xs text-gray-600 dark:text-gray-300">Healthy range 25-40%. Room to grow.</div>
      </div>
    ),
  },
  {
    id: 'asset-quality-score',
    name: 'Asset Quality Score',
    category: 'fundamental',
    description: 'Balance sheet quality',
    samplePreview: (
      <div className="grid grid-cols-2 gap-3 text-xs">
        <MetricCard label="Asset Quality" value="8.2/10" change="Good" isPositive={true} />
        <MetricCard label="Current Assets" value="$120B" change="+5.2%" isPositive={true} />
        <MetricCard label="Intangibles" value="18%" change="Reasonable" isPositive={true} />
        <MetricCard label="Receivables" value="Good" change="60 day avg" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'revenue-growth-analysis',
    name: 'Revenue Growth Analysis',
    category: 'fundamental',
    description: 'Growth trends',
    samplePreview: (
      <div className="space-y-2 text-xs">
        {[{period: '1Y Growth', val: '12.3%'}, {period: '3Y CAGR', val: '14.1%'}, {period: '5Y CAGR', val: '13.8%'}, {period: 'Next Year Est', val: '11.5%'}].map(g => (
          <div key={g.period} className="flex justify-between"><span>{g.period}</span><span className="font-bold text-green-600">{g.val}</span></div>
        ))}
      </div>
    ),
  },

  // TAX (8)
  {
    id: 'tax-loss-harvesting-opportunities',
    name: 'Tax Loss Harvesting',
    category: 'tax',
    description: 'Harvesting opportunities',
    samplePreview: (
      <div className="text-xs space-y-2">
        <div className="font-semibold">Current Opportunities</div>
        {[{holding: 'ABD', loss: '-$2,500'}, {holding: 'GE', loss: '-$1,800'}, {holding: 'F', loss: '-$1,250'}].map(o => (
          <div key={o.holding} className="flex justify-between"><span>{o.holding}</span><span className="font-bold text-red-600">{o.loss}</span></div>
        ))}
        <div className="text-xs text-green-600 mt-2">Total harvestable: -$5,550</div>
      </div>
    ),
  },
  {
    id: 'capital-gains-summary',
    name: 'Capital Gains Summary',
    category: 'tax',
    description: 'Gains/losses breakdown',
    samplePreview: (
      <div className="grid grid-cols-2 gap-3 text-xs">
        <MetricCard label="Long-term Gains" value="$12,500" change="Favorable" isPositive={true} />
        <MetricCard label="Short-term Gains" value="$3,200" change="Taxable" isPositive={false} />
        <MetricCard label="Losses" value="-$5,550" change="Offset" isPositive={true} />
        <MetricCard label="Net Gain" value="$10,150" change="Tax-efficient" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'tax-liability-projection',
    name: 'Tax Liability Projection',
    category: 'tax',
    description: 'Projected tax bill',
    samplePreview: (
      <div className="text-xs space-y-2">
        <div className="font-semibold">Estimated 2024 Tax Bill</div>
        <div className="grid grid-cols-2 gap-2">
          <div>Dividends: $4,825</div>
          <div className="text-right">$675</div>
        </div>
        <div className="grid grid-cols-2 gap-2">
          <div>Cap Gains: $10,150</div>
          <div className="text-right">$1,522</div>
        </div>
        <div className="border-t pt-2 grid grid-cols-2 gap-2 font-semibold">
          <div>Total Tax Due</div>
          <div className="text-right text-red-600">$2,197</div>
        </div>
      </div>
    ),
  },
  {
    id: 'tax-average-vs-cost',
    name: 'Tax Average vs Cost',
    category: 'tax',
    description: 'Cost basis analysis',
    samplePreview: (
      <div className="text-xs space-y-2">
        {[{holding: 'AAPL', cost: '$142.50', current: '$189.95', gain: '+33.2%'}, {holding: 'MSFT', cost: '$310.00', current: '$424.55', gain: '+36.9%'}, {holding: 'GOOGL', cost: '$98.50', current: '$152.30', gain: '+54.6%'}].map(t => (
          <div key={t.holding} className="text-xs">
            <div className="flex justify-between"><span className="font-bold">{t.holding}</span><span className="text-green-600">{t.gain}</span></div>
            <div className="text-gray-500">Cost {t.cost} → {t.current}</div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'tax-efficiency-ratio',
    name: 'Tax Efficiency Ratio',
    category: 'tax',
    description: 'Efficiency metrics',
    samplePreview: (
      <div className="grid grid-cols-2 gap-3 text-xs">
        <MetricCard label="Tax Efficiency" value="78%" change="Good" isPositive={true} />
        <MetricCard label="After-Tax Return" value="9.2%" change="vs 12.3%" isPositive={true} />
        <MetricCard label="Tax Impact" value="-25.3%" change="Of returns" isPositive={false} />
        <MetricCard label="Improvement" value="Possible" change="+3-5%" isPositive={true} />
      </div>
    ),
  },
  {
    id: 'state-local-tax-exposure',
    name: 'State/Local Tax Exposure',
    category: 'tax',
    description: 'State tax analysis',
    samplePreview: (
      <div className="text-xs space-y-2">
        <div className="font-semibold">Current State: California</div>
        {[{tax: 'State Income', rate: '9.3%'}, {tax: 'Local', rate: '1.25%'}, {tax: 'Combined', rate: '10.55%'}, {tax: 'Effective', rate: '~$1,850'}].map(t => (
          <div key={t.tax} className="flex justify-between"><span>{t.tax}</span><span className="font-bold">{t.rate}</span></div>
        ))}
      </div>
    ),
  },
  {
    id: 'harvesting-calendar',
    name: 'Harvesting Calendar',
    category: 'tax',
    description: 'Calendar view',
    samplePreview: (
      <div className="text-xs space-y-1">
        <div className="font-semibold mb-2">Q1 2024 Harvesting Plan</div>
        {[{month: 'January', target: '-$2,500', holdings: 'ABD, GE'}, {month: 'February', target: '-$1,800', holdings: 'F, GM'}, {month: 'March', target: '-$1,250', holdings: 'T, VZ'}].map(h => (
          <div key={h.month} className="flex justify-between text-xs">
            <span className="font-semibold">{h.month}</span>
            <span className="text-right"><span className="font-bold text-red-600">{h.target}</span> ({h.holdings})</span>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'tax-risk-assessment',
    name: 'Tax Risk Assessment',
    category: 'tax',
    description: 'Risk analysis',
    samplePreview: (
      <div className="grid grid-cols-2 gap-3 text-xs">
        <MetricCard label="Audit Risk" value="Low" change="Normal" isPositive={true} />
        <MetricCard label="IRS Flags" value="None" change="Clean" isPositive={true} />
        <MetricCard label="Documentation" value="Excellent" change="Complete" isPositive={true} />
        <MetricCard label="Compliance" value="100%" change="Compliant" isPositive={true} />
      </div>
    ),
  },

  // MONITORING (10)
  {
    id: 'price-alerts-summary',
    name: 'Price Alerts Summary',
    category: 'monitoring',
    description: 'Active alerts',
    samplePreview: (
      <div className="text-xs space-y-1">
        <div className="font-semibold mb-2">Active Price Alerts</div>
        {[{stock: 'AAPL', trigger: '$195'}, {stock: 'MSFT', trigger: '$450'}, {stock: 'GOOGL', trigger: '$160'}, {stock: 'TSLA', trigger: '$250'}].map(a => (
          <div key={a.stock} className="flex justify-between"><span>{a.stock}</span><span className="font-bold">{a.trigger}</span></div>
        ))}
      </div>
    ),
  },
  {
    id: 'earnings-calendar',
    name: 'Earnings Calendar',
    category: 'monitoring',
    description: 'Upcoming earnings',
    samplePreview: (
      <div className="text-xs space-y-1">
        <div className="font-semibold mb-2">Next 30 Days</div>
        {[{date: 'Mar 28', companies: 'MSFT, GE'}, {date: 'Apr 4', companies: 'AAPL, AMD'}, {date: 'Apr 18', companies: 'GOOGL, AMZN'}].map(e => (
          <div key={e.date} className="flex justify-between"><span className="font-bold">{e.date}</span><span className="text-xs">{e.companies}</span></div>
        ))}
      </div>
    ),
  },
  {
    id: 'news-headlines-widget',
    name: 'News Headlines',
    category: 'monitoring',
    description: 'Latest news',
    samplePreview: (
      <div className="text-xs space-y-2">
        {[{headline: 'Fed holds rates steady', time: '2h ago'}, {headline: 'Tech stocks rally on AI hopes', time: '4h ago'}, {headline: 'Oil prices down 2.5%', time: '6h ago'}].map(n => (
          <div key={n.headline} className="border-b pb-1 last:border-b-0">
            <div className="font-semibold line-clamp-2">{n.headline}</div>
            <div className="text-gray-500">{n.time}</div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'ratings-consensus',
    name: 'Ratings Consensus',
    category: 'monitoring',
    description: 'Analyst ratings',
    samplePreview: (
      <div className="text-xs space-y-2">
        <div className="flex items-center gap-2">
          <div className="w-16">Buy</div>
          <div className="flex-1 bg-green-500 h-4 rounded" style={{width: '70%'}}></div>
          <div className="w-8 text-right">28</div>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-16">Hold</div>
          <div className="flex-1 bg-yellow-500 h-4 rounded" style={{width: '20%'}}></div>
          <div className="w-8 text-right">8</div>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-16">Sell</div>
          <div className="flex-1 bg-red-500 h-4 rounded" style={{width: '5%'}}></div>
          <div className="w-8 text-right">2</div>
        </div>
      </div>
    ),
  },
  {
    id: 'market-movers-list',
    name: 'Market Movers',
    category: 'monitoring',
    description: 'Top movers',
    samplePreview: (
      <div className="grid grid-cols-2 gap-4 text-xs">
        <div><div className="font-semibold text-green-600 mb-2">Top Gainers</div><div className="space-y-1"><div>NVDA +6.2%</div><div>TSLA +4.8%</div><div>AMD +3.9%</div></div></div>
        <div><div className="font-semibold text-red-600 mb-2">Top Losers</div><div className="space-y-1"><div>GE -4.2%</div><div>F -3.8%</div><div>BAC -2.5%</div></div></div>
      </div>
    ),
  },
  {
    id: 'economic-calendar',
    name: 'Economic Calendar',
    category: 'monitoring',
    description: 'Macro events',
    samplePreview: (
      <div className="text-xs space-y-2">
        <div className="font-semibold mb-2">This Week</div>
        {[{date: 'Today', event: 'Fed Chair Testimony'}, {date: 'Wed', event: 'Unemployment Report'}, {date: 'Fri', event: 'Jobs Report'}].map(e => (
          <div key={e.date} className="flex justify-between"><span className="font-bold">{e.date}</span><span>{e.event}</span></div>
        ))}
      </div>
    ),
  },
  {
    id: 'portfolio-health-score',
    name: 'Portfolio Health Score',
    category: 'monitoring',
    description: 'Health assessment',
    samplePreview: (
      <div className="space-y-2 text-xs">
        <div className="flex items-center gap-2">
          <div className="text-lg font-bold text-green-600">8.2/10</div>
          <div className="flex-1">
            <div className="bg-slate-200 h-4 rounded overflow-hidden">
              <div className="bg-green-500 h-full" style={{width: '82%'}}></div>
            </div>
          </div>
        </div>
        <div className="text-green-600 font-semibold">Excellent Health</div>
        <div className="text-gray-600">Well-diversified, healthy risk profile</div>
      </div>
    ),
  },
  {
    id: 'compliance-monitoring',
    name: 'Compliance Monitoring',
    category: 'monitoring',
    description: 'Compliance status',
    samplePreview: (
      <div className="text-xs space-y-2">
        {[{check: 'Wash Sales', status: 'Clear', icon: '✓'}, {check: 'Pattern Day Trading', status: 'OK', icon: '✓'}, {check: 'Margin Calls', status: 'None', icon: '✓'}, {check: 'Tax Docs', status: 'Ready', icon: '✓'}].map(c => (
          <div key={c.check} className="flex items-center gap-2">
            <span className="text-green-600">{c.icon}</span>
            <span className="flex-1">{c.check}</span>
            <span className="text-gray-600">{c.status}</span>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'regulatory-updates',
    name: 'Regulatory Updates',
    category: 'monitoring',
    description: 'Regulatory news',
    samplePreview: (
      <div className="text-xs space-y-2">
        <div className="font-semibold mb-2">Recent Updates</div>
        {[{title: 'SEC Rule 10b5-1 Updates', date: 'This Month'}, {title: 'Tax Loss Harvesting Rules', date: 'Recently'}, {title: 'Wash Sale Clarification', date: 'Q1 2024'}].map(r => (
          <div key={r.title} className="border-b pb-1 last:border-b-0">
            <div className="font-semibold">{r.title}</div>
            <div className="text-gray-500">{r.date}</div>
          </div>
        ))}
      </div>
    ),
  },
  {
    id: 'security-analysis',
    name: 'Security Analysis',
    category: 'monitoring',
    description: 'Security overview',
    samplePreview: (
      <div className="grid grid-cols-2 gap-3 text-xs">
        <MetricCard label="Account Security" value="Strong" change="2FA Active" isPositive={true} />
        <MetricCard label="Login History" value="Normal" change="No Issues" isPositive={true} />
        <MetricCard label="Fraud Risk" value="Low" change="Monitored" isPositive={true} />
        <MetricCard label="Data Backup" value="Current" change="Auto Sync" isPositive={true} />
      </div>
    ),
  },
];

const CATEGORIES = ['All', 'portfolio', 'stock_research', 'etf_analysis', 'risk_management', 'performance', 'income', 'sector', 'technical', 'fundamental', 'tax', 'monitoring'];

export const FinBlockGalleryPage: React.FC = () => {
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedBlock, setSelectedBlock] = useState<FinBlockItem | null>(FINBLOCKS[0]);

  const filtered = useMemo(() => {
    return FINBLOCKS.filter((block) => {
      const matchCategory = selectedCategory === 'All' || block.category === selectedCategory;
      const matchSearch = block.name.toLowerCase().includes(searchQuery.toLowerCase()) || block.description.toLowerCase().includes(searchQuery.toLowerCase());
      return matchCategory && matchSearch;
    });
  }, [selectedCategory, searchQuery]);

  const categories = CATEGORIES.map((cat) => {
    const count = FINBLOCKS.filter((b) => cat === 'All' || b.category === cat).length;
    return { name: cat, count };
  });

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      {/* Header */}
      <div className="sticky top-0 z-40 bg-white dark:bg-slate-800 border-b border-slate-200 dark:border-slate-700 shadow-sm">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-4">finBlock Gallery</h1>
          <p className="text-gray-600 dark:text-gray-300 mb-4">Complete showcase of all 110 financial UI components with live previews</p>

          {/* Search */}
          <div className="mb-4">
            <input
              type="text"
              placeholder="Search finBlocks..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full px-4 py-2 bg-slate-50 dark:bg-slate-700 border border-slate-200 dark:border-slate-600 rounded-lg text-gray-900 dark:text-white placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          {/* Category Tabs */}
          <div className="flex flex-wrap gap-2 overflow-x-auto pb-2">
            {categories.map((cat) => (
              <button
                key={cat.name}
                onClick={() => setSelectedCategory(cat.name)}
                className={`px-4 py-2 rounded-full whitespace-nowrap font-medium transition ${
                  selectedCategory === cat.name
                    ? 'bg-blue-500 text-white'
                    : 'bg-slate-200 dark:bg-slate-700 text-gray-700 dark:text-gray-300 hover:bg-slate-300 dark:hover:bg-slate-600'
                }`}
              >
                {cat.name === 'All' ? 'All' : cat.name.replace(/_/g, ' ')} ({cat.count})
              </button>
            ))}
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar - List */}
          <div className="lg:col-span-1">
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow p-4 max-h-[600px] overflow-y-auto sticky top-24">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                Components ({filtered.length})
              </h2>
              <div className="space-y-2">
                {filtered.map((block) => (
                  <button
                    key={block.id}
                    onClick={() => setSelectedBlock(block)}
                    className={`w-full text-left px-3 py-2 rounded transition text-sm ${
                      selectedBlock?.id === block.id
                        ? 'bg-blue-100 dark:bg-blue-900 text-blue-900 dark:text-blue-100 font-medium'
                        : 'text-gray-700 dark:text-gray-300 hover:bg-slate-100 dark:hover:bg-slate-700'
                    }`}
                  >
                    <div className="font-medium">{block.name}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">{block.category}</div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Main - Preview */}
          <div className="lg:col-span-3">
            {selectedBlock ? (
              <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-8">
                {/* Header */}
                <div className="mb-6 border-b border-slate-200 dark:border-slate-700 pb-6">
                  <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{selectedBlock.name}</h2>
                  <p className="text-gray-600 dark:text-gray-300 mb-4">{selectedBlock.description}</p>
                  <div className="flex flex-wrap gap-2">
                    <span className="px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-100 rounded-full text-sm font-medium">
                      {selectedBlock.category.replace(/_/g, ' ')}
                    </span>
                    <span className="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 rounded-full text-sm font-mono">
                      {selectedBlock.id}
                    </span>
                  </div>
                </div>

                {/* Preview */}
                <div className="bg-slate-50 dark:bg-slate-900 rounded-lg p-6 border border-slate-200 dark:border-slate-700">
                  {selectedBlock.samplePreview}
                </div>

                {/* Info */}
                <div className="mt-6 text-sm text-gray-600 dark:text-gray-400">
                  <p>
                    📍 Location: <code className="text-xs bg-slate-100 dark:bg-slate-700 px-2 py-1 rounded">finBlocks/components/{selectedBlock.category}/{selectedBlock.id}.tsx</code>
                  </p>
                </div>
              </div>
            ) : (
              <div className="bg-white dark:bg-slate-800 rounded-lg shadow-lg p-8 text-center">
                <p className="text-gray-600 dark:text-gray-300">Select a component to preview</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default FinBlockGalleryPage;
