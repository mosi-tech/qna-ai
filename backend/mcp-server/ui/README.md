# React Components MCP Server

This MCP server provides tools for dynamically selecting and configuring React insight components for financial analysis UI generation.

## Overview

The server exposes metadata about all available React components in the frontend and provides AI-powered tools for:
- Component selection based on data structure and analysis type
- UI configuration generation with responsive layouts
- Props validation and optimization
- Layout templates and responsive design

## Available Tools

### 1. `list_available_components`
Lists all React components with filtering options.
- **Parameters**: `category` (optional), `data_type` (optional)
- **Returns**: Filtered list of components with metadata

### 2. `get_component_schema` 
Gets detailed props schema for a specific component.
- **Parameters**: `component_name` (required)
- **Returns**: Complete component metadata and props schema

### 3. `suggest_components_for_data`
AI-powered component suggestions based on data and analysis type.
- **Parameters**: `data_structure`, `analysis_type`, `question`, `max_components`
- **Returns**: Ranked component suggestions with scores and reasoning

### 4. `generate_ui_configuration`
Generates complete UI configuration with layout and data mapping.
- **Parameters**: `selected_components`, `data_mappings`, `layout_template`
- **Returns**: Full UI configuration JSON for frontend rendering

### 5. `validate_component_props`
Validates component props against schema.
- **Parameters**: `component_name`, `props`
- **Returns**: Validation results with errors, warnings, and suggestions

### 6. `get_layout_templates`
Returns available responsive layout templates.
- **Returns**: All layout template configurations

### 7. `optimize_layout`
Optimizes component layout for target audience.
- **Parameters**: `components`, `target_audience`
- **Returns**: Optimized layout suggestions

## Component Categories

### Charts
- **BarChart**: Categorical comparisons, rankings
- **PieChart**: Proportional data, distributions  
- **LineChart**: Time series, trends
- **ScatterChart**: Correlations, relationships

### Tables
- **RankingTable**: Performance rankings, leaderboards
- **ComparisonTable**: Side-by-side comparisons
- **HeatmapTable**: Matrix data, correlations

### Lists & Text
- **ExecutiveSummary**: Key findings, insights
- **BulletList**: Simple lists, highlights
- **RankedList**: Ordered lists with performance indicators
- **CalloutList**: Warnings, alerts, important notes

### Cards & Display  
- **StatGroup**: KPI display, summary metrics
- **SectionedInsightCard**: Multi-section detailed analysis

### Text Components
- **SummaryConclusion**: Comprehensive conclusions with recommendations

## Layout Templates

### Dashboard
Stats at top, main content in middle, summary at bottom.

### Analysis
Executive summary, main analysis, conclusion flow.

### Comparison
Side-by-side comparison focused layout.

### Ranking
Primary table with supporting visualizations.

## Usage Example

```python
# List components for charts
components = await mcp_client.call_tool("list_available_components", {
    "category": "charts"
})

# Get suggestions for ranking analysis
suggestions = await mcp_client.call_tool("suggest_components_for_data", {
    "data_structure": {"etf_rankings": [{"symbol": "QQQ", "improvement": 0.67}]},
    "analysis_type": "ranking", 
    "question": "Which ETFs had the largest Sharpe ratio improvement?"
})

# Generate UI configuration
ui_config = await mcp_client.call_tool("generate_ui_configuration", {
    "selected_components": [
        {"component_name": "RankingTable", "role": "primary"},
        {"component_name": "StatGroup", "role": "supporting"}
    ],
    "data_mappings": {
        "RankingTable": {
            "data": "{{analysis_data.etf_rankings}}",
            "title": "ETF Sharpe Ratio Improvements"
        }
    },
    "layout_template": "ranking"
})
```

## Running the Server

```bash
# Install dependencies
pip install -r requirements.txt

# Run the server
python react_components_server.py
```

The server runs as a stdio MCP server and can be integrated with any MCP client.

## Integration with Backend

This MCP server is designed to work with the financial analysis backend:

1. **Analysis Results** → **Component Selection** → **UI Configuration** → **Frontend Rendering**

2. Python analysis produces data → MCP tools select optimal components → Frontend receives JSON config → React renders dynamic UI

## Component Metadata Schema

Each component includes:
- **Props schema**: TypeScript interface for validation
- **Use cases**: When to use this component  
- **Data format**: Expected data structure
- **Layout hints**: Responsive sizing recommendations
- **Best data types**: Optimal data type matches

This enables intelligent component selection based on analysis results and user questions.