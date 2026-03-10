#!/usr/bin/env python3
"""
Cache Hydration Pipeline

Iteratively discovers generic question templates to achieve high cache hit rates.

The pipeline:
1. Generates realistic financial questions (via LLM)
2. Sends them to UIPlanner to get block decompositions
3. Converts specific questions → generic templates (block-aware)
4. Tracks cache hit rate
5. Repeats until target hit rate achieved (default 95%)

Usage:
    # Quick test without LLM (uses fallback questions)
    python hydrate_pipeline.py --max-iterations 500

    # With LLM for realistic question generation
    python hydrate_pipeline.py --use-llm --warm-cache 500

    # Full pipeline with UIPlanner
    python hydrate_pipeline.py --use-planner --use-llm --max-iterations 1000

    # Run until 95% hit rate
    python hydrate_pipeline.py --target 0.95 --max-iterations 5000
"""

import asyncio
import json
import hashlib
import os
import sys
import random
import argparse
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import defaultdict

# Path setup
_DIR = os.path.dirname(os.path.abspath(__file__))
_BACKEND = os.path.normpath(os.path.join(_DIR, "..", ".."))
_OUTPUT = os.path.join(_DIR, "output")
sys.path.insert(0, _BACKEND)

from dotenv import load_dotenv
load_dotenv(os.path.join(_BACKEND, "apiServer", ".env"))

import logging
logging.basicConfig(level=logging.WARNING, stream=sys.stderr)

logger = logging.getLogger("hydrate")
logger.setLevel(logging.INFO)
_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("[hydrate] %(message)s"))
logger.addHandler(_handler)
logger.propagate = False

# Import prompts
from prompts import (
    QUESTION_GENERATOR_PROMPT,
    GENERIC_QUESTION_PROMPT,
    BLOCK_CONTEXT_PROMPT,
)


# =============================================================================
# Data Structures
# =============================================================================

@dataclass
class GenericQuestion:
    """A generic, parametric question template."""
    template: str                           # "What is {{ticker}}'s current price?"
    params: List[str]                       # ["ticker"]
    block_type: str                         # "kpi-cards"
    output_shape: str                       # "single scalar value"
    block_contract: Dict[str, Any]          # {"type": "kpi", "points": 1}
    generic_key: str = ""                   # Computed hash
    intent: str = ""                        # Intent category: PRICE_QUERY, RISK_METRICS, etc.
    metrics_included: List[str] = None      # Specific metrics: ["max_drawdown", "sharpe_ratio"]
    discovered_from: str = ""               # Original sub-question
    original_question: str = ""             # Original complex question (before decomposition)
    block_id: str = ""                      # Block ID from UIPlanner
    hit_count: int = 0                      # How many times this was hit
    first_seen: str = ""                    # ISO timestamp
    last_seen: str = ""                     # ISO timestamp

    def __post_init__(self):
        if self.metrics_included is None:
            self.metrics_included = []
        if not self.generic_key:
            key_data = {
                "template": self.template,
                "block_type": self.block_type,
            }
            self.generic_key = hashlib.sha256(
                json.dumps(key_data, sort_keys=True).encode()
            ).hexdigest()[:16]


@dataclass
class QuestionDecomposition:
    """Tracks the mapping from original question to sub-questions to generic templates."""
    original_question: str                  # Complex question from user
    sub_questions: List[Dict[str, Any]]     # Decomposed blocks from UIPlanner
    generic_templates: List[str]            # Generic template for each block
    timestamp: str = ""


@dataclass
class CacheStats:
    """Statistics for cache coverage."""
    total_questions: int = 0
    total_blocks: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    unique_generic_questions: int = 0

    @property
    def hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        return self.cache_hits / total if total > 0 else 0.0


# =============================================================================
# Question Generator (LLM-powered)
# =============================================================================

