'use client';

import React from 'react';
import { LeaderboardFormat } from '@/components/mdx/insights/LeaderboardFormat';
import { HeadToHeadFormat } from '@/components/mdx/insights/HeadToHeadFormat';
import { WeatherReportFormat } from '@/components/mdx/insights/WeatherReportFormat';
import { SportsCasterFormat } from '@/components/mdx/insights/SportsCasterFormat';
import { TrendStoryFormat } from '@/components/mdx/insights/TrendStoryFormat';
import { RiskDashboardFormat } from '@/components/mdx/insights/RiskDashboardFormat';
import { EarningsReportFormat } from '@/components/mdx/insights/EarningsReportFormat';

export default function WorkingExamplesPage() {
  // Sample data based on tight weekly ranges analysis
  const leaderboardData = {
    winner: { symbol: "AAPL", metric: 2.1, achievement: "Tightest Weekly Ranges", badge: "Range Master" },
    runnerUps: [
      { rank: 2, symbol: "MSFT", metric: 2.3, gap: "0.2%" },
      { rank: 3, symbol: "KO", metric: 2.5, gap: "0.4%" }
    ],
    fullRankings: [
      { rank: 1, symbol: "AAPL", primaryMetric: 2.1, secondaryMetrics: { minRange: 0.8, compression: "Very High" } },
      { rank: 2, symbol: "MSFT", primaryMetric: 2.3, secondaryMetrics: { minRange: 1.0, compression: "High" } },
      { rank: 3, symbol: "KO", primaryMetric: 2.5, secondaryMetrics: { minRange: 1.2, compression: "High" } }
    ],
    insights: ["AAPL demonstrates exceptional price stability", "Large-cap tech outperformed in volatility control"]
  };

  const trendData = {
    timeframe: "Q1 2024",
    overallTrend: { direction: "Range Compression", strength: 85, description: "Sustained period of declining volatility across portfolio" },
    threeActs: {
      beginning: "Q4 2023 showed elevated volatility from Fed uncertainty and earnings concerns",
      middle: "January 2024 marked the start of systematic range compression as markets found direction",
      current: "March 2024 ended with historically tight ranges, setting stage for potential breakout"
    },
    inflectionPoints: [
      { date: "Jan 15", event: "Fed Pivot Signals", impact: "Volatility dropped 30% as rate uncertainty cleared" },
      { date: "Feb 12", event: "Tech Earnings Beat", impact: "Range compression accelerated in growth names" }
    ],
    nextChapter: {
      outlook: "Volatility expansion likely as compressed ranges reach historical extremes",
      keyCatalysts: ["Q1 earnings season", "Fed meeting minutes", "Geopolitical developments"],
      timeframe: "Next 30-60 days"
    }
  };

  const riskData = {
    overallRisk: { level: "Moderate", score: 45, trend: "Stable", description: "Balanced risk profile with controlled exposures" },
    exposures: [
      { category: "Tech Sector", exposure: 35.2, limit: 40.0, status: "safe" as const },
      { category: "Single Name", exposure: 8.9, limit: 10.0, status: "caution" as const },
      { category: "Duration Risk", exposure: 12.1, limit: 15.0, status: "safe" as const }
    ],
    scenarios: [
      { scenario: "Market Correction (-15%)", probability: 20, impact: "Moderate portfolio stress", drawdown: -12.3 },
      { scenario: "Tech Sector Rotation", probability: 35, impact: "Sector concentration risk", drawdown: -8.7 }
    ],
    trends: [
      { metric: "VaR (1-day)", current: 1.23, previous: 1.18, direction: "up" },
      { metric: "Beta to SPY", current: 0.89, previous: 0.92, direction: "down" }
    ],
    alerts: [
      { priority: "medium" as const, message: "Tech concentration approaching limit", action: "Consider rebalancing", deadline: "End of week" }
    ]
  };

  const earningsData = {
    headline: "AAPL Beats Q1 Estimates on Strong iPhone Sales and Services Growth",
    keyResults: [
      { metric: "EPS", actual: 2.18, estimate: 2.10, surprise: "4% Beat" },
      { metric: "Revenue ($M)", actual: 119800, estimate: 117900, surprise: "2% Beat" },
      { metric: "iPhone Revenue ($M)", actual: 69700, estimate: 68200, surprise: "2% Beat" }
    ],
    commentary: [
      "iPhone 15 cycle performing better than expected with strong Pro model mix",
      "Services revenue growth of 11% demonstrates recurring revenue strength",
      "Guidance for Q2 suggests continued momentum despite macro headwinds"
    ],
    analystReaction: { upgrades: 3, downgrades: 1, priceTargetChange: 5.50 },
    takeaways: [
      { insight: "iPhone cycle strength reduces near-term downside risk", importance: "high" as const },
      { insight: "Services growth trajectory supports premium valuation", importance: "medium" as const }
    ]
  };

  return (
    <div className="min-h-screen bg-gray-50 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Navigation */}
        <div className="mb-6 flex items-center gap-4">
          <a href="/examples/insight-formats" className="text-blue-600 hover:text-blue-800 text-sm font-medium">← Back to Formats</a>
          <span className="text-gray-300">|</span>
          <span className="text-sm text-gray-600">Working Examples</span>
        </div>

        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Working Format Examples</h1>
          <p className="text-gray-600">7 implemented financial insight formats with live data</p>
        </div>

        <div className="space-y-8">
          {/* Leaderboard */}
          <div>
            <h2 className="text-xl font-semibold mb-4 text-blue-900">🏆 Leaderboard Format</h2>
            <LeaderboardFormat data={leaderboardData} title="Tightest Weekly Ranges Q1 2024" />
          </div>

          {/* Trend Story */}
          <div>
            <h2 className="text-xl font-semibold mb-4 text-purple-900">📈 Trend Story Format</h2>
            <TrendStoryFormat data={trendData} title="Range Compression Story" />
          </div>

          {/* Risk Dashboard */}
          <div>
            <h2 className="text-xl font-semibold mb-4 text-rose-900">⚠️ Risk Dashboard Format</h2>
            <RiskDashboardFormat data={riskData} title="Portfolio Risk Monitor" />
          </div>

          {/* Earnings Report */}
          <div>
            <h2 className="text-xl font-semibold mb-4 text-green-900">📊 Earnings Report Format</h2>
            <EarningsReportFormat data={earningsData} title="Q1 2024 Earnings" ticker="AAPL" />
          </div>

          <div className="bg-white rounded-lg p-6 border border-gray-200 text-center">
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Additional Formats Available</h3>
            <p className="text-gray-600 mb-4">HeadToHeadFormat, WeatherReportFormat, SportsCasterFormat also implemented</p>
            <div className="flex justify-center gap-4">
              <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full text-sm">7 Built</span>
              <span className="bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full text-sm">8 Remaining</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}