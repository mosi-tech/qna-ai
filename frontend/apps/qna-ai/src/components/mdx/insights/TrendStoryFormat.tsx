'use client';

import React from 'react';

interface TrendStoryData {
  timeframe: string;
  overallTrend: {
    direction: string;
    strength: number;
    description: string;
  };
  threeActs: {
    beginning: string;
    middle: string;
    current: string;
  };
  inflectionPoints: Array<{
    date: string;
    event: string;
    impact: string;
  }>;
  nextChapter: {
    outlook: string;
    keyCatalysts: string[];
    timeframe: string;
  };
}

interface TrendStoryFormatProps {
  data: TrendStoryData;
  title?: string;
}

export function TrendStoryFormat({
  data,
  title = "Investment Trend Story"
}: TrendStoryFormatProps) {
  const { timeframe, overallTrend, threeActs, inflectionPoints, nextChapter } = data;

  const getDirectionColor = (direction: string) => {
    const dir = direction.toLowerCase();
    if (dir.includes('up') || dir.includes('bull') || dir.includes('positive')) return 'text-green-600 bg-green-100';
    if (dir.includes('down') || dir.includes('bear') || dir.includes('negative')) return 'text-red-600 bg-red-100';
    return 'text-yellow-600 bg-yellow-100';
  };

  const getStrengthBar = (strength: number) => {
    return (
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div 
          className={`h-2 rounded-full ${
            strength >= 80 ? 'bg-green-500' :
            strength >= 60 ? 'bg-yellow-500' :
            strength >= 40 ? 'bg-orange-500' : 'bg-red-500'
          }`}
          style={{ width: `${strength}%` }}
        />
      </div>
    );
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 overflow-hidden">
      <div className="px-6 py-4 border-b border-gray-100">
        <h2 className="text-2xl font-bold text-gray-900">{title}</h2>
        <p className="text-sm text-gray-500 mt-1">Investment narrative over {timeframe}</p>
      </div>

      <div className="p-6">
        {/* Story Header */}
        <div className="mb-8">
          <div className="bg-gradient-to-r from-blue-50 to-blue-100 rounded-xl p-6 border-2 border-blue-200">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xl font-bold text-blue-900">Overall Trend Direction</h3>
              <span className={`px-3 py-1 rounded-full text-sm font-medium ${getDirectionColor(overallTrend.direction)}`}>
                {overallTrend.direction}
              </span>
            </div>
            
            <p className="text-blue-800 mb-4 text-lg">{overallTrend.description}</p>
            
            <div className="space-y-2">
              <div className="flex justify-between text-sm">
                <span className="text-blue-700">Trend Strength:</span>
                <span className="text-blue-900 font-semibold">{overallTrend.strength}/100</span>
              </div>
              {getStrengthBar(overallTrend.strength)}
            </div>
          </div>
        </div>

        {/* Three Act Structure */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">The Investment Story</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-gray-50 rounded-lg p-6 border border-gray-200">
              <div className="flex items-center gap-2 mb-3">
                <div className="bg-gray-300 rounded-full w-8 h-8 flex items-center justify-center text-gray-700 font-bold">1</div>
                <h4 className="font-semibold text-gray-900">Beginning</h4>
              </div>
              <p className="text-gray-700 text-sm">{threeActs.beginning}</p>
            </div>

            <div className="bg-yellow-50 rounded-lg p-6 border border-yellow-200">
              <div className="flex items-center gap-2 mb-3">
                <div className="bg-yellow-300 rounded-full w-8 h-8 flex items-center justify-center text-yellow-800 font-bold">2</div>
                <h4 className="font-semibold text-yellow-900">Middle</h4>
              </div>
              <p className="text-yellow-800 text-sm">{threeActs.middle}</p>
            </div>

            <div className="bg-blue-50 rounded-lg p-6 border border-blue-200">
              <div className="flex items-center gap-2 mb-3">
                <div className="bg-blue-300 rounded-full w-8 h-8 flex items-center justify-center text-blue-800 font-bold">3</div>
                <h4 className="font-semibold text-blue-900">Current State</h4>
              </div>
              <p className="text-blue-800 text-sm">{threeActs.current}</p>
            </div>
          </div>
        </div>

        {/* Trend Strength Meter */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Trend Sustainability</h3>
          <div className="bg-gradient-to-r from-green-50 to-green-100 rounded-xl p-6 border-2 border-green-200">
            <div className="flex items-center justify-between mb-4">
              <span className="text-green-800 font-medium">Strength Assessment</span>
              <span className="text-green-900 font-bold text-lg">{overallTrend.strength}%</span>
            </div>
            
            <div className="space-y-2 mb-4">
              {getStrengthBar(overallTrend.strength)}
            </div>
            
            <div className="grid grid-cols-4 gap-2 text-xs text-center">
              <span className={overallTrend.strength <= 25 ? 'font-bold text-red-700' : 'text-gray-600'}>Weak</span>
              <span className={overallTrend.strength > 25 && overallTrend.strength <= 50 ? 'font-bold text-orange-700' : 'text-gray-600'}>Moderate</span>
              <span className={overallTrend.strength > 50 && overallTrend.strength <= 75 ? 'font-bold text-yellow-700' : 'text-gray-600'}>Strong</span>
              <span className={overallTrend.strength > 75 ? 'font-bold text-green-700' : 'text-gray-600'}>Very Strong</span>
            </div>
          </div>
        </div>

        {/* Inflection Points Timeline */}
        <div className="mb-8">
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Key Turning Points</h3>
          <div className="space-y-4">
            {inflectionPoints.map((point, index) => (
              <div key={index} className="flex items-start gap-4 p-4 bg-purple-50 rounded-lg border border-purple-200">
                <div className="bg-purple-300 rounded-full w-8 h-8 flex items-center justify-center text-purple-900 font-bold flex-shrink-0">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-3 mb-1">
                    <span className="text-purple-900 font-semibold">{point.event}</span>
                    <span className="bg-purple-200 text-purple-800 px-2 py-0.5 rounded text-xs">{point.date}</span>
                  </div>
                  <p className="text-purple-800 text-sm">{point.impact}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Next Chapter Preview */}
        <div>
          <h3 className="text-xl font-semibold text-gray-900 mb-4">Next Chapter Preview</h3>
          <div className="bg-gradient-to-r from-indigo-50 to-indigo-100 rounded-xl p-6 border-2 border-indigo-200">
            <div className="flex items-center gap-3 mb-4">
              <div className="text-2xl">🔮</div>
              <h4 className="text-lg font-semibold text-indigo-900">What's Next ({nextChapter.timeframe})</h4>
            </div>
            
            <p className="text-indigo-800 mb-4 font-medium">{nextChapter.outlook}</p>
            
            <div>
              <h5 className="font-semibold text-indigo-900 mb-2">Key Catalysts to Watch</h5>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                {nextChapter.keyCatalysts.map((catalyst, index) => (
                  <div key={index} className="bg-white/50 rounded-lg p-3 border border-indigo-200">
                    <div className="flex items-center gap-2">
                      <span className="text-indigo-600">📍</span>
                      <p className="text-sm text-indigo-800">{catalyst}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}