'use client';

import React from 'react';

export default function InsightFormatsPage() {
  return (
    <div className="h-screen bg-gray-50 p-6 overflow-hidden">
      <div className="max-w-7xl mx-auto h-full flex flex-col">
        {/* Navigation Header */}
        <div className="mb-4 flex items-center justify-between flex-shrink-0">
          <div className="flex items-center gap-4">
            <a 
              href="/examples" 
              className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center gap-2"
            >
              ← Back to Examples
            </a>
            <span className="text-gray-300">|</span>
            <span className="text-sm text-gray-600">Financial Insight Formats</span>
          </div>
        </div>

        <div className="mb-6 flex-shrink-0">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Financial Analysis Presentation Formats
          </h1>
          <p className="text-gray-600 mb-3">
            15 specialized formats for presenting financial analysis in different narrative styles
          </p>
          <div className="flex gap-3">
            <a 
              href="/examples/insight-formats/working-examples"
              className="bg-blue-600 text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
            >
              🚀 View Working Examples (7 Built)
            </a>
            <span className="bg-yellow-100 text-yellow-800 px-3 py-2 rounded-lg text-sm font-medium">
              8 formats remaining to build
            </span>
          </div>
        </div>

        {/* Formats Grid - Fits on single screen */}
        <div className="flex-1 grid grid-cols-3 gap-4 overflow-hidden">
          
          {/* Column 1 - Performance & Rankings */}
          <div className="space-y-4 overflow-auto">
            <div className="bg-blue-50 rounded-lg p-4 border border-blue-200 cursor-pointer hover:bg-blue-100 transition-colors" onClick={() => window.location.href = '/examples/insight-formats/leaderboard'}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">🏆</span>
                <h3 className="font-semibold text-blue-900">LeaderboardFormat</h3>
              </div>
              <p className="text-sm text-blue-800 mb-2">Performance rankings with winners/losers</p>
              <p className="text-xs text-blue-600">Use: "which performed best/worst", "top performers"</p>
            </div>

            <div className="bg-green-50 rounded-lg p-4 border border-green-200 cursor-pointer hover:bg-green-100 transition-colors" onClick={() => window.location.href = '/examples/insight-formats/head-to-head'}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">⚔️</span>
                <h3 className="font-semibold text-green-900">HeadToHeadFormat</h3>
              </div>
              <p className="text-sm text-green-800 mb-2">Direct A vs B comparison with clear winner</p>
              <p className="text-xs text-green-600">Use: "X vs Y", "compare stocks", investment showdowns</p>
            </div>

            <div className="bg-purple-50 rounded-lg p-4 border border-purple-200 cursor-pointer hover:bg-purple-100 transition-colors" onClick={() => window.location.href = '/examples/insight-formats/trend-story'}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">📈</span>
                <h3 className="font-semibold text-purple-900">TrendStoryFormat</h3>
              </div>
              <p className="text-sm text-purple-800 mb-2">Investment story with narrative arc over time</p>
              <p className="text-xs text-purple-600">Use: "over time", "trend analysis", "this quarter"</p>
            </div>

            <div className="bg-yellow-50 rounded-lg p-4 border border-yellow-200 cursor-pointer hover:bg-yellow-100 transition-colors" onClick={() => window.location.href = '/examples/insight-formats/volatility-weather'}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">🌦️</span>
                <h3 className="font-semibold text-yellow-900">VolatilityWeatherFormat</h3>
              </div>
              <p className="text-sm text-yellow-800 mb-2">Volatility analysis using weather metaphors</p>
              <p className="text-xs text-yellow-600">Use: volatility, risk, VIX, market conditions</p>
            </div>

            <div className="bg-red-50 rounded-lg p-4 border border-red-200 cursor-pointer hover:bg-red-100 transition-colors" onClick={() => window.location.href = '/examples/insight-formats/outlier-spotlight'}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">⚡</span>
                <h3 className="font-semibold text-red-900">OutlierSpotlightFormat</h3>
              </div>
              <p className="text-sm text-red-800 mb-2">Highlight extreme/unusual investment cases</p>
              <p className="text-xs text-red-600">Use: "most/least", "highest/lowest", unusual behavior</p>
            </div>
          </div>

          {/* Column 2 - Analysis & Factors */}
          <div className="space-y-4 overflow-auto">
            <div className="bg-indigo-50 rounded-lg p-4 border border-indigo-200 cursor-pointer hover:bg-indigo-100 transition-colors" onClick={() => window.location.href = '/examples/insight-formats/market-regime'}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">🔄</span>
                <h3 className="font-semibold text-indigo-900">MarketRegimeFormat</h3>
              </div>
              <p className="text-sm text-indigo-800 mb-2">Asset behavior in different market conditions</p>
              <p className="text-xs text-indigo-600">Use: "during bull/bear", "when rates rise", regime analysis</p>
            </div>

            <div className="bg-cyan-50 rounded-lg p-4 border border-cyan-200 cursor-pointer hover:bg-cyan-100 transition-colors" onClick={() => window.location.href = '/examples/insight-formats/factor-analysis'}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">🧬</span>
                <h3 className="font-semibold text-cyan-900">FactorAnalysisFormat</h3>
              </div>
              <p className="text-sm text-cyan-800 mb-2">Factor discovery with statistical evidence</p>
              <p className="text-xs text-cyan-600">Use: correlation, factor exposure, performance drivers</p>
            </div>

            <div className="bg-orange-50 rounded-lg p-4 border border-orange-200 cursor-pointer hover:bg-orange-100 transition-colors" onClick={() => window.location.href = '/examples/insight-formats/earnings-report'}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">📊</span>
                <h3 className="font-semibold text-orange-900">EarningsReportFormat</h3>
              </div>
              <p className="text-sm text-orange-800 mb-2">Earnings style with financial highlights</p>
              <p className="text-xs text-orange-600">Use: fundamental analysis, earnings, financial metrics</p>
            </div>

            <div className="bg-teal-50 rounded-lg p-4 border border-teal-200 cursor-pointer hover:bg-teal-100 transition-colors" onClick={() => window.location.href = '/examples/insight-formats/trading-desk'}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">📺</span>
                <h3 className="font-semibold text-teal-900">TradingDeskFormat</h3>
              </div>
              <p className="text-sm text-teal-800 mb-2">Trading desk commentary with actionable levels</p>
              <p className="text-xs text-teal-600">Use: technical analysis, momentum, short-term moves</p>
            </div>

            <div className="bg-pink-50 rounded-lg p-4 border border-pink-200 cursor-pointer hover:bg-pink-100 transition-colors" onClick={() => window.location.href = '/examples/insight-formats/portfolio-review'}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">📋</span>
                <h3 className="font-semibold text-pink-900">PortfolioReviewFormat</h3>
              </div>
              <p className="text-sm text-pink-800 mb-2">Professional portfolio review for decisions</p>
              <p className="text-xs text-pink-600">Use: complex multi-asset, allocation decisions</p>
            </div>
          </div>

          {/* Column 3 - Specialized & Advanced */}
          <div className="space-y-4 overflow-auto">
            <div className="bg-emerald-50 rounded-lg p-4 border border-emerald-200 cursor-pointer hover:bg-emerald-100 transition-colors" onClick={() => window.location.href = '/examples/insight-formats/sports-trading'}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">🎙️</span>
                <h3 className="font-semibold text-emerald-900">SportsTradingFormat</h3>
              </div>
              <p className="text-sm text-emerald-800 mb-2">Sports commentary for market momentum</p>
              <p className="text-xs text-emerald-600">Use: momentum, streaks, winning/losing performance</p>
            </div>

            <div className="bg-rose-50 rounded-lg p-4 border border-rose-200 cursor-pointer hover:bg-rose-100 transition-colors" onClick={() => window.location.href = '/examples/insight-formats/risk-dashboard'}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">⚠️</span>
                <h3 className="font-semibold text-rose-900">RiskDashboardFormat</h3>
              </div>
              <p className="text-sm text-rose-800 mb-2">Comprehensive risk monitoring dashboard</p>
              <p className="text-xs text-rose-600">Use: VaR, drawdown, risk analysis, portfolio health</p>
            </div>

            <div className="bg-violet-50 rounded-lg p-4 border border-violet-200 cursor-pointer hover:bg-violet-100 transition-colors" onClick={() => window.location.href = '/examples/insight-formats/sector-rotation'}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">🔄</span>
                <h3 className="font-semibold text-violet-900">SectorRotationFormat</h3>
              </div>
              <p className="text-sm text-violet-800 mb-2">Sector rotation story with winners/losers</p>
              <p className="text-xs text-violet-600">Use: sector performance, rotation, style analysis</p>
            </div>

            <div className="bg-amber-50 rounded-lg p-4 border border-amber-200 cursor-pointer hover:bg-amber-100 transition-colors" onClick={() => window.location.href = '/examples/insight-formats/valuation-story'}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">💰</span>
                <h3 className="font-semibold text-amber-900">ValuationStoryFormat</h3>
              </div>
              <p className="text-sm text-amber-800 mb-2">Fair value assessment and valuation narrative</p>
              <p className="text-xs text-amber-600">Use: valuation, intrinsic value, cheap/expensive</p>
            </div>

            <div className="bg-slate-50 rounded-lg p-4 border border-slate-200 cursor-pointer hover:bg-slate-100 transition-colors" onClick={() => window.location.href = '/examples/insight-formats/catalyst-timeline'}>
              <div className="flex items-center gap-2 mb-2">
                <span className="text-lg">📅</span>
                <h3 className="font-semibold text-slate-900">CatalystTimelineFormat</h3>
              </div>
              <p className="text-sm text-slate-800 mb-2">Chronological investment catalysts and events</p>
              <p className="text-xs text-slate-600">Use: "when", catalyst analysis, event-driven</p>
            </div>
          </div>
        </div>

        {/* Bottom Summary - Fixed Height */}
        <div className="mt-6 bg-white rounded-lg shadow-sm border border-gray-200 p-4 flex-shrink-0">
          <div className="grid grid-cols-3 gap-4 text-center">
            <div>
              <div className="font-semibold text-gray-900">15 Formats</div>
              <div className="text-sm text-gray-600">Financial-focused presentations</div>
            </div>
            <div>
              <div className="font-semibold text-gray-900">LLM Selection</div>
              <div className="text-sm text-gray-600">Automatic format based on question</div>
            </div>
            <div>
              <div className="font-semibold text-gray-900">Same Data</div>
              <div className="text-sm text-gray-600">Different narrative styles</div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}