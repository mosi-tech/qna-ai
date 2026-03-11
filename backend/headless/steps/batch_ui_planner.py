#!/usr/bin/env python3
"""Run UI Planner for first N dashboards in batch mode."""
import json
import asyncio
from pathlib import Path
from datetime import datetime
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from headless.agents.ui_planner_agent import UIPlannerAgent
from backend.shared.config.settings import get_settings
from backend.shared.config.constants import CACHE_DIR

async def run_batch(n_dashboards: int = 10):
    """Run UI Planner for first N dashboards."""
    settings = get_settings()
    checkpoint_file = Path(settings.QUESTIONS_DIR) / "sub_questions_ui_planner_system_checkpoint_100.json"

    # Load checkpoint
    with open(checkpoint_file) as f:
        dashboards = json.load(f)

    # Get first N dashboards
    dashboards_to_process = dashboards[:n_dashboards]

    print(f"Processing {len(dashboards_to_process)} dashboards...")
    print(f"Total sub-questions: {sum(len(d['blocks'][0]['sub_questions']) for d in dashboards_to_process)}")

    results = []
    start_time = datetime.now()

    for i, dashboard in enumerate(dashboards_to_process, 1):
        print(f"\n[{i}/{len(dashboards_to_process)}] {dashboard['question']}")

        try:
            agent = UIPlannerAgent(
                model=settings.ANTHROPIC_MODEL,
                timeout_seconds=300,
                cache_dir=str(CACHE_DIR)
            )

            # Extract original question from first block
            question = dashboard['question']
            blocks = dashboard['blocks']

            # Build context from other blocks
            context = "\n\n".join([
                f"Block {j+1}: {b['title']}\nSub-questions:\n" +
                "\n".join([f"  - {sq}" for sq in b['sub_questions']])
                for j, b in enumerate(blocks[1:], 1)
            ])

            result = await agent.run(
                question=question,
                context=context if context else None
            )

            elapsed = (datetime.now() - start_time).total_seconds()
            results.append({
                "question": question,
                "status": "success",
                "time": elapsed
            })

            print(f"  ✓ Success ({elapsed:.1f}s total)")

        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            results.append({
                "question": question,
                "status": "error",
                "error": str(e),
                "time": elapsed
            })
            print(f"  ✗ Error: {e}")

    # Summary
    total_time = (datetime.now() - start_time).total_seconds()
    success = sum(1 for r in results if r["status"] == "success")
    print(f"\n{'='*60}")
    print(f"Complete! {success}/{len(results)} successful")
    print(f"Total time: {total_time:.1f}s ({total_time/60:.1f}m)")
    print(f"Avg per dashboard: {total_time/len(results):.1f}s")

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    asyncio.run(run_batch(n))