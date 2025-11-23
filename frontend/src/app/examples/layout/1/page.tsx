'use client';

import { useState, useEffect } from 'react';
import LayoutContainer from '@/components/insights/layout/components/LayoutContainer';
import LayoutHeader from '@/components/insights/layout/components/LayoutHeader';
import GridContainer4x6 from '@/components/insights/layout/components/GridContainer4x6';
import HalfWidthTopLeft from '@/components/insights/layout/components/HalfWidthTopLeft';
import HalfWidthTopRight from '@/components/insights/layout/components/HalfWidthTopRight';
import QuarterWidthMiddleLeft from '@/components/insights/layout/components/QuarterWidthMiddleLeft';
import HalfWidthMiddleCenter from '@/components/insights/layout/components/HalfWidthMiddleCenter';
import QuarterWidthMiddleRight from '@/components/insights/layout/components/QuarterWidthMiddleRight';
import FullWidthBottom from '@/components/insights/layout/components/FullWidthBottom';
import { getRandomComponentsForLayout, getRandomComponentsWithIndices, getRandomComponentsFromIndices } from '@/components/insights/layout/utils/layout-randomizer';
import { DebugProvider } from '@/components/insights/layout/components/OverflowTracker';
import OverflowTracker from '@/components/insights/layout/components/OverflowTracker';
import DebugToggle from '@/components/insights/layout/components/DebugToggle';
import StatGroup from '@/components/insights/StatGroup';
import Section from '@/components/insights/Section';
import ExecutiveSummary from '@/components/insights/ExecutiveSummary';
import ComparisonTable from '@/components/insights/ComparisonTable';
import CalloutNote from '@/components/insights/CalloutNote';
import CalloutList from '@/components/insights/CalloutList';
import ActionList from '@/components/insights/ActionList';
import { validateComponent, autoFixComponent } from '@/components/insights/layout/utils/componentValidator';
import ValidationDisplay from '@/components/insights/layout/components/ValidationDisplay';

