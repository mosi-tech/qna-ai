'use client';

import { useState } from 'react';
import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';
import GridContainer4x3 from '@/components/insights/layout/components/GridContainer4x3';
import QuarterWidthTopLeft4x3 from '@/components/insights/layout/components/QuarterWidthTopLeft4x3';
import HalfWidthTop4x3 from '@/components/insights/layout/components/HalfWidthTop4x3';
import QuarterWidthTopRight4x3 from '@/components/insights/layout/components/QuarterWidthTopRight4x3';
import QuarterWidthLeft4x3 from '@/components/insights/layout/components/QuarterWidthLeft4x3';
import HalfWidthCenter4x3 from '@/components/insights/layout/components/HalfWidthCenter4x3';
import QuarterWidthRight4x3 from '@/components/insights/layout/components/QuarterWidthRight4x3';
import FullWidthBottom4x3 from '@/components/insights/layout/components/FullWidthBottom4x3';
import { getRandomComponentsForLayout } from '@/components/insights/layout/utils/layout-randomizer';

export default function Layout4Demo() {
  const layout4Positions = ['quarterWidthTopLeft4x3', 'halfWidthTop4x3', 'quarterWidthTopRight4x3', 'quarterWidthLeft4x3', 'halfWidthCenter4x3', 'quarterWidthRight4x3', 'fullWidthBottom4x3'];
  const [randomComponents, setRandomComponents] = useState<Record<string, React.ReactNode>>({});
  const [useRandom, setUseRandom] = useState(false);

  const generateRandomLayout = () => {
    const newComponents = getRandomComponentsForLayout(layout4Positions);
    setRandomComponents(newComponents);
    setUseRandom(true);
  };

  const resetToOriginal = () => {
    setUseRandom(false);
  };

  const originalComponents = {
    quarterWidthTopLeft4x3: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-2">Current Price</h3>
        <div className="text-2xl font-bold text-green-600 mb-1">$175.43</div>
        <div className="text-sm text-green-600">+$2.18 (+1.26%)</div>
        <div className="text-xs text-gray-500 mt-2">
          Volume: 52.8M<br/>
          Avg Vol: 58.1M
        </div>
      </div>
    ),
    halfWidthTop4x3: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-1">Apple Inc. (AAPL) - Technical Analysis</h3>
        <p className="text-sm text-gray-600 mb-3">6-Month Price Chart with Moving Averages & RSI Indicator</p>
        <div className="flex gap-6 text-xs">
          <div>
            <span className="text-gray-600">Period:</span>
            <span className="font-medium ml-1">6M</span>
          </div>
          <div>
            <span className="text-gray-600">Timeframe:</span>
            <span className="font-medium ml-1">Daily</span>
          </div>
          <div>
            <span className="text-gray-600">Last Updated:</span>
            <span className="font-medium ml-1">Nov 17, 2024 4:00 PM EST</span>
          </div>
        </div>
      </div>
    ),
    quarterWidthTopRight4x3: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-2">Market Cap</h3>
        <div className="text-2xl font-bold text-gray-900 mb-1">$2.73T</div>
        <div className="text-sm text-gray-600">Rank: #1</div>
        <div className="text-xs text-gray-500 mt-2">
          P/E: 29.8<br/>
          52W: $164.08 - $199.62
        </div>
      </div>
    ),
    quarterWidthLeft4x3: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-2">Key Levels</h3>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Resistance</span>
            <span className="font-medium text-red-600">$180.50</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Support</span>
            <span className="font-medium text-green-600">$172.15</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Pivot</span>
            <span className="font-medium">$176.33</span>
          </div>
        </div>
      </div>
    ),
    halfWidthCenter4x3: (
      <div>
        <div className="h-full bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center">
          <div className="text-center">
            <div className="text-lg font-semibold text-gray-700 mb-2">Interactive Price Chart</div>
            <div className="text-sm text-gray-500 mb-4">
              6-Month AAPL Price Action with Technical Indicators
            </div>
            <div className="bg-white p-4 rounded shadow-sm text-xs text-left max-w-sm">
              <div className="font-medium mb-2">Chart Elements:</div>
              <div className="space-y-1 text-gray-600">
                <div>• Candlestick price action</div>
                <div>• 20/50/200 Moving averages</div>
                <div>• RSI oscillator (bottom panel)</div>
                <div>• Volume bars</div>
                <div>• Support/resistance lines</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    ),
    quarterWidthRight4x3: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-2">Indicators</h3>
        <div className="space-y-3 text-sm">
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-gray-600">RSI (14)</span>
              <span className="font-medium text-yellow-600">58.3</span>
            </div>
            <div className="text-xs text-gray-500">Neutral</div>
          </div>
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-gray-600">MACD</span>
              <span className="font-medium text-green-600">Bullish</span>
            </div>
            <div className="text-xs text-gray-500">Above signal</div>
          </div>
          <div>
            <div className="flex justify-between mb-1">
              <span className="text-gray-600">MA Cross</span>
              <span className="font-medium text-green-600">Buy</span>
            </div>
            <div className="text-xs text-gray-500">20 &gt; 50 &gt; 200</div>
          </div>
        </div>
      </div>
    ),
    fullWidthBottom4x3: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-2">Technical Analysis Summary</h3>
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            <strong>Overall Signal: BULLISH</strong> • Price above all major MAs with RSI in neutral zone. 
            MACD crossover suggests continued upward momentum. Next resistance at $180.50, strong support at $172.15. 
            Volume slightly below average but trend remains intact.
          </div>
          <div className="flex gap-4 text-xs">
            <button className="px-3 py-1 bg-green-600 text-white rounded hover:bg-green-700">
              Set Alert
            </button>
            <button className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">
              Add to Watchlist
            </button>
            <button className="px-3 py-1 border border-gray-300 text-gray-700 rounded hover:bg-gray-50">
              Export Chart
            </button>
            <span className="text-gray-500 self-center">Signal Strength: 7/10</span>
          </div>
        </div>
      </div>
    )
  };

  const activeComponents = useRandom ? randomComponents : originalComponents;

  return (
    <>
      {/* Randomizer Controls */}
      <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-yellow-800">Layout Testing Controls</h3>
            <p className="text-xs text-yellow-600">Test different component combinations in sub-layouts</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={generateRandomLayout}
              className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
            >
              🎲 Randomize Components
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
            🎯 Showing randomized components to test variant compatibility
          </div>
        )}
      </div>

    <LayoutContainer>
      
      <LayoutHeader>
        <h1 className="text-2xl font-bold text-gray-900">Layout 4: Focus + Detail {useRandom && '(Randomized)'}</h1>
        <p className="text-gray-600 mt-1">4x3 grid • AAPL Stock Analysis with Technical Indicators</p>
      </LayoutHeader>

      <GridContainer4x3>
        
        <QuarterWidthTopLeft4x3>
          {activeComponents.quarterWidthTopLeft4x3}
        </QuarterWidthTopLeft4x3>

        <HalfWidthTop4x3>
          {activeComponents.halfWidthTop4x3}
        </HalfWidthTop4x3>

        <QuarterWidthTopRight4x3>
          {activeComponents.quarterWidthTopRight4x3}
        </QuarterWidthTopRight4x3>

        <QuarterWidthLeft4x3>
          {activeComponents.quarterWidthLeft4x3}
        </QuarterWidthLeft4x3>

        <HalfWidthCenter4x3>
          {activeComponents.halfWidthCenter4x3}
        </HalfWidthCenter4x3>

        <QuarterWidthRight4x3>
          {activeComponents.quarterWidthRight4x3}
        </QuarterWidthRight4x3>

        <FullWidthBottom4x3>
          {activeComponents.fullWidthBottom4x3}
        </FullWidthBottom4x3>

      </GridContainer4x3>
      
    </LayoutContainer>
    </>
  );
}