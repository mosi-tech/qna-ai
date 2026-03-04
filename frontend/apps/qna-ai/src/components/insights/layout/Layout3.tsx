/**
 * Layout3: Three-Column Dashboard
 * 
 * 3x4 grid layout for multi-metric monitoring and KPI dashboards
 * Best for: Portfolio dashboards, department metrics, real-time monitoring
 * 
 * When to use:
 * - Need to display 3+ related metrics side by side
 * - Multi-category analysis (sales, marketing, operations)
 * - Real-time monitoring with alerts
 * - Portfolio views with multiple assets
 * 
 * When NOT to use:
 * - Simple single-metric analysis (use Layout1)
 * - Direct comparisons between 2 items (use Layout2)
 * - Detailed single-topic deep dive
 */

'use client';

import { useState } from 'react';
import LayoutContainer from './components/LayoutContainer';
import LayoutHeader from './components/LayoutHeader';
import GridContainer3x4 from './components/GridContainer3x4';
import ThirdWidthTop from './components/ThirdWidthTop';
import ThirdWidthMiddle from './components/ThirdWidthMiddle';
import FullWidthBottom3x4 from './components/FullWidthBottom3x4';
import { getRandomComponentsForLayout } from './utils/layout-randomizer';

interface Layout3Props {
  title?: React.ReactNode;
  leftTop?: React.ReactNode;       // ThirdWidthTop - Primary metrics overview
  centerTop?: React.ReactNode;     // ThirdWidthTop - Main analysis/charts
  rightTop?: React.ReactNode;      // ThirdWidthTop - Secondary metrics/alerts
  leftBottom?: React.ReactNode;    // ThirdWidthMiddle - Left details
  centerBottom?: React.ReactNode;  // ThirdWidthMiddle - Center details  
  rightBottom?: React.ReactNode;   // ThirdWidthMiddle - Right details
  bottom?: React.ReactNode;        // FullWidthBottom3x4 - Full-width actions/summary
}

export default function Layout3({
  title,
  leftTop,
  centerTop,
  rightTop,
  leftBottom,
  centerBottom,
  rightBottom,
  bottom
}: Layout3Props) {
  const [randomComponents, setRandomComponents] = useState<Record<string, React.ReactNode>>({});
  const [useRandom, setUseRandom] = useState(false);

  const originalComponents = {
    thirdWidthTop1: (
      <div className="h-full bg-white rounded-lg  p-4">
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Primary Metrics</h3>
          <div className="text-sm text-gray-600">
            [Key performance indicators and primary metrics]
          </div>
        </div>
      </div>
    ),
    thirdWidthTop2: (
      <div className="h-full bg-white rounded-lg  p-4">
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Main Analysis</h3>
          <div className="text-sm text-gray-600">
            [Charts, analysis, main content]
          </div>
        </div>
      </div>
    ),
    thirdWidthTop3: (
      <div className="h-full bg-white rounded-lg  p-4">
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Secondary Metrics</h3>
          <div className="text-sm text-gray-600">
            [Secondary metrics and alerts]
          </div>
        </div>
      </div>
    ),
    thirdWidthMiddle1: (
      <div className="h-full bg-white rounded-lg  p-4">
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Left Details</h3>
          <div className="text-sm text-gray-600">
            [Detailed information and context]
          </div>
        </div>
      </div>
    ),
    thirdWidthMiddle2: (
      <div className="h-full bg-white rounded-lg  p-4">
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Center Details</h3>
          <div className="text-sm text-gray-600">
            [Central detailed analysis]
          </div>
        </div>
      </div>
    ),
    thirdWidthMiddle3: (
      <div className="h-full bg-white rounded-lg  p-4">
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Right Details</h3>
          <div className="text-sm text-gray-600">
            [Right panel details and insights]
          </div>
        </div>
      </div>
    ),
    fullWidthBottom3x4: (
      <div className="h-full bg-white rounded-lg  p-4">
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Summary & Actions</h3>
          <div className="text-sm text-gray-600">
            [Full-width summary, actions, and next steps]
          </div>
        </div>
      </div>
    )
  };

  const generateRandomLayout = () => {
    const positions = ['thirdWidthTop1', 'thirdWidthTop2', 'thirdWidthTop3', 'thirdWidthMiddle1', 'thirdWidthMiddle2', 'thirdWidthMiddle3', 'fullWidthBottom3x4'];
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

      <LayoutHeader>
        {typeof title === 'string' ? `${title}${useRandom ? ' (Randomized)' : ''}` : title}
      </LayoutHeader>

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

      <GridContainer3x4>

        <ThirdWidthTop>
          {leftTop || activeComponents.thirdWidthTop1}
        </ThirdWidthTop>

        <ThirdWidthTop>
          {centerTop || activeComponents.thirdWidthTop2}
        </ThirdWidthTop>

        <ThirdWidthTop>
          {rightTop || activeComponents.thirdWidthTop3}
        </ThirdWidthTop>

        <ThirdWidthMiddle>
          {leftBottom || activeComponents.thirdWidthMiddle1}
        </ThirdWidthMiddle>

        <ThirdWidthMiddle>
          {centerBottom || activeComponents.thirdWidthMiddle2}
        </ThirdWidthMiddle>

        <ThirdWidthMiddle>
          {rightBottom || activeComponents.thirdWidthMiddle3}
        </ThirdWidthMiddle>

        <FullWidthBottom3x4>
          {bottom || activeComponents.fullWidthBottom3x4}
        </FullWidthBottom3x4>

      </GridContainer3x4>

    </LayoutContainer>
  );
}