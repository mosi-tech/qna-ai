'use client';

import React from 'react';

interface HeadToHeadData {
  competitor1: {
    name: string;
    metrics: Record<string, any>;
    performance: string;
    strengths: string[];
  };
  competitor2: {
    name: string;
    metrics: Record<string, any>;
    performance: string;
    strengths: string[];
  };
  winner: {
    name: string;
    margin: string;
    reason: string;
  };
  context: string;
  implications: string[];
}

interface HeadToHeadFormatProps {
  data: HeadToHeadData;
  title?: string;
}

export function HeadToHeadFormat({
  data,
  title = "Comparative Analysis"
}: HeadToHeadFormatProps) {
  const { competitor1, competitor2, winner, context, implications } = data;

  const isWinner = (name: string) => winner.name === name;

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-500 mt-1">Direct comparison analysis</p>
      </div>

      <div className="p-6 space-y-6">
        {/* Winner Summary */}
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <h4 className="text-sm font-semibold text-blue-800 mb-2">Analysis Result</h4>
          <div className="flex justify-between items-center">
            <div>
              <span className="text-lg font-bold text-blue-900">{winner.name}</span>
              <span className="text-sm text-blue-700 ml-2">outperforms by {winner.margin}</span>
            </div>
          </div>
          <p className="text-sm text-blue-700 mt-2">{winner.reason}</p>
        </div>

        {/* Context */}
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <h4 className="text-sm font-semibold text-gray-800 mb-2">Analysis Context</h4>
          <p className="text-sm text-gray-700">{context}</p>
        </div>

        {/* Detailed Comparison */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Competitor 1 */}
          <div className={`rounded-lg p-4 border ${
            isWinner(competitor1.name) 
              ? 'bg-green-50 border-green-200' 
              : 'bg-gray-50 border-gray-200'
          }`}>
            <div className="mb-4">
              <h4 className={`text-lg font-semibold ${
                isWinner(competitor1.name) ? 'text-green-800' : 'text-gray-800'
              }`}>
                {competitor1.name}
              </h4>
              <p className={`text-sm mt-1 ${
                isWinner(competitor1.name) ? 'text-green-600' : 'text-gray-600'
              }`}>
                {competitor1.performance}
              </p>
            </div>

            <div className="space-y-3">
              <div>
                <h5 className="text-sm font-semibold text-gray-800 mb-2">Key Metrics</h5>
                {Object.entries(competitor1.metrics).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-sm">
                    <span className="text-gray-600">{key}:</span>
                    <span className="font-medium text-gray-900">
                      {typeof value === 'number' ? value.toFixed(2) : value}
                    </span>
                  </div>
                ))}
              </div>

              <div>
                <h5 className="text-sm font-semibold text-gray-800 mb-2">Key Strengths</h5>
                <ul className="space-y-1">
                  {competitor1.strengths.map((strength, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <div className="w-1.5 h-1.5 bg-gray-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-sm text-gray-700">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>

          {/* Competitor 2 */}
          <div className={`rounded-lg p-4 border ${
            isWinner(competitor2.name) 
              ? 'bg-green-50 border-green-200' 
              : 'bg-gray-50 border-gray-200'
          }`}>
            <div className="mb-4">
              <h4 className={`text-lg font-semibold ${
                isWinner(competitor2.name) ? 'text-green-800' : 'text-gray-800'
              }`}>
                {competitor2.name}
              </h4>
              <p className={`text-sm mt-1 ${
                isWinner(competitor2.name) ? 'text-green-600' : 'text-gray-600'
              }`}>
                {competitor2.performance}
              </p>
            </div>

            <div className="space-y-3">
              <div>
                <h5 className="text-sm font-semibold text-gray-800 mb-2">Key Metrics</h5>
                {Object.entries(competitor2.metrics).map(([key, value]) => (
                  <div key={key} className="flex justify-between text-sm">
                    <span className="text-gray-600">{key}:</span>
                    <span className="font-medium text-gray-900">
                      {typeof value === 'number' ? value.toFixed(2) : value}
                    </span>
                  </div>
                ))}
              </div>

              <div>
                <h5 className="text-sm font-semibold text-gray-800 mb-2">Key Strengths</h5>
                <ul className="space-y-1">
                  {competitor2.strengths.map((strength, index) => (
                    <li key={index} className="flex items-start space-x-2">
                      <div className="w-1.5 h-1.5 bg-gray-500 rounded-full mt-2 flex-shrink-0"></div>
                      <span className="text-sm text-gray-700">{strength}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          </div>
        </div>

        {/* Metric Comparison Table */}
        <div>
          <h4 className="text-sm font-semibold text-gray-800 mb-3">Side-by-Side Comparison</h4>
          <div className="overflow-hidden rounded-lg border border-gray-200">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase">Metric</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">{competitor1.name}</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">{competitor2.name}</th>
                  <th className="px-4 py-3 text-center text-xs font-medium text-gray-500 uppercase">Better Performance</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {Object.keys(competitor1.metrics).map((metric) => {
                  const value1 = competitor1.metrics[metric];
                  const value2 = competitor2.metrics[metric];
                  
                  let advantage = 'Tie';
                  if (typeof value1 === 'number' && typeof value2 === 'number') {
                    advantage = value1 > value2 ? competitor1.name : value2 > value1 ? competitor2.name : 'Tie';
                  }

                  return (
                    <tr key={metric} className="hover:bg-gray-50">
                      <td className="px-4 py-3 text-sm font-medium text-gray-900">{metric}</td>
                      <td className="px-4 py-3 text-center text-sm text-gray-700">
                        {typeof value1 === 'number' ? value1.toFixed(2) : value1}
                      </td>
                      <td className="px-4 py-3 text-center text-sm text-gray-700">
                        {typeof value2 === 'number' ? value2.toFixed(2) : value2}
                      </td>
                      <td className="px-4 py-3 text-center text-sm text-gray-600">
                        {advantage === 'Tie' ? '—' : advantage}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>

        {/* Investment Implications */}
        <div className="p-4 bg-orange-50 rounded-lg border border-orange-200">
          <h4 className="text-sm font-semibold text-orange-800 mb-3">Investment Implications</h4>
          <ul className="space-y-2">
            {implications.map((implication, index) => (
              <li key={index} className="flex items-start space-x-2">
                <div className="w-1.5 h-1.5 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                <span className="text-sm text-orange-700">{implication}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}