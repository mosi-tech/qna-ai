'use client';

import React from 'react';
import { MetricsTable } from '@/components/mdx/MetricsTable';
import { ScatterChart } from '@/components/mdx/ScatterChart';
import { BarChart } from '@/components/mdx/BarChart';
import { AnalysisInsights } from '@/components/mdx/AnalysisInsights';
import { ApproveButtons } from '@/components/mdx/ApproveButtons';

export default function PositionSymmetryV2Page() {
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
            <span className="text-sm text-gray-600">Position Symmetry Analysis V2</span>
          </div>
        </div>

        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Position Symmetry Dashboard
          </h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <MetricsTable 
            data={[
              {Symbol: "MSFT", "Up Days": 51, "Down Days": 49, "Ratio": 1.04, "Score": "96%"},
              {Symbol: "AAPL", "Up Days": 48, "Down Days": 52, "Ratio": 0.92, "Score": "92%"},
              {Symbol: "META", "Up Days": 49, "Down Days": 51, "Ratio": 0.96, "Score": "94%"},
              {Symbol: "TSLA", "Up Days": 38, "Down Days": 62, "Ratio": 0.61, "Score": "61%"}
            ]}
            columns={["Symbol", "Up Days", "Down Days", "Ratio", "Score"]} 
            title="Symmetry Rankings"
            sortBy="Score" 
          />
          
          <ScatterChart 
            data={[
              {symbol: "MSFT", upDays: 51, downDays: 49},
              {symbol: "AAPL", upDays: 48, downDays: 52}, 
              {symbol: "META", upDays: 49, downDays: 51},
              {symbol: "TSLA", upDays: 38, downDays: 62}
            ]}
            xField="upDays"
            yField="downDays"
            labelField="symbol"
            title="Up vs Down Days"
            height={300} 
          />
        </div>

        <ApproveButtons component="MetricsTable" />
        <ApproveButtons component="ScatterChart" />

        <BarChart 
          data={[
            {range: "0.5-0.7", count: 1},
            {range: "0.7-0.9", count: 0}, 
            {range: "0.9-1.1", count: 3},
            {range: "1.1-1.3", count: 0}
          ]}
          xField="range"
          yField="count"
          title="Symmetry Distribution"
          color="#3B82F6"
        />
        <ApproveButtons component="BarChart" />

        <AnalysisInsights 
          summary="Portfolio shows mixed symmetry with MSFT leading at 96% balance"
          keyFindings={[
            "MSFT displays excellent up/down balance (51/49 days)",
            "TSLA shows significant asymmetry bias (38/62 days)", 
            "3 positions cluster near perfect symmetry (0.9-1.1 ratio)"
          ]}
          recommendations={[
            "Focus allocation on symmetric positions (MSFT, META)",
            "Consider reducing TSLA exposure due to directional bias",
            "Monitor for mean reversion in asymmetric positions"
          ]}
          metrics={{portfolioBalance: 0.88, averageRatio: 0.88, topSymmetric: "MSFT"}}
        />
        <ApproveButtons component="AnalysisInsights" />
      </div>
    </div>
  );
}