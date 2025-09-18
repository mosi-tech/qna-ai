'use client';

import { useState } from 'react';

interface Trade {
  id: string;
  symbol: string;
  type: 'buy' | 'sell';
  date: string;
  price: number;
  quantity: number;
  pnl?: number;
  reason: string;
}

interface BacktestResultsProps {
  isRunning: boolean;
  results: {
    totalReturn: number;
    annualizedReturn: number;
    sharpeRatio: number;
    maxDrawdown: number;
    winRate: number;
    totalTrades: number;
    avgTradeReturn: number;
    trades: Trade[];
  } | null;
}

export default function BacktestResults({ isRunning, results }: BacktestResultsProps) {
  const [activeTab, setActiveTab] = useState<'performance' | 'metrics' | 'trades'>('performance');

  if (isRunning) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="text-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <h3 className="text-lg font-semibold text-gray-900 mb-2">Running Backtest...</h3>
          <p className="text-gray-600">This may take a few moments</p>
        </div>
      </div>
    );
  }

  if (!results) {
    return (
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <div className="text-center py-12 text-gray-500">
          <div className="text-4xl mb-4">📊</div>
          <h3 className="text-lg font-semibold mb-2">Ready to Backtest</h3>
          <p>Configure your strategy and run a backtest to see results here</p>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Backtest Results</h3>

      {/* Tab Navigation */}
      <div className="flex border-b border-gray-200 mb-6">
        <button
          onClick={() => setActiveTab('performance')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'performance'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          📈 Performance
        </button>
        <button
          onClick={() => setActiveTab('metrics')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'metrics'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          📊 Metrics
        </button>
        <button
          onClick={() => setActiveTab('trades')}
          className={`px-4 py-2 text-sm font-medium border-b-2 transition-colors ${
            activeTab === 'trades'
              ? 'border-blue-500 text-blue-600'
              : 'border-transparent text-gray-500 hover:text-gray-700'
          }`}
        >
          📋 Trades ({results.totalTrades})
        </button>
      </div>

      {/* Performance Tab */}
      {activeTab === 'performance' && (
        <div>
          {/* Chart Placeholder */}
          <div className="bg-gradient-to-br from-blue-50 to-indigo-100 rounded-lg p-8 text-center border border-blue-200 relative overflow-hidden mb-6">
            <div className="absolute inset-0 opacity-10">
              <svg className="w-full h-full" viewBox="0 0 400 200">
                <path d="M50,150 Q100,120 150,100 T250,80 T350,60" stroke="rgb(34, 197, 94)" strokeWidth="3" fill="none"/>
                <path d="M50,160 Q100,140 150,130 T250,120 T350,110" stroke="rgb(59, 130, 246)" strokeWidth="2" fill="none" opacity="0.7"/>
              </svg>
            </div>
            <div className="relative z-10">
              <div className="text-green-600 text-3xl mb-3">📈</div>
              <div className="text-gray-700 font-medium text-lg">Portfolio Performance</div>
              <div className="text-sm text-gray-600 mt-2">
                Strategy vs Buy & Hold comparison chart would be displayed here
              </div>
              <div className="mt-4 flex justify-center gap-4">
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-green-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">Strategy</span>
                </div>
                <div className="flex items-center gap-2">
                  <div className="w-3 h-3 bg-blue-500 rounded-full"></div>
                  <span className="text-sm text-gray-600">Buy & Hold</span>
                </div>
              </div>
            </div>
          </div>

          {/* Key Performance Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-600">
                {results.totalReturn > 0 ? '+' : ''}{results.totalReturn.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Total Return</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-blue-600">
                {results.annualizedReturn.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Annualized</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-purple-600">
                {results.sharpeRatio.toFixed(2)}
              </div>
              <div className="text-sm text-gray-600">Sharpe Ratio</div>
            </div>
            <div className="bg-gray-50 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-red-600">
                {results.maxDrawdown.toFixed(1)}%
              </div>
              <div className="text-sm text-gray-600">Max Drawdown</div>
            </div>
          </div>
        </div>
      )}

      {/* Metrics Tab */}
      {activeTab === 'metrics' && (
        <div className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Returns */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-3">Returns</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Total Return</span>
                  <span className="font-medium">{results.totalReturn.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Annualized Return</span>
                  <span className="font-medium">{results.annualizedReturn.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Avg Trade Return</span>
                  <span className="font-medium">{results.avgTradeReturn.toFixed(2)}%</span>
                </div>
              </div>
            </div>

            {/* Risk Metrics */}
            <div className="bg-gray-50 rounded-lg p-4">
              <h4 className="font-medium text-gray-900 mb-3">Risk</h4>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-600">Sharpe Ratio</span>
                  <span className="font-medium">{results.sharpeRatio.toFixed(2)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Max Drawdown</span>
                  <span className="font-medium">{results.maxDrawdown.toFixed(2)}%</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-600">Win Rate</span>
                  <span className="font-medium">{results.winRate.toFixed(1)}%</span>
                </div>
              </div>
            </div>
          </div>

          {/* Trading Activity */}
          <div className="bg-gray-50 rounded-lg p-4">
            <h4 className="font-medium text-gray-900 mb-3">Trading Activity</h4>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-xl font-bold text-blue-600">{results.totalTrades}</div>
                <div className="text-sm text-gray-600">Total Trades</div>
              </div>
              <div>
                <div className="text-xl font-bold text-green-600">
                  {Math.round(results.totalTrades * results.winRate / 100)}
                </div>
                <div className="text-sm text-gray-600">Winning Trades</div>
              </div>
              <div>
                <div className="text-xl font-bold text-red-600">
                  {results.totalTrades - Math.round(results.totalTrades * results.winRate / 100)}
                </div>
                <div className="text-sm text-gray-600">Losing Trades</div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Trades Tab */}
      {activeTab === 'trades' && (
        <div>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left py-2 px-3 font-medium text-gray-900">Date</th>
                  <th className="text-left py-2 px-3 font-medium text-gray-900">Symbol</th>
                  <th className="text-left py-2 px-3 font-medium text-gray-900">Type</th>
                  <th className="text-right py-2 px-3 font-medium text-gray-900">Price</th>
                  <th className="text-right py-2 px-3 font-medium text-gray-900">Quantity</th>
                  <th className="text-right py-2 px-3 font-medium text-gray-900">P&L</th>
                  <th className="text-left py-2 px-3 font-medium text-gray-900">Reason</th>
                </tr>
              </thead>
              <tbody>
                {results.trades.map((trade) => (
                  <tr key={trade.id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="py-2 px-3">{trade.date}</td>
                    <td className="py-2 px-3 font-medium">{trade.symbol}</td>
                    <td className="py-2 px-3">
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        trade.type === 'buy' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {trade.type.toUpperCase()}
                      </span>
                    </td>
                    <td className="py-2 px-3 text-right">${trade.price.toFixed(2)}</td>
                    <td className="py-2 px-3 text-right">{trade.quantity}</td>
                    <td className="py-2 px-3 text-right">
                      {trade.pnl !== undefined && (
                        <span className={trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'}>
                          {trade.pnl >= 0 ? '+' : ''}${trade.pnl.toFixed(2)}
                        </span>
                      )}
                    </td>
                    <td className="py-2 px-3 text-gray-600">{trade.reason}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
}