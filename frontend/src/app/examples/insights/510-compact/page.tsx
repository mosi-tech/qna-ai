'use client';

export default function DefensiveLeadershipAnalysisCompact() {
  const holdingsData = [
    { symbol: 'PG', name: 'Procter & Gamble', outperform: 5, total: 5, avgReturn: 1.5, correlation: 0.68, sector: 'Staples', beta: 0.45 },
    { symbol: 'JNJ', name: 'Johnson & Johnson', outperform: 4, total: 5, avgReturn: 1.8, correlation: 0.72, sector: 'Healthcare', beta: 0.52 },
    { symbol: 'KO', name: 'Coca-Cola', outperform: 4, total: 5, avgReturn: 1.3, correlation: 0.65, sector: 'Staples', beta: 0.48 },
    { symbol: 'WMT', name: 'Walmart', outperform: 3, total: 5, avgReturn: 1.1, correlation: 0.58, sector: 'Staples', beta: 0.41 },
    { symbol: 'VZ', name: 'Verizon', outperform: 3, total: 5, avgReturn: 0.9, correlation: 0.71, sector: 'Telecom', beta: 0.63 },
    { symbol: 'T', name: 'AT&T', outperform: 2, total: 5, avgReturn: 0.7, correlation: 0.69, sector: 'Telecom', beta: 0.67 }
  ];

  const defensiveDays = [
    { date: '11/15', xlu: 2.8, xlp: 1.9, portfolio: 1.4, spyReturn: -0.3 },
    { date: '11/08', xlu: 1.6, xlp: 2.4, portfolio: 1.2, spyReturn: 0.1 },
    { date: '11/01', xlu: 3.1, xlp: 1.7, portfolio: 1.8, spyReturn: -0.2 },
    { date: '10/25', xlu: 2.2, xlp: 2.8, portfolio: 1.3, spyReturn: 0.4 },
    { date: '10/18', xlu: 1.9, xlp: 3.2, portfolio: 1.1, spyReturn: -0.1 }
  ];

  const getSuccessRate = (outperform: number, total: number) => ((outperform / total) * 100).toFixed(0);
  const getPerformanceColor = (rate: number) => {
    if (rate >= 80) return 'text-green-600 bg-green-50';
    if (rate >= 60) return 'text-amber-600 bg-amber-50';
    return 'text-red-600 bg-red-50';
  };

  return (
    <div className="h-screen bg-gray-50 p-6 overflow-hidden">
      <div className="max-w-7xl mx-auto h-full flex flex-col">
        
        {/* Header */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-900 mb-2">
            Holdings Performance During Defensive Leadership
          </h1>
          <div className="flex items-center gap-6 text-sm text-gray-600">
            <span>5 defensive days analyzed (Oct-Nov 2024)</span>
            <span>•</span>
            <span>Defensive = XLU & XLP both outperforming SPY</span>
            <span>•</span>
            <span>Portfolio avg: +1.36% on defensive days</span>
          </div>
        </div>

        <div className="flex-1 grid grid-cols-3 gap-6 min-h-0">
          
          {/* Rankings & Performance */}
          <div className="space-y-4">
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-900 mb-4">Outperformance Rankings</h3>
              <div className="space-y-3">
                {holdingsData
                  .sort((a, b) => (b.outperform / b.total) - (a.outperform / a.total))
                  .map((stock, idx) => {
                    const rate = (stock.outperform / stock.total) * 100;
                    return (
                      <div key={stock.symbol} className="flex items-center justify-between">
                        <div className="flex items-center gap-3">
                          <div className="w-6 h-6 bg-gray-100 rounded flex items-center justify-center text-xs font-semibold">
                            {idx + 1}
                          </div>
                          <div>
                            <div className="font-medium text-gray-900">{stock.symbol}</div>
                            <div className="text-xs text-gray-500">{stock.sector}</div>
                          </div>
                        </div>
                        <div className="text-right">
                          <div className={`px-2 py-1 rounded text-xs font-semibold ${getPerformanceColor(rate)}`}>
                            {stock.outperform}/{stock.total} days
                          </div>
                          <div className="text-xs text-gray-500 mt-1">+{stock.avgReturn}% avg</div>
                        </div>
                      </div>
                    );
                  })
                }
              </div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-900 mb-4">Key Insights</h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
                  <div>
                    <span className="font-medium">Consumer Staples dominate:</span> PG, KO, WMT show strongest defensive correlation
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
                  <div>
                    <span className="font-medium">Healthcare resilient:</span> JNJ delivers highest returns (+1.8% avg) with 80% success
                  </div>
                </div>
                <div className="flex items-start gap-2">
                  <div className="w-2 h-2 bg-amber-500 rounded-full mt-2"></div>
                  <div>
                    <span className="font-medium">Telecom mixed:</span> High defensive correlation but lower outperformance rates
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Detailed Performance Table */}
          <div className="bg-white rounded-lg border border-gray-200 p-4">
            <h3 className="font-semibold text-gray-900 mb-4">Performance Breakdown</h3>
            <div className="overflow-hidden">
              <table className="w-full text-xs">
                <thead>
                  <tr className="border-b border-gray-100">
                    <th className="text-left py-2 font-semibold text-gray-700">Stock</th>
                    <th className="text-center py-2 font-semibold text-gray-700">Success</th>
                    <th className="text-center py-2 font-semibold text-gray-700">Avg Return</th>
                    <th className="text-center py-2 font-semibold text-gray-700">Def Corr</th>
                    <th className="text-center py-2 font-semibold text-gray-700">Beta</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-50">
                  {holdingsData.map(stock => {
                    const rate = (stock.outperform / stock.total) * 100;
                    return (
                      <tr key={stock.symbol} className="hover:bg-gray-25">
                        <td className="py-3">
                          <div>
                            <div className="font-semibold text-gray-900">{stock.symbol}</div>
                            <div className="text-gray-500">{stock.name}</div>
                          </div>
                        </td>
                        <td className="text-center py-3">
                          <span className={`px-2 py-1 rounded text-xs font-semibold ${getPerformanceColor(rate)}`}>
                            {rate}%
                          </span>
                        </td>
                        <td className="text-center py-3 font-semibold text-gray-900">
                          +{stock.avgReturn}%
                        </td>
                        <td className="text-center py-3 text-gray-700">
                          {stock.correlation}
                        </td>
                        <td className="text-center py-3 text-gray-700">
                          {stock.beta}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            {/* Historical Performance */}
            <div className="mt-6 pt-4 border-t border-gray-100">
              <h4 className="font-semibold text-gray-900 mb-3">Daily Returns on Defensive Days</h4>
              <div className="space-y-2">
                {defensiveDays.map(day => (
                  <div key={day.date} className="flex items-center justify-between text-xs bg-gray-50 px-3 py-2 rounded">
                    <span className="font-medium text-gray-700">{day.date}</span>
                    <div className="flex gap-4">
                      <span className="text-blue-600">XLU: +{day.xlu}%</span>
                      <span className="text-green-600">XLP: +{day.xlp}%</span>
                      <span className="font-semibold text-gray-900">Portfolio: +{day.portfolio}%</span>
                      <span className="text-gray-500">SPY: {day.spyReturn > 0 ? '+' : ''}{day.spyReturn}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          {/* Sector Analysis & Recommendations */}
          <div className="space-y-4">
            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-900 mb-4">Sector Performance</h3>
              <div className="space-y-4">
                <div className="border-l-4 border-green-400 pl-3">
                  <div className="font-medium text-green-700">Consumer Staples</div>
                  <div className="text-sm text-gray-600 mt-1">3/3 stocks outperform 67%+ of time</div>
                  <div className="text-xs text-green-600 mt-1">PG (100%), KO (80%), WMT (60%)</div>
                </div>
                
                <div className="border-l-4 border-blue-400 pl-3">
                  <div className="font-medium text-blue-700">Healthcare</div>
                  <div className="text-sm text-gray-600 mt-1">Strong returns with defensive qualities</div>
                  <div className="text-xs text-blue-600 mt-1">JNJ (80%, +1.8% avg return)</div>
                </div>
                
                <div className="border-l-4 border-amber-400 pl-3">
                  <div className="font-medium text-amber-700">Telecom</div>
                  <div className="text-sm text-gray-600 mt-1">High correlation, mixed performance</div>
                  <div className="text-xs text-amber-600 mt-1">VZ (60%), T (40%)</div>
                </div>
              </div>
            </div>

            <div className="bg-white rounded-lg border border-gray-200 p-4">
              <h3 className="font-semibold text-gray-900 mb-4">Action Items</h3>
              <div className="space-y-3 text-sm">
                <div className="bg-green-50 border border-green-200 rounded p-3">
                  <div className="font-medium text-green-800">Increase Allocation</div>
                  <div className="text-green-700 mt-1">Consider boosting PG position - 100% success rate with consistent +1.5% returns</div>
                </div>
                
                <div className="bg-blue-50 border border-blue-200 rounded p-3">
                  <div className="font-medium text-blue-800">Maintain Position</div>
                  <div className="text-blue-700 mt-1">JNJ & KO provide reliable defensive performance</div>
                </div>
                
                <div className="bg-amber-50 border border-amber-200 rounded p-3">
                  <div className="font-medium text-amber-800">Review Strategy</div>
                  <div className="text-amber-700 mt-1">Monitor T performance - lowest success rate despite high defensive correlation</div>
                </div>
              </div>
            </div>

            <div className="bg-gray-100 rounded-lg p-3">
              <div className="text-xs text-gray-600">
                <strong>Methodology:</strong> Analysis covers 5 days when both XLU and XLP outperformed SPY by 1%+. 
                Outperformance = holding return &gt; portfolio average on that day.
              </div>
            </div>
          </div>

        </div>
      </div>
    </div>
  );
}