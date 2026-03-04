/**
 * UI Configuration Test Data
 * Simulates various backend responses with different component combinations
 */

export const drawdownAnalysisData = {
  max_drawdown_percentage: -13.97,
  data_points_analyzed: 261,
  trading_days: 260
};

export const sampleAnalysisData = {
  portfolio_metrics: {
    total_value: 1250000,
    monthly_return: 0.125,
    annual_return: 0.187,
    sharpe_ratio: 1.54,
    volatility: 0.082,
    max_drawdown: 0.156,
    beta: 1.23,
    alpha: 0.032
  },
  holdings: [
    { symbol: "AAPL", weight: 0.25, return: 0.156, sector: "Technology" },
    { symbol: "MSFT", weight: 0.18, return: 0.142, sector: "Technology" },
    { symbol: "GOOGL", weight: 0.15, return: 0.089, sector: "Technology" },
    { symbol: "TSLA", weight: 0.12, return: 0.234, sector: "Consumer" },
    { symbol: "JPM", weight: 0.10, return: 0.076, sector: "Finance" },
    { symbol: "JNJ", weight: 0.08, return: 0.045, sector: "Healthcare" },
    { symbol: "XOM", weight: 0.07, return: 0.123, sector: "Energy" },
    { symbol: "BAC", weight: 0.05, return: 0.098, sector: "Finance" }
  ],
  sector_allocation: [
    { sector: "Technology", weight: 0.58, return: 0.162 },
    { sector: "Finance", weight: 0.15, return: 0.087 },
    { sector: "Consumer", weight: 0.12, return: 0.234 },
    { sector: "Healthcare", weight: 0.08, return: 0.045 },
    { sector: "Energy", weight: 0.07, return: 0.123 }
  ],
  performance_timeline: [
    { date: "2024-01", value: 1.08 },
    { date: "2024-02", value: 1.12 },
    { date: "2024-03", value: 1.15 },
    { date: "2024-04", value: 1.09 },
    { date: "2024-05", value: 1.18 },
    { date: "2024-06", value: 1.25 }
  ],
  key_insights: [
    "Technology sector driving portfolio performance with 58% allocation",
    "Sharpe ratio of 1.54 indicates strong risk-adjusted returns",
    "Portfolio beta of 1.23 shows moderate market sensitivity",
    "6-month return of 25% significantly outperforms benchmark"
  ],
  recommendations: [
    {
      action: "Rebalance Portfolio",
      description: "Reduce tech concentration to 45% for better diversification",
      priority: "High",
      impact: "Risk Reduction"
    },
    {
      action: "Add International Exposure",
      description: "Allocate 10-15% to emerging markets for growth potential",
      priority: "Medium", 
      impact: "Diversification"
    },
    {
      action: "ESG Review",
      description: "Evaluate holdings against ESG criteria for sustainable investing",
      priority: "Low",
      impact: "Alignment"
    }
  ]
};

