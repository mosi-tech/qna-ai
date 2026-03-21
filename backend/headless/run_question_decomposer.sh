#!/bin/bash

# Question Decomposer Agent Runner
# Initializes environment and runs the decomposer
# Usage:
#   ./run_question_decomposer.sh                    # Process 200 questions from start
#   ./run_question_decomposer.sh 50 100             # Process 100 questions starting at Q50
#   ./run_question_decomposer.sh --start-at 50 --max-questions 100

echo "🚀 Initializing environment..."
eval "$(curl -sS localhost:8001/setup)"

echo "📖 Starting Question Decomposer Agent..."
cd "$(dirname "$0")"

# Parse arguments
START_AT=0
MAX_QUESTIONS=200
QUESTIONS_FILE="all-questions/consolidated_questions_prioritized.json"

if [[ $# -eq 2 && ! "$1" =~ ^-- ]]; then
    # Old style: ./run_question_decomposer.sh 50 100
    START_AT=$1
    MAX_QUESTIONS=$2
else
    # New style with flags
    while [[ $# -gt 0 ]]; do
        case $1 in
            --start-at)
                START_AT="$2"
                shift 2
                ;;
            --max-questions)
                MAX_QUESTIONS="$2"
                shift 2
                ;;
            --questions)
                QUESTIONS_FILE="$2"
                shift 2
                ;;
            *)
                shift
                ;;
        esac
    done
fi

echo "📊 Configuration:"
echo "   Start at question: $START_AT"
echo "   Max questions: $MAX_QUESTIONS"
echo "   Questions file: $QUESTIONS_FILE"
python3 agents/question_decomposer.py --start-at $START_AT --max-questions $MAX_QUESTIONS --questions "$QUESTIONS_FILE"

echo "✅ Done!"
