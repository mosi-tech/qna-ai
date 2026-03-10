#!/usr/bin/env python3
"""
step3_cache_enhanced.py — Enhanced Cache with LLM Classification and Routing

Purpose: Classify sub-questions, check cache, and route to optimal path.
         Uses LLM-based classification instead of verbose registry patterns.

Usage:
    python step3_cache_enhanced.py --dashboard-id <uuid>
    python step3_cache_enhanced.py --question "What is QQQ's current price?"
    python step3_cache_enhanced.py --sub-questions '{"blocks": [...]}'

This step:
    1. Uses LLM classifier to identify MCP function(s) for each question
    2. Checks cache based on identified function(s)
    3. Returns routing decisions for each block

Output: JSON with routing decisions for each block
"""

import asyncio
import sys
import os
import argparse
import json
import hashlib
import re
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add backend to path
_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_DIR, "..", ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(_DIR), "..", "..", "apiServer", ".env"))

from shared.llm.service import LLMService, LLMConfig
from shared.llm.mcp_tools import _mcp_loader


class QuestionClassifier:
    """
    Question classifier that uses LLM to identify MCP functions.

    Uses LLMService for intelligent classification with regex fallback.
    """

    PATHS = {
        "direct_mcp": {
            "route_to": "step5a_direct_function",
            "priority": 1,
            "expected_time_ms": 100,
            "description": "Direct MCP function call (fastest)"
        },
        "script_generation": {
            "route_to": "step4_enqueue",
            "priority": 2,
            "expected_time_ms": 7500,
            "description": "Script generation + execution (slowest)"
        }
    }

    # System prompt for LLM classification
    _SYSTEM_PROMPT = """You are a question classifier. Your job is to determine the fastest path to answer a financial question.

## Context

You are part of a dashboard pipeline where questions are broken down into sub-questions. Each sub-question needs to be answered via one of two paths:

### Paths (in order of speed)

1. **direct_mcp** (Fastest - 100-500ms)
   - Question maps directly to a registered MCP function
   - Single, well-defined operation
   - Examples:
     - "What is QQQ's current price?" → get_real_time_data
     - "Top 10 gainers today" → get_top_gainers
     - "Calculate VaR at 95%" → calculate_var

2. **script_generation** (Fallback - 5-10s)
   - Novel question, no matching MCP function
   - Complex, custom analysis required
   - Examples:
     - "Analyze how earnings announcements affect my portfolio's beta"
     - "Build a custom strategy based on RSI and volume divergences"

## Available MCP Functions

The following MCP functions are available. Match the question to the most appropriate function:

{{MCP_FUNCTIONS}}

## Output Format

Return ONLY a JSON object with this structure:
{
  "question": "original question",
  "path": "direct_mcp|script_generation",
  "target": "function_name|script_generation",
  "mcp_server": "mcp-financial-server|mcp-analytics-server|mcp-validation-server",
  "confidence": 0.95,
  "params": {
    "param1": "value1",
    "param2": "value2"
  },
  "reasoning": "Brief explanation of classification"
}

## Process

1. Parse the question
2. Check if it matches any available MCP function
3. If confident match → return direct_mcp with the function name
4. If no confident match → return script_generation

## Keep It Fast

- This is a classification task, NOT an analysis task
- Return result immediately on confident match
- Don't overthink - if uncertain, fall back to script_generation
- Output ONLY JSON, no other text"""

    # Simple pattern-based classification (fallback)
    _MCP_PATTERNS = {
        # Financial MCP patterns
        "get_real_time_data": [
            r"(?:current price|quote|trading at).*?([A-Z]{2,5})",
            r"([A-Z]{2,5}).*?(?:current price|quote|trading at)",
            r"what(?:'?s| is)\s+([A-Z]{2,5}).*?(?:trading at|currently at|price)",
        ],
        "get_top_gainers": [
            r"top\s+(\d+)\s+(?:gainers|winners|best performers)",
            r"stocks with (?:biggest|largest)\s+(?:gains)",
        ],
        "get_top_losers": [
            r"top\s+(\d+)\s+(?:losers|droppers|worst performers)",
            r"stocks with (?:biggest|largest)\s+(?:drops|loss)",
        ],
        "get_most_active_stocks": [
            r"(?:most active|highest volume|highest.*volume) stocks?",
            r"stocks with (?:highest|most)\s+volume",
            r"highest.*trading volume",
            r"most.*volume",
        ],
        "get_fundamentals": [
            r"(?:P\/E|PE) ratio.*?([A-Z]{2,5})",
            r"([A-Z]{2,5}).*?(?:fundamentals|P\/E|PE)",
            r"fundamentals of ([A-Z]{2,5})",
        ],
        "get_dividends": [
            r"dividends?(?:\s+(?:history|yield|for))?.*?([A-Z]{2,5})",
            r"([A-Z]{2,5}).*?dividends?",
        ],
        "get_account": [
            r"(?:my\s+)?account",
            r"account\s+(?:balance|info|details)",
            r"buying\s+power",
        ],
        "get_positions": [
            r"my\s+(?:positions|holdings)",
            r"current\s+positions",
        ],
        # Analytics MCP patterns
        "calculate_var": [
            r"VaR at\s+(\d+(?:\.\d+)?)\s*%",
            r"value at risk.*at\s+(\d+(?:\.\d+)?)\s*%",
        ],
        "calculate_sma": [
            r"(\d+)[-–\s]day\s+(?:simple\s+)?moving\s+average",
            r"SMA(?:\s+(\d+))?",
            r"moving average",
        ],
        "calculate_rsi": [
            r"RSI(?:\s+of\s+([A-Z]{2,5}))?",
        ],
        "calculate_macd": [
            r"MACD(?:\s+of\s+([A-Z]{2,5}))?",
        ],
        "calculate_correlation": [
            r"correlation\s+between\s+([A-Z]{2,5})\s+(?:and|vs)\s+([A-Z]{2,5})",
        ],
        "calculate_risk_metrics": [
            r"(?:Sortino|Sharpe|risk.*metric)s?\s+ratio",
            r"portfolio.*risk.*metric",
        ],
    }

    def __init__(self, no_fallback: bool = False):
        self._llm_service = None
        self._llm_initialized = False
        self._no_fallback = no_fallback
        self._mcp_functions = None
        self._system_prompt_cached = None

    async def _ensure_mcp_functions(self) -> List[Dict[str, Any]]:
        """Discover and cache MCP functions"""
        if self._mcp_functions is not None:
            return self._mcp_functions

        try:
            # Load tools from MCP servers
            tools = await _mcp_loader.load_tools_for_service("analysis")

            # Extract function info for classification
            mcp_functions = []
            for tool in tools:
                if tool.get("type") == "function":
                    func_info = tool.get("function", {})
                    name = func_info.get("name", "")
                    description = func_info.get("description", "")

                    # Strip server prefix if present
                    if "__" in name:
                        server_name, func_name = name.split("__", 1)
                    else:
                        server_name = "unknown"
                        func_name = name

                    mcp_functions.append({
                        "name": func_name,
                        "server": server_name,
                        "full_name": name,
                        "description": description
                    })

            self._mcp_functions = mcp_functions
            print(f"Discovered {len(mcp_functions)} MCP functions", file=sys.stderr)
            return mcp_functions

        except Exception as e:
            print(f"Warning: Failed to discover MCP functions: {e}", file=sys.stderr)
            self._mcp_functions = []
            return []

    def _get_system_prompt(self) -> str:
        """Get system prompt with MCP functions populated"""
        if self._system_prompt_cached:
            return self._system_prompt_cached

        # If no functions discovered yet, return template with empty list
        if self._mcp_functions is None:
            return self._SYSTEM_PROMPT.replace("{{MCP_FUNCTIONS}}", "No MCP functions available.")

        # Build function list grouped by server
        server_groups = {}
        for func in self._mcp_functions:
            server = func.get("server", "unknown")
            if server not in server_groups:
                server_groups[server] = []
            server_groups[server].append(func)

        # Format function list for system prompt
        functions_text = ""
        for server, funcs in sorted(server_groups.items()):
            functions_text += f"\n### {server}\n"
            for func in funcs:
                name = func.get("name", "")
                desc = func.get("description", "")
                functions_text += f"- **{name}**: {desc}\n"

        self._system_prompt_cached = self._SYSTEM_PROMPT.replace("{{MCP_FUNCTIONS}}", functions_text)
        return self._system_prompt_cached

    def _ensure_llm(self):
        """Lazy initialization of LLM service"""
        if self._llm_initialized:
            return

        try:
            config = LLMConfig.for_task("ANALYSIS")
            self._llm_service = LLMService(config)
            self._llm_initialized = True
        except Exception as e:
            if self._no_fallback:
                raise RuntimeError(f"LLM initialization failed and no_fallback is True: {e}")
            print(f"Warning: Failed to initialize LLM service: {e}", file=sys.stderr)
            self._llm_initialized = True  # Mark as initialized to avoid retries

    async def classify_async(self, question: str) -> Dict[str, Any]:
        """
        Classify a question into optimal response path using LLM.

        Args:
            question: The question string to classify

        Returns:
            Dict with path, target function(s), confidence, params, and reasoning
        """
        # Ensure LLM is initialized
        self._ensure_llm()

        # Discover MCP functions
        await self._ensure_mcp_functions()

        if not self._llm_service:
            # Fallback to regex if LLM not available
            return self._classify_regex(question)

        try:
            prompt = f"""Classify this financial question and return the result as JSON:

Question: "{question}"

Remember to return ONLY JSON, no other text."""

            response = await self._llm_service.simple_completion(
                prompt=prompt,
                system_prompt=self._get_system_prompt(),
                max_tokens=500,
                temperature=0.1  # Low temperature for consistent classification
            )

            if response.get("success") and response.get("content"):
                # Parse JSON from LLM response
                import re
                content = response["content"].strip()

                # Extract JSON from response (handle potential markdown code blocks)
                json_match = re.search(r'\{[\s\S]*\}', content)
                if json_match:
                    json_str = json_match.group(0)
                    classification = json.loads(json_str)

                    # Get the path from classification (should be "direct_mcp" or "script_generation")
                    internal_path = classification.get("path", "script_generation")
                    # Normalize: allow "direct_function" from LLM but convert to "direct_mcp"
                    if internal_path == "direct_function":
                        internal_path = "direct_mcp"
                    elif internal_path not in self.PATHS:
                        internal_path = "script_generation"

                    # Get target and mcp_server from classification
                    target = classification.get("target", "script_generation")
                    mcp_server = classification.get("mcp_server")

                    # If path is direct_mcp but mcp_server not provided, try to determine from target
                    if internal_path == "direct_mcp" and not mcp_server:
                        # Look up the function in discovered MCP functions
                        for func in self._mcp_functions or []:
                            if func["name"] == target:
                                mcp_server = func["server"]
                                break

                    # Get path info
                    path_info = self.PATHS.get(internal_path, self.PATHS["script_generation"])

                    return {
                        "path": internal_path,
                        "target": target,
                        "mcp_server": mcp_server,
                        "confidence": classification.get("confidence", 0.70),
                        "params": classification.get("params", {}),
                        "reasoning": classification.get("reasoning", "LLM classification"),
                        **path_info
                    }

            # Fallback if LLM response parsing fails
            return self._classify_regex(question)

        except Exception as e:
            print(f"Warning: LLM classification failed, using regex fallback: {e}", file=sys.stderr)
            return self._classify_regex(question)

    def classify(self, question: str) -> Dict[str, Any]:
        """
        Classify a question (synchronous wrapper).

        Args:
            question: The question string to classify

        Returns:
            Dict with path, target function(s), confidence, params, and reasoning
        """
        # Run async classification in sync context
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a new loop
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.classify_async(question)
                    )
                    return future.result(timeout=10)
            else:
                return asyncio.run(self.classify_async(question))
        except Exception as e:
            if self._no_fallback:
                raise RuntimeError(f"Classification failed and no_fallback is True: {e}")
            print(f"Warning: Async classification failed, using regex fallback: {e}", file=sys.stderr)
            if self._no_fallback:
                raise RuntimeError(f"Classification failed and no_fallback is True: {e}")
            return self._classify_regex(question)

    def _classify_regex(self, question: str) -> Dict[str, Any]:
        """Fallback classification using regex patterns"""
        import re

        question_lower = question.lower()

        # Try to match MCP function patterns
        for function_name, patterns in self._MCP_PATTERNS.items():
            for pattern in patterns:
                match = re.search(pattern, question, re.IGNORECASE)
                if match:
                    # Determine MCP server
                    if function_name.startswith("get_") and function_name not in ["get_account", "get_positions"]:
                        mcp_server = "mcp-financial-server"
                    elif function_name.startswith("calculate_"):
                        mcp_server = "mcp-analytics-server"
                    else:
                        mcp_server = "mcp-financial-server"

                    # Extract parameters
                    params = self._extract_params(question, match, pattern, function_name)

                    return {
                        "path": "direct_mcp",
                        "target": function_name,
                        "mcp_server": mcp_server,
                        "confidence": 0.85,  # Slightly lower confidence for regex
                        "params": params,
                        "reasoning": f"Matched pattern for {function_name}",
                        **self.PATHS["direct_mcp"]
                    }

        # Fallback to script generation
        return {
            "path": "script_generation",
            "target": "script_generation",
            "mcp_server": None,
            "confidence": 0.50,
            "params": {},
            "reasoning": "No direct MCP function match found",
            **self.PATHS["script_generation"]
        }

    def _extract_params(self, question: str, match: re.Match, pattern: str,
                       function_name: str) -> Dict[str, Any]:
        """Extract parameters from question based on pattern match"""
        params = {}
        groups = match.groups()

        # Extract symbols
        symbols = re.findall(r"\b[A-Z]{2,5}\b", question)
        if symbols:
            if function_name in ["get_real_time_data", "get_historical_data", "get_latest_quotes", "get_latest_trades"]:
                params["symbols"] = symbols
            elif function_name in ["get_fundamentals", "get_dividends", "get_splits"]:
                params["symbol"] = symbols[0]

        # Extract numbers (limits, confidence levels, periods)
        if groups:
            for i, group in enumerate(groups):
                if group and group.isdigit():
                    num = int(group)
                    if "gainer" in pattern.lower() or "loser" in pattern.lower():
                        params["limit"] = num
                    elif "var" in pattern.lower() or "confidence" in pattern.lower():
                        params["confidence_level"] = float(num) / 100
                    elif "sma" in pattern.lower() or "ema" in pattern.lower() or "rsi" in pattern.lower():
                        params["period"] = num

        return params


