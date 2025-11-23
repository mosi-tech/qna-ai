/**
 * Test file for UIConfigurationRenderer
 * 
 * Simple test to verify the component renders with sample data
 */

import React from 'react';
import UIConfigurationRenderer from './UIConfigurationRenderer';

// Sample UI configuration for testing
const sampleUIConfig = {
  analysis_data: {
    etf_rankings: [
      { rank: 1, symbol: "QQQ", sharpe_improvement: 0.67, sharpe_improvement_pct: 67.0 },
      { rank: 2, symbol: "VTI", sharpe_improvement: 0.45, sharpe_improvement_pct: 45.0 },
      { rank: 3, symbol: "SPY", sharpe_improvement: 0.32, sharpe_improvement_pct: 32.0 }
    ],
    summary: {
      total_analyzed: 3,
      avg_improvement: 0.48,
      best_performer: "QQQ",
      worst_performer: "SPY"
    }
  },
  ui_config: {
    selected_components: [
      {
        component_name: "StatGroup",
        role: "summary" as const,
        props: {
          title: "Key Insights",
          stats: [
            { label: "Best Performer", value: "{{analysis_data.summary.best_performer}}" },
            { label: "Total ETFs", value: "{{analysis_data.summary.total_analyzed}}" },
            { label: "Avg Improvement", value: "{{analysis_data.summary.avg_improvement}}", format: "percentage" }
          ]
        },
        layout: { size: "third" as const, height: "short" as const },
        reasoning: "Summary component for quick insights"
      },
      {
        component_name: "BarChart",
        role: "primary" as const,
        props: {
          title: "ETF Performance",
          data: "{{analysis_data.etf_rankings}}",
          format: "percentage"
        },
        layout: { size: "half" as const, height: "medium" as const },
        reasoning: "Primary chart showing performance"
      },
      {
        component_name: "RankingTable",
        role: "supporting" as const,
        props: {
          title: "Complete Rankings",
          data: "{{analysis_data.etf_rankings}}",
          columns: [
            { id: "rank", name: "Rank", align: "center" },
            { id: "symbol", name: "Symbol", align: "left" },
            { id: "sharpe_improvement_pct", name: "Improvement", align: "right", format: "percentage" }
          ]
        },
        layout: { size: "full" as const, height: "medium" as const },
        reasoning: "Detailed table with complete data"
      }
    ],
    layout_template: "summary_first",
    priority: "insights_focus"
  },
  metadata: {
    question: "Which ETFs posted the largest improvement in 3-month Sharpe ratio?",
    generated_at: new Date().toISOString(),
    formatter_version: "1.0.0"
  }
};

// Simple test component
export default function UIConfigurationTest() {
  return (
    <div className="p-8 max-w-6xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-900 mb-2">
          UI Configuration Renderer Test
        </h1>
        <p className="text-gray-600">
          Testing dynamic component rendering from JSON configuration
        </p>
      </div>
      
      <UIConfigurationRenderer 
        uiConfig={sampleUIConfig}
      />
    </div>
  );
}