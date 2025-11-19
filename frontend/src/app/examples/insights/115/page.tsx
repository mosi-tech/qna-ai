'use client';

import PositionSymmetryCard from '@/components/insights/PositionSymmetryCard';
import SymmetryRankingTable from '@/components/insights/SymmetryRankingTable';
import SymmetryMetricsPanel from '@/components/insights/SymmetryMetricsPanel';

export default function PositionSymmetryAnalysis() {
  // Mock data for position symmetry analysis
  const portfolioData = {
    totalPositions: 12,
    avgSymmetryScore: 0.67,
    mostSymmetricPosition: "KO (Coca-Cola)",
    leastSymmetricPosition: "NVDA (NVIDIA)",
    symmetricPositions: 5,
    asymmetricPositions: 3,
    portfolioUpDays: 142,
    portfolioDownDays: 110,
    overallBalance: 0.13
  };

  const positionData = [
    {
      symbol: "KO",
      name: "The Coca-Cola Company",
      symmetryScore: 0.94,
      upDays: 126,
      downDays: 124,
      upDayAvg: 1.24,
      downDayAvg: -1.18,
      totalDays: 252,
      volatility: 14.2,
      beta: 0.58
    },
    {
      symbol: "JNJ",
      name: "Johnson & Johnson", 
      symmetryScore: 0.89,
      upDays: 128,
      downDays: 122,
      upDayAvg: 1.31,
      downDayAvg: -1.42,
      totalDays: 252,
      volatility: 12.7,
      beta: 0.71
    },
    {
      symbol: "PG",
      name: "Procter & Gamble Co",
      symmetryScore: 0.85,
      upDays: 131,
      downDays: 119,
      upDayAvg: 1.18,
      downDayAvg: -1.29,
      totalDays: 252,
      volatility: 15.8,
      beta: 0.44
    },
    {
      symbol: "WMT",
      name: "Walmart Inc",
      symmetryScore: 0.78,
      upDays: 135,
      downDays: 115,
      upDayAvg: 1.42,
      downDayAvg: -1.67,
      totalDays: 252,
      volatility: 18.3,
      beta: 0.52
    },
    {
      symbol: "HD",
      name: "The Home Depot Inc",
      symmetryScore: 0.72,
      upDays: 138,
      downDays: 112,
      upDayAvg: 1.87,
      downDayAvg: -2.18,
      totalDays: 252,
      volatility: 22.1,
      beta: 1.05
    },
    {
      symbol: "MSFT",
      name: "Microsoft Corporation",
      symmetryScore: 0.64,
      upDays: 142,
      downDays: 108,
      upDayAvg: 2.14,
      downDayAvg: -2.67,
      totalDays: 252,
      volatility: 28.4,
      beta: 0.89
    },
    {
      symbol: "AAPL",
      name: "Apple Inc",
      symmetryScore: 0.58,
      upDays: 145,
      downDays: 105,
      upDayAvg: 2.31,
      downDayAvg: -2.94,
      totalDays: 252,
      volatility: 31.7,
      beta: 1.24
    },
    {
      symbol: "AMZN",
      name: "Amazon.com Inc",
      symmetryScore: 0.52,
      upDays: 148,
      downDays: 102,
      upDayAvg: 2.89,
      downDayAvg: -3.67,
      totalDays: 252,
      volatility: 35.2,
      beta: 1.33
    },
    {
      symbol: "TSLA",
      name: "Tesla Inc",
      symmetryScore: 0.41,
      upDays: 156,
      downDays: 94,
      upDayAvg: 4.12,
      downDayAvg: -5.87,
      totalDays: 252,
      volatility: 52.8,
      beta: 2.01
    },
    {
      symbol: "NVDA",
      name: "NVIDIA Corporation",
      symmetryScore: 0.34,
      upDays: 162,
      downDays: 88,
      upDayAvg: 5.24,
      downDayAvg: -7.41,
      totalDays: 252,
      volatility: 68.3,
      beta: 1.67
    }
  ];

  const handleApprove = () => {
    console.log('Analysis approved');
  };

  const handleDisapprove = () => {
    console.log('Analysis disapproved');
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        
        {/* Page Header */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h1 className="text-2xl font-semibold text-gray-900 mb-2">
            Position Symmetry Analysis
          </h1>
          <p className="text-gray-600">
            Analysis of which positions display the most symmetric up vs down day patterns in your portfolio
          </p>
        </div>

        {/* Portfolio Overview */}
        <SymmetryMetricsPanel 
          data={portfolioData}
          onApprove={handleApprove}
          onDisapprove={handleDisapprove}
        />

        {/* Top Symmetric Positions Cards */}
        <div>
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Most Symmetric Positions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {positionData.slice(0, 3).map((position) => (
              <PositionSymmetryCard
                key={position.symbol}
                data={position}
                variant="detailed"
                onApprove={handleApprove}
                onDisapprove={handleDisapprove}
              />
            ))}
          </div>
        </div>

        {/* Complete Rankings Table */}
        <SymmetryRankingTable 
          data={positionData}
          onApprove={handleApprove}
          onDisapprove={handleDisapprove}
        />

        {/* Key Insights */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Key Insights</h2>
          <div className="space-y-4">
            <div className="border-l-4 border-green-300 pl-4">
              <h3 className="font-medium text-gray-900">Most Balanced Positions</h3>
              <p className="text-gray-700 text-sm">
                Defensive stocks (KO, JNJ, PG) show the highest symmetry scores (85-94%), indicating 
                consistent risk-reward profiles with balanced up and down day patterns.
              </p>
            </div>
            <div className="border-l-4 border-red-300 pl-4">
              <h3 className="font-medium text-gray-900">Asymmetric Positions</h3>
              <p className="text-gray-700 text-sm">
                Growth/tech stocks (TSLA, NVDA) display significant asymmetry with more frequent up days 
                but larger down day losses, indicating higher risk-reward volatility.
              </p>
            </div>
            <div className="border-l-4 border-blue-300 pl-4">
              <h3 className="font-medium text-gray-900">Portfolio Impact</h3>
              <p className="text-gray-700 text-sm">
                Overall portfolio shows moderate symmetry (67%) with a slight bullish bias. 
                Consider rebalancing towards more symmetric positions for risk reduction.
              </p>
            </div>
          </div>
          
          <div className="flex gap-2 mt-6 pt-4 border-t border-gray-100">
            <button
              onClick={handleApprove}
              className="px-4 py-2 bg-green-50 text-green-700 rounded-md hover:bg-green-100 transition-colors text-sm font-medium"
            >
              Approve Analysis
            </button>
            <button
              onClick={handleDisapprove}
              className="px-4 py-2 bg-red-50 text-red-700 rounded-md hover:bg-red-100 transition-colors text-sm font-medium"
            >
              Disapprove Analysis
            </button>
          </div>
        </div>

      </div>
    </div>
  );
}