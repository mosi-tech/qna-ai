/**
 * Predefined Grid UI Configuration
 * 2 columns x 5 rows = 10 slots with conditional rendering
 */

// Grid slot definitions - each slot has a specific purpose
export const GRID_SLOTS = {
  // Row 1: Key Metrics (always shown if data exists)
  slot_1_1: { position: [0, 0], type: 'metric', priority: 1, component: 'StatGroup' },
  slot_1_2: { position: [0, 1], type: 'metric', priority: 2, component: 'StatGroup' },
  
  // Row 2: Primary Charts (main visualization)
  slot_2_1: { position: [1, 0], type: 'chart_primary', priority: 3, component: ['BarChart', 'LineChart', 'PieChart'] },
  slot_2_2: { position: [1, 1], type: 'chart_secondary', priority: 4, component: ['ScatterChart', 'PieChart', 'AreaChart'] },
  
  // Row 3: Data Tables or Lists
  slot_3_1: { position: [2, 0], type: 'data', priority: 5, component: ['RankingTable', 'ComparisonTable'] },
  slot_3_2: { position: [2, 1], type: 'list', priority: 6, component: ['RankedList', 'BulletList'] },
  
  // Row 4: Analysis & Insights  
  slot_4_1: { position: [3, 0], type: 'analysis', priority: 7, component: ['ExecutiveSummary', 'CalloutList'] },
  slot_4_2: { position: [3, 1], type: 'insight', priority: 8, component: ['SectionedInsightCard', 'HeatmapTable'] },
  
  // Row 5: Summary & Actions (span full width)
  slot_5_1: { position: [4, 0], type: 'summary', priority: 9, component: 'SummaryConclusion', span: 'full' },
  slot_5_2: { position: [4, 1], type: 'hidden', priority: 10, component: null } // Hidden when row 5 spans full
};

