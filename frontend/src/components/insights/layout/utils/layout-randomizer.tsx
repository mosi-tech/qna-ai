'use client';

import React from 'react';
import StatGroup from '../../StatGroup';
import ExecutiveSummary from '../../ExecutiveSummary';
import ComparisonTable from '../../ComparisonTable';
import SummaryConclusion from '../../SummaryConclusion';
import BulletList from '../../BulletList';
import ActionList from '../../poor/ActionList';
import CalloutNote from '../../poor/CalloutNote';
import KeyValueTable from '../../poor/KeyValueTable';
import RankedList from '../../RankedList';

// Import our mapping configuration
import layoutMapping from '../layout-component-mapping.json';

// Helper function to get the best variant for a component in a specific space
const getBestVariant = (componentType: string, spaceType: string): string => {
  const componentVariants = layoutMapping.component_variants[componentType];
  if (!componentVariants) return 'default';

  // Find variants that list this space type in their best_spaces
  const suitableVariants = Object.entries(componentVariants).filter(([variant, config]) =>
    config.best_spaces.includes(spaceType)
  );

  // If we found suitable variants, pick the first one
  if (suitableVariants.length > 0) {
    return suitableVariants[0][0];
  }

  // Fallback to default
  return 'default';
};

// Helper function to get the best variant for a component in a specific position
const getBestVariantForPosition = (componentType: string, position: string): string => {
  const positionConfig = layoutMapping.sub_layout_positions?.[position];
  const preferredVariant = positionConfig?.component_limits?.[componentType]?.preferred_variant;
  
  if (preferredVariant) {
    return preferredVariant;
  }
  
  // Fallback to space-based variant selection
  const spaceType = getSpaceType(position);
  return getBestVariant(componentType, spaceType);
};

// Helper function to get max items for a component variant
const getMaxItems = (componentType: string, variant: string): number => {
  const componentVariants = layoutMapping.component_variants[componentType];
  if (!componentVariants || !componentVariants[variant]) return 4; // fallback

  return componentVariants[variant].max_items || 4;
};

// Helper function to get max items for a specific position
const getMaxItemsForPosition = (componentType: string, position: string): number => {
  const positionConfig = layoutMapping.sub_layout_positions?.[position];
  if (positionConfig?.component_limits?.[componentType]?.max_items) {
    return positionConfig.component_limits[componentType].max_items;
  }

  // Fallback to variant-based limits
  const variant = getBestVariant(componentType, getSpaceType(position));
  return getMaxItems(componentType, variant);
};

// Helper function to get space type from position
const getSpaceType = (position: string): string => {
  const positionConfig = layoutMapping.sub_layout_positions?.[position];
  return positionConfig?.space_type || spaceMapping[position] || "full_width";
};

// Diverse sample data generators for different themes
const generateFinancialStats = (count: number = 4) => [
  { label: "Revenue", value: "$2.4M", change: "+12.5%", changeType: "positive" as const },
  { label: "Growth", value: "18.7%", change: "+3.2%", changeType: "positive" as const },
  { label: "Risk", value: "Low", change: "Stable", changeType: "neutral" as const },
  { label: "ROI", value: "24.1%", change: "+5.8%", changeType: "positive" as const }
].slice(0, count);

const generateTechStats = (count: number = 4) => [
  { label: "Users", value: "2.4M", change: "+23.1%", changeType: "positive" as const },
  { label: "Uptime", value: "99.9%", change: "+0.1%", changeType: "positive" as const },
  { label: "Latency", value: "12ms", change: "-3ms", changeType: "positive" as const },
  { label: "API Calls", value: "450K", change: "+67%", changeType: "positive" as const }
].slice(0, count);

const generateHealthcareStats = (count: number = 4) => [
  { label: "Patients", value: "1,247", change: "+8.3%", changeType: "positive" as const },
  { label: "Satisfaction", value: "94%", change: "+2%", changeType: "positive" as const },
  { label: "Wait Time", value: "4.2min", change: "-30s", changeType: "positive" as const },
  { label: "Efficiency", value: "87%", change: "+5%", changeType: "positive" as const }
].slice(0, count);

const generateEnergyStats = (count: number = 4) => [
  { label: "Output", value: "450MW", change: "+12%", changeType: "positive" as const },
  { label: "Efficiency", value: "92%", change: "+1.5%", changeType: "positive" as const },
  { label: "Downtime", value: "0.8%", change: "-0.3%", changeType: "positive" as const },
  { label: "Cost/MWh", value: "$45", change: "-$3", changeType: "positive" as const }
].slice(0, count);

