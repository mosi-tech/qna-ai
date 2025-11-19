'use client';

import { useState } from 'react';
import { 
  RobinhoodStylePortfolio, 
  ElegantPortfolioMetrics,
  ElegantHoldingsTable, 
  ElegantHoldingsSummary,
  ElegantAllocation,
  ElegantRiskDashboard,
  ElegantAttribution,
  ElegantMaxDrawdown,
  ElegantSharpeRatio,
  ElegantAnnualizedReturns,
  ElegantCumulativeReturns,
  ElegantAssetAllocationPie,
  ElegantVolatility
} from '@/components/financial/elegant';
import { 
  elegantPortfolioData, 
  elegantHoldingsData, 
  elegantAllocationData, 
  elegantRiskMetrics,
  elegantVolatilityData,
  elegantDrawdownData,
  elegantAttributionData 
} from '@/data/elegantFinancialData';

// Note: This page is intentionally NOT wrapped with withAuth
// so it can be accessed without authentication for demo purposes
export default function ExamplesPage() {
  const [selectedCategory, setSelectedCategory] = useState('elegant');

  const componentCategories = [
    { id: 'elegant', name: '✨ Elegant Dashboards', count: 5 },
    { id: 'individual', name: '🎯 Individual Components', count: 6 },
  ];

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-7xl mx-auto">
        {/* Navigation Header */}
        <div className="mb-6 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <a 
              href="/" 
              className="text-blue-600 hover:text-blue-800 text-sm font-medium flex items-center gap-2"
            >
              ← Back to App
            </a>
            <span className="text-gray-300">|</span>
            <span className="text-sm text-gray-600">Public Demo</span>
          </div>
          <div className="text-xs text-gray-500">
            No authentication required
          </div>
        </div>
        
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900">
            Elegant Financial Components
          </h1>
          <p className="text-xl text-gray-600 mt-2">
            Investment-grade UI with visx for maximum elegance
          </p>
          <div className="mt-4 p-4 bg-emerald-50 rounded-lg border border-emerald-200">
            <p className="text-emerald-800 text-sm">
              🎯 <strong>Built for Investment Professionals:</strong> Comprehensive library using visx + D3
            </p>
            <p className="text-emerald-700 text-xs mt-1">
              Clean, borderless design with Robinhood/TradingView aesthetics • Each component has simple APIs for LLM reliability
            </p>
          </div>
        </div>

        <div>
          <div className="flex space-x-4 mb-8">
            {componentCategories.map((category) => (
              <button
                key={category.id}
                onClick={() => setSelectedCategory(category.id)}
                className={`px-4 py-2 rounded-lg font-medium transition-colors ${
                  selectedCategory === category.id
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
              >
                <div className="text-center">
                  <div className="font-medium">{category.name}</div>
                  <div className="text-xs opacity-75">{category.count} components</div>
                </div>
              </button>
            ))}
          </div>

          <div>
            {selectedCategory === 'elegant' && <ElegantComponentsSection />}
            {selectedCategory === 'individual' && <IndividualComponentsSection />}
          </div>
        </div>
      </div>
    </div>
  );
}

function ElegantComponentsSection() {
  const [selectedDemo, setSelectedDemo] = useState('portfolio');

  const demos = [
    { id: 'portfolio', name: '📈 Portfolio Overview', desc: 'Robinhood-style chart with metrics' },
    { id: 'holdings', name: '📊 Holdings Analysis', desc: 'Elegant table with embedded visuals' },
    { id: 'allocation', name: '🥧 Asset Allocation', desc: 'Smart donut with risk insights' },
    { id: 'risk', name: '⚡ Risk Dashboard', desc: 'Comprehensive risk analytics' },
    { id: 'attribution', name: '🎯 Performance Attribution', desc: 'Factor decomposition analysis' }
  ];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">✨ Elegant Financial Components</h2>
        <p className="text-gray-600 mb-8">
          Investment-grade UI with Robinhood/TradingView aesthetics - Built with visx for maximum elegance
        </p>
        
        <div className="mb-8 p-6 bg-gradient-to-r from-emerald-50 via-blue-50 to-purple-50 rounded-2xl border border-emerald-200">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
            <div>
              <h4 className="font-bold text-gray-800 mb-3">🎯 Investment Professional Focus</h4>
              <ul className="space-y-2 text-sm text-gray-700">
                <li>• <strong>Risk-adjusted metrics</strong> - Sharpe, Sortino, Calmar ratios</li>
                <li>• <strong>Attribution analysis</strong> - Factor & sector decomposition</li>
                <li>• <strong>Drawdown visualization</strong> - Underwater charts</li>
                <li>• <strong>Regime awareness</strong> - Market volatility contexts</li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-gray-800 mb-3">💎 Elegant Design Principles</h4>
              <ul className="space-y-2 text-sm text-gray-700">
                <li>• <strong>Typography-first</strong> - Large, readable numbers</li>
                <li>• <strong>Borderless layout</strong> - Clean, open space</li>
                <li>• <strong>Semantic colors</strong> - Green/red for gains/losses</li>
                <li>• <strong>Smooth gradients</strong> - Professional depth</li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold text-gray-800 mb-3">⚡ Technical Excellence</h4>
              <ul className="space-y-2 text-sm text-gray-700">
                <li>• <strong>visx + D3</strong> - Performance optimized</li>
                <li>• <strong>Spring animations</strong> - Smooth transitions</li>
                <li>• <strong>Responsive scaling</strong> - Mobile-first</li>
                <li>• <strong>TypeScript</strong> - Full type safety</li>
              </ul>
            </div>
          </div>
        </div>

        {/* Component Selection */}
        <div className="mb-8">
          <div className="flex flex-wrap gap-3">
            {demos.map((demo) => (
              <button
                key={demo.id}
                onClick={() => setSelectedDemo(demo.id)}
                className={`px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                  selectedDemo === demo.id
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
                }`}
              >
                <div className="text-left">
                  <div>{demo.name}</div>
                  <div className="text-xs opacity-75 mt-1">{demo.desc}</div>
                </div>
              </button>
            ))}
          </div>
        </div>

        {/* Component Demos */}
        <div className="min-h-[600px]">
          {selectedDemo === 'portfolio' && (
            <div className="space-y-6">
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100">
                <RobinhoodStylePortfolio
                  data={elegantPortfolioData.chartData}
                  currentValue={elegantPortfolioData.currentValue}
                  dayChange={elegantPortfolioData.dayChange}
                  dayChangePercent={elegantPortfolioData.dayChangePercent}
                  title="Portfolio Performance"
                  showBenchmark={true}
                  height={400}
                />
                <ElegantPortfolioMetrics
                  metrics={{
                    totalReturn: elegantPortfolioData.totalReturn,
                    dayChange: elegantPortfolioData.dayChange,
                    dayChangePercent: elegantPortfolioData.dayChangePercent,
                    sharpeRatio: elegantPortfolioData.sharpeRatio,
                    maxDrawdown: elegantPortfolioData.maxDrawdown,
                    ytdReturn: elegantPortfolioData.ytdReturn
                  }}
                />
              </div>
              <ComponentAPIInfo 
                componentName="RobinhoodStylePortfolio"
                apiProps="data, currentValue, dayChange, dayChangePercent, title?, showBenchmark?, height?"
              />
            </div>
          )}

          {selectedDemo === 'holdings' && (
            <div className="space-y-6">
              <ElegantHoldingsSummary 
                holdings={elegantHoldingsData}
                totalValue={elegantPortfolioData.currentValue}
              />
              <div className="bg-white rounded-2xl shadow-sm border border-gray-100">
                <ElegantHoldingsTable
                  holdings={elegantHoldingsData}
                  totalValue={elegantPortfolioData.currentValue}
                  title="Portfolio Holdings"
                  showMetrics={true}
                />
              </div>
              <ComponentAPIInfo 
                componentName="ElegantHoldingsTable"
                apiProps="holdings, totalValue, title?, showMetrics?"
              />
            </div>
          )}

          {selectedDemo === 'allocation' && (
            <div className="space-y-6">
              <ElegantAllocation
                allocations={elegantAllocationData}
                title="Strategic Asset Allocation"
                showTargets={true}
                showRiskMetrics={true}
                size={320}
                innerRadius={90}
              />
              <ComponentAPIInfo 
                componentName="ElegantAllocation"
                apiProps="allocations, title?, showTargets?, showRiskMetrics?, size?, innerRadius?"
              />
            </div>
          )}

          {selectedDemo === 'risk' && (
            <div className="space-y-6">
              <ElegantRiskDashboard
                metrics={elegantRiskMetrics}
                volatilityData={elegantVolatilityData}
                drawdownData={elegantDrawdownData}
                benchmarkMetrics={{
                  sharpe: 1.12,
                  maxDrawdown: -15.8,
                  volatility: 16.2,
                  var95: -2.8
                }}
                title="Portfolio Risk Analysis"
                timeframe="12 Month Analysis"
                height={350}
              />
              <ComponentAPIInfo 
                componentName="ElegantRiskDashboard"
                apiProps="metrics, volatilityData, drawdownData, benchmarkMetrics?, title?, timeframe?, height?"
              />
            </div>
          )}

          {selectedDemo === 'attribution' && (
            <div className="space-y-6">
              <ElegantAttribution
                factors={elegantAttributionData}
                totalAlpha={2.8}
                benchmarkReturn={8.2}
                portfolioReturn={11.0}
                title="Performance Attribution Analysis"
                timeframe="Trailing 12 Months"
                height={450}
              />
              <ComponentAPIInfo 
                componentName="ElegantAttribution"
                apiProps="factors, totalAlpha, benchmarkReturn, portfolioReturn, title?, timeframe?, height?"
              />
            </div>
          )}
        </div>

        {/* Comparison with Tremor */}
        <div className="mt-12 p-8 bg-gradient-to-r from-gray-50 to-gray-100 rounded-2xl border border-gray-200">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">Elegant visx vs Tremor Comparison</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h4 className="font-semibold text-emerald-800 mb-4 flex items-center">
                <span className="w-3 h-3 bg-emerald-500 rounded-full mr-2"></span>
                Elegant visx Advantages
              </h4>
              <div className="space-y-3 text-sm">
                <div className="flex items-start space-x-3">
                  <span className="text-emerald-600 font-bold">•</span>
                  <div>
                    <strong>Investment Professional UI:</strong> Risk-adjusted metrics, attribution analysis, regime awareness
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-emerald-600 font-bold">•</span>
                  <div>
                    <strong>Borderless Design:</strong> Clean, modern aesthetic inspired by Robinhood/TradingView
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-emerald-600 font-bold">•</span>
                  <div>
                    <strong>Performance Optimized:</strong> visx + D3 for smooth 60fps animations
                  </div>
                </div>
                <div className="flex items-start space-x-3">
                  <span className="text-emerald-600 font-bold">•</span>
                  <div>
                    <strong>Typography Focus:</strong> Large, readable numbers with clear hierarchies
                  </div>
                </div>
              </div>
            </div>

            <div>
              <h4 className="font-semibold text-blue-800 mb-4 flex items-center">
                <span className="w-3 h-3 bg-blue-500 rounded-full mr-2"></span>
                When to Use Each
              </h4>
              <div className="space-y-3 text-sm">
                <div className="p-3 bg-emerald-50 rounded-lg border border-emerald-200">
                  <strong className="text-emerald-800">Use Elegant visx for:</strong>
                  <ul className="mt-1 space-y-1 text-emerald-700">
                    <li>• Client-facing dashboards</li>
                    <li>• Investment presentations</li>
                    <li>• Portfolio analytics</li>
                    <li>• Modern financial apps</li>
                  </ul>
                </div>
                <div className="p-3 bg-blue-50 rounded-lg border border-blue-200">
                  <strong className="text-blue-800">Use Tremor for:</strong>
                  <ul className="mt-1 space-y-1 text-blue-700">
                    <li>• Internal admin tools</li>
                    <li>• Rapid prototyping</li>
                    <li>• Corporate reporting</li>
                    <li>• Traditional BI dashboards</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

function IndividualComponentsSection() {
  const [selectedComponent, setSelectedComponent] = useState('maxdrawdown');

  const components = [
    { id: 'maxdrawdown', name: '📉 Max Drawdown', desc: 'Risk assessment with recovery analysis' },
    { id: 'sharpe', name: '🎯 Sharpe Ratio', desc: 'Risk-adjusted return measurement' },
    { id: 'annualized', name: '📈 Annualized Returns', desc: 'Performance scoring with targets' },
    { id: 'cumulative', name: '📊 Cumulative Returns', desc: 'Interactive time series chart' },
    { id: 'allocation', name: '🥧 Asset Allocation', desc: 'Smart pie with risk insights' },
    { id: 'volatility', name: '⚡ Volatility', desc: 'Risk measurement and regime analysis' }
  ];

  return (
    <div className="space-y-8">
      <div>
        <h2 className="text-3xl font-bold text-gray-900 mb-4">🎯 Individual Elegant Components</h2>
        <p className="text-gray-600 mb-8">
          Standalone financial components for answering specific queries
        </p>
        
        <div className="mb-8 p-6 bg-gradient-to-r from-green-50 via-blue-50 to-purple-50 rounded-2xl border border-green-200">
          <h4 className="font-bold text-gray-800 mb-3">💡 Usage for Financial Queries</h4>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 text-sm text-gray-700">
            <div>
              <strong>Query:</strong> "What's the risk level of my portfolio?"<br/>
              <strong>Components:</strong> ElegantMaxDrawdown + ElegantVolatility
            </div>
            <div>
              <strong>Query:</strong> "How does my portfolio perform vs benchmark?"<br/>
              <strong>Components:</strong> ElegantSharpeRatio + ElegantAnnualizedReturns
            </div>
            <div>
              <strong>Query:</strong> "Show me my asset allocation breakdown"<br/>
              <strong>Components:</strong> ElegantAssetAllocationPie + ElegantAllocation
            </div>
            <div>
              <strong>Query:</strong> "What's my portfolio performance over time?"<br/>
              <strong>Components:</strong> ElegantCumulativeReturns + performance metrics
            </div>
          </div>
        </div>

        {/* Component Selection */}
        <div className="mb-8">
          <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-3">
            {components.map((comp) => (
              <button
                key={comp.id}
                onClick={() => setSelectedComponent(comp.id)}
                className={`p-3 rounded-xl text-sm font-medium transition-all text-left ${
                  selectedComponent === comp.id
                    ? 'bg-blue-600 text-white shadow-lg'
                    : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
                }`}
              >
                <div>{comp.name}</div>
                <div className="text-xs opacity-75 mt-1">{comp.desc}</div>
              </button>
            ))}
          </div>
        </div>

        {/* Individual Component Demos */}
        <div className="min-h-[700px]">
          {selectedComponent === 'maxdrawdown' && (
            <div className="space-y-6">
              <ElegantMaxDrawdown
                value={elegantRiskMetrics.maxDrawdown}
                benchmark={-15.8}
                currentDrawdown={-2.1}
                date="2024-03-01"
                recoveryDate="2024-05-15"
                duration={75}
                drawdownHistory={elegantDrawdownData}
                title="Maximum Drawdown Analysis"
                subtitle="Comprehensive downside risk assessment"
              />
              <ComponentAPIInfo 
                componentName="ElegantMaxDrawdown"
                apiProps="value, benchmark?, currentDrawdown?, date?, recoveryDate?, duration?, drawdownHistory?, title?, subtitle?"
              />
            </div>
          )}

          {selectedComponent === 'sharpe' && (
            <div className="space-y-6">
              <ElegantSharpeRatio
                value={elegantRiskMetrics.sharpe}
                benchmark={1.12}
                historicalRange={{ min: 0.3, max: 2.1, avg: 1.2 }}
                riskFreeRate={2.0}
                period="3Y"
                portfolioLabel="Growth Portfolio"
                benchmarkLabel="S&P 500"
                peerComparison={[
                  { name: "Peer Average", value: 1.08 },
                  { name: "Top Quartile", value: 1.65 }
                ]}
                title="Sharpe Ratio Analysis"
              />
              <ComponentAPIInfo 
                componentName="ElegantSharpeRatio"
                apiProps="value, benchmark?, historicalRange?, riskFreeRate?, period?, portfolioLabel?, benchmarkLabel?, peerComparison?, title?"
              />
            </div>
          )}

          {selectedComponent === 'annualized' && (
            <div className="space-y-6">
              <ElegantAnnualizedReturns
                returns={12.4}
                benchmark={10.2}
                target={15.0}
                period="3Y"
                portfolioLabel="Growth Portfolio"
                benchmarkLabel="S&P 500"
                periodBreakdown={[
                  { period: "YTD", portfolio: 8.4, benchmark: 6.1, target: 7.5 },
                  { period: "1Y", portfolio: 12.7, benchmark: 10.2, target: 12.0 },
                  { period: "3Y", portfolio: 12.4, benchmark: 10.8, target: 15.0 },
                  { period: "5Y", portfolio: 11.2, benchmark: 9.5, target: 13.0 }
                ]}
                volatility={18.5}
                title="Annualized Returns Analysis"
                subtitle="Performance measurement with target tracking"
              />
              <ComponentAPIInfo 
                componentName="ElegantAnnualizedReturns"
                apiProps="returns, benchmark?, target?, period?, portfolioLabel?, benchmarkLabel?, periodBreakdown?, volatility?, title?, subtitle?"
              />
            </div>
          )}

          {selectedComponent === 'cumulative' && (
            <div className="space-y-6">
              <ElegantCumulativeReturns
                portfolio={elegantPortfolioData.chartData.map(d => ({
                  date: d.date,
                  portfolio: d.value,
                  benchmark: d.benchmark
                }))}
                title="Cumulative Performance Chart"
                portfolioLabel="Growth Portfolio"
                benchmarkLabel="S&P 500 Index"
                height={500}
                showDrawdown={true}
                annotations={[
                  { 
                    date: new Date('2024-03-01'), 
                    label: "Market Correction", 
                    description: "COVID-19 impact" 
                  }
                ]}
              />
              <ComponentAPIInfo 
                componentName="ElegantCumulativeReturns"
                apiProps="portfolio, benchmark?, title?, portfolioLabel?, benchmarkLabel?, height?, showDrawdown?, annotations?"
              />
            </div>
          )}

          {selectedComponent === 'allocation' && (
            <div className="space-y-6">
              <ElegantAssetAllocationPie
                allocations={elegantAllocationData}
                title="Strategic Asset Allocation"
                subtitle="Portfolio composition with target analysis"
                showPercentage={true}
                showTargets={true}
                showRiskMetrics={true}
                size={400}
                innerRadius={120}
                totalValue={elegantPortfolioData.currentValue}
              />
              <ComponentAPIInfo 
                componentName="ElegantAssetAllocationPie"
                apiProps="allocations, title?, subtitle?, showPercentage?, showTargets?, showRiskMetrics?, size?, innerRadius?, totalValue?"
              />
            </div>
          )}

          {selectedComponent === 'volatility' && (
            <div className="space-y-6">
              <ElegantVolatility
                volatility={elegantRiskMetrics.volatility}
                regime="normal"
                percentile={65}
                benchmark={16.2}
                historicalData={elegantVolatilityData}
                period="12M"
                title="Volatility Risk Analysis"
                subtitle="Market regime assessment and risk implications"
              />
              <ComponentAPIInfo 
                componentName="ElegantVolatility"
                apiProps="volatility, regime?, percentile?, benchmark?, historicalData?, period?, title?, subtitle?"
              />
            </div>
          )}
        </div>

        {/* LLM Usage Guide */}
        <div className="mt-12 p-8 bg-gradient-to-r from-indigo-50 to-purple-50 rounded-2xl border border-indigo-200">
          <h3 className="text-xl font-semibold text-gray-900 mb-6">🤖 LLM Integration Guide</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            <div>
              <h4 className="font-semibold text-indigo-800 mb-4">Component Selection Logic</h4>
              <div className="space-y-3 text-sm text-indigo-700">
                <div>
                  <strong>Risk Questions:</strong> Use ElegantMaxDrawdown, ElegantVolatility, ElegantSharpeRatio
                </div>
                <div>
                  <strong>Performance Questions:</strong> Use ElegantAnnualizedReturns, ElegantCumulativeReturns
                </div>
                <div>
                  <strong>Allocation Questions:</strong> Use ElegantAssetAllocationPie, ElegantAllocation
                </div>
                <div>
                  <strong>Holdings Questions:</strong> Use ElegantHoldingsTable, ElegantHoldingsSummary
                </div>
              </div>
            </div>
            
            <div>
              <h4 className="font-semibold text-purple-800 mb-4">API Design Principles</h4>
              <div className="space-y-3 text-sm text-purple-700">
                <div>
                  <strong>Simple Props:</strong> Most required props are basic numbers/arrays
                </div>
                <div>
                  <strong>Smart Defaults:</strong> Components work with minimal configuration
                </div>
                <div>
                  <strong>TypeScript:</strong> Full type safety prevents LLM errors
                </div>
                <div>
                  <strong>Flexible Styling:</strong> title?, subtitle?, showX? props for customization
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// All old Tremor-based sections removed

interface ComponentAPIInfoProps {
  componentName: string;
  apiProps: string;
}

function ComponentAPIInfo({ componentName, apiProps }: ComponentAPIInfoProps) {
  return (
    <div className="mt-4 p-3 bg-slate-50 rounded-lg border border-slate-200">
      <div className="text-xs font-medium text-slate-700 mb-2">
        📋 LLM-Friendly API
      </div>
      <div className="text-xs text-slate-600 space-y-1">
        <div>
          <span className="font-mono text-blue-600">&lt;{componentName}</span>
        </div>
        <div className="pl-4 font-mono text-gray-600">
          {apiProps.split(', ').map((prop, index) => (
            <div key={index}>
              {prop}={'{...}'}
            </div>
          ))}
        </div>
        <div>
          <span className="font-mono text-blue-600">/&gt;</span>
        </div>
      </div>
      <div className="mt-2 flex items-center gap-2">
        <button className="text-xs text-blue-600 hover:text-blue-800 font-medium">
          Copy for LLM
        </button>
        <span className="text-gray-300 text-xs">•</span>
        <button className="text-xs text-blue-600 hover:text-blue-800 font-medium">
          View TypeScript
        </button>
      </div>
    </div>
  );
}