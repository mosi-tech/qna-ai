'use client';

import React from 'react';
import { SymmetryMetricsTable } from '@/components/mdx/SymmetryMetricsTable';
import { SymmetryScatterChart } from '@/components/mdx/SymmetryScatterChart';
import { SymmetryDistributionChart } from '@/components/mdx/SymmetryDistributionChart';
import { SymmetryInsights } from '@/components/mdx/SymmetryInsights';
import { ApproveButtons } from '@/components/mdx/ApproveButtons';

export default function PositionSymmetryPage() {
  // Sample data
  const symmetryData = [
    { symbol: "AAPL", upDays: 48, downDays: 52, ratio: 0.92, symmetryScore: 92.3 },
    { symbol: "MSFT", upDays: 51, downDays: 49, ratio: 1.04, symmetryScore: 96.1 },
    { symbol: "GOOGL", upDays: 46, downDays: 54, ratio: 0.85, symmetryScore: 85.2 },
    { symbol: "TSLA", upDays: 38, downDays: 62, ratio: 0.61, symmetryScore: 61.3 },
    { symbol: "NVDA", upDays: 44, downDays: 56, ratio: 0.79, symmetryScore: 78.6 },
    { symbol: "META", upDays: 49, downDays: 51, ratio: 0.96, symmetryScore: 94.1 },
    { symbol: "AMZN", upDays: 42, downDays: 58, ratio: 0.72, symmetryScore: 72.4 }
  ];

  const ratios = symmetryData.map(d => d.ratio);

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Navigation Header */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <a 
              href="/examples" 
              className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center gap-2"
            >
              ← Back to Examples
            </a>
            <span className="text-gray-300">|</span>
            <span className="text-sm text-gray-600">Position Symmetry Analysis</span>
          </div>
        </div>

        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Position Symmetry Dashboard
          </h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
          <SymmetryMetricsTable 
            positions={symmetryData} 
            sortBy="symmetryScore" 
          />
          
          <SymmetryScatterChart 
            data={symmetryData.map(d => ({
              symbol: d.symbol,
              upDays: d.upDays,
              downDays: d.downDays
            }))} 
            height={300} 
          />
        </div>

        <ApproveButtons component="SymmetryMetricsTable" />
        <ApproveButtons component="SymmetryScatterChart" />

        <div className="mb-6">
          <SymmetryDistributionChart 
            ratios={ratios} 
            bins={10} 
          />
        </div>

        <ApproveButtons component="SymmetryDistributionChart" />

        <SymmetryInsights 
          mostSymmetric={["MSFT", "META", "AAPL"]} 
          leastSymmetric={["TSLA", "AMZN"]}
          portfolioBalance={0.84}
          recommendations={[
            "Focus on symmetric positions (MSFT, META) for stability",
            "Consider reducing exposure to highly asymmetric positions (TSLA)",
            "Monitor NVDA and GOOGL for potential rebalancing opportunities",
            "Implement dynamic position sizing based on symmetry scores"
          ]}
        />
        <ApproveButtons component="SymmetryInsights" />
      </div>
    </div>
  );
}