class QuestionGenerator:
    """
    Generates realistic financial questions using an LLM.
    Simulates real-world user queries for cache coverage testing.
    """

    def __init__(self, llm_service=None):
        self.llm_service = llm_service

    async def generate_batch(self, count: int = 100) -> List[str]:
        """Generate a batch of realistic financial questions."""
        if self.llm_service:
            try:
                # Use system_prompt parameter for LLM service, user message for actual request
                system_prompt = QUESTION_GENERATOR_PROMPT.split("## OUTPUT FORMAT")[0].strip()
                user_message = f"Generate {count} diverse, realistic financial questions now. Output JSON array format: [\"Question 1?\", \"Question 2?\", ...]"

                response = await self.llm_service.make_request(
                    messages=[{"role": "user", "content": user_message}],
                    system_prompt=system_prompt,
                    max_tokens=4000,
                    temperature=0.8,  # Higher temperature for diversity
                )

                content = response.get("content", "")
                questions = self._parse_questions(content)

                if questions:
                    logger.info(f"LLM generated {len(questions)} questions")
                    return questions

            except Exception as e:
                logger.warning(f"LLM question generation failed: {e}")

        # Fallback: return predefined questions
        return self._fallback_questions(count)

    def _parse_questions(self, content: str) -> List[str]:
        """Parse LLM response into list of questions."""
        try:
            content = content.strip()
            if content.startswith("["):
                return json.loads(content)

            start = content.find("[")
            end = content.rfind("]") + 1
            if start >= 0 and end > start:
                return json.loads(content[start:end])

        except json.JSONDecodeError:
            pass

        # Fallback: parse line by line
        lines = content.strip().split("\n")
        questions = []
        for line in lines:
            line = line.strip()
            if line and len(line) > 10:
                if line[0].isdigit():
                    line = line.lstrip("0123456789. ").strip()
                line = line.strip('"\'')
                if line.endswith("?"):
                    questions.append(line)

        return questions

    def _fallback_questions(self, count: int) -> List[str]:
        """Fallback questions when LLM is not available."""
        base_questions = [
            "What is QQQ's current price?",
            "How has SPY performed this year?",
            "Compare NVDA and AMD performance",
            "What's Tesla's P/E ratio?",
            "Show me Apple's revenue growth",
            "What are the top holdings in VOO?",
            "How volatile is Bitcoin right now?",
            "What's the dividend yield on SCHD?",
            "Compare QQQ vs SPY vs DIA returns",
            "What's Microsoft's market cap?",
            "Show me Amazon's earnings history",
            "What is Meta's current valuation?",
            "How has the tech sector performed?",
            "What's the 52-week high for GOOGL?",
            "Show me JPMorgan's key metrics",
            "What is Costco's profit margin?",
            "How correlated are NVDA and AMD?",
            "What's the Sharpe ratio for QQQ?",
            "Show me Visa vs Mastercard comparison",
            "What's the beta of TSLA?",
            "How has gold performed vs S&P 500?",
            "What are the best performing ETFs?",
            "Show me Netflix's subscriber growth",
            "What's the debt-to-equity for Intel?",
            "Compare growth vs value ETFs",
            "What's the PE ratio of the S&P 500?",
            "Show me defensive sector performance",
            "What's the yield on 10-year Treasury?",
            "How has the dollar performed lately?",
            "What's the VIX level right now?",
        ]

        questions = []
        while len(questions) < count:
            questions.extend(base_questions)
        random.shuffle(questions)
        return questions[:count]


# =============================================================================
# Generic Question Generator
# =============================================================================

