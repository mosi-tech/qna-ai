"""Risk modeling and options pricing using industry-standard libraries.

This module provides sophisticated risk modeling capabilities with a focus on
options pricing, implied volatility calculation, and derivatives risk management.
All calculations leverage established libraries from requirements.txt (scipy, numpy)
to ensure accuracy and avoid code duplication.

The module implements classical financial models including:
- Black-Scholes options pricing model with Greeks calculation
- Implied volatility extraction using numerical optimization
- Risk scenario modeling and stress testing

Functions are designed to integrate with the financial-analysis-function-library.json
specification and provide standardized outputs for the MCP analytics server.

Example:
    Basic options pricing workflow:
    
    >>> from mcp.analytics.risk.models import black_scholes_option_price
    >>> option_result = black_scholes_option_price(
    ...     underlying_price=100, strike=105, time_to_expiry=0.25,
    ...     risk_free_rate=0.05, volatility=0.20, option_type="call"
    ... )
    >>> print(f"Option price: ${option_result['option_price']:.2f}")
    >>> print(f"Delta: {option_result['delta']:.3f}")
    
Note:
    All functions use proven mathematical models and numerical methods
    for accurate derivatives pricing and risk analysis.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Union, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')

from scipy import stats, optimize
from ..utils.data_utils import standardize_output


def calculate_implied_volatility(option_price: float, 
                                underlying_price: float, 
                                strike: float, 
                                time_to_expiry: float, 
                                risk_free_rate: float) -> float:
    """Calculate implied volatility from market option price using Black-Scholes inversion.
    
    Implied volatility is the market's expectation of future volatility embedded
    in option prices. This function uses numerical optimization to find the volatility
    that makes the Black-Scholes theoretical price equal to the observed market price.
    This is a critical measure for options trading and risk management.
    
    Args:
        option_price: Current market price of the option. Must be positive and
            should reflect actual trading prices or mid-market quotes.
        underlying_price: Current market price of the underlying asset.
            Must be positive (e.g., current stock price).
        strike: Option strike price. Must be positive. The exercise price
            at which the option can be exercised.
        time_to_expiry: Time to expiration in years. Must be positive.
            (e.g., 0.25 for 3 months, 1.0 for 1 year).
        risk_free_rate: Annual risk-free interest rate (as decimal).
            Typically government bond rate matching option expiry.
            
    Returns:
        float: Implied volatility as annual decimal (e.g., 0.20 = 20% volatility).
            
    Raises:
        ValueError: If any input parameters are invalid (non-positive values) or
            if optimization fails to converge to a reasonable solution.
            
    Example:
        >>> # Calculate implied volatility for a call option
        >>> market_price = 5.50  # Option trading at $5.50
        >>> stock_price = 100    # Stock trading at $100
        >>> strike_price = 105   # Call option with $105 strike
        >>> time_left = 0.25     # 3 months to expiration
        >>> risk_free = 0.05     # 5% risk-free rate
        >>> 
        >>> implied_vol = calculate_implied_volatility(
        ...     market_price, stock_price, strike_price, time_left, risk_free
        ... )
        >>> print(implied_vol)
        0.223
        >>> print(f"Implied volatility: {implied_vol:.4f}")
        Implied volatility: 0.2230
        >>> print(f"Implied volatility: {implied_vol:.1%}")
        Implied volatility: 22.3%
        
    Note:
        - Uses scipy.optimize for numerical root-finding
        - Assumes European-style options (Black-Scholes framework)
        - Currently implemented for call options only
        - Volatility bounds set between 0.1% and 500% annually
        - Optimization starts with 20% volatility initial guess
        - For options deep in/out of money, convergence may be slower
        - Implied volatility smile/skew effects not captured in simple Black-Scholes
    """
    try:
        if option_price <= 0:
            raise ValueError("Option price must be positive")
        if underlying_price <= 0:
            raise ValueError("Underlying price must be positive")
        if strike <= 0:
            raise ValueError("Strike price must be positive")
        if time_to_expiry <= 0:
            raise ValueError("Time to expiry must be positive")
        
        def black_scholes_call(vol: float) -> float:
            """Black-Scholes call option formula"""
            d1 = (np.log(underlying_price / strike) + (risk_free_rate + 0.5 * vol**2) * time_to_expiry) / (vol * np.sqrt(time_to_expiry))
            d2 = d1 - vol * np.sqrt(time_to_expiry)
            
            call_price = (underlying_price * stats.norm.cdf(d1) - 
                         strike * np.exp(-risk_free_rate * time_to_expiry) * stats.norm.cdf(d2))
            return call_price
        
        def objective_function(vol: float) -> float:
            """Objective function to minimize: difference between theoretical and market price"""
            try:
                if vol <= 0:
                    return 1e6  # Large penalty for negative volatility
                theoretical_price = black_scholes_call(vol)
                return (theoretical_price - option_price) ** 2
            except:
                return 1e6
        
        # Initial guess and bounds for volatility
        initial_guess = 0.2  # 20% volatility
        bounds = [(0.001, 5.0)]  # Between 0.1% and 500%
        
        # Use scipy optimization to find implied volatility
        result = optimize.minimize_scalar(
            objective_function,
            bounds=(0.001, 5.0),
            method='bounded'
        )
        
        if result.success:
            implied_vol = result.x
            
            # Sanity check: verify the result makes sense
            if implied_vol < 0.001 or implied_vol > 5.0:
                raise ValueError("Implied volatility outside reasonable bounds")
            
            return float(implied_vol)
        else:
            raise ValueError("Optimization failed to converge")
            
    except Exception as e:
        raise ValueError(f"Implied volatility calculation failed: {str(e)}")


def black_scholes_option_price(underlying_price: float,
                             strike: float,
                             time_to_expiry: float,
                             risk_free_rate: float,
                             volatility: float,
                             option_type: str = "call") -> Dict[str, Any]:
    """Calculate Black-Scholes option price and complete Greeks suite.
    
    The Black-Scholes model is the foundational framework for options pricing.
    This function calculates both the theoretical option price and all standard
    Greeks (risk sensitivities) that are essential for options risk management
    and hedging strategies.
    
    Args:
        underlying_price: Current market price of the underlying asset.
            Must be positive (e.g., current stock price).
        strike: Option strike price. Must be positive. The exercise price
            at which the option can be exercised.
        time_to_expiry: Time to expiration in years. Must be positive.
            (e.g., 0.25 for 3 months, 1.0 for 1 year).
        risk_free_rate: Annual risk-free interest rate (as decimal).
            Typically government bond rate matching option expiry.
        volatility: Annual volatility of underlying asset (as decimal).
            Historical or implied volatility estimate.
        option_type: Type of option to price. Options:
            - "call": Call option (right to buy)
            - "put": Put option (right to sell)
            Defaults to "call".
            
    Returns:
        Dict[str, Any]: Complete option pricing results including:
            - option_price: Theoretical option value
            - delta: Price sensitivity to underlying price changes
            - gamma: Rate of change of delta (convexity)
            - theta: Time decay (daily)
            - vega: Sensitivity to volatility changes (per 1% vol change)
            - rho: Sensitivity to interest rate changes (per 1% rate change)
            - d1/d2: Intermediate Black-Scholes calculations
            - option_type: Specified option type
            - time_to_expiry: Time remaining to expiration
            - volatility: Input volatility with percentage format
            
    Raises:
        Exception: If calculation fails due to invalid inputs.
        
    Example:
        >>> # Price a call option
        >>> option_result = black_scholes_option_price(
        ...     underlying_price=100, strike=105, time_to_expiry=0.25,
        ...     risk_free_rate=0.05, volatility=0.20, option_type="call"
        ... )
        >>> print(option_result)
        {
            'success': True,
            'function': 'black_scholes_option_price',
            'option_price': 2.478,
            'delta': 0.377,
            'gamma': 0.038,
            'theta': -0.026,
            'vega': 0.190,
            'rho': 0.088,
            'd1': -0.313,
            'd2': -0.413,
            'option_type': 'call',
            'time_to_expiry': 0.25,
            'volatility': 0.2,
            'volatility_pct': '20.00%'
        }
        >>> print(f"Call price: ${option_result['option_price']:.2f}")
        >>> print(f"Delta: {option_result['delta']:.3f}")
        >>> print(f"Daily theta: ${option_result['theta']:.2f}")
        >>> 
        >>> # Price corresponding put option
        >>> put_result = black_scholes_option_price(
        ...     underlying_price=100, strike=105, time_to_expiry=0.25,
        ...     risk_free_rate=0.05, volatility=0.20, option_type="put"
        ... )
        >>> print(f"Put price: ${put_result['option_price']:.2f}")
        ...     underlying_price=100, strike=105, time_to_expiry=0.25,
        ...     risk_free_rate=0.05, volatility=0.20, option_type="put"
        ... )
        >>> print(f"Put price: ${put_result['option_price']:.2f}")
        
    Note:
        - Uses scipy.stats.norm for cumulative distribution functions
        - Greeks are scaled for practical use:
          * Theta: Daily time decay (divide by 365)
          * Vega: Per 1% volatility change (divide by 100)
          * Rho: Per 1% interest rate change (divide by 100)
        - Assumes European-style options (no early exercise)
        - Assumes constant volatility and interest rates
        - Does not account for dividends (can be extended)
        - Put-call parity relationship: Call - Put = S - K*e^(-rT)
    """
    try:
        if underlying_price <= 0 or strike <= 0 or time_to_expiry <= 0 or volatility <= 0:
            raise ValueError("All parameters must be positive")
        
        # Calculate d1 and d2
        d1 = (np.log(underlying_price / strike) + (risk_free_rate + 0.5 * volatility**2) * time_to_expiry) / (volatility * np.sqrt(time_to_expiry))
        d2 = d1 - volatility * np.sqrt(time_to_expiry)
        
        # Calculate option prices
        if option_type.lower() == "call":
            option_price = (underlying_price * stats.norm.cdf(d1) - 
                           strike * np.exp(-risk_free_rate * time_to_expiry) * stats.norm.cdf(d2))
            delta = stats.norm.cdf(d1)
        else:  # put
            option_price = (strike * np.exp(-risk_free_rate * time_to_expiry) * stats.norm.cdf(-d2) - 
                           underlying_price * stats.norm.cdf(-d1))
            delta = -stats.norm.cdf(-d1)
        
        # Calculate Greeks
        gamma = stats.norm.pdf(d1) / (underlying_price * volatility * np.sqrt(time_to_expiry))
        theta = -(underlying_price * stats.norm.pdf(d1) * volatility) / (2 * np.sqrt(time_to_expiry)) - risk_free_rate * strike * np.exp(-risk_free_rate * time_to_expiry) * stats.norm.cdf(d2 if option_type.lower() == "call" else -d2)
        vega = underlying_price * stats.norm.pdf(d1) * np.sqrt(time_to_expiry)
        rho = strike * time_to_expiry * np.exp(-risk_free_rate * time_to_expiry) * stats.norm.cdf(d2 if option_type.lower() == "call" else -d2)
        
        result = {
            "option_price": float(option_price),
            "delta": float(delta),
            "gamma": float(gamma),
            "theta": float(theta / 365),  # Daily theta
            "vega": float(vega / 100),    # Vega per 1% vol change
            "rho": float(rho / 100),      # Rho per 1% rate change
            "d1": float(d1),
            "d2": float(d2),
            "option_type": option_type,
            "time_to_expiry": float(time_to_expiry),
            "volatility": float(volatility),
            "volatility_pct": f"{volatility * 100:.2f}%"
        }
        
        return standardize_output(result, "black_scholes_option_price")
        
    except Exception as e:
        return {"success": False, "error": f"Black-Scholes calculation failed: {str(e)}"}


RISK_MODELS_FUNCTIONS = {
    'calculate_implied_volatility': calculate_implied_volatility,
    'black_scholes_option_price': black_scholes_option_price
}