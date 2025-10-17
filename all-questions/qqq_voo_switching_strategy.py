import json
import random
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any
import statistics

def mock_get_historical_prices(symbol: str, start_date: str, end_date: str, frequency: str = "daily") -> List[Dict[str, Any]]:
    """
    Mock function to simulate historical price data retrieval.
    
    Args:
        symbol: Stock symbol (e.g., 'QQQ', 'VOO')
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        frequency: Data frequency ('daily', 'weekly')
    
    Returns:
        List of price data dictionaries with date, open, high, low, close, volume
    """
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    
    # Base prices for different symbols
    base_prices = {'QQQ': 350.0, 'VOO': 400.0}
    base_price = base_prices.get(symbol, 100.0)
    
    prices = []
    current_date = start
    current_price = base_price
    
    # Generate mock daily data
    while current_date <= end:
        # Simulate price movement with some volatility
        daily_return = random.normalvariate(0.0008, 0.015)  # ~0.08% daily return, 1.5% daily volatility
        current_price *= (1 + daily_return)
        
        # Generate OHLC data
        high = current_price * (1 + abs(random.normalvariate(0, 0.005)))
        low = current_price * (1 - abs(random.normalvariate(0, 0.005)))
        open_price = current_price * (1 + random.normalvariate(0, 0.003))
        
        prices.append({
            'date': current_date.strftime("%Y-%m-%d"),
            'open': round(open_price, 2),
            'high': round(high, 2),
            'low': round(low, 2),
            'close': round(current_price, 2),
            'volume': random.randint(50000000, 200000000)
        })
        
        current_date += timedelta(days=1)
    
    return prices

def calculate_rolling_weekly_returns(prices: List[Dict[str, Any]], window_days: int = 7) -> List[Dict[str, Any]]:
    """
    Calculate rolling weekly returns from daily price data.
    
    Args:
        prices: List of daily price dictionaries
        window_days: Number of days for rolling calculation
    
    Returns:
        List of dictionaries with date and rolling_weekly_return
    """
    rolling_returns = []
    
    for i in range(window_days, len(prices)):
        current_price = prices[i]['close']
        past_price = prices[i - window_days]['close']
        weekly_return = (current_price - past_price) / past_price
        
        rolling_returns.append({
            'date': prices[i]['date'],
            'rolling_weekly_return': round(weekly_return, 6),
            'current_price': current_price
        })
    
    return rolling_returns