const generateSampleEntities = () => [
  { id: "stock1", name: "AAPL", subtitle: "Technology • Large Cap" },
  { id: "stock2", name: "MSFT", subtitle: "Technology • Large Cap" },
  { id: "stock3", name: "GOOGL", subtitle: "Technology • Large Cap" },
  { id: "stock4", name: "TSLA", subtitle: "Consumer • Large Cap" }
];

const generateSampleMetrics = () => [
  { id: "return", name: "1Y Return", format: "percentage" as const },
  { id: "pe", name: "P/E Ratio", format: "number" as const },
  { id: "beta", name: "Beta", format: "number" as const },
  { id: "yield", name: "Dividend Yield", format: "percentage" as const }
];

const generateSampleTableData = () => ({
  "stock1": { "return": "+28.4%", "pe": "33.2", "beta": "0.89", "yield": "0.5%" },
  "stock2": { "return": "+31.8%", "pe": "42.1", "beta": "1.34", "yield": "0.7%" },
  "stock3": { "return": "+26.7%", "pe": "24.3", "beta": "1.05", "yield": "0.0%" },
  "stock4": { "return": "+15.3%", "pe": "58.7", "beta": "2.21", "yield": "0.0%" }
});

const generateSampleKeyFindings = () => [
  "Portfolio performance exceeded benchmarks by 340bps this quarter",
  "Technology sector concentration at 38% presents both opportunity and risk",
  "Risk-adjusted returns improved significantly with Sharpe ratio of 1.42",
  "Market volatility remained contained despite geopolitical uncertainties",
  "ESG integration enhanced long-term performance sustainability"
];

const generateSampleActions = () => [
  {
    id: "1",
    title: "Rebalance tech exposure",
    description: "Reduce technology allocation from 38% to 30%",
    priority: "high" as const,
    timeline: "immediate" as const
  },
  {
    id: "2",
    title: "Increase defensive positions",
    description: "Add healthcare and utilities for stability",
    priority: "medium" as const,
    timeline: "short-term" as const
  },
  {
    id: "3",
    title: "Review ESG criteria",
    description: "Update screening parameters for better alignment",
    priority: "low" as const,
    timeline: "medium-term" as const
  }
];

const generateSampleBullets = () => [
  "Strong momentum across growth factors with technology leadership",
  "Defensive positioning in healthcare provides downside protection",
  "Energy sector underweight strategy proved successful this quarter",
  "International diversification reduced overall portfolio volatility"
];

