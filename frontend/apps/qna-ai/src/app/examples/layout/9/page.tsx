'use client';

import { useState } from 'react';
import Layout9 from '@/components/insights/layout/Layout9';
import SummaryConclusion from '@/components/insights/SummaryConclusion';
import Section from '@/components/insights/Section';
import ComparisonTable from '@/components/insights/ComparisonTable';
import { getRandomComponentsForLayout } from '@/components/insights/layout/utils/layout-randomizer';

export default function Layout9Demo() {
  const layout9Positions = ['top', 'middleLeft9', 'middleCenter9', 'middleRight1_9', 'middleRight2_9', 'bottom8'];
  const [randomComponents, setRandomComponents] = useState<Record<string, React.ReactNode>>({});
  const [useRandom, setUseRandom] = useState(false);

  const generateRandomLayout = () => {
    const newComponents = getRandomComponentsForLayout(layout9Positions);
    setRandomComponents(newComponents);
    setUseRandom(true);
  };

  const resetToOriginal = () => {
    setUseRandom(false);
  };

  const originalComponents = {
    top: (
      <SummaryConclusion
        title="Advanced Analytics Summary"
        keyFindings={[
          "Statistical analysis reveals 92% correlation between tech sector performance and portfolio returns",
          "Monte Carlo simulation shows 85% probability of positive returns over next 12 months",
          "Sharpe ratio optimization suggests reducing energy exposure from 8.1% to 4.5%",
          "Factor analysis identifies momentum and quality as primary return drivers"
        ]}
        conclusion="Advanced analytics confirm portfolio's strong risk-adjusted performance while highlighting optimization opportunities. Statistical models support maintaining growth tilt with tactical rebalancing in underperforming sectors."
        nextSteps={[
          "Execute Monte Carlo-based position sizing for new investments",
          "Implement factor-based rebalancing strategy",
          "Monitor correlation breakdown points for risk management"
        ]}
        confidence="high"
      />
    ),
    middleLeft9: (
      <Section title="Performance Trend">
        <div className="h-full flex flex-col">
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-2">
            <div className="text-center">
              <div className="text-sm font-semibold text-gray-700 mb-1">Rolling Returns</div>
              <div className="text-xs text-gray-500 mb-2">12-Month Window</div>
              <div className="bg-white p-2 rounded shadow-sm text-xs">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-blue-600">Mean:</span>
                    <span className="font-medium">+16.2%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Trend:</span>
                    <span className="font-medium text-green-600">↗ Up</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="text-xs text-center">
            <span className="text-green-600 font-medium">Bullish Trend</span>
          </div>
        </div>
      </Section>
    ),
    middleCenter9: (
      <Section title="Return Distribution">
        <div className="h-full flex flex-col">
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-2">
            <div className="text-center">
              <div className="text-sm font-semibold text-gray-700 mb-1">Monthly Returns</div>
              <div className="text-xs text-gray-500 mb-2">Frequency Analysis</div>
              <div className="bg-white p-2 rounded shadow-sm text-xs">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Skew:</span>
                    <span className="font-medium">0.23</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Kurtosis:</span>
                    <span className="font-medium">2.1</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="text-xs text-center">
            <span className="text-blue-600 font-medium">Normal Distribution</span>
          </div>
        </div>
      </Section>
    ),
    middleRight1_9: (
      <Section title="Correlation Matrix">
        <div className="h-full flex flex-col">
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-2">
            <div className="text-center">
              <div className="text-sm font-semibold text-gray-700 mb-1">Asset Correlation</div>
              <div className="text-xs text-gray-500 mb-2">Heat Map</div>
              <div className="bg-white p-2 rounded shadow-sm text-xs">
                <div className="grid grid-cols-2 gap-1 text-center">
                  <div className="bg-red-100 p-1 rounded">0.92</div>
                  <div className="bg-yellow-100 p-1 rounded">0.45</div>
                  <div className="bg-green-100 p-1 rounded">0.23</div>
                  <div className="bg-blue-100 p-1 rounded">-0.12</div>
                </div>
              </div>
            </div>
          </div>
          <div className="text-xs text-center">
            <span className="text-orange-600 font-medium">High Correlation</span>
          </div>
        </div>
      </Section>
    ),
    middleRight2_9: (
      <Section title="Risk vs Return">
        <div className="h-full flex flex-col">
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-2">
            <div className="text-center">
              <div className="text-sm font-semibold text-gray-700 mb-1">Scatter Plot</div>
              <div className="text-xs text-gray-500 mb-2">Volatility vs Return</div>
              <div className="bg-white p-2 rounded shadow-sm text-xs">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-gray-600">R²:</span>
                    <span className="font-medium">0.73</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Slope:</span>
                    <span className="font-medium">1.12</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="text-xs text-center">
            <span className="text-purple-600 font-medium">Strong Relationship</span>
          </div>
        </div>
      </Section>
    ),
    bottom8: (
      <ComparisonTable
        title="Comprehensive Holdings Analysis - Top 15 Positions"
        entities={[
          { id: "nvda", name: "NVIDIA Corp", subtitle: "8.2% • Technology • Large Cap" },
          { id: "msft", name: "Microsoft Corp", subtitle: "7.8% • Technology • Large Cap" },
          { id: "aapl", name: "Apple Inc", subtitle: "6.4% • Technology • Large Cap" },
          { id: "amzn", name: "Amazon.com Inc", subtitle: "5.9% • Consumer Disc. • Large Cap" },
          { id: "googl", name: "Alphabet Inc", subtitle: "4.3% • Technology • Large Cap" },
          { id: "tsla", name: "Tesla Inc", subtitle: "3.8% • Consumer Disc. • Large Cap" },
          { id: "jnj", name: "Johnson & Johnson", subtitle: "3.2% • Healthcare • Large Cap" },
          { id: "v", name: "Visa Inc", subtitle: "2.9% • Financials • Large Cap" }
        ]}
        metrics={[
          { id: "ytd_return", name: "YTD Return", format: "percentage" },
          { id: "contribution", name: "Contribution", format: "percentage" },
          { id: "beta", name: "Beta", format: "number" },
          { id: "pe_ratio", name: "P/E", format: "number" },
          { id: "volatility", name: "Volatility", format: "percentage" },
          { id: "sharpe", name: "Sharpe", format: "number" }
        ]}
        data={{
          "nvda": { 
            "ytd_return": "+189.5%", 
            "contribution": "+3.71%", 
            "beta": "1.68", 
            "pe_ratio": "68.5",
            "volatility": "45.2%",
            "sharpe": "1.42"
          },
          "msft": { 
            "ytd_return": "+28.4%", 
            "contribution": "+2.21%", 
            "beta": "0.89", 
            "pe_ratio": "33.2",
            "volatility": "22.1%",
            "sharpe": "1.28"
          },
          "aapl": { 
            "ytd_return": "+22.1%", 
            "contribution": "+1.41%", 
            "beta": "1.12", 
            "pe_ratio": "29.8",
            "volatility": "18.2%",
            "sharpe": "1.21"
          },
          "amzn": { 
            "ytd_return": "+31.8%", 
            "contribution": "+1.88%", 
            "beta": "1.34", 
            "pe_ratio": "42.1",
            "volatility": "28.7%",
            "sharpe": "1.11"
          },
          "googl": { 
            "ytd_return": "+26.7%", 
            "contribution": "+1.15%", 
            "beta": "1.05", 
            "pe_ratio": "24.3",
            "volatility": "24.5%",
            "sharpe": "1.09"
          },
          "tsla": { 
            "ytd_return": "+15.3%", 
            "contribution": "+0.58%", 
            "beta": "2.21", 
            "pe_ratio": "58.7",
            "volatility": "52.3%",
            "sharpe": "0.29"
          },
          "jnj": { 
            "ytd_return": "+8.9%", 
            "contribution": "+0.28%", 
            "beta": "0.67", 
            "pe_ratio": "15.2",
            "volatility": "12.1%",
            "sharpe": "0.74"
          },
          "v": { 
            "ytd_return": "+12.4%", 
            "contribution": "+0.36%", 
            "beta": "0.98", 
            "pe_ratio": "31.8",
            "volatility": "19.3%",
            "sharpe": "0.64"
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

    <Layout9
      title={
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Advanced Portfolio Analytics Dashboard {useRandom && '(Randomized)'}</h1>
          <p className="text-gray-600 mt-1">Multi-Dimensional Analysis • Statistical Modeling • Comprehensive Data</p>
        </div>
      }
      
      top={activeComponents.top}
      middleLeft={activeComponents.middleLeft9}
      middleCenter={activeComponents.middleCenter9}
      middleRight1={activeComponents.middleRight1_9}
      middleRight2={activeComponents.middleRight2_9}
      bottom={activeComponents.bottom8}
    />
    </>
  );
}