def simulate_switching_strategy(
    primary_symbol: str = "QQQ",
    secondary_symbol: str = "VOO", 
    start_date: str = "2020-01-01",
    end_date: str = "2023-12-31",
    switching_threshold: float = -0.03,
    initial_investment: float = 10000.0,
    monthly_contribution: float = 1000.0
) -> Dict[str, Any]:
    """
    Simulate a monthly switching strategy between two ETFs based on rolling weekly returns.
    
    Args:
        primary_symbol: Primary ETF symbol (default: QQQ)
        secondary_symbol: Secondary ETF symbol to switch to (default: VOO)
        start_date: Strategy start date
        end_date: Strategy end date
        switching_threshold: Weekly return threshold for switching (default: -3%)
        initial_investment: Initial investment amount
        monthly_contribution: Monthly contribution amount
    
    Returns:
        Comprehensive analysis results as dictionary
    """
    
    # Get historical data for both symbols
    primary_prices = mock_get_historical_prices(primary_symbol, start_date, end_date)
    secondary_prices = mock_get_historical_prices(secondary_symbol, start_date, end_date)
    
    # Calculate rolling weekly returns for primary symbol
    primary_rolling_returns = calculate_rolling_weekly_returns(primary_prices)
    
    # Create price lookup dictionaries
    primary_price_lookup = {item['date']: item['close'] for item in primary_prices}
    secondary_price_lookup = {item['date']: item['close'] for item in secondary_prices}
    rolling_returns_lookup = {item['date']: item['rolling_weekly_return'] for item in primary_rolling_returns}
    
    # Simulation variables
    portfolio_value = initial_investment
    cash = 0.0
    primary_shares = 0.0
    secondary_shares = 0.0
    current_holding = primary_symbol
    
    # Track portfolio history
    portfolio_history = []
    transactions = []
    monthly_contributions = []
    switching_events = []
    
    # Get monthly dates for contributions
    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = datetime.strptime(end_date, "%Y-%m-%d")
    
    current_date = start_dt
    monthly_dates = []
    while current_date <= end_dt:
        monthly_dates.append(current_date.strftime("%Y-%m-%d"))
        # Move to next month
        if current_date.month == 12:
            current_date = current_date.replace(year=current_date.year + 1, month=1)
        else:
            current_date = current_date.replace(month=current_date.month + 1)
    
    # Initial purchase
    if primary_symbol in primary_price_lookup:
        initial_price = primary_price_lookup[start_date]
        primary_shares = initial_investment / initial_price
        transactions.append({
            'date': start_date,
            'action': 'initial_buy',
            'symbol': primary_symbol,
            'shares': round(primary_shares, 6),
            'price': initial_price,
            'amount': initial_investment
        })
    
    # Process each monthly contribution
    for month_date in monthly_dates[1:]:  # Skip first month (initial investment)
        if month_date not in rolling_returns_lookup:
            continue
            
        # Check if we need to switch based on rolling weekly return
        weekly_return = rolling_returns_lookup[month_date]
        
        # Determine which symbol to buy this month
        target_symbol = secondary_symbol if weekly_return < switching_threshold else primary_symbol
        
        # Record switching event if different from current holding
        if target_symbol != current_holding:
            switching_events.append({
                'date': month_date,
                'from_symbol': current_holding,
                'to_symbol': target_symbol,
                'trigger_return': round(weekly_return, 6),
                'threshold': switching_threshold
            })
            current_holding = target_symbol
        
        # Make monthly purchase
        if target_symbol == primary_symbol and month_date in primary_price_lookup:
            price = primary_price_lookup[month_date]
            shares_bought = monthly_contribution / price
            primary_shares += shares_bought
            
            transactions.append({
                'date': month_date,
                'action': 'monthly_buy',
                'symbol': primary_symbol,
                'shares': round(shares_bought, 6),
                'price': price,
                'amount': monthly_contribution
            })
            
        elif target_symbol == secondary_symbol and month_date in secondary_price_lookup:
            price = secondary_price_lookup[month_date]
            shares_bought = monthly_contribution / price
            secondary_shares += shares_bought
            
            transactions.append({
                'date': month_date,
                'action': 'monthly_buy',
                'symbol': secondary_symbol,
                'shares': round(shares_bought, 6),
                'price': price,
                'amount': monthly_contribution
            })
        
        monthly_contributions.append({
            'date': month_date,
            'amount': monthly_contribution,
            'target_symbol': target_symbol,
            'weekly_return': round(weekly_return, 6)
        })
        
        # Calculate portfolio value
        primary_value = primary_shares * primary_price_lookup.get(month_date, 0)
        secondary_value = secondary_shares * secondary_price_lookup.get(month_date, 0)
        total_value = primary_value + secondary_value
        
        portfolio_history.append({
            'date': month_date,
            'primary_shares': round(primary_shares, 6),
            'secondary_shares': round(secondary_shares, 6),
            'primary_value': round(primary_value, 2),
            'secondary_value': round(secondary_value, 2),
            'total_value': round(total_value, 2),
            'weekly_return': round(weekly_return, 6)
        })
    
    # Calculate final metrics
    total_invested = initial_investment + (monthly_contribution * (len(monthly_dates) - 1))
    final_primary_value = primary_shares * primary_price_lookup.get(end_date, primary_price_lookup[max(primary_price_lookup.keys())])
    final_secondary_value = secondary_shares * secondary_price_lookup.get(end_date, secondary_price_lookup[max(secondary_price_lookup.keys())])
    final_portfolio_value = final_primary_value + final_secondary_value
    
    total_return = (final_portfolio_value - total_invested) / total_invested
    
    # Calculate comparison: buy and hold primary only
    buy_hold_shares = total_invested / statistics.mean([primary_price_lookup[date] for date in monthly_dates if date in primary_price_lookup])
    buy_hold_final_value = buy_hold_shares * primary_price_lookup.get(end_date, primary_price_lookup[max(primary_price_lookup.keys())])
    buy_hold_return = (buy_hold_final_value - total_invested) / total_invested
    
    # Compile comprehensive results
    results = {
        'strategy_parameters': {
            'primary_symbol': primary_symbol,
            'secondary_symbol': secondary_symbol,
            'start_date': start_date,
            'end_date': end_date,
            'switching_threshold': switching_threshold,
            'initial_investment': initial_investment,
            'monthly_contribution': monthly_contribution
        },
        'performance_summary': {
            'total_invested': round(total_invested, 2),
            'final_portfolio_value': round(final_portfolio_value, 2),
            'total_return': round(total_return, 4),
            'total_return_percentage': round(total_return * 100, 2),
            'buy_hold_final_value': round(buy_hold_final_value, 2),
            'buy_hold_return': round(buy_hold_return, 4),
            'buy_hold_return_percentage': round(buy_hold_return * 100, 2),
            'excess_return': round((total_return - buy_hold_return) * 100, 2),
            'final_primary_shares': round(primary_shares, 6),
            'final_secondary_shares': round(secondary_shares, 6),
            'final_primary_value': round(final_primary_value, 2),
            'final_secondary_value': round(final_secondary_value, 2)
        },
        'switching_analysis': {
            'total_switches': len(switching_events),
            'switches_to_secondary': len([s for s in switching_events if s['to_symbol'] == secondary_symbol]),
            'switches_to_primary': len([s for s in switching_events if s['to_symbol'] == primary_symbol]),
            'average_trigger_return': round(statistics.mean([s['trigger_return'] for s in switching_events]) if switching_events else 0, 6),
            'switching_events': switching_events[:10]  # First 10 events
        },
        'portfolio_allocation': {
            'primary_allocation_percentage': round((final_primary_value / final_portfolio_value) * 100, 2),
            'secondary_allocation_percentage': round((final_secondary_value / final_portfolio_value) * 100, 2)
        },
        'transaction_summary': {
            'total_transactions': len(transactions),
            'initial_purchases': len([t for t in transactions if t['action'] == 'initial_buy']),
            'monthly_purchases': len([t for t in transactions if t['action'] == 'monthly_buy']),
            'primary_purchases': len([t for t in transactions if t['symbol'] == primary_symbol]),
            'secondary_purchases': len([t for t in transactions if t['symbol'] == secondary_symbol])
        },
        'detailed_data': {
            'portfolio_history': portfolio_history[-12:],  # Last 12 months
            'monthly_contributions': monthly_contributions[-12:],  # Last 12 months
            'recent_transactions': transactions[-20:]  # Last 20 transactions
        }
    }
    
    return results

