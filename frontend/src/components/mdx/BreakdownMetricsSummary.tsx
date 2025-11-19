'use client';

import React from 'react';

interface BreakdownMetricsSummaryProps {
  totalBreakdowns: number;
  successRate: number;
  avgRecoveryTime: number;
  period: string;
}

export function BreakdownMetricsSummary({
  totalBreakdowns,
  successRate,
  avgRecoveryTime,
  period
}: BreakdownMetricsSummaryProps) {
  const failureRate = 100 - successRate;

  return (
    <div className="w-full bg-gradient-to-br from-red-50 to-orange-50 rounded-2xl border border-red-200 p-6 mb-6">
      <div className="mb-4">
        <h2 className="text-2xl font-light text-gray-900">
          Breakdown Analysis Summary
        </h2>
        <p className="text-sm text-gray-600 mt-1">
          Key metrics for failed breakdowns over {period}
        </p>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {/* Total Breakdowns */}
        <div className="text-center">
          <div className="text-4xl font-bold text-red-600 mb-2">
            {totalBreakdowns}
          </div>
          <div className="text-sm text-gray-600 mb-1">Total Breakdowns</div>
          <div className="text-xs text-gray-500">Support failures detected</div>
        </div>

        {/* Failure Rate */}
        <div className="text-center">
          <div className="text-4xl font-bold text-red-600 mb-2">
            {failureRate.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600 mb-1">Failure Rate</div>
          <div className="text-xs text-gray-500">Breakdowns that failed</div>
        </div>

        {/* Success Rate */}
        <div className="text-center">
          <div className={`text-4xl font-bold mb-2 ${
            successRate < 20 ? 'text-red-600' : 
            successRate < 40 ? 'text-orange-600' : 'text-green-600'
          }`}>
            {successRate.toFixed(1)}%
          </div>
          <div className="text-sm text-gray-600 mb-1">Recovery Rate</div>
          <div className="text-xs text-gray-500">Successful recoveries</div>
        </div>

        {/* Average Recovery Time */}
        <div className="text-center">
          <div className="text-4xl font-bold text-blue-600 mb-2">
            {avgRecoveryTime.toFixed(1)}
          </div>
          <div className="text-sm text-gray-600 mb-1">Avg Recovery</div>
          <div className="text-xs text-gray-500">Days to recovery</div>
        </div>
      </div>

      {/* Risk Assessment */}
      <div className={`mt-6 p-4 rounded-xl ${
        failureRate > 80 ? 'bg-red-100 border border-red-200' :
        failureRate > 60 ? 'bg-orange-100 border border-orange-200' :
        'bg-yellow-100 border border-yellow-200'
      }`}>
        <div className={`text-sm font-medium mb-2 ${
          failureRate > 80 ? 'text-red-800' :
          failureRate > 60 ? 'text-orange-800' :
          'text-yellow-800'
        }`}>
          Risk Assessment
        </div>
        <div className={`text-sm ${
          failureRate > 80 ? 'text-red-700' :
          failureRate > 60 ? 'text-orange-700' :
          'text-yellow-700'
        }`}>
          {failureRate > 80 ? 
            'High Risk: Extremely high breakdown failure rate indicates severe market stress or poor support identification.' :
            failureRate > 60 ?
            'Moderate Risk: Elevated breakdown failure rate suggests challenging market conditions.' :
            'Normal Risk: Breakdown failure rate within typical range for current market conditions.'
          }
        </div>
      </div>
    </div>
  );
}