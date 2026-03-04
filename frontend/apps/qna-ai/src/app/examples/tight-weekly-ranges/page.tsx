'use client';

import React from 'react';
import { MetricsTable } from '@/components/mdx/MetricsTable';
import { BarChart } from '@/components/mdx/BarChart';
import { LineChart } from '@/components/mdx/LineChart';
import { AnalysisInsights } from '@/components/mdx/AnalysisInsights';
import { ApproveButtons } from '@/components/mdx/ApproveButtons';

export default function TightWeeklyRangesPage() {
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
            <span className="text-sm text-gray-600">Tight Weekly Ranges</span>
          </div>
        </div>

        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Weekly Range Compression Dashboard
          </h1>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <MetricsTable 
            data={[
              {Symbol: "AAPL", "Avg Range": "2.1%", "Min Range": "0.8%", "Max Range": "4.2%", "Compression": "Very High"},
              {Symbol: "MSFT", "Avg Range": "2.3%", "Min Range": "1.0%", "Max Range": "4.8%", "Compression": "High"},
              {Symbol: "KO", "Avg Range": "2.5%", "Min Range": "1.2%", "Max Range": "5.1%", "Compression": "High"},
              {Symbol: "NVDA", "Avg Range": "8.4%", "Min Range": "3.2%", "Max Range": "15.7%", "Compression": "Low"},
              {Symbol: "TSLA", "Avg Range": "12.1%", "Min Range": "5.8%", "Max Range": "22.4%", "Compression": "Very Low"}
            ]}
            columns={["Symbol", "Avg Range", "Min Range", "Max Range", "Compression"]} 
            title="Range Compression Rankings"
            sortBy="Avg Range" 
          />
          
          <BarChart 
            data={[
              {symbol: "AAPL", range: 2.1},
              {symbol: "MSFT", range: 2.3}, 
              {symbol: "KO", range: 2.5},
              {symbol: "NVDA", range: 8.4},
              {symbol: "TSLA", range: 12.1}
            ]}
            xField="symbol"
            yField="range"
            title="Average Weekly Ranges"
            color="#10B981"
          />
        </div>

        <ApproveButtons component="MetricsTable" />
        <ApproveButtons component="BarChart" />

        <LineChart 
          data={[
            {week: "Week 1", avgRange: 3.2},
            {week: "Week 2", avgRange: 2.8}, 
            {week: "Week 3", avgRange: 2.1},
            {week: "Week 4", avgRange: 1.9},
            {week: "Week 5", avgRange: 2.0},
            {week: "Week 6", avgRange: 1.8},
            {week: "Week 7", avgRange: 2.2},
            {week: "Week 8", avgRange: 1.7},
            {week: "Week 9", avgRange: 1.9},
            {week: "Week 10", avgRange: 1.6},
            {week: "Week 11", avgRange: 2.1},
            {week: "Week 12", avgRange: 1.8}
          ]}
          xField="week"
          yField="avgRange"
          title="Weekly Range Evolution"
          height={300}
        />
        <ApproveButtons component="LineChart" />

        <AnalysisInsights 
          summary="AAPL leads with tightest ranges at 2.1% average, indicating strong price stability"
          keyFindings={[
            "AAPL shows exceptional range compression (2.1% avg, 0.8% min)",
            "Tech giants (AAPL, MSFT) demonstrate lower volatility than expected", 
            "Portfolio volatility compressed 47% from Q4 to Q1",
            "Range compression accelerated in final 4 weeks of quarter"
          ]}
          recommendations={[
            "Consider increasing position sizes in compressed names (AAPL, MSFT)",
            "Prepare for potential volatility expansion after compression",
            "Use tight ranges for options strategies (iron condors, butterflies)",
            "Monitor for breakout signals as compression often precedes large moves"
          ]}
          metrics={{
            avgPortfolioRange: 2.28, 
            compressionRatio: 0.47, 
            tightestPosition: "AAPL",
            compressionTrend: "Accelerating"
          }}
        />
        <ApproveButtons component="AnalysisInsights" />
      </div>
    </div>
  );
}