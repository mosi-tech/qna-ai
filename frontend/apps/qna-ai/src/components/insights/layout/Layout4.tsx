/**
 * Layout4: Focus + Detail
 * 
 * 4x3 grid layout with large central focus area and supporting details
 * Best for: Single metric deep-dive, chart analysis, detailed reports
 * 
 * When to use:
 * - Deep-dive analysis into one specific metric or chart
 * - Single topic with extensive supporting context
 * - Interactive charts with surrounding data panels
 * - Detailed financial/technical analysis
 * 
 * When NOT to use:
 * - Multi-metric comparisons (use Layout2 or Layout3)
 * - Executive summaries (use Layout1)
 * - Equal-weight information display
 */

'use client';

import { useState } from 'react';
import LayoutContainer from './components/LayoutContainer';
import LayoutHeader from './components/LayoutHeader';
import GridContainer4x3 from './components/GridContainer4x3';
import QuarterWidthTopLeft4x3 from './components/QuarterWidthTopLeft4x3';
import HalfWidthTop4x3 from './components/HalfWidthTop4x3';
import QuarterWidthTopRight4x3 from './components/QuarterWidthTopRight4x3';
import QuarterWidthLeft4x3 from './components/QuarterWidthLeft4x3';
import HalfWidthCenter4x3 from './components/HalfWidthCenter4x3';
import QuarterWidthRight4x3 from './components/QuarterWidthRight4x3';
import FullWidthBottom4x3 from './components/FullWidthBottom4x3';
import { getRandomComponentsForLayout } from './utils/layout-randomizer';

interface Layout4Props {
  title?: React.ReactNode;
  topLeft?: React.ReactNode;       // QuarterWidthTopLeft4x3 - Supporting metric
  topCenter?: React.ReactNode;     // HalfWidthTop4x3 - Header/title area
  topRight?: React.ReactNode;      // QuarterWidthTopRight4x3 - Supporting metric
  middleLeft?: React.ReactNode;    // QuarterWidthLeft4x3 - Context panel
  center?: React.ReactNode;        // HalfWidthCenter4x3 - Main focus area (2x2)
  middleRight?: React.ReactNode;   // QuarterWidthRight4x3 - Context panel
  bottom?: React.ReactNode;        // FullWidthBottom4x3 - Summary/actions
}

export default function Layout4({
  title,
  topLeft,
  topCenter,
  topRight,
  middleLeft,
  center,
  middleRight,
  bottom
}: Layout4Props) {
  const [randomComponents, setRandomComponents] = useState<Record<string, React.ReactNode>>({});
  const [useRandom, setUseRandom] = useState(false);

  const originalComponents = {
    quarterWidthTopLeft4x3: (
      <div className="h-full bg-white rounded-lg  p-4">
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Supporting Metric</h3>
          <div className="text-sm text-gray-600">
            [Supporting metrics and KPIs]
          </div>
        </div>
      </div>
    ),
    halfWidthTop4x3: (
      <div className="h-full bg-white rounded-lg  p-4">
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Header Area</h3>
          <div className="text-sm text-gray-600">
            [Title, overview, and introduction]
          </div>
        </div>
      </div>
    ),
    quarterWidthTopRight4x3: (
      <div className="h-full bg-white rounded-lg  p-4">
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Supporting Metric</h3>
          <div className="text-sm text-gray-600">
            [Additional metrics and context]
          </div>
        </div>
      </div>
    ),
    quarterWidthLeft4x3: (
      <div className="h-full bg-white rounded-lg  p-4">
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Context Panel</h3>
          <div className="text-sm text-gray-600">
            [Supporting data and context]
          </div>
        </div>
      </div>
    ),
    halfWidthCenter4x3: (
      <div className="h-full bg-white rounded-lg  p-4">
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Main Focus Area</h3>
          <div className="text-sm text-gray-600">
            [Primary chart, analysis, or detailed content]
          </div>
        </div>
      </div>
    ),
    quarterWidthRight4x3: (
      <div className="h-full bg-white rounded-lg  p-4">
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Context Panel</h3>
          <div className="text-sm text-gray-600">
            [Right panel insights and data]
          </div>
        </div>
      </div>
    ),
    fullWidthBottom4x3: (
      <div className="h-full bg-white rounded-lg  p-4">
        <div>
          <h3 className="font-semibold text-gray-900 mb-3">Summary & Actions</h3>
          <div className="text-sm text-gray-600">
            [Summary, actions, and next steps]
          </div>
        </div>
      </div>
    )
  };

  const generateRandomLayout = () => {
    const positions = ['quarterWidthTopLeft4x3', 'halfWidthTop4x3', 'quarterWidthTopRight4x3', 'quarterWidthLeft4x3', 'halfWidthCenter4x3', 'quarterWidthRight4x3', 'fullWidthBottom4x3'];
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

      <GridContainer4x3>

        <QuarterWidthTopLeft4x3>
          {topLeft || activeComponents.quarterWidthTopLeft4x3}
        </QuarterWidthTopLeft4x3>

        <HalfWidthTop4x3>
          {topCenter || activeComponents.halfWidthTop4x3}
        </HalfWidthTop4x3>

        <QuarterWidthTopRight4x3>
          {topRight || activeComponents.quarterWidthTopRight4x3}
        </QuarterWidthTopRight4x3>

        <QuarterWidthLeft4x3>
          {middleLeft || activeComponents.quarterWidthLeft4x3}
        </QuarterWidthLeft4x3>

        <HalfWidthCenter4x3>
          {center || activeComponents.halfWidthCenter4x3}
        </HalfWidthCenter4x3>

        <QuarterWidthRight4x3>
          {middleRight || activeComponents.quarterWidthRight4x3}
        </QuarterWidthRight4x3>

        <FullWidthBottom4x3>
          {bottom || activeComponents.fullWidthBottom4x3}
        </FullWidthBottom4x3>

      </GridContainer4x3>

    </LayoutContainer>
  );
}