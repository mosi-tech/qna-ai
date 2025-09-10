import fs from 'fs';
import path from 'path';

// Generate realistic financial data based on API specs
export function generateMockData(api, endpoint, args = {}) {
  const today = new Date();
  const symbols = parseSymbols(args.symbols || args.symbol || 'AAPL,TSLA,SPY');
  
  switch (api) {
    case 'alpaca-trading':
      return generateAlpacaTradingData(endpoint, args, symbols, today);
    case 'alpaca-market':
      return generateAlpacaMarketData(endpoint, args, symbols, today);
    case 'eodhd':
      return generateEodhdData(endpoint, args, symbols, today);
    default:
      throw new Error(`Unknown API: ${api}`);
  }
}

function parseSymbols(symbolString) {
  if (typeof symbolString !== 'string') return ['AAPL'];
  return symbolString.split(',').map(s => s.trim());
}

function generateAlpacaTradingData(endpoint, args, symbols, today) {
  switch (endpoint) {
    case '/v2/account':
      return {
        id: "904837e3-3b76-47ec-b432-046db621571b",
        account_number: "010203ABCD",
        status: "ACTIVE",
        crypto_status: "ACTIVE",
        currency: "USD",
        buying_power: "262113.632",
        regt_buying_power: "262113.632",
        daytrading_buying_power: "262113.632",
        non_marginable_buying_power: "131056.82",
        cash: "131056.82",
        accrued_fees: "0",
        portfolio_value: "525487.34",
        pattern_day_trader: false,
        trading_blocked: false,
        transfers_blocked: false,
        account_blocked: false,
        created_at: "2019-06-12T22:47:07.99Z",
        trade_suspended_by_user: false,
        multiplier: "2",
        shorting_enabled: true,
        equity: "525487.34",
        last_equity: "518234.12",
        long_market_value: "394430.52",
        short_market_value: "0",
        initial_margin: "197215.26",
        maintenance_margin: "118329.16",
        last_maintenance_margin: "115642.08",
        sma: "131056.82",
        daytrade_count: 2
      };

    case '/v2/positions':
      return symbols.slice(0, 5).map((symbol, i) => {
        const prices = { AAPL: 185.64, TSLA: 248.50, SPY: 451.23, MSFT: 374.58, GOOGL: 134.12 };
        const basePrice = prices[symbol] || (150 + i * 20);
        const qty = [100, 50, 200, 75, 150][i] || 100;
        const avgEntry = basePrice * (0.85 + Math.random() * 0.3);
        const marketValue = basePrice * qty;
        const costBasis = avgEntry * qty;
        const unrealizedPl = marketValue - costBasis;
        
        return {
          asset_id: `asset-${symbol.toLowerCase()}-${i}`,
          symbol,
          exchange: "NASDAQ",
          asset_class: "us_equity",
          avg_entry_price: avgEntry.toFixed(2),
          qty: qty.toString(),
          side: "long",
          market_value: marketValue.toFixed(2),
          cost_basis: costBasis.toFixed(2),
          unrealized_pl: unrealizedPl.toFixed(2),
          unrealized_plpc: (unrealizedPl / costBasis).toFixed(6),
          unrealized_intraday_pl: (Math.random() * 200 - 100).toFixed(2),
          unrealized_intraday_plpc: (Math.random() * 0.02 - 0.01).toFixed(6),
          current_price: basePrice.toFixed(2),
          lastday_price: (basePrice * (0.98 + Math.random() * 0.04)).toFixed(2),
          change_today: (Math.random() * 0.04 - 0.02).toFixed(6)
        };
      });

    case '/v2/orders':
      const limit = parseInt(args.limit) || 10;
      return Array.from({ length: limit }, (_, i) => {
        const symbol = symbols[i % symbols.length];
        const statuses = ['filled', 'open', 'canceled', 'partially_filled'];
        const status = args.status || statuses[i % statuses.length];
        
        return {
          id: `order-${Date.now()}-${i}`,
          client_order_id: `client-order-${i}`,
          created_at: new Date(today.getTime() - i * 3600000).toISOString(),
          updated_at: new Date(today.getTime() - i * 3600000 + 300000).toISOString(),
          submitted_at: new Date(today.getTime() - i * 3600000).toISOString(),
          filled_at: status === 'filled' ? new Date(today.getTime() - i * 3600000 + 600000).toISOString() : null,
          asset_id: `asset-${symbol.toLowerCase()}`,
          symbol,
          asset_class: "us_equity",
          notional: null,
          qty: (10 + i * 5).toString(),
          filled_qty: status === 'filled' ? (10 + i * 5).toString() : (i * 2).toString(),
          filled_avg_price: status !== 'open' ? (100 + i * 10).toFixed(2) : null,
          order_class: "",
          order_type: ["market", "limit", "stop"][i % 3],
          type: ["market", "limit", "stop"][i % 3],
          side: i % 2 === 0 ? "buy" : "sell",
          time_in_force: "day",
          limit_price: (100 + i * 10).toFixed(2),
          stop_price: null,
          status,
          extended_hours: false,
          legs: null
        };
      });

    case '/v2/portfolio/history':
      const period = args.period || '1M';
      const timeframe = args.timeframe || '1D';
      const days = period === '1D' ? 1 : period === '7D' ? 7 : period === '1M' ? 30 : 90;
      
      const timestamps = [];
      const equity = [];
      const profit_loss = [];
      const profit_loss_pct = [];
      
      let currentEquity = 500000;
      
      for (let i = 0; i < days; i++) {
        const date = new Date(today);
        date.setDate(date.getDate() - (days - i));
        timestamps.push(date.getTime());
        
        const dailyChange = (Math.random() - 0.5) * 20000;
        currentEquity += dailyChange;
        equity.push(parseFloat(currentEquity.toFixed(2)));
        profit_loss.push(parseFloat(dailyChange.toFixed(2)));
        profit_loss_pct.push(parseFloat((dailyChange / currentEquity).toFixed(6)));
      }
      
      return {
        timestamp: timestamps,
        equity,
        profit_loss,
        profit_loss_pct,
        base_value: 500000,
        timeframe
      };

    case '/v2/watchlists':
      return [
        {
          id: "fb306e55-16d3-4118-8c3d-c1615fcd4c03",
          account_id: "1d5493c9-ea39-4377-aa94-340734c368ae",
          created_at: "2019-10-30T07:54:42Z",
          updated_at: "2024-01-15T12:30:00Z",
          name: "Tech Stocks",
          assets: symbols.slice(0, 5).map(symbol => ({
            id: `asset-${symbol.toLowerCase()}`,
            class: "us_equity",
            exchange: "NASDAQ",
            symbol,
            name: getCompanyName(symbol),
            status: "active",
            tradable: true
          }))
        },
        {
          id: "ab123456-78cd-9012-ef34-567890abcdef",
          account_id: "1d5493c9-ea39-4377-aa94-340734c368ae",
          created_at: "2020-03-15T09:15:30Z",
          updated_at: "2024-01-10T16:45:00Z",
          name: "Growth Picks",
          assets: ['NVDA', 'AMD', 'CRM'].map(symbol => ({
            id: `asset-${symbol.toLowerCase()}`,
            class: "us_equity",
            exchange: "NASDAQ",
            symbol,
            name: getCompanyName(symbol),
            status: "active",
            tradable: true
          }))
        }
      ];

    case '/v2/account/activities':
      const pageSize = parseInt(args.page_size) || 20;
      const activityType = args.activity_type;
      const activityTypes = activityType ? [activityType] : ['FILL', 'TRANS', 'MISC'];
      
      return Array.from({ length: pageSize }, (_, i) => {
        const type = activityTypes[i % activityTypes.length];
        const symbol = symbols[i % symbols.length];
        
        return {
          id: `activity-${Date.now()}-${i}`,
          account_id: "1d5493c9-ea39-4377-aa94-340734c368ae",
          activity_type: type,
          transaction_time: new Date(today.getTime() - i * 3600000).toISOString(),
          type: type.toLowerCase(),
          price: type === 'FILL' ? (100 + Math.random() * 200).toFixed(2) : null,
          qty: type === 'FILL' ? (10 + i * 5).toString() : null,
          side: type === 'FILL' ? (i % 2 === 0 ? "buy" : "sell") : null,
          symbol: type === 'FILL' ? symbol : null,
          description: `${type} activity for ${symbol}`,
          net_amount: (Math.random() * 10000 - 5000).toFixed(2)
        };
      });

    case '/v2/assets':
      return symbols.map(symbol => ({
        id: `asset-${symbol.toLowerCase()}`,
        class: args.asset_class || "us_equity",
        exchange: "NASDAQ",
        symbol,
        name: getCompanyName(symbol),
        status: args.status || "active",
        tradable: true,
        marginable: true,
        shortable: true,
        easy_to_borrow: true,
        fractionable: true
      }));

    case '/v2/calendar':
      const start = args.start ? new Date(args.start) : new Date(today);
      const end = args.end ? new Date(args.end) : new Date(today.getTime() + 30 * 24 * 3600000);
      const calendar = [];
      
      for (let d = new Date(start); d <= end; d.setDate(d.getDate() + 1)) {
        if (d.getDay() !== 0 && d.getDay() !== 6) { // Skip weekends
          calendar.push({
            date: d.toISOString().split('T')[0],
            open: "09:30",
            close: "16:00",
            session_open: "04:00",
            session_close: "20:00"
          });
        }
      }
      
      return calendar;

    case '/v2/clock':
      const now = new Date();
      const marketOpen = new Date(now);
      marketOpen.setHours(9, 30, 0, 0);
      const marketClose = new Date(now);
      marketClose.setHours(16, 0, 0, 0);
      
      return {
        timestamp: now.toISOString(),
        is_open: now >= marketOpen && now <= marketClose && now.getDay() >= 1 && now.getDay() <= 5,
        next_open: getNextMarketOpen(now),
        next_close: getNextMarketClose(now)
      };

    case '/v2/options/contracts':
      return symbols.filter(s => !s.includes('/')).slice(0, 3).flatMap(symbol => 
        ['call', 'put'].flatMap(type => 
          [180, 190, 200].map(strike => ({
            id: `option-${symbol.toLowerCase()}-${type}-${strike}`,
            symbol: `${symbol}241220${type.toUpperCase()[0]}00${strike}000`,
            name: `${symbol} Dec 20 '24 $${strike} ${type}`,
            status: "active",
            tradable: true,
            expiration_date: "2024-12-20",
            root_symbol: symbol,
            underlying_symbol: symbol,
            underlying_asset_id: `asset-${symbol.toLowerCase()}`,
            type,
            style: "american",
            strike_price: strike.toString(),
            multiplier: "100",
            size: "100",
            open_interest: (Math.random() * 5000).toFixed(0),
            open_interest_date: today.toISOString().split('T')[0],
            close_price: (Math.random() * 20 + 5).toFixed(2),
            close_price_date: today.toISOString().split('T')[0]
          }))
        )
      );

    case '/v2/corporate_actions/announcements':
      return symbols.slice(0, 3).map((symbol, i) => ({
        id: `ca-${symbol.toLowerCase()}-${i}`,
        corporate_action_id: `${['DIVD', 'SPLT', 'MRGR'][i]}_${symbol}_${today.getFullYear()}${String(today.getMonth() + 1).padStart(2, '0')}15`,
        ca_type: ['dividend', 'stock_split', 'merger'][i],
        ca_sub_type: ['cash', 'forward', 'cash'][i],
        initiating_symbol: symbol,
        target_symbol: symbol,
        declaration_date: formatDate(new Date(today.getTime() - 30 * 24 * 3600000)),
        ex_date: formatDate(new Date(today.getTime() - 7 * 24 * 3600000)),
        record_date: formatDate(new Date(today.getTime() - 5 * 24 * 3600000)),
        payable_date: formatDate(new Date(today.getTime() + 7 * 24 * 3600000)),
        cash_amount: i === 0 ? "0.24" : null,
        old_rate: i === 1 ? "1" : "1",
        new_rate: i === 1 ? "2" : "1"
      }));

    case '/v2/wallets':
      return [
        {
          id: "97522d8b-1ad5-4b3d-af5d-1d4839205161",
          account_id: "1d5493c9-ea39-4377-aa94-340734c368ae",
          name: "BTC Wallet",
          currency: "BTC",
          balance: "2.45671234",
          last_transaction_at: formatDateTime(new Date(today.getTime() - 2 * 3600000)),
          created_at: "2023-05-15T18:40:04.504Z",
          updated_at: formatDateTime(today)
        },
        {
          id: "12345678-abcd-efgh-ijkl-987654321098",
          account_id: "1d5493c9-ea39-4377-aa94-340734c368ae",
          name: "ETH Wallet", 
          currency: "ETH",
          balance: "15.67890123",
          last_transaction_at: formatDateTime(new Date(today.getTime() - 5 * 3600000)),
          created_at: "2023-06-20T10:15:30.200Z",
          updated_at: formatDateTime(today)
        }
      ];

    default:
      return { error: `Mock data not implemented for endpoint: ${endpoint}` };
  }
}

