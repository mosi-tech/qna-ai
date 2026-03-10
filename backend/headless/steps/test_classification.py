#!/usr/bin/env python3
"""
test_classification.py — Test Question Classification Coverage

Purpose: Test how questions are routed through the new architecture.
         Validates that LLM classifier correctly identifies MCP functions.

Usage:
    python test_classification.py
    python test_classification.py --sample 50
    python test_classification.py --questions-file path/to/questions.json
"""

import asyncio
import sys
import os
import argparse
import json
from datetime import datetime
from typing import Dict, Any, List
from collections import Counter, defaultdict

# Add backend to path
_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_DIR, "..", ".."))

from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(_DIR), "..", "..", "apiServer", ".env"))

from step3_cache_enhanced import QuestionClassifier


class ClassificationTester:
    """Tester for question classification coverage"""

    def __init__(self):
        self.classifier = QuestionClassifier()

    def load_questions(self, questions_file: str = None, sample_size: int = None):
        """Load questions from consolidated questions file"""
        default_path = os.path.join(_DIR, "..", "..", "..", "..",
                                     "all-questions", "consolidated_questions.json")

        if questions_file:
            path = questions_file
        else:
            path = default_path

        with open(path, "r") as f:
            data = json.load(f)

        # Extract questions from various formats
        questions = []

        if "consolidated_questions" in data:
            questions.extend(data["consolidated_questions"])
        elif "valid_questions" in data:
            questions.extend(data["valid_questions"])
        elif isinstance(data, list):
            questions.extend(data)

        # Clean up questions
        cleaned_questions = []
        for q in questions:
            if isinstance(q, str):
                cleaned_questions.append({"question": q})
            elif isinstance(q, dict):
                if "question" in q:
                    cleaned_questions.append(q)
                elif "sub_question" in q:
                    cleaned_questions.append({"question": q["sub_question"]})
                elif "q" in q:
                    cleaned_questions.append({"question": q["q"]})

        # Sample if needed
        if sample_size and sample_size < len(cleaned_questions):
            import random
            random.seed(42)  # For reproducibility
            cleaned_questions = random.sample(cleaned_questions, sample_size)

        return cleaned_questions

    def test_classification(self, questions: List[Dict]) -> Dict[str, Any]:
        """Test classification on all questions"""
        results = []

        for i, q in enumerate(questions):
            question_text = q.get("question", "")
            if not question_text:
                continue

            classification = self.classifier.classify(question_text)

            results.append({
                "index": i,
                "question": question_text,
                "path": classification["path"],
                "target": classification["target"],
                "mcp_server": classification.get("mcp_server"),
                "confidence": classification["confidence"],
                "params": classification.get("params", {}),
                "route_to": classification["route_to"],
                "reasoning": classification["reasoning"]
            })

        return results

    def analyze_results(self, results: List[Dict]) -> Dict[str, Any]:
        """Analyze classification results"""
        total = len(results)

        # Count by path
        path_counts = Counter(r["path"] for r in results)
        route_counts = Counter(r["route_to"] for r in results)

        # Count by MCP function
        mcp_function_counts = defaultdict(int)
        mcp_server_counts = defaultdict(int)
        for r in results:
            if r["target"] and r["path"] == "direct_mcp":
                mcp_function_counts[r["target"]] += 1
            if r["mcp_server"]:
                mcp_server_counts[r["mcp_server"]] += 1

        # Confidence distribution
        confidences = [r["confidence"] for r in results]
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0

        # Find examples of each path
        examples_by_path = defaultdict(list)
        for r in results:
            examples_by_path[r["path"]].append(r["question"][:100] + "...")

        return {
            "total_questions": total,
            "by_path": dict(path_counts),
            "by_route": dict(route_counts),
            "by_mcp_function": dict(mcp_function_counts),
            "by_mcp_server": dict(mcp_server_counts),
            "average_confidence": avg_confidence,
            "confidence_distribution": {
                "high (>0.8)": len([c for c in confidences if c > 0.8]),
                "medium (0.5-0.8)": len([c for c in confidences if 0.5 <= c <= 0.8]),
                "low (<0.5)": len([c for c in confidences if c < 0.5])
            },
            "examples_by_path": {k: v[:5] for k, v in examples_by_path.items()}
        }

    def generate_report(self, results: List[Dict], analysis: Dict, output_file: str = None):
        """Generate a human-readable report"""
        report = []
        report.append("=" * 80)
        report.append("QUESTION CLASSIFICATION TEST REPORT")
        report.append("=" * 80)
        report.append(f"Timestamp: {datetime.now().isoformat()}")
        report.append("")

        # Summary
        report.append("## Summary")
        report.append(f"Total questions tested: {analysis['total_questions']}")
        report.append(f"Average confidence: {analysis['average_confidence']:.2f}")
        report.append("")

        # Coverage by path
        report.append("## Coverage by Path")
        total = analysis['total_questions']
        for path, count in sorted(analysis['by_path'].items(),
                                   key=lambda x: -x[1]):
            percentage = (count / total * 100) if total > 0 else 0
            report.append(f"  {path}: {count} ({percentage:.1f}%)")
        report.append("")

        # Coverage by route
        report.append("## Coverage by Route")
        for route, count in sorted(analysis['by_route'].items(),
                                   key=lambda x: -x[1]):
            percentage = (count / total * 100) if total > 0 else 0
            report.append(f"  {route}: {count} ({percentage:.1f}%)")
        report.append("")

        # Top MCP functions
        report.append("## Top MCP Functions (Direct Path)")
        top_functions = sorted(analysis['by_mcp_function'].items(),
                              key=lambda x: -x[1])[:10]
        for func, count in top_functions:
            percentage = (count / total * 100) if total > 0 else 0
            report.append(f"  {func}: {count} ({percentage:.1f}%)")
        report.append("")

        # MCP server distribution
        report.append("## MCP Server Distribution")
        for server, count in sorted(analysis['by_mcp_server'].items(),
                                   key=lambda x: -x[1]):
            percentage = (count / total * 100) if total > 0 else 0
            report.append(f"  {server}: {count} ({percentage:.1f}%)")
        report.append("")

        # Confidence distribution
        report.append("## Confidence Distribution")
        for level, count in analysis['confidence_distribution'].items():
            percentage = (count / total * 100) if total > 0 else 0
            report.append(f"  {level}: {count} ({percentage:.1f}%)")
        report.append("")

        # Examples
        report.append("## Example Questions by Path")
        for path, examples in analysis['examples_by_path'].items():
            report.append(f"\n### {path}")
            for i, ex in enumerate(examples, 1):
                report.append(f"  {i}. {ex}")
        report.append("")

        report.append("=" * 80)

        report_text = "\n".join(report)
        print(report_text)

        if output_file:
            with open(output_file, "w") as f:
                f.write(report_text)
            print(f"\nReport saved to: {output_file}", file=sys.stderr)

        # Also save JSON
        json_file = output_file.replace(".txt", ".json") if output_file else None
        if json_file:
            with open(json_file, "w") as f:
                json.dump({
                    "results": results,
                    "analysis": analysis,
                    "timestamp": datetime.now().isoformat()
                }, f, indent=2)
            print(f"JSON results saved to: {json_file}", file=sys.stderr)

        return report_text


def save_output(results: List[Dict], analysis: Dict, output_dir: str = None):
    """Save test results to output directory"""
    if output_dir is None:
        output_dir = os.path.join(_DIR, "output")

    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_file = os.path.join(output_dir, f"test_classification_{timestamp}.json")

    with open(json_file, "w") as f:
        json.dump({
            "results": results,
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }, f, indent=2)

    print(f"Results saved to: {json_file}", file=sys.stderr)
    return json_file


async def main():
    parser = argparse.ArgumentParser(
        description="Test question classification coverage"
    )
    parser.add_argument("--questions-file", help="Path to questions JSON file")
    parser.add_argument("--sample", type=int, help="Sample N questions randomly")
    parser.add_argument("--output-dir", help="Output directory (default: ./output)")
    parser.add_argument("--output-file", help="Output file path for report")
    parser.add_argument("--json-only", action="store_true", help="Only output JSON, no report text")

    args = parser.parse_args()

    tester = ClassificationTester()

    print("Loading questions...", file=sys.stderr)
    questions = tester.load_questions(args.questions_file, args.sample)
    print(f"Loaded {len(questions)} questions", file=sys.stderr)

    print("Classifying questions...", file=sys.stderr)
    results = tester.test_classification(questions)

    print("Analyzing results...", file=sys.stderr)
    analysis = tester.analyze_results(results)

    if args.json_only:
        save_output(results, analysis, args.output_dir)
    else:
        tester.generate_report(results, analysis, args.output_file)


if __name__ == "__main__":
    asyncio.run(main())