#!/bin/bash
"""
Test Analysis API Script

Tests the /analyze endpoint with various financial questions.
"""

# Configuration
API_URL="http://localhost:8010"
USER_ID="test-user-$(date +%s)"
SESSION_ID=""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Financial Analysis API Test${NC}"
echo "=================================="
echo "API URL: $API_URL"
echo "User ID: $USER_ID"
echo ""

# Function to create session
create_session() {
    echo -e "${BLUE}📝 Creating new session...${NC}"
    
    RESPONSE=$(curl -s -X POST "$API_URL/session/start" \
        -H "Content-Type: application/json" \
        -d "{
            \"user_id\": \"$USER_ID\",
            \"title\": \"Test Analysis Session\"
        }")
    
    SESSION_ID=$(echo $RESPONSE | jq -r '.session_id // empty')
    
    if [ -n "$SESSION_ID" ]; then
        echo -e "${GREEN}✅ Session created: $SESSION_ID${NC}"
    else
        echo -e "${RED}❌ Failed to create session${NC}"
        echo "Response: $RESPONSE"
        exit 1
    fi
    echo ""
}

# Function to test analysis
test_analysis() {
    local question="$1"
    local description="$2"
    
    echo -e "${YELLOW}🔍 Testing: $description${NC}"
    echo "Question: $question"
    echo ""
    
    RESPONSE=$(curl -s -X POST "$API_URL/analyze" \
        -H "Content-Type: application/json" \
        -d "{
            \"question\": \"$question\",
            \"user_id\": \"$USER_ID\",
            \"session_id\": \"$SESSION_ID\",
            \"enable_caching\": true,
            \"auto_expand\": true,
            \"auto_execute\": true
        }")
    
    # Check if response is successful
    SUCCESS=$(echo $RESPONSE | jq -r '.success // false')
    
    if [ "$SUCCESS" = "true" ]; then
        echo -e "${GREEN}✅ Analysis successful${NC}"
        
        # Extract key information
        MESSAGE_ID=$(echo $RESPONSE | jq -r '.data.message_id // "N/A"')
        ANALYSIS_ID=$(echo $RESPONSE | jq -r '.data.analysisId // "N/A"')
        EXECUTION_ID=$(echo $RESPONSE | jq -r '.data.executionId // "N/A"')
        RESPONSE_TYPE=$(echo $RESPONSE | jq -r '.data.response_type // "N/A"')
        CONTENT=$(echo $RESPONSE | jq -r '.data.content // "N/A"')
        
        echo "Response Type: $RESPONSE_TYPE"
        echo "Message ID: $MESSAGE_ID"
        echo "Analysis ID: $ANALYSIS_ID"
        echo "Execution ID: $EXECUTION_ID"
        echo "Content Preview: $(echo "$CONTENT" | head -c 100)..."
        
        # Check for uiData with markdown
        HAS_MARKDOWN=$(echo $RESPONSE | jq -r '.data.uiData.markdown // empty')
        if [ -n "$HAS_MARKDOWN" ]; then
            echo -e "${GREEN}📝 Markdown generated!${NC}"
            echo "Markdown Preview: $(echo "$HAS_MARKDOWN" | head -c 150)..."
        fi
        
        # Check for results
        HAS_RESULTS=$(echo $RESPONSE | jq -r '.data.uiData.results // empty')
        if [ -n "$HAS_RESULTS" ]; then
            echo -e "${GREEN}📊 Results available!${NC}"
        fi
        
    else
        echo -e "${RED}❌ Analysis failed${NC}"
        ERROR=$(echo $RESPONSE | jq -r '.error // "Unknown error"')
        echo "Error: $ERROR"
    fi
    
    echo ""
    echo "Raw Response:"
    echo $RESPONSE | jq '.'
    echo ""
    echo "----------------------------------------"
    echo ""
}

# Function to check server health
check_server() {
    echo -e "${BLUE}🏥 Checking server health...${NC}"
    
    HEALTH_RESPONSE=$(curl -s "$API_URL/health" || echo "Connection failed")
    
    if echo "$HEALTH_RESPONSE" | jq -e . >/dev/null 2>&1; then
        echo -e "${GREEN}✅ Server is responding${NC}"
        echo "Health Response: $HEALTH_RESPONSE"
    else
        echo -e "${RED}❌ Server is not responding or returned invalid JSON${NC}"
        echo "Response: $HEALTH_RESPONSE"
        echo ""
        echo "Make sure the API server is running on $API_URL"
        exit 1
    fi
    echo ""
}

# Main execution
main() {
    # Check if jq is available
    if ! command -v jq &> /dev/null; then
        echo -e "${RED}❌ jq is required but not installed. Please install jq first.${NC}"
        echo "On macOS: brew install jq"
        echo "On Ubuntu: sudo apt-get install jq"
        exit 1
    fi
    
    # Check server health
    check_server
    
    # Create session
    create_session
    
    # Test different types of questions
    echo -e "${BLUE}🎯 Running Analysis Tests${NC}"
    echo ""
    
    # Test 1: Simple stock analysis
    test_analysis "What is the correlation between AAPL and SPY over the last year?" "Stock Correlation Analysis"
    
    # Test 2: Meaningless query
    test_analysis "hello how are you?" "Meaningless Query Test"
    
    # Test 3: Complex strategy analysis
    test_analysis "What if I buy QQQ when it drops more than 2% and hold for a month?" "Strategy Backtesting"
    
    # Test 4: Portfolio analysis
    test_analysis "Show me the weekday performance analysis for TSLA over the last 6 months" "Weekday Performance Analysis"
    
    echo -e "${GREEN}🎉 All tests completed!${NC}"
    echo ""
    echo "Session ID for further testing: $SESSION_ID"
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi