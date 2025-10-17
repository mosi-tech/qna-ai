# MCP Server Management Guide

## Overview
MCP (Model Context Protocol) servers must be **manually restarted** after code changes to load new functions and updates. This is a critical step often overlooked in development workflows.

## Current MCP Server Status

### ✅ Working Servers
- **MCP Financial Server**: Node.js server providing Alpaca API functions
- **MCP Analytics Engine**: Python library with 44+ functions (not currently running as MCP server)

### ❌ Server Restart Issues
- **XGBoost Dependency**: OpenMP library missing on macOS (handled gracefully now)
- **Server Startup**: MCP protocol server needs proper error handling

## Required Workflow: MCP Server Restart Protocol

### After Any Code Changes to Analytics Functions:

1. **Check Running Servers**
   ```bash
   ps aux | grep mcp
   ```

2. **Kill Analytics Server** (if running)
   ```bash
   pkill -f "python.*mcp-analytics-server" || echo "No server running"
   ```

3. **Restart Analytics Server**
   ```bash
   cd mcp-analytics-server
   python server.py > server_startup.log 2>&1 &
   ```

4. **Verify Server Status**
   ```bash
   # Check process
   ps aux | grep "python.*server.py"
   
   # Check logs
   tail -f server_startup.log
   ```

5. **Test Function Availability**
   ```bash
   # Test analytics engine directly
   python -c "from analytics.main import AnalyticsEngine; print('✅ Engine loaded')"
   ```

## Signs Server Restart is Needed

### ❌ Error Indicators:
- `Unknown function: <function_name>` errors
- Import errors in server logs
- MCP tool discovery not showing new functions
- Pipeline testing fails on engine-type functions

### ✅ Success Indicators:
- Server startup logs show "tools registered"
- Function discovery includes new functions
- Mock pipeline testing passes
- No import/dependency errors

## Current Analytics Functions Status

### ✅ Successfully Loaded (44+ functions):
```
Categories: returns, volatility, correlation, rolling_metrics, 
trend_analysis, moving_averages, gaps, event_driven, 
relative_strength, patterns, ranges

New Functions Added:
- calculate_fair_value_gaps (pandas/scipy statistical analysis)
- analyze_weekday_patterns (pandas/scipy weekday analysis) 
- comprehensive_technical_analysis (ta library integration)
- cluster_stocks_by_returns (sklearn clustering)
- detect_outlier_stocks (sklearn/scipy outlier detection)
```

## Updated MCP Question Processor Wrapper

### Key Additions:
1. **Mandatory MCP server restart after function implementation**
2. **Server status verification before pipeline testing**
3. **Function discovery confirmation**
4. **Error handling for server startup issues**

### New Requirements in Processing:
```
4. Test Workflow Pipeline:
   - FIRST: Verify MCP servers are running and current ✅
   - Generate mock input data for Step 1
   - Execute Step 1 with mock data
   - [continue pipeline testing...]

5. Implement Missing Functions:
   - Add missing analytics functions
   - Update MCP server tool definitions
   - MANDATORY: Restart MCP analytics server ✅
   - Test new functions with mock data
```

## Common Issues & Solutions

### Issue: XGBoost Import Error
**Problem**: `XGBoostError: XGBoost Library (libxgboost.dylib) could not be loaded`
**Solution**: 
```python
# Graceful handling in ml_analytics.py
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except (ImportError, Exception) as e:
    XGBOOST_AVAILABLE = False
    xgb = None
```

### Issue: Analytics Engine Import Success but MCP Server Fails
**Problem**: Analytics functions work in Python but MCP server doesn't start
**Solution**: 
- Check MCP protocol dependencies
- Verify server.py has proper error handling
- Test individual components before full server startup

### Issue: New Functions Not Recognized
**Problem**: Recently added functions show "Unknown function" errors
**Solution**: 
- Verify function is in function_map in analytics/main.py
- Ensure MCP server tool definitions updated in server.py
- Restart MCP server to load changes
- Test function discovery

## Best Practices

### 1. Test Before MCP Server
Always verify analytics functions work independently:
```bash
python -c "from analytics.main import AnalyticsEngine; engine = AnalyticsEngine()"
```

### 2. Graceful Dependency Handling
```python
try:
    import optional_library
    LIBRARY_AVAILABLE = True
except (ImportError, Exception):
    LIBRARY_AVAILABLE = False
    optional_library = None
```

### 3. Comprehensive Error Logging
```bash
python server.py > server_startup.log 2>&1 &
tail -f server_startup.log
```

### 4. Function Verification
After restart, verify functions are available:
```bash
# Check function categories
python -c "
from analytics.main import AnalyticsEngine
engine = AnalyticsEngine()
print('Available functions:', engine.list_functions().keys())
"
```

## Integration with Question Processing

### Before Processing Any Question:
1. ✅ Check MCP server status
2. ✅ Verify function availability
3. ✅ Test critical functions if recently modified

### After Implementing New Functions:
1. ✅ Add function to analytics/main.py function_map
2. ✅ Update server.py tool definitions
3. ✅ Restart MCP analytics server
4. ✅ Verify function discovery
5. ✅ Test pipeline with mock data

This ensures the updated MCP Question Processor Wrapper will have access to all implemented functions and can perform reliable end-to-end pipeline validation.