function generateAlpacaMarketData(endpoint, args, symbols, today) {
  switch (endpoint) {
    case '/v2/stocks/bars':
      const timeframe = args.timeframe || '1Day';
      const days = timeframe === '1Day' ? 30 : timeframe === '1Hour' ? 7 : 1;
      const intervals = timeframe === '1Day' ? days : timeframe === '1Hour' ? days * 24 : days * 24 * 60;
      
      const bars = {};
      symbols.forEach(symbol => {
        bars[symbol] = Array.from({ length: intervals }, (_, i) => {
          const date = new Date(today);
          if (timeframe === '1Day') {
            date.setDate(date.getDate() - (intervals - i - 1));
          } else if (timeframe === '1Hour') {
            date.setHours(date.getHours() - (intervals - i - 1));
          } else {
            date.setMinutes(date.getMinutes() - (intervals - i - 1));
          }
          
          const basePrice = getBasePrice(symbol);
          const open = basePrice * (0.95 + Math.random() * 0.1);
          const close = open * (0.98 + Math.random() * 0.04);
          const high = Math.max(open, close) * (1 + Math.random() * 0.03);
          const low = Math.min(open, close) * (1 - Math.random() * 0.03);
          const volume = Math.floor(Math.random() * 10000000) + 100000;
          
          return {
            t: date.toISOString(),
            o: parseFloat(open.toFixed(2)),
            h: parseFloat(high.toFixed(2)),
            l: parseFloat(low.toFixed(2)),
            c: parseFloat(close.toFixed(2)),
            v: volume
          };
        });
      });
      
      return { bars };

    case '/v2/stocks/quotes/latest':
      const quotes = {};
      symbols.forEach(symbol => {
        const basePrice = getBasePrice(symbol);
        const bid = basePrice * (0.999 - Math.random() * 0.002);
        const ask = basePrice * (1.001 + Math.random() * 0.002);
        
        quotes[symbol] = {
          t: today.toISOString(),
          bp: parseFloat(bid.toFixed(2)),
          bs: Math.floor(Math.random() * 10) + 1,
          ap: parseFloat(ask.toFixed(2)),
          as: Math.floor(Math.random() * 10) + 1
        };
      });
      
      return { quotes };

    case '/v2/stocks/trades/latest':
      const trades = {};
      symbols.forEach(symbol => {
        const basePrice = getBasePrice(symbol);
        const price = basePrice * (0.998 + Math.random() * 0.004);
        
        trades[symbol] = {
          t: today.toISOString(),
          p: parseFloat(price.toFixed(2)),
          s: Math.floor(Math.random() * 1000) + 100
        };
      });
      
      return { trades };

    case '/v2/stocks/snapshots':
      const snapshots = {};
      symbols.forEach(symbol => {
        const basePrice = getBasePrice(symbol);
        const currentPrice = basePrice * (0.98 + Math.random() * 0.04);
        const bid = currentPrice * 0.999;
        const ask = currentPrice * 1.001;
        
        snapshots[symbol] = {
          latestTrade: {
            p: parseFloat(currentPrice.toFixed(2)),
            s: Math.floor(Math.random() * 1000) + 100,
            t: today.toISOString()
          },
          latestQuote: {
            bp: parseFloat(bid.toFixed(2)),
            ap: parseFloat(ask.toFixed(2)),
            t: today.toISOString()
          },
          dailyBar: {
            o: parseFloat((basePrice * 0.995).toFixed(2)),
            h: parseFloat((basePrice * 1.025).toFixed(2)),
            l: parseFloat((basePrice * 0.975).toFixed(2)),
            c: parseFloat(currentPrice.toFixed(2)),
            v: Math.floor(Math.random() * 50000000) + 1000000
          }
        };
      });
      
      return { snapshots };

    case '/v1beta1/options/quotes/latest':
      const optionQuotes = {};
      symbols.forEach(symbol => {
        if (!symbol.includes('C') && !symbol.includes('P')) return;
        
        const bid = 5 + Math.random() * 15;
        const ask = bid + 0.05 + Math.random() * 0.5;
        
        optionQuotes[symbol] = {
          bp: parseFloat(bid.toFixed(2)),
          bs: Math.floor(Math.random() * 10) + 1,
          ap: parseFloat(ask.toFixed(2)),
          as: Math.floor(Math.random() * 10) + 1,
          t: today.toISOString()
        };
      });
      
      return { quotes: optionQuotes };

    case '/v1beta1/options/trades/latest':
      const optionTrades = {};
      symbols.forEach(symbol => {
        if (!symbol.includes('C') && !symbol.includes('P')) return;
        
        const price = 5 + Math.random() * 15;
        
        optionTrades[symbol] = {
          p: parseFloat(price.toFixed(2)),
          s: Math.floor(Math.random() * 20) + 1,
          t: today.toISOString()
        };
      });
      
      return { trades: optionTrades };

    case '/v1beta1/options/snapshots':
      const optionSnapshots = {};
      symbols.forEach(symbol => {
        if (!symbol.includes('C') && !symbol.includes('P')) return;
        
        const price = 5 + Math.random() * 15;
        const bid = price * 0.98;
        const ask = price * 1.02;
        
        optionSnapshots[symbol] = {
          latestTrade: {
            p: parseFloat(price.toFixed(2)),
            s: Math.floor(Math.random() * 20) + 1
          },
          latestQuote: {
            bp: parseFloat(bid.toFixed(2)),
            ap: parseFloat(ask.toFixed(2))
          },
          impliedVolatility: parseFloat((0.2 + Math.random() * 0.4).toFixed(3)),
          openInterest: Math.floor(Math.random() * 5000) + 100
        };
      });
      
      return { snapshots: optionSnapshots };

    case '/v1beta3/crypto/{loc}/bars':
      const cryptoBars = {};
      const cryptoPairs = symbols.filter(s => s.includes('/'));
      
      cryptoPairs.forEach(pair => {
        const basePrice = pair.includes('BTC') ? 42000 : pair.includes('ETH') ? 2500 : 1;
        
        cryptoBars[pair] = Array.from({ length: 24 }, (_, i) => {
          const date = new Date(today);
          date.setHours(date.getHours() - (24 - i));
          
          const open = basePrice * (0.98 + Math.random() * 0.04);
          const close = open * (0.99 + Math.random() * 0.02);
          const high = Math.max(open, close) * (1 + Math.random() * 0.02);
          const low = Math.min(open, close) * (1 - Math.random() * 0.02);
          const volume = Math.random() * 1000;
          
          return {
            t: date.toISOString(),
            o: parseFloat(open.toFixed(2)),
            h: parseFloat(high.toFixed(2)),
            l: parseFloat(low.toFixed(2)),
            c: parseFloat(close.toFixed(2)),
            v: parseFloat(volume.toFixed(8))
          };
        });
      });
      
      return { bars: cryptoBars };

    case '/v1beta1/forex/latest/rates':
      const rates = {};
      const forexPairs = args.currency_pairs ? args.currency_pairs.split(',') : ['EUR/USD', 'GBP/USD', 'USD/JPY'];
      
      forexPairs.forEach(pair => {
        const baseRates = {
          'EUR/USD': 1.1067,
          'GBP/USD': 1.2734,
          'USD/JPY': 149.85,
          'USD/CAD': 1.3456,
          'AUD/USD': 0.6789
        };
        
        const baseRate = baseRates[pair] || 1.0;
        const rate = baseRate * (0.999 + Math.random() * 0.002);
        
        rates[pair] = {
          rate: parseFloat(rate.toFixed(4)),
          timestamp: today.toISOString()
        };
      });
      
      return { rates };

    case '/v1beta1/screener/stocks/most-actives':
      const top = args.top || 10;
      const activeStocks = [
        'AAPL', 'TSLA', 'SPY', 'QQQ', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'NFLX'
      ].slice(0, top);
      
      return {
        most_actives: activeStocks.map((symbol, i) => ({
          symbol,
          volume: Math.floor(Math.random() * 100000000) + 10000000,
          trade_count: Math.floor(Math.random() * 500000) + 50000,
          price: getBasePrice(symbol),
          change: (Math.random() - 0.5) * 10,
          change_percent: (Math.random() - 0.5) * 5
        }))
      };

    case '/v1beta1/screener/stocks/top-gainers':
      const gainersTop = args.top || 10;
      const gainerStocks = [
        'NVDA', 'AMD', 'TSLA', 'AAPL', 'MSFT', 'GOOGL', 'CRM', 'NFLX', 'AMZN', 'META'
      ].slice(0, gainersTop);
      
      return {
        top_gainers: gainerStocks.map(symbol => {
          const basePrice = getBasePrice(symbol);
          const change = 2 + Math.random() * 15;
          const changePercent = 1 + Math.random() * 8;
          
          return {
            symbol,
            percent_change: parseFloat(changePercent.toFixed(2)),
            change: parseFloat(change.toFixed(2)),
            price: parseFloat(basePrice.toFixed(2))
          };
        })
      };

    case '/v1beta1/screener/stocks/top-losers':
      const losersTop = args.top || 10;
      const loserStocks = [
        'META', 'NFLX', 'PYPL', 'SHOP', 'ROKU', 'ZM', 'PTON', 'TDOC', 'SQ', 'TWTR'
      ].slice(0, losersTop);
      
      return {
        top_losers: loserStocks.map(symbol => {
          const basePrice = getBasePrice(symbol);
          const change = -(2 + Math.random() * 12);
          const changePercent = -(1 + Math.random() * 6);
          
          return {
            symbol,
            percent_change: parseFloat(changePercent.toFixed(2)),
            change: parseFloat(change.toFixed(2)),
            price: parseFloat(basePrice.toFixed(2))
          };
        })
      };

    case '/v1beta1/news':
      const newsCount = 20;
      const newsSymbols = symbols.length > 0 ? symbols : ['AAPL', 'TSLA', 'SPY'];
      
      return {
        news: Array.from({ length: newsCount }, (_, i) => ({
          id: 24843171 + i,
          headline: generateNewsHeadline(newsSymbols[i % newsSymbols.length]),
          summary: generateNewsSummary(newsSymbols[i % newsSymbols.length]),
          symbols: [newsSymbols[i % newsSymbols.length]],
          created_at: new Date(today.getTime() - i * 3600000).toISOString(),
          updated_at: new Date(today.getTime() - i * 3600000 + 300000).toISOString(),
          url: `https://example.com/news/${24843171 + i}`,
          content: args.include_content ? generateNewsContent(newsSymbols[i % newsSymbols.length]) : null
        }))
      };

    case '/v1/corporate-actions':
      return {
        corporate_actions: symbols.slice(0, 5).map((symbol, i) => {
          const types = ['cash_dividend', 'stock_dividend', 'forward_split', 'reverse_split', 'spin_off'];
          const type = args.types ? args.types.split(',')[0] : types[i % types.length];
          
          return {
            symbol,
            type,
            ex_date: formatDate(new Date(today.getTime() + (i + 1) * 7 * 24 * 3600000)),
            record_date: formatDate(new Date(today.getTime() + (i + 1) * 7 * 24 * 3600000 + 2 * 24 * 3600000)),
            payable_date: formatDate(new Date(today.getTime() + (i + 1) * 7 * 24 * 3600000 + 5 * 24 * 3600000)),
            amount: type.includes('dividend') ? parseFloat((0.1 + Math.random() * 0.5).toFixed(2)) : null,
            ratio: type.includes('split') ? (type === 'forward_split' ? '2:1' : '1:2') : null
          };
        })
      };

    default:
      return { error: `Mock data not implemented for endpoint: ${endpoint}` };
  }
}