class CacheService:
    """Service for cache operations"""

    def __init__(self):
        self.memory_cache = {}

    def generate_cache_key(self, question: str, path: str, target: str) -> str:
        """Generate deterministic cache key"""
        key_str = f"{path}:{target}:{question.lower().strip()}"
        return hashlib.md5(key_str.encode()).hexdigest()[:16]

    def get(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached result"""
        return self.memory_cache.get(cache_key)

    def set(self, cache_key: str, result: Dict[str, Any], ttl: int = 300):
        """Set cached result with TTL"""
        self.memory_cache[cache_key] = {
            "result": result,
            "expires_at": datetime.now().timestamp() + ttl
        }

    def check_ttl(self, cache_key: str) -> bool:
        """Check if cached result is still valid"""
        cached = self.memory_cache.get(cache_key)
        if not cached:
            return False
        return cached["expires_at"] > datetime.now().timestamp()


class EnhancedCacheStep:
    """Enhanced cache step with LLM classification and routing"""

    def __init__(self):
        self.classifier = QuestionClassifier()
        self.cache = CacheService()

    def process_sub_questions(self, sub_questions: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process sub-questions and return routing decisions.

        Args:
            sub_questions: List of sub-questions with block metadata

        Returns:
            Dict with routing decisions for each block
        """
        routing_decisions = []

        for sq in sub_questions:
            block_id = sq.get("block_id", sq.get("id", ""))
            sub_question = sq.get("sub_question", sq.get("question", ""))

            # Classify the question
            classification = self.classifier.classify(sub_question)

            # Check cache
            cache_key = self.cache.generate_cache_key(
                sub_question,
                classification["path"],
                classification["target"]
            )

            cache_hit = False
            cached_result = None

            if self.cache.check_ttl(cache_key):
                cached = self.cache.get(cache_key)
                if cached:
                    cache_hit = True
                    cached_result = cached["result"]

            # Create routing decision
            routing_decisions.append({
                "block_id": block_id,
                "sub_question": sub_question,
                "classification": {
                    "path": classification["path"],
                    "target": classification["target"],
                    "mcp_server": classification.get("mcp_server"),
                    "confidence": classification["confidence"],
                    "reasoning": classification["reasoning"],
                    "expected_time_ms": classification["expected_time_ms"]
                },
                "params": classification.get("params", {}),
                "cache_hit": cache_hit,
                "route_to": classification["route_to"],
                "cached_result": cached_result if cache_hit else None
            })

        # Calculate summary
        summary = self._calculate_summary(routing_decisions)

        return {
            "timestamp": datetime.now().isoformat(),
            "total_blocks": len(routing_decisions),
            "routing_decisions": routing_decisions,
            "summary": summary
        }

    def _calculate_summary(self, decisions: List[Dict]) -> Dict[str, Any]:
        """Calculate summary statistics"""
        summary = {
            "cache_hits": 0,
            "cache_misses": 0,
            "by_path": {
                "direct_mcp": 0,
                "script_generation": 0
            },
            "by_route": {
                "step5a_direct_function": 0,
                "step4_enqueue": 0
            },
            "expected_total_time_ms": 0
        }

        for decision in decisions:
            if decision["cache_hit"]:
                summary["cache_hits"] += 1
            else:
                summary["cache_misses"] += 1

            path = decision["classification"]["path"]
            summary["by_path"][path] += 1

            route = decision["route_to"]
            summary["by_route"][route] += 1

            if not decision["cache_hit"]:
                summary["expected_total_time_ms"] += decision["classification"]["expected_time_ms"]

        summary["expected_total_time_seconds"] = summary["expected_total_time_ms"] / 1000
        return summary


def save_output(result: Dict[str, Any], output_dir: str = None):
    """Save result to output directory"""
    if output_dir is None:
        output_dir = os.path.join(_DIR, "output")

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_dir, f"step3_routing_{timestamp}.json")

    with open(output_file, "w") as f:
        json.dump(result, f, indent=2)

    print(f"Output saved to: {output_file}", file=sys.stderr)
    return output_file


