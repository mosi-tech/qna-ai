/**
 * UIConfigurationRenderer
 * 
 * Description: Dynamic UI renderer that takes JSON configuration from backend and renders React components
 * Use Cases: Analysis result dashboards, dynamic UI generation from LLM
 * Data Format: UI configuration JSON with component specs and layout
 * 
 * @param uiConfig - UI configuration object from backend
 * @param onApprove - Callback for approve action
 * @param onDisapprove - Callback for disapprove action
 */

'use client';

import React from 'react';
import { cn } from './shared/styles';

// Import all available components
import BarChart from './BarChart';
import BulletList from './BulletList';
import CalloutList from './CalloutList';
import ComparisonTable from './ComparisonTable';
import ExecutiveSummary from './ExecutiveSummary';
import HeatmapTable from './HeatmapTable';
import LineChart from './LineChart';
import PieChart from './PieChart';
import RankedList from './RankedList';
import RankingTable from './RankingTable';
import ScatterChart from './ScatterChart';
import SectionedInsightCard from './SectionedInsightCard';
import StatGroup from './StatGroup';
import SummaryConclusion from './SummaryConclusion';

// Component registry for dynamic loading
const COMPONENT_REGISTRY = {
  BarChart,
  BulletList,
  CalloutList,
  ComparisonTable,
  ExecutiveSummary,
  HeatmapTable,
  LineChart,
  PieChart,
  RankedList,
  RankingTable,
  ScatterChart,
  SectionedInsightCard,
  StatGroup,
  SummaryConclusion,
} as const;

interface ComponentConfig {
  component_name: string;
  props: Record<string, any>;
  layout: {
    span: 'normal' | 'full';
  };
  reasoning?: string;
}

interface UIConfiguration {
  selected_components: ComponentConfig[];
  layout_template?: string;
  priority?: string;
}

interface UIConfigurationRendererProps {
  uiConfig: {
    analysis_data: any;
    ui_config: UIConfiguration;
    metadata?: {
      question?: string;
      generated_at?: string;
      formatter_version?: string;
    };
  };
}

/**
 * Transform data references like {{analysis_data.path}} to actual data values
 */
function transformDataReferences(props: any, analysisData: any): any {
  if (typeof props === 'string') {
    // Handle {{analysis_data.path}} syntax
    const match = props.match(/^\{\{analysis_data\.(.+)\}\}$/);
    if (match) {
      const path = match[1];
      const value = getNestedValue(analysisData, path);
      return value !== undefined ? value : props;
    }
    return props;
  }
  
  if (Array.isArray(props)) {
    return props.map(item => transformDataReferences(item, analysisData));
  }
  
  if (props && typeof props === 'object') {
    const transformed: any = {};
    for (const [key, value] of Object.entries(props)) {
      transformed[key] = transformDataReferences(value, analysisData);
    }
    return transformed;
  }
  
  return props;
}

/**
 * Get nested value from object using dot notation
 */
function getNestedValue(obj: any, path: string): any {
  return path.split('.').reduce((current, key) => current?.[key], obj);
}


/**
 * Render individual component based on configuration
 */
function renderComponent(config: ComponentConfig, analysisData: any, key: number) {
  const Component = COMPONENT_REGISTRY[config.component_name as keyof typeof COMPONENT_REGISTRY];
  const span = config.layout?.span || 'normal';
  
  // Apply span class - 'full' spans both columns, 'normal' is one column
  const spanClass = span === 'full' ? 'col-span-1 sm:col-span-2' : 'col-span-1';
  
  if (!Component) {
    console.warn(`Unknown component: ${config.component_name}`);
    return (
      <div key={key} className={cn('min-h-[250px] bg-white rounded-lg shadow-lg border-t border-slate-100 overflow-hidden flex flex-col', spanClass)}>
        <div className="p-4">
          <div className="text-red-600 text-sm font-medium">
            Unknown component: {config.component_name}
          </div>
          <div className="text-red-500 text-xs mt-1">
            Span: {span}
          </div>
        </div>
      </div>
    );
  }
  
  // Transform data references in props
  const transformedProps = transformDataReferences(config.props, analysisData);
  
  return (
    <div key={key} className={cn('min-h-[250px] bg-white rounded-xl shadow-md shadow-slate-200/40 border border-slate-100/50 hover:shadow-lg hover:shadow-slate-200/60 transition-all duration-300 overflow-hidden flex flex-col', spanClass)}>
      <Component {...transformedProps} />
    </div>
  );
}

export default function UIConfigurationRenderer({ 
  uiConfig
}: UIConfigurationRendererProps) {
  
  if (!uiConfig?.ui_config?.selected_components) {
    return (
      <div className="p-6 bg-yellow-50 border border-yellow-200 rounded-lg">
        <div className="text-yellow-800 font-medium">Invalid UI Configuration</div>
        <div className="text-yellow-600 text-sm mt-1">
          No component configuration found
        </div>
        <pre className="text-xs text-yellow-500 mt-2 overflow-auto max-h-32">
          {JSON.stringify(uiConfig, null, 2)}
        </pre>
      </div>
    );
  }
  
  const { selected_components } = uiConfig.ui_config;
  const { analysis_data, metadata } = uiConfig;
  
  return (
    <div className="space-y-6">
      {/* Header with metadata */}
      {metadata?.question && (
        <div className="bg-blue-50 rounded-lg p-4 border-l-4 border-blue-500">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
            <span className="text-sm font-medium text-blue-700">Analysis Question</span>
          </div>
          <div className="text-blue-800 font-medium">
            {metadata.question}
          </div>
        </div>
      )}
      
      {/* 2-column fixed grid layout */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-4 w-full auto-rows-max">
        {selected_components.map((config, index) => 
          renderComponent(config, analysis_data, index)
        )}
      </div>
      
      {/* Debug info (development only) */}
      {process.env.NODE_ENV === 'development' && (
        <details className="mt-6">
          <summary className="cursor-pointer text-sm text-gray-500 hover:text-gray-700">
            Debug: UI Configuration
          </summary>
          <pre className="text-xs text-gray-500 mt-2 overflow-auto max-h-64 bg-gray-50 p-3 rounded border">
            {JSON.stringify(uiConfig, null, 2)}
          </pre>
        </details>
      )}
      
    </div>
  );
}