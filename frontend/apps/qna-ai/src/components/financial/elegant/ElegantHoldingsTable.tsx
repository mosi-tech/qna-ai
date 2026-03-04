'use client';

import React from 'react';
import { Group } from '@visx/group';
import { Bar } from '@visx/shape';
import { scaleLinear } from '@visx/scale';
import { ParentSize } from '@visx/responsive';

interface Holding {
  symbol: string;
  name: string;
  shares: number;
  value: number;
  weight: number;
  dayChange: number;
  sector: string;
  pe?: number;
  yield?: number;
}

interface ElegantHoldingsTableProps {
  holdings: Holding[];
  totalValue: number;
  title?: string;
  showMetrics?: boolean;
}

export function ElegantHoldingsTable({
  holdings,
  totalValue,
  title = "Top Holdings",
  showMetrics = true
}: ElegantHoldingsTableProps) {
  // Sort holdings by weight descending
  const sortedHoldings = [...holdings].sort((a, b) => b.weight - a.weight);
  const maxWeight = Math.max(...sortedHoldings.map(h => h.weight));
  
  return (
    <div className="w-full">
      {/* Clean header */}
      <div className="px-6 py-4 border-b border-gray-100">
        <h2 className="text-2xl font-light text-gray-900">{title}</h2>
        <p className="text-sm text-gray-500 mt-1">
          ${totalValue.toLocaleString()} • {sortedHoldings.length} positions
        </p>
      </div>

      {/* Holdings list with embedded visualizations */}
      <div className="divide-y divide-gray-50">
        {sortedHoldings.map((holding, index) => (
          <HoldingRow
            key={holding.symbol}
            holding={holding}
            maxWeight={maxWeight}
            rank={index + 1}
            showMetrics={showMetrics}
          />
        ))}
      </div>
    </div>
  );
}

interface HoldingRowProps {
  holding: Holding;
  maxWeight: number;
  rank: number;
  showMetrics: boolean;
}

function HoldingRow({ holding, maxWeight, rank, showMetrics }: HoldingRowProps) {
  const isPositive = holding.dayChange >= 0;
  
  return (
    <div className="group hover:bg-gray-25 transition-colors duration-150">
      <div className="px-6 py-4">
        <div className="flex items-center justify-between">
          {/* Left: Symbol, Name, and Weight Bar */}
          <div className="flex-1 min-w-0">
            <div className="flex items-center space-x-4">
              {/* Rank */}
              <div className="w-6 text-right">
                <span className="text-xs font-medium text-gray-400">{rank}</span>
              </div>
              
              {/* Symbol & Company */}
              <div className="min-w-0 flex-1">
                <div className="flex items-baseline space-x-3">
                  <h3 className="text-lg font-semibold text-gray-900 tracking-tight">
                    {holding.symbol}
                  </h3>
                  <span className="text-sm text-gray-500 truncate max-w-[200px]">
                    {holding.name}
                  </span>
                </div>
                
                {/* Weight visualization bar */}
                <div className="mt-2 flex items-center space-x-3">
                  <div className="flex-1 max-w-[120px]">
                    <div className="h-1 bg-gray-100 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-gradient-to-r from-blue-500 to-blue-400 transition-all duration-300"
                        style={{ width: `${(holding.weight / maxWeight) * 100}%` }}
                      />
                    </div>
                  </div>
                  <span className="text-sm font-medium text-gray-600 min-w-[40px]">
                    {holding.weight.toFixed(1)}%
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Right: Value and Performance */}
          <div className="flex items-center space-x-8 ml-6">
            {/* Position Value */}
            <div className="text-right">
              <div className="text-lg font-semibold text-gray-900">
                ${holding.value.toLocaleString()}
              </div>
              <div className="text-xs text-gray-500">
                {holding.shares.toLocaleString()} shares
              </div>
            </div>

            {/* Day Change */}
            <div className="text-right">
              <div className={`text-lg font-semibold ${
                isPositive ? 'text-emerald-600' : 'text-red-600'
              }`}>
                {isPositive ? '+' : ''}{holding.dayChange.toFixed(2)}%
              </div>
              <div className="text-xs text-gray-500">today</div>
            </div>

            {/* Metrics (PE, Yield, Sector) */}
            {showMetrics && (
              <div className="text-right min-w-[80px]">
                <div className="space-y-1">
                  {holding.pe && (
                    <div className="text-xs text-gray-600">
                      P/E: <span className="font-medium">{holding.pe.toFixed(1)}</span>
                    </div>
                  )}
                  {holding.yield && (
                    <div className="text-xs text-gray-600">
                      Yield: <span className="font-medium">{holding.yield.toFixed(1)}%</span>
                    </div>
                  )}
                </div>
                <div className="mt-2">
                  <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-700">
                    {holding.sector}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// Elegant Holdings Summary Component
interface ElegantHoldingsSummaryProps {
  holdings: Holding[];
  totalValue: number;
}

export function ElegantHoldingsSummary({ holdings, totalValue }: ElegantHoldingsSummaryProps) {
  // Calculate key metrics
  const totalPositions = holdings.length;
  const avgPosition = totalValue / totalPositions;
  const topTenWeight = holdings.slice(0, 10).reduce((sum, h) => sum + h.weight, 0);
  const gainers = holdings.filter(h => h.dayChange > 0).length;
  const losers = holdings.filter(h => h.dayChange < 0).length;
  
  const metrics = [
    { label: 'Total Positions', value: totalPositions.toString(), sublabel: 'holdings' },
    { label: 'Avg Position', value: `$${(avgPosition / 1000).toFixed(0)}K`, sublabel: 'per holding' },
    { label: 'Top 10 Weight', value: `${topTenWeight.toFixed(1)}%`, sublabel: 'concentration' },
    { label: 'Today', value: `${gainers}↑ ${losers}↓`, sublabel: 'gainers/losers' }
  ];

  return (
    <div className="bg-gradient-to-r from-gray-50 to-gray-25 rounded-xl p-6 border border-gray-100">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">Portfolio Summary</h3>
      
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-6">
        {metrics.map((metric, index) => (
          <div key={index} className="text-center">
            <div className="text-2xl font-bold text-gray-900 mb-1">
              {metric.value}
            </div>
            <div className="text-sm font-medium text-gray-600">
              {metric.label}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {metric.sublabel}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}