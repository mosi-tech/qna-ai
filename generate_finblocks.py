#!/usr/bin/env python3
"""Generate React TypeScript components for all finBlocks from FINBLOCK_CATALOG.json"""

import json
import os
from pathlib import Path
from datetime import datetime

# Load catalog
catalog_path = "/Users/shivc/Documents/Workspace/JS/qna-ai-admin/frontend/apps/base-ui/src/finBlocks/FINBLOCK_CATALOG.json"
with open(catalog_path) as f:
    catalog = json.load(f)

base_path = Path("/Users/shivc/Documents/Workspace/JS/qna-ai-admin/frontend/apps/base-ui/src/finBlocks/components")

def get_sample_data_for_block(block_id, block_type):
    """Generate sample data based on block type"""
    samples = {
        "kpi-card": {
            "metrics": [
                {"name": "Total Value", "stat": 125000, "change": "+5.2%", "changeType": "positive"},
                {"name": "P&L YTD", "stat": 6250, "change": "+12.5%", "changeType": "positive"},
                {"name": "Sharpe Ratio", "stat": 1.8, "change": "+0.2", "changeType": "positive"},
            ],
            "cols": 3
        },
        "table": {
            "rows": [
                {"Symbol": "AAPL", "Shares": 100, "AvgCost": 150, "MarketValue": 17000, "PL": 2000, "PL%": 13.3},
                {"Symbol": "MSFT", "Shares": 50, "AvgCost": 300, "MarketValue": 16000, "PL": 1000, "PL%": 6.7},
            ],
            "columns": ["Symbol", "Shares", "Avg Cost", "Market Value", "P&L", "P&L %"]
        },
        "donut-chart": {
            "data": [
                {"name": "Technology", "value": 35},
                {"name": "Healthcare", "value": 20},
                {"name": "Finance", "value": 25},
                {"name": "Other", "value": 20},
            ]
        },
        "line-chart": {
            "data": [
                {"date": "2024-01-01", "Portfolio": 100, "Benchmark": 100},
                {"date": "2024-02-01", "Portfolio": 105, "Benchmark": 102},
                {"date": "2024-03-01", "Portfolio": 110, "Benchmark": 104},
            ],
            "categories": ["Portfolio", "Benchmark"],
            "summary": [{"name": "YTD Return", "value": 10}]
        },
        "bar-chart": {
            "data": [
                {"name": "Jan", "value": 2.5},
                {"name": "Feb", "value": 1.8},
                {"name": "Mar", "value": 3.2},
            ],
            "categories": ["value"]
        },
        "bar-list": {
            "data": [
                {"name": "AAPL", "value": 15.5},
                {"name": "MSFT", "value": 12.3},
                {"name": "GOOGL", "value": 10.8},
            ]
        },
        "spark-chart": {
            "data": [
                {"date": "2024-03-01", "AAPL": 150, "MSFT": 300},
                {"date": "2024-03-02", "AAPL": 152, "MSFT": 302},
            ],
            "items": [
                {"id": "AAPL", "name": "Apple", "value": "152.50", "change": "+1.7%", "changeType": "positive"},
            ]
        },
        "heatmap": {
            "data": [[1.0, 0.6, 0.4], [0.6, 1.0, 0.5], [0.4, 0.5, 1.0]],
            "labels": ["AAPL", "MSFT", "GOOGL"]
        }
    }
    return samples.get(block_type, {})

def generate_component(category, block):
    """Generate a React component for a finBlock"""
    block_id = block["id"]
    name = block["name"]
    description = block["description"]
    block_type = block["blockType"]

    # Create sample data
    sample_data = get_sample_data_for_block(block_id, block_type)

    # Convert kebab-case to PascalCase for component name
    component_name = ''.join(word.capitalize() for word in block_id.split('-'))

    # Generate TypeScript interface
    interface_code = f"""interface {component_name}Props {{
  title?: string;
  data: any;
  loading?: boolean;
  error?: string;
}}
"""

    component_code = f'''import React from 'react';

// Data interface for {name}
{interface_code}

// Sample data for development
export const SAMPLE_DATA: {component_name}Props = {{
  title: '{name}',
  data: {json.dumps(sample_data, indent=4)},
  loading: false,
  error: undefined,
}};

/**
 * {name} finBlock
 *
 * @description {description}
 * @blockType {block_type}
 * @concepts {', '.join(block['financialConcepts'])}
 * @mcpRequired {', '.join(block['mcpRequired'])}
 */
export const {component_name}: React.FC<{component_name}Props> = ({{
  title = '{name}',
  data,
  loading = false,
  error,
}}) => {{
  if (loading) {{
    return <div className="p-4">Loading...</div>;
  }}

  if (error) {{
    return <div className="p-4 text-red-500">Error: {{error}}</div>;
  }}

  return (
    <div className="finblock {block_id} rounded-lg border border-gray-200 bg-white p-4 shadow-sm">
      <h3 className="mb-3 font-semibold text-gray-800">{{title}}</h3>
      {{/* Block Type: {block_type} */}}
      <pre className="max-h-96 overflow-auto rounded bg-gray-50 p-3 text-xs">
        {{JSON.stringify(data, null, 2)}}
      </pre>
    </div>
  );
}};

export default {component_name};
'''

    return component_code

def generate_category_index(category, blocks):
    """Generate index.ts for a category"""
    exports = []
    for block in blocks:
        block_id = block["id"]
        component_name = ''.join(word.capitalize() for word in block_id.split('-'))
        exports.append(f"export {{ default as {component_name}, SAMPLE_DATA as {component_name}SampleData }} from './{block_id}';")

    index_content = "// Auto-generated finBlocks index\n\n" + "\n".join(exports) + "\n"
    return index_content

# Generate all components
total_blocks = 0
for category, category_data in catalog["categories"].items():
    blocks = category_data["blocks"]
    category_path = base_path / category
    category_path.mkdir(parents=True, exist_ok=True)

    print(f"\nGenerating {category} category ({len(blocks)} blocks)...")

    for block in blocks:
        block_id = block["id"]
        component_file = category_path / f"{block_id}.tsx"

        component_code = generate_component(category, block)

        with open(component_file, 'w') as f:
            f.write(component_code)

        print(f"  ✓ {block_id}")
        total_blocks += 1

    # Generate index.ts for category
    index_file = category_path / "index.ts"
    index_content = generate_category_index(category, blocks)

    with open(index_file, 'w') as f:
        f.write(index_content)

    print(f"✓ Generated index.ts for {category}")

# Generate root index.ts
root_index_exports = []
for category in catalog["categories"].keys():
    root_index_exports.append(f"export * from './{category}';")

root_index_content = "// Auto-generated finBlocks root index\n\n" + "\n".join(root_index_exports) + "\n"
root_index_file = base_path / "index.ts"

with open(root_index_file, 'w') as f:
    f.write(root_index_content)

print(f"\n✓ Generated root index.ts")
print(f"\n=== Summary ===")
print(f"Total finBlocks generated: {total_blocks}")
print(f"Categories: {len(catalog['categories'])}")
print(f"Output directory: {base_path}")
