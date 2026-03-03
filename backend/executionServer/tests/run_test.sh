#!/bin/bash
# Run ResultFormatter test script

echo "🧪 Running ResultFormatter Test"
echo "==============================="

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found!"
    echo "📝 Please create .env file with your API key:"
    echo "   RESULT_FORMATTER_LLM_API_KEY=your-api-key-here"
    echo "   or"
    echo "   ANTHROPIC_API_KEY=your-api-key-here"
    exit 1
fi

# Check if python-dotenv is installed
python3 -c "import dotenv" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "📦 Installing python-dotenv..."
    pip3 install python-dotenv
fi

# Run the test
echo "🚀 Starting test..."
python3 test_result_formatter.py