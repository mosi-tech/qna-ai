# Analytics Library Usage Guide

## Overview
This guide documents the proper use of industry-standard Python libraries in our MCP Analytics Server, following the principle of "don't reinvent the wheel."

## Core Libraries Used

### 1. **pandas** - Data Manipulation and Time Series
✅ **Use For:**
- Data manipulation and cleaning
- Time series analysis (resampling, rolling windows)
- Data alignment and merging
- Handling missing data

```python
# ✅ GOOD: Use pandas for time series operations
rolling_vol = returns.rolling(30).std() * np.sqrt(252)
weekly_data = daily_data.resample('W').agg({'o': 'first', 'h': 'max', 'l': 'min', 'c': 'last'})
```

### 2. **ta** - Technical Analysis
✅ **Use For:**
- All standard technical indicators
- Avoid custom implementations of common indicators

```python
# ✅ GOOD: Use ta library for all indicators
import ta
df['rsi'] = ta.momentum.rsi(df['close'], window=14)
df['macd'] = ta.trend.macd_diff(df['close'])
df['bb_upper'] = ta.volatility.bollinger_hband(df['close'])

# ❌ AVOID: Custom RSI implementation
def custom_rsi(prices): ...  # Don't do this!
```

**Available Categories:**
- **Momentum**: RSI, Stochastic, Williams %R, ROC
- **Trend**: MACD, ADX, Parabolic SAR, CCI
- **Volatility**: Bollinger Bands, ATR, Keltner Channels
- **Volume**: OBV, Chaikin Money Flow, Volume SMA

### 3. **scipy.stats** - Statistical Analysis
✅ **Use For:**
- Hypothesis testing
- Statistical significance testing
- Distribution analysis
- Correlation analysis

```python
# ✅ GOOD: Use scipy for statistical tests
from scipy.stats import ttest_ind, pearsonr, normaltest
statistic, p_value = ttest_ind(sample1, sample2)
correlation, p_val = pearsonr(returns1, returns2)
stat, p = normaltest(returns)  # Test for normality
```

### 4. **scikit-learn** - Machine Learning
✅ **Use For:**
- Clustering analysis (KMeans, DBSCAN)
- Classification and regression
- Feature selection and dimensionality reduction
- Data preprocessing and scaling

```python
# ✅ GOOD: Use sklearn for clustering
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

scaler = StandardScaler()
scaled_data = scaler.fit_transform(features)
clusters = KMeans(n_clusters=5).fit_predict(scaled_data)
pca = PCA(n_components=3).fit_transform(scaled_data)
```

### 5. **xgboost** - Advanced ML (Optional)
✅ **Use For:**
- Advanced predictions
- Feature importance analysis
- Non-linear pattern detection

```python
# ✅ GOOD: Use XGBoost for predictions
import xgboost as xgb
model = xgb.XGBRegressor(n_estimators=100, max_depth=6)
model.fit(X_train, y_train)
predictions = model.predict(X_test)
importance = model.feature_importances_
```

**Note**: XGBoost may require OpenMP installation on Mac: `brew install libomp`

### 6. **numpy & scipy** - Numerical Computations
✅ **Use For:**
- Mathematical operations
- Array manipulations
- Numerical algorithms

```python
# ✅ GOOD: Use numpy/scipy for math
import numpy as np
from scipy import stats

returns_array = np.array(returns)
sharpe_ratio = np.mean(returns_array) / np.std(returns_array) * np.sqrt(252)
var_95 = np.percentile(returns_array, 5)  # 95% VaR
```

## Implementation Examples

### Advanced Technical Analysis
```python
def comprehensive_technical_analysis(price_data):
    df = pd.DataFrame(price_data)
    
    # Use ta library for all indicators
    df['rsi'] = ta.momentum.rsi(df['close'])
    df['macd'] = ta.trend.macd_diff(df['close'])
    df['bb_upper'] = ta.volatility.bollinger_hband(df['close'])
    df['atr'] = ta.volatility.average_true_range(df['high'], df['low'], df['close'])
    
    # Use pandas for rolling operations
    df['rolling_vol'] = df['close'].pct_change().rolling(30).std() * np.sqrt(252)
    
    return df
```

