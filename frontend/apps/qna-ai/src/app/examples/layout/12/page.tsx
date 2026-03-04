'use client';

import { useState } from 'react';
import Layout12 from '@/components/insights/layout/Layout12';
import SummaryConclusion from '@/components/insights/SummaryConclusion';
import Section from '@/components/insights/Section';
import MatrixTable from '@/components/insights/MatrixTable';
import ComparisonTable from '@/components/insights/ComparisonTable';
import { getRandomComponentsForLayout } from '@/components/insights/layout/utils/layout-randomizer';

export default function Layout12Demo() {
  const layout12Positions = ['top', 'middleLeft', 'middleCenter1_12', 'middleCenter2_12', 'middleRight', 'bottomLeft', 'bottomRight'];
  const [randomComponents, setRandomComponents] = useState<Record<string, React.ReactNode>>({});
  const [useRandom, setUseRandom] = useState(false);

  const generateRandomLayout = () => {
    const newComponents = getRandomComponentsForLayout(layout12Positions);
    setRandomComponents(newComponents);
    setUseRandom(true);
  };

  const resetToOriginal = () => {
    setUseRandom(false);
  };

  const originalComponents = {
    top: (
      <SummaryConclusion
        title="Trading Performance & Signal Intelligence"
        keyFindings={[
          "Generated 247 high-conviction signals with 73.2% win rate across multi-factor model",
          "Momentum factor outperforming with +420bps alpha while mean reversion shows rotation opportunity", 
          "Trade execution efficiency improved 23% through enhanced routing and timing algorithms",
          "Risk-adjusted returns up 340bps YTD with maximum drawdown contained to -2.1%"
        ]}
        conclusion="Advanced quantitative strategies delivering superior risk-adjusted performance through systematic signal generation and optimized execution. Multi-factor approach providing robust alpha generation across market cycles."
        nextSteps={[
          "Increase allocation to momentum signals given current market regime",
          "Deploy enhanced execution algorithms for better fill rates", 
          "Implement real-time factor rotation monitoring"
        ]}
        confidence="very-high"
      />
    ),
    middleLeft: (
      <Section title="Strategy Performance">
        <div className="h-full flex flex-col">
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-2">
            <div className="text-center">
              <div className="text-sm font-semibold text-gray-700 mb-1">Cumulative Returns</div>
              <div className="text-xs text-gray-500 mb-2">vs Benchmark</div>
              <div className="bg-white p-2 rounded shadow-sm text-xs">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-blue-600">Strategy:</span>
                    <span className="font-medium">+18.7%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Benchmark:</span>
                    <span className="font-medium">+12.3%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-green-600">Alpha:</span>
                    <span className="font-medium">+6.4%</span>
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
    middleCenter1_12: (
      <Section title="Signal Distribution">
        <div className="h-full flex flex-col">
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-2">
            <div className="text-center">
              <div className="text-sm font-semibold text-gray-700 mb-1">Signal Strength</div>
              <div className="text-xs text-gray-500 mb-2">Z-Score Distribution</div>
              <div className="bg-white p-2 rounded shadow-sm text-xs">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-gray-600">High Conv.:</span>
                    <span className="font-medium">73</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Med Conv.:</span>
                    <span className="font-medium">142</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Low Conv.:</span>
                    <span className="font-medium">32</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="text-xs text-center">
            <span className="text-blue-600 font-medium">247 Active Signals</span>
          </div>
        </div>
      </Section>
    ),
    middleCenter2_12: (
      <Section title="Market Regime">
        <div className="h-full flex flex-col">
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-2">
            <div className="text-center">
              <div className="text-sm font-semibold text-gray-700 mb-1">Sector Rotation</div>
              <div className="text-xs text-gray-500 mb-2">Factor Heat Map</div>
              <div className="bg-white p-2 rounded shadow-sm text-xs">
                <div className="grid grid-cols-2 gap-1 text-center">
                  <div className="bg-green-100 p-1 rounded text-xs">Tech +</div>
                  <div className="bg-yellow-100 p-1 rounded text-xs">Health =</div>
                  <div className="bg-red-100 p-1 rounded text-xs">Energy -</div>
                  <div className="bg-blue-100 p-1 rounded text-xs">Finance +</div>
                </div>
              </div>
            </div>
          </div>
          <div className="text-xs text-center">
            <span className="text-orange-600 font-medium">Growth Rotation</span>
          </div>
        </div>
      </Section>
    ),
    middleRight: (
      <Section title="Factor Exposure">
        <div className="h-full flex flex-col">
          <div className="flex-1 bg-gray-100 rounded border-2 border-dashed border-gray-300 flex items-center justify-center mb-2">
            <div className="text-center">
              <div className="text-sm font-semibold text-gray-700 mb-1">Active Factors</div>
              <div className="text-xs text-gray-500 mb-2">Model Loadings</div>
              <div className="bg-white p-2 rounded shadow-sm text-xs">
                <div className="space-y-1">
                  <div className="flex justify-between">
                    <span className="text-blue-600">Momentum:</span>
                    <span className="font-medium">+0.85</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Quality:</span>
                    <span className="font-medium">+0.62</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Value:</span>
                    <span className="font-medium">-0.34</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div className="text-xs text-center">
            <span className="text-purple-600 font-medium">Momentum Tilt</span>
          </div>
        </div>
      </Section>
    ),
    bottomLeft: (
      <ComparisonTable
        title="Active Trading Signals - High Conviction Opportunities"
        entities={[
          { id: "msft_mom", name: "MSFT Momentum", subtitle: "Technology • Long • High Conv." },
          { id: "aapl_qual", name: "AAPL Quality", subtitle: "Technology • Long • Medium Conv." },
          { id: "jpm_val", name: "JPM Value", subtitle: "Financials • Long • High Conv." },
          { id: "tsla_rev", name: "TSLA Mean Rev", subtitle: "Auto • Short • Medium Conv." },
          { id: "nvda_mom", name: "NVDA Momentum", subtitle: "Technology • Long • High Conv." },
          { id: "spy_hedge", name: "SPY Hedge", subtitle: "Index • Short • Low Conv." }
        ]}
        metrics={[
          { id: "signal_str", name: "Signal", format: "number" },
          { id: "conviction", name: "Conviction", format: "percentage" },
          { id: "target_size", name: "Target Size", format: "currency" },
          { id: "expected_ret", name: "Expected Return", format: "percentage" },
          { id: "risk_score", name: "Risk", format: "number" }
        ]}
        data={{
          "msft_mom": { 
            "signal_str": "+2.8σ", 
            "conviction": "92%", 
            "target_size": "$2.4M",
            "expected_ret": "+8.7%",
            "risk_score": "3.2"
          },
          "aapl_qual": { 
            "signal_str": "+1.9σ", 
            "conviction": "78%", 
            "target_size": "$1.8M",
            "expected_ret": "+5.4%",
            "risk_score": "2.1"
          },
          "jpm_val": { 
            "signal_str": "+2.1σ", 
            "conviction": "85%", 
            "target_size": "$1.5M",
            "expected_ret": "+7.2%",
            "risk_score": "2.8"
          },
          "tsla_rev": { 
            "signal_str": "-1.7σ", 
            "conviction": "69%", 
            "target_size": "-$900K",
            "expected_ret": "+4.1%",
            "risk_score": "4.6"
          },
          "nvda_mom": { 
            "signal_str": "+3.1σ", 
            "conviction": "94%", 
            "target_size": "$2.8M",
            "expected_ret": "+11.3%",
            "risk_score": "5.2"
          },
          "spy_hedge": { 
            "signal_str": "-0.9σ", 
            "conviction": "42%", 
            "target_size": "-$3.2M",
            "expected_ret": "+2.8%",
            "risk_score": "1.4"
          }
        }}
      />
    ),
    bottomRight: (
      <ComparisonTable
        title="Recent Trade Executions - Performance Tracking"
        entities={[
          { id: "trade_001", name: "AAPL Long", subtitle: "Completed • 1,250 shares • $189.45 avg" },
          { id: "trade_002", name: "MSFT Long", subtitle: "Completed • 750 shares • $428.12 avg" },
          { id: "trade_003", name: "TSLA Short", subtitle: "Active • -400 shares • $248.67 avg" },
          { id: "trade_004", name: "SPY Hedge", subtitle: "Completed • -1,800 shares • $445.23 avg" },
          { id: "trade_005", name: "NVDA Long", subtitle: "Active • 320 shares • $875.45 avg" }
        ]}
        metrics={[
          { id: "entry_time", name: "Entry", format: "text" },
          { id: "fill_quality", name: "Fill Quality", format: "percentage" },
          { id: "unrealized_pnl", name: "Unrealized P&L", format: "currency" },
          { id: "duration", name: "Duration", format: "text" },
          { id: "status", name: "Status", format: "text" }
        ]}
        data={{
          "trade_001": { 
            "entry_time": "09:32", 
            "fill_quality": "98.2%", 
            "unrealized_pnl": "+$4,250",
            "duration": "2.3h",
            "status": "Closed +"
          },
          "trade_002": { 
            "entry_time": "10:15", 
            "fill_quality": "96.8%", 
            "unrealized_pnl": "+$2,890",
            "duration": "1.8h",
            "status": "Closed +"
          },
          "trade_003": { 
            "entry_time": "11:45", 
            "fill_quality": "94.1%", 
            "unrealized_pnl": "+$1,120",
            "duration": "45m",
            "status": "Active"
          },
          "trade_004": { 
            "entry_time": "14:22", 
            "fill_quality": "99.1%", 
            "unrealized_pnl": "+$890",
            "duration": "3.2h",
            "status": "Closed +"
          },
          "trade_005": { 
            "entry_time": "15:01", 
            "fill_quality": "97.5%", 
            "unrealized_pnl": "+$3,440",
            "duration": "28m",
            "status": "Active"
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

    <Layout12
      title={
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Quantitative Trading Analytics Platform {useRandom && '(Randomized)'}</h1>
          <p className="text-gray-600 mt-1">Signal Generation • Factor Analysis • Trade Execution • Risk Management</p>
        </div>
      }
      
      top={activeComponents.top}
      middleLeft={activeComponents.middleLeft}
      middleCenter1={activeComponents.middleCenter1_12}
      middleCenter2={activeComponents.middleCenter2_12}
      middleRight={activeComponents.middleRight}
      bottomLeft={activeComponents.bottomLeft}
      bottomRight={activeComponents.bottomRight}
    />
    </>
  );
}