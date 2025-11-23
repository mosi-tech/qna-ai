"""
Test UI Routes - Generate mock financial data and test UI Result Formatter

This module provides endpoints for testing the UI generation chain with mock data
before integrating with actual financial analysis workflows.
"""

import logging
import random
import json
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Query, Request, Depends
from pydantic import BaseModel

# Import auth components (not used for test endpoints)

# Import UI Result Formatter
from shared.services.ui_result_formatter import create_ui_result_formatter

logger = logging.getLogger("test-ui-routes")

router = APIRouter(prefix="/api/test-ui", tags=["test-ui"])


class MockDataRequest(BaseModel):
    """Request for generating mock financial data"""
    analysis_type: str = "ranking"  # ranking, comparison, time_series, distribution, correlation
    data_size: int = 10
    question: Optional[str] = None


class UITestResponse(BaseModel):
    """Response from UI generation test"""
    success: bool
    mock_data: Optional[Dict[str, Any]] = None
    ui_config: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    generation_time_ms: Optional[int] = None


# Mock Financial Data Generators

def generate_etf_ranking_data(size: int = 10) -> Dict[str, Any]:
    """Generate mock ETF ranking data for performance analysis"""
    
    etf_symbols = ["QQQ", "SPY", "VTI", "ARKK", "TQQQ", "VGT", "XLK", "IWM", "EFA", "VWO", 
                   "GLD", "SLV", "TLT", "HYG", "LQD", "EEM", "IEMG", "VEA", "VXUS", "BND"]
    
    etf_names = {
        "QQQ": "Invesco QQQ Trust",
        "SPY": "SPDR S&P 500 ETF",
        "VTI": "Vanguard Total Stock Market",
        "ARKK": "ARK Innovation ETF",
        "TQQQ": "ProShares UltraPro QQQ",
        "VGT": "Vanguard Information Technology",
        "XLK": "Technology Select Sector",
        "IWM": "iShares Russell 2000",
        "EFA": "iShares MSCI EAFE",
        "VWO": "Vanguard Emerging Markets"
    }
    
    rankings = []
    for i in range(min(size, len(etf_symbols))):
        symbol = etf_symbols[i]
        base_return = random.uniform(-0.15, 0.45)  # -15% to 45% improvement
        
        rankings.append({
            "rank": i + 1,
            "symbol": symbol,
            "name": etf_names.get(symbol, f"{symbol} Fund"),
            "sharpe_improvement": round(base_return, 4),
            "sharpe_improvement_pct": round(base_return * 100, 2),
            "previous_sharpe": round(random.uniform(0.3, 1.2), 3),
            "current_sharpe": round(random.uniform(0.8, 1.8), 3),
            "volatility": round(random.uniform(0.08, 0.25), 3),
            "avg_return": round(random.uniform(-0.05, 0.25), 3),
            "market_cap": random.randint(1000000000, 500000000000)
        })
    
    # Sort by improvement descending
    rankings.sort(key=lambda x: x["sharpe_improvement"], reverse=True)
    
    # Update ranks
    for i, item in enumerate(rankings):
        item["rank"] = i + 1
    
    return {
        "etf_rankings": rankings,
        "summary": {
            "total_analyzed": len(rankings),
            "avg_improvement": round(sum(r["sharpe_improvement"] for r in rankings) / len(rankings), 4),
            "best_performer": rankings[0]["symbol"] if rankings else None,
            "worst_performer": rankings[-1]["symbol"] if rankings else None,
            "positive_improvements": len([r for r in rankings if r["sharpe_improvement"] > 0]),
            "analysis_date": datetime.now().isoformat(),
            "market_conditions": "Bullish" if sum(r["sharpe_improvement"] for r in rankings) > 0 else "Bearish"
        },
        "distribution": {
            "excellent": len([r for r in rankings if r["sharpe_improvement"] > 0.2]),
            "good": len([r for r in rankings if 0.1 <= r["sharpe_improvement"] <= 0.2]), 
            "average": len([r for r in rankings if 0 <= r["sharpe_improvement"] < 0.1]),
            "poor": len([r for r in rankings if r["sharpe_improvement"] < 0])
        }
    }


