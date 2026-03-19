#!/usr/bin/env python3
"""
Mock Data Generator Agent

Generates mock data based on UI Planner output (data contracts).
Saves mock data to mock_data directory and registers with ChromaDB.

Input:
    {
        "question": "Show portfolio P&L",
        "ui_planner_output": {
            "dashboard_blocks": [...]
        }
    }

Output:
    {
        "mock_data_file": "mock_data/q001.json",
        "data_points": [...]
    }
"""

import json
import logging
import os
import hashlib
from typing import Dict, Any, List
from datetime import datetime

# Add parent directory to path for imports
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent_base import AgentBase, AgentResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_data_generator")


class MockDataGenerator(AgentBase):
    """Agent that generates mock data for testing UI Planner"""

    def __init__(
        self,
        prompt_file: str = None,
        llm_model: str = None,
        llm_provider: str = None
    ):
        super().__init__(
            name="mock_data_generator",
            task="MOCK_DATA_GENERATOR",
            prompt_file=prompt_file,
            llm_model=llm_model,
            llm_provider=llm_provider
        )

        # Mock data directory (relative to backend/headless/agents)
        self.mock_data_dir = os.path.join(os.path.dirname(__file__), "..", "..", "output", "mock_data")
        os.makedirs(self.mock_data_dir, exist_ok=True)

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "question": {"type": "string", "description": "User's question"},
                "ui_planner_output": {"type": "object", "description": "UI Planner output with dashboard blocks"},
                "question_id": {"type": "string", "description": "Question ID for filename"}
            },
            "required": ["question", "ui_planner_output"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "mock_data_file": {"type": "string"},
                "data_points": {"type": "array"}
            },
            "required": ["mock_data_file"]
        }

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Generate mock data based on UI Planner output"""
        question = input_data.get("question", "")
        ui_output = input_data.get("ui_planner_output", {})
        question_id = input_data.get("question_id", self._generate_question_id(question))

        if not ui_output:
            return AgentResult(success=False, error="ui_planner_output is required")

        try:
            # Extract data contracts from UI Planner output
            data_contracts = self._extract_data_contracts(ui_output)

            # Generate mock data for each data point
            mock_data = self._generate_mock_data(data_contracts, question)

            # Save mock data to file
            mock_file_path = self._save_mock_data(mock_data, question_id, question)

            # Register with ChromaDB (via mock_reuse_evaluator)
            self._register_with_chroma(question, mock_file_path, question_id)

            self.logger.info(f"✅ Generated mock data: {mock_file_path}")

            return AgentResult(success=True, data={
                "mock_data_file": mock_file_path,
                "data_points": list(mock_data.keys())
            })

        except Exception as e:
            self.logger.error(f"❌ Failed to generate mock data: {e}")
            return AgentResult(success=False, error=str(e))

    def _generate_question_id(self, question: str) -> str:
        """Generate a safe question ID from question text"""
        safe = question.replace(" ", "_").replace("/", "_").replace("?", "").replace(":", "")
        safe = "".join(c for c in safe if c.isalnum() or c in "._-")
        return safe.lower()[:40]

    def _extract_data_contracts(self, ui_output: Dict) -> List[Dict[str, Any]]:
        """Extract data contracts from UI Planner output"""
        contracts = []

        blocks = ui_output.get("blocks", [])

        for block in blocks:
            # Extract dataContract from each block
            data_contract = block.get("dataContract", {})
            if data_contract:
                contracts.append({
                    "name": block.get("blockId", ""),
                    "type": data_contract.get("type", "string"),
                    "description": data_contract.get("description", ""),
                    "points": data_contract.get("points", 1),
                    "block_id": block.get("blockId", ""),
                    "sub_question": block.get("sub_question", ""),
                    "canonical_params": block.get("canonical_params", {})
                })

        return contracts

    def _generate_mock_data(self, contracts: List[Dict], question: str) -> Dict[str, Any]:
        """Generate mock data for each data contract"""
        mock_data = {
            "question": question,
            "generated_at": datetime.now().isoformat(),
            "data": {},
            "blocks": []
        }

        for idx, contract in enumerate(contracts):
            block_id = contract.get("block_id", f"block_{idx}")
            data_type = contract.get("type", "string")
            sub_question = contract.get("sub_question", "")

            # Generate mock data for this block
            block_data = {
                "block_id": block_id,
                "type": data_type,
                "sub_question": sub_question,
                "canonical_params": contract.get("canonical_params", {}),
                "data": self._generate_block_data(contract)
            }

            mock_data["blocks"].append(block_data)

        return mock_data

    def _generate_block_data(self, contract: Dict) -> Any:
        """Generate mock data for a specific block based on its type"""
        import random
        from datetime import datetime, timedelta

        data_type = contract.get("type", "string")
        block_id = contract.get("block_id", "")
        sub_question = contract.get("sub_question", "")

        # Determine component type from block_id and data_type
        component_type = None
        if "kpi-card" in block_id:
            component_type = "kpi"
        elif "line-chart" in block_id:
            component_type = "line"
        elif "bar-chart" in block_id:
            component_type = "bar"
        elif "bar-list" in block_id or "barlist" in data_type.lower() or data_type.lower() == "barlist":
            component_type = "barlist"
        elif "donut-chart" in block_id or "donut" in data_type.lower() or data_type.lower() == "donut":
            component_type = "donut"
        elif "spark-chart" in block_id or "spark" in data_type.lower() or data_type.lower() == "spark":
            component_type = "spark"
        elif "table" in block_id or data_type.lower() == "table" or "table" in data_type.lower():
            component_type = "table"
        elif "tracker" in block_id:
            component_type = "tracker"

        if component_type == "kpi" or data_type == "kpi":
            # KPI card: return metrics array matching frontend KPI card format
            num_metrics = random.randint(2, 4)
            metric_names = [
                "Portfolio Value", "Daily P&L", "YTD Return", "Sharpe Ratio",
                "Holdings", "Avg Cost", "Market Value", "Unrealized Gain",
                "Sector Exposure", "Beta", "Alpha", "Max Drawdown"
            ][:num_metrics]

            return {
                "metrics": [
                    {
                        "name": name,
                        "stat": round(random.uniform(1000, 100000), 2),
                        "change": f"{random.uniform(-20, 30):.2f}%",
                        "changeType": "positive" if random.random() > 0.4 else "negative"
                    }
                    for name in metric_names
                ],
                "cols": num_metrics
            }

        elif component_type == "line" or data_type == "timeseries" or "trend" in sub_question.lower() or "performance" in sub_question.lower() or "history" in sub_question.lower():
            # Line chart: return time series data matching frontend format
            # Use intelligent default for time series: 12 months for YTD performance
            num_points = contract.get("points", 12) if contract.get("points", 12) > 1 else 12
            categories = ["Value", "Benchmark"] if "comparison" in sub_question.lower() or "benchmark" in sub_question.lower() else ["Value"]

            dates = [(datetime.now() - timedelta(days=30*i)).strftime("%Y-%m-%d") for i in reversed(range(num_points))]

            # Generate data for each category
            data = []
            for cat in categories:
                base_value = random.uniform(50000, 100000)
                values = [round(base_value + random.uniform(-10000, 15000), 2) for _ in range(num_points)]
                for i, date in enumerate(dates):
                    row = {"date": date}
                    row[cat] = values[i]
                    data.append(row)

            return {
                "data": data,
                "categories": categories,
                "summary": [
                    {
                        "name": cat,
                        "value": round(random.uniform(50000, 100000), 2)
                    }
                    for cat in categories
                ]
            }

        elif component_type == "bar" or data_type == "bar":
            # Bar chart: return categorical or timeseries data
            num_points = contract.get("points", 6) if contract.get("points", 6) > 1 else 6
            categories = ["Value"]

            # Check if it should be timeseries (with dates) or categorical (with names)
            if "trend" in sub_question.lower() or "history" in sub_question.lower() or "over time" in sub_question.lower():
                dates = [(datetime.now() - timedelta(days=30*i)).strftime("%Y-%m-%d") for i in reversed(range(num_points))]
                return {
                    "data": [
                        {
                            "date": date,
                            **{cat: round(random.uniform(10000, 100000), 2) for cat in categories}
                        }
                        for date in dates
                    ],
                    "categories": categories
                }
            else:
                return {
                    "data": [
                        {
                            "name": f"Item {i+1}",
                            **{cat: round(random.uniform(1000, 50000), 2) for cat in categories}
                        }
                        for i in range(num_points)
                    ],
                    "categories": categories
                }

        elif component_type == "table" or "table" in data_type.lower():
            # Table: return rows and columns (check before barlist for "holdings" questions)
            # For tables, use sensible default of 5-10 rows even if points=1
            num_rows = contract.get("points", 5) if contract.get("points", 5) > 1 else random.randint(5, 10)
            columns = ["Symbol", "Shares", "Avg Cost", "Market Value", "P&L", "P&L %"]

            return {
                "rows": [
                    {
                        "Symbol": f"STK{i+1}",
                        "Shares": random.randint(10, 1000),
                        "Avg Cost": round(random.uniform(10, 500), 2),
                        "Market Value": round(random.uniform(1000, 100000), 2),
                        "P&L": round(random.uniform(-5000, 20000), 2),
                        "P&L %": round(random.uniform(-30, 50), 2)
                    }
                    for i in range(num_rows)
                ],
                "columns": columns
            }

        elif component_type == "barlist" or data_type == "list" or "list" in sub_question.lower():
            # Bar list: return ranked list data
            num_items = contract.get("points", 5) if contract.get("points", 5) > 1 else 5
            return {
                "data": [
                    {
                        "name": f"Holding {chr(65+i)}",
                        "value": round(random.uniform(1000, 50000), 2)
                    }
                    for i in range(num_items)
                ]
            }

        elif component_type == "donut" or "allocation" in sub_question.lower() or "donut" in sub_question.lower():
            # Donut chart: return categorical data
            # For allocation/sector charts, use sensible default of 5-6 items even if points=1
            sectors = ["Technology", "Healthcare", "Finance", "Energy", "Consumer", "Industrial"]
            points = contract.get("points", 5) if contract.get("points", 5) > 1 else 5
            num_points = min(points, len(sectors))
            selected_sectors = random.sample(sectors, num_points)

            return {
                "data": [
                    {
                        "name": sector,
                        "value": round(random.uniform(10, 30), 2)
                    }
                    for sector in selected_sectors
                ]
            }

        elif component_type == "spark" or "spark" in sub_question.lower() or "watchlist" in sub_question.lower():
            # Spark chart: return spark data
            tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "TSLA", "META", "JPM"]
            num_items = min(contract.get("points", 5), len(tickers))
            selected_tickers = random.sample(tickers, num_items)
            num_points = contract.get("points", 14)

            dates = [(datetime.now() - timedelta(days=1*i)).strftime("%Y-%m-%d") for i in reversed(range(num_points))]

            return {
                "data": [
                    {
                        "date": date,
                        **{ticker: round(random.uniform(100, 200), 2) for ticker in selected_tickers}
                    }
                    for date in dates
                ],
                "items": [{"name": ticker} for ticker in selected_tickers]
            }

        elif component_type == "tracker" or "tracker" in sub_question.lower() or "monitoring" in sub_question.lower():
            # Status tracker: return status data
            num_points = contract.get("points", 30)
            statuses = ["ok", "ok", "ok", "ok", "warning", "error"]  # Weighted towards ok

            return {
                "data": [
                    {"status": random.choice(statuses)}
                    for _ in range(num_points)
                ]
            }

        else:
            # Default: simple KPI metrics
            return {
                "metrics": [
                    {
                        "name": "Metric",
                        "stat": round(random.uniform(1000, 100000), 2),
                        "change": f"{random.uniform(-10, 20):.2f}%",
                        "changeType": "positive" if random.random() > 0.4 else "negative"
                    }
                ],
                "cols": 1
            }

    def _mock_value_by_type(self, data_type: str, name: str) -> Any:
        """Generate mock value based on data type"""
        type_lower = data_type.lower()

        if "number" in type_lower or "price" in type_lower or "pnl" in type_lower or "value" in type_lower:
            # Numeric values
            import random
            return round(random.uniform(-1000, 100000), 2)

        elif "percentage" in type_lower or "%" in type_lower:
            import random
            return round(random.uniform(-20, 50), 2)

        elif "date" in type_lower or "time" in type_lower:
            from datetime import datetime, timedelta
            days_ago = hash(name) % 365
            return (datetime.now() - timedelta(days=days_ago)).strftime("%Y-%m-%d")

        elif "array" in type_lower or "list" in type_lower or type_lower.endswith("s"):
            # Array/list values
            import random
            return [
                {"name": f"Item {i}", "value": round(random.uniform(100, 10000), 2)}
                for i in range(5)
            ]

        else:
            # String values
            import random
            mock_strings = [
                f"Mock {name}",
                f"Sample data for {name}",
                f"Test value: {hash(name) % 1000}",
                f"Example {name} data"
            ]
            return random.choice(mock_strings)

    def _save_mock_data(self, mock_data: Dict, question_id: str, question: str) -> str:
        """Save mock data to file"""
        filename = f"{question_id}.json"
        filepath = os.path.join(self.mock_data_dir, filename)

        with open(filepath, 'w') as f:
            json.dump(mock_data, f, indent=2)

        return filepath

    def _register_with_chroma(self, question: str, mock_file: str, question_id: str):
        """Register the mock data reference in ChromaDB"""
        try:
            from mock_reuse_evaluator import create_mock_reuse_evaluator

            evaluator = create_mock_reuse_evaluator()
            evaluator.save_mock_data_reference(
                question=question,
                mock_data_file=mock_file,
                analysis_id=question_id
            )
        except Exception as e:
            self.logger.warning(f"⚠️ Could not register with ChromaDB: {e}")


# Factory function
def create_mock_data_generator(**kwargs) -> MockDataGenerator:
    """Create Mock Data Generator agent with optional overrides"""
    return MockDataGenerator(**kwargs)


# For direct execution
if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        question = sys.argv[1]
        generator = create_mock_data_generator()

        # Mock UI Planner output
        mock_ui_output = {
            "dashboard_blocks": [
                {
                    "id": "block_1",
                    "type": "summary_card",
                    "data_points": [
                        {"name": "total_pnl", "type": "number", "description": "Total profit/loss"},
                        {"name": "return_pct", "type": "percentage", "description": "Return percentage"},
                        {"name": "positions", "type": "array", "description": "List of positions"}
                    ]
                }
            ]
        }

        result = generator.execute({
            "question": question,
            "ui_planner_output": mock_ui_output
        })
        print(json.dumps(result.to_dict(), indent=2))
    else:
        print("Usage: python mock_data_generator.py \"Your question here\"")