class GenericQuestionGenerator:
    """Converts specific questions into generic, cacheable templates."""

    def __init__(self, llm_service=None):
        self.llm_service = llm_service

    async def genericize(
        self,
        sub_question: str,
        block_id: str,
        block_type: str,
        data_contract: Dict[str, Any],
        block_catalog: Dict[str, Any] = None,
        original_question: str = "",  # Original complex question before decomposition
    ) -> Optional[GenericQuestion]:
        """Convert a specific sub-question into a generic template."""

        # Get block definition from catalog
        block_def = {}
        if block_catalog:
            for category, blocks in block_catalog.get("categories", {}).items():
                for block in blocks:
                    if block.get("id") == block_id:
                        # Include full block definition for comprehensive context
                        block_def = {
                            "id": block.get("id"),
                            "category": category,
                            "bestFor": block.get("bestFor", []),
                            "avoidWhen": block.get("avoidWhen", ""),
                            "dataShape": block.get("dataShape", ""),
                            "requiredProps": block.get("requiredProps", {}),
                            "formatterHint": block.get("formatterHint", ""),
                        }
                        break

        # Call LLM if available
        if self.llm_service:
            try:
                # Use system_prompt parameter for LLM service, user message for actual request
                system_prompt = GENERIC_QUESTION_PROMPT.split("## YOUR TASK")[0].strip()
                user_message = f"""Specific Question: {sub_question}
Block Type: {block_type}
Block Definition:
{json.dumps(block_def, indent=2)}
Block Contract: {json.dumps(data_contract, indent=2)}"""

                response = await self.llm_service.make_request(
                    messages=[{"role": "user", "content": user_message}],
                    system_prompt=system_prompt,
                    max_tokens=500,
                    temperature=0.1,
                )
                content = response.get("content", "")
                logger.debug(f"LLM response: {content[:500]}")

                json_start = content.find("{")
                json_end = content.rfind("}") + 1
                if json_start >= 0 and json_end > json_start:
                    data = json.loads(content[json_start:json_end])
                    logger.info(f"Genericized: intent={data.get('intent')}, metrics={data.get('metrics_included')}")
                    return GenericQuestion(
                        template=data.get("template", ""),
                        params=data.get("params", []),
                        block_type=block_type,
                        output_shape=data.get("output_shape", ""),
                        block_contract=data_contract,
                        intent=data.get("intent", ""),
                        metrics_included=data.get("metrics_included", []),
                        discovered_from=sub_question,
                        original_question=original_question,
                        block_id=block_id,
                        first_seen=datetime.now().isoformat(),
                        last_seen=datetime.now().isoformat(),
                    )
            except Exception as e:
                logger.warning(f"LLM genericization failed: {e}")

        # Fallback: heuristic genericization
        return self._heuristic_genericize(sub_question, block_type, data_contract, original_question, block_id)

    def _heuristic_genericize(
        self,
        sub_question: str,
        block_type: str,
        data_contract: Dict[str, Any],
        original_question: str = "",
        block_id: str = "",
    ) -> GenericQuestion:
        """Simple heuristic genericization without LLM."""
        import re

        # Known tickers
        known_tickers = {
            "QQQ", "SPY", "VOO", "VTI", "IWM", "DIA", "GLD", "TLT", "EEM",
            "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "AMD",
            "JPM", "BAC", "WFC", "GS", "V", "MA", "JNJ", "UNH", "PFE",
            "WMT", "COST", "HD", "NKE", "XOM", "CVX", "COIN",
        }

        template = sub_question
        params = []

        # Extract tickers
        ticker_pattern = r'\b([A-Z]{2,5})\b'
        tickers = list(set(re.findall(ticker_pattern, sub_question)))
        tickers = [t for t in tickers if t in known_tickers]

        if len(tickers) == 1:
            template = template.replace(tickers[0], "{{ticker}}")
            params.append("ticker")
        elif len(tickers) >= 2:
            for i, ticker in enumerate(tickers[:2]):
                template = template.replace(ticker, f"{{{{ticker{i+1}}}}}", 1)
            params.extend(["ticker1", "ticker2"])

        return GenericQuestion(
            template=template,
            params=params,
            block_type=block_type,
            output_shape=f"data for {block_type}",
            block_contract=data_contract,
            discovered_from=sub_question,
            original_question=original_question,
            block_id=block_id,
            first_seen=datetime.now().isoformat(),
            last_seen=datetime.now().isoformat(),
        )


# =============================================================================
# Cache Simulator
# =============================================================================

