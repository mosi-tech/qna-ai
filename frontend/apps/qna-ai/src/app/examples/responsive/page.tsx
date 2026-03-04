"use client";

import React, { useState } from "react";

// Import ALL insight components (excluding layout, shared, poor folders)
import BarChart from "@/components/insights/BarChart";
import BulletList from "@/components/insights/BulletList";
import CalloutList from "@/components/insights/CalloutList";
import ExecutiveSummary from "@/components/insights/ExecutiveSummary";
import LineChart from "@/components/insights/LineChart";
import PieChart from "@/components/insights/PieChart";
import ScatterChart from "@/components/insights/ScatterChart";
import HeatmapTable from "@/components/insights/HeatmapTable";
import ComparisonTable from "@/components/insights/ComparisonTable";
import RankedList from "@/components/insights/RankedList";
import SectionedInsightCard from "@/components/insights/SectionedInsightCard";
import StatGroup from "@/components/insights/StatGroup";
import SummaryConclusion from "@/components/insights/SummaryConclusion";
import RankingTable from "@/components/insights/RankingTable";

const GRID_COLUMNS = 3; // 3x3 system

type GridItem = {
  id: string;
  component: React.ReactNode;
  layoutHint: "full" | "half" | "third";
  heightHint: "short" | "medium" | "tall";
  category: string;
};

const layoutHintToCols = {
  full: 3,
  half: 2,
  third: 1,
};

const layoutHintToClass = {
  full: "col-span-3",
  half: "col-span-2", 
  third: "col-span-1",
};

const heightHintToClass = {
  short: "min-h-32",
  medium: "min-h-48", 
  tall: "min-h-64",
};