async def main():
    parser = argparse.ArgumentParser(
        description="Enhanced cache step with LLM classification and routing"
    )
    parser.add_argument("--dashboard-id", help="Dashboard ID (loads from DB)")
    parser.add_argument("--question", help="Single question to classify")
    parser.add_argument("--sub-questions", help="Sub-questions as JSON string")
    parser.add_argument("--sub-questions-file", help="File containing sub-questions")
    parser.add_argument("--output-dir", help="Output directory (default: ./output)")
    parser.add_argument("--pretty", action="store_true", help="Pretty print output")

    args = parser.parse_args()

    step = EnhancedCacheStep()
    result = None

    if args.question:
        # Classify single question
        classification = step.classifier.classify(args.question)
        cache_key = step.cache.generate_cache_key(args.question, classification["path"], classification["target"])
        cache_hit = step.cache.check_ttl(cache_key)

        result = {
            "timestamp": datetime.now().isoformat(),
            "question": args.question,
            "classification": {
                "path": classification["path"],
                "target": classification["target"],
                "mcp_server": classification.get("mcp_server"),
                "confidence": classification["confidence"],
                "reasoning": classification["reasoning"],
                "expected_time_ms": classification["expected_time_ms"]
            },
            "params": classification.get("params", {}),
            "cache_key": cache_key,
            "cache_hit": cache_hit,
            "route_to": classification["route_to"]
        }

    elif args.sub_questions:
        # Process sub-questions from JSON string
        sub_questions = json.loads(args.sub_questions)
        result = step.process_sub_questions(sub_questions)

    elif args.sub_questions_file:
        # Process sub-questions from file
        with open(args.sub_questions_file, "r") as f:
            sub_questions = json.load(f)
        result = step.process_sub_questions(sub_questions)

    elif args.dashboard_id:
        # Load sub-questions from DB (placeholder)
        result = {
            "timestamp": datetime.now().isoformat(),
            "dashboard_id": args.dashboard_id,
            "routing_decisions": [],
            "summary": {
                "cache_hits": 0,
                "cache_misses": 0,
                "by_path": {},
                "by_route": {},
                "expected_total_time_seconds": 0
            }
        }

    else:
        parser.print_help()
        sys.exit(1)

    _ = save_output(result, args.output_dir)

    if args.pretty:
        print(json.dumps(result, indent=2))
    else:
        print(json.dumps(result))

    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())