'use client';

import { useState } from 'react';
import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';
import GridContainer2x5 from '@/components/insights/layout/components/GridContainer2x5';
import LeftPrimary from '@/components/insights/layout/components/LeftPrimary';
import RightPrimary from '@/components/insights/layout/components/RightPrimary';
import LeftSecondary from '@/components/insights/layout/components/LeftSecondary';
import RightSecondary from '@/components/insights/layout/components/RightSecondary';
import FullWidthBottom from '@/components/insights/layout/components/FullWidthBottom';
import { getRandomComponentsForLayout } from '@/components/insights/layout/utils/layout-randomizer';

export default function Layout2Demo() {
  const layout2Positions = ['leftPrimary', 'rightPrimary', 'leftSecondary', 'rightSecondary', 'fullWidthBottom2x5'];
  const [randomComponents, setRandomComponents] = useState<Record<string, React.ReactNode>>({});
  const [useRandom, setUseRandom] = useState(false);

  const generateRandomLayout = () => {
    const newComponents = getRandomComponentsForLayout(layout2Positions);
    setRandomComponents(newComponents);
    setUseRandom(true);
  };

  const resetToOriginal = () => {
    setUseRandom(false);
  };

  const originalComponents = {
    leftPrimary: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-1">MACD Strategy</h3>
        <p className="text-sm text-gray-600 mb-4">Moving Average Convergence Divergence</p>
        <h4 className="font-medium text-gray-800 mb-3">Performance Metrics</h4>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">YTD Return</span>
            <span className="font-medium text-green-600">+12.3%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Sharpe Ratio</span>
            <span className="font-medium">1.18</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Max Drawdown</span>
            <span className="font-medium text-red-600">-15.8%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Win Rate</span>
            <span className="font-medium">58.4%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Volatility</span>
            <span className="font-medium">18.7%</span>
          </div>
        </div>
      </div>
    ),
    rightPrimary: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-1">Bollinger Bands</h3>
        <p className="text-sm text-gray-600 mb-4">Statistical Price Channel Strategy</p>
        <h4 className="font-medium text-gray-800 mb-3">Performance Metrics</h4>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">YTD Return</span>
            <span className="font-medium text-green-600">+9.7%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Sharpe Ratio</span>
            <span className="font-medium">0.94</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Max Drawdown</span>
            <span className="font-medium text-red-600">-12.3%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Win Rate</span>
            <span className="font-medium">62.1%</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">Volatility</span>
            <span className="font-medium">15.2%</span>
          </div>
        </div>
      </div>
    ),
    leftSecondary: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-3">Strategy Analysis</h3>
        <div className="space-y-3 text-sm">
          <div className="bg-green-50 p-3 rounded border border-green-200">
            <div className="font-medium text-green-800 mb-1">Strengths</div>
            <ul className="text-green-700 text-xs space-y-1">
              <li>• Higher absolute returns</li>
              <li>• Better trend following</li>
              <li>• Strong momentum capture</li>
            </ul>
          </div>
          <div className="bg-red-50 p-3 rounded border border-red-200">
            <div className="font-medium text-red-800 mb-1">Weaknesses</div>
            <ul className="text-red-700 text-xs space-y-1">
              <li>• Higher drawdowns</li>
              <li>• More false signals</li>
              <li>• Lagging in sideways markets</li>
            </ul>
          </div>
        </div>
      </div>
    ),
    rightSecondary: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-3">Strategy Analysis</h3>
        <div className="space-y-3 text-sm">
          <div className="bg-green-50 p-3 rounded border border-green-200">
            <div className="font-medium text-green-800 mb-1">Strengths</div>
            <ul className="text-green-700 text-xs space-y-1">
              <li>• Better risk control</li>
              <li>• Higher win rate</li>
              <li>• Works in ranging markets</li>
            </ul>
          </div>
          <div className="bg-red-50 p-3 rounded border border-red-200">
            <div className="font-medium text-red-800 mb-1">Weaknesses</div>
            <ul className="text-red-700 text-xs space-y-1">
              <li>• Lower absolute returns</li>
              <li>• Misses strong trends</li>
              <li>• Sensitive to parameters</li>
            </ul>
          </div>
        </div>
      </div>
    ),
    fullWidthBottom2x5: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-2">Winner: MACD Strategy</h3>
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            <strong>MACD delivers 2.6% higher returns</strong> with acceptable risk increase. Choose MACD for growth, Bollinger for stability.
          </div>
          <div className="flex gap-4 text-xs text-gray-500">
            <span>Backtest Period: Jan 2023 - Nov 2024</span>
            <span>Next Review: Dec 15, 2024</span>
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
        <h1 className="text-2xl font-bold text-gray-900">Layout 2: Side-by-Side Comparison {useRandom && '(Randomized)'}</h1>
        <p className="text-gray-600 mt-1">Built with: LayoutContainer → LayoutHeader → GridContainer2x5 → Positional Components</p>
      </LayoutHeader>

      <GridContainer2x5>
        
        <LeftPrimary>
          {activeComponents.leftPrimary}
        </LeftPrimary>

        <RightPrimary>
          {activeComponents.rightPrimary}
        </RightPrimary>

        <LeftSecondary>
          {activeComponents.leftSecondary}
        </LeftSecondary>

        <RightSecondary>
          {activeComponents.rightSecondary}
        </RightSecondary>

        <FullWidthBottom>
          {activeComponents.fullWidthBottom2x5}
        </FullWidthBottom>

      </GridContainer2x5>
      
    </LayoutContainer>
    </>
  );
}