### ML-Based Stock Clustering
```python
def cluster_stocks_by_returns(returns_data, n_clusters=5):
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from sklearn.metrics import silhouette_score
    
    df = pd.DataFrame(returns_data)
    scaled_data = StandardScaler().fit_transform(df.T)
    
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    clusters = kmeans.fit_predict(scaled_data)
    
    silhouette_avg = silhouette_score(scaled_data, clusters)
    
    return {
        "clusters": clusters,
        "silhouette_score": silhouette_avg
    }
```

### Statistical Significance Testing
```python
def test_strategy_significance(strategy_returns, benchmark_returns):
    from scipy.stats import ttest_ind
    
    # Test if strategy significantly outperforms benchmark
    statistic, p_value = ttest_ind(strategy_returns, benchmark_returns)
    
    return {
        "statistic": statistic,
        "p_value": p_value,
        "is_significant": p_value < 0.05,
        "confidence_level": 0.95
    }
```

## Available MCP Functions

### Core Analytics
- `calculate_daily_returns` - Using pandas
- `calculate_rolling_volatility` - Using pandas + numpy
- `calculate_correlation_matrix` - Using scipy.stats

### Technical Analysis (ta library)
- `comprehensive_technical_analysis` - All indicators in one call
- `calculate_rsi` - RSI using ta.momentum.rsi
- `calculate_macd` - MACD using ta.trend.MACD
- `calculate_bollinger_bands` - Bollinger Bands using ta.volatility.BollingerBands

### Machine Learning (scikit-learn/xgboost)
- `cluster_stocks_by_returns` - KMeans clustering
- `detect_outlier_stocks` - Outlier detection (DBSCAN, z-score)
- `feature_importance_analysis` - Random Forest feature importance
- `predict_returns_xgboost` - XGBoost predictions
- `dimensionality_reduction_analysis` - PCA analysis

### Statistical Analysis (scipy.stats)
- `calculate_statistical_significance` - Hypothesis testing
- `calculate_risk_metrics` - VaR, Sharpe, drawdowns

## Best Practices

### 1. Library Priority
1. **First**: Check if functionality exists in established libraries
2. **Second**: Use library implementations with minimal wrapper code
3. **Last Resort**: Write custom code only when no library solution exists

### 2. Error Handling
```python
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False

def predict_with_xgboost(...):
    if not XGBOOST_AVAILABLE:
        return {"error": "XGBoost not available"}
    # ... implementation
```

### 3. Data Validation
```python
def validate_input(data):
    df = pd.DataFrame(data)
    if df.empty:
        return {"error": "No data provided"}
    
    # Clean data using pandas
    df = df.dropna()
    
    if len(df) < 20:
        return {"error": "Insufficient data for analysis"}
    
    return df
```

### 4. Combine Libraries Effectively
```python
def advanced_portfolio_analysis(returns_data):
    # Use pandas for data manipulation
    df = pd.DataFrame(returns_data)
    
    # Use scipy for statistical tests
    from scipy.stats import normaltest
    normality_test = normaltest(df.values.flatten())
    
    # Use sklearn for clustering
    from sklearn.cluster import KMeans
    clusters = KMeans(n_clusters=3).fit_predict(df.T)
    
    # Use ta for technical indicators if price data available
    # ... technical analysis
    
    return {
        "normality_test": normality_test,
        "clusters": clusters,
        # ... other results
    }
```

## Dependencies
See `mcp-analytics-server/requirements.txt` for specific version requirements:
- pandas>=2.0.0
- numpy>=1.24.0
- scipy>=1.10.0
- scikit-learn>=1.3.0
- ta>=0.10.2
- xgboost>=1.7.0 (optional, may need OpenMP)

## Summary
By leveraging these established libraries, we achieve:
- ✅ **Reliability**: Battle-tested implementations
- ✅ **Performance**: Optimized algorithms
- ✅ **Maintainability**: Standard interfaces
- ✅ **Features**: Comprehensive functionality
- ✅ **Documentation**: Well-documented APIs

Always prefer library solutions over custom implementations!