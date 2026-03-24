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
                    "points": data_contract.get("points", 12),
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
        """Generate mock data shaped for finkit-ui components.

        Dispatches on the FK* blockId emitted by the updated UI Planner.
        Data shapes match each finkit component's expected props exactly.
        """
        import random
        from datetime import datetime, timedelta

        block_id = contract.get("block_id", "")
        sub_question = contract.get("sub_question", "")
        n = max(contract.get("points", 12), 2)

        # ── helpers ──────────────────────────────────────────────────────────
        def dates_monthly(count):
            return [(datetime.now() - timedelta(days=30*i)).strftime("%Y-%m-%d")
                    for i in reversed(range(count))]

        def dates_daily(count):
            return [(datetime.now() - timedelta(days=i)).strftime("%Y-%m-%d")
                    for i in reversed(range(count))]

        def walk(start, volatility=0.02, count=12):
            v, out = start, []
            for _ in range(count):
                v = round(v * (1 + random.gauss(0.002, volatility)), 2)
                out.append(v)
            return out

        def label_items(count, prefix="Item"):
            return [f"{prefix} {chr(65+i)}" for i in range(min(count, 26))]

        # ── dispatch on FK block id ───────────────────────────────────────────

        # FKMetricGrid ─────────────────────────────────────────────────────────
        if block_id == "FKMetricGrid":
            cols = min(max(n, 2), 4)
            names = ["Portfolio Value", "Daily P&L", "YTD Return", "Sharpe Ratio",
                     "Beta", "Alpha", "Max Drawdown", "Volatility"][:cols]
            return {
                "cards": [
                    {
                        "label": name,
                        "value": f"${random.uniform(1000, 200000):,.0f}" if "Value" in name or "P&L" in name
                                 else f"{random.uniform(-30, 50):.2f}%",
                        "delta": round(random.uniform(-15, 25), 2),
                        "sub": random.choice(["vs yesterday", "YTD", "vs benchmark", "annualised"])
                    }
                    for name in names
                ],
                "cols": cols
            }

        # FKLineChart / FKAreaChart / FKBandChart / FKAnnotatedChart ──────────
        elif block_id in ("FKLineChart", "FKAreaChart", "FKBandChart"):
            has_bench = "benchmark" in sub_question.lower() or "comparison" in sub_question.lower()
            series_keys = ["portfolio", "benchmark"] if has_bench else ["value"]
            series = [{"key": k, "label": k.title()} for k in series_keys]
            starts = {k: random.uniform(80, 120) for k in series_keys}
            ds = dates_monthly(n)
            data = []
            vals = {k: starts[k] for k in series_keys}
            for d in ds:
                row = {"date": d}
                for k in series_keys:
                    vals[k] = round(vals[k] * (1 + random.gauss(0.003, 0.018)), 2)
                    row[k] = vals[k]
                data.append(row)
            out = {"data": data, "series": series}
            if block_id == "FKAreaChart":
                out["fillMode"] = "below" if "drawdown" in sub_question.lower() else "above"
            if block_id == "FKBandChart":
                out["baseline"] = 0
            return out

        elif block_id == "FKAnnotatedChart":
            series = [
                {"key": "price",  "label": "Price",  "color": "#6366f1"},
                {"key": "sma50",  "label": "SMA 50", "color": "#f59e0b", "strokeDash": "4 2"},
            ]
            ds = dates_daily(n * 5)
            price, sma = 100.0, 100.0
            data = []
            for d in ds:
                price = round(price * (1 + random.gauss(0.0005, 0.015)), 2)
                sma   = round(sma * 0.98 + price * 0.02, 2)
                data.append({"date": d, "price": price, "sma50": sma})
            mid = len(data) // 2
            return {
                "data": data,
                "series": series,
                "events": [
                    {"date": data[mid]["date"],      "type": "buy",  "label": "Signal Buy"},
                    {"date": data[mid + 10]["date"], "type": "sell", "label": "Signal Sell"},
                ],
                "bands":    [{"from": data[5]["date"], "to": data[15]["date"],
                               "color": "rgba(220,38,38,0.08)", "label": "Bear regime"}],
                "callouts": [{"date": data[mid - 5]["date"], "label": "Key event"}],
            }

        # FKBarChart ───────────────────────────────────────────────────────────
        elif block_id == "FKBarChart":
            is_time = ("month" in sub_question.lower() or "annual" in sub_question.lower()
                       or "history" in sub_question.lower() or "over time" in sub_question.lower())
            series = [{"key": "value", "label": "Return"}]
            if is_time:
                ds = dates_monthly(n)
                data = [{"date": d, "value": round(random.gauss(1.5, 4), 2)} for d in ds]
            else:
                labels = label_items(n, "Sector")
                data = [{"name": l, "value": round(random.uniform(5, 35), 2)} for l in labels]
            return {
                "data": data,
                "series": series,
                "xKey": "date" if is_time else "name",
                "colorRule": "gain-loss",
            }

        # FKWaterfall ──────────────────────────────────────────────────────────
        elif block_id == "FKWaterfall":
            items = ["Revenue", "COGS", "Gross Profit", "OpEx", "EBITDA", "D&A", "EBIT", "Tax", "Net Income"]
            total = round(random.uniform(80, 120), 1)
            rows = [{"label": "Revenue", "value": total, "type": "start"}]
            for item in items[1:-1]:
                v = round(random.uniform(-30, 20), 1)
                rows.append({"label": item, "value": v, "type": "delta"})
            rows.append({"label": "Net Income", "value": None, "type": "end"})
            return {"data": rows}

        # FKHistogram ──────────────────────────────────────────────────────────
        elif block_id == "FKHistogram":
            count = max(n * 10, 100)
            return {
                "data": [round(random.gauss(0.8, 3.5), 3) for _ in range(count)],
                "overlayNormal": True,
            }

        # FKPartChart ──────────────────────────────────────────────────────────
        elif block_id == "FKPartChart":
            sectors = ["Technology", "Healthcare", "Financials", "Consumer", "Energy",
                       "Industrials", "Materials", "Utilities", "Real Estate", "Communication"]
            count = min(max(n, 4), len(sectors))
            chosen = random.sample(sectors, count)
            raw = [random.uniform(5, 35) for _ in chosen]
            total = sum(raw)
            mode = "treemap" if count > 7 else "donut"
            return {
                "data": [{"label": s, "value": round(v / total * 100, 2)}
                         for s, v in zip(chosen, raw)],
                "labelKey": "label",
                "valueKey": "value",
                "mode": mode,
            }

        # FKHeatGrid ───────────────────────────────────────────────────────────
        elif block_id == "FKHeatGrid":
            months = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
            years  = ["2022","2023","2024"]
            return {
                "data": [
                    {"row": m, "col": y, "value": round(random.gauss(1.0, 3.5), 2)}
                    for m in months for y in years
                ],
                "rowKey": "row",
                "colKey": "col",
                "valueKey": "value",
                "colorScale": "diverging",
                "valueFormat": "pct",
            }

        # FKScatterChart ───────────────────────────────────────────────────────
        elif block_id == "FKScatterChart":
            tickers = ["AAPL","MSFT","NVDA","AMZN","META","GOOGL","TSLA","JPM","BRK","V"]
            count = min(n, len(tickers))
            return {
                "data": [
                    {
                        "x": round(random.uniform(0, 25), 2),
                        "y": round(random.uniform(-10, 35), 2),
                        "size": round(random.uniform(5, 50), 1),
                        "label": tickers[i],
                    }
                    for i in range(count)
                ],
                "xKey": "x",
                "yKey": "y",
                "sizeKey": "size",
                "labelKey": "label",
                "trendLine": True,
            }

        # FKBulletChart ────────────────────────────────────────────────────────
        elif block_id == "FKBulletChart":
            labels = label_items(max(n, 3), "Target")
            return {
                "data": [
                    {
                        "label": l,
                        "value":    round(random.uniform(40, 95), 1),
                        "target":   round(random.uniform(70, 100), 1),
                        "rangeMin": 0,
                        "rangeMax": 100,
                    }
                    for l in labels
                ]
            }

        # FKRangeChart ─────────────────────────────────────────────────────────
        elif block_id == "FKRangeChart":
            tickers = ["AAPL","MSFT","GOOGL","NVDA","AMZN","META","TSLA","JPM"]
            count = min(max(n, 4), len(tickers))
            return {
                "data": [
                    {
                        "label": tickers[i],
                        "min":   round(random.uniform(80, 150), 2),
                        "max":   round(random.uniform(200, 350), 2),
                        "value": round(random.uniform(150, 250), 2),
                    }
                    for i in range(count)
                ],
                "labelKey": "label",
                "minKey":   "min",
                "maxKey":   "max",
                "valueKey": "value",
            }

        # FKCandleChart ────────────────────────────────────────────────────────
        elif block_id == "FKCandleChart":
            count = max(n * 5, 60)
            price = 150.0
            ds = [(datetime.now() - timedelta(days=count-i)).strftime("%Y-%m-%d")
                  for i in range(count)]
            candles = []
            for d in ds:
                o = round(price * (1 + random.gauss(0, 0.008)), 2)
                c = round(o    * (1 + random.gauss(0.001, 0.012)), 2)
                h = round(max(o, c) * (1 + abs(random.gauss(0, 0.005))), 2)
                l = round(min(o, c) * (1 - abs(random.gauss(0, 0.005))), 2)
                candles.append({"date": d, "open": o, "high": h, "low": l, "close": c,
                                 "volume": random.randint(1_000_000, 50_000_000)})
                price = c
            return {"data": candles}

        # FKMultiPanel ─────────────────────────────────────────────────────────
        elif block_id == "FKMultiPanel":
            ds = dates_daily(max(n * 5, 60))
            price, vol_ma = 150.0, 10_000_000
            price_data, rsi_data, vol_data = [], [], []
            for d in ds:
                price = round(price * (1 + random.gauss(0.001, 0.014)), 2)
                price_data.append({"date": d, "price": price})
                rsi_data.append({"date": d, "rsi": round(random.uniform(30, 70), 1)})
                vol_data.append({"date": d, "volume": random.randint(5_000_000, 50_000_000)})
            return {
                "panels": [
                    {"series": [{"key": "price", "label": "Price"}],
                     "data": price_data, "height": 200},
                    {"series": [{"key": "rsi", "label": "RSI"}],
                     "data": rsi_data, "height": 100,
                     "referenceLines": [{"y": 70, "color": "#dc2626"}, {"y": 30, "color": "#16a34a"}]},
                    {"series": [{"key": "volume", "label": "Volume"}],
                     "data": vol_data, "height": 80},
                ]
            }

        # FKProjectionChart ────────────────────────────────────────────────────
        elif block_id == "FKProjectionChart":
            hist_n  = max(n * 3, 24)
            proj_n  = max(n, 12)
            hist_dates = dates_monthly(hist_n)
            split_date = hist_dates[-1]
            proj_dates = [(datetime.now() + timedelta(days=30*i)).strftime("%Y-%m-%d")
                          for i in range(1, proj_n + 1)]
            v = 100.0
            historical = []
            for d in hist_dates:
                v = round(v * (1 + random.gauss(0.005, 0.025)), 2)
                historical.append({"date": d, "value": v})
            projection = []
            p = v
            for d in proj_dates:
                p50 = round(p * (1 + random.gauss(0.006, 0.02)), 2)
                spread = abs(p50 - p) * random.uniform(0.5, 1.5)
                projection.append({
                    "date": d,
                    "p50": p50,
                    "p25": round(p50 - spread * 0.6, 2),
                    "p75": round(p50 + spread * 0.6, 2),
                    "p10": round(p50 - spread * 1.2, 2),
                    "p90": round(p50 + spread * 1.2, 2),
                })
                p = p50
            return {
                "historical": historical,
                "projection": projection,
                "splitDate": split_date,
            }

        # FKRadarChart ─────────────────────────────────────────────────────────
        elif block_id == "FKRadarChart":
            axis_names = ["Value", "Quality", "Momentum", "Growth", "Safety", "Yield"]
            axes = [{"key": a.lower(), "label": a} for a in axis_names]
            tickers = ["AAPL", "MSFT", "GOOGL"]
            colors  = ["#6366f1", "#22c55e", "#f59e0b"]
            series = [
                {
                    "label": t,
                    "color": colors[i],
                    "data": {a["key"]: round(random.uniform(3, 9), 1) for a in axes},
                }
                for i, t in enumerate(tickers[:2])
            ]
            return {"axes": axes, "series": series}

        # FKSankeyChart ────────────────────────────────────────────────────────
        elif block_id == "FKSankeyChart":
            nodes = [
                {"id": "equities",   "label": "Equities",   "column": 0},
                {"id": "fixed",      "label": "Fixed Inc.", "column": 0},
                {"id": "alts",       "label": "Alts",       "column": 0},
                {"id": "us",         "label": "US",         "column": 1},
                {"id": "intl",       "label": "Intl",       "column": 1},
                {"id": "growth",     "label": "Growth",     "column": 2},
                {"id": "value",      "label": "Value",      "column": 2},
                {"id": "income",     "label": "Income",     "column": 2},
            ]
            flows = [
                {"from": "equities", "to": "us",     "value": 30},
                {"from": "equities", "to": "intl",   "value": 20},
                {"from": "fixed",    "to": "us",     "value": 15},
                {"from": "fixed",    "to": "income", "value": 10},
                {"from": "alts",     "to": "intl",   "value": 8},
                {"from": "us",       "to": "growth", "value": 28},
                {"from": "us",       "to": "value",  "value": 17},
                {"from": "intl",     "to": "growth", "value": 18},
                {"from": "intl",     "to": "income", "value": 10},
            ]
            return {"nodes": nodes, "flows": flows}

        # FKDataTable / FKTable ────────────────────────────────────────────────
        elif block_id in ("FKDataTable", "FKTable"):
            num_rows = max(n, 5)
            tickers = [f"TKR{i+1}" for i in range(num_rows)]
            columns = [
                {"key": "ticker",   "label": "Symbol"},
                {"key": "price",    "label": "Price",   "align": "right", "mono": True},
                {"key": "change",   "label": "Change",  "align": "right", "mono": True,
                 "colorRule": "gain-loss"},
                {"key": "weight",   "label": "Weight",  "align": "right", "mono": True},
                {"key": "value",    "label": "Value",   "align": "right", "mono": True},
            ]
            return {
                "columns": columns,
                "rows": [
                    {
                        "ticker": tickers[i],
                        "price":  round(random.uniform(20, 500), 2),
                        "change": round(random.uniform(-5, 8), 2),
                        "weight": round(random.uniform(1, 20), 1),
                        "value":  round(random.uniform(1000, 50000), 0),
                    }
                    for i in range(num_rows)
                ]
            }

        # FKRankedList ─────────────────────────────────────────────────────────
        elif block_id == "FKRankedList":
            count = max(n, 5)
            labels = label_items(count, "Asset")
            return {
                "data": sorted(
                    [{"label": l, "value": round(random.uniform(-10, 40), 2)} for l in labels],
                    key=lambda x: x["value"], reverse=True
                ),
                "labelKey": "label",
                "valueKey": "value",
            }

        # FKTimeline ───────────────────────────────────────────────────────────
        elif block_id == "FKTimeline":
            types = ["earnings", "dividend", "split", "news", "fed"]
            labels = ["Q3 Earnings", "Dividend $0.25", "Fed Rate Decision",
                      "Product Launch", "Analyst Upgrade", "M&A Announcement"]
            count = max(n, 4)
            events = []
            for i in range(count):
                d = (datetime.now() - timedelta(days=random.randint(0, 180))).strftime("%Y-%m-%d")
                events.append({
                    "date": d,
                    "label": labels[i % len(labels)],
                    "type": types[i % len(types)],
                })
            return {"events": sorted(events, key=lambda x: x["date"])}

        # ── fallback: FKMetricGrid with 3 generic cards ────────────────────────
        else:
            return {
                "cards": [
                    {"label": "Value",  "value": f"${random.uniform(10000, 500000):,.0f}", "delta": round(random.uniform(-10, 20), 2)},
                    {"label": "Return", "value": f"{random.uniform(-10, 30):.2f}%",        "delta": round(random.uniform(-5, 15), 2)},
                    {"label": "Risk",   "value": f"{random.uniform(5, 25):.2f}%",          "sub": "annualised"},
                ],
                "cols": 3,
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