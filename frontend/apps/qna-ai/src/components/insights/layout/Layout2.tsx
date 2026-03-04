/**
 * Layout 2: Side-by-Side Comparison Layout
 * 
 * Grid Structure: 2x5 (2 columns, 5 rows)
 * 
 * Layout Map:
 * [2x2] [2x2]     <- Top: Main comparison content (bigger)
 * [2x2] [2x2]     <- Middle: Secondary comparison content  
 * [4x1]           <- Bottom: Summary/conclusion across both
 * 
 * When to Use This Layout:
 * ✅ Stock A vs Stock B comparisons
 * ✅ Strategy comparisons (MACD vs Bollinger)
 * ✅ Before vs After analysis
 * ✅ Product comparison analysis
 * ✅ Vendor evaluations (A vs B)
 * ✅ Any "X vs Y" analysis
 * 
 * Don't Use For:
 * ❌ Single entity analysis (use Layout1)
 * ❌ Multi-entity analysis (3+ items, use Layout3)
 * ❌ Time-series analysis (use Layout4)
 * ❌ Complex dashboards (use Layout1)
 */

'use client';

import { useState } from 'react';
import LayoutContainer from './components/LayoutContainer';
import LayoutHeader from './components/LayoutHeader';
import { getRandomComponentsForLayout } from './utils/layout-randomizer';

interface Layout2Props {
  title?: React.ReactNode;
  leftTop?: React.ReactNode;       // 1x2 - Left primary content (bigger)
  rightTop?: React.ReactNode;      // 1x2 - Right primary content (bigger)
  leftBottom?: React.ReactNode;    // 1x2 - Left secondary content
  rightBottom?: React.ReactNode;   // 1x2 - Right secondary content
  summary?: React.ReactNode;       // 2x1 - Comparison summary/conclusion
}

export default function Layout2({
  title,
  leftTop,
  rightTop,
  leftBottom,
  rightBottom,
  summary
}: Layout2Props) {
  const [randomComponents, setRandomComponents] = useState<Record<string, React.ReactNode>>({});
  const [useRandom, setUseRandom] = useState(false);

  const originalComponents = {
    leftPrimary: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-3">[Entity A - Main Analysis]</h3>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">[Primary Metric]</span>
            <span className="font-medium">[Value]</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">[Secondary Metric]</span>
            <span className="font-medium">[Value]</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">[Performance Metric]</span>
            <span className="font-medium">[Value]</span>
          </div>
        </div>
      </div>
    ),
    rightPrimary: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-3">[Entity B - Main Analysis]</h3>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-gray-600">[Primary Metric]</span>
            <span className="font-medium">[Value]</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">[Secondary Metric]</span>
            <span className="font-medium">[Value]</span>
          </div>
          <div className="flex justify-between">
            <span className="text-gray-600">[Performance Metric]</span>
            <span className="font-medium">[Value]</span>
          </div>
        </div>
      </div>
    ),
    leftSecondary: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-3">[Secondary Analysis]</h3>
        <div className="text-sm text-gray-600">
          [Charts, details, breakdowns]
        </div>
      </div>
    ),
    rightSecondary: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-3">[Secondary Analysis]</h3>
        <div className="text-sm text-gray-600">
          [Charts, details, breakdowns]
        </div>
      </div>
    ),
    fullWidthBottom2x5: (
      <div>
        <h3 className="font-semibold text-gray-900 mb-2">Comparison Summary</h3>
        <div className="flex justify-between items-center">
          <div className="text-sm text-gray-600">
            [Winner, key differences, recommendations]
          </div>
          <div className="text-xs text-gray-500">
            [Last updated, next review]
          </div>
        </div>
      </div>
    )
  };

  const generateRandomLayout = () => {
    const positions = ['leftPrimary', 'rightPrimary', 'leftSecondary', 'rightSecondary', 'fullWidthBottom2x5'];
    const newComponents = getRandomComponentsForLayout(positions);
    setRandomComponents(newComponents);
    setUseRandom(true);
  };

  const resetToOriginal = () => {
    setUseRandom(false);
    setRandomComponents({});
  };

  const activeComponents = useRandom ? randomComponents : originalComponents;
  return (
    <LayoutContainer>

      {title && (
        <LayoutHeader>
          {typeof title === 'string' ? `${title}${useRandom ? ' (Randomized)' : ''}` : title}
        </LayoutHeader>
      )}

      {/* Randomizer Controls */}
      <div className="mb-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-center gap-3">
          <span className="text-sm font-medium text-yellow-800">Layout Randomizer:</span>
          <button
            onClick={generateRandomLayout}
            className="px-3 py-1 text-xs bg-yellow-200 hover:bg-yellow-300 text-yellow-800 rounded transition-colors"
          >
            Generate Random
          </button>
          <button
            onClick={resetToOriginal}
            className="px-3 py-1 text-xs bg-gray-200 hover:bg-gray-300 text-gray-700 rounded transition-colors"
          >
            Reset Original
          </button>
          <span className="text-xs text-yellow-700">
            {useRandom ? 'Showing randomized components' : 'Showing original layout'}
          </span>
        </div>
      </div>

      {/* 2x5 Grid for Side-by-Side Comparison */}
      <div className="flex-1 grid grid-cols-2 grid-rows-5 gap-4 min-h-0">

        {/* Primary Comparison Row - Now Bigger */}
        <div className="col-span-1 row-span-2">
          <div className="h-full bg-white rounded-lg  p-4">
            {leftTop || activeComponents.leftPrimary}
          </div>
        </div>

        <div className="col-span-1 row-span-2">
          <div className="h-full bg-white rounded-lg  p-4">
            {rightTop || activeComponents.rightPrimary}
          </div>
        </div>

        {/* Secondary Comparison Row */}
        <div className="col-span-1 row-span-2">
          <div className="h-full bg-white rounded-lg  p-4">
            {leftBottom || activeComponents.leftSecondary}
          </div>
        </div>

        <div className="col-span-1 row-span-2">
          <div className="h-full bg-white rounded-lg  p-4">
            {rightBottom || activeComponents.rightSecondary}
          </div>
        </div>

        {/* Summary Row - Spans Full Width */}
        <div className="col-span-2 row-span-1">
          <div className="h-full bg-white rounded-lg  p-4">
            {summary || activeComponents.fullWidthBottom2x5}
          </div>
        </div>

      </div>
    </LayoutContainer>
  );
}