export default function Layout1Demo() {
  const layout1Positions = ['halfWidthTopLeft', 'halfWidthTopRight', 'quarterWidthMiddleLeft', 'halfWidthMiddleCenter', 'quarterWidthMiddleRight', 'fullWidthBottom'];
  const [randomComponents, setRandomComponents] = useState<Record<string, React.ReactNode>>({});
  const [useRandom, setUseRandom] = useState(false);

  // Load persisted random state on mount
  useEffect(() => {
    const savedIndices = localStorage.getItem('layout1-random-indices');
    if (savedIndices) {
      try {
        const indices = JSON.parse(savedIndices);
        const restoredComponents = getRandomComponentsFromIndices(layout1Positions, indices);
        setRandomComponents(restoredComponents);
        setUseRandom(true);
      } catch (error) {
        console.warn('Failed to restore random components:', error);
        localStorage.removeItem('layout1-random-indices');
      }
    }
  }, []);

  const generateRandomLayout = () => {
    const { components, indices } = getRandomComponentsWithIndices(layout1Positions);
    setRandomComponents(components);
    setUseRandom(true);
    localStorage.setItem('layout1-random-indices', JSON.stringify(indices));
  };

  const resetToOriginal = () => {
    setUseRandom(false);
    localStorage.removeItem('layout1-random-indices');
  };

  // Component validation demonstration
  const validateComponents = () => {
    const componentConfigs = [
      { name: 'Section (Executive Summary)', type: 'Section', space: 'half_width', props: { title: 'Executive Summary', variant: 'compact' }},
      { name: 'StatGroup (Key Metrics)', type: 'StatGroup', space: 'half_width', props: { title: 'Key Metrics', variant: 'compact', stats: [1,2,3,4] }},
      { name: 'CalloutList (Key Highlights)', type: 'CalloutList', space: 'quarter_width', props: { title: 'Key Highlights', variant: 'compact', items: [1,2,3] }},
      { name: 'ComparisonTable (Sector Perf)', type: 'ComparisonTable', space: 'half_width', props: { title: 'Sector Performance', variant: 'narrow', entities: [1,2,3,4] }},
      { name: 'CalloutList (Key Insights)', type: 'CalloutList', space: 'quarter_width', props: { title: 'Key Insights', variant: 'compact', items: [1,2,3] }},
      { name: 'ActionList (Recommended)', type: 'ActionList', space: 'full_width', props: { title: 'Recommended Actions', variant: 'compact', actions: [1,2,3] }}
    ];

    console.log('=== Component Validation Results ===');
    componentConfigs.forEach(config => {
      const result = validateComponent(config.type, config.space, config.props);
      console.log(`\n${config.name}:`, result);
      if (!result.isValid) {
        const fixed = autoFixComponent(config.type, config.space, config.props);
        console.log('Auto-fixed props:', fixed);
      }
    });
  };

  const originalComponents = {
    halfWidthTopLeft: (
      <ExecutiveSummary
        title="Executive Summary"
        items={[
          { label: "Key Finding", text: "Portfolio delivered +12.4% YTD return, outperforming benchmark by 240bps", color: "blue" },
          { label: "Performance", text: "Risk-adjusted returns rank in top quartile with Sharpe ratio of 1.18", color: "green" },
          { label: "Recommendation", text: "Rebalance technology allocation to maintain target weights", color: "purple" }
        ]}
        variant="compact"
      />
    ),
    halfWidthTopRight: (
      <StatGroup
        title="Key Metrics"
        variant="compact"
        stats={[
          { label: "YTD", value: "+12.4%", change: "+2.4%", changeType: "positive" as const },
          { label: "Sharpe", value: "1.18", change: "Top Q", changeType: "positive" as const },
          { label: "Drawdown", value: "-8.2%", change: "Below", changeType: "neutral" as const },
          { label: "Beta", value: "0.72", change: "Def.", changeType: "neutral" as const }
        ]}
        columns={2}
      />
    ),
    quarterWidthMiddleLeft: (
      <CalloutList
        title="Key Highlights"
        variant="compact"
        items={[
          {
            id: "1",
            title: "Strong Performance",
            content: "Outperformed 89% of peers",
            type: "success"
          },
          {
            id: "2", 
            title: "Risk Control",
            content: "Volatility 15% below market",
            type: "info"
          },
          {
            id: "3",
            title: "Tech Overweight", 
            content: "5% above target allocation",
            type: "warning"
          }
        ]}
      />
    ),
    halfWidthMiddleCenter: (
      <ComparisonTable
        title="Sector Performance"
        variant="narrow"
        entities={[
          { id: "tech", name: "Technology", subtitle: "25% allocation" },
          { id: "health", name: "Healthcare", subtitle: "18% allocation" },
          { id: "finance", name: "Financials", subtitle: "15% allocation" },
          { id: "consumer", name: "Consumer", subtitle: "12% allocation" }
        ]}
        metrics={[
          { id: "return", name: "Return", format: "percentage" },
          { id: "vs_index", name: "vs Index", format: "percentage" }
        ]}
        data={{
          "tech": { "return": "+18.7%", "vs_index": "+4.2%" },
          "health": { "return": "+11.3%", "vs_index": "+2.1%" },
          "finance": { "return": "+8.9%", "vs_index": "-1.3%" },
          "consumer": { "return": "+6.4%", "vs_index": "+0.8%" }
        }}
      />
    ),
    quarterWidthMiddleRight: (
      <CalloutList
        title="Key Insights"
        variant="compact"
        items={[
          {
            id: "1",
            title: "Defensive Positioning",
            content: "Lower beta cushioned downside",
            type: "info"
          },
          {
            id: "2",
            title: "Sector Selection", 
            content: "Tech allocation drove outperformance",
            type: "success"
          },
          {
            id: "3",
            title: "Rebalancing Due",
            content: "Tech weight above target range", 
            type: "warning"
          }
        ]}
      />
    ),
    fullWidthBottom: (
      <div className="p-8 bg-gray-100 border-2 border-dashed border-gray-300 rounded-lg text-center">
        <div className="text-gray-500 text-lg font-medium">Component TBD</div>
        <div className="text-sm text-gray-400 mt-2">ActionList doesn't belong in this layout - will determine appropriate component later</div>
      </div>
    )
  };

  const activeComponents = useRandom ? randomComponents : originalComponents;

  return (
    <DebugProvider>
      {/* Debug Mode Controls */}
      <DebugToggle />
      
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
            <button
              onClick={validateComponents}
              className="px-3 py-1.5 bg-purple-600 text-white text-sm rounded hover:bg-purple-700 transition-colors"
            >
              🔍 Validate Components
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
          <h1 className="text-2xl font-bold text-gray-900">Layout 1: Executive Analysis {useRandom && '(Randomized)'}</h1>
          <p className="text-gray-600 mt-1">Built with: LayoutContainer → LayoutHeader → GridContainer4x6 → Positional Components</p>
        </LayoutHeader>

        <GridContainer4x6>
          
          <HalfWidthTopLeft>
            <div className="relative">
              <OverflowTracker
                componentName="ExecutiveSummary"
                componentType="Section"
                layoutName="Layout1"
                spaceName="halfWidthTopLeft"
              >
                {activeComponents.halfWidthTopLeft}
              </OverflowTracker>
              <ValidationDisplay
                componentType="Section"
                spaceType="half_width"
                props={{ title: "Executive Summary", variant: "compact" }}
                componentName="Executive Summary"
              />
            </div>
          </HalfWidthTopLeft>

          <HalfWidthTopRight>
            <div className="relative">
              <OverflowTracker
                componentName="KeyMetrics"
                componentType="StatGroup"
                layoutName="Layout1"
                spaceName="halfWidthTopRight"
              >
                {activeComponents.halfWidthTopRight}
              </OverflowTracker>
              <ValidationDisplay
                componentType="StatGroup"
                spaceType="half_width"
                props={{ title: "Key Metrics", variant: "compact", stats: [1,2,3,4], columns: 2 }}
                componentName="Key Metrics"
              />
            </div>
          </HalfWidthTopRight>

          <QuarterWidthMiddleLeft>
            <div className="relative">
              <OverflowTracker
                componentName="KeyHighlights"
                componentType="BulletList"
                layoutName="Layout1"
                spaceName="quarterWidthMiddleLeft"
              >
                {activeComponents.quarterWidthMiddleLeft}
              </OverflowTracker>
              <ValidationDisplay
                componentType="CalloutList"
                spaceType="quarter_width"
                props={{ title: "Key Highlights", variant: "compact", items: [1,2,3] }}
                componentName="Key Highlights"
              />
            </div>
          </QuarterWidthMiddleLeft>

          <HalfWidthMiddleCenter>
            <div className="relative">
              <OverflowTracker
                componentName="SectorPerformance"
                componentType="ComparisonTable"
                layoutName="Layout1"
                spaceName="halfWidthMiddleCenter"
              >
                {activeComponents.halfWidthMiddleCenter}
              </OverflowTracker>
              <ValidationDisplay
                componentType="ComparisonTable"
                spaceType="half_width"
                props={{ title: "Sector Performance", variant: "narrow", entities: [1,2,3,4], columns: 2 }}
                componentName="Sector Performance"
              />
            </div>
          </HalfWidthMiddleCenter>

          <QuarterWidthMiddleRight>
            <div className="relative">
              <OverflowTracker
                componentName="KeyInsights"
                componentType="CalloutNote"
                layoutName="Layout1"
                spaceName="quarterWidthMiddleRight"
              >
                {activeComponents.quarterWidthMiddleRight}
              </OverflowTracker>
              <ValidationDisplay
                componentType="CalloutList"
                spaceType="quarter_width"
                props={{ title: "Key Insights", variant: "compact", items: [1,2,3] }}
                componentName="Key Insights"
              />
            </div>
          </QuarterWidthMiddleRight>

          <FullWidthBottom>
            <div className="relative">
              <OverflowTracker
                componentName="RecommendedActions"
                componentType="ActionList"
                layoutName="Layout1"
                spaceName="fullWidthBottom"
              >
                {activeComponents.fullWidthBottom}
              </OverflowTracker>
              <ValidationDisplay
                componentType="ActionList"
                spaceType="full_width"
                props={{ title: "Recommended Actions", variant: "compact", actions: [1,2,3] }}
                componentName="Recommended Actions"
              />
            </div>
          </FullWidthBottom>

        </GridContainer4x6>
      
      </LayoutContainer>
    </DebugProvider>
  );
}