function generateEodhdData(endpoint, args, symbols, today) {
  const symbol = args.symbol || symbols[0] || 'AAPL.US';
  
  switch (endpoint) {
    case '/api/eod/{symbol}':
      const period = args.period || 'd';
      const days = period === 'd' ? 30 : period === 'w' ? 12 : 6;
      
      return Array.from({ length: days }, (_, i) => {
        const date = new Date(today);
        if (period === 'd') {
          date.setDate(date.getDate() - (days - i - 1));
        } else if (period === 'w') {
          date.setDate(date.getDate() - (days - i - 1) * 7);
        } else {
          date.setMonth(date.getMonth() - (days - i - 1));
        }
        
        const basePrice = getBasePrice(symbol.split('.')[0]);
        const open = basePrice * (0.95 + Math.random() * 0.1);
        const close = open * (0.98 + Math.random() * 0.04);
        const high = Math.max(open, close) * (1 + Math.random() * 0.03);
        const low = Math.min(open, close) * (1 - Math.random() * 0.03);
        const volume = Math.floor(Math.random() * 50000000) + 1000000;
        
        return {
          date: formatDate(date),
          open: parseFloat(open.toFixed(2)),
          high: parseFloat(high.toFixed(2)),
          low: parseFloat(low.toFixed(2)),
          close: parseFloat(close.toFixed(2)),
          adjusted_close: parseFloat(close.toFixed(2)),
          volume
        };
      });

    case '/api/real-time/{symbol}':
      const basePrice = getBasePrice(symbol.split('.')[0]);
      const currentPrice = basePrice * (0.98 + Math.random() * 0.04);
      const previousClose = basePrice * 0.995;
      const change = currentPrice - previousClose;
      const changePercent = (change / previousClose) * 100;
      
      return {
        code: symbol,
        timestamp: Math.floor(today.getTime() / 1000),
        gmtoffset: 0,
        open: parseFloat((basePrice * 0.99).toFixed(2)),
        high: parseFloat((currentPrice * 1.01).toFixed(2)),
        low: parseFloat((currentPrice * 0.99).toFixed(2)),
        close: parseFloat(currentPrice.toFixed(2)),
        volume: Math.floor(Math.random() * 50000000) + 1000000,
        previousClose: parseFloat(previousClose.toFixed(2)),
        change: parseFloat(change.toFixed(2)),
        change_p: parseFloat(changePercent.toFixed(2))
      };

    case '/api/fundamentals/{symbol}':
      const stockSymbol = symbol.split('.')[0];
      return {
        General: {
          Code: stockSymbol,
          Type: "Common Stock",
          Name: getCompanyName(stockSymbol),
          Exchange: "NASDAQ",
          CurrencyCode: "USD",
          CurrencyName: "US Dollar",
          CurrencySymbol: "$",
          CountryName: "USA",
          CountryISO: "US",
          ISIN: generateISIN(stockSymbol),
          CUSIP: generateCUSIP(stockSymbol),
          Description: `${getCompanyName(stockSymbol)} operates in the technology sector...`,
          Sector: "Technology",
          Industry: getIndustry(stockSymbol),
          FullTimeEmployees: Math.floor(Math.random() * 500000) + 10000,
          MarketCapitalization: Math.floor(Math.random() * 3000000000000) + 100000000000,
          SharesOutstanding: Math.floor(Math.random() * 20000000000) + 1000000000,
          DividendYield: parseFloat((Math.random() * 0.05).toFixed(4)),
          EPS: parseFloat((Math.random() * 10 + 1).toFixed(2)),
          PERatio: parseFloat((15 + Math.random() * 25).toFixed(2)),
          Beta: parseFloat((0.5 + Math.random() * 1.5).toFixed(3))
        },
        Financials: {
          Balance_Sheet: {
            quarterly: {
              [formatQuarter(today)]: {
                totalAssets: (Math.random() * 500000000000 + 100000000000).toFixed(0),
                totalLiab: (Math.random() * 300000000000 + 50000000000).toFixed(0),
                totalStockholderEquity: (Math.random() * 200000000000 + 50000000000).toFixed(0),
                cash: (Math.random() * 50000000000 + 10000000000).toFixed(0),
                shortTermInvestments: (Math.random() * 40000000000 + 5000000000).toFixed(0)
              }
            }
          },
          Income_Statement: {
            quarterly: {
              [formatQuarter(today)]: {
                totalRevenue: (Math.random() * 100000000000 + 10000000000).toFixed(0),
                costOfRevenue: (Math.random() * 60000000000 + 5000000000).toFixed(0),
                grossProfit: (Math.random() * 40000000000 + 5000000000).toFixed(0),
                netIncome: (Math.random() * 25000000000 + 2000000000).toFixed(0)
              }
            }
          }
        },
        Valuation: {
          TrailingPE: parseFloat((15 + Math.random() * 25).toFixed(2)),
          ForwardPE: parseFloat((12 + Math.random() * 20).toFixed(2)),
          PriceSalesTrailing12Months: parseFloat((3 + Math.random() * 10).toFixed(2)),
          PriceBookMRQ: parseFloat((2 + Math.random() * 8).toFixed(2))
        }
      };

    case '/api/div/{symbol}':
      const numDividends = 4;
      return Array.from({ length: numDividends }, (_, i) => {
        const exDate = new Date(today);
        exDate.setMonth(exDate.getMonth() - i * 3);
        
        const recordDate = new Date(exDate);
        recordDate.setDate(recordDate.getDate() + 2);
        
        const paymentDate = new Date(recordDate);
        paymentDate.setDate(paymentDate.getDate() + 3);
        
        const declarationDate = new Date(exDate);
        declarationDate.setDate(declarationDate.getDate() - 30);
        
        return {
          date: formatDate(exDate),
          declarationDate: formatDate(declarationDate),
          recordDate: formatDate(recordDate),
          paymentDate: formatDate(paymentDate),
          period: `Q${4 - i}`,
          value: parseFloat((0.15 + Math.random() * 0.2).toFixed(2)),
          unadjustedValue: parseFloat((0.15 + Math.random() * 0.2).toFixed(2)),
          currency: "USD"
        };
      });

    case '/api/splits/{symbol}':
      // Most stocks don't have recent splits, so return empty or occasional split
      if (Math.random() > 0.8) {
        return [
          {
            date: formatDate(new Date(today.getTime() - 365 * 24 * 3600000)),
            split: Math.random() > 0.5 ? "2:1" : "4:1"
          }
        ];
      }
      return [];

    case '/api/technical/{symbol}':
      const func = args.function || 'sma';
      const periodVal = parseInt(args.period) || 14;
      const technicalDays = 30;
      
      return Array.from({ length: technicalDays }, (_, i) => {
        const date = new Date(today);
        date.setDate(date.getDate() - (technicalDays - i - 1));
        
        let value;
        switch (func) {
          case 'sma':
          case 'ema':
            value = getBasePrice(symbol.split('.')[0]) * (0.95 + Math.random() * 0.1);
            break;
          case 'rsi':
            value = 30 + Math.random() * 40; // RSI between 30-70
            break;
          case 'macd':
            value = -2 + Math.random() * 4; // MACD can be negative or positive
            break;
          default:
            value = Math.random() * 100;
        }
        
        return {
          date: formatDate(date),
          [func]: parseFloat(value.toFixed(4))
        };
      });

    case '/api/screener':
      const limit = parseInt(args.limit) || 50;
      const sampleStocks = [
        'AAPL.US', 'MSFT.US', 'GOOGL.US', 'AMZN.US', 'TSLA.US', 
        'NVDA.US', 'META.US', 'NFLX.US', 'CRM.US', 'ORCL.US'
      ];
      
      return sampleStocks.slice(0, limit).map(sym => {
        const stockSymbol = sym.split('.')[0];
        const price = getBasePrice(stockSymbol);
        
        return {
          code: sym,
          name: getCompanyName(stockSymbol),
          market_cap: Math.floor(Math.random() * 3000000000000) + 50000000000,
          pe_ratio: parseFloat((10 + Math.random() * 30).toFixed(2)),
          dividend_yield: parseFloat((Math.random() * 0.06).toFixed(4)),
          price: parseFloat(price.toFixed(2)),
          change_p: parseFloat((Math.random() * 10 - 5).toFixed(2)),
          volume: Math.floor(Math.random() * 50000000) + 1000000
        };
      });

    case '/api/search/{query}':
      const query = args.query || 'apple';
      const results = [];
      
      // Generate some matching results based on query
      if (query.toLowerCase().includes('apple') || query.toLowerCase().includes('aapl')) {
        results.push({
          Code: "AAPL.US",
          Name: "Apple Inc",
          Country: "USA",
          Exchange: "NASDAQ",
          Currency: "USD",
          Type: "Common Stock"
        });
      }
      
      if (query.toLowerCase().includes('microsoft') || query.toLowerCase().includes('msft')) {
        results.push({
          Code: "MSFT.US",
          Name: "Microsoft Corporation",
          Country: "USA",
          Exchange: "NASDAQ",
          Currency: "USD",
          Type: "Common Stock"
        });
      }
      
      // Add some generic results
      const genericStocks = ['GOOGL.US', 'TSLA.US', 'AMZN.US'];
      genericStocks.forEach(stock => {
        const symbol = stock.split('.')[0];
        results.push({
          Code: stock,
          Name: getCompanyName(symbol),
          Country: "USA",
          Exchange: "NASDAQ",
          Currency: "USD",
          Type: "Common Stock"
        });
      });
      
      return results.slice(0, 10);

    case '/api/exchanges-list':
      return [
        {
          Name: "New York Stock Exchange",
          Code: "NYSE",
          OperatingMIC: "XNYS",
          Country: "USA",
          Currency: "USD",
          CountryISO2: "US",
          CountryISO3: "USA"
        },
        {
          Name: "NASDAQ Global Market",
          Code: "NASDAQ",
          OperatingMIC: "XNAS",
          Country: "USA",
          Currency: "USD",
          CountryISO2: "US",
          CountryISO3: "USA"
        },
        {
          Name: "London Stock Exchange",
          Code: "LSE",
          OperatingMIC: "XLON",
          Country: "UK",
          Currency: "GBP",
          CountryISO2: "GB",
          CountryISO3: "GBR"
        }
      ];

    case '/api/etf/{symbol}':
      const etfSymbol = symbol.split('.')[0];
      return {
        General: {
          Code: etfSymbol,
          Name: getETFName(etfSymbol),
          Family: "State Street Global Advisors",
          Net_Assets: Math.floor(Math.random() * 500000000000) + 10000000000,
          Expense_Ratio: parseFloat((0.03 + Math.random() * 0.5).toFixed(4))
        },
        Holdings: [
          {
            Symbol: "AAPL.US",
            Name: "Apple Inc",
            Weight: parseFloat((5 + Math.random() * 5).toFixed(2)),
            Shares: Math.floor(Math.random() * 200000000) + 10000000
          },
          {
            Symbol: "MSFT.US",
            Name: "Microsoft Corporation",
            Weight: parseFloat((4 + Math.random() * 4).toFixed(2)),
            Shares: Math.floor(Math.random() * 150000000) + 8000000
          },
          {
            Symbol: "GOOGL.US",
            Name: "Alphabet Inc",
            Weight: parseFloat((3 + Math.random() * 3).toFixed(2)),
            Shares: Math.floor(Math.random() * 100000000) + 5000000
          }
        ],
        SectorWeights: {
          Technology: parseFloat((25 + Math.random() * 10).toFixed(1)),
          Healthcare: parseFloat((12 + Math.random() * 6).toFixed(1)),
          "Financial Services": parseFloat((10 + Math.random() * 8).toFixed(1)),
          "Consumer Cyclical": parseFloat((8 + Math.random() * 6).toFixed(1)),
          "Consumer Defensive": parseFloat((6 + Math.random() * 4).toFixed(1))
        }
      };

    case '/api/insider-transactions':
      const numTransactions = 10;
      return Array.from({ length: numTransactions }, (_, i) => {
        const transactionDate = new Date(today);
        transactionDate.setDate(transactionDate.getDate() - i * 7);
        
        const filingDate = new Date(transactionDate);
        filingDate.setDate(filingDate.getDate() + 2);
        
        return {
          symbol: symbol,
          filingDate: formatDate(filingDate),
          transactionDate: formatDate(transactionDate),
          owner: generateInsiderName(),
          relationship: ["Chief Executive Officer", "Chief Financial Officer", "Director", "Chief Operating Officer"][i % 4],
          transactionType: Math.random() > 0.5 ? "Sale" : "Purchase",
          securitiesOwned: Math.floor(Math.random() * 500000) + 10000,
          securitiesTransacted: Math.floor(Math.random() * 50000) + 1000,
          price: parseFloat((50 + Math.random() * 200).toFixed(2)),
          securityTitle: "Common Stock"
        };
      });

    case '/api/short-interest/{symbol}':
      const numReports = 6;
      return Array.from({ length: numReports }, (_, i) => {
        const date = new Date(today);
        date.setDate(date.getDate() - i * 15); // Bi-weekly reports
        
        const shortInterest = Math.floor(Math.random() * 200000000) + 10000000;
        const sharesOutstanding = Math.floor(Math.random() * 20000000000) + 1000000000;
        const shortRatio = shortInterest / sharesOutstanding * 100;
        
        return {
          symbol: symbol,
          date: formatDate(date),
          shortInterest,
          sharesOutstanding,
          shortRatio: parseFloat((1 + Math.random() * 8).toFixed(1)),
          percentOfFloat: parseFloat((shortRatio * 10).toFixed(2)),
          daysTocover: parseFloat((1 + Math.random() * 10).toFixed(1))
        };
      });

    case '/api/macro-indicator/{indicator}':
      const indicator = args.indicator || 'GDPUS.FRED';
      const numDataPoints = 20;
      
      return Array.from({ length: numDataPoints }, (_, i) => {
        const date = new Date(today);
        date.setMonth(date.getMonth() - i);
        
        let value;
        switch (indicator) {
          case 'GDPUS.FRED':
            value = 20000 + Math.random() * 5000; // GDP in billions
            break;
          case 'UNRATE.FRED':
            value = 3 + Math.random() * 4; // Unemployment rate 3-7%
            break;
          case 'CPIAUCSL.FRED':
            value = 250 + Math.random() * 50; // CPI
            break;
          case 'FEDFUNDS.FRED':
            value = 2 + Math.random() * 4; // Fed funds rate 2-6%
            break;
          default:
            value = Math.random() * 1000;
        }
        
        return {
          date: formatDate(date),
          value: parseFloat(value.toFixed(2)),
          indicator: indicator.split('.')[0]
        };
      });

    case '/api/calendar/{symbol}':
      // Generate earnings dates for next few quarters
      return Array.from({ length: 4 }, (_, i) => {
        const earningsDate = new Date(today);
        earningsDate.setMonth(earningsDate.getMonth() + i * 3);
        
        return {
          symbol: symbol,
          name: getCompanyName(symbol.split('.')[0]),
          date: formatDate(earningsDate),
          time: "after_market_close",
          period: `Q${i + 1}`,
          estimate: parseFloat((1 + Math.random() * 3).toFixed(2)),
          currency: "USD"
        };
      });

    default:
      return { error: `Mock data not implemented for endpoint: ${endpoint}` };
  }
}

