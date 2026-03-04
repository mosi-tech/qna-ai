'use client';

import React from 'react';

interface LeaderboardData {
  winner: {
    symbol: string;
    metric: number;
    achievement: string;
    badge: string;
  };
  runnerUps: Array<{
    rank: number;
    symbol: string;
    metric: number;
    gap: string;
  }>;
  fullRankings: Array<{
    rank: number;
    symbol: string;
    primaryMetric: number;
    secondaryMetrics: Record<string, any>;
  }>;
  insights: string[];
}

interface LeaderboardFormatProps {
  data: LeaderboardData;
  title?: string;
  metricLabel?: string;
}

export function LeaderboardFormat({
  data,
  title = "Performance Ranking",
  metricLabel = "Performance"
}: LeaderboardFormatProps) {
  const { winner, runnerUps, fullRankings, insights } = data;

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-500 mt-1">Ranked performance analysis</p>
      </div>

      <div className="p-6 space-y-6">
        {/* Top Performer Summary */}
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="text-sm font-semibold text-blue-800 mb-2">Top Performer</h4>
          <div className="flex justify-between items-center">
            <div>
              <span className="text-lg font-bold text-blue-900">{winner.symbol}</span>
              <span className="text-sm text-blue-700 ml-2">{winner.achievement}</span>
            </div>
            <div className="text-right">
              <div className="text-lg font-bold text-blue-900">{winner.metric.toFixed(2)}%</div>
              <div className="text-xs text-blue-600">{metricLabel}</div>
            </div>
          </div>
        </div>

        {/* Rankings Table */}
        <div className="overflow-hidden rounded-lg border border-gray-200">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Rank</th>
                <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Symbol</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">{metricLabel}</th>
                <th className="px-4 py-3 text-right text-xs font-medium text-gray-500 uppercase">Gap to Leader</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {fullRankings.map((item) => (
                <tr key={item.rank} className="hover:bg-gray-50">
                  <td className="px-4 py-3 text-sm font-medium text-gray-900">#{item.rank}</td>
                  <td className="px-4 py-3 font-medium text-gray-900">{item.symbol}</td>
                  <td className="px-4 py-3 text-right font-semibold text-gray-900">{item.primaryMetric.toFixed(2)}%</td>
                  <td className="px-4 py-3 text-right text-sm text-gray-500">
                    {item.rank === 1 ? '-' : `+${(item.primaryMetric - winner.metric).toFixed(1)}%`}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Analysis Summary */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 className="text-sm font-semibold text-green-800 mb-3">Key Findings</h4>
            <ul className="space-y-2">
              {insights.slice(0, Math.ceil(insights.length / 2)).map((insight, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span className="text-sm text-green-700">{insight}</span>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
            <h4 className="text-sm font-semibold text-orange-800 mb-3">Performance Notes</h4>
            <ul className="space-y-2">
              {insights.slice(Math.ceil(insights.length / 2)).map((insight, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <div className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span className="text-sm text-orange-700">{insight}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}