def generate_portfolio_comparison_data(size: int = 5) -> Dict[str, Any]:
    """Generate mock portfolio comparison data"""
    
    portfolios = ["Current Portfolio", "Aggressive Growth", "Conservative", "Income Focused", "Balanced Index"]
    metrics = ["return", "volatility", "sharpe_ratio", "max_drawdown", "beta"]
    
    comparison_data = {}
    entities = []
    
    for i, portfolio in enumerate(portfolios[:size]):
        portfolio_id = f"portfolio_{i+1}"
        entities.append({
            "id": portfolio_id,
            "name": portfolio,
            "shortName": f"P{i+1}",
            "description": f"{portfolio} strategy"
        })
        
        comparison_data[portfolio_id] = {
            "return": round(random.uniform(-0.05, 0.35), 4),
            "volatility": round(random.uniform(0.08, 0.25), 4), 
            "sharpe_ratio": round(random.uniform(0.5, 2.0), 3),
            "max_drawdown": round(random.uniform(-0.35, -0.05), 4),
            "beta": round(random.uniform(0.7, 1.4), 3)
        }
    
    return {
        "comparison_data": comparison_data,
        "entities": entities,
        "metrics": [
            {"id": "return", "name": "Annual Return", "format": "percentage"},
            {"id": "volatility", "name": "Volatility", "format": "percentage"},
            {"id": "sharpe_ratio", "name": "Sharpe Ratio", "format": "ratio"},
            {"id": "max_drawdown", "name": "Max Drawdown", "format": "percentage"},
            {"id": "beta", "name": "Beta", "format": "ratio"}
        ],
        "summary": {
            "best_return": max(comparison_data.values(), key=lambda x: x["return"])["return"],
            "lowest_volatility": min(comparison_data.values(), key=lambda x: x["volatility"])["volatility"],
            "best_sharpe": max(comparison_data.values(), key=lambda x: x["sharpe_ratio"])["sharpe_ratio"]
        }
    }


def generate_time_series_data(size: int = 12) -> Dict[str, Any]:
    """Generate mock time series performance data"""
    
    base_date = datetime.now() - timedelta(days=size * 30)
    time_series = []
    cumulative_return = 0
    
    for i in range(size):
        date = base_date + timedelta(days=i * 30)
        monthly_return = random.uniform(-0.08, 0.15)  # -8% to 15% monthly
        cumulative_return += monthly_return
        
        time_series.append({
            "date": date.isoformat()[:10],  # YYYY-MM-DD format
            "label": date.strftime("%b %Y"),
            "monthly_return": round(monthly_return, 4),
            "cumulative_return": round(cumulative_return, 4),
            "value": round(cumulative_return * 100, 2),  # Percentage for charts
            "portfolio_value": round(100000 * (1 + cumulative_return), 2),
            "benchmark_return": round(random.uniform(-0.05, 0.12), 4)
        })
    
    return {
        "time_series": time_series,
        "performance_summary": {
            "total_return": round(cumulative_return, 4),
            "annualized_return": round(cumulative_return * (12/size), 4),
            "best_month": max(time_series, key=lambda x: x["monthly_return"]),
            "worst_month": min(time_series, key=lambda x: x["monthly_return"]),
            "positive_months": len([x for x in time_series if x["monthly_return"] > 0]),
            "volatility": round(
                (sum([(x["monthly_return"] - cumulative_return/size) ** 2 for x in time_series]) / size) ** 0.5, 
                4
            )
        }
    }


def generate_correlation_data(size: int = 8) -> Dict[str, Any]:
    """Generate mock correlation analysis data"""
    
    assets = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMZN", "META", "NFLX"][:size]
    
    # Generate correlation matrix
    correlation_matrix = []
    for i in range(size):
        row = []
        for j in range(size):
            if i == j:
                row.append(1.0)  # Perfect self-correlation
            elif i < j:
                corr = random.uniform(-0.3, 0.9)  # Random correlation
                row.append(round(corr, 3))
            else:
                # Mirror the upper triangle
                corr = correlation_matrix[j][i] 
                row.append(corr)
        correlation_matrix.append(row)
    
    # Generate scatter plot data for two assets
    scatter_data = []
    for _ in range(50):  # 50 data points
        scatter_data.append({
            "x": round(random.uniform(-0.1, 0.15), 4),  # Asset 1 returns
            "y": round(random.uniform(-0.08, 0.12), 4),  # Asset 2 returns
            "label": f"Day {len(scatter_data) + 1}"
        })
    
    return {
        "correlation_matrix": correlation_matrix,
        "asset_labels": assets,
        "scatter_data": scatter_data,
        "correlation_summary": {
            "highest_correlation": max([max(row[i+1:]) for i, row in enumerate(correlation_matrix[:-1])]),
            "lowest_correlation": min([min(row[i+1:]) for i, row in enumerate(correlation_matrix[:-1])]),
            "average_correlation": round(
                sum([sum(row[i+1:]) for i, row in enumerate(correlation_matrix[:-1])]) / 
                sum([len(row[i+1:]) for i, row in enumerate(correlation_matrix[:-1])]), 3
            )
        }
    }