export const uiConfigurations = {
  // Configuration 1: Dense Component Showcase
  denseShowcase: {
    ui_config: {
      selected_components: [
        {
          component_name: "StatGroup",
          props: {
            title: "Key Metrics",
            stats: [
              { label: "Value", value: "{{analysis_data.portfolio_metrics.total_value}}", format: "currency", change: 125000, changeType: "positive" },
              { label: "Return", value: "{{analysis_data.portfolio_metrics.annual_return}}", format: "percentage", change: 3.2, changeType: "positive" },
              { label: "Sharpe", value: "{{analysis_data.portfolio_metrics.sharpe_ratio}}", format: "number", change: 0.15, changeType: "positive" },
              { label: "Risk", value: "{{analysis_data.portfolio_metrics.volatility}}", format: "percentage", change: -0.8, changeType: "negative" }
            ],
            columns: 4,
          },
          layout: { size: "full", height: "short" }
        },
        {
          component_name: "RankedList",
          props: {
            title: "Top Holdings",
            items: [
              { id: "1", name: "Apple Inc.", value: "25.0%", changeType: "positive" },
              { id: "2", name: "Microsoft", value: "18.0%", changeType: "positive" },
              { id: "3", name: "Tesla", value: "12.0%", changeType: "positive" }
            ],
            maxItems: 3,
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "PieChart",
          props: {
            title: "Allocation",
            data: [
              { label: "Tech", value: 58, color: "#3B82F6" },
              { label: "Finance", value: 15, color: "#10B981" },
              { label: "Other", value: 27, color: "#F59E0B" }
            ],
            showLegend: false,
            showPercentages: true
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "ExecutiveSummary",
          props: {
            title: "Summary",
            items: [
              { label: "Performance", text: "Portfolio outperformed by 6.8%", color: "green" },
              { label: "Risk", text: "Volatility within target range", color: "blue" }
            ],
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "BarChart",
          props: {
            title: "Sector Performance",
            data: [
              { label: "Tech", value: 16.2 },
              { label: "Finance", value: 8.7 },
              { label: "Consumer", value: 23.4 },
              { label: "Energy", value: 12.3 }
            ],
            format: "percentage",
            color: "blue",
            showValues: true
          },
          layout: { size: "half", height: "short" }
        },
        {
          component_name: "HeatmapTable",
          props: {
            title: "Correlation",
            data: [
              [1.00, 0.15, 0.28],
              [0.15, 1.00, 0.65],
              [0.28, 0.65, 1.00]
            ],
            rowLabels: ["Tech", "Finance", "Energy"],
            columnLabels: ["Tech", "Fin", "Eng"],
            cellConfig: {
              format: "number",
              decimals: 2,
              colorScheme: "correlation"
            },
          },
          layout: { size: "half", height: "short" }
        }
      ]
    }
  },

  // Configuration 2: Maximum Component Density
  maxDensity: {
    ui_config: {
      selected_components: [
        {
          component_name: "StatGroup",
          props: {
            title: "Performance",
            stats: [
              { label: "Return", value: 18.7, format: "percentage" },
              { label: "Risk", value: 8.2, format: "percentage" },
              { label: "Sharpe", value: 1.54, format: "number" }
            ],
            columns: 3
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "StatGroup", 
          props: {
            title: "Holdings",
            stats: [
              { label: "Top", value: "AAPL" },
              { label: "Count", value: 8, format: "number" },
              { label: "Concentration", value: 58, format: "percentage" }
            ],
            columns: 3
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "StatGroup",
          props: {
            title: "Risk",
            stats: [
              { label: "Beta", value: 1.23, format: "number" },
              { label: "Alpha", value: 3.2, format: "percentage" },
              { label: "Drawdown", value: 15.6, format: "percentage" }
            ],
            variant: "compact", 
            columns: 3
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "BarChart",
          props: {
            title: "Holdings",
            data: [
              { label: "AAPL", value: 25.0 },
              { label: "MSFT", value: 18.0 },
              { label: "GOOGL", value: 15.0 },
              { label: "TSLA", value: 12.0 }
            ],
            format: "percentage",
            color: "green",
            showValues: true
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "PieChart",
          props: {
            title: "Sectors",
            data: [
              { label: "Tech", value: 58, color: "#3B82F6" },
              { label: "Finance", value: 15, color: "#10B981" },
              { label: "Consumer", value: 12, color: "#F59E0B" },
              { label: "Other", value: 15, color: "#EF4444" }
            ],
            showLegend: false,
            showPercentages: true
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "LineChart",
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
            showDots: false,
            showArea: true
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "RankedList",
          props: {
            title: "Top Performers",
            items: [
              { id: "1", name: "Tesla", value: "23.4%", changeType: "positive" },
              { id: "2", name: "Apple", value: "15.6%", changeType: "positive" },
              { id: "3", name: "Microsoft", value: "14.2%", changeType: "positive" }
            ],
            maxItems: 3,
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "BulletList",
          props: {
            title: "Key Points",
            items: [
              "Tech sector drives performance",
              "Risk metrics within targets", 
              "Strong momentum continues"
            ],
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "CalloutList",
          props: {
            title: "Alerts",
            items: [
              { id: "1", title: "Concentration Risk", content: "High tech allocation", type: "warning" },
              { id: "2", title: "Strong Performance", content: "Above benchmark", type: "success" }
            ],
          },
          layout: { size: "third", height: "short" }
        }
      ]
    }
  },

  // Configuration 3: All Components Showcase 
  allComponentsShowcase: {
    ui_config: {
      selected_components: [
        {
          component_name: "RankingTable",
          props: {
            title: "Holdings Ranking",
            data: [
              { id: "AAPL", name: "Apple", score: 0.156, return: 0.156, weight: 0.25 },
              { id: "MSFT", name: "Microsoft", score: 0.142, return: 0.142, weight: 0.18 },
              { id: "TSLA", name: "Tesla", score: 0.234, return: 0.234, weight: 0.12 }
            ],
            columns: [
              { id: "score", name: "Score", align: "center", format: "percentage" },
              { id: "return", name: "Return", align: "center", format: "percentage" },
              { id: "weight", name: "Weight", align: "right", format: "percentage" }
            ],
            primaryColumn: "score",
          },
          layout: { size: "half", height: "short" }
        },
        {
          component_name: "ComparisonTable",
          props: {
            title: "Sector Comparison",
            entities: [
              { id: "tech", name: "Tech", shortName: "Tech" },
              { id: "finance", name: "Finance", shortName: "Fin" },
              { id: "consumer", name: "Consumer", shortName: "Con" }
            ],
            metrics: [
              { id: "weight", name: "Weight", format: "percentage" },
              { id: "return", name: "Return", format: "percentage" }
            ],
            data: {
              weight: { tech: 58, finance: 15, consumer: 12 },
              return: { tech: 16.2, finance: 8.7, consumer: 23.4 }
            },
            showChange: true,
          },
          layout: { size: "half", height: "short" }
        },
        {
          component_name: "ScatterChart",
          props: {
            title: "Risk vs Return",
            data: [
              { x: 8.1, y: 15.6, label: "AAPL" },
              { x: 7.2, y: 14.2, label: "MSFT" },
              { x: 15.8, y: 23.4, label: "TSLA" }
            ],
            xAxis: { label: "Risk", format: "percentage" },
            yAxis: { label: "Return", format: "percentage" },
            showTrendLine: false
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "HeatmapTable",
          props: {
            title: "Correlation Matrix",
            data: [
              [1.00, 0.15, 0.28],
              [0.15, 1.00, 0.65],
              [0.28, 0.65, 1.00]
            ],
            rowLabels: ["Tech", "Fin", "Con"],
            columnLabels: ["T", "F", "C"],
            cellConfig: {
              format: "number",
              decimals: 2,
              colorScheme: "correlation"
            },
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "SectionedInsightCard",
          props: {
            title: "Analysis",
            description: "Portfolio insights", 
            sections: [
              { 
                title: "Performance", 
                content: ["Strong 25% return", "Outperformed benchmark"],
                type: "highlight"
              },
              { 
                title: "Risk", 
                content: ["Controlled volatility", "Good Sharpe ratio"],
                type: "default"
              }
            ],
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "ExecutiveSummary",
          props: {
            title: "Key Findings",
            items: [
              { label: "Performance", text: "Portfolio outperformed by 6.8%", color: "green" },
              { label: "Risk", text: "Volatility within target range", color: "blue" },
              { label: "Outlook", text: "Positive momentum continues", color: "green" }
            ],
          },
          layout: { size: "half", height: "short" }
        },
        {
          component_name: "SummaryConclusion",
          props: {
            title: "Investment Summary",
            keyFindings: [
              "Portfolio outperformed benchmark significantly",
              "Technology concentration presents opportunity and risk",
              "Strong risk-adjusted returns with 1.54 Sharpe ratio"
            ],
            conclusion: "Portfolio shows excellent performance with controlled risk. Consider selective rebalancing.",
            nextSteps: [
              "Reduce tech allocation to 45%",
              "Add international exposure"
            ],
            confidence: "high",
          },
          layout: { size: "half", height: "short" }
        }
      ]
    }
  },

  // Configuration 4: Ultra Dense Grid
  ultraDense: {
    ui_config: {
      selected_components: [
        {
          component_name: "StatGroup",
          props: {
            title: "Quick Stats",
            stats: [
              { label: "Value", value: 1250000, format: "currency" },
              { label: "Return", value: 18.7, format: "percentage" }
            ],
            columns: 2
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "StatGroup",
          props: {
            title: "Risk Metrics", 
            stats: [
              { label: "Volatility", value: 8.2, format: "percentage" },
              { label: "Beta", value: 1.23, format: "number" }
            ],
            columns: 2
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "StatGroup",
          props: {
            title: "Performance",
            stats: [
              { label: "Sharpe", value: 1.54, format: "number" },
              { label: "Alpha", value: 3.2, format: "percentage" }
            ],
            columns: 2
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "BarChart",
          props: {
            title: "Top Holdings",
            data: [
              { label: "AAPL", value: 25 },
              { label: "MSFT", value: 18 },
              { label: "GOOGL", value: 15 }
            ],
            format: "percentage",
            color: "blue",
            showValues: false
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "PieChart",
          props: {
            title: "Allocation",
            data: [
              { label: "Stocks", value: 75, color: "#3B82F6" },
              { label: "Bonds", value: 20, color: "#10B981" },
              { label: "Cash", value: 5, color: "#F59E0B" }
            ],
            showLegend: false,
            showPercentages: false
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "LineChart",
          props: {
            title: "6M Performance",
            data: [
              { label: "Jan", value: 8 },
              { label: "Feb", value: 12 },
              { label: "Mar", value: 15 },
              { label: "Apr", value: 18 },
              { label: "May", value: 22 },
              { label: "Jun", value: 25 }
            ],
            format: "percentage",
            showDots: false,
            showArea: false
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "RankedList",
          props: {
            title: "Winners",
            items: [
              { id: "1", name: "Tesla", value: "+23.4%", changeType: "positive" },
              { id: "2", name: "Apple", value: "+15.6%", changeType: "positive" }
            ],
            maxItems: 2,
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "BulletList",
          props: {
            title: "Highlights",
            items: [
              "Strong performance vs benchmark",
              "Tech sector concentration high"
            ],
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "CalloutList",
          props: {
            title: "Alerts",
            items: [
              { id: "1", title: "Risk", content: "High tech allocation", type: "warning" }
            ],
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "ScatterChart", 
          props: {
            title: "Risk/Return",
            data: [
              { x: 8, y: 16, label: "AAPL" },
              { x: 7, y: 14, label: "MSFT" },
              { x: 16, y: 23, label: "TSLA" }
            ],
            xAxis: { label: "Risk", format: "percentage" },
            yAxis: { label: "Return", format: "percentage" },
            showTrendLine: false
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "HeatmapTable",
          props: {
            title: "Correlation",
            data: [
              [1.00, 0.15],
              [0.15, 1.00]
            ],
            rowLabels: ["Tech", "Finance"],
            columnLabels: ["T", "F"],
            cellConfig: {
              format: "number",
              decimals: 2,
              colorScheme: "correlation"
            },
          },
          layout: { size: "third", height: "short" }
        },
        {
          component_name: "ExecutiveSummary",
          props: {
            title: "Summary",
            items: [
              { label: "Performance", text: "Portfolio up 25% YTD", color: "green" },
              { label: "Risk", text: "Moderate volatility", color: "blue" }
            ],
          },
          layout: { size: "third", height: "short" }
        }
      ]
    }
  },

  // Configuration 5: Component Variety Showcase
  componentVariety: {
    ui_config: {
      selected_components: [
        {
          component_name: "RankingTable",
          props: {
            title: "Asset Rankings",
            data: [
              { id: "AAPL", name: "Apple", score: 0.92, return: 0.156, risk: 0.081 },
              { id: "MSFT", name: "Microsoft", score: 0.87, return: 0.142, risk: 0.072 },
              { id: "TSLA", name: "Tesla", score: 0.83, return: 0.234, risk: 0.158 }
            ],
            columns: [
              { id: "score", name: "Score", align: "center", format: "badge", colorScale: (value: number) => 
                value >= 0.8 ? 'text-green-700 bg-green-50' : 'text-yellow-600 bg-yellow-50'
              },
              { id: "return", name: "Return", align: "center", format: "percentage" },
              { id: "risk", name: "Risk", align: "center", format: "percentage" }
            ],
            primaryColumn: "score",
          },
          layout: { size: "half", height: "short" }
        },
        {
          component_name: "ComparisonTable", 
          props: {
            title: "Performance vs Benchmarks",
            entities: [
              { id: "portfolio", name: "Our Portfolio", shortName: "Portfolio" },
              { id: "sp500", name: "S&P 500", shortName: "S&P 500" },
              { id: "nasdaq", name: "NASDAQ", shortName: "NASDAQ" }
            ],
            metrics: [
              { id: "return", name: "6M Return", format: "percentage" },
              { id: "volatility", name: "Volatility", format: "percentage" }
            ],
            data: {
              return: { portfolio: 25.0, sp500: 18.2, nasdaq: 22.1 },
              volatility: { portfolio: 8.2, sp500: 9.1, nasdaq: 12.3 }
            },
            showChange: true,
            highlightBest: true,
          },
          layout: { size: "half", height: "short" }
        },
        {
          component_name: "SectionedInsightCard",
          props: {
            title: "Market Analysis",
            description: "Comprehensive analysis",
            sections: [
              { 
                title: "Performance Highlights", 
                content: [
                  "25% return outperforms all benchmarks",
                  "Lower volatility than NASDAQ",
                  "Sharpe ratio leads all comparisons"
                ],
                type: "highlight"
              },
              { 
                title: "Risk Assessment", 
                content: [
                  "Concentration risk in technology",
                  "Beta exposure manageable at 1.23",
                  "Correlation with markets moderate"
                ],
                type: "default"
              }
            ],
          },
          layout: { size: "half", height: "short" }
        },
        {
          component_name: "SummaryConclusion",
          props: {
            title: "Investment Recommendation",
            keyFindings: [
              "Portfolio exceeds all performance benchmarks with superior risk-adjusted returns",
              "Technology sector allocation drives outperformance but creates concentration risk", 
              "Strong momentum with controlled downside exposure"
            ],
            conclusion: "Portfolio demonstrates exceptional performance with measured risk profile. Strategic rebalancing recommended to maintain competitive edge while reducing sector concentration.",
            nextSteps: [
              "Reduce tech exposure to 45% from current 58%",
              "Diversify into international markets (10-15% allocation)",
              "Implement quarterly rebalancing schedule"
            ],
            confidence: "high",
          },
          layout: { size: "half", height: "short" }
        }
      ]
    }
  },
  drawdownAnalysis: {
    ui_config: {
      selected_components: [
        {
          component_name: "StatGroup",
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
          },
          layout: {
            size: "third",
            height: "medium"
          },
          reasoning: "Compact summary of key drawdown metrics for quick overview"
        },
        {
          component_name: "BarChart",
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
          },
          layout: {
            size: "half",
            height: "medium"
          },
          reasoning: "Visual representation of key metrics, red color emphasizes drawdown significance"
        },
        {
          component_name: "ExecutiveSummary",
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
          },
          layout: {
            size: "full",
            height: "short"
          },
          reasoning: "Contextual insights about the drawdown analysis and its implications"
        }
      ],
      layout_template: "balanced",
      priority: "viewport_optimized"
    }
  }
};