def generate_json_output(results: Dict[str, Any]) -> str:
    """
    Generate comprehensive JSON output with descriptions for retail investors.
    
    Args:
        results: Strategy simulation results
    
    Returns:
        JSON string with structured output
    """
    
    json_output = {
        "description": "Comprehensive analysis of a monthly QQQ-to-VOO switching strategy based on rolling weekly returns. This strategy involves making monthly investments, but switching from QQQ to VOO whenever QQQ's rolling 7-day return falls below -3%. This approach aims to capture growth during strong markets while providing defensive positioning during volatile periods.",
        "body": [
            {
                "key": "strategy_type",
                "value": "Monthly Dollar-Cost Averaging with Tactical Switching",
                "description": f"A systematic investment approach that combines regular monthly contributions with tactical asset allocation between {results['strategy_parameters']['primary_symbol']} and {results['strategy_parameters']['secondary_symbol']} based on short-term momentum signals"
            },
            {
                "key": "switching_threshold",
                "value": f"{results['strategy_parameters']['switching_threshold'] * 100}%",
                "description": f"The rolling 7-day return threshold that triggers switching from {results['strategy_parameters']['primary_symbol']} to {results['strategy_parameters']['secondary_symbol']}. When QQQ's weekly return drops below this level, new monthly investments go into VOO instead"
            },
            {
                "key": "total_invested",
                "value": f"${results['performance_summary']['total_invested']:,.2f}",
                "description": f"Total amount invested over the strategy period, including initial investment of ${results['strategy_parameters']['initial_investment']:,.2f} plus monthly contributions of ${results['strategy_parameters']['monthly_contribution']:,.2f}"
            },
            {
                "key": "final_portfolio_value", 
                "value": f"${results['performance_summary']['final_portfolio_value']:,.2f}",
                "description": "Final value of the portfolio combining all QQQ and VOO holdings at the end of the analysis period"
            },
            {
                "key": "total_return_percentage",
                "value": f"{results['performance_summary']['total_return_percentage']}%",
                "description": "Total percentage return of the switching strategy, calculated as (Final Value - Total Invested) / Total Invested"
            },
            {
                "key": "buy_hold_comparison",
                "value": f"{results['performance_summary']['buy_hold_return_percentage']}%",
                "description": f"Total return if you had simply bought and held {results['strategy_parameters']['primary_symbol']} with the same investment schedule, without any switching"
            },
            {
                "key": "excess_return",
                "value": f"{results['performance_summary']['excess_return']}%",
                "description": "Additional return generated by the switching strategy compared to simple buy-and-hold. Positive values indicate the strategy outperformed"
            },
            {
                "key": "total_switching_events",
                "value": results['switching_analysis']['total_switches'],
                "description": "Number of times the strategy switched between QQQ and VOO due to the rolling weekly return threshold being triggered"
            },
            {
                "key": "switches_to_voo",
                "value": results['switching_analysis']['switches_to_secondary'],
                "description": "Number of times the strategy switched to VOO (defensive positioning) when QQQ showed weakness below the threshold"
            },
            {
                "key": "switches_to_qqq",
                "value": results['switching_analysis']['switches_to_primary'],
                "description": "Number of times the strategy switched back to QQQ when market conditions improved and weekly returns recovered"
            },
            {
                "key": "final_qqq_allocation",
                "value": f"{results['portfolio_allocation']['primary_allocation_percentage']}%",
                "description": "Percentage of final portfolio value held in QQQ shares, reflecting the cumulative impact of switching decisions"
            },
            {
                "key": "final_voo_allocation", 
                "value": f"{results['portfolio_allocation']['secondary_allocation_percentage']}%",
                "description": "Percentage of final portfolio value held in VOO shares, showing defensive allocation accumulated during volatile periods"
            },
            {
                "key": "qqq_shares_owned",
                "value": f"{results['performance_summary']['final_primary_shares']:.6f}",
                "description": "Total number of QQQ shares accumulated through monthly purchases when market conditions were favorable"
            },
            {
                "key": "voo_shares_owned",
                "value": f"{results['performance_summary']['final_secondary_shares']:.6f}", 
                "description": "Total number of VOO shares accumulated through monthly purchases during defensive periods when QQQ showed weakness"
            },
            {
                "key": "average_trigger_return",
                "value": f"{results['switching_analysis']['average_trigger_return'] * 100:.2f}%",
                "description": "Average rolling weekly return that triggered switches to VOO, indicating the typical market condition that prompted defensive positioning"
            },
            {
                "key": "strategy_period",
                "value": f"{results['strategy_parameters']['start_date']} to {results['strategy_parameters']['end_date']}",
                "description": "Time period over which the switching strategy was analyzed and backtested"
            },
            {
                "key": "total_transactions", 
                "value": results['transaction_summary']['total_transactions'],
                "description": "Total number of purchase transactions executed, including initial investment and all monthly contributions"
            },
            {
                "key": "qqq_purchase_frequency",
                "value": f"{(results['transaction_summary']['primary_purchases'] / results['transaction_summary']['total_transactions'] * 100):.1f}%",
                "description": "Percentage of transactions that purchased QQQ, indicating how often market conditions favored growth positioning"
            },
            {
                "key": "voo_purchase_frequency",
                "value": f"{(results['transaction_summary']['secondary_purchases'] / results['transaction_summary']['total_transactions'] * 100):.1f}%", 
                "description": "Percentage of transactions that purchased VOO, showing how often defensive positioning was triggered by market weakness"
            }
        ]
    }
    
    return json.dumps(json_output, indent=2)

