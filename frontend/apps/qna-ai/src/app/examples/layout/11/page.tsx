'use client';

import { useState } from 'react';
import Layout11 from '@/components/insights/layout/Layout11';
import SummaryConclusion from '@/components/insights/SummaryConclusion';
import StatGroup from '@/components/insights/StatGroup';
import Section from '@/components/insights/Section';
import MatrixTable from '@/components/insights/MatrixTable';
import ComparisonTable from '@/components/insights/ComparisonTable';
import { getRandomComponentsForLayout } from '@/components/insights/layout/utils/layout-randomizer';

export default function Layout11Demo() {
  const layout11Positions = ['top', 'middleLeft', 'middleCenter1_11', 'middleCenter2_11', 'middleCenter3_11', 'middleRight', 'bottom1_11', 'bottom2_11'];
  const [randomComponents, setRandomComponents] = useState<Record<string, React.ReactNode>>({});
  const [useRandom, setUseRandom] = useState(false);

  const generateRandomLayout = () => {
    const newComponents = getRandomComponentsForLayout(layout11Positions);
    setRandomComponents(newComponents);
    setUseRandom(true);
  };

  const resetToOriginal = () => {
    setUseRandom(false);
  };

  const originalComponents = {
    top: (
      <SummaryConclusion
        title="Q4 Portfolio Intelligence Summary"
        keyFindings={[
          "Enterprise portfolio outperformed benchmark by 340bps with $2.3B total AUM growth",
          "Technology sector concentration at 38% presents both opportunity and concentration risk",
          "ESG screening improved risk-adjusted returns by 180bps while maintaining growth objectives",
          "Alternative investment allocation optimization identified $450M rebalancing opportunity"
        ]}
        conclusion="Comprehensive multi-level analysis confirms strong portfolio performance across strategic, tactical, and operational metrics. Advanced analytics support continued growth strategy with enhanced risk management protocols."
        nextSteps={[
          "Execute sector rebalancing strategy to optimize concentration risk",
          "Implement ESG-enhanced screening for new investment opportunities",
          "Deploy predictive analytics for systematic alpha generation"
        ]}
        confidence="very-high"
      />
    ),
    middleLeft: (
      <StatGroup
        title="Portfolio KPIs"
        stats={[
          {
            label: "Total AUM",
            value: "$2.3B",
            change: "+12.8%",
            changeType: "positive"
          },
          {
            label: "Alpha",
            value: "340bps",
            change: "+85bps",
            changeType: "positive"
          },
          {
            label: "Sharpe",
            value: "1.82",
            change: "+0.31",
            changeType: "positive"
          },
          {
            label: "Max DD",
            value: "-4.2%",
            change: "-1.1%",
            changeType: "positive"
          }
        ]}
        columns={2}
        variant="compact"
      />
    ),
    middleCenter1_11: (
      <Section title="Performance Attribution">
        <div className="h-full flex flex-col">
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-2">
            <div className="text-center">
              <div className="text-sm font-semibold text-gray-700 mb-1">Rolling Alpha</div>
              <div className="text-xs text-gray-500 mb-2">36-Month Analysis</div>
              <div className="bg-white p-2 rounded shadow-sm text-xs">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-blue-600">Current:</span>
                    <span className="font-medium">340bps</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Trend:</span>
                    <span className="font-medium text-green-600">↗ Rising</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="text-xs text-center">
            <span className="text-green-600 font-medium">Outperforming</span>
          </div>
        </div>
      </Section>
    ),
    middleCenter2_11: (
      <Section title="Return Distribution">
        <div className="h-full flex flex-col">
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-2">
            <div className="text-center">
              <div className="text-sm font-semibold text-gray-700 mb-1">Monthly Returns</div>
              <div className="text-xs text-gray-500 mb-2">Statistical Analysis</div>
              <div className="bg-white p-2 rounded shadow-sm text-xs">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-gray-600">VaR 95%:</span>
                    <span className="font-medium">-2.8%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Skew:</span>
                    <span className="font-medium">0.12</span>
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
    middleCenter3_11: (
      <Section title="Risk Heatmap">
        <div className="h-full flex flex-col">
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-2">
            <div className="text-center">
              <div className="text-sm font-semibold text-gray-700 mb-1">Factor Exposure</div>
              <div className="text-xs text-gray-500 mb-2">Risk Decomposition</div>
              <div className="bg-white p-2 rounded shadow-sm text-xs">
                <div className="grid grid-cols-2 gap-1 text-center">
                  <div className="bg-green-100 p-1 rounded text-xs">Quality</div>
                  <div className="bg-yellow-100 p-1 rounded text-xs">Growth</div>
                  <div className="bg-red-100 p-1 rounded text-xs">Value</div>
                  <div className="bg-blue-100 p-1 rounded text-xs">Size</div>
                </div>
              </div>
            </div>
          </div>
          <div className="text-xs text-center">
            <span className="text-orange-600 font-medium">Factor Balanced</span>
          </div>
        </div>
      </Section>
    ),
    middleRight: (
      <Section title="Risk vs Return Matrix">
        <div className="h-full flex flex-col">
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-2">
            <div className="text-center">
              <div className="text-sm font-semibold text-gray-700 mb-1">Portfolio Positioning</div>
              <div className="text-xs text-gray-500 mb-2">Efficient Frontier Analysis</div>
              <div className="bg-white p-2 rounded shadow-sm text-xs">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Risk:</span>
                    <span className="font-medium">12.8%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Return:</span>
                    <span className="font-medium">18.4%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Position:</span>
                    <span className="font-medium text-green-600">Efficient</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="text-xs text-center mt-2">
            <span className="text-purple-600 font-medium">Optimal Zone</span>
          </div>
        </div>
      </Section>
    ),
    bottom1_11: (
      <ComparisonTable
        title="Sector Performance Breakdown - Strategic Allocation Analysis"
        entities={[
          { id: "tech", name: "Technology", subtitle: "38.2% • Growth Focus • High Conviction" },
          { id: "health", name: "Healthcare", subtitle: "18.7% • Defensive Growth • Innovation" },
          { id: "finance", name: "Financial Services", subtitle: "15.1% • Value Opportunity • Cyclical" },
          { id: "consumer", name: "Consumer Discretionary", subtitle: "12.4% • Quality Selection • Brands" },
          { id: "industrial", name: "Industrials", subtitle: "8.9% • Infrastructure • Automation" },
          { id: "materials", name: "Materials", subtitle: "4.2% • Commodity Exposure • Tactical" },
          { id: "energy", name: "Energy", subtitle: "2.5% • Transition Play • ESG Screened" }
        ]}
        metrics={[
          { id: "allocation", name: "Allocation", format: "percentage" },
          { id: "return", name: "Return", format: "percentage" },
          { id: "alpha", name: "Alpha", format: "number" },
          { id: "sharpe", name: "Sharpe", format: "number" },
          { id: "risk", name: "Risk", format: "percentage" }
        ]}
        data={{
          "tech": { 
            "allocation": "38.2%", 
            "return": "+24.7%", 
            "alpha": "420bps",
            "sharpe": "1.94",
            "risk": "16.2%"
          },
          "health": { 
            "allocation": "18.7%", 
            "return": "+16.3%", 
            "alpha": "180bps",
            "sharpe": "1.67",
            "risk": "11.8%"
          },
          "finance": { 
            "allocation": "15.1%", 
            "return": "+19.8%", 
            "alpha": "340bps",
            "sharpe": "1.52",
            "risk": "18.4%"
          },
          "consumer": { 
            "allocation": "12.4%", 
            "return": "+14.2%", 
            "alpha": "120bps",
            "sharpe": "1.38",
            "risk": "13.7%"
          },
          "industrial": { 
            "allocation": "8.9%", 
            "return": "+21.5%", 
            "alpha": "280bps",
            "sharpe": "1.61",
            "risk": "15.9%"
          },
          "materials": { 
            "allocation": "4.2%", 
            "return": "+8.7%", 
            "alpha": "-80bps",
            "sharpe": "0.94",
            "risk": "22.1%"
          },
          "energy": { 
            "allocation": "2.5%", 
            "return": "+12.1%", 
            "alpha": "-120bps",
            "sharpe": "0.87",
            "risk": "28.3%"
          }
        }}
      />
    ),
    bottom2_11: (
      <ComparisonTable
        title="Detailed Holdings Analysis - Top 20 Positions with Risk Metrics"
        entities={[
          { id: "msft", name: "Microsoft Corporation", subtitle: "4.8% • MSFT • Technology • $428.50" },
          { id: "aapl", name: "Apple Inc.", subtitle: "4.2% • AAPL • Technology • $189.25" },
          { id: "nvda", name: "NVIDIA Corporation", subtitle: "3.9% • NVDA • Technology • $875.30" },
          { id: "googl", name: "Alphabet Inc. Class A", subtitle: "3.6% • GOOGL • Technology • $142.80" },
          { id: "amzn", name: "Amazon.com Inc.", subtitle: "3.1% • AMZN • Consumer Disc. • $151.90" },
          { id: "tsla", name: "Tesla Inc.", subtitle: "2.8% • TSLA • Consumer Disc. • $248.42" },
          { id: "jnj", name: "Johnson & Johnson", subtitle: "2.5% • JNJ • Healthcare • $156.78" },
          { id: "v", name: "Visa Inc. Class A", subtitle: "2.3% • V • Financial Services • $272.45" }
        ]}
        metrics={[
          { id: "weight", name: "Weight", format: "percentage" },
          { id: "return_1y", name: "1Y Return", format: "percentage" },
          { id: "beta", name: "Beta", format: "number" },
          { id: "pe_ratio", name: "P/E", format: "number" },
          { id: "volatility", name: "Volatility", format: "percentage" },
          { id: "var_95", name: "VaR 95%", format: "percentage" }
        ]}
        data={{
          "msft": { 
            "weight": "4.8%", 
            "return_1y": "+28.4%", 
            "beta": "0.89",
            "pe_ratio": "33.2",
            "volatility": "22.1%",
            "var_95": "-3.2%"
          },
          "aapl": { 
            "weight": "4.2%", 
            "return_1y": "+22.1%", 
            "beta": "1.12",
            "pe_ratio": "29.8",
            "volatility": "18.2%",
            "var_95": "-2.8%"
          },
          "nvda": { 
            "weight": "3.9%", 
            "return_1y": "+189.5%", 
            "beta": "1.68",
            "pe_ratio": "68.5",
            "volatility": "45.2%",
            "var_95": "-6.8%"
          },
          "googl": { 
            "weight": "3.6%", 
            "return_1y": "+26.7%", 
            "beta": "1.05",
            "pe_ratio": "24.3",
            "volatility": "24.5%",
            "var_95": "-3.7%"
          },
          "amzn": { 
            "weight": "3.1%", 
            "return_1y": "+31.8%", 
            "beta": "1.34",
            "pe_ratio": "42.1",
            "volatility": "28.7%",
            "var_95": "-4.3%"
          },
          "tsla": { 
            "weight": "2.8%", 
            "return_1y": "+15.3%", 
            "beta": "2.21",
            "pe_ratio": "58.7",
            "volatility": "52.3%",
            "var_95": "-7.9%"
          },
          "jnj": { 
            "weight": "2.5%", 
            "return_1y": "+8.9%", 
            "beta": "0.67",
            "pe_ratio": "15.2",
            "volatility": "12.1%",
            "var_95": "-1.8%"
          },
          "v": { 
            "weight": "2.3%", 
            "return_1y": "+12.4%", 
            "beta": "0.98",
            "pe_ratio": "31.8",
            "volatility": "19.3%",
            "var_95": "-2.9%"
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

    <Layout11
      title={
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Enterprise Portfolio Intelligence Platform {useRandom && '(Randomized)'}</h1>
          <p className="text-gray-600 mt-1">Multi-Level Analysis • Sector Intelligence • Granular Data • Risk Management</p>
        </div>
      }
      
      top={activeComponents.top}
      middleLeft={activeComponents.middleLeft}
      middleCenter1={activeComponents.middleCenter1_11}
      middleCenter2={activeComponents.middleCenter2_11}
      middleCenter3={activeComponents.middleCenter3_11}
      middleRight={activeComponents.middleRight}
      bottom1={activeComponents.bottom1_11}
      bottom2={activeComponents.bottom2_11}
    />
    </>
  );
}