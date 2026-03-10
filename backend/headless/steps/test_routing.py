#!/usr/bin/env python3
"""
test_routing.py — Test question classification and routing

Purpose: Validate that the question classifier correctly routes questions
         to appropriate paths (direct_mcp vs script_generation) and
         measures coverage.

Usage:
    python test_routing.py --questions all-questions/consolidated_questions.json
    python test_routing.py --sample 100
    python test_routing.py --questions all-questions/consolidated_questions.json --output report.json
"""

import asyncio
import sys
import os
import argparse
import json
import time
from datetime import datetime
from typing import Dict, Any, List
from collections import Counter, defaultdict

# Add backend to path
_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _DIR)  # Add current directory first
sys.path.insert(0, os.path.join(_DIR, "..", ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(_DIR), "..", "..", "apiServer", ".env"))

from step3_cache_enhanced import QuestionClassifier, CacheService


class RoutingTest:
    """Test routing decisions for questions"""

    def __init__(self, no_fallback: bool = False):
        self.classifier = QuestionClassifier(no_fallback=no_fallback)
        self.cache = CacheService()

    def load_questions(self, questions_file: str, sample_size: int = None) -> List[str]:
        """Load questions from JSON file"""
        with open(questions_file, "r") as f:
            data = json.load(f)

        # Extract questions from different formats
        questions = []

        if "consolidated_questions" in data:
            questions = [q["question"] for q in data["consolidated_questions"]]

        elif "questions" in data:
            questions = [q if isinstance(q, str) else q.get("question", str(q))
                        for q in data["questions"]]

        elif isinstance(data, list):
            questions = [q if isinstance(q, str) else q.get("question", str(q))
                        for q in data]

        # Sample if requested
        if sample_size and sample_size < len(questions):
            import random
            random.seed(42)
            questions = random.sample(questions, sample_size)

        return questions

    def test_classification(self, questions: List[str]) -> Dict[str, Any]:
        """Test classification for all questions"""
        results = {
            "test_run": {
                "timestamp": datetime.now().isoformat(),
                "total_questions": len(questions),
            },
            "classifications": [],
            "summary": {
                "by_path": Counter(),
                "by_confidence": {
                    "high": 0,      # >= 0.90
                    "medium": 0,    # 0.70-0.89
                    "low": 0       # < 0.70
                },
                "by_function": Counter(),
                "errors": 0
            }
        }

        for i, question in enumerate(questions, 1):
            if i % 100 == 0:
                print(f"Processing {i}/{len(questions)}...")

            try:
                classification = self.classifier.classify(question)

                result = {
                    "question": question,
                    "index": i,
                    "path": classification["path"],
                    "target": classification["target"],
                    "mcp_server": classification.get("mcp_server"),
                    "confidence": classification["confidence"],
                    "params": classification.get("params", {}),
                    "reasoning": classification["reasoning"],
                    "expected_time_ms": classification["expected_time_ms"]
                }

                results["classifications"].append(result)

                # Update summary
                path = classification["path"]
                results["summary"]["by_path"][path] += 1

                confidence = classification["confidence"]
                if confidence >= 0.90:
                    results["summary"]["by_confidence"]["high"] += 1
                elif confidence >= 0.70:
                    results["summary"]["by_confidence"]["medium"] += 1
                else:
                    results["summary"]["by_confidence"]["low"] += 1

                # Track MCP functions
                if classification.get("mcp_server"):
                    results["summary"]["by_function"][classification["target"]] += 1

            except Exception as e:
                results["summary"]["errors"] += 1
                results["classifications"].append({
                    "question": question,
                    "index": i,
                    "error": str(e),
                    "path": "error"
                })

        return results

    def analyze_results(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze test results"""
        summary = results["summary"]

        total = results["test_run"]["total_questions"]
        errors = summary["errors"]

        analysis = {
            "success_rate": ((total - errors) / total * 100) if total > 0 else 0,
            "direct_mcp_coverage": (summary["by_path"]["direct_mcp"] / total * 100) if total > 0 else 0,
            "script_generation_rate": (summary["by_path"]["script_generation"] / total * 100) if total > 0 else 0,
            "average_confidence": 0,
            "fast_path_questions": [],
            "slow_path_questions": [],
            "top_functions": []
        }

        # Calculate average confidence
        confidences = [c["confidence"] for c in results["classifications"] if "confidence" in c]
        if confidences:
            analysis["average_confidence"] = sum(confidences) / len(confidences)

        # Sample questions by path
        for c in results["classifications"]:
            if "error" not in c:
                if c["path"] == "direct_mcp":
                    if len(analysis["fast_path_questions"]) < 10:
                        analysis["fast_path_questions"].append({
                            "question": c["question"],
                            "function": c["target"]
                        })
                elif c["path"] == "script_generation":
                    if len(analysis["slow_path_questions"]) < 10:
                        analysis["slow_path_questions"].append({
                            "question": c["question"],
                            "reasoning": c["reasoning"]
                        })

        # Top functions
        top_functions = summary["by_function"].most_common(10)
        analysis["top_functions"] = [
            {"function": func, "count": count}
            for func, count in top_functions
        ]

        return analysis

    def print_report(self, results: Dict[str, Any], analysis: Dict[str, Any]):
        """Print test report"""
        print("\n" + "=" * 70)
        print("QUESTION ROUTING TEST REPORT")
        print("=" * 70)

        # Test run info
        print(f"\nTest Run:")
        print(f"  Timestamp:  {results['test_run']['timestamp']}")
        print(f"  Questions:  {results['test_run']['total_questions']}")
        print(f"  Errors:     {results['summary']['errors']}")

        # Coverage
        print(f"\nCoverage:")
        print(f"  Direct MCP (fast):      {analysis['direct_mcp_coverage']:.1f}%")
        print(f"  Script Gen (slow):      {analysis['script_generation_rate']:.1f}%")
        print(f"  Success Rate:           {analysis['success_rate']:.1f}%")

        # Confidence
        print(f"\nConfidence Distribution:")
        print(f"  High (≥0.90):   {results['summary']['by_confidence']['high']} ({results['summary']['by_confidence']['high']/results['test_run']['total_questions']*100:.1f}%)")
        print(f"  Medium (0.70-0.89): {results['summary']['by_confidence']['medium']} ({results['summary']['by_confidence']['medium']/results['test_run']['total_questions']*100:.1f}%)")
        print(f"  Low (<0.70):    {results['summary']['by_confidence']['low']} ({results['summary']['by_confidence']['low']/results['test_run']['total_questions']*100:.1f}%)")
        print(f"  Average:        {analysis['average_confidence']:.2f}")

        # Top functions
        if analysis['top_functions']:
            print(f"\nTop Identified MCP Functions:")
            for item in analysis['top_functions']:
                print(f"  {item['function']:30s} {item['count']:5d} times")

        # Sample questions
        if analysis['fast_path_questions']:
            print(f"\nSample Fast Path Questions (Direct MCP):")
            for item in analysis['fast_path_questions']:
                print(f"  - \"{item['question'][:60]}\" → {item['function']}")

        if analysis['slow_path_questions']:
            print(f"\nSample Slow Path Questions (Script Generation):")
            for item in analysis['slow_path_questions']:
                print(f"  - \"{item['question'][:60]}\" → {item['reasoning']}")

        # Performance estimate
        total = results["test_run"]["total_questions"]
        fast_count = results["summary"]["by_path"]["direct_mcp"]
        slow_count = results["summary"]["by_path"]["script_generation"]
        avg_fast_time = 0.3  # seconds
        avg_slow_time = 7.5  # seconds

        estimated_avg_time = ((fast_count * avg_fast_time) + (slow_count * avg_slow_time)) / total if total > 0 else 0

        print(f"\nPerformance Estimate:")
        print(f"  Old (all slow path):       {avg_slow_time:.1f}s per question")
        print(f"  New (mixed paths):        {estimated_avg_time:.1f}s per question")
        if estimated_avg_time > 0:
            print(f"  Speedup:                  {avg_slow_time/estimated_avg_time:.1f}x faster")
            print(f"  Time saved per 100 questions: {(avg_slow_time - estimated_avg_time) * 100:.1f}s")
        else:
            print(f"  Speedup:                  N/A (no successful classifications)")

        print("\n" + "=" * 70)

    def save_report(self, results: Dict[str, Any], analysis: Dict[str, Any],
                   output_file: str = None):
        """Save test report to file"""
        report = {
            "test_run": results["test_run"],
            "results": results,
            "analysis": analysis
        }

        if output_file is None:
            output_dir = os.path.join(_DIR, "output")
            os.makedirs(output_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = os.path.join(output_dir, f"routing_test_{timestamp}.json")

        with open(output_file, "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nReport saved to: {output_file}")
        return output_file


async def main():
    parser = argparse.ArgumentParser(
        description="Test question classification and routing"
    )
    parser.add_argument("--questions", help="Path to questions JSON file")
    parser.add_argument("--sample", type=int, help="Sample N questions randomly")
    parser.add_argument("--output", help="Output report file")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--no-fallback", action="store_true", help="Fail if LLM initialization fails (no regex fallback)")

    args = parser.parse_args()

    if not args.questions:
        # Default to consolidated questions
        args.questions = os.path.join(_DIR, "..", "..", "..", "..", "all-questions", "consolidated_questions.json")

    if not os.path.exists(args.questions):
        print(f"Error: Questions file not found: {args.questions}")
        sys.exit(1)

    tester = RoutingTest(no_fallback=args.no_fallback)

    print(f"Loading questions from: {args.questions}")
    questions = tester.load_questions(args.questions, args.sample)
    print(f"Loaded {len(questions)} questions")

    start_time = time.time()

    print("\nClassifying questions...")
    results = tester.test_classification(questions)

    end_time = time.time()

    print(f"\nAnalyzing results...")
    analysis = tester.analyze_results(results)

    print(f"\nTest completed in {end_time - start_time:.2f}s")

    tester.print_report(results, analysis)
    tester.save_report(results, analysis, args.output)

    sys.exit(0)


if __name__ == "__main__":
    asyncio.run(main())