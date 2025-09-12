"""
Portfolio Dashboard and Reporting

Simple, retail-friendly portfolio reports and dashboards.
Focus on actionable insights and plain English summaries.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta


def portfolio_health_dashboard(
    portfolio_value: float,
    current_allocation: Dict[str, float],
    target_allocation: Dict[str, float],
    recent_returns: List[float],
    last_rebalance_days: int = 0
) -> Dict[str, Any]:
    """
    Complete portfolio health dashboard
    
    Perfect for: "How is my portfolio doing overall?"
    
    Args:
        portfolio_value: Total portfolio value
        current_allocation: Current asset percentages
        target_allocation: Target asset percentages
        recent_returns: Recent daily returns (decimal format)
        last_rebalance_days: Days since last rebalancing
        
    Returns:
        Dict with comprehensive portfolio health report
    """
    
    # Calculate portfolio drift
    total_drift = 0
    max_drift = 0
    drift_details = {}
    
    for asset in target_allocation:
        current = current_allocation.get(asset, 0)
        target = target_allocation[asset]
        drift = abs(current - target)
        total_drift += drift
        max_drift = max(max_drift, drift)
        
        drift_details[asset] = {
            "current": f"{current:.1f}%",
            "target": f"{target:.1f}%", 
            "drift": f"{drift:.1f}%",
            "status": "OK" if drift < 5 else "Review" if drift < 10 else "Action Needed"
        }
    
    # Calculate recent performance
    if recent_returns:
        recent_returns_array = np.array(recent_returns)
        
        # Last 30 days performance (assuming daily returns)
        recent_performance = (np.prod(1 + recent_returns_array[-30:]) - 1) * 100 if len(recent_returns_array) >= 30 else 0
        
        # Volatility (annualized)
        volatility = np.std(recent_returns_array) * np.sqrt(252) * 100
        
        # Win rate
        positive_days = np.sum(recent_returns_array > 0)
        win_rate = (positive_days / len(recent_returns_array)) * 100
    else:
        recent_performance = 0
        volatility = 0
        win_rate = 0
    
    # Overall health score (0-100)
    health_score = 100
    health_factors = []
    
    # Deduct points for drift
    if max_drift > 10:
        health_score -= 20
        health_factors.append("High allocation drift detected")
    elif max_drift > 5:
        health_score -= 10
        health_factors.append("Moderate allocation drift")
    
    # Deduct points for not rebalancing
    if last_rebalance_days > 365:
        health_score -= 15
        health_factors.append("Portfolio hasn't been rebalanced in over a year")
    elif last_rebalance_days > 180:
        health_score -= 5
        health_factors.append("Consider rebalancing soon")
    
    # Adjust for recent performance (minor factor)
    if recent_performance < -10:
        health_score -= 5
        health_factors.append("Recent performance below average")
    
    # Determine overall health level
    if health_score >= 90:
        health_level = "Excellent"
        health_color = "green"
    elif health_score >= 80:
        health_level = "Good"
        health_color = "green"
    elif health_score >= 70:
        health_level = "Fair"
        health_color = "yellow"
    else:
        health_level = "Needs Attention"
        health_color = "red"
    
    # Generate action items
    action_items = []
    if max_drift > 5:
        action_items.append("Consider rebalancing to target allocation")
    if last_rebalance_days > 180:
        action_items.append("Schedule portfolio rebalancing")
    if not action_items:
        action_items.append("Portfolio is healthy - continue monitoring")
    
    return {
        "success": True,
        "portfolio_overview": {
            "total_value": f"${portfolio_value:,.0f}",
            "health_score": f"{health_score:.0f}/100",
            "health_level": health_level,
            "health_color": health_color
        },
        "allocation_status": {
            "drift_summary": {
                "total_drift": f"{total_drift:.1f}%",
                "max_single_drift": f"{max_drift:.1f}%",
                "status": "Good" if max_drift < 5 else "Moderate" if max_drift < 10 else "High"
            },
            "allocation_details": drift_details
        },
        "recent_performance": {
            "last_30_days": f"{recent_performance:+.1f}%",
            "volatility": f"{volatility:.1f}%",
            "win_rate": f"{win_rate:.0f}% positive days"
        },
        "maintenance_status": {
            "days_since_rebalance": last_rebalance_days,
            "rebalance_status": "Overdue" if last_rebalance_days > 365 else "Due Soon" if last_rebalance_days > 180 else "Current"
        },
        "action_items": action_items,
        "health_factors": health_factors if health_factors else ["Portfolio is performing well"],
        "plain_english_summary": (
            f"Your ${portfolio_value:,.0f} portfolio has a health score of {health_score:.0f}/100 ({health_level}). "
            f"Maximum allocation drift is {max_drift:.1f}%. "
            f"Recent 30-day performance: {recent_performance:+.1f}%. "
            f"{'Rebalancing recommended' if max_drift > 5 else 'Portfolio is well-balanced'}."
        )
    }


def portfolio_report_card(
    portfolio_returns: List[float],
    benchmark_returns: List[float],
    portfolio_allocation: Dict[str, float],
    fees_paid_annually: float = 0,
    portfolio_name: str = "Your Portfolio"
) -> Dict[str, Any]:
    """
    Generate a portfolio report card with letter grades
    
    Perfect for: "Grade my portfolio like a school report card"
    
    Args:
        portfolio_returns: Portfolio daily returns
        benchmark_returns: Benchmark daily returns (e.g., S&P 500)
        portfolio_allocation: Current portfolio allocation
        fees_paid_annually: Annual fees paid
        portfolio_name: Name of the portfolio
        
    Returns:
        Dict with graded portfolio analysis
    """
    
    port_returns = np.array(portfolio_returns)
    bench_returns = np.array(benchmark_returns)
    
    # Ensure same length
    min_length = min(len(port_returns), len(bench_returns))
    port_returns = port_returns[:min_length]
    bench_returns = bench_returns[:min_length]
    
    # Calculate metrics for grading
    port_annual_return = (np.prod(1 + port_returns) ** (252/len(port_returns)) - 1) * 100
    bench_annual_return = (np.prod(1 + bench_returns) ** (252/len(bench_returns)) - 1) * 100
    
    port_volatility = np.std(port_returns) * np.sqrt(252) * 100
    bench_volatility = np.std(bench_returns) * np.sqrt(252) * 100
    
    # Sharpe ratio (assuming 2% risk-free rate)
    risk_free_rate = 2
    sharpe_ratio = (port_annual_return - risk_free_rate) / port_volatility if port_volatility > 0 else 0
    
    # Alpha (excess return vs benchmark)
    alpha = port_annual_return - bench_annual_return
    
    # Maximum drawdown
    cumulative = np.cumprod(1 + port_returns)
    rolling_max = np.maximum.accumulate(cumulative)
    drawdowns = (cumulative - rolling_max) / rolling_max
    max_drawdown = abs(np.min(drawdowns)) * 100
    
    # Diversification score (simple version)
    num_allocations = len([a for a in portfolio_allocation.values() if a > 5])
    max_allocation = max(portfolio_allocation.values()) if portfolio_allocation else 100
    diversification_score = min(100, (num_allocations * 10) + (100 - max_allocation))
    
    # Grading criteria
    grades = {}
    
    # Performance Grade (vs benchmark)
    if alpha >= 3:
        grades["performance"] = "A+"
    elif alpha >= 1:
        grades["performance"] = "A"
    elif alpha >= -1:
        grades["performance"] = "B"
    elif alpha >= -3:
        grades["performance"] = "C"
    else:
        grades["performance"] = "D"
    
    # Risk Management Grade (based on Sharpe ratio)
    if sharpe_ratio >= 1.5:
        grades["risk_management"] = "A+"
    elif sharpe_ratio >= 1.0:
        grades["risk_management"] = "A"
    elif sharpe_ratio >= 0.5:
        grades["risk_management"] = "B"
    elif sharpe_ratio >= 0.0:
        grades["risk_management"] = "C"
    else:
        grades["risk_management"] = "D"
    
    # Diversification Grade
    if diversification_score >= 90:
        grades["diversification"] = "A+"
    elif diversification_score >= 80:
        grades["diversification"] = "A"
    elif diversification_score >= 70:
        grades["diversification"] = "B"
    elif diversification_score >= 60:
        grades["diversification"] = "C"
    else:
        grades["diversification"] = "D"
    
    # Cost Management Grade (lower fees = better grade)
    portfolio_value = 100000  # Assume for calculation
    fee_percentage = (fees_paid_annually / portfolio_value) * 100 if portfolio_value > 0 else 0
    
    if fee_percentage <= 0.1:
        grades["cost_management"] = "A+"
    elif fee_percentage <= 0.3:
        grades["cost_management"] = "A"
    elif fee_percentage <= 0.75:
        grades["cost_management"] = "B"
    elif fee_percentage <= 1.5:
        grades["cost_management"] = "C"
    else:
        grades["cost_management"] = "D"
    
    # Calculate overall GPA
    grade_points = {"A+": 4.0, "A": 4.0, "B": 3.0, "C": 2.0, "D": 1.0, "F": 0.0}
    gpa = np.mean([grade_points[grade] for grade in grades.values()])
    
    # Overall grade
    if gpa >= 3.7:
        overall_grade = "A"
    elif gpa >= 3.0:
        overall_grade = "B"
    elif gpa >= 2.0:
        overall_grade = "C"
    else:
        overall_grade = "D"
    
    return {
        "success": True,
        "report_card": {
            "portfolio_name": portfolio_name,
            "overall_grade": overall_grade,
            "gpa": f"{gpa:.1f}/4.0",
            "analysis_period": f"{len(port_returns)} trading days"
        },
        "subject_grades": {
            "Performance vs Benchmark": {
                "grade": grades["performance"],
                "score": f"{alpha:+.1f}% annually",
                "explanation": _grade_explanation("performance", grades["performance"], alpha)
            },
            "Risk Management": {
                "grade": grades["risk_management"], 
                "score": f"Sharpe ratio: {sharpe_ratio:.2f}",
                "explanation": _grade_explanation("risk", grades["risk_management"], sharpe_ratio)
            },
            "Diversification": {
                "grade": grades["diversification"],
                "score": f"{diversification_score:.0f}/100",
                "explanation": _grade_explanation("diversification", grades["diversification"], diversification_score)
            },
            "Cost Management": {
                "grade": grades["cost_management"],
                "score": f"{fee_percentage:.2f}% annually",
                "explanation": _grade_explanation("cost", grades["cost_management"], fee_percentage)
            }
        },
        "key_metrics": {
            "annual_return": f"{port_annual_return:.1f}%",
            "benchmark_return": f"{bench_annual_return:.1f}%",
            "volatility": f"{port_volatility:.1f}%",
            "max_drawdown": f"-{max_drawdown:.1f}%",
            "sharpe_ratio": f"{sharpe_ratio:.2f}"
        },
        "improvement_suggestions": _get_improvement_suggestions(grades, alpha, diversification_score, fee_percentage),
        "plain_english_summary": (
            f"{portfolio_name} earns an overall grade of {overall_grade} ({gpa:.1f}/4.0 GPA). "
            f"Strongest area: {_best_subject(grades)}. "
            f"Area for improvement: {_worst_subject(grades)}. "
            f"You {'outperformed' if alpha > 0 else 'underperformed'} the benchmark by {abs(alpha):.1f}% annually."
        )
    }


def retirement_goal_tracker(
    current_age: int,
    retirement_age: int,
    current_portfolio_value: float,
    monthly_contribution: float,
    target_retirement_income: float,
    expected_annual_return: float = 7.0
) -> Dict[str, Any]:
    """
    Track progress toward retirement goals
    
    Perfect for: "Am I on track for retirement?"
    
    Args:
        current_age: Current age
        retirement_age: Target retirement age  
        current_portfolio_value: Current portfolio value
        monthly_contribution: Monthly investment amount
        target_retirement_income: Desired annual retirement income
        expected_annual_return: Expected annual return percentage
        
    Returns:
        Dict with retirement planning analysis
    """
    
    years_to_retirement = retirement_age - current_age
    months_to_retirement = years_to_retirement * 12
    
    # Calculate future value with current trajectory
    monthly_return = expected_annual_return / 100 / 12
    
    # Future value of current portfolio
    current_fv = current_portfolio_value * (1 + expected_annual_return/100) ** years_to_retirement
    
    # Future value of monthly contributions (annuity)
    if monthly_return > 0:
        contributions_fv = monthly_contribution * (((1 + monthly_return) ** months_to_retirement - 1) / monthly_return)
    else:
        contributions_fv = monthly_contribution * months_to_retirement
    
    total_projected_value = current_fv + contributions_fv
    
    # Calculate required portfolio value (using 4% withdrawal rule)
    required_portfolio_value = target_retirement_income / 0.04
    
    # Calculate gap
    funding_gap = required_portfolio_value - total_projected_value
    
    # Calculate what monthly contribution would be needed to reach goal
    if monthly_return > 0 and years_to_retirement > 0:
        needed_contribution = (required_portfolio_value - current_fv) / (((1 + monthly_return) ** months_to_retirement - 1) / monthly_return)
    else:
        needed_contribution = funding_gap / months_to_retirement if months_to_retirement > 0 else float('inf')
    
    # Progress percentage
    progress_percentage = (total_projected_value / required_portfolio_value) * 100
    
    # Status determination
    if progress_percentage >= 100:
        status = "On Track"
        status_color = "green"
    elif progress_percentage >= 80:
        status = "Close"
        status_color = "yellow"
    else:
        status = "Behind"
        status_color = "red"
    
    return {
        "success": True,
        "retirement_timeline": {
            "current_age": current_age,
            "retirement_age": retirement_age,
            "years_remaining": years_to_retirement
        },
        "current_status": {
            "portfolio_value": f"${current_portfolio_value:,.0f}",
            "monthly_contribution": f"${monthly_contribution:,.0f}",
            "progress_percentage": f"{progress_percentage:.0f}%",
            "status": status,
            "status_color": status_color
        },
        "projections": {
            "expected_return": f"{expected_annual_return:.1f}% annually",
            "projected_portfolio_value": f"${total_projected_value:,.0f}",
            "target_portfolio_value": f"${required_portfolio_value:,.0f}",
            "funding_gap": f"${funding_gap:+,.0f}"
        },
        "retirement_income": {
            "target_annual_income": f"${target_retirement_income:,.0f}",
            "projected_annual_income": f"${total_projected_value * 0.04:,.0f}",
            "monthly_income": f"${total_projected_value * 0.04 / 12:,.0f}"
        },
        "action_plan": {
            "current_monthly_contribution": f"${monthly_contribution:,.0f}",
            "needed_monthly_contribution": f"${max(0, needed_contribution):,.0f}",
            "monthly_increase_needed": f"${max(0, needed_contribution - monthly_contribution):,.0f}"
        },
        "scenarios": _generate_retirement_scenarios(
            current_portfolio_value, monthly_contribution, years_to_retirement,
            target_retirement_income, expected_annual_return
        ),
        "plain_english_summary": (
            f"You're {progress_percentage:.0f}% on track for retirement. "
            f"At {retirement_age}, your projected portfolio of ${total_projected_value:,.0f} "
            f"would provide ${total_projected_value * 0.04:,.0f} annually. "
            + (
                f"You're on track to meet your ${target_retirement_income:,.0f} goal!"
                if progress_percentage >= 100 
                else f"To reach your ${target_retirement_income:,.0f} goal, increase monthly savings to ${needed_contribution:,.0f}."
            )
        )
    }


def _grade_explanation(subject: str, grade: str, score: float) -> str:
    """Generate explanation for each grade"""
    explanations = {
        "performance": {
            "A+": f"Outstanding! Beating benchmark by {score:.1f}%+ annually",
            "A": f"Excellent performance, ahead of benchmark by {score:.1f}%",
            "B": f"Good performance, roughly matching the market",
            "C": f"Below market performance by {abs(score):.1f}%",
            "D": f"Poor performance, significantly trailing market"
        },
        "risk": {
            "A+": f"Excellent risk-adjusted returns (Sharpe: {score:.2f})",
            "A": f"Good risk management with solid returns",
            "B": f"Acceptable risk-return tradeoff", 
            "C": f"High risk for the returns achieved",
            "D": f"Poor risk management - too much risk for returns"
        },
        "diversification": {
            "A+": "Excellent diversification across asset classes",
            "A": "Well-diversified portfolio",
            "B": "Good diversification with minor concentrations",
            "C": "Some concentration risk present",
            "D": "Poor diversification - significant concentration risk"
        },
        "cost": {
            "A+": f"Excellent - ultra-low costs ({score:.2f}%)",
            "A": f"Very low costs ({score:.2f}%)",
            "B": f"Reasonable costs ({score:.2f}%)",
            "C": f"High costs eating into returns ({score:.2f}%)",
            "D": f"Excessive costs seriously impacting performance ({score:.2f}%)"
        }
    }
    
    return explanations[subject][grade]


def _best_subject(grades: Dict[str, str]) -> str:
    """Find the subject with the best grade"""
    grade_order = {"A+": 0, "A": 1, "B": 2, "C": 3, "D": 4}
    best_grade = min(grades.values(), key=lambda g: grade_order[g])
    subjects = [k for k, v in grades.items() if v == best_grade]
    subject_names = {
        "performance": "Performance",
        "risk_management": "Risk Management", 
        "diversification": "Diversification",
        "cost_management": "Cost Management"
    }
    return subject_names[subjects[0]]


def _worst_subject(grades: Dict[str, str]) -> str:
    """Find the subject with the worst grade"""
    grade_order = {"A+": 0, "A": 1, "B": 2, "C": 3, "D": 4}
    worst_grade = max(grades.values(), key=lambda g: grade_order[g])
    subjects = [k for k, v in grades.items() if v == worst_grade]
    subject_names = {
        "performance": "Performance",
        "risk_management": "Risk Management",
        "diversification": "Diversification", 
        "cost_management": "Cost Management"
    }
    return subject_names[subjects[0]]


def _get_improvement_suggestions(grades: Dict[str, str], alpha: float, 
                                diversification_score: float, fee_percentage: float) -> List[str]:
    """Generate specific improvement suggestions"""
    suggestions = []
    
    if grades["performance"] in ["C", "D"]:
        if alpha < -2:
            suggestions.append("Consider index funds for better benchmark tracking")
        else:
            suggestions.append("Review investment selection and consider broader diversification")
    
    if grades["risk_management"] in ["C", "D"]:
        suggestions.append("Consider reducing portfolio volatility with more bonds or defensive assets")
    
    if grades["diversification"] in ["C", "D"]:
        if diversification_score < 70:
            suggestions.append("Increase diversification across asset classes and sectors")
    
    if grades["cost_management"] in ["C", "D"]:
        if fee_percentage > 1:
            suggestions.append("Switch to lower-cost index funds to reduce fees")
    
    if not suggestions:
        suggestions.append("Portfolio is performing well - continue current strategy")
    
    return suggestions


def _generate_retirement_scenarios(portfolio_value: float, monthly_contrib: float,
                                 years: int, target_income: float, base_return: float) -> List[Dict[str, Any]]:
    """Generate different retirement scenarios"""
    scenarios = []
    
    for scenario_name, return_rate in [("Conservative", 5.0), ("Moderate", 7.0), ("Optimistic", 9.0)]:
        monthly_return = return_rate / 100 / 12
        months = years * 12
        
        # Calculate future value
        current_fv = portfolio_value * (1 + return_rate/100) ** years
        if monthly_return > 0:
            contributions_fv = monthly_contrib * (((1 + monthly_return) ** months - 1) / monthly_return)
        else:
            contributions_fv = monthly_contrib * months
        
        total_value = current_fv + contributions_fv
        annual_income = total_value * 0.04
        
        scenarios.append({
            "scenario": scenario_name,
            "return_assumption": f"{return_rate:.1f}%",
            "projected_value": f"${total_value:,.0f}",
            "annual_income": f"${annual_income:,.0f}",
            "meets_goal": annual_income >= target_income
        })
    
    return scenarios


# Registry of reporting functions
REPORTING_FUNCTIONS = {
    'portfolio_health_dashboard': portfolio_health_dashboard,
    'portfolio_report_card': portfolio_report_card,
    'retirement_goal_tracker': retirement_goal_tracker
}


def get_reporting_function_names():
    """Get list of all reporting function names"""
    return list(REPORTING_FUNCTIONS.keys())