// Component generators with truly diverse variants
const componentGenerators = {
  quarter_width: [
    {
      name: "StatGroup - Financial",
      component: (key: string) => {
        const variant = getBestVariant('StatGroup', 'quarter_width');
        const maxItems = getMaxItems('StatGroup', variant);
        return (
          <StatGroup
            key={key}
            title="Financial KPIs"
            stats={generateFinancialStats(maxItems)}
            variant={variant}
            columns={2}
          />
        );
      }
    },
    {
      name: "StatGroup - Technology",
      component: (key: string) => {
        const variant = getBestVariant('StatGroup', 'quarter_width');
        const maxItems = getMaxItems('StatGroup', variant);
        return (
          <StatGroup
            key={key}
            title="System Performance"
            stats={generateTechStats(maxItems)}
            variant={variant}
            columns={2}
          />
        );
      }
    },
    {
      name: "ExecutiveSummary - Risk",
      component: (key: string) => (
        <ExecutiveSummary
          key={key}
          title="Risk Assessment"
          items={[
            { label: "Status", text: "Low volatility environment", color: "green" },
            { label: "Score", text: "2.1/10 risk level", color: "blue" },
            { label: "Action", text: "Maintain current allocation", color: "purple" }
          ]}
          variant={getBestVariant('ExecutiveSummary', 'quarter_width')}
        />
      )
    },
    {
      name: "ExecutiveSummary - Performance",
      component: (key: string) => (
        <ExecutiveSummary
          key={key}
          title="Performance Summary"
          items={[
            { label: "Returns", text: "+18.7% quarterly performance", color: "green" },
            { label: "Benchmark", text: "Outperforming by 420bps", color: "blue" },
            { label: "Strategy", text: "Continue current approach", color: "purple" }
          ]}
          variant={getBestVariant('ExecutiveSummary', 'quarter_width')}
        />
      )
    },
    {
      name: "CalloutNote - Warning",
      component: (key: string) => (
        <CalloutNote
          key={key}
          type="warning"
          title="Risk Alert"
          content="Volatility spike detected in sector allocation."
          variant="compact"
        />
      )
    },
    {
      name: "CalloutNote - Success",
      component: (key: string) => (
        <CalloutNote
          key={key}
          type="success"
          title="Target Met"
          content="Portfolio exceeded quarterly return objectives."
          variant="compact"
        />
      )
    },
    {
      name: "CalloutNote - Info",
      component: (key: string) => (
        <CalloutNote
          key={key}
          type="info"
          title="Market Update"
          content="Economic indicators suggest continued growth trends."
          variant="compact"
        />
      )
    }
  ],
  half_width: [
    {
      name: "StatGroup - Healthcare",
      component: (key: string, position: string = 'half_width') => {
        const variant = getBestVariant('StatGroup', getSpaceType(position));
        const maxItems = getMaxItemsForPosition('StatGroup', position);
        return (
          <StatGroup
            key={key}
            title="Healthcare KPIs"
            stats={generateHealthcareStats(maxItems)}
            variant={variant}
            columns={2}
          />
        );
      }
    },
    {
      name: "StatGroup - Energy",
      component: (key: string, position: string = 'half_width') => {
        const variant = getBestVariant('StatGroup', getSpaceType(position));
        const maxItems = getMaxItemsForPosition('StatGroup', position);
        return (
          <StatGroup
            key={key}
            title="Energy Performance"
            stats={generateEnergyStats(maxItems)}
            variant={variant}
            columns={2}
          />
        );
      }
    },
    {
      name: "BulletList - Insights",
      component: (key: string) => (
        <BulletList
          key={key}
          title="Market Insights"
          items={[
            "Technology sector showing strong momentum with 18% quarterly gains",
            "Interest rate environment favorable for growth equities",
            "ESG integration improving risk-adjusted returns significantly"
          ]}
          variant="default"
        />
      )
    },
    {
      name: "BulletList - Risks",
      component: (key: string) => (
        <BulletList
          key={key}
          title="Risk Factors"
          items={[
            "Geopolitical tensions creating market volatility",
            "Inflation concerns persist despite recent improvements",
            "Currency fluctuations impacting international holdings"
          ]}
          variant="compact"
        />
      )
    },
    {
      name: "KeyValueTable - Financial",
      component: (key: string, position: string = 'half_width') => {
        const variant = getBestVariantForPosition('KeyValueTable', position);
        const maxItems = getMaxItemsForPosition('KeyValueTable', position);
        const data = [
          { metric: "Total AUM", value: "$4.2B", change: "+12.5%" },
          { metric: "YTD Return", value: "+16.8%", change: "+3.2%" },
          { metric: "Sharpe Ratio", value: "1.42", change: "+0.15%" },
          { metric: "Max Drawdown", value: "-3.8%", change: "+1.2%" }
        ].slice(0, maxItems);

        return (
          <KeyValueTable
            key={key}
            title="Financial Metrics"
            data={data}
            columns={[
              { key: "metric", label: "Metric", align: "left" },
              { key: "value", label: "Value", align: "right" },
              { key: "change", label: "QoQ Change", align: "right" }
            ]}
            variant={variant}
          />
        );
      }
    },
    {
      name: "KeyValueTable - Operational",
      component: (key: string, position: string = 'half_width') => {
        const variant = getBestVariantForPosition('KeyValueTable', position);
        const maxItems = getMaxItemsForPosition('KeyValueTable', position);
        const data = [
          { metric: "Active Positions", value: "247", status: "Normal" },
          { metric: "Trades Today", value: "89", status: "High" },
          { metric: "Cash Balance", value: "$45M", status: "Optimal" },
          { metric: "Allocation Drift", value: "2.1%", status: "Low" }
        ].slice(0, maxItems);

        return (
          <KeyValueTable
            key={key}
            title="Operational Stats"
            data={data}
            columns={[
              { key: "metric", label: "Metric", align: "left" },
              { key: "value", label: "Value", align: "center" },
              { key: "status", label: "Status", align: "right" }
            ]}
            variant={variant}
          />
        );
      }
    },
    {
      name: "PerformanceChart - Trend",
      component: (key: string) => (
        <div key={key} className="bg-white  rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Performance Chart</h3>
          <div className="h-32 bg-blue-50 rounded border border-blue-200 flex items-center justify-center">
            <div className="text-center">
              <div className="text-sm font-medium text-blue-700">6-Month Trend</div>
              <div className="text-lg font-bold text-blue-800">+18.7%</div>
              <div className="text-xs text-blue-600">Outperforming benchmark</div>
            </div>
          </div>
        </div>
      )
    },
    {
      name: "TechnicalAnalysis - Signals",
      component: (key: string) => (
        <div key={key} className="bg-white  rounded-lg p-4">
          <h3 className="text-sm font-medium text-gray-900 mb-3">Technical Analysis</h3>
          <div className="h-32 bg-green-50 rounded border border-green-200 flex items-center justify-center">
            <div className="text-center">
              <div className="text-sm font-medium text-green-700">Signal Strength</div>
              <div className="text-2xl font-bold text-green-800">STRONG BUY</div>
              <div className="text-xs text-green-600">RSI: 58 | MACD: Bullish</div>
            </div>
          </div>
        </div>
      )
    }
  ],
  two_thirds_width: [
    {
      name: "ComparisonTable",
      component: (key: string) => (
        <ComparisonTable
          key={key}
          title="Asset Comparison"
          entities={generateSampleEntities().slice(0, 3)}
          metrics={generateSampleMetrics().slice(0, 3)}
          data={generateSampleTableData()}
          variant="default"
        />
      )
    },
    {
      name: "StatGroup",
      component: (key: string) => (
        <StatGroup
          key={key}
          title="Extended Metrics"
          stats={generateEnergyStats(3)}
          variant="horizontal"
          columns={3}
        />
      )
    },
    {
      name: "RankedList",
      component: (key: string) => (
        <RankedList
          key={key}
          title="Top Performers"
          items={[
            { id: "1", name: "NVIDIA Corp", value: "+89.2%", subtitle: "Technology" },
            { id: "2", name: "Microsoft Corp", value: "+28.4%", subtitle: "Technology" },
            { id: "3", name: "Apple Inc", value: "+22.1%", subtitle: "Technology" }
          ]}
        />
      )
    }
  ],
  full_width: [
    {
      name: "SummaryConclusion - Portfolio",
      component: (key: string) => (
        <SummaryConclusion
          key={key}
          title="Q4 Portfolio Performance Summary"
          keyFindings={[
            "Portfolio outperformed benchmark by 340bps with strong risk-adjusted returns",
            "Technology sector concentration at 38% presents both opportunity and concentration risk",
            "ESG integration improved performance by 180bps while maintaining growth objectives",
            "International diversification reduced volatility by 12% quarter-over-quarter"
          ]}
          conclusion="Exceptional performance demonstrates successful strategy execution. Advanced analytics support continued growth with enhanced risk management protocols."
          nextSteps={[
            "Execute sector rebalancing to optimize concentration risk",
            "Deploy predictive analytics for systematic alpha generation",
            "Implement ESG-enhanced screening for new opportunities"
          ]}
          confidence="high"
          variant="default"
        />
      )
    },
    {
      name: "SummaryConclusion - Trading",
      component: (key: string) => (
        <SummaryConclusion
          key={key}
          title="Quantitative Trading Intelligence Report"
          keyFindings={[
            "Generated 247 high-conviction signals with 73.2% win rate across multi-factor model",
            "Momentum factor outperforming with +420bps alpha while mean reversion shows rotation opportunity",
            "Trade execution efficiency improved 23% through enhanced routing and timing algorithms",
            "Risk-adjusted returns up 340bps YTD with maximum drawdown contained to -2.1%"
          ]}
          conclusion="Advanced quantitative strategies delivering superior risk-adjusted performance through systematic signal generation and optimized execution."
          nextSteps={[
            "Increase allocation to momentum signals given current market regime",
            "Deploy enhanced execution algorithms for better fill rates",
            "Implement real-time factor rotation monitoring"
          ]}
          confidence="high"
        />
      )
    },
    {
      name: "ActionList - Portfolio",
      component: (key: string) => (
        <ActionList
          key={key}
          title="Portfolio Action Items"
          actions={[
            {
              id: "1",
              title: "Rebalance sector allocation",
              description: "Reduce technology concentration from 38% to target 32% over next 30 days",
              priority: "high",
              timeline: "immediate"
            },
            {
              id: "2",
              title: "Implement ESG screening",
              description: "Deploy enhanced ESG criteria for all new equity positions",
              priority: "medium",
              timeline: "short-term"
            },
            {
              id: "3",
              title: "Review international exposure",
              description: "Evaluate emerging markets allocation for diversification benefits",
              priority: "low",
              timeline: "medium-term"
            }
          ]}
          variant="detailed"
          showPriority={true}
        />
      )
    },
    {
      name: "ActionList - Trading",
      component: (key: string) => (
        <ActionList
          key={key}
          title="Trading System Improvements"
          actions={[
            {
              id: "1",
              title: "Upgrade execution algorithms",
              description: "Deploy machine learning-enhanced order routing for better fill rates",
              priority: "high",
              timeline: "immediate"
            },
            {
              id: "2",
              title: "Enhance risk monitoring",
              description: "Implement real-time portfolio risk analytics with dynamic alerts",
              priority: "medium",
              timeline: "short-term"
            },
            {
              id: "3",
              title: "Expand factor models",
              description: "Integrate alternative data sources for improved signal generation",
              priority: "medium",
              timeline: "medium-term"
            }
          ]}
          variant="compact"
          showPriority={false}
        />
      )
    },
    {
      name: "StatGroup - Tech Metrics",
      component: (key: string) => (
        <StatGroup
          key={key}
          title="Technology Performance Dashboard"
          stats={generateTechStats(4)}
          variant="horizontal"
          columns={4}
        />
      )
    },
    {
      name: "StatGroup - Financial Overview",
      component: (key: string) => (
        <StatGroup
          key={key}
          title="Financial Performance Overview"
          stats={generateFinancialStats(4)}
          variant="default"
          columns={4}
        />
      )
    }
  ]
};