def generate_distribution_data(size: int = 8) -> Dict[str, Any]:
    """Generate mock portfolio allocation/distribution data"""
    
    sectors = ["Technology", "Healthcare", "Finance", "Consumer Discretionary", 
              "Industrials", "Communication", "Consumer Staples", "Energy"][:size]
    
    # Generate random weights that sum to 100%
    weights = [random.uniform(5, 25) for _ in range(size)]
    total = sum(weights)
    normalized_weights = [(w/total) * 100 for w in weights]
    
    allocation_data = []
    for i, sector in enumerate(sectors):
        allocation_data.append({
            "label": sector,
            "value": round(normalized_weights[i], 2),
            "target_allocation": round(random.uniform(8, 20), 1),
            "market_value": round(normalized_weights[i] * 10000, 2),  # $1M portfolio
            "color": ["#3B82F6", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", 
                     "#06B6D4", "#84CC16", "#F97316"][i]
        })
    
    return {
        "allocation_data": allocation_data,
        "portfolio_summary": {
            "total_sectors": len(allocation_data),
            "largest_allocation": max(allocation_data, key=lambda x: x["value"]),
            "smallest_allocation": min(allocation_data, key=lambda x: x["value"]),
            "concentration_risk": "High" if max(normalized_weights) > 30 else "Medium" if max(normalized_weights) > 20 else "Low",
            "diversification_score": round(100 - max(normalized_weights), 1)
        }
    }


def generate_holdings_analysis_data(size: int = 12) -> Dict[str, Any]:
    """Generate mock holdings analysis for green weeks question"""
    
    holdings = ["AAPL", "MSFT", "GOOGL", "TSLA", "NVDA", "AMZN", "META", "NFLX", 
               "BRK.B", "JNJ", "V", "PG"][:size]
    
    holdings_data = []
    for symbol in holdings:
        total_weeks = 52
        green_weeks = random.randint(20, 45)
        green_percentage = (green_weeks / total_weeks) * 100
        
        holdings_data.append({
            "symbol": symbol,
            "name": f"{symbol} Corporation", 
            "total_weeks": total_weeks,
            "green_weeks": green_weeks,
            "red_weeks": total_weeks - green_weeks,
            "green_week_percentage": round(green_percentage, 1),
            "position_size": round(random.uniform(5000, 50000), 2),
            "ytd_return": round(random.uniform(-20, 80), 2),
            "volatility": round(random.uniform(15, 40), 1),
            "consistency_rating": "High" if green_percentage > 70 else "Medium" if green_percentage > 60 else "Low"
        })
    
    # Sort by green week percentage
    holdings_data.sort(key=lambda x: x["green_week_percentage"], reverse=True)
    
    return {
        "holdings_analysis": holdings_data,
        "portfolio_stats": {
            "total_holdings": len(holdings_data),
            "avg_green_week_pct": round(sum(h["green_week_percentage"] for h in holdings_data) / len(holdings_data), 1),
            "most_consistent": holdings_data[0]["symbol"],
            "least_consistent": holdings_data[-1]["symbol"],
            "weeks_analyzed": 52,
            "high_consistency_count": len([h for h in holdings_data if h["green_week_percentage"] > 70]),
            "portfolio_value": sum(h["position_size"] for h in holdings_data)
        },
        "distribution": {
            "high_consistency": len([h for h in holdings_data if h["green_week_percentage"] > 70]),
            "medium_consistency": len([h for h in holdings_data if 60 <= h["green_week_percentage"] <= 70]),
            "low_consistency": len([h for h in holdings_data if h["green_week_percentage"] < 60])
        }
    }


# Mock Data Generator Factory
MOCK_DATA_GENERATORS = {
    "ranking": generate_etf_ranking_data,
    "comparison": generate_portfolio_comparison_data, 
    "time_series": generate_time_series_data,
    "correlation": generate_correlation_data,
    "distribution": generate_distribution_data,
    "holdings_analysis": generate_holdings_analysis_data
}

# Sample Questions for Each Analysis Type
SAMPLE_QUESTIONS = {
    "ranking": "Which ETFs posted the largest improvement in 3-month Sharpe ratio?",
    "comparison": "How do different portfolio strategies compare in terms of risk-adjusted returns?",
    "time_series": "What has been the monthly performance trend of my portfolio over the past year?",
    "correlation": "Which assets in my portfolio show the strongest correlations?", 
    "distribution": "How is my portfolio allocated across different sectors?",
    "holdings_analysis": "Which of my holdings had the highest proportion of green weeks this year?"
}


