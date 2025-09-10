#!/usr/bin/env node

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { 
  CallToolRequestSchema, 
  ErrorCode, 
  ListToolsRequestSchema, 
  McpError 
} from '@modelcontextprotocol/sdk/types.js';

import { generateMockData } from './mockDataGenerator.js';
import { FINANCIAL_TOOLS } from './toolDefinitions.js';

class FinancialMockServer {
  constructor() {
    this.server = new Server(
      {
        name: 'financial-mock-server',
        version: '1.0.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupToolHandlers();
  }

  setupToolHandlers() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: FINANCIAL_TOOLS,
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        const result = await this.handleToolCall(name, args || {});
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      } catch (error) {
        throw new McpError(
          ErrorCode.InternalError,
          `Error executing tool ${name}: ${error.message}`
        );
      }
    });
  }

  async handleToolCall(toolName, args) {
    console.error(`[MCP] Executing tool: ${toolName}`, args);

    // Parse the tool name to extract API and endpoint info
    const [api, ...endpointParts] = toolName.split('_');
    const endpoint = endpointParts.join('_');

    switch (api) {
      case 'alpaca-trading':
        return this.handleAlpacaTradingCall(endpoint, args);
      case 'alpaca-market':
        return this.handleAlpacaMarketCall(endpoint, args);
      case 'eodhd':
        return this.handleEodhdCall(endpoint, args);
      default:
        throw new Error(`Unknown API: ${api}`);
    }
  }

  handleAlpacaTradingCall(endpoint, args) {
    switch (endpoint) {
      case 'account':
        return generateMockData('alpaca-trading', '/v2/account', args);
      case 'positions':
        return generateMockData('alpaca-trading', '/v2/positions', args);
      case 'orders':
        return generateMockData('alpaca-trading', '/v2/orders', args);
      case 'portfolio-history':
        return generateMockData('alpaca-trading', '/v2/portfolio/history', args);
      case 'watchlists':
        return generateMockData('alpaca-trading', '/v2/watchlists', args);
      case 'account-activities':
        return generateMockData('alpaca-trading', '/v2/account/activities', args);
      case 'assets':
        return generateMockData('alpaca-trading', '/v2/assets', args);
      case 'calendar':
        return generateMockData('alpaca-trading', '/v2/calendar', args);
      case 'clock':
        return generateMockData('alpaca-trading', '/v2/clock', args);
      case 'options-contracts':
        return generateMockData('alpaca-trading', '/v2/options/contracts', args);
      case 'corporate-actions':
        return generateMockData('alpaca-trading', '/v2/corporate_actions/announcements', args);
      case 'wallets':
        return generateMockData('alpaca-trading', '/v2/wallets', args);
      default:
        throw new Error(`Unknown Alpaca Trading endpoint: ${endpoint}`);
    }
  }

  handleAlpacaMarketCall(endpoint, args) {
    switch (endpoint) {
      case 'stocks-bars':
        return generateMockData('alpaca-market', '/v2/stocks/bars', args);
      case 'stocks-quotes-latest':
        return generateMockData('alpaca-market', '/v2/stocks/quotes/latest', args);
      case 'stocks-trades-latest':
        return generateMockData('alpaca-market', '/v2/stocks/trades/latest', args);
      case 'stocks-snapshots':
        return generateMockData('alpaca-market', '/v2/stocks/snapshots', args);
      case 'options-quotes-latest':
        return generateMockData('alpaca-market', '/v1beta1/options/quotes/latest', args);
      case 'options-trades-latest':
        return generateMockData('alpaca-market', '/v1beta1/options/trades/latest', args);
      case 'options-snapshots':
        return generateMockData('alpaca-market', '/v1beta1/options/snapshots', args);
      case 'crypto-bars':
        return generateMockData('alpaca-market', '/v1beta3/crypto/{loc}/bars', args);
      case 'forex-rates':
        return generateMockData('alpaca-market', '/v1beta1/forex/latest/rates', args);
      case 'screener-most-actives':
        return generateMockData('alpaca-market', '/v1beta1/screener/stocks/most-actives', args);
      case 'screener-top-gainers':
        return generateMockData('alpaca-market', '/v1beta1/screener/stocks/top-gainers', args);
      case 'screener-top-losers':
        return generateMockData('alpaca-market', '/v1beta1/screener/stocks/top-losers', args);
      case 'news':
        return generateMockData('alpaca-market', '/v1beta1/news', args);
      case 'corporate-actions':
        return generateMockData('alpaca-market', '/v1/corporate-actions', args);
      default:
        throw new Error(`Unknown Alpaca Market Data endpoint: ${endpoint}`);
    }
  }

  handleEodhdCall(endpoint, args) {
    switch (endpoint) {
      case 'eod-data':
        return generateMockData('eodhd', '/api/eod/{symbol}', args);
      case 'real-time':
        return generateMockData('eodhd', '/api/real-time/{symbol}', args);
      case 'fundamentals':
        return generateMockData('eodhd', '/api/fundamentals/{symbol}', args);
      case 'dividends':
        return generateMockData('eodhd', '/api/div/{symbol}', args);
      case 'splits':
        return generateMockData('eodhd', '/api/splits/{symbol}', args);
      case 'technical-indicators':
        return generateMockData('eodhd', '/api/technical/{symbol}', args);
      case 'screener':
        return generateMockData('eodhd', '/api/screener', args);
      case 'search':
        return generateMockData('eodhd', '/api/search/{query}', args);
      case 'exchanges':
        return generateMockData('eodhd', '/api/exchanges-list', args);
      case 'etf-holdings':
        return generateMockData('eodhd', '/api/etf/{symbol}', args);
      case 'insider-transactions':
        return generateMockData('eodhd', '/api/insider-transactions', args);
      case 'short-interest':
        return generateMockData('eodhd', '/api/short-interest/{symbol}', args);
      case 'macro-indicators':
        return generateMockData('eodhd', '/api/macro-indicator/{indicator}', args);
      case 'earnings-calendar':
        return generateMockData('eodhd', '/api/calendar/{symbol}', args);
      default:
        throw new Error(`Unknown EODHD endpoint: ${endpoint}`);
    }
  }

  async run() {
    const transport = new StdioServerTransport();
    await this.server.connect(transport);
    console.error('Financial Mock MCP server running on stdio');
  }
}

const server = new FinancialMockServer();
server.run().catch((error) => {
  console.error('Server failed to start:', error);
  process.exit(1);
});