// Space mapping for sub-layout components
const spaceMapping = {
  // Layout 1 (4x6 mixed)
  "halfWidthTopLeft": "half_width",
  "halfWidthTopRight": "half_width",
  "quarterWidthMiddleLeft": "quarter_width",
  "halfWidthMiddleCenter": "half_width",
  "quarterWidthMiddleRight": "quarter_width",
  "fullWidthBottom": "full_width",

  // Layout 2 (2x5)
  "leftPrimary": "half_width",
  "rightPrimary": "half_width",
  "leftSecondary": "half_width",
  "rightSecondary": "half_width",
  "fullWidthBottom2x5": "full_width",

  // Layout 3 (3x4)
  "thirdWidthTop1": "quarter_width",
  "thirdWidthTop2": "quarter_width",
  "thirdWidthTop3": "quarter_width",
  "thirdWidthMiddle1": "quarter_width",
  "thirdWidthMiddle2": "quarter_width",
  "thirdWidthMiddle3": "quarter_width",
  "fullWidthBottom3x4": "full_width",

  // Layout 4 (4x3)
  "quarterWidthTopLeft4x3": "quarter_width",
  "halfWidthTop4x3": "half_width",
  "quarterWidthTopRight4x3": "quarter_width",
  "quarterWidthLeft4x3": "quarter_width",
  "halfWidthCenter4x3": "half_width",
  "quarterWidthRight4x3": "quarter_width",
  "fullWidthBottom4x3": "full_width",

  // Layout 5 (2x3)
  "top5": "full_width",
  "bottomLeft5": "half_width",
  "bottomRight5": "half_width",

  // Layout 6 (2x2 quadrants)
  "topLeft6": "half_width",
  "topRight6": "half_width",
  "bottomLeft6": "half_width",
  "bottomRight6": "half_width",

  // Layout 7 (3x2)
  "top7": "full_width",
  "bottomLeft7": "quarter_width",
  "bottomCenter7": "quarter_width",
  "bottomRight7": "quarter_width",

  // Layout 8 (3x3 mixed)
  "middleLeft8": "quarter_width",
  "middleCenter8": "quarter_width",
  "middleRight8": "quarter_width",
  "bottom8": "two_thirds_width",

  // Layout 9 (4x3 mixed)
  "middleLeft9": "quarter_width",
  "middleCenter9": "quarter_width",
  "middleRight1_9": "quarter_width",
  "middleRight2_9": "quarter_width",

  // Layout 10 (4x3 mixed)
  "middleRight1_10": "quarter_width",
  "middleRight2_10": "quarter_width",

  // Layout 11 (5x4 mixed)  
  "middleCenter1_11": "quarter_width",
  "middleCenter2_11": "quarter_width",
  "middleCenter3_11": "quarter_width",
  "bottom1_11": "full_width",
  "bottom2_11": "full_width",

  // Layout 12 (4x3 mixed)
  "middleCenter1_12": "quarter_width",
  "middleCenter2_12": "quarter_width"
};