function ResponsiveGrid({ items }: { items: GridItem[] }) {
  const rows: GridItem[][] = [];
  let currentRow: GridItem[] = [];
  let currentWidth = 0;

  for (const item of items) {
    const width = layoutHintToCols[item.layoutHint];
    if (currentWidth + width > GRID_COLUMNS) {
      rows.push(currentRow);
      currentRow = [];
      currentWidth = 0;
    }
    currentRow.push(item);
    currentWidth += width;
  }
  if (currentRow.length) rows.push(currentRow);

  return (
    <div className="space-y-4 p-4 w-full">
      {rows.map((row, rowIndex) => (
        <div key={rowIndex} className="grid grid-cols-3 gap-4 auto-rows-min w-full">
          {row.map((item) => (
            <div
              key={item.id}
              className={`${layoutHintToClass[item.layoutHint]} ${heightHintToClass[item.heightHint]}`}
            >
              {item.component}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
}

function ComponentShowcase() {
  const [selectedSizes, setSelectedSizes] = useState<Record<string, string>>({});
  const [selectedVariants, setSelectedVariants] = useState<Record<string, string>>({});
  const [selectedCategory, setSelectedCategory] = useState<string>("all");

  const updateSize = (componentId: string, size: string) => {
    setSelectedSizes(prev => ({ ...prev, [componentId]: size }));
  };

  const updateVariant = (componentId: string, variant: string) => {
    setSelectedVariants(prev => ({ ...prev, [componentId]: variant }));
  };

  const getSize = (componentId: string) => selectedSizes[componentId] || "half";
  const getVariant = (componentId: string) => selectedVariants[componentId] || "default";

  // Comprehensive sample data for all components
  const sampleData = {
    // Basic data structures
    executiveSummary: [
      { label: "Key Finding", text: "Portfolio performed 15% above benchmark", color: "green" as const },
      { label: "Performance", text: "Strong growth in tech sector positions", color: "blue" as const },
      { label: "Recommendation", text: "Consider rebalancing to maintain target allocation", color: "orange" as const }
    ],
    
    bulletPoints: ["Tech sector outperformed by 8% this quarter", "Emerging markets showed resilience", "Fixed income allocation provided stable returns"],
    
    rankedItems: [
      { id: "1", name: "Apple Inc.", value: "25.3%", changeType: "positive" as const },
      { id: "2", name: "Microsoft Corp.", value: "18.7%", changeType: "positive" as const },
      { id: "3", name: "Amazon.com Inc.", value: "12.1%", changeType: "negative" as const }
    ],

    keyValueData: [
      { metric: "Total Return", value: "12.5%", target: "10.0%" },
      { metric: "Volatility", value: "8.2%", target: "9.0%" },
      { metric: "Sharpe Ratio", value: "1.52", target: "1.30" }
    ],

    keyValueColumns: [
      { key: "metric", label: "Metric", align: "left" as const },
      { key: "value", label: "Value", align: "right" as const },
      { key: "target", label: "Target", align: "right" as const }
    ],


    actionItems: [
      { 
        id: "1", 
        title: "Rebalance Portfolio Allocation",
        description: "Adjust portfolio weights to maintain target allocation ratios",
        priority: "high" as const, 
        timeline: "immediate" as const,
        impact: "high" as const,
        effort: "medium" as const
      },
      { 
        id: "2", 
        title: "Review ESG Compliance",
        description: "Assess portfolio holdings against ESG criteria and standards",
        priority: "medium" as const,
        timeline: "short-term" as const,
        impact: "medium" as const,
        effort: "low" as const
      },
      { 
        id: "3", 
        title: "Update Risk Assessment",
        description: "Refresh risk models and stress test scenarios",
        priority: "low" as const,
        timeline: "medium-term" as const,
        impact: "medium" as const,
        effort: "high" as const
      }
    ],

    comparisonEntities: [
      { id: "current", name: "Current Quarter" },
      { id: "previous", name: "Previous Quarter" },
      { id: "benchmark", name: "Benchmark" }
    ],

    comparisonMetrics: [
      { id: "return", name: "Return", format: "percentage" },
      { id: "risk", name: "Risk", format: "percentage" },
      { id: "sharpe", name: "Sharpe Ratio", format: "number" }
    ],

    comparisonData: {
      current: { return: 12.5, risk: 8.1, sharpe: 1.54 },
      previous: { return: 10.2, risk: 9.3, sharpe: 1.10 },
      benchmark: { return: 8.9, risk: 7.5, sharpe: 1.19 }
    },

    matrixData: [
      [1.00, 0.25, 0.15, -0.12],
      [0.25, 1.00, 0.45, 0.32],
      [0.15, 0.45, 1.00, 0.67],
      [-0.12, 0.32, 0.67, 1.00]
    ],
    
    matrixRowLabels: ["Stocks", "Bonds", "REITs", "Commodities"],
    matrixColumnLabels: ["Stocks", "Bonds", "REITs", "Commodities"],

    confidenceInterval: { lower: 8.2, upper: 16.8 },

    timelineEvents: [
      { id: "1", date: "2024-Q1", title: "Portfolio Rebalancing", description: "Adjusted allocation based on market conditions" },
      { id: "2", date: "2024-Q2", title: "ESG Integration", description: "Implemented sustainable investing criteria" }
    ]
  };

  // All components with sample data
  const components = [
    // CHARTS
    {
      id: "barchart",
      name: "BarChart",
      category: "charts",
      component: (
        <BarChart
          title="Holdings Performance"
          data={[
            { label: "AAPL", value: 35.3 },
            { label: "MSFT", value: 31.0 },
            { label: "GOOGL", value: 27.8 },
            { label: "TSLA", value: 23.5 },
            { label: "NVDA", value: 18.2 }
          ]}
          format="percentage"
          color="blue"
          showValues={true}
        />
      )
    },
    {
      id: "piechart", 
      name: "PieChart",
      category: "charts",
      component: (
        <PieChart
          title="Portfolio Allocation"
          data={[
            { label: "Technology", value: 35, color: "#3B82F6" },
            { label: "Healthcare", value: 25, color: "#10B981" },
            { label: "Finance", value: 20, color: "#F59E0B" },
            { label: "Energy", value: 15, color: "#EF4444" },
            { label: "Other", value: 5, color: "#8B5CF6" }
          ]}
          showLegend={true}
          showPercentages={true}
        />
      )
    },
    {
      id: "linechart",
      name: "LineChart", 
      category: "charts",
      component: (
        <LineChart
          title="Portfolio Return Over Time"
          data={[
            { label: "Jan", value: 8.2 },
            { label: "Feb", value: 12.1 },
            { label: "Mar", value: 15.3 },
            { label: "Apr", value: 11.8 },
            { label: "May", value: 18.7 },
            { label: "Jun", value: 22.4 }
          ]}
          format="percentage"
          showDots={true}
          showArea={false}
        />
      )
    },
    {
      id: "scatterchart",
      name: "ScatterChart",
      category: "charts", 
      component: (
        <ScatterChart
          title="Risk vs Return Analysis"
          data={[
            { x: 8.2, y: 12.5, label: "AAPL" },
            { x: 15.3, y: 18.7, label: "TSLA" },
            { x: 6.8, y: 9.3, label: "MSFT" },
            { x: 12.1, y: 14.2, label: "GOOGL" },
            { x: 20.5, y: 25.8, label: "NVDA" }
          ]}
          xAxis={{ label: "Risk (%)", format: "percentage" }}
          yAxis={{ label: "Return (%)", format: "percentage" }}
          showTrendLine={true}
        />
      )
    },

    // CARDS & DISPLAYS
    {
      id: "statgroup",
      name: "StatGroup",
      category: "cards",
      component: (
        <StatGroup
          title="Key Metrics"
          stats={[
            { label: "Return", value: "12.5%", change: 2.3 },
            { label: "Risk", value: "8.2%", change: -0.5 },
            { label: "Sharpe", value: "1.52", change: 0.2 }
          ]}
          variant={getVariant("statgroup") as any}
        />
      )
    },
    {
      id: "sectionedinsight",
      name: "SectionedInsightCard",
      category: "cards",
      component: (
        <SectionedInsightCard
          title="Market Analysis"
          description="Comprehensive quarterly market review"
          sections={[
            { 
              title: "Overview", 
              content: [
                "Market showed strong performance this quarter",
                "Volatility remained within expected ranges",
                "Investor sentiment improved significantly"
              ],
              type: "default"
            },
            { 
              title: "Key Drivers", 
              content: [
                "Technology sector led with 18% gains",
                "Healthcare innovations drove growth",
                "Federal Reserve policy remained accommodative"
              ],
              type: "highlight"
            }
          ]}
          variant={getVariant("sectionedinsight") as any}
        />
      )
    },

    // LISTS & TEXT
    {
      id: "executive",
      name: "ExecutiveSummary",
      category: "lists",
      component: (
        <ExecutiveSummary
          title="Portfolio Summary"
          items={sampleData.executiveSummary}
          variant={getVariant("executive") as any}
        />
      )
    },
    {
      id: "bullets",
      name: "BulletList",
      category: "lists",
      component: (
        <BulletList
          title="Key Insights"
          items={sampleData.bulletPoints}
          variant={getVariant("bullets") as any}
        />
      )
    },
    {
      id: "ranked",
      name: "RankedList",
      category: "lists",
      component: (
        <RankedList
          title="Top Holdings"
          items={sampleData.rankedItems}
          maxItems={3}
          variant={getVariant("ranked") as any}
        />
      )
    },
    {
      id: "calloutlist",
      name: "CalloutList",
      category: "lists",
      component: (
        <CalloutList
          title="Important Notes"
          items={[
            { 
              id: "1",
              title: "Sector Concentration Risk", 
              content: "High concentration in tech sector requires monitoring",
              type: "warning" 
            },
            { 
              id: "2", 
              title: "ESG Performance", 
              content: "ESG score improved significantly this quarter",
              type: "success" 
            },
            { 
              id: "3", 
              title: "Market Volatility", 
              content: "Increased volatility expected due to upcoming earnings",
              type: "info" 
            }
          ]}
          variant={getVariant("calloutlist") as any}
        />
      )
    },

    // TABLES
    {
      id: "heatmap",
      name: "HeatmapTable",
      category: "tables",
      component: (
        <HeatmapTable
          title="Performance Heatmap"
          data={[
            [0.85, 0.23, 0.67, 0.92],
            [0.23, 1.00, 0.45, 0.31],
            [0.67, 0.45, 0.88, 0.76],
            [0.92, 0.31, 0.76, 0.95]
          ]}
          rowLabels={["Technology", "Healthcare", "Finance", "Energy"]}
          columnLabels={["Q1", "Q2", "Q3", "Q4"]}
          cellConfig={{
            format: "percentage",
            decimals: 1,
            colorScheme: "heatmap",
            showDiagonal: true,
            highlightDiagonal: false
          }}
          legend={[
            { color: "bg-blue-200", label: "Excellent", description: "80-100%" },
            { color: "bg-blue-100", label: "Good", description: "60-80%" },
            { color: "bg-blue-50", label: "Average", description: "40-60%" },
            { color: "bg-white", label: "Below Average", description: "0-40%" }
          ]}
          variant={getVariant("heatmap") as any}
        />
      )
    },
    {
      id: "comparison",
      name: "ComparisonTable",
      category: "tables",
      component: (
        <ComparisonTable
          title="Performance Comparison"
          entities={[
            { id: "q1", name: "Q1 2024", shortName: "Q1", description: "First Quarter" },
            { id: "q2", name: "Q2 2024", shortName: "Q2", description: "Second Quarter" },
            { id: "portfolio", name: "Our Portfolio", shortName: "Portfolio", description: "Current Strategy" },
            { id: "benchmark", name: "Benchmark", shortName: "Benchmark", description: "S&P 500 Index" }
          ]}
          metrics={[
            { id: "return", name: "Return", format: "percentage" },
            { id: "risk", name: "Risk", format: "percentage" },
            { id: "sharpe", name: "Sharpe Ratio", format: "ratio" }
          ]}
          data={{
            return: { q1: 8.2, q2: 12.1, portfolio: 15.3, benchmark: 11.5 },
            risk: { q1: 9.1, q2: 8.5, portfolio: 8.2, benchmark: 9.0 },
            sharpe: { q1: 0.90, q2: 1.42, portfolio: 1.87, benchmark: 1.28 }
          }}
          showChange={true}
          highlightBest={true}
          variant={getVariant("comparison") as any}
        />
      )
    },
    {
      id: "ranking",
      name: "RankingTable",
      category: "tables",
      component: (
        <RankingTable
          title="Top Performers Ranking"
          data={[
            {
              id: "AAPL",
              name: "Apple Inc.",
              score: 0.92,
              return: 0.156,
              volume: 45000000,
              marketCap: 2800000000000
            },
            {
              id: "MSFT", 
              name: "Microsoft Corp.",
              score: 0.87,
              return: 0.142,
              volume: 38000000,
              marketCap: 2400000000000
            },
            {
              id: "NVDA",
              name: "NVIDIA Corp.", 
              score: 0.83,
              return: 0.234,
              volume: 52000000,
              marketCap: 1800000000000
            },
            {
              id: "GOOGL",
              name: "Alphabet Inc.",
              score: 0.78,
              return: 0.089,
              volume: 28000000,
              marketCap: 1600000000000
            }
          ]}
          columns={[
            { id: "score", name: "Score", align: "center", format: "badge", colorScale: (value: number) => 
              value >= 0.8 ? 'text-green-700 bg-green-50' : 
              value >= 0.6 ? 'text-yellow-600 bg-yellow-50' : 
              'text-red-600 bg-red-50'
            },
            { id: "return", name: "Return", align: "center", format: "percentage" },
            { id: "volume", name: "Volume", align: "right", format: "number" },
            { id: "marketCap", name: "Market Cap", align: "right", format: "currency" }
          ]}
          primaryColumn="score"
          variant={getVariant("ranking") as any}
        />
      )
    },


    // TEXT
    {
      id: "summaryconclusion",
      name: "SummaryConclusion",
      category: "text",
      component: (
        <SummaryConclusion
          title="Investment Analysis Conclusion"
          keyFindings={[
            "Portfolio outperformed benchmark by 3.6% this quarter",
            "Technology sector contributed 65% of total returns",
            "Risk metrics improved with Sharpe ratio increasing to 1.54",
            "ESG score advanced from B+ to A- rating"
          ]}
          conclusion="Based on comprehensive analysis, the portfolio demonstrates strong performance with controlled risk. Recommend maintaining current allocation with slight rebalancing towards emerging markets to capture additional growth opportunities."
          nextSteps={[
            "Increase emerging markets allocation by 2-3%",
            "Monitor technology sector concentration",
            "Review ESG criteria quarterly"
          ]}
          confidence="high"
          variant={getVariant("summaryconclusion") as any}
        />
      )
    },



  ];

  const categories = ["all", "charts", "cards", "lists", "tables", "text"];

  const filteredComponents = selectedCategory === "all" 
    ? components 
    : components.filter(comp => comp.category === selectedCategory);

  const gridItems: GridItem[] = filteredComponents.map(comp => ({
    id: comp.id,
    component: comp.component,
    layoutHint: getSize(comp.id) as any,
    heightHint: "medium",
    category: comp.category
  }));

  return (
    <div className="min-h-screen w-full bg-gray-50">
      <div className="p-6">
        <h1 className="text-3xl font-bold mb-2">Responsive Insights Components</h1>
        <p className="text-gray-600 mb-4">Test all 48 insights components in a 3x3 responsive grid system</p>
        <p className="text-sm text-gray-500 mb-8">
          Total Components: <strong>{components.length}</strong> | 
          Filtered: <strong>{filteredComponents.length}</strong>
        </p>
        
        {/* Category Filter */}
        <div className="mb-6 bg-white rounded-lg p-4 shadow-sm">
          <label className="block text-sm font-medium mb-2">Filter by Category:</label>
          <div className="flex flex-wrap gap-2">
            {categories.map(category => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-3 py-1 rounded text-sm capitalize ${
                  selectedCategory === category 
                    ? "bg-blue-500 text-white" 
                    : "bg-gray-200 text-gray-700 hover:bg-gray-300"
                }`}
              >
                {category} {category !== "all" && `(${components.filter(c => c.category === category).length})`}
              </button>
            ))}
          </div>
        </div>
        
        {/* Controls */}
        <div className="mb-8 bg-white rounded-lg p-6 shadow-sm max-h-96 overflow-y-auto">
          <h2 className="text-xl font-semibold mb-4">Component Controls</h2>
          <div className="grid gap-3">
            {filteredComponents.map(comp => {
              const isChart = comp.category === "charts";
              return (
                <div key={comp.id} className="flex items-center gap-4 p-3 bg-gray-50 rounded text-sm">
                  <div className="min-w-48 font-medium">{comp.name}</div>
                  <div className="text-xs text-gray-500 min-w-20">{comp.category}</div>
                  
                  <div className="flex gap-2">
                    <label className="text-xs text-gray-600">Size:</label>
                    {["third", "half", "full"].map(size => (
                      <button
                        key={size}
                        onClick={() => updateSize(comp.id, size)}
                        className={`px-2 py-1 rounded text-xs ${
                          getSize(comp.id) === size 
                            ? "bg-blue-500 text-white" 
                            : "bg-white text-gray-700 hover:bg-gray-100"
                        }`}
                      >
                        {size}
                      </button>
                    ))}
                  </div>

                  {!isChart && (
                    <div className="flex gap-2">
                      <label className="text-xs text-gray-600">Variant:</label>
                      {["compact", "default", "detailed"].map(variant => (
                        <button
                          key={variant}
                          onClick={() => updateVariant(comp.id, variant)}
                          className={`px-2 py-1 rounded text-xs ${
                            getVariant(comp.id) === variant 
                              ? "bg-green-500 text-white" 
                              : "bg-white text-gray-700 hover:bg-gray-100"
                          }`}
                        >
                          {variant}
                        </button>
                      ))}
                    </div>
                  )}

                  {isChart && (
                    <div className="flex gap-2">
                      <span className="text-xs text-gray-500 italic">Auto-responsive</span>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Grid Layout */}
        <div className="bg-white rounded-lg shadow-sm">
          <div className="p-4 border-b">
            <h2 className="text-xl font-semibold">3x3 Responsive Grid Preview</h2>
            <p className="text-sm text-gray-600">
              Showing {filteredComponents.length} components | Components auto-wrap when they don't fit
            </p>
          </div>
          <ResponsiveGrid items={gridItems} />
        </div>
      </div>
    </div>
  );
}

export default ComponentShowcase;