// Helper functions
function getBasePrice(symbol) {
  const prices = {
    AAPL: 185.64,
    TSLA: 248.50,
    SPY: 451.23,
    MSFT: 374.58,
    GOOGL: 134.12,
    AMZN: 146.80,
    NVDA: 481.45,
    META: 325.67,
    NFLX: 432.18,
    CRM: 251.34,
    ORCL: 112.45
  };
  return prices[symbol] || (100 + Math.random() * 200);
}

function getCompanyName(symbol) {
  const names = {
    AAPL: "Apple Inc.",
    TSLA: "Tesla, Inc.",
    SPY: "SPDR S&P 500 ETF Trust",
    MSFT: "Microsoft Corporation",
    GOOGL: "Alphabet Inc.",
    AMZN: "Amazon.com, Inc.",
    NVDA: "NVIDIA Corporation",
    META: "Meta Platforms, Inc.",
    NFLX: "Netflix, Inc.",
    CRM: "Salesforce, Inc.",
    ORCL: "Oracle Corporation"
  };
  return names[symbol] || `${symbol} Corporation`;
}

function getIndustry(symbol) {
  const industries = {
    AAPL: "Consumer Electronics",
    TSLA: "Auto Manufacturers",
    MSFT: "Software—Infrastructure",
    GOOGL: "Internet Content & Information",
    AMZN: "Internet Retail",
    NVDA: "Semiconductors",
    META: "Internet Content & Information",
    NFLX: "Entertainment",
    CRM: "Software—Application",
    ORCL: "Software—Infrastructure"
  };
  return industries[symbol] || "Technology";
}