class CacheSimulator:
    """Simulates the generic question cache and tracks hit rates."""

    def __init__(self):
        self.cache: Dict[str, GenericQuestion] = {}
        self.stats = CacheStats()
        self.block_type_coverage: Dict[str, int] = defaultdict(int)

    def lookup(self, generic_q: GenericQuestion) -> bool:
        """Check if this generic question is in cache. Returns True if HIT."""
        key = generic_q.generic_key

        if key in self.cache:
            self.stats.cache_hits += 1
            self.cache[key].hit_count += 1
            self.cache[key].last_seen = datetime.now().isoformat()
            return True
        else:
            self.stats.cache_misses += 1
            generic_q.hit_count = 1
            self.cache[key] = generic_q
            self.stats.unique_generic_questions = len(self.cache)
            self.block_type_coverage[generic_q.block_type] += 1
            return False

    def get_hit_rate(self) -> float:
        return self.stats.hit_rate

    def get_coverage_report(self) -> Dict[str, Any]:
        """Generate a coverage report."""
        return {
            "stats": asdict(self.stats),
            "hit_rate": f"{self.stats.hit_rate:.1%}",
            "block_type_coverage": dict(self.block_type_coverage),
            "top_generic_questions": [
                {
                    "template": q.template,
                    "block_type": q.block_type,
                    "hit_count": q.hit_count,
                    "original_question": q.original_question,
                    "sub_question": q.discovered_from,
                }
                for q in sorted(self.cache.values(), key=lambda x: x.hit_count, reverse=True)[:20]
            ],
            "all_generic_questions": [
                {
                    "template": q.template,
                    "params": q.params,
                    "block_type": q.block_type,
                    "generic_key": q.generic_key,
                    "output_shape": q.output_shape,
                    "original_question": q.original_question,
                    "sub_question": q.discovered_from,
                    "block_id": q.block_id,
                    "hit_count": q.hit_count,
                }
                for q in self.cache.values()
            ],
            # Group by original question to show decomposition
            "decompositions": self._get_decompositions(),
        }

    def _get_decompositions(self) -> List[Dict[str, Any]]:
        """Group generic questions by original question to show decomposition."""
        from collections import defaultdict

        # Group by original question
        groups = defaultdict(list)
        for q in self.cache.values():
            if q.original_question:
                groups[q.original_question].append({
                    "sub_question": q.discovered_from,
                    "block_type": q.block_type,
                    "block_id": q.block_id,
                    "generic_template": q.template,
                    "hit_count": q.hit_count,
                })

        # Convert to list, sorted by max hit count
        return [
            {
                "original_question": orig_q,
                "block_count": len(blocks),
                "blocks": blocks,
            }
            for orig_q, blocks in sorted(groups.items(), key=lambda x: -max(b["hit_count"] for b in x[1]))
        ]


# =============================================================================
# Block Catalog Loader
# =============================================================================

def load_block_catalog() -> Dict[str, Any]:
    """Load the block catalog with data contracts."""
    catalog_path = os.path.normpath(os.path.join(
        _DIR, "..", "..", "..",
        "frontend", "apps", "base-ui", "src", "blocks", "BLOCK_CATALOG.json"
    ))

    try:
        with open(catalog_path) as f:
            return json.load(f)
    except FileNotFoundError:
        logger.warning(f"Block catalog not found at {catalog_path}")
        return {"categories": {}}


# =============================================================================
# Main Pipeline
# =============================================================================

