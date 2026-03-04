'use client';

import { useState } from 'react';
import Layout6 from '@/components/insights/layout/Layout6';
import SummaryConclusion from '@/components/insights/SummaryConclusion';
import Section from '@/components/insights/Section';
import ComparisonTable from '@/components/insights/ComparisonTable';
import MatrixTable from '@/components/insights/MatrixTable';
import { getRandomComponentsForLayout } from '@/components/insights/layout/utils/layout-randomizer';

export default function Layout6Demo() {
  const layout6Positions = ['topLeft6', 'topRight6', 'bottomLeft6', 'bottomRight6'];
  const [randomComponents, setRandomComponents] = useState<Record<string, React.ReactNode>>({});
  const [useRandom, setUseRandom] = useState(false);

  const generateRandomLayout = () => {
    const newComponents = getRandomComponentsForLayout(layout6Positions);
    setRandomComponents(newComponents);
    setUseRandom(true);
  };

  const resetToOriginal = () => {
    setUseRandom(false);
  };

  const originalComponents = {
    topLeft6: (
      <SummaryConclusion
        title="Risk Summary & Key Findings"
        keyFindings={[
          "Portfolio VaR (95%) stands at $42K, within acceptable risk tolerance",
          "Technology sector concentration at 28.5% creates single-factor risk exposure", 
          "Correlation with market increased to 0.89, reducing diversification benefits",
          "Maximum drawdown of -8.2% significantly lower than benchmark -12.1%"
        ]}
        conclusion="Overall risk profile remains conservative with controlled volatility at 15.8%. However, increased market correlation and technology concentration warrant attention. Recommend sector rebalancing to reduce single-factor exposure while maintaining growth orientation."
        nextSteps={[
          "Reduce technology allocation by 3-5% to mitigate concentration risk",
          "Add international diversification to reduce market correlation",
          "Implement defensive hedging strategies for downside protection"
        ]}
        confidence="high"
        variant="compact"
      />
    ),
    topRight6: (
      <Section title="Risk Trend Analysis" variant="default">
        <div className="space-y-4">
          <div className="h-32 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center">
            <span className="text-sm text-gray-500">VaR Trend Chart</span>
          </div>
          <div className="grid grid-cols-2 gap-2 text-sm">
            <div className="bg-red-50 p-2 rounded">
              <div className="font-medium text-red-800">Current VaR</div>
              <div className="text-red-700">$42K</div>
            </div>
            <div className="bg-yellow-50 p-2 rounded">
              <div className="font-medium text-yellow-800">Risk Limit</div>
              <div className="text-yellow-700">$50K</div>
            </div>
          </div>
        </div>
      </Section>
    ),
    bottomLeft6: (
      <ComparisonTable
        title="Sector Risk Breakdown"
        entities={[
          { id: "tech", name: "Technology", subtitle: "28.5% allocation" },
          { id: "health", name: "Healthcare", subtitle: "18.7% allocation" },
          { id: "finance", name: "Financial", subtitle: "15.2% allocation" }
        ]}
        metrics={[
          { id: "weight", name: "Weight", format: "percentage" },
          { id: "volatility", name: "Volatility", format: "percentage" },
          { id: "beta", name: "Beta", format: "number" }
        ]}
        data={{
          "tech": { "weight": "28.5%", "volatility": "18.2%", "beta": "1.23" },
          "health": { "weight": "18.7%", "volatility": "12.1%", "beta": "0.67" },
          "finance": { "weight": "15.2%", "volatility": "19.8%", "beta": "1.45" }
        }}
        variant="narrow"
      />
    ),
    bottomRight6: (
      <MatrixTable
        title="Correlation Matrix"
        matrix={[
          [1.00, 0.89, 0.76],
          [0.89, 1.00, 0.82],
          [0.76, 0.82, 1.00]
        ]}
        rowLabels={["Portfolio", "S&P 500", "NASDAQ"]}
        columnLabels={["Portfolio", "S&P 500", "NASDAQ"]}
        format="number"
        colorScale={true}
      />
    )
  };

  const activeComponents = useRandom ? randomComponents : originalComponents;

  return (
    <>
      {/* Randomizer Controls */}
      <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-medium text-yellow-800">Layout Testing Controls - 4 Quadrants</h3>
            <p className="text-xs text-yellow-600">Test components in half-width spaces (2x2 grid)</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={generateRandomLayout}
              className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
            >
              🎲 Randomize Quadrants
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
            🎯 Testing half-width component variants in quadrant layout
          </div>
        )}
      </div>

      <Layout6
        title={
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Portfolio Risk Analysis Dashboard {useRandom && '(Randomized)'}</h1>
            <p className="text-gray-600 mt-1">Risk Assessment • Performance Tracking • Correlation Analysis</p>
          </div>
        }
        
        topLeft={activeComponents.topLeft6}
        topRight={activeComponents.topRight6}
        bottomLeft={activeComponents.bottomLeft6}
        bottomRight={activeComponents.bottomRight6}
      />
    </>
  );
}