# Mock data functions documentation
mock_functions_documentation = {
    "description": "Documentation for mock data functions used in the QQQ-VOO switching strategy analysis",
    "mock_functions": [
        {
            "function_name": "mock_get_historical_prices",
            "input_parameters": {
                "symbol": "Stock symbol string (e.g., 'QQQ', 'VOO')",
                "start_date": "Start date in YYYY-MM-DD format",
                "end_date": "End date in YYYY-MM-DD format", 
                "frequency": "Data frequency string ('daily', 'weekly')"
            },
            "expected_output": {
                "type": "List[Dict]",
                "structure": [
                    {
                        "date": "YYYY-MM-DD string",
                        "open": "Float - opening price",
                        "high": "Float - daily high price", 
                        "low": "Float - daily low price",
                        "close": "Float - closing price",
                        "volume": "Integer - trading volume"
                    }
                ],
                "sample": [
                    {
                        "date": "2020-01-01",
                        "open": 350.25,
                        "high": 352.10,
                        "low": 349.80,
                        "close": 351.45,
                        "volume": 125000000
                    }
                ]
            },
            "data_generation_logic": "Uses random normal distribution for daily returns (~0.08% mean, 1.5% volatility). Base prices: QQQ=$350, VOO=$400. Generates realistic OHLC data with small intraday movements."
        },
        {
            "function_name": "calculate_rolling_weekly_returns",
            "input_parameters": {
                "prices": "List of daily price dictionaries from mock_get_historical_prices",
                "window_days": "Integer - number of days for rolling calculation (default: 7)"
            },
            "expected_output": {
                "type": "List[Dict]",
                "structure": [
                    {
                        "date": "YYYY-MM-DD string",
                        "rolling_weekly_return": "Float - 7-day rolling return",
                        "current_price": "Float - current closing price"
                    }
                ],
                "sample": [
                    {
                        "date": "2020-01-08",
                        "rolling_weekly_return": -0.025,
                        "current_price": 348.75
                    }
                ]
            },
            "calculation_logic": "Calculates (current_price - price_7_days_ago) / price_7_days_ago for each date starting from day 7"
        }
    ],
    "data_characteristics": {
        "qqq_base_price": 350.0,
        "voo_base_price": 400.0,
        "daily_return_mean": 0.0008,
        "daily_return_volatility": 0.015,
        "volume_range": [50000000, 200000000],
        "intraday_volatility": 0.005
    }
}

if __name__ == "__main__":
    # Run the simulation with default parameters
    results = simulate_switching_strategy()
    
    # Generate and save JSON output
    json_output = generate_json_output(results)
    with open('qqq_voo_strategy_output.json', 'w') as f:
        f.write(json_output)
    
    # Generate and save mock functions documentation
    with open('mock_functions_documentation.json', 'w') as f:
        f.write(json.dumps(mock_functions_documentation, indent=2))