class HydratePipeline:
    """Main pipeline for cache hydration."""

    def __init__(
        self,
        ui_planner=None,
        llm_service=None,
        question_generator=None,
        target_hit_rate: float = 0.95,
        max_iterations: int = 1000,
    ):
        self.ui_planner = ui_planner
        self.question_generator = question_generator or QuestionGenerator(llm_service=llm_service)
        self.generic_generator = GenericQuestionGenerator(llm_service=llm_service)
        self.cache = CacheSimulator()
        self.target_hit_rate = target_hit_rate
        self.max_iterations = max_iterations
        self._question_cache: List[str] = []
        self.block_catalog = load_block_catalog()

    async def warm_question_cache(self, count: int = 500) -> None:
        """Pre-generate questions for testing."""
        logger.info(f"Warming question cache with {count} questions...")
        self._question_cache = await self.question_generator.generate_batch(count)
        logger.info(f"Cached {len(self._question_cache)} questions")

    async def run_iteration(self, question: str) -> Dict[str, Any]:
        """Run one iteration of the pipeline."""
        result = {
            "question": question,
            "blocks": [],
            "generic_questions": [],
            "cache_results": [],
        }

        # Step 1: Get UIPlanner response (or mock)
        if self.ui_planner:
            try:
                plan = await self.ui_planner.plan(question)
                blocks = plan.get("blocks", [])
            except Exception as e:
                logger.warning(f"UIPlanner failed: {e}")
                blocks = self._mock_blocks(question)
        else:
            blocks = self._mock_blocks(question)

        result["blocks"] = [b.get("blockId") for b in blocks]
        self.cache.stats.total_questions += 1
        self.cache.stats.total_blocks += len(blocks)

        # Track the decomposition mapping
        result["decomposition"] = {
            "original_question": question,
            "block_count": len(blocks),
            "sub_questions": [],
        }

        # Step 2: Genericize each block's sub-question
        for block in blocks:
            generic_q = await self.generic_generator.genericize(
                sub_question=block.get("sub_question", ""),
                block_id=block.get("blockId", ""),
                block_type=block.get("category", "unknown"),
                data_contract=block.get("dataContract", {}),
                block_catalog=self.block_catalog,
                original_question=question,  # Pass original question
            )

            if generic_q:
                # Track the decomposition
                result["decomposition"]["sub_questions"].append({
                    "block_id": block.get("blockId"),
                    "block_type": block.get("category"),
                    "sub_question": block.get("sub_question"),
                    "generic_template": generic_q.template,
                })

                result["generic_questions"].append(generic_q.template)
                is_hit = self.cache.lookup(generic_q)
                result["cache_results"].append({
                    "block": block.get("blockId"),
                    "generic_template": generic_q.template,
                    "cache_hit": is_hit,
                })

        return result

    def _mock_blocks(self, question: str) -> List[Dict]:
        """Generate mock blocks for testing without UIPlanner."""
        import re

        known_tickers = {
            "QQQ", "SPY", "VOO", "VTI", "IWM", "DIA", "GLD", "TLT",
            "AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA",
        }

        ticker_pattern = r'\b([A-Z]{2,5})\b'
        tickers = re.findall(ticker_pattern, question)
        tickers = [t for t in tickers if t in known_tickers]

        blocks = []

        if "compare" in question.lower():
            blocks.append({
                "blockId": "comparison-chart-01",
                "category": "comparison-chart",
                "sub_question": question,
                "dataContract": {"type": "comparison", "series": 2},
            })
        elif "trend" in question.lower() or "over" in question.lower() or "history" in question.lower():
            blocks.append({
                "blockId": "line-chart-01",
                "category": "line-chart",
                "sub_question": question,
                "dataContract": {"type": "timeseries"},
            })
        elif "holding" in question.lower() or "top" in question.lower():
            blocks.append({
                "blockId": "table-01",
                "category": "table",
                "sub_question": question,
                "dataContract": {"type": "table", "columns": 4},
            })
        else:
            blocks.append({
                "blockId": "kpi-cards-01",
                "category": "kpi-cards",
                "sub_question": question,
                "dataContract": {"type": "kpi", "points": 4},
            })

        return blocks

    async def run(self, verbose: bool = True, warm_cache_size: int = 500) -> Dict[str, Any]:
        """Run the pipeline until target hit rate or max iterations."""
        logger.info(f"Starting cache hydration pipeline")
        logger.info(f"Target hit rate: {self.target_hit_rate:.0%}")
        logger.info(f"Max iterations: {self.max_iterations}")

        # Warm the question cache
        if warm_cache_size > 0:
            await self.warm_question_cache(warm_cache_size)

        iteration = 0
        results = []

        while iteration < self.max_iterations:
            iteration += 1

            # Get question from cache or generate more
            if self._question_cache:
                question = self._question_cache.pop(0)
            else:
                new_questions = await self.question_generator.generate_batch(50)
                self._question_cache.extend(new_questions)
                question = self._question_cache.pop(0)

            # Process question
            result = await self.run_iteration(question)
            results.append(result)

            if verbose and iteration % 50 == 0:
                logger.info(
                    f"Iteration {iteration}: "
                    f"hit_rate={self.cache.get_hit_rate():.1%}, "
                    f"unique={self.cache.stats.unique_generic_questions}, "
                    f"remaining={len(self._question_cache)}"
                )

            # Check if target reached
            if self.cache.get_hit_rate() >= self.target_hit_rate and iteration >= 100:
                logger.info(f"Target hit rate reached at iteration {iteration}!")
                break

            # Stop if cache exhausted
            if not self._question_cache and iteration >= 100:
                logger.info(f"Question cache exhausted at iteration {iteration}")
                break

        # Generate report
        report = self.cache.get_coverage_report()
        report["total_iterations"] = iteration
        report["target_reached"] = self.cache.get_hit_rate() >= self.target_hit_rate
        report["questions_remaining"] = len(self._question_cache)

        return report


