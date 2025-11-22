'use client';

import React from 'react';
import { GRID_SLOTS, GRID_STYLES, SLOT_VISIBILITY_RULES, PREDEFINED_CONFIGS } from './predefined-grid-config';

// Import all our existing components
import BarChart from '@/components/insights/BarChart';
import BulletList from '@/components/insights/BulletList';
import CalloutList from '@/components/insights/CalloutList';
import ExecutiveSummary from '@/components/insights/ExecutiveSummary';
import LineChart from '@/components/insights/LineChart';
import PieChart from '@/components/insights/PieChart';
import ScatterChart from '@/components/insights/ScatterChart';
import HeatmapTable from '@/components/insights/HeatmapTable';
import ComparisonTable from '@/components/insights/ComparisonTable';
import RankedList from '@/components/insights/RankedList';
import SectionedInsightCard from '@/components/insights/SectionedInsightCard';
import StatGroup from '@/components/insights/StatGroup';
import SummaryConclusion from '@/components/insights/SummaryConclusion';
import RankingTable from '@/components/insights/RankingTable';

interface PredefinedGridRendererProps {
  configType: string;
  analysisData: any;
}

const COMPONENT_MAP = {
  BarChart,
  BulletList,
  CalloutList,
  ExecutiveSummary,
  LineChart,
  PieChart,
  ScatterChart,
  HeatmapTable,
  ComparisonTable,
  RankedList,
  SectionedInsightCard,
  StatGroup,
  SummaryConclusion,
  RankingTable
};

// Transform data placeholders like {{analysis_data.path}} to actual values
const transformProps = (props: any, analysisData: any) => {
  const transformValue = (value: any): any => {
    if (typeof value === 'string' && value.startsWith('{{') && value.endsWith('}}')) {
      const path = value.slice(2, -2).replace('analysis_data.', '');
      return getNestedValue(analysisData, path) || value;
    }
    if (Array.isArray(value)) {
      return value.map(transformValue);
    }
    if (typeof value === 'object' && value !== null) {
      const transformed: any = {};
      Object.keys(value).forEach(key => {
        transformed[key] = transformValue(value[key]);
      });
      return transformed;
    }
    return value;
  };

  return transformValue(props);
};

// Helper to get nested object values
const getNestedValue = (obj: any, path: string) => {
  return path.split('.').reduce((current, key) => current?.[key], obj);
};

// Determine if a slot should be visible based on data
const isSlotVisible = (slotId: string, analysisData: any): boolean => {
  const rule = SLOT_VISIBILITY_RULES[slotId];
  return rule ? rule(analysisData) : false;
};

export default function PredefinedGridRenderer({ 
  configType, 
  analysisData 
}: PredefinedGridRendererProps) {
  const config = PREDEFINED_CONFIGS[configType];
  
  if (!config) {
    return <div className="text-red-400">Unknown configuration type: {configType}</div>;
  }

  return (
    <div className="w-full">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-gray-800">{config.title}</h2>
        <p className="text-sm text-gray-600">Responsive 2x5 Grid Layout</p>
      </div>
      
      {/* Responsive Grid - Flattened for better mobile experience */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-2 gap-4 w-full">
        {Object.entries(config.slots).map(([slotId, slotConfig]) => {
          if (!slotConfig || !isSlotVisible(slotId, analysisData)) return null;
          
          const slot = GRID_SLOTS[slotId];
          const Component = COMPONENT_MAP[slotConfig.component];
          
          if (!Component) return null;
          
          const transformedProps = transformProps(slotConfig.props, analysisData);

          return (
            <div
              key={slotId}
              className={`
                min-h-[250px]
                bg-white
                rounded-lg
                shadow-lg
                border-t border-slate-100
                overflow-hidden
                flex flex-col
                ${slot.span === 'full' ? 'sm:col-span-2' : ''}
              `}
            >
              {transformedProps && Component && <Component {...transformedProps} />}
            </div>
          );
        })}
      </div>
      
      {/* Debug info */}
      <details className="mt-4 text-sm">
        <summary className="cursor-pointer text-gray-600 hover:text-gray-800">
          Debug: Grid Layout Info
        </summary>
        <div className="mt-2 bg-gray-50 p-3 rounded border">
          <p><strong>Configuration:</strong> {configType}</p>
          <p><strong>Total Slots:</strong> 10 (2 columns × 5 rows)</p>
          <p><strong>Visible Components:</strong> {Object.keys(config.slots).filter(slotId => isSlotVisible(slotId, analysisData)).length}</p>
          <p><strong>Data Keys:</strong> {Object.keys(analysisData).join(', ')}</p>
        </div>
      </details>
    </div>
  );
}