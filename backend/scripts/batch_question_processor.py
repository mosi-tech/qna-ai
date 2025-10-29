#!/usr/bin/env python3
"""
Batch Question Processor

This script processes all questions from the questions-list directory (1-634)
and makes curl requests to the analyze endpoint to generate scripts for each question.

Usage:
    python batch_question_processor.py [OPTIONS]

Options:
    --start NUM     Start question number (default: 1)
    --end NUM       End question number (default: 634)
    --server URL    Server URL (default: http://localhost:8010)
    --delay SECS    Delay between requests in seconds (default: 2)
    --parallel NUM  Number of parallel requests (default: 1)
    --output-dir    Directory to save results (default: ./batch_results)
    --resume        Resume from last processed question
    --dry-run       Show what would be processed without making requests
"""

import argparse
import asyncio
import aiohttp
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import uuid

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('batch_processor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class BatchQuestionProcessor:
    """Processes questions in batch mode with parallel execution and resume capability"""
    
    def __init__(self, 
                 server_url: str = "http://localhost:8010",
                 delay: float = 2.0,
                 parallel: int = 1,
                 output_dir: str = "./batch_results"):
        self.server_url = server_url
        self.delay = delay
        self.parallel = parallel
        self.output_dir = Path(output_dir)
        self.session_id = str(uuid.uuid4())
        
        # Create output directories
        self.output_dir.mkdir(exist_ok=True)
        self.results_dir = self.output_dir / "results"
        self.results_dir.mkdir(exist_ok=True)
        self.logs_dir = self.output_dir / "logs"
        self.logs_dir.mkdir(exist_ok=True)
        
        # Progress tracking
        self.progress_file = self.output_dir / "progress.json"
        self.stats = {
            "total": 0,
            "processed": 0,
            "successful": 0,
            "failed": 0,
            "start_time": None,
            "last_processed": 0
        }
        
    def load_progress(self) -> Dict:
        """Load progress from previous run"""
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Could not load progress: {e}")
        return {}
        
    def save_progress(self):
        """Save current progress"""
        try:
            with open(self.progress_file, 'w') as f:
                json.dump(self.stats, f, indent=2)
        except Exception as e:
            logger.error(f"Could not save progress: {e}")
            
    def get_questions_list(self, start: int, end: int) -> List[Dict]:
        """Get list of questions to process"""
        questions = []
        questions_dir = Path(__file__).parent.parent.parent / "all-questions" / "questions-list"
        
        if not questions_dir.exists():
            raise FileNotFoundError(f"Questions directory not found: {questions_dir}")
            
        for num in range(start, end + 1):
            question_file = questions_dir / f"{num}.txt"
            if question_file.exists():
                try:
                    with open(question_file, 'r', encoding='utf-8') as f:
                        question_text = f.read().strip()
                    questions.append({
                        "number": num,
                        "text": question_text,
                        "file": str(question_file)
                    })
                except Exception as e:
                    logger.error(f"Error reading question {num}: {e}")
            else:
                logger.warning(f"Question file not found: {question_file}")
                
        return questions
        
    async def process_single_question(self, session: aiohttp.ClientSession, question: Dict) -> Dict:
        """Process a single question"""
        start_time = time.time()
        num = question["number"]
        text = question["text"]
        
        logger.info(f"Processing question {num}: {text[:100]}...")
        
        # Prepare request
        payload = {
            "question": text,
            "session_id": self.session_id,
            "enable_caching": False  # Disable caching for batch processing
        }
        
        result = {
            "question_number": num,
            "question_text": text,
            "success": False,
            "response": None,
            "error": None,
            "duration": 0,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            async with session.post(
                f"{self.server_url}/analyze",
                json=payload,
                timeout=aiohttp.ClientTimeout(total=300)  # 5 minute timeout
            ) as response:
                result["duration"] = time.time() - start_time
                
                if response.status == 200:
                    response_data = await response.json()
                    result["success"] = True
                    result["response"] = response_data
                    
                    # Save individual result
                    result_file = self.results_dir / f"question_{num:03d}_result.json"
                    with open(result_file, 'w', encoding='utf-8') as f:
                        json.dump(result, f, indent=2)
                        
                    logger.info(f"✅ Question {num} completed successfully in {result['duration']:.1f}s")
                    self.stats["successful"] += 1
                    
                else:
                    error_text = await response.text()
                    result["error"] = f"HTTP {response.status}: {error_text}"
                    logger.error(f"❌ Question {num} failed: {result['error']}")
                    self.stats["failed"] += 1
                    
        except asyncio.TimeoutError:
            result["duration"] = time.time() - start_time
            result["error"] = "Request timeout (300s)"
            logger.error(f"⏰ Question {num} timed out")
            self.stats["failed"] += 1
            
        except Exception as e:
            result["duration"] = time.time() - start_time
            result["error"] = str(e)
            logger.error(f"❌ Question {num} error: {e}")
            self.stats["failed"] += 1
            
        # Save error cases too
        if not result["success"]:
            error_file = self.logs_dir / f"question_{num:03d}_error.json"
            with open(error_file, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=2)
                
        self.stats["processed"] += 1
        self.stats["last_processed"] = num
        
        # Save progress periodically
        if self.stats["processed"] % 10 == 0:
            self.save_progress()
            
        return result
        
    async def process_batch(self, questions: List[Dict], dry_run: bool = False):
        """Process questions in parallel batches"""
        self.stats["total"] = len(questions)
        self.stats["start_time"] = datetime.now().isoformat()
        
        if dry_run:
            logger.info(f"🔍 DRY RUN: Would process {len(questions)} questions")
            for q in questions[:5]:  # Show first 5
                logger.info(f"  - Question {q['number']}: {q['text'][:80]}...")
            if len(questions) > 5:
                logger.info(f"  ... and {len(questions) - 5} more questions")
            return
            
        logger.info(f"🚀 Starting batch processing of {len(questions)} questions")
        logger.info(f"📊 Parallel requests: {self.parallel}, Delay: {self.delay}s")
        logger.info(f"💾 Results will be saved to: {self.output_dir}")
        
        # Create session with appropriate connection limits
        connector = aiohttp.TCPConnector(limit=self.parallel * 2)
        async with aiohttp.ClientSession(connector=connector) as session:
            
            # Process in chunks of parallel size
            for i in range(0, len(questions), self.parallel):
                chunk = questions[i:i + self.parallel]
                
                # Process chunk in parallel
                tasks = [self.process_single_question(session, q) for q in chunk]
                results = await asyncio.gather(*tasks, return_exceptions=True)
                
                # Log progress
                progress_pct = (self.stats["processed"] / self.stats["total"]) * 100
                logger.info(f"📈 Progress: {self.stats['processed']}/{self.stats['total']} ({progress_pct:.1f}%) - ✅ {self.stats['successful']} success, ❌ {self.stats['failed']} failed")
                
                # Add delay between chunks (except for last chunk)
                if i + self.parallel < len(questions) and self.delay > 0:
                    await asyncio.sleep(self.delay)
                    
        # Final progress save
        self.save_progress()
        
        # Summary
        duration = time.time() - time.mktime(datetime.fromisoformat(self.stats["start_time"]).timetuple())
        logger.info(f"🏁 Batch processing completed!")
        logger.info(f"📊 Total: {self.stats['total']}, Successful: {self.stats['successful']}, Failed: {self.stats['failed']}")
        logger.info(f"⏱️  Duration: {duration:.1f}s ({duration/60:.1f} minutes)")
        logger.info(f"💾 Results saved to: {self.output_dir}")
        
    def generate_summary_report(self):
        """Generate a summary report of all results"""
        summary = {
            "overview": self.stats,
            "successful_questions": [],
            "failed_questions": [],
            "generated_at": datetime.now().isoformat()
        }
        
        # Collect results
        for result_file in self.results_dir.glob("question_*_result.json"):
            try:
                with open(result_file, 'r') as f:
                    result = json.load(f)
                    if result.get("success"):
                        summary["successful_questions"].append({
                            "number": result["question_number"],
                            "text": result["question_text"][:100] + "..." if len(result["question_text"]) > 100 else result["question_text"],
                            "duration": result["duration"]
                        })
            except Exception as e:
                logger.error(f"Error reading result file {result_file}: {e}")
                
        # Collect errors
        for error_file in self.logs_dir.glob("question_*_error.json"):
            try:
                with open(error_file, 'r') as f:
                    result = json.load(f)
                    summary["failed_questions"].append({
                        "number": result["question_number"],
                        "text": result["question_text"][:100] + "..." if len(result["question_text"]) > 100 else result["question_text"],
                        "error": result["error"]
                    })
            except Exception as e:
                logger.error(f"Error reading error file {error_file}: {e}")
                
        # Save summary
        summary_file = self.output_dir / "summary_report.json"
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
            
        logger.info(f"📋 Summary report saved to: {summary_file}")

def main():
    parser = argparse.ArgumentParser(description="Batch process questions from questions-list directory")
    parser.add_argument("--start", type=int, default=1, help="Start question number (default: 1)")
    parser.add_argument("--end", type=int, default=634, help="End question number (default: 634)")
    parser.add_argument("--server", default="http://localhost:8010", help="Server URL (default: http://localhost:8010)")
    parser.add_argument("--delay", type=float, default=2.0, help="Delay between request batches in seconds (default: 2.0)")
    parser.add_argument("--parallel", type=int, default=1, help="Number of parallel requests (default: 1)")
    parser.add_argument("--output-dir", default="./batch_results", help="Output directory (default: ./batch_results)")
    parser.add_argument("--resume", action="store_true", help="Resume from last processed question")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be processed without making requests")
    parser.add_argument("--verbose", "-v", action="store_true", help="Enable verbose logging")
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Initialize processor
    processor = BatchQuestionProcessor(
        server_url=args.server,
        delay=args.delay,
        parallel=args.parallel,
        output_dir=args.output_dir
    )
    
    # Handle resume
    start_num = args.start
    if args.resume:
        progress = processor.load_progress()
        if progress.get("last_processed"):
            start_num = progress["last_processed"] + 1
            logger.info(f"🔄 Resuming from question {start_num}")
            
    # Get questions list
    try:
        questions = processor.get_questions_list(start_num, args.end)
        if not questions:
            logger.error(f"No questions found in range {start_num}-{args.end}")
            sys.exit(1)
            
        logger.info(f"📋 Found {len(questions)} questions to process (#{start_num}-#{args.end})")
        
    except FileNotFoundError as e:
        logger.error(f"❌ {e}")
        sys.exit(1)
        
    # Run processing
    try:
        asyncio.run(processor.process_batch(questions, dry_run=args.dry_run))
        
        if not args.dry_run:
            processor.generate_summary_report()
            
    except KeyboardInterrupt:
        logger.info("🛑 Processing interrupted by user")
        processor.save_progress()
        sys.exit(0)
        
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        processor.save_progress()
        sys.exit(1)

if __name__ == "__main__":
    main()