# =============================================================================
# CLI Entry Point
# =============================================================================

async def main():
    parser = argparse.ArgumentParser(
        description="Cache Hydration Pipeline - Discover and warm generic question templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick test without LLM (uses fallback questions)
  python hydrate_pipeline.py --max-iterations 500

  # With LLM for realistic question generation
  python hydrate_pipeline.py --use-llm --warm-cache 500

  # Full pipeline with UIPlanner
  python hydrate_pipeline.py --use-planner --use-llm --max-iterations 1000

  # Run until 95% hit rate
  python hydrate_pipeline.py --target 0.95 --max-iterations 5000
        """,
    )
    parser.add_argument("--target", type=float, default=0.95,
                        help="Target cache hit rate (default: 0.95)")
    parser.add_argument("--max-iterations", type=int, default=1000,
                        help="Maximum iterations (default: 1000)")
    parser.add_argument("--warm-cache", type=int, default=500,
                        help="Number of questions to pre-generate (default: 500)")
    parser.add_argument("--use-planner", action="store_true",
                        help="Use real UIPlanner (requires LLM)")
    parser.add_argument("--use-llm", action="store_true",
                        help="Use LLM for question generation")
    parser.add_argument("--output", type=str, default=None,
                        help="Output file for report")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Verbose output")
    args = parser.parse_args()

    # Initialize services
    ui_planner = None
    llm_service = None

    if args.use_llm:
        from shared.llm import create_llm_service
        llm_service = create_llm_service(task="generic")
        logger.info("LLM service initialized")

    if args.use_planner:
        from shared.services.ui_planner import create_ui_planner
        ui_planner = create_ui_planner(llm_service=llm_service)
        logger.info("UIPlanner initialized")

    # Create pipeline
    pipeline = HydratePipeline(
        ui_planner=ui_planner,
        llm_service=llm_service,
        target_hit_rate=args.target,
        max_iterations=args.max_iterations,
    )

    # Run
    logger.info("=" * 60)
    logger.info("CACHE HYDRATION PIPELINE")
    logger.info("=" * 60)

    report = await pipeline.run(verbose=args.verbose, warm_cache_size=args.warm_cache)

    # Save report
    os.makedirs(_OUTPUT, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = args.output or os.path.join(_OUTPUT, f"hydrate_{timestamp}.json")

    with open(output_file, "w") as f:
        json.dump(report, f, indent=2, default=str)

    # Print summary
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(f"Total Questions: {report['stats']['total_questions']}")
    print(f"Total Blocks: {report['stats']['total_blocks']}")
    print(f"Cache Hits: {report['stats']['cache_hits']}")
    print(f"Cache Misses: {report['stats']['cache_misses']}")
    print(f"Hit Rate: {report['hit_rate']}")
    print(f"Unique Generic Questions: {report['stats']['unique_generic_questions']}")
    print(f"Target Reached: {report['target_reached']}")
    print(f"\nReport saved to: {output_file}")

    print("\n" + "-" * 60)
    print("TOP GENERIC QUESTIONS BY HIT COUNT")
    print("-" * 60)
    for i, q in enumerate(report['top_generic_questions'][:10], 1):
        print(f"{i}. [{q['block_type']:15}] {q['template'][:60]}")
        print(f"   Hits: {q['hit_count']}")

    print("\n" + "-" * 60)
    print("COVERAGE BY BLOCK TYPE")
    print("-" * 60)
    for block_type, count in sorted(report['block_type_coverage'].items(), key=lambda x: -x[1]):
        print(f"  {block_type}: {count}")


if __name__ == "__main__":
    asyncio.run(main())