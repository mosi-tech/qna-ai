'use client';

import React from 'react';

interface WeatherReportData {
  current: {
    condition: string;
    temperature: string;
    description: string;
    visibility: string;
  };
  forecast: Array<{
    area: string;
    condition: string;
    probability: number;
    description: string;
  }>;
  alerts: Array<{
    type: 'storm' | 'calm' | 'change';
    severity: string;
    description: string;
    timing: string;
  }>;
  patterns: {
    seasonal: string[];
    cyclical: string[];
    anomalies: string[];
  };
  outlook: {
    trend: string;
    confidence: number;
    changingFactors: string[];
  };
}

interface WeatherReportFormatProps {
  data: WeatherReportData;
  title?: string;
}

export function WeatherReportFormat({
  data,
  title = "Market Conditions Analysis"
}: WeatherReportFormatProps) {
  const { current, forecast, alerts, patterns, outlook } = data;

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
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
        <p className="text-sm text-gray-500 mt-1">Current market environment assessment</p>
      </div>

      <div className="p-6 space-y-6">
        {/* Current Market Conditions */}
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="text-sm font-semibold text-blue-800 mb-2">Current Market Environment</h4>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <div className="text-lg font-bold text-blue-900">{current.condition}</div>
              <div className="text-sm text-blue-700">{current.description}</div>
            </div>
            <div>
              <div className="text-sm text-blue-600">Volatility Level</div>
              <div className="font-semibold text-blue-900">{current.temperature}</div>
            </div>
          </div>
        </div>

        {/* Market Segment Outlook */}
        <div>
          <h4 className="text-sm font-semibold text-gray-800 mb-3">Sector Outlook</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {forecast.map((segment, index) => (
              <div key={index} className="p-4 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex justify-between items-center mb-2">
                  <h5 className="font-medium text-gray-900">{segment.area}</h5>
                  <span className="text-sm text-gray-600">{segment.probability}%</span>
                </div>
                <div className="text-sm font-medium text-gray-800 mb-1">{segment.condition}</div>
                <p className="text-sm text-gray-600">{segment.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Market Alerts */}
        <div>
          <h4 className="text-sm font-semibold text-gray-800 mb-3">Market Alerts</h4>
          <div className="space-y-3">
            {alerts.map((alert, index) => (
              <div key={index} className={`rounded-lg p-4 border ${getSeverityColor(alert.severity)}`}>
                <div className="flex justify-between items-start mb-2">
                  <div>
                    <span className="font-medium text-sm uppercase">{alert.type} Alert</span>
                    <span className="text-xs ml-2 opacity-75">({alert.severity} severity)</span>
                  </div>
                  <span className="text-xs">{alert.timing}</span>
                </div>
                <p className="text-sm">{alert.description}</p>
              </div>
            ))}
          </div>
        </div>

        {/* Market Patterns */}
        <div>
          <h4 className="text-sm font-semibold text-gray-800 mb-3">Observed Market Patterns</h4>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="p-4 bg-green-50 rounded-lg border border-green-200">
              <h5 className="text-sm font-semibold text-green-800 mb-3">Seasonal Trends</h5>
              <ul className="space-y-2">
                {patterns.seasonal.map((pattern, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-sm text-green-700">{pattern}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h5 className="text-sm font-semibold text-blue-800 mb-3">Cyclical Patterns</h5>
              <ul className="space-y-2">
                {patterns.cyclical.map((pattern, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <div className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-sm text-blue-700">{pattern}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
              <h5 className="text-sm font-semibold text-orange-800 mb-3">Market Anomalies</h5>
              <ul className="space-y-2">
                {patterns.anomalies.map((anomaly, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <div className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                    <span className="text-sm text-orange-700">{anomaly}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>

        {/* Market Outlook */}
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h4 className="text-sm font-semibold text-gray-800 mb-2">Market Outlook</h4>
          <div className="mb-3">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm text-gray-700">Expected Trend</span>
              <span className="text-sm font-medium text-gray-900">Confidence: {outlook.confidence}%</span>
            </div>
            <p className="text-sm text-gray-700">{outlook.trend}</p>
          </div>
          
          <div>
            <h5 className="text-sm font-semibold text-gray-800 mb-2">Key Factors to Monitor</h5>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
              {outlook.changingFactors.map((factor, index) => (
                <div key={index} className="text-sm text-gray-700 p-2 bg-white rounded border">
                  {factor}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}