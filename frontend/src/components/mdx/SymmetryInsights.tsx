'use client';

import React from 'react';

interface SymmetryInsightsProps {
  mostSymmetric: string[];
  leastSymmetric: string[];
  portfolioBalance: number;
  recommendations: string[];
}

export function SymmetryInsights({
  mostSymmetric,
  leastSymmetric,
  portfolioBalance,
  recommendations
}: SymmetryInsightsProps) {
  const getBalanceAssessment = () => {
    if (portfolioBalance >= 0.9 && portfolioBalance <= 1.1) {
      return {
        level: 'Excellent',
        color: 'emerald',
        description: 'Portfolio shows excellent up/down day balance'
      };
    } else if (portfolioBalance >= 0.8 && portfolioBalance <= 1.2) {
      return {
        level: 'Good',
        color: 'blue',
        description: 'Portfolio maintains good symmetry overall'
      };
    } else {
      return {
        level: 'Poor',
        color: 'red',
        description: 'Portfolio shows significant asymmetric bias'
      };
    }
  };

  const assessment = getBalanceAssessment();

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">
          Symmetry Analysis Insights
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          Key findings and trading implications
        </p>
      </div>
      
      <div className="p-6 space-y-6">
        {/* Portfolio Balance Score */}
        <div className={`p-4 rounded-xl border ${
          assessment.color === 'emerald' ? 'bg-emerald-50 border-emerald-200' :
          assessment.color === 'blue' ? 'bg-blue-50 border-blue-200' :
          'bg-red-50 border-red-200'
        }`}>
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Portfolio Symmetry Score</span>
            <span className={`text-lg font-bold ${
              assessment.color === 'emerald' ? 'text-emerald-600' :
              assessment.color === 'blue' ? 'text-blue-600' :
              'text-red-600'
            }`}>
              {portfolioBalance.toFixed(2)} ({assessment.level})
            </span>
          </div>
          <p className={`text-sm ${
            assessment.color === 'emerald' ? 'text-emerald-700' :
            assessment.color === 'blue' ? 'text-blue-700' :
            'text-red-700'
          }`}>
            {assessment.description}
          </p>
        </div>

        {/* Key Findings */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Most Symmetric */}
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 className="text-sm font-semibold text-green-800 mb-2">Most Symmetric Positions</h4>
            <div className="space-y-1">
              {mostSymmetric.map((symbol, index) => (
                <div key={symbol} className="flex items-center justify-between">
                  <span className="text-sm text-green-700 font-medium">{symbol}</span>
                  <span className="text-xs text-green-600">#{index + 1}</span>
                </div>
              ))}
            </div>
            <p className="text-xs text-green-600 mt-2">
              These positions show balanced volatility patterns
            </p>
          </div>

          {/* Least Symmetric */}
          <div className="p-4 bg-red-50 rounded-lg border border-red-200">
            <h4 className="text-sm font-semibold text-red-800 mb-2">Least Symmetric Positions</h4>
            <div className="space-y-1">
              {leastSymmetric.map((symbol, index) => (
                <div key={symbol} className="flex items-center justify-between">
                  <span className="text-sm text-red-700 font-medium">{symbol}</span>
                  <span className="text-xs text-red-600">Risk</span>
                </div>
              ))}
            </div>
            <p className="text-xs text-red-600 mt-2">
              These positions show biased directional patterns
            </p>
          </div>
        </div>

        {/* Trading Recommendations */}
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="text-sm font-semibold text-blue-800 mb-3">Trading Recommendations</h4>
          <ul className="space-y-2">
            {recommendations.map((rec, index) => (
              <li key={index} className="flex items-start space-x-2">
                <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                <span className="text-sm text-blue-700">{rec}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Risk Assessment */}
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h4 className="text-sm font-semibold text-gray-800 mb-2">Risk Assessment</h4>
          <div className="text-sm text-gray-700 space-y-1">
            <p>
              <strong>Symmetric positions</strong> typically offer more predictable volatility patterns 
              and may provide better risk-adjusted returns.
            </p>
            <p>
              <strong>Asymmetric positions</strong> may indicate trending bias or structural changes 
              that require closer monitoring and position sizing adjustments.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}