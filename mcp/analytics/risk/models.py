"""
Risk Models using scipy and empyrical

Risk modeling functions using libraries from requirements.txt
From financial-analysis-function-library.json
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
    """
    Calculate implied volatility from option price using Black-Scholes model.
    
    From financial-analysis-function-library.json specialized_analysis category
    Uses scipy for numerical optimization - no code duplication
    
    Args:
        option_price: Current option price
        underlying_price: Current underlying asset price
        strike: Option strike price
        time_to_expiry: Time to expiration in years
        risk_free_rate: Risk-free interest rate
        
    Returns:
        float: Implied volatility
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
    """
    Calculate Black-Scholes option price and Greeks.
    
    Helper function for options pricing models
    Uses scipy for statistical calculations - no code duplication
    
    Args:
        underlying_price: Current underlying asset price
        strike: Option strike price
        time_to_expiry: Time to expiration in years
        risk_free_rate: Risk-free interest rate
        volatility: Volatility of underlying asset
        option_type: "call" or "put"
        
    Returns:
        Dict: Option price and Greeks
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