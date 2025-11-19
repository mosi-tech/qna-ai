'use client';

import React from 'react';

interface EarningsReportData {
  headline: string;
  keyResults: Array<{
    metric: string;
    actual: number;
    estimate: number;
    surprise: string;
  }>;
  commentary: string[];
  analystReaction: {
    upgrades: number;
    downgrades: number;
    priceTargetChange: number;
  };
  takeaways: Array<{
    insight: string;
    importance: 'high' | 'medium' | 'low';
  }>;
}

interface EarningsReportFormatProps {
  data: EarningsReportData;
  title?: string;
  ticker?: string;
}

export function EarningsReportFormat({
  data,
  title = "Earnings Analysis",
  ticker = "STOCK"
}: EarningsReportFormatProps) {
  const { headline, keyResults, commentary, analystReaction, takeaways } = data;

  const getSurpriseColor = (surprise: string) => {
    if (surprise.toLowerCase().includes('beat')) return 'text-green-600 bg-green-100';
    if (surprise.toLowerCase().includes('miss')) return 'text-red-600 bg-red-100';
    return 'text-gray-600 bg-gray-100';
  };

  const getImportanceColor = (importance: string) => {
    switch (importance) {
      case 'high': return 'border-l-red-400 bg-red-50';
      case 'medium': return 'border-l-yellow-400 bg-yellow-50';
      case 'low': return 'border-l-blue-400 bg-blue-50';
      default: return 'border-l-gray-400 bg-gray-50';
    }
  };

  const getReactionIcon = (change: number) => {
    if (change > 0) return '📈';
    if (change < 0) return '📉';
    return '➡️';
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100 bg-gradient-to-r from-green-50 to-green-100">
        <div className="flex items-center gap-3 mb-2">
          <span className="text-2xl">📊</span>
          <h2 className="text-2xl font-bold text-green-900">{title}</h2>
        </div>
        <p className="text-sm text-green-600">Financial results and analyst insights</p>
      </div>

      <div className="p-6">
        {/* Earnings Header */}
        <div className="mb-8">
          <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-xl p-6 border-2 border-blue-200">
            <div className="flex items-center gap-2 mb-4">
              <span className="bg-blue-200 text-blue-800 px-3 py-1 rounded-full text-sm font-bold">{ticker}</span>
              <span className="text-blue-600">EARNINGS RELEASE</span>
            </div>
            <h3 className="text-xl font-bold text-blue-900 mb-2">{headline}</h3>
            <div className="text-sm text-blue-600">
              Released: {new Date().toLocaleDateString()} • Market Hours: After Close
            </div>
          </div>
        </div>

        {/* Key Financial Metrics */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Key Results vs Estimates</h3>
          <div className="overflow-hidden rounded-lg border border-gray-200">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Metric</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actual</th>
                  <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Estimate</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Surprise</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {keyResults.map((result, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-4 py-3 font-medium text-gray-900">{result.metric}</td>
                    <td className="px-4 py-3 text-right font-semibold text-gray-900">
                      {result.metric.toLowerCase().includes('eps') ? `$${result.actual.toFixed(2)}` : result.actual.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-right text-gray-600">
                      {result.metric.toLowerCase().includes('eps') ? `$${result.estimate.toFixed(2)}` : result.estimate.toLocaleString()}
                    </td>
                    <td className="px-4 py-3 text-center">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getSurpriseColor(result.surprise)}`}>
                        {result.surprise}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Management Commentary */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Management Commentary & Guidance</h3>
          <div className="space-y-4">
            {commentary.map((comment, index) => (
              <div key={index} className="bg-yellow-50 rounded-lg p-4 border-l-4 border-yellow-400">
                <div className="flex items-start gap-3">
                  <span className="text-lg">💬</span>
                  <p className="text-yellow-900 italic">"{comment}"</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Analyst Reaction */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Analyst Reaction</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="bg-green-50 rounded-lg p-4 border border-green-200">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-green-900">Upgrades</h4>
                <span className="text-2xl">⬆️</span>
              </div>
              <div className="text-2xl font-bold text-green-800">{analystReaction.upgrades}</div>
              <div className="text-sm text-green-600">Rating improvements</div>
            </div>

            <div className="bg-red-50 rounded-lg p-4 border border-red-200">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-red-900">Downgrades</h4>
                <span className="text-2xl">⬇️</span>
              </div>
              <div className="text-2xl font-bold text-red-800">{analystReaction.downgrades}</div>
              <div className="text-sm text-red-600">Rating reductions</div>
            </div>

            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200">
              <div className="flex items-center justify-between mb-2">
                <h4 className="font-semibold text-blue-900">Price Target</h4>
                <span className="text-2xl">{getReactionIcon(analystReaction.priceTargetChange)}</span>
              </div>
              <div className={`text-2xl font-bold ${
                analystReaction.priceTargetChange > 0 ? 'text-green-800' : 
                analystReaction.priceTargetChange < 0 ? 'text-red-800' : 'text-blue-800'
              }`}>
                {analystReaction.priceTargetChange > 0 ? '+' : ''}${analystReaction.priceTargetChange.toFixed(0)}
              </div>
              <div className="text-sm text-blue-600">Average change</div>
            </div>
          </div>
        </div>

        {/* Investment Takeaways */}
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Key Investment Takeaways</h3>
          <div className="space-y-3">
            {takeaways.map((takeaway, index) => (
              <div key={index} className={`rounded-lg p-4 border-l-4 ${getImportanceColor(takeaway.importance)}`}>
                <div className="flex items-start gap-3">
                  <div className="flex items-center gap-2">
                    <span className={`w-3 h-3 rounded-full ${
                      takeaway.importance === 'high' ? 'bg-red-400' :
                      takeaway.importance === 'medium' ? 'bg-yellow-400' : 'bg-blue-400'
                    }`} />
                    <span className="text-xs font-medium uppercase text-gray-600">{takeaway.importance}</span>
                  </div>
                  <p className="text-gray-800 flex-1">{takeaway.insight}</p>
                </div>
              </div>
            ))}
          </div>

          {/* Bottom Summary */}
          <div className="mt-6 bg-gray-50 rounded-lg p-4 border border-gray-200">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-lg">📝</span>
              <span className="font-semibold text-gray-900">Bottom Line</span>
            </div>
            <p className="text-gray-700 text-sm">
              {keyResults.some(r => r.surprise.toLowerCase().includes('beat')) ? 'Strong' : 'Mixed'} quarterly results with 
              {analystReaction.upgrades > analystReaction.downgrades ? ' positive' : ' cautious'} analyst sentiment. 
              Focus on {takeaways.filter(t => t.importance === 'high').length} high-priority factors for investment decisions.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}