export const getRandomComponent = (spaceName: string, key: string = "random") => {
  const spaceType = spaceMapping[spaceName as keyof typeof spaceMapping] || "full_width";
  const availableComponents = componentGenerators[spaceType as keyof typeof componentGenerators] || componentGenerators.full_width;

  const randomIndex = Math.floor(Math.random() * availableComponents.length);
  const selectedComponent = availableComponents[randomIndex];

  return selectedComponent.component(key);
};

export const getRandomComponentsForLayout = (layoutPositions: string[]) => {
  const components: Record<string, React.ReactNode> = {};
  const usedComponents: Set<string> = new Set();

  layoutPositions.forEach(position => {
    components[position] = getRandomComponentUnique(position, `${position}-${Date.now()}`, usedComponents);
  });

  return components;
};

export const getRandomComponentsWithIndices = (layoutPositions: string[]) => {
  const components: Record<string, React.ReactNode> = {};
  const indices: Record<string, number> = {};
  const usedComponents: Set<string> = new Set();

  layoutPositions.forEach(position => {
    const { component, index } = getRandomComponentUniqueWithIndex(position, `${position}-${Date.now()}`, usedComponents);
    components[position] = component;
    indices[position] = index;
  });

  return { components, indices };
};

export const getRandomComponentsFromIndices = (layoutPositions: string[], indices: Record<string, number>) => {
  const components: Record<string, React.ReactNode> = {};

  layoutPositions.forEach(position => {
    const index = indices[position];
    if (index !== undefined) {
      components[position] = getComponentByIndex(position, index, `${position}-restored`);
    }
  });

  return components;
};

const getRandomComponentUnique = (spaceName: string, key: string, usedComponents: Set<string>) => {
  const spaceType = spaceMapping[spaceName as keyof typeof spaceMapping] || "full_width";
  const availableComponents = componentGenerators[spaceType as keyof typeof componentGenerators] || componentGenerators.full_width;

  // Filter out already used components
  const unusedComponents = availableComponents.filter(comp => !usedComponents.has(comp.name));

  // If all components are used, reset and use any component (fallback)
  const componentsToChooseFrom = unusedComponents.length > 0 ? unusedComponents : availableComponents;

  const randomIndex = Math.floor(Math.random() * componentsToChooseFrom.length);
  const selectedComponent = componentsToChooseFrom[randomIndex];

  // Mark this component as used
  usedComponents.add(selectedComponent.name);

  return selectedComponent.component(key, spaceName);
};

const getRandomComponentUniqueWithIndex = (spaceName: string, key: string, usedComponents: Set<string>) => {
  const spaceType = spaceMapping[spaceName as keyof typeof spaceMapping] || "full_width";
  const availableComponents = componentGenerators[spaceType as keyof typeof componentGenerators] || componentGenerators.full_width;

  // Filter out already used components
  const unusedComponents = availableComponents.filter(comp => !usedComponents.has(comp.name));

  // If all components are used, reset and use any component (fallback)
  const componentsToChooseFrom = unusedComponents.length > 0 ? unusedComponents : availableComponents;

  const randomIndex = Math.floor(Math.random() * componentsToChooseFrom.length);
  const selectedComponent = componentsToChooseFrom[randomIndex];

  // Mark this component as used
  usedComponents.add(selectedComponent.name);

  // Find original index in the full array
  const originalIndex = availableComponents.findIndex(comp => comp.name === selectedComponent.name);

  return {
    component: selectedComponent.component(key, spaceName),
    index: originalIndex
  };
};

const getComponentByIndex = (spaceName: string, index: number, key: string) => {
  const spaceType = spaceMapping[spaceName as keyof typeof spaceMapping] || "full_width";
  const availableComponents = componentGenerators[spaceType as keyof typeof componentGenerators] || componentGenerators.full_width;

  if (index >= 0 && index < availableComponents.length) {
    const selectedComponent = availableComponents[index];
    return selectedComponent.component(key, spaceName);
  }

  // Fallback to first component if index is invalid
  return availableComponents[0]?.component(key, spaceName) || null;
};

// Utility to get all available components for a space
export const getAvailableComponentsForSpace = (spaceName: string) => {
  const spaceType = spaceMapping[spaceName as keyof typeof spaceMapping] || "full_width";
  return componentGenerators[spaceType as keyof typeof componentGenerators] || componentGenerators.full_width;
};