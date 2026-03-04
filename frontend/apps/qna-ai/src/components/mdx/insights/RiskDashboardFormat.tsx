'use client';

import React from 'react';

interface RiskDashboardData {
  overallRisk: {
    level: string;
    score: number;
    trend: string;
    description: string;
  };
  exposures: Array<{
    category: string;
    exposure: number;
    limit: number;
    status: 'safe' | 'caution' | 'breach';
  }>;
  scenarios: Array<{
    scenario: string;
    probability: number;
    impact: string;
    drawdown: number;
  }>;
  trends: Array<{
    metric: string;
    current: number;
    previous: number;
    direction: string;
  }>;
  alerts: Array<{
    priority: 'high' | 'medium' | 'low';
    message: string;
    action: string;
    deadline: string;
  }>;
}

interface RiskDashboardFormatProps {
  data: RiskDashboardData;
  title?: string;
}

export function RiskDashboardFormat({
  data,
  title = "Risk Assessment"
}: RiskDashboardFormatProps) {
  const { overallRisk, exposures, scenarios, trends, alerts } = data;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'safe': return 'bg-green-50 border-green-200 text-green-800';
      case 'caution': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'breach': return 'bg-red-50 border-red-200 text-red-800';
      default: return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'high': return 'bg-red-50 border-red-200 text-red-800';
      case 'medium': return 'bg-yellow-50 border-yellow-200 text-yellow-800';
      case 'low': return 'bg-blue-50 border-blue-200 text-blue-800';
      default: return 'bg-gray-50 border-gray-200 text-gray-800';
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-500 mt-1">Portfolio risk monitoring and analysis</p>
      </div>

      <div className="p-6 space-y-6">
        {/* Overall Risk Summary */}
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="text-sm font-semibold text-blue-800 mb-2">Risk Level Assessment</h4>
          <div className="flex justify-between items-center">
            <div>
              <span className="text-lg font-bold text-blue-900">{overallRisk.level}</span>
              <span className="text-sm text-blue-700 ml-2">Score: {overallRisk.score}/100</span>
            </div>
            <div className="text-sm text-blue-700">Trend: {overallRisk.trend}</div>
          </div>
          <p className="text-sm text-blue-700 mt-2">{overallRisk.description}</p>
        </div>

        {/* Risk Exposures */}
        <div>
          <h4 className="text-sm font-semibold text-gray-800 mb-3">Risk Exposures</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {exposures.map((exposure, index) => (
              <div key={index} className={`rounded-lg p-4 border ${getStatusColor(exposure.status)}`}>
                <div className="flex justify-between items-center mb-2">
                  <h5 className="font-medium text-sm">{exposure.category}</h5>
                  <span className="text-xs uppercase font-medium">{exposure.status}</span>
                </div>
                <div className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span>Current:</span>
                    <span className="font-medium">{exposure.exposure.toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between text-sm">
                    <span>Limit:</span>
                    <span className="font-medium">{exposure.limit.toFixed(1)}%</span>
                  </div>
                  <div className="w-full bg-white/50 rounded-full h-2 mt-2">
                    <div 
                      className={`h-2 rounded-full ${
                        exposure.status === 'safe' ? 'bg-green-500' :
                        exposure.status === 'caution' ? 'bg-yellow-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${Math.min((exposure.exposure / exposure.limit) * 100, 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Stress Test Scenarios */}
        <div>
          <h4 className="text-sm font-semibold text-gray-800 mb-3">Stress Test Results</h4>
          <div className="overflow-hidden rounded-lg border border-gray-200">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Scenario</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Probability</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Max Drawdown</th>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Impact</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {scenarios.map((scenario, index) => (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-4 py-3 text-sm font-medium text-gray-900">{scenario.scenario}</td>
                    <td className="px-4 py-3 text-center text-sm text-gray-900">{scenario.probability}%</td>
                    <td className="px-4 py-3 text-center text-sm font-semibold text-red-600">
                      {scenario.drawdown}%
                    </td>
                    <td className="px-4 py-3 text-sm text-gray-600">{scenario.impact}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Analysis Summary */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-4 bg-green-50 rounded-lg border border-green-200">
            <h4 className="text-sm font-semibold text-green-800 mb-3">Risk Metrics Trend</h4>
            <ul className="space-y-2">
              {trends.map((trend, index) => (
                <li key={index} className="flex justify-between items-center">
                  <span className="text-sm text-green-700">{trend.metric}</span>
                  <div className="text-right">
                    <div className="text-sm font-medium text-green-900">{trend.current.toFixed(2)}</div>
                    <div className="text-xs text-green-600">
                      {trend.direction === 'up' ? '↑' : trend.direction === 'down' ? '↓' : '→'} 
                      {trend.previous.toFixed(2)}
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          </div>

          <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
            <h4 className="text-sm font-semibold text-orange-800 mb-3">Active Alerts</h4>
            <ul className="space-y-2">
              {alerts.map((alert, index) => (
                <li key={index} className="text-sm">
                  <div className="flex items-center gap-2 mb-1">
                    <span className={`px-2 py-0.5 rounded text-xs uppercase font-medium ${getPriorityColor(alert.priority)}`}>
                      {alert.priority}
                    </span>
                    <span className="text-xs text-orange-600">{alert.deadline}</span>
                  </div>
                  <div className="text-orange-700">{alert.message}</div>
                  <div className="text-xs text-orange-600 mt-1">Action: {alert.action}</div>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Risk Considerations */}
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h4 className="text-sm font-semibold text-gray-800 mb-2">Risk Assessment Notes</h4>
          <div className="text-sm text-gray-700">
            <p className="mb-2">
              <strong>Methodology:</strong> Risk metrics calculated based on historical volatility and correlation analysis over rolling 252-day period.
            </p>
            <p>
              <strong>Limitations:</strong> Past performance and correlations may not predict future risk. Stress test scenarios are hypothetical and may not capture all risk factors.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}