// Predefined configurations for different analysis types
export const PREDEFINED_CONFIGS = {
  portfolioAnalysis: {
    title: "Portfolio Analysis Dashboard",
    slots: {
      slot_1_1: {
        component: "StatGroup",
        props: {
          title: "Performance Metrics",
          stats: [
            { label: "Annual Return", value: "18.7%", subtitle: "Year-over-year", format: "text" },
            { label: "Sharpe Ratio", value: "1.54", subtitle: "Risk-adjusted", format: "text" },
            { label: "YTD Return", value: "12.3%", subtitle: "Year-to-date", format: "text" },
            { label: "3Y Return", value: "45.8%", subtitle: "3-year CAGR", format: "text" }
          ],
          columns: 4
        }
      },
      slot_1_2: {
        component: "StatGroup", 
        props: {
          title: "Portfolio Risk & Details",
          stats: [
            { label: "Volatility", value: "12.4%", subtitle: "Annual std dev", format: "text" },
            { label: "Beta", value: "1.23", subtitle: "Market sensitivity", format: "text" },
            { label: "Max Drawdown", value: "-15.6%", subtitle: "Worst decline", format: "text" },
            { label: "Win Rate", value: "68%", subtitle: "Positive months", format: "text" },
            { label: "Sharpe Ratio", value: "1.54", subtitle: "Risk-adjusted return", format: "text" },
            { label: "Sortino Ratio", value: "2.31", subtitle: "Downside adjusted", format: "text" }
          ],
          columns: 6
        }
      },
      slot_2_1: {
        component: "PieChart",
        props: {
          title: "Sector Allocation",
          data: [
            { label: "Technology", value: 58, color: "#3B82F6" },
            { label: "Finance", value: 15, color: "#10B981" },
            { label: "Consumer", value: 12, color: "#F59E0B" },
            { label: "Healthcare", value: 8, color: "#EF4444" },
            { label: "Energy", value: 7, color: "#8B5CF6" }
          ],
          showLegend: true,
          showPercentages: true
        }
      },
      slot_2_2: {
        component: "LineChart",
        props: {
          title: "Performance Timeline",
          data: [
            { label: "Jan", value: 8.0 },
            { label: "Feb", value: 12.0 },
            { label: "Mar", value: 15.0 },
            { label: "Apr", value: 9.0 },
            { label: "May", value: 18.0 },
            { label: "Jun", value: 25.0 }
          ],
          format: "percentage",
          showDots: true
        }
      },
      slot_3_1: {
        component: "RankingTable",
        props: {
          title: "Top Holdings",
          data: [
            { id: "AAPL", symbol: "AAPL", name: "Apple Inc.", weight: 0.25, return: 0.156 },
            { id: "MSFT", symbol: "MSFT", name: "Microsoft", weight: 0.18, return: 0.142 },
            { id: "GOOGL", symbol: "GOOGL", name: "Google", weight: 0.15, return: 0.089 },
            { id: "TSLA", symbol: "TSLA", name: "Tesla", weight: 0.12, return: 0.234 }
          ],
          columns: [
            { id: "symbol", name: "Symbol", align: "left" },
            { id: "weight", name: "Weight", align: "right", format: "percentage" },
            { id: "return", name: "Return", align: "right", format: "percentage" }
          ],
          primaryColumn: "symbol",
          variant: "compact"
        }
      },
      slot_3_2: {
        component: "BulletList",
        props: {
          title: "Key Insights",
          items: [
            "Technology sector drives portfolio performance with 58% allocation",
            "Sharpe ratio of 1.54 indicates strong risk-adjusted returns",
            "Portfolio beta of 1.23 shows moderate market sensitivity",
            "6-month return of 25% significantly outperforms benchmark"
          ],
          variant: "compact"
        }
      },
      slot_4_1: {
        component: "ExecutiveSummary",
        props: {
          title: "Summary",
          items: [
            { label: "Performance", text: "Strong returns vs benchmark", color: "green" },
            { label: "Risk", text: "Moderate volatility profile", color: "blue" }
          ],
          variant: "compact"
        }
      },
      slot_4_2: {
        component: "CalloutList",
        props: {
          title: "Recommendations",
          items: [
            {
              id: "1",
              title: "Rebalance Portfolio",
              content: "Reduce tech concentration from 58% to 45% for better diversification",
              type: "warning"
            },
            {
              id: "2", 
              title: "Add International",
              content: "Allocate 10-15% to emerging markets for growth potential",
              type: "info"
            },
            {
              id: "3",
              title: "Strong Performance",
              content: "Portfolio generates 18.7% annual return with attractive risk metrics",
              type: "success"
            }
          ],
          variant: "compact"
        }
      },
      slot_5_1: {
        component: "SummaryConclusion",
        props: {
          title: "Investment Conclusion",
          keyFindings: [
            "Portfolio outperformed benchmark by 6.8%",
            "Risk metrics within target parameters",
            "Technology allocation requires monitoring"
          ],
          conclusion: "Maintain current strategy with selective rebalancing",
          nextSteps: [
            "Reduce tech allocation to 45%",
            "Add international exposure"
          ],
          confidence: "high",
          variant: "compact"
        }
      }
    }
  },
  
  stockAnalysis: {
    title: "Stock Analysis Dashboard", 
    slots: {
      slot_1_1: {
        component: "StatGroup",
        props: {
          title: "Price Metrics",
          stats: [
            { label: "Current", value: "{{analysis_data.current_price}}", format: "currency" },
            { label: "Change", value: "{{analysis_data.price_change}}", format: "percentage" }
          ],
          variant: "compact"
        }
      },
      slot_1_2: {
        component: "StatGroup",
        props: {
          title: "Valuation",
          stats: [
            { label: "P/E Ratio", value: "{{analysis_data.pe_ratio}}", format: "number" },
            { label: "Market Cap", value: "{{analysis_data.market_cap}}", format: "currency" }
          ],
          variant: "compact"
        }
      },
      slot_2_1: {
        component: "LineChart",
        props: {
          title: "Price History",
          data: "{{analysis_data.price_history}}",
          format: "currency",
          showArea: true
        }
      },
      slot_2_2: {
        component: "BarChart", 
        props: {
          title: "Volume Analysis",
          data: "{{analysis_data.volume_data}}",
          format: "number"
        }
      },
      // ... continue with remaining slots
    }
  },
  
  sectorComparison: {
    title: "Sector Comparison Dashboard",
    slots: {
      slot_1_1: {
        component: "StatGroup",
        props: {
          title: "Best Performer",
          stats: [
            { label: "Sector", value: "{{analysis_data.best_sector.name}}" },
            { label: "Return", value: "{{analysis_data.best_sector.return}}", format: "percentage" }
          ]
        }
      },
      // ... continue with sector-specific layout
    }
  },

  drawdownAnalysis: {
    title: "QQQ 2010 Drawdown Analysis",
    slots: {
      slot_1_1: {
        component: "StatGroup",
        props: {
          title: "QQQ 2010 Drawdown Analysis",
          stats: [
            {
              label: "Max Drawdown",
              value: "{{analysis_data.max_drawdown_percentage}}"
            },
            {
              label: "Data Points",
              value: "{{analysis_data.data_points_analyzed}}",
              format: "number"
            },
            {
              label: "Trading Days",
              value: "{{analysis_data.trading_days}}",
              format: "number"
            }
          ],
          columns: 3
        }
      },
      slot_1_2: {
        component: "ExecutiveSummary",
        props: {
          title: "Key Findings",
          items: [
            {
              label: "Drawdown Severity",
              text: "QQQ experienced a maximum drawdown of 13.97% in 2010, indicating significant market volatility",
              color: "red"
            },
            {
              label: "Data Coverage",
              text: "Analysis covered 261 data points across 260 trading days, providing comprehensive market coverage",
              color: "blue"
            },
            {
              label: "Risk Assessment",
              text: "The 13.97% maximum drawdown represents substantial risk exposure for investors in 2010",
              color: "orange"
            }
          ]
        }
      },
      slot_2_1: {
        component: "BarChart",
        props: {
          title: "Analysis Metrics",
          data: [
            {
              label: "Max Drawdown %",
              value: -13.97
            },
            {
              label: "Data Points",
              value: 261
            },
            {
              label: "Trading Days",
              value: 260
            }
          ],
          format: "number",
          color: "red"
        }
      },
      slot_2_2: null,
      slot_3_1: null,
      slot_3_2: null,
      slot_4_1: null,
      slot_4_2: null,
      slot_5_1: null,
      slot_5_2: null
    }
  }
};

// Data-driven slot visibility rules
export const SLOT_VISIBILITY_RULES = {
  slot_1_1: (data) => data.portfolio_metrics || data.current_price || data.max_drawdown_percentage,
  slot_1_2: (data) => data.portfolio_metrics || data.pe_ratio || data.max_drawdown_percentage,
  slot_2_1: (data) => data.sector_allocation || data.price_history || data.data_points_analyzed,
  slot_2_2: (data) => data.performance_timeline || data.volume_data,
  slot_3_1: (data) => data.holdings || data.comparison_data,
  slot_3_2: (data) => data.key_insights || data.ranked_items,
  slot_4_1: (data) => true, // Summary always shown
  slot_4_2: (data) => data.recommendations || data.callouts,
  slot_5_1: (data) => true, // Conclusion always shown if space available
};

// Responsive grid classes
export const GRID_STYLES = {
  container: "grid grid-cols-2 gap-3 w-full max-w-none",
  slot: "min-h-[200px] flex flex-col",
  slotFull: "col-span-2 min-h-[250px]", // For full-width components
  slotHidden: "hidden",
  slotCompact: "min-h-[150px]"
};