@router.get("/mock-data/{analysis_type}")
async def generate_mock_data(
    analysis_type: str,
    size: int = Query(10, description="Number of data points to generate")
) -> Dict[str, Any]:
    """Generate mock financial data for testing"""
    
    try:
        if analysis_type not in MOCK_DATA_GENERATORS:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown analysis type: {analysis_type}. Available: {list(MOCK_DATA_GENERATORS.keys())}"
            )
        
        generator = MOCK_DATA_GENERATORS[analysis_type]
        mock_data = generator(size)
        
        logger.info(f"Generated mock {analysis_type} data with {size} items")
        
        return {
            "analysis_type": analysis_type,
            "data_size": size,
            "sample_question": SAMPLE_QUESTIONS.get(analysis_type),
            "mock_data": mock_data,
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating mock data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate mock data: {str(e)}")


@router.post("/test-ui-generation")
async def test_ui_generation(
    request: MockDataRequest
) -> UITestResponse:
    """Test complete UI generation chain with mock data"""
    
    start_time = datetime.now()
    
    try:
        logger.info(f"Testing UI generation for {request.analysis_type} analysis")
        
        # 1. Generate mock financial data
        if request.analysis_type not in MOCK_DATA_GENERATORS:
            return UITestResponse(
                success=False,
                error=f"Unknown analysis type: {request.analysis_type}"
            )
        
        generator = MOCK_DATA_GENERATORS[request.analysis_type]
        mock_data = generator(request.data_size)
        
        # 2. Use sample question if not provided
        question = request.question or SAMPLE_QUESTIONS.get(request.analysis_type, "Analyze this data")
        
        # 3. Create mock execution result structure (matching real analysis results)
        execution_result = {
            "results": mock_data,
            "response_type": request.analysis_type,
            "status": "completed",
            "execution_id": f"test_{int(datetime.now().timestamp())}",
            "created_at": datetime.now().isoformat()
        }
        
        # 4. Initialize UI Result Formatter
        ui_formatter = create_ui_result_formatter()
        
        # 5. Generate UI configuration using LLM + MCP tools
        ui_response = await ui_formatter.format_execution_result_to_ui(
            execution_result=execution_result,
            user_question=question
        )
        
        end_time = datetime.now()
        generation_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        if ui_response:
            logger.info(f"✅ Successfully generated UI config in {generation_time_ms}ms")
            return UITestResponse(
                success=True,
                mock_data=mock_data,
                ui_config=ui_response,  # This already has the proper structure from UIResultFormatter
                generation_time_ms=generation_time_ms
            )
        else:
            logger.warning("UI generation returned None")
            return UITestResponse(
                success=False,
                mock_data=mock_data,
                error="UI generation returned no configuration",
                generation_time_ms=generation_time_ms
            )
            
    except Exception as e:
        end_time = datetime.now()
        generation_time_ms = int((end_time - start_time).total_seconds() * 1000)
        
        logger.error(f"❌ Error in UI generation test: {str(e)}")
        return UITestResponse(
            success=False,
            error=str(e),
            generation_time_ms=generation_time_ms
        )


@router.get("/sample-questions")
async def get_sample_questions() -> Dict[str, Any]:
    """Get sample questions for each analysis type"""
    
    return {
        "sample_questions": SAMPLE_QUESTIONS,
        "analysis_types": list(MOCK_DATA_GENERATORS.keys()),
        "description": "Sample questions that can be used to test UI generation for each analysis type"
    }


@router.get("/test-all-types")
async def test_all_analysis_types(
    data_size: int = Query(8, description="Number of data points per analysis")
) -> Dict[str, Any]:
    """Run UI generation test for all analysis types"""
    
    results = {}
    total_start_time = datetime.now()
    
    for analysis_type in MOCK_DATA_GENERATORS.keys():
        try:
            logger.info(f"Testing {analysis_type}...")
            
            request = MockDataRequest(
                analysis_type=analysis_type,
                data_size=data_size,
                question=SAMPLE_QUESTIONS.get(analysis_type)
            )
            
            result = await test_ui_generation(request)
            results[analysis_type] = {
                "success": result.success,
                "generation_time_ms": result.generation_time_ms,
                "has_ui_config": result.ui_config is not None,
                "component_count": len(result.ui_config.get("ui_config", {}).get("selected_components", [])) if result.ui_config else 0,
                "error": result.error
            }
            
        except Exception as e:
            logger.error(f"Error testing {analysis_type}: {str(e)}")
            results[analysis_type] = {
                "success": False,
                "error": str(e),
                "generation_time_ms": None
            }
    
    total_time_ms = int((datetime.now() - total_start_time).total_seconds() * 1000)
    
    # Summary statistics
    successful_tests = len([r for r in results.values() if r["success"]])
    total_tests = len(results)
    avg_generation_time = sum([r["generation_time_ms"] for r in results.values() if r["generation_time_ms"]]) / successful_tests if successful_tests > 0 else 0
    
    return {
        "summary": {
            "total_tests": total_tests,
            "successful_tests": successful_tests,
            "success_rate": f"{(successful_tests/total_tests)*100:.1f}%",
            "total_time_ms": total_time_ms,
            "avg_generation_time_ms": round(avg_generation_time, 2)
        },
        "results": results,
        "tested_at": datetime.now().isoformat()
    }