function getETFName(symbol) {
  const names = {
    SPY: "SPDR S&P 500 ETF Trust",
    QQQ: "Invesco QQQ Trust",
    VTI: "Vanguard Total Stock Market ETF",
    IWM: "iShares Russell 2000 ETF"
  };
  return names[symbol] || `${symbol} ETF`;
}

function formatDate(date) {
  return date.toISOString().split('T')[0];
}

function formatDateTime(date) {
  return date.toISOString();
}

function formatQuarter(date) {
  const year = date.getFullYear();
  const quarter = Math.floor(date.getMonth() / 3) + 1;
  return `${year}-${String(quarter * 3).padStart(2, '0')}-30`;
}

function generateISIN(symbol) {
  // Simplified ISIN generation
  return `US${symbol.padEnd(7, '0').substring(0, 7)}05`;
}

function generateCUSIP(symbol) {
  // Simplified CUSIP generation  
  return `${symbol.padEnd(6, '0').substring(0, 6)}100`;
}

function generateNewsHeadline(symbol) {
  const headlines = [
    `${getCompanyName(symbol)} Reports Strong Quarterly Earnings`,
    `${getCompanyName(symbol)} Announces New Product Launch`,
    `Analysts Upgrade ${getCompanyName(symbol)} Price Target`,
    `${getCompanyName(symbol)} Beats Revenue Expectations`,
    `${getCompanyName(symbol)} Expands Into New Markets`
  ];
  return headlines[Math.floor(Math.random() * headlines.length)];
}

function generateNewsSummary(symbol) {
  return `${getCompanyName(symbol)} announced strong financial results, exceeding analyst expectations across key metrics...`;
}

function generateNewsContent(symbol) {
  return `${getCompanyName(symbol)} today reported financial results for the quarter, showing continued growth and strong performance across all business segments. The company's innovative approach and strategic investments have positioned it well for future growth...`;
}

function generateInsiderName() {
  const firstNames = ['John', 'Jane', 'Michael', 'Sarah', 'David', 'Lisa', 'Robert', 'Jennifer'];
  const lastNames = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis'];
  
  return `${firstNames[Math.floor(Math.random() * firstNames.length)]} ${lastNames[Math.floor(Math.random() * lastNames.length)]}`;
}

function getNextMarketOpen(now) {
  const next = new Date(now);
  if (now.getDay() === 6) { // Saturday
    next.setDate(next.getDate() + 2);
  } else if (now.getDay() === 0) { // Sunday
    next.setDate(next.getDate() + 1);
  } else if (now.getHours() >= 16) { // After market close
    next.setDate(next.getDate() + 1);
  }
  next.setHours(9, 30, 0, 0);
  return next.toISOString();
}

function getNextMarketClose(now) {
  const next = new Date(now);
  if (now.getDay() === 6) { // Saturday
    next.setDate(next.getDate() + 2);
  } else if (now.getDay() === 0) { // Sunday
    next.setDate(next.getDate() + 1);
  } else if (now.getHours() >= 16) { // After market close
    next.setDate(next.getDate() + 1);
  }
  next.setHours(16, 0, 0, 0);
  return next.toISOString();
}