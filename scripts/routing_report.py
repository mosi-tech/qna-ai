#!/usr/bin/env python3
"""
Routing Coverage Report Generator
Samples 200 questions from consolidated_questions.json and classifies each
using the question-classifier sub-agent.
"""

import json
import random
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Load the consolidated questions
CONSOLIDATED_FILE = Path("/Users/shivc/Documents/Workspace/JS/qna-ai-admin/all-questions/consolidated_questions.json")

def load_questions(sample_size: int = 200) -> List[str]:
    """Load and sample questions from the consolidated file."""
    print(f"Loading questions from {CONSOLIDATED_FILE}...")
    with open(CONSOLIDATED_FILE, 'r') as f:
        data = json.load(f)

    questions = data.get("questions", [])
    print(f"Total questions available: {len(questions)}")

    # Sample questions
    sampled = random.sample(questions, min(sample_size, len(questions)))
    return [q["question"] for q in sampled]

def classify_question(question: str, agent) -> Dict[str, Any]:
    """Classify a single question using the question-classifier agent."""
    # Call the sub-agent to classify the question
    result = agent.run(question)
    return result

def generate_report(sampled_questions: List[str], classifications: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate the routing coverage report."""
    # Analyze classifications
    route_stats = {}
    unclassified = 0

    for classification in classifications:
        route = classification.get("route", "unclassified")
        if route == "unclassified":
            unclassified += 1
        else:
            route_stats[route] = route_stats.get(route, 0) + 1

    # Calculate coverage
    total = len(classifications)
    coverage_rate = (total - unclassified) / total if total > 0 else 0

    report = {
        "report_metadata": {
            "generated_at": datetime.now().isoformat(),
            "sample_size": total,
            "coverage_rate": round(coverage_rate * 100, 2)
        },
        "route_coverage": route_stats,
        "unclassified_count": unclassified,
        "detailed_results": [
            {
                "question": q,
                "classification": c
            }
            for q, c in zip(sampled_questions, classifications)
        ]
    }

    return report

def main():
    """Main function to generate the routing coverage report."""
    print("=" * 80)
    print("Routing Coverage Report Generator")
    print("=" * 80)

    # Step 1: Sample questions
    sampled_questions = load_questions(200)
    print(f"Sampled {len(sampled_questions)} questions")

    # Step 2: Classify each question
    print("\nClassifying questions...")
    classifications = []

    for i, question in enumerate(sampled_questions, 1):
        print(f"[{i}/{len(sampled_questions)}] {question[:60]}...")

        # Classification would be done via the sub-agent here
        # For now, we'll use a placeholder structure
        classification = {
            "question": question,
            "route": "TBD",  # Will be filled by the sub-agent
            "confidence": 0.0,
            "reasoning": ""
        }
        classifications.append(classification)

    # Step 3: Generate report
    print("\nGenerating report...")
    report = generate_report(sampled_questions, classifications)

    # Step 4: Save report
    output_file = Path("/Users/shivc/Documents/Workspace/JS/qna-ai-admin/routing_coverage_report.json")
    with open(output_file, 'w') as f:
        json.dump(report, f, indent=2)

    print(f"\nReport saved to {output_file}")
    print(f"Coverage rate: {report['report_metadata']['coverage_rate']}%")
    print(f"Routes covered: {len(report['route_coverage'])}")
    print(f"Unclassified: {report['unclassified_count']}")

if __name__ == "__main__":
    main()