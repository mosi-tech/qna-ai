'use client';

import React from 'react';
import { FailedBreakdownRankingTable } from '@/components/mdx/FailedBreakdownRankingTable';
import { BreakdownFrequencyChart } from '@/components/mdx/BreakdownFrequencyChart';
import { BreakdownTimelineChart } from '@/components/mdx/BreakdownTimelineChart';
import { BreakdownMetricsSummary } from '@/components/mdx/BreakdownMetricsSummary';
import { ApproveButtons } from '@/components/mdx/ApproveButtons';

export default function FailedBreakdownAnalysisPage() {
  // Sample data for the analysis
  const sampleSymbols = [
    { symbol: "NVDA", failedBreakdowns: 12, successRate: 18.5, avgLoss: -4.2 },
    { symbol: "TSLA", failedBreakdowns: 11, successRate: 22.1, avgLoss: -3.8 },
    { symbol: "AMD", failedBreakdowns: 9, successRate: 25.4, avgLoss: -3.5 },
    { symbol: "META", failedBreakdowns: 8, successRate: 31.2, avgLoss: -3.1 },
    { symbol: "AAPL", failedBreakdowns: 7, successRate: 28.9, avgLoss: -2.9 }
  ];

  const frequencyData = [
    { symbol: "NVDA", count: 12 },
    { symbol: "TSLA", count: 11 }, 
    { symbol: "AMD", count: 9 },
    { symbol: "META", count: 8 },
    { symbol: "AAPL", count: 7 }
  ];

  const breakdownEvents = [
    { symbol: "NVDA", date: "2024-01-15", price: 485.2, support: 480 },
    { symbol: "TSLA", date: "2024-01-18", price: 218.7, support: 220 },
    { symbol: "AMD", date: "2024-01-22", price: 142.1, support: 145 },
    { symbol: "META", date: "2024-01-25", price: 385.4, support: 390 },
    { symbol: "AAPL", date: "2024-01-28", price: 189.3, support: 192 },
    { symbol: "NVDA", date: "2024-02-05", price: 478.9, support: 485 },
    { symbol: "TSLA", date: "2024-02-08", price: 215.2, support: 218 },
    { symbol: "AMD", date: "2024-02-12", price: 138.7, support: 142 }
  ];

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
            <span className="text-sm text-gray-600">Failed Breakdown Analysis</span>
          </div>
        </div>

        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Failed Breakdown Analysis - Past 60 Days
          </h1>
          <p className="text-xl text-gray-600">
            This analysis identifies which symbols experienced the most failed breakdowns in the last 60 days, helping traders understand which stocks struggled to maintain support levels.
          </p>
        </div>

        <div className="space-y-8">
          <div>
            <BreakdownMetricsSummary 
              totalBreakdowns={247} 
              successRate={23.8} 
              avgRecoveryTime={8.4} 
              period="60 days" 
            />
            <ApproveButtons component="BreakdownMetricsSummary" />
          </div>

          <div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Top Symbols by Failed Breakdowns
            </h2>
            <p className="text-gray-600 mb-6">
              The following table ranks symbols by the number of failed breakdowns, showing which stocks had the most difficulty holding support levels.
            </p>
            
            <FailedBreakdownRankingTable 
              symbols={sampleSymbols} 
              timeframe="60 days" 
              showDetails={true} 
            />
            <ApproveButtons component="FailedBreakdownRankingTable" />
          </div>

          <div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Breakdown Frequency Distribution
            </h2>
            <p className="text-gray-600 mb-6">
              This chart visualizes the frequency of failed breakdowns across different symbols, making it easy to identify outliers.
            </p>
            
            <BreakdownFrequencyChart 
              data={frequencyData} 
              period="60 days" 
              height={400} 
            />
            <ApproveButtons component="BreakdownFrequencyChart" />
          </div>

          <div>
            <h2 className="text-2xl font-semibold text-gray-900 mb-4">
              Timeline of Failed Breakdowns
            </h2>
            <p className="text-gray-600 mb-6">
              Understanding when breakdowns occurred helps identify market stress periods and potential catalysts.
            </p>
            
            <BreakdownTimelineChart 
              breakdowns={breakdownEvents} 
              symbols={["NVDA", "TSLA", "AMD", "META", "AAPL"]} 
              dateRange={{start: "2024-01-01", end: "2024-03-01"}} 
            />
            <ApproveButtons component="BreakdownTimelineChart" />
          </div>
        </div>
      </div>
    </div>
  );
}