/**
 * Test page for Chat UI Configuration Rendering
 * 
 * This page tests various UI configurations through the chat message system
 */

'use client';

import { useState } from 'react';
import ChatMessage from '@/components/chat/ChatMessage';
import { ProgressProvider } from '@/lib/context/ProgressContext';
import { sampleAnalysisData, drawdownAnalysisData, uiConfigurations } from './ui-configurations';
import PredefinedGridRenderer from './PredefinedGridRenderer';
import { GRID_SLOTS, SLOT_VISIBILITY_RULES, PREDEFINED_CONFIGS } from './predefined-grid-config';

// Create test messages for each UI configuration
const createTestMessage = (configName: string, config: any, title: string, question: string) => {
  const analysisData = configName === 'drawdownAnalysis' ? drawdownAnalysisData : sampleAnalysisData;
  return {
    id: `test-msg-${configName}`,
    role: "assistant" as const,
    response_type: "script_generation",
    status: "completed" as const,
    content: `${title} - Analysis completed successfully`,
    timestamp: "2024-01-15T10:30:00.000Z",
    results: {
      ui_config: {
        analysis_data: analysisData,
        ...config,
        metadata: {
          question,
          generated_at: "2024-01-15T10:30:00.000Z",
          formatter_version: "1.0.0"
        }
      }
    }
  };
};

// Dynamic UI configurations
const dynamicConfigurations = [
  {
    name: "denseShowcase",
    title: "Dense Component Showcase",
    question: "Show me a comprehensive portfolio overview with all key metrics and insights",
    description: "6 components: StatGroup(4 stats) + RankedList + PieChart + ExecutiveSummary + BarChart + HeatmapTable - minimal white space"
  },
  {
    name: "maxDensity", 
    title: "Maximum Density Grid",
    question: "Pack as much portfolio information as possible into a single view",
    description: "9 components: 3×StatGroup + BarChart + PieChart + LineChart + RankedList + BulletList + CalloutList - all third/short layout"
  },
  {
    name: "allComponentsShowcase",
    title: "All Components Showcase", 
    question: "Demonstrate all available component types in one analysis",
    description: "7 components: RankingTable + ComparisonTable + ScatterChart + HeatmapTable + SectionedInsightCard + ExecutiveSummary + SummaryConclusion"
  },
  {
    name: "ultraDense",
    title: "Ultra Dense 12-Component Grid",
    question: "Maximum component density test - how many components can fit?", 
    description: "12 components: 3×StatGroup + BarChart + PieChart + LineChart + RankedList + BulletList + CalloutList + ScatterChart + HeatmapTable + ExecutiveSummary"
  },
  {
    name: "componentVariety",
    title: "Component Variety Showcase",
    question: "Show different component types with varied layouts and content",
    description: "4 components: RankingTable + ComparisonTable + SectionedInsightCard + SummaryConclusion - focused on component variety"
  },
  {
    name: "drawdownAnalysis",
    title: "QQQ 2010 Drawdown Analysis",
    question: "Analyze the maximum drawdown for QQQ in 2010",
    description: "3 components: StatGroup + BarChart + ExecutiveSummary - drawdown analysis with metrics and insights"
  }
];

// Predefined grid configurations
const predefinedConfigurations = [
  {
    name: "portfolioAnalysis",
    title: "Portfolio Analysis (2x5 Grid)",
    question: "Analyze my portfolio performance using a structured layout",
    description: "Fixed 2x5 grid: Performance metrics → Charts → Data tables → Analysis → Summary"
  },
  {
    name: "stockAnalysis", 
    title: "Stock Analysis (2x5 Grid)",
    question: "Analyze individual stock performance in a structured format",
    description: "Fixed 2x5 grid: Price metrics → Charts → Volume data → Analysis → Conclusion"
  },
  {
    name: "sectorComparison",
    title: "Sector Comparison (2x5 Grid)", 
    question: "Compare sector performance using predefined layout",
    description: "Fixed 2x5 grid: Best performer → Comparison charts → Sector data → Insights → Summary"
  },
  {
    name: "drawdownAnalysis",
    title: "QQQ 2010 Drawdown Analysis (2x5 Grid)",
    question: "Analyze the maximum drawdown for QQQ in 2010",
    description: "Fixed 2x5 grid: Drawdown metrics → Executive summary → Analysis charts"
  }
];

// Sample message without UI configuration (fallback test)
const sampleMessageWithoutUIConfig = {
  id: "test-msg-fallback",
  role: "assistant" as const,
  response_type: "script_generation",
  status: "completed" as const,
  content: "Analysis completed with traditional markdown formatting",
  timestamp: "2024-01-15T10:30:00.000Z",
  data: {
    content: "## Analysis Results\n\nThis is a traditional markdown response without UI configuration."
  }
};

export default function ChatUITestPage() {
  const [selectedConfig, setSelectedConfig] = useState<string>("denseShowcase");
  const [showAllConfigs, setShowAllConfigs] = useState<boolean>(false);
  const [layoutApproach, setLayoutApproach] = useState<'dynamic' | 'predefined'>('dynamic');

  const currentConfigurations = layoutApproach === 'dynamic' ? dynamicConfigurations : predefinedConfigurations;

  return (
    <ProgressProvider sessionId={null}>
      <div className="p-8 max-w-7xl mx-auto space-y-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">
            Chat UI Configuration Test
          </h1>
          <p className="text-gray-600 mb-4">
            Compare Dynamic vs Predefined Grid layout approaches
          </p>
          <p className="text-sm text-gray-500">
            Dynamic: Flexible component sizing with third/half/full layouts | Predefined: Fixed 2x5 grid with conditional slots
          </p>
        </div>

        {/* Layout Approach Toggle */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-800">Layout Approach</h2>
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => {
                  setLayoutApproach('dynamic');
                  setSelectedConfig('denseShowcase');
                }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  layoutApproach === 'dynamic' 
                    ? "bg-white text-gray-900 shadow-sm" 
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                Dynamic Grid
              </button>
              <button
                onClick={() => {
                  setLayoutApproach('predefined');
                  setSelectedConfig('portfolioAnalysis');
                }}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  layoutApproach === 'predefined' 
                    ? "bg-white text-gray-900 shadow-sm" 
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                Predefined 2x5 Grid
              </button>
            </div>
          </div>
          
          <div className="grid md:grid-cols-2 gap-6 text-sm">
            <div className={`p-4 rounded-lg border-2 ${layoutApproach === 'dynamic' ? 'border-blue-200 bg-blue-50' : 'border-gray-200 bg-gray-50'}`}>
              <h3 className="font-semibold text-gray-900 mb-2">Dynamic Grid Approach</h3>
              <ul className="text-gray-600 space-y-1">
                <li>• Flexible component sizing (third/half/full)</li>
                <li>• Variable number of components</li> 
                <li>• Complex responsive calculations</li>
                <li>• Maximum layout flexibility</li>
                <li>• Current UIConfigurationRenderer</li>
              </ul>
            </div>
            
            <div className={`p-4 rounded-lg border-2 ${layoutApproach === 'predefined' ? 'border-green-200 bg-green-50' : 'border-gray-200 bg-gray-50'}`}>
              <h3 className="font-semibold text-gray-900 mb-2">Predefined 2x5 Grid</h3>
              <ul className="text-gray-600 space-y-1">
                <li>• Fixed 10-slot grid layout</li>
                <li>• Predictable, consistent spacing</li>
                <li>• Data-driven slot visibility</li>
                <li>• Better responsive performance</li>
                <li>• Structured visual hierarchy</li>
              </ul>
            </div>
          </div>
        </div>
        
        {/* Configuration Selector */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-800">
              {layoutApproach === 'dynamic' ? 'Dynamic' : 'Predefined Grid'} Configurations
            </h2>
            <button
              onClick={() => setShowAllConfigs(!showAllConfigs)}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                showAllConfigs 
                  ? "bg-blue-500 text-white hover:bg-blue-600" 
                  : "bg-gray-100 text-gray-700 hover:bg-gray-200"
              }`}
            >
              {showAllConfigs ? "Show Selected Only" : "Show All Configs"}
            </button>
          </div>
          
          {!showAllConfigs && (
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {currentConfigurations.map(config => (
                <div 
                  key={config.name}
                  onClick={() => setSelectedConfig(config.name)}
                  className={`p-4 rounded-lg border-2 cursor-pointer transition-all ${
                    selectedConfig === config.name
                      ? "border-blue-500 bg-blue-50"
                      : "border-gray-200 hover:border-gray-300 hover:bg-gray-50"
                  }`}
                >
                  <h3 className="font-semibold text-gray-900 mb-2">{config.title}</h3>
                  <p className="text-sm text-gray-600 mb-2">{config.description}</p>
                  <p className="text-xs text-gray-500 italic">"{config.question}"</p>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Selected Configuration Display */}
        {!showAllConfigs && (
          <div className="space-y-6">
            {currentConfigurations
              .filter(config => config.name === selectedConfig)
              .map(config => {
                if (layoutApproach === 'dynamic') {
                  const message = createTestMessage(
                    config.name,
                    (uiConfigurations as any)[config.name],
                    config.title,
                    config.question
                  );
                  
                  return (
                    <div key={config.name}>
                      <h2 className="text-xl font-semibold text-gray-800 mb-4">
                        {config.title}
                      </h2>
                      <div className="bg-gray-50 p-4 rounded-lg">
                        <ChatMessage message={message} />
                      </div>
                    </div>
                  );
                } else {
                  // Predefined grid approach
                  const gridAnalysisData = config.name === 'drawdownAnalysis' ? drawdownAnalysisData : sampleAnalysisData;
                  return (
                    <div key={config.name}>
                      <h2 className="text-xl font-semibold text-gray-800 mb-4">
                        {config.title}
                      </h2>
                      <div className="bg-white border border-gray-200 rounded-lg p-6">
                        <PredefinedGridRenderer 
                          configType={config.name}
                          analysisData={gridAnalysisData}
                        />
                      </div>
                    </div>
                  );
                }
              })}
          </div>
        )}

        {/* All Configurations Display */}
        {showAllConfigs && (
          <div className="space-y-12">
            {currentConfigurations.map(config => {
              if (layoutApproach === 'dynamic') {
                const message = createTestMessage(
                  config.name,
                  (uiConfigurations as any)[config.name],
                  config.title,
                  config.question
                );
                
                return (
                  <div key={config.name} className="space-y-4">
                    <div className="border-l-4 border-blue-500 pl-4">
                      <h2 className="text-xl font-semibold text-gray-800">{config.title}</h2>
                      <p className="text-gray-600 text-sm">{config.description}</p>
                      <p className="text-gray-500 text-xs italic mt-1">Question: "{config.question}"</p>
                    </div>
                    <div className="bg-gray-50 p-4 rounded-lg">
                      <ChatMessage message={message} />
                    </div>
                  </div>
                );
              } else {
                const gridAnalysisData = config.name === 'drawdownAnalysis' ? drawdownAnalysisData : sampleAnalysisData;
                return (
                  <div key={config.name} className="space-y-4">
                    <div className="border-l-4 border-green-500 pl-4">
                      <h2 className="text-xl font-semibold text-gray-800">{config.title}</h2>
                      <p className="text-gray-600 text-sm">{config.description}</p>
                      <p className="text-gray-500 text-xs italic mt-1">Question: "{config.question}"</p>
                    </div>
                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                      <PredefinedGridRenderer 
                        configType={config.name}
                        analysisData={gridAnalysisData}
                      />
                    </div>
                  </div>
                );
              }
            })}
            
            {/* Fallback message for dynamic approach only */}
            {layoutApproach === 'dynamic' && (
              <div className="space-y-4">
                <div className="border-l-4 border-gray-400 pl-4">
                  <h2 className="text-xl font-semibold text-gray-800">Fallback: Traditional Markdown</h2>
                  <p className="text-gray-600 text-sm">Message without UI configuration (shows traditional AnalysisResult rendering)</p>
                </div>
                <div className="bg-gray-50 p-4 rounded-lg">
                  <ChatMessage message={sampleMessageWithoutUIConfig} />
                </div>
              </div>
            )}
          </div>
        )}
        
        {/* Debug info */}
        <details className="mt-12 bg-white border border-gray-200 rounded-lg p-4">
          <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
            Debug: Sample Data & Configurations
          </summary>
          <div className="mt-4 space-y-6">
            <div>
              <h3 className="font-medium text-gray-700 mb-2">Sample Analysis Data:</h3>
              <pre className="text-xs text-gray-600 overflow-auto max-h-48 bg-gray-50 p-3 rounded border">
                {JSON.stringify(sampleAnalysisData, null, 2)}
              </pre>
            </div>
            <div>
              <h3 className="font-medium text-gray-700 mb-2">
                {layoutApproach === 'dynamic' ? 'Dynamic' : 'Predefined Grid'} Configurations:
              </h3>
              <pre className="text-xs text-gray-600 overflow-auto max-h-48 bg-gray-50 p-3 rounded border">
                {layoutApproach === 'dynamic' 
                  ? JSON.stringify(uiConfigurations, null, 2)
                  : JSON.stringify({
                      availableConfigs: Object.keys(PREDEFINED_CONFIGS),
                      gridSlots: GRID_SLOTS,
                      visibilityRules: SLOT_VISIBILITY_RULES
                    }, null, 2)
                }
              </pre>
            </div>
          </div>
        </details>
      </div>
    </ProgressProvider>
  );
}