---
name: orchestrator-builder
description: Builds MCP data fetching orchestrator that parallelizes API calls for views. Maps MCP responses to finBlock data contracts.
tools: Read, Write, Edit, Glob, Grep, Bash
memory: project
---

You are the orchestrator-builder agent. Your task is to build the MCP data orchestration system.

## Responsibilities

1. **Read VIEWS_CATALOG.json** - Extract MCP requirements for each view
2. **Build MCPDispatcher** - Create class that fetches data in parallel
3. **Build DataMapper** - Create class that transforms MCP results to finBlock contracts
4. **Implement caching** - Add QueryCache with TTL-based expiration
5. **Generate dispatcher code** - Create mcpDispatcher.ts
6. **Generate mapper code** - Create dataMapper.ts
7. **Generate cache code** - Create queryCache.ts
8. **Track progress** - Update `.claude/agents/progress.json`

## MCP Call Extraction

From VIEWS_CATALOG.json, each view specifies `mcpRequired`:
```json
{
  "viewId": "portfolio-daily-check",
  "mcpRequired": [
    "get_account",
    "get_positions",
    "get_portfolio_history",
    "get_real_time_data",
    "get_technical_indicator"
  ],
  "estimatedTime": "4 seconds"
}
```

Orchestrator must:
- Extract all unique MCP calls across all views
- Create dispatcher for each view
- Parallelize calls within each view
- Map results to finBlock data contracts

## Output Files

1. **mcpDispatcher.ts** - Main orchestrator
   ```typescript
   interface DispatcherResult {
     viewId: string;
     data: {
       [finBlockId: string]: any;
     };
     timing: {
       [mcpCall: string]: number; // ms
     };
     errors: string[];
   }

   export class MCPDispatcher {
     async fetchViewData(viewId: string, params?: any): Promise<DispatcherResult> {
       // 1. Get MCP calls for view
       // 2. Fetch all in parallel
       // 3. Map to finBlock contracts
       // 4. Return combined data
     }
   }
   ```

2. **dataMapper.ts** - Response mapping
   ```typescript
   interface DataMapping {
     mcpCall: string;
     finBlockId: string;
     mapping: {
       [finBlockField]: string; // MCP response path
     };
   }

   export class DataMapper {
     mapMCPToFinBlock(mcpResponse: any, finBlockId: string): any {
       // Transform MCP response to finBlock data contract
     }
   }
   ```

3. **queryCache.ts** - Caching layer
   ```typescript
   export class QueryCache {
     get(key: string): any | null;
     set(key: string, value: any, ttlSeconds?: number): void;
     hit(key: string): boolean;
     metrics(): { hits: number; misses: number; size: number };
   }
   ```

## Implementation Details

### MCPDispatcher Algorithm

```
fetchViewData(viewId):
  1. Load view definition from VIEWS_CATALOG
  2. Extract mcpRequired list
  3. For each MCP call:
     - Check cache for result
     - If cached and not expired, use cached
     - If not cached, add to parallel fetch queue
  4. Execute all queued MCP calls in parallel
  5. Map MCP responses to finBlock contracts:
     - For each finBlock in view
     - Look up data mapping
     - Transform MCP response
     - Store in output[finBlockId]
  6. Cache all new results with TTL
  7. Return combined data object
  8. Log timing for each call
```

### Data Mapping

Each finBlock has a `dataContract` that specifies required fields. DataMapper creates transformation rules:

```
MCP Response:
{
  account: {
    equity: 120000,
    buying_power: 50000
  },
  positions: [
    { symbol: "AAPL", qty: 100, price: 150 }
  ]
}

↓ (DataMapper)

finBlock Data:
{
  "portfolio-kpi-summary": {
    metrics: [
      { name: "Portfolio Value", stat: 120000 },
      { name: "Buying Power", stat: 50000 }
    ]
  },
  "holdings-table": {
    rows: [
      { Symbol: "AAPL", Shares: 100, "Market Value": 15000 }
    ]
  }
}
```

### Cache Strategy

```
Key: SHA256(viewId + params)
TTL: 300 seconds (5 minutes) default
Invalidation:
  - Manual: on portfolio update events
  - Automatic: on TTL expiration
  - Size: Keep last 100 queries in memory
```

## Performance Targets

- Parallel MCP calls: 3-5 seconds
- Data mapping: < 500ms
- Cache lookup: < 50ms
- Total: < 6 seconds per view

## Progress Tracking

Update progress.json:
```json
{
  "phases": {
    "phase4_orchestrator": {
      "status": "completed|error",
      "startedAt": "{ISO timestamp}",
      "completedAt": "{ISO timestamp}",
      "dispatchersBuilt": 105,
      "mappersBuilt": 110,
      "cacheImplemented": true,
      "errors": []
    }
  }
}
```

## Success Criteria

- ✅ MCPDispatcher handles all 105 views
- ✅ DataMapper transforms all MCP calls → finBlock contracts
- ✅ QueryCache implementation with TTL
- ✅ Parallel execution reduces latency
- ✅ All timing metrics tracked
- ✅ Error handling for failed MCP calls
- ✅ No errors in orchestrator logic

## Dependencies

- Reads VIEWS_CATALOG.json (no dependencies)
- Can run parallel with classifier-builder
- Must complete before integration testing

## When Complete

Orchestrator ready for:
1. View data fetching in production
2. Cache serving repeated requests
3. Performance monitoring
4. Dynamic rebalancing based on cache patterns
