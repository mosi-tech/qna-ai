'use client';

import React from 'react';

interface AnalysisInsightsProps {
  summary: string;
  keyFindings: string[];
  recommendations: string[];
  metrics?: Record<string, any>;
}

export function AnalysisInsights({
  summary,
  keyFindings,
  recommendations,
  metrics = {}
}: AnalysisInsightsProps) {
  // Extract key metrics for display
  const displayMetrics = Object.entries(metrics).filter(([key, value]) => 
    value !== undefined && value !== null && value !== ''
  );

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">
          Analysis Insights
        </h3>
        <p className="text-sm text-gray-500 mt-1">
          Key findings and recommendations
        </p>
      </div>
      
      <div className="p-6 space-y-6">
        {/* Summary */}
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="text-sm font-semibold text-blue-800 mb-2">Executive Summary</h4>
          <p className="text-sm text-blue-700">{summary}</p>
        </div>

        {/* Key Metrics (if provided) */}
        {displayMetrics.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {displayMetrics.map(([key, value]) => (
              <div key={key} className="text-center p-3 bg-gray-50 rounded-lg">
                <div className="text-lg font-bold text-gray-900">
                  {typeof value === 'number' ? 
                    (value < 1 && value > 0 ? value.toFixed(2) : value) : 
                    String(value)
                  }
                </div>
                <div className="text-xs text-gray-600 capitalize">
                  {key.replace(/([A-Z])/g, ' $1').toLowerCase()}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Key Findings */}
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 className="text-sm font-semibold text-green-800 mb-3">Key Findings</h4>
            <ul className="space-y-2">
              {keyFindings.map((finding, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span className="text-sm text-green-700">{finding}</span>
                </li>
              ))}
            </ul>
          </div>

          {/* Recommendations */}
          <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
            <h4 className="text-sm font-semibold text-orange-800 mb-3">Recommendations</h4>
            <ul className="space-y-2">
              {recommendations.map((rec, index) => (
                <li key={index} className="flex items-start space-x-2">
                  <div className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                  <span className="text-sm text-orange-700">{rec}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Risk Assessment */}
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h4 className="text-sm font-semibold text-gray-800 mb-2">Risk Considerations</h4>
          <div className="text-sm text-gray-700">
            <p className="mb-2">
              <strong>Data Quality:</strong> Analysis is based on historical patterns which may not predict future performance.
            </p>
            <p>
              <strong>Market Conditions:</strong> Current market regime may affect the relevance of these insights for trading decisions.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}