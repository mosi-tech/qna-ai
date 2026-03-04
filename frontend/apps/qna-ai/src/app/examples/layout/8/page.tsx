'use client';

import { useState } from 'react';
import Layout8 from '@/components/insights/layout/Layout8';
import SummaryConclusion from '@/components/insights/SummaryConclusion';
import StatGroup from '@/components/insights/StatGroup';
import Section from '@/components/insights/Section';
import ComparisonTable from '@/components/insights/ComparisonTable';
import { getRandomComponentsForLayout } from '@/components/insights/layout/utils/layout-randomizer';

export default function Layout8Demo() {
  const layout8Positions = ['top', 'middleLeft8', 'middleCenter8', 'middleRight8', 'bottom8'];
  const [randomComponents, setRandomComponents] = useState<Record<string, React.ReactNode>>({});
  const [useRandom, setUseRandom] = useState(false);

  const generateRandomLayout = () => {
    const newComponents = getRandomComponentsForLayout(layout8Positions);
    setRandomComponents(newComponents);
    setUseRandom(true);
  };

  const resetToOriginal = () => {
    setUseRandom(false);
  };

  const originalComponents = {
    top: (
      <SummaryConclusion
        title="Portfolio Performance Summary"
        keyFindings={[
          "Portfolio achieved +18.4% YTD returns, outperforming S&P 500 benchmark by +4.2%",
          "Technology sector overweight (28.5%) contributed +3.7% to performance alpha",
          "Risk metrics remain conservative with Sharpe ratio of 1.34 and max drawdown of -8.2%",
          "Strong momentum across growth factors with 78% earnings beat rate in holdings"
        ]}
        conclusion="The portfolio demonstrates exceptional risk-adjusted performance with strategic sector allocation driving outperformance. Technology overweight position has proven successful, while defensive positioning in healthcare provides downside protection."
        nextSteps={[
          "Consider profit-taking in technology positions above 30% allocation",
          "Increase international exposure for diversification benefits",
          "Monitor interest rate sensitivity as yields approach 4.5% threshold"
        ]}
        confidence="high"
      />
    ),
    middleLeft8: (
      <StatGroup
        title="Key Metrics"
        stats={[
          { label: "Portfolio Value", value: "$3.2M", format: "currency" },
          { label: "YTD Return", value: "+18.4%", changeType: "positive", format: "percentage" },
          { label: "Sharpe Ratio", value: "1.34", format: "number" },
          { label: "Max Drawdown", value: "-8.2%", changeType: "negative", format: "percentage" },
          { label: "Beta", value: "1.12", format: "number" },
          { label: "Alpha", value: "+4.2%", changeType: "positive", format: "percentage" }
        ]}
        columns={2}
        variant="compact"
      />
    ),
    middleCenter8: (
      <Section title="Performance Timeline">
        <div className="h-full flex flex-col">
          {/* Line chart placeholder */}
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-3">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-700 mb-2">12-Month Returns</div>
              <div className="text-sm text-gray-500 mb-3">Portfolio vs S&P 500</div>
              <div className="bg-white p-3 rounded shadow-sm text-xs">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-blue-600">■ Portfolio:</span>
                    <span className="font-medium">+18.4%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">■ Benchmark:</span>
                    <span className="font-medium">+14.2%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-green-600">■ Alpha:</span>
                    <span className="font-medium">+4.2%</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Timeline metrics */}
          <div className="grid grid-cols-3 gap-2 text-xs">
            <div className="bg-blue-50 p-2 rounded text-center">
              <div className="font-medium text-blue-800">1M</div>
              <div className="text-blue-700">+2.8%</div>
            </div>
            <div className="bg-green-50 p-2 rounded text-center">
              <div className="font-medium text-green-800">3M</div>
              <div className="text-green-700">+8.1%</div>
            </div>
            <div className="bg-purple-50 p-2 rounded text-center">
              <div className="font-medium text-purple-800">6M</div>
              <div className="text-purple-700">+12.5%</div>
            </div>
          </div>
        </div>
      </Section>
    ),
    middleRight8: (
      <Section title="Return Distribution">
        <div className="h-full flex flex-col">
          {/* Histogram placeholder */}
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-3">
            <div className="text-center">
              <div className="text-lg font-semibold text-gray-700 mb-2">Monthly Returns</div>
              <div className="text-sm text-gray-500 mb-3">Distribution Analysis</div>
              <div className="bg-white p-3 rounded shadow-sm text-xs">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Mean:</span>
                    <span className="font-medium">+1.4%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Std Dev:</span>
                    <span className="font-medium">4.2%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Skewness:</span>
                    <span className="font-medium">0.23</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          {/* Distribution stats */}
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-green-50 p-2 rounded text-center">
              <div className="font-medium text-green-800">Win Rate</div>
              <div className="text-green-700">67%</div>
            </div>
            <div className="bg-orange-50 p-2 rounded text-center">
              <div className="font-medium text-orange-800">Volatility</div>
              <div className="text-orange-700">15.8%</div>
            </div>
          </div>
        </div>
      </Section>
    ),
    bottom8: (
      <ComparisonTable
        title="Top 10 Holdings Detailed Analysis"
        entities={[
          { id: "nvda", name: "NVIDIA Corp", subtitle: "8.2% • Technology" },
          { id: "msft", name: "Microsoft Corp", subtitle: "7.8% • Technology" },
          { id: "aapl", name: "Apple Inc", subtitle: "6.4% • Technology" },
          { id: "amzn", name: "Amazon.com Inc", subtitle: "5.9% • Consumer Disc." },
          { id: "googl", name: "Alphabet Inc", subtitle: "4.3% • Technology" }
        ]}
        metrics={[
          { id: "ytd_return", name: "YTD Return", format: "percentage" },
          { id: "contribution", name: "Contribution", format: "percentage" },
          { id: "pe_ratio", name: "P/E Ratio", format: "number" },
          { id: "market_cap", name: "Market Cap", format: "currency" }
        ]}
        data={{
          "nvda": { 
            "ytd_return": "+189.5%", 
            "contribution": "+3.71%", 
            "pe_ratio": "68.5", 
            "market_cap": "$1.8T" 
          },
          "msft": { 
            "ytd_return": "+28.4%", 
            "contribution": "+2.21%", 
            "pe_ratio": "33.2", 
            "market_cap": "$3.1T" 
          },
          "aapl": { 
            "ytd_return": "+22.1%", 
            "contribution": "+1.41%", 
            "pe_ratio": "29.8", 
            "market_cap": "$2.7T" 
          },
          "amzn": { 
            "ytd_return": "+31.8%", 
            "contribution": "+1.88%", 
            "pe_ratio": "42.1", 
            "market_cap": "$1.5T" 
          },
          "googl": { 
            "ytd_return": "+26.7%", 
            "contribution": "+1.15%", 
            "pe_ratio": "24.3", 
            "market_cap": "$2.1T" 
          }
        }}
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
            <h3 className="text-sm font-medium text-yellow-800">Layout Testing Controls - 3x3 Mixed Grid</h3>
            <p className="text-xs text-yellow-600">Test comprehensive analytics with varied component sizes</p>
          </div>
          <div className="flex gap-2">
            <button
              onClick={generateRandomLayout}
              className="px-3 py-1.5 bg-blue-600 text-white text-sm rounded hover:bg-blue-700 transition-colors"
            >
              🎲 Randomize Analytics
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
            🎯 Testing mixed component sizes in comprehensive dashboard layout
          </div>
        )}
      </div>

      <Layout8
        title={
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Comprehensive Portfolio Analytics Dashboard {useRandom && '(Randomized)'}</h1>
            <p className="text-gray-600 mt-1">Performance • Risk • Holdings • Market Analysis</p>
          </div>
        }
        
        top={activeComponents.top}
        middleLeft={activeComponents.middleLeft8}
        middleCenter={activeComponents.middleCenter8}
        middleRight={activeComponents.middleRight8}
        bottom={activeComponents.bottom8}
      />
    </>
  );
}