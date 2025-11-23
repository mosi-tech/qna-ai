'use client';

import { useState } from 'react';
import Layout5 from '@/components/insights/layout/Layout5';
import SummaryConclusion from '@/components/insights/SummaryConclusion';
import ComparisonTable from '@/components/insights/ComparisonTable';
import Section from '@/components/insights/Section';
import { getRandomComponentsForLayout } from '@/components/insights/layout/utils/layout-randomizer';

export default function Layout5Demo() {
  const layout5Positions = ['top5', 'bottomLeft5', 'bottomRight5'];
  const [randomComponents, setRandomComponents] = useState<Record<string, React.ReactNode>>({});
  const [useRandom, setUseRandom] = useState(false);

  const generateRandomLayout = () => {
    const newComponents = getRandomComponentsForLayout(layout5Positions);
    setRandomComponents(newComponents);
    setUseRandom(true);
  };

  const resetToOriginal = () => {
    setUseRandom(false);
  };
  const originalComponents = {
    top5: (
      <SummaryConclusion
        title="Executive Summary & Key Highlights"
        keyFindings={[
          "Technology sector led market gains with +32.1% quarterly performance, driven by AI infrastructure investments",
          "Portfolio outperformed S&P 500 by +4.2% with strong risk-adjusted returns (Sharpe ratio: 1.34)",
          "Energy sector underperformed (-4.2%) due to demand concerns and regulatory headwinds",
          "Healthcare allocation positioned defensively ahead of 2025 market uncertainties"
        ]}
        conclusion="Q4 2024 demonstrated exceptional technology sector leadership while highlighting the importance of diversified positioning. Our strategic overweight in AI infrastructure companies delivered significant alpha, validating our thesis on secular technology trends. Moving forward, we recommend maintaining tech exposure while adding defensive healthcare allocation."
        nextSteps={[
          "Rebalance energy exposure from 8.1% to 5.0% target allocation",
          "Increase healthcare sector to 21% for defensive positioning",
          "Evaluate emerging market opportunities in AI semiconductor supply chain"
        ]}
        confidence="high"
      />
    ),
    bottomLeft5: (
      <ComparisonTable
        title="Sector Performance Analysis"
        entities={[
          { id: "tech", name: "Technology", subtitle: "32.1% • Outperformer" },
          { id: "health", name: "Healthcare", subtitle: "18.7% • Stable" },
          { id: "finance", name: "Financial", subtitle: "12.4% • Moderate" },
          { id: "energy", name: "Energy", subtitle: "-4.2% • Underperformer" }
        ]}
        metrics={[
          { id: "return", name: "Q4 Return", format: "percentage" },
          { id: "volatility", name: "Volatility", format: "percentage" },
          { id: "sharpe", name: "Sharpe Ratio", format: "number" }
        ]}
        data={{
          "tech": { "return": "+32.1%", "volatility": "18.2%", "sharpe": "1.76" },
          "health": { "return": "+18.7%", "volatility": "12.1%", "sharpe": "1.54" },
          "finance": { "return": "+12.4%", "volatility": "15.8%", "sharpe": "0.78" },
          "energy": { "return": "-4.2%", "volatility": "24.3%", "sharpe": "-0.17" }
        }}
      />
    ),
    bottomRight5: (
      <Section title="Risk Assessment Outlook">
        <div className="space-y-4">
          <div className="h-32 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center">
            <span className="text-sm text-gray-500">Risk Matrix Chart</span>
          </div>
          <div className="text-sm text-gray-600">
            <p><strong>Overall Risk Level:</strong> Moderate</p>
            <p><strong>Key Risk Factors:</strong> Technology concentration, geopolitical tensions, interest rate sensitivity</p>
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

      <Layout5
        title={
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Q4 2024 Market Analysis Report {useRandom && '(Randomized)'}</h1>
            <p className="text-gray-600 mt-1">Sector Performance • Risk Assessment • Strategic Outlook</p>
          </div>
        }
        
        top={activeComponents.top5}
        bottomLeft={activeComponents.bottomLeft5}
        bottomRight={activeComponents.bottomRight5}
      />
    </>
  );
}