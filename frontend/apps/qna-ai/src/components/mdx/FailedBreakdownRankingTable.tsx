'use client';

import React from 'react';

interface BreakdownSymbol {
  symbol: string;
  failedBreakdowns: number;
  successRate: number;
  avgLoss: number;
}

interface FailedBreakdownRankingTableProps {
  symbols: BreakdownSymbol[];
  timeframe: string;
  showDetails: boolean;
}

export function FailedBreakdownRankingTable({
  symbols,
  timeframe,
  showDetails
}: FailedBreakdownRankingTableProps) {
  const sortedSymbols = [...symbols].sort((a, b) => b.failedBreakdowns - a.failedBreakdowns);

  return (
    <div className="w-full bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">
          Failed Breakdown Rankings
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          Symbols ranked by failed breakdowns over {timeframe}
        </p>
      </div>
      
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50">
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Rank
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Symbol
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                Failed Breakdowns
              </th>
              {showDetails && (
                <>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Success Rate
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Avg Loss
                  </th>
                </>
              )}
            </tr>
          </thead>
          <tbody className="bg-white divide-y divide-gray-200">
            {sortedSymbols.map((symbol, index) => (
              <tr key={symbol.symbol} className="hover:bg-gray-50">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  #{index + 1}
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="text-sm font-medium text-gray-900">
                    {symbol.symbol}
                  </div>
                </td>
                <td className="px-6 py-4 whitespace-nowrap">
                  <div className="flex items-center">
                    <div className="text-sm font-semibold text-red-600">
                      {symbol.failedBreakdowns}
                    </div>
                    <div className="ml-2 w-16 bg-gray-200 rounded-full h-2">
                      <div
                        className="bg-red-500 h-2 rounded-full"
                        style={{
                          width: `${Math.min((symbol.failedBreakdowns / Math.max(...sortedSymbols.map(s => s.failedBreakdowns))) * 100, 100)}%`
                        }}
                      ></div>
                    </div>
                  </div>
                </td>
                {showDetails && (
                  <>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className={`font-medium ${
                        symbol.successRate < 20 ? 'text-red-600' : 
                        symbol.successRate < 40 ? 'text-orange-600' : 'text-green-600'
                      }`}>
                        {symbol.successRate.toFixed(1)}%
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-red-600">
                      {symbol.avgLoss.toFixed(1)}%
                    </td>
                  </>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}