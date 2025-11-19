'use client';

import { useState } from 'react';
import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';
import GridContainer3x4 from '@/components/insights/layout/components/GridContainer3x4';
import ThirdWidthTop from '@/components/insights/layout/components/ThirdWidthTop';
import ThirdWidthMiddle from '@/components/insights/layout/components/ThirdWidthMiddle';
import FullWidthBottom3x4 from '@/components/insights/layout/components/FullWidthBottom3x4';
import { getRandomComponentsForLayout } from '@/components/insights/layout/utils/layout-randomizer';

export default function Layout3Demo() {
  const layout3Positions = ['thirdWidthTop1', 'thirdWidthTop2', 'thirdWidthTop3', 'thirdWidthMiddle1', 'thirdWidthMiddle2', 'thirdWidthMiddle3', 'fullWidthBottom3x4'];
  const [randomComponents, setRandomComponents] = useState<Record<string, React.ReactNode>>({});
  const [useRandom, setUseRandom] = useState(false);

  const generateRandomLayout = () => {
    const newComponents = getRandomComponentsForLayout(layout3Positions);
    setRandomComponents(newComponents);
    setUseRandom(true);
  };

  const resetToOriginal = () => {
    setUseRandom(false);
  };

  const originalComponents = {
    thirdWidthTop1: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-1">Equity Portfolio</h3>
        <p className="text-sm text-gray-600 mb-4">US Large Cap Growth</p>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Portfolio Value</span>
            <span className="font-medium text-green-600">$2.4M</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Today's P&L</span>
            <span className="font-medium text-green-600">+$18.2K (+0.76%)</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">YTD Return</span>
            <span className="font-medium text-green-600">+14.8%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Risk Level</span>
            <span className="font-medium text-yellow-600">Moderate</span>
          </div>
        </div>
        <div className="mt-4 p-3 bg-blue-50 rounded border border-blue-200">
          <div className="text-blue-800 font-medium text-xs">Top Performers</div>
          <div className="text-blue-700 text-xs mt-1">
            AAPL: +2.1% • MSFT: +1.8% • GOOGL: +1.4%
          </div>
        </div>
      </div>
    ),
    thirdWidthTop2: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-1">Fixed Income</h3>
        <p className="text-sm text-gray-600 mb-4">Investment Grade Bonds</p>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Portfolio Value</span>
            <span className="font-medium">$1.2M</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Today's P&L</span>
            <span className="font-medium text-green-600">+$3.1K (+0.26%)</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">YTD Return</span>
            <span className="font-medium text-green-600">+6.2%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Duration</span>
            <span className="font-medium">4.2 years</span>
          </div>
        </div>
        <div className="mt-4 p-3 bg-green-50 rounded border border-green-200">
          <div className="text-green-800 font-medium text-xs">Yield Analysis</div>
          <div className="text-green-700 text-xs mt-1">
            Current: 4.8% • 30-day avg: 4.6% • Target: 5.0%
          </div>
        </div>
      </div>
    ),
    thirdWidthTop3: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-1">Alternative Investments</h3>
        <p className="text-sm text-gray-600 mb-4">REITs & Commodities</p>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">Portfolio Value</span>
            <span className="font-medium">$400K</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Today's P&L</span>
            <span className="font-medium text-red-600">-$2.8K (-0.70%)</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">YTD Return</span>
            <span className="font-medium text-green-600">+8.1%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Volatility</span>
            <span className="font-medium">22.3%</span>
          </div>
        </div>
        <div className="mt-4 p-3 bg-yellow-50 rounded border border-yellow-200">
          <div className="text-yellow-800 font-medium text-xs">⚠️ Alert</div>
          <div className="text-yellow-700 text-xs mt-1">
            Gold exposure above target (12% vs 8%)
          </div>
        </div>
      </div>
    ),
    thirdWidthMiddle1: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-2">Risk Metrics</h3>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-600">Portfolio Beta</span>
            <span className="font-medium">1.12</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">VaR (95%)</span>
            <span className="font-medium text-red-600">-$42K</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Sharpe Ratio</span>
            <span className="font-medium">1.34</span>
          </div>
        </div>
      </div>
    ),
    thirdWidthMiddle2: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-2">Allocation</h3>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-600">Equity</span>
            <span className="font-medium">60%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Fixed Income</span>
            <span className="font-medium">30%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Alternatives</span>
            <span className="font-medium">10%</span>
          </div>
        </div>
      </div>
    ),
    thirdWidthMiddle3: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-2">Cash Flow</h3>
        <div className="space-y-2 text-xs">
          <div className="flex justify-between">
            <span className="text-gray-600">Monthly Income</span>
            <span className="font-medium text-green-600">$12.4K</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Reinvestment</span>
            <span className="font-medium">$8.7K</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Available Cash</span>
            <span className="font-medium">$85K</span>
          </div>
        </div>
      </div>
    ),
    fullWidthBottom3x4: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-2">Portfolio Summary & Actions</h3>
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            <strong>Total Portfolio: $4.0M</strong> • Total P&L: +$18.5K (+0.46%) • 
            Next rebalancing due in 12 days • 2 alerts require attention
          </div>
          <div className="flex gap-4 text-xs">
            <button className="px-3 py-1 bg-blue-600 text-white rounded hover:bg-blue-700">
              Rebalance Now
            </button>
            <button className="px-3 py-1 border border-gray-300 text-gray-700 rounded hover:bg-gray-50">
              Generate Report
            </button>
            <span className="text-gray-500">Last updated: 2 min ago</span>
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
        <h1 className="text-2xl font-bold text-gray-900">Layout 3: Three-Column Dashboard {useRandom && '(Randomized)'}</h1>
        <p className="text-gray-600 mt-1">3x4 grid • Multi-asset portfolio monitoring with real-time alerts</p>
      </LayoutHeader>

      <GridContainer3x4>
        
        <ThirdWidthTop>
          {activeComponents.thirdWidthTop1}
        </ThirdWidthTop>

        <ThirdWidthTop>
          {activeComponents.thirdWidthTop2}
        </ThirdWidthTop>

        <ThirdWidthTop>
          {activeComponents.thirdWidthTop3}
        </ThirdWidthTop>

        <ThirdWidthMiddle>
          {activeComponents.thirdWidthMiddle1}
        </ThirdWidthMiddle>

        <ThirdWidthMiddle>
          {activeComponents.thirdWidthMiddle2}
        </ThirdWidthMiddle>

        <ThirdWidthMiddle>
          {activeComponents.thirdWidthMiddle3}
        </ThirdWidthMiddle>

        <FullWidthBottom3x4>
          {activeComponents.fullWidthBottom3x4}
        </FullWidthBottom3x4>

      </GridContainer3x4>
      
    </LayoutContainer>
    </>
  );
}