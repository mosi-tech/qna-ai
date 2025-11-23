'use client';

import { useState } from 'react';
import Layout7 from '@/components/insights/layout/Layout7';
import SummaryConclusion from '@/components/insights/SummaryConclusion';
import Section from '@/components/insights/Section';
import { getRandomComponentsForLayout } from '@/components/insights/layout/utils/layout-randomizer';

export default function Layout7Demo() {
  const layout7Positions = ['top7', 'bottomLeft7', 'bottomCenter7', 'bottomRight7'];
  const [randomComponents, setRandomComponents] = useState<Record<string, React.ReactNode>>({});
  const [useRandom, setUseRandom] = useState(false);

  const generateRandomLayout = () => {
    const newComponents = getRandomComponentsForLayout(layout7Positions);
    setRandomComponents(newComponents);
    setUseRandom(true);
  };

  const resetToOriginal = () => {
    setUseRandom(false);
  };

  const originalComponents = {
    top7: (
      <SummaryConclusion
        title="Market Overview & Technical Summary"
        keyFindings={[
          "Strong bullish momentum across all major indices with RSI readings above 60",
          "Technology sector showing exceptional relative strength with +32.1% quarterly gains",
          "VIX remains elevated at 18.4, suggesting continued market uncertainty despite gains",
          "Bond yields rising to 4.3% creating headwinds for growth stocks going forward"
        ]}
        conclusion="Technical indicators suggest continued upward momentum in the near term, supported by strong earnings and improving economic data. However, elevated volatility and rising yields warrant caution. Recommend maintaining current equity allocation while monitoring key resistance levels."
        nextSteps={[
          "Monitor S&P 500 resistance at 4,800 level for potential breakout",
          "Watch 10-year Treasury yield for moves above 4.5% threshold",
          "Track technology sector for signs of momentum exhaustion"
        ]}
        confidence="medium"
      />
    ),
    bottomLeft7: (
      <Section title="S&P 500 Price Action">
        <div className="h-full flex flex-col">
          {/* Line chart placeholder */}
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-3">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-700 mb-2">Price Chart</div>
              <div className="text-sm text-gray-500 mb-3">S&P 500 • 6 Months</div>
              <div className="bg-white p-3 rounded shadow-sm text-xs">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-blue-600">Current:</span>
                    <span className="font-medium">4,742</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-green-600">Support:</span>
                    <span className="font-medium">4,650</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-red-600">Resistance:</span>
                    <span className="font-medium">4,800</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Technical indicators */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-green-50 p-2 rounded">
              <div className="font-medium text-green-800">RSI (14)</div>
              <div className="text-green-700">62.3</div>
            </div>
            <div className="bg-blue-50 p-2 rounded">
              <div className="font-medium text-blue-800">MACD</div>
              <div className="text-blue-700">Bullish</div>
            </div>
          </div>
        </div>
      </Section>
    ),
    bottomCenter7: (
      <Section title="Sector Rotation">
        <div className="h-full flex flex-col">
          {/* Bar chart placeholder */}
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-3">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-700 mb-2">Sector Performance</div>
              <div className="text-sm text-gray-500 mb-3">YTD Returns • Bar Chart</div>
              <div className="bg-white p-3 rounded shadow-sm text-xs text-left">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-blue-600">Tech:</span>
                    <span className="font-medium text-green-600">+42.3%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-purple-600">Finance:</span>
                    <span className="font-medium text-green-600">+24.2%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-yellow-600">Energy:</span>
                    <span className="font-medium text-red-600">+8.3%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Rotation metrics */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-purple-50 p-2 rounded">
              <div className="font-medium text-purple-800">Leader</div>
              <div className="text-purple-700">Technology</div>
            </div>
            <div className="bg-red-50 p-2 rounded">
              <div className="font-medium text-red-800">Laggard</div>
              <div className="text-red-700">Energy</div>
            </div>
          </div>
        </div>
      </Section>
    ),
    bottomRight7: (
      <Section title="Volatility Index">
        <div className="h-full flex flex-col">
          {/* Volatility chart placeholder */}
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-3">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-700 mb-2">VIX Analysis</div>
              <div className="text-sm text-gray-500 mb-3">Fear & Greed Index</div>
              <div className="bg-white p-3 rounded shadow-sm text-xs">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-orange-600">VIX:</span>
                    <span className="font-medium">18.4</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">20-day avg:</span>
                    <span className="font-medium">16.2</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-blue-600">Trend:</span>
                    <span className="font-medium">Elevated</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Volatility levels */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-yellow-50 p-2 rounded">
              <div className="font-medium text-yellow-800">Signal</div>
              <div className="text-yellow-700">Caution</div>
            </div>
            <div className="bg-orange-50 p-2 rounded">
              <div className="font-medium text-orange-800">Regime</div>
              <div className="text-orange-700">Uncertain</div>
            </div>
          </div>
        </div>
      </Section>
    )
  };

  const activeComponents = useRandom ? randomComponents : originalComponents;

  return (
    <>
      {/* Randomizer Controls */}
      <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-yellow-800">Layout Testing Controls - 3x2 Grid</h3>
            <p className="text-xs text-yellow-600">Test multi-chart dashboard with mixed space sizes</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={generateRandomLayout}
              className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
            >
              🎲 Randomize Charts
            </button>
            <button
              onClick={resetToOriginal}
              className="px-3 py-1.5 bg-gray-600 text-white text-sm rounded hover:bg-gray-700 transition-colors"
            >
              🔄 Reset Original
            </button>
          </div>
        </div>
        {useRandom && (
          <div className="mt-2 text-xs text-yellow-700">
            🎯 Testing full-width top + three quarter-width bottom components
          </div>
        )}
      </div>

      <Layout7
        title={
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Multi-Asset Technical Analysis Dashboard {useRandom && '(Randomized)'}</h1>
            <p className="text-gray-600 mt-1">Performance Tracking • Technical Indicators • Market Analysis</p>
          </div>
        }
        
        top={activeComponents.top7}
        bottomLeft={activeComponents.bottomLeft7}
        bottomCenter={activeComponents.bottomCenter7}
        bottomRight={activeComponents.bottomRight7}
      />
    </>
  );
}