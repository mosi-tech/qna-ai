#!/usr/bin/env python3
"""
Mock Data Generator V2

Generates realistic mock financial data for atomic sub-questions.
Unlike v1 which tries to answer a question in one shot,
v2 takes a batch of sub-questions and generates data for each independently.

Input:
    {
        "original_question": "Show me my equity portfolio with holdings and daily P&L",
        "decomposition": [
            {
                "sub_question": "What are my current stock holdings?",
                "block_type": "table",
                "title": "Portfolio Holdings",
                "canonical_params": {"metric": "holdings"}
            },
            ...
        ]
    }

Output:
    {
        "blocks": [
            {
                "blockId": "table-01",
                "title": "Portfolio Holdings",
                "data": {...}
            },
            ...
        ],
        "blocks_data": [
            {
                "block_id": "table-01",
                "data": {...}
            },
            ...
        ]
    }
"""

import json
import logging
import os
import sys
import hashlib
from typing import Dict, Any, List
from datetime import datetime, timedelta
import random

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/..")
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../..")

from agent_base import AgentBase, AgentResult

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mock_v2_generator")


class MockV2Generator(AgentBase):
    """Generates mock data for atomic sub-questions in batch mode"""

    def __init__(
        self,
        prompt_file: str = None,
        llm_model: str = None,
        llm_provider: str = None
    ):
        super().__init__(
            name="mock_v2_generator",
            task="MOCK_V2_GENERATOR",
            prompt_file=prompt_file,
            llm_model=llm_model,
            llm_provider=llm_provider
        )
        logger.info("✅ Mock V2 Generator initialized")

    def get_input_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "original_question": {"type": "string"},
                "decomposition": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "sub_question": {"type": "string"},
                            "block_type": {"type": "string"},
                            "title": {"type": "string"},
                            "canonical_params": {"type": "object"}
                        }
                    }
                }
            },
            "required": ["original_question", "decomposition"]
        }

    def get_output_schema(self) -> Dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "blocks": {"type": "array"},
                "blocks_data": {"type": "array"}
            },
            "required": ["blocks", "blocks_data"]
        }

    def process(self, input_data: Dict[str, Any]) -> AgentResult:
        """Generate mock data for batch of sub-questions"""
        original_question = input_data.get("original_question", "")
        decomposition = input_data.get("decomposition", [])

        if not decomposition:
            self.logger.warning("No sub-questions in decomposition")
            return AgentResult(success=True, data={"blocks": [], "blocks_data": []})

        try:
            blocks = []
            blocks_data = []

            for idx, sub_q in enumerate(decomposition):
                block_type = sub_q.get("block_type", "kpi-card")
                title = sub_q.get("title", f"Block {idx + 1}")
                sub_question = sub_q.get("sub_question", "")
                params = sub_q.get("canonical_params", {})

                # Generate blockId from block_type and index (keep hyphens for registry matching)
                block_id = f"{block_type}-{idx + 1:02d}"

                # Generate mock data based on block type
                mock_data = self._generate_mock_data(
                    block_type=block_type,
                    sub_question=sub_question,
                    title=title,
                    params=params
                )

                # Add to blocks list (for UI schema)
                blocks.append({
                    "blockId": block_id,
                    "category": self._get_category(block_type),
                    "title": title,
                    "dataContract": {
                        "type": self._get_contract_type(block_type),
                        "description": sub_question
                    },
                    "sub_question": sub_question,
                    "canonical_params": params
                })

                # Add to blocks_data list (for data payload)
                blocks_data.append({
                    "blockId": block_id,
                    "data": mock_data
                })

                self.logger.info(f"✅ Generated mock data for: {title}")

            return AgentResult(success=True, data={
                "blocks": blocks,
                "blocks_data": blocks_data
            })

        except Exception as e:
            self.logger.error(f"❌ Failed to generate mock data: {e}")
            return AgentResult(success=False, error=str(e))

    def _generate_mock_data(
        self,
        block_type: str,
        sub_question: str,
        title: str,
        params: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate mock data based on block type"""

        if block_type == "kpi-card":
            return self._mock_kpi_card(title, params)
        elif block_type == "line-chart":
            return self._mock_line_chart(title, params)
        elif block_type == "bar-chart":
            return self._mock_bar_chart(title, params)
        elif block_type == "bar-list":
            return self._mock_bar_list(title, params)
        elif block_type == "donut-chart":
            return self._mock_donut_chart(title, params)
        elif block_type == "table":
            return self._mock_table(title, params)
        elif block_type == "spark-chart":
            return self._mock_spark_chart(title, params)
        else:
            return self._mock_kpi_card(title, params)

    def _mock_kpi_card(self, title: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """KPI Card: Single metric"""
        metric = params.get("metric", "value")

        if "price" in metric.lower() or "price" in title.lower():
            return {
                "metrics": [
                    {
                        "label": title,
                        "value": f"${random.uniform(50, 500):.2f}",
                        "change": f"{random.uniform(-10, 10):.1f}%",
                        "changeType": "positive" if random.random() > 0.5 else "negative"
                    }
                ]
            }
        elif "return" in metric.lower() or "p&l" in metric.lower():
            return {
                "metrics": [
                    {
                        "label": title,
                        "value": f"{random.uniform(-20, 50):.1f}%",
                        "change": f"{random.uniform(-5, 5):.1f}%",
                        "changeType": "positive" if random.random() > 0.5 else "negative"
                    }
                ]
            }
        else:
            return {
                "metrics": [
                    {
                        "label": title,
                        "value": f"{random.uniform(0, 100):.2f}",
                        "change": f"{random.uniform(-10, 10):.1f}%",
                        "changeType": "positive" if random.random() > 0.5 else "negative"
                    }
                ]
            }

    def _mock_line_chart(self, title: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Line Chart: Time-series data"""
        period = params.get("period", "30d")
        days = self._period_to_days(period)

        data = []
        start_date = datetime.now() - timedelta(days=days)
        value = random.uniform(100, 500)

        for i in range(days):
            date = start_date + timedelta(days=i)
            value += random.uniform(-10, 10)  # Random walk
            data.append({
                "date": date.strftime("%Y-%m-%d"),
                "value": max(10, value)
            })

        return {
            "data": data,
            "categories": ["value"],
            "summary": [{"name": "value", "value": data[-1]["value"]}]
        }

    def _mock_bar_chart(self, title: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Bar Chart: Comparisons"""
        data = []
        categories = ["A", "B", "C", "D"]

        for cat in categories:
            data.append({
                "name": cat,
                "value": random.uniform(10, 100),
                "date": datetime.now().strftime("%Y-%m-%d")
            })

        return {
            "data": data,
            "categories": ["value"],
            "summary": [{"name": "value", "value": sum(d["value"] for d in data)}]
        }

    def _mock_bar_list(self, title: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Bar List: Ranked items"""
        items = ["Item A", "Item B", "Item C", "Item D", "Item E"]
        data = []

        for item in items:
            data.append({
                "name": item,
                "value": random.uniform(5, 50)
            })

        # Sort by value descending
        data.sort(key=lambda x: x["value"], reverse=True)

        return {"data": data}

    def _mock_donut_chart(self, title: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Donut Chart: Composition/Allocation"""
        categories = ["Sector A", "Sector B", "Sector C", "Sector D"]
        total = 100

        data = []
        for cat in categories:
            data.append({
                "name": cat,
                "value": random.uniform(15, 35)
            })

        # Normalize to 100%
        total_val = sum(d["value"] for d in data)
        for d in data:
            d["value"] = (d["value"] / total_val) * 100

        return {"data": data}

    def _mock_table(self, title: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Table: Detailed data rows"""
        # Generate realistic holdings table
        rows = []
        symbols = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA"]

        for symbol in symbols:
            rows.append({
                "symbol": symbol,
                "shares": random.randint(10, 100),
                "price": random.uniform(100, 500),
                "value": random.uniform(1000, 50000),
                "P&L": random.uniform(-500, 5000),
                "P&L %": random.uniform(-5, 15)
            })

        return {
            "rows": rows,
            "columns": ["symbol", "shares", "price", "value", "P&L", "P&L %"]
        }

    def _mock_spark_chart(self, title: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Spark Chart: Mini time-series"""
        period = params.get("period", "30d")
        days = self._period_to_days(period)

        data = []
        value = random.uniform(50, 150)

        for i in range(days):
            value += random.uniform(-5, 5)
            data.append({
                "date": (datetime.now() - timedelta(days=days - i)).strftime("%Y-%m-%d"),
                "value": max(10, value)
            })

        return {
            "data": data,
            "items": [{"name": title, "value": data[-1]["value"]}],
            "dataIndex": "date"
        }

    def _get_category(self, block_type: str) -> str:
        """Map block_type to category"""
        mapping = {
            "kpi-card": "kpi-cards",
            "line-chart": "line-charts",
            "bar-chart": "bar-charts",
            "bar-list": "bar-lists",
            "donut-chart": "donut-charts",
            "table": "tables",
            "spark-chart": "spark-charts"
        }
        return mapping.get(block_type, "kpi-cards")

    def _get_contract_type(self, block_type: str) -> str:
        """Map block_type to data contract type"""
        mapping = {
            "kpi-card": "kpi",
            "line-chart": "timeseries",
            "bar-chart": "bar",
            "bar-list": "barlist",
            "donut-chart": "donut",
            "table": "table",
            "spark-chart": "spark"
        }
        return mapping.get(block_type, "kpi")

    def _period_to_days(self, period: str) -> int:
        """Convert period string to number of days"""
        mapping = {
            "1d": 1,
            "7d": 7,
            "30d": 30,
            "1m": 30,
            "3m": 90,
            "6m": 180,
            "1y": 365,
            "ytd": 80  # Approximate
        }
        return mapping.get(period, 30)


def create_mock_v2_generator(**kwargs) -> MockV2Generator:
    """Factory function"""
    return MockV2Generator(**kwargs)


if __name__ == "__main__":
    # Test the generator
    test_input = {
        "original_question": "Show me my equity portfolio with holdings and daily P&L",
        "decomposition": [
            {
                "sub_question": "What are my current stock holdings?",
                "block_type": "table",
                "title": "Portfolio Holdings",
                "canonical_params": {"metric": "holdings"}
            },
            {
                "sub_question": "What is my portfolio value?",
                "block_type": "kpi-card",
                "title": "Total Portfolio Value",
                "canonical_params": {"metric": "portfolio_value"}
            },
            {
                "sub_question": "What is my daily portfolio return?",
                "block_type": "kpi-card",
                "title": "Daily P&L",
                "canonical_params": {"metric": "return"}
            }
        ]
    }

    generator = create_mock_v2_generator()
    result = generator.execute(test_input)
    print(json.dumps(result.to_dict(), indent=2))
