"""
Advanced ML-based analytics using scikit-learn and xgboost.
Demonstrates proper use of established libraries instead of custom implementations.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from scipy.stats import zscore
import warnings
warnings.filterwarnings('ignore')

# Optional: Import xgboost if available (handles OpenMP issues gracefully)
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except (ImportError, Exception) as e:
    # Handle both ImportError and XGBoost-specific errors (like missing OpenMP)
    XGBOOST_AVAILABLE = False
    xgb = None


class MLAnalytics:
    """Advanced analytics using machine learning libraries."""
    
    def __init__(self):
        self.scaler = StandardScaler()
    
    def cluster_stocks_by_returns(self, returns_data: Dict[str, List[float]], 
                                n_clusters: int = 5) -> Dict[str, Any]:
        """
        Cluster stocks based on return patterns using scikit-learn KMeans.
        
        Args:
            returns_data: Dictionary with symbol -> return series
            n_clusters: Number of clusters to create
            
        Returns:
            Dictionary with cluster assignments and statistics
        """
        # Convert to DataFrame
        df = pd.DataFrame(returns_data).fillna(0)
        
        if df.empty or len(df.columns) < 3:
            return {"error": "Insufficient data for clustering"}
        
        # Standardize features
        scaled_data = self.scaler.fit_transform(df.T)  # Transpose: symbols as rows
        
        # Perform KMeans clustering
        kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
        cluster_labels = kmeans.fit_predict(scaled_data)
        
        # Calculate silhouette score
        silhouette_avg = silhouette_score(scaled_data, cluster_labels)
        
        # Organize results
        clusters = {}
        for i, symbol in enumerate(df.columns):
            cluster_id = int(cluster_labels[i])
            if cluster_id not in clusters:
                clusters[cluster_id] = []
            clusters[cluster_id].append(symbol)
        
        # Calculate cluster statistics
        cluster_stats = {}
        for cluster_id, symbols in clusters.items():
            cluster_returns = df[symbols].mean(axis=1)
            cluster_stats[cluster_id] = {
                "symbols": symbols,
                "count": len(symbols),
                "avg_return": float(cluster_returns.mean()),
                "volatility": float(cluster_returns.std()),
                "sharpe_proxy": float(cluster_returns.mean() / cluster_returns.std()) if cluster_returns.std() > 0 else 0
            }
        
        return {
            "cluster_assignments": clusters,
            "cluster_statistics": cluster_stats,
            "silhouette_score": float(silhouette_avg),
            "n_clusters": n_clusters,
            "method": "KMeans"
        }
    
    def detect_outlier_stocks(self, returns_data: Dict[str, List[float]], 
                            method: str = "isolation") -> Dict[str, Any]:
        """
        Detect outlier stocks using scikit-learn methods.
        
        Args:
            returns_data: Dictionary with symbol -> return series
            method: "isolation", "dbscan", or "zscore"
            
        Returns:
            Dictionary with outlier analysis results
        """
        df = pd.DataFrame(returns_data).fillna(0)
        
        if df.empty:
            return {"error": "No data provided"}
        
        if method == "zscore":
            # Simple z-score approach using scipy
            symbol_stats = {}
            for symbol in df.columns:
                returns = df[symbol].values
                z_scores = np.abs(zscore(returns))
                outlier_count = np.sum(z_scores > 2.0)  # 2 standard deviations
                
                symbol_stats[symbol] = {
                    "outlier_days": int(outlier_count),
                    "outlier_percentage": float(outlier_count / len(returns) * 100),
                    "max_zscore": float(np.max(z_scores)),
                    "is_outlier_stock": outlier_count > len(returns) * 0.1  # >10% outlier days
                }
            
            outlier_stocks = [s for s, stats in symbol_stats.items() if stats["is_outlier_stock"]]
            
            return {
                "method": "zscore",
                "outlier_stocks": outlier_stocks,
                "symbol_statistics": symbol_stats,
                "threshold": "2 standard deviations"
            }
        
        elif method == "dbscan":
            # Use DBSCAN for density-based outlier detection
            scaled_data = self.scaler.fit_transform(df.T)
            
            # DBSCAN clustering
            dbscan = DBSCAN(eps=0.5, min_samples=3)
            cluster_labels = dbscan.fit_predict(scaled_data)
            
            # Points labeled as -1 are outliers
            outlier_mask = cluster_labels == -1
            outlier_symbols = df.columns[outlier_mask].tolist()
            
            return {
                "method": "DBSCAN",
                "outlier_stocks": outlier_symbols,
                "n_outliers": int(np.sum(outlier_mask)),
                "n_clusters": len(set(cluster_labels)) - (1 if -1 in cluster_labels else 0),
                "outlier_percentage": float(np.sum(outlier_mask) / len(cluster_labels) * 100)
            }
        
        else:
            return {"error": f"Unknown method: {method}"}
    
    def feature_importance_analysis(self, target_returns: List[float], 
                                  features: Dict[str, List[float]]) -> Dict[str, Any]:
        """
        Analyze feature importance using Random Forest.
        
        Args:
            target_returns: Target variable (e.g., next day returns)
            features: Dictionary of feature name -> feature values
            
        Returns:
            Feature importance analysis results
        """
        try:
            # Prepare data
            feature_df = pd.DataFrame(features)
            target = np.array(target_returns)
            
            # Remove rows with NaN values
            mask = ~(feature_df.isnull().any(axis=1) | np.isnan(target))
            X = feature_df[mask].values
            y = target[mask]
            
            if len(X) < 10:
                return {"error": "Insufficient clean data for analysis"}
            
            # Fit Random Forest
            rf = RandomForestRegressor(n_estimators=100, random_state=42, max_depth=10)
            rf.fit(X, y)
            
            # Get feature importances
            importances = rf.feature_importances_
            feature_names = feature_df.columns.tolist()
            
            # Create importance ranking
            importance_data = []
            for i, (name, importance) in enumerate(zip(feature_names, importances)):
                importance_data.append({
                    "feature": name,
                    "importance": float(importance),
                    "rank": i + 1
                })
            
            # Sort by importance
            importance_data.sort(key=lambda x: x["importance"], reverse=True)
            
            # Add ranking
            for i, item in enumerate(importance_data):
                item["rank"] = i + 1
            
            return {
                "feature_importances": importance_data,
                "model_score": float(rf.score(X, y)),
                "n_samples": len(X),
                "n_features": len(feature_names),
                "top_feature": importance_data[0]["feature"] if importance_data else None
            }
            
        except Exception as e:
            return {"error": f"Feature importance analysis failed: {str(e)}"}
    
    def predict_returns_xgboost(self, features: Dict[str, List[float]], 
                              target_returns: List[float],
                              prediction_features: Optional[Dict[str, List[float]]] = None) -> Dict[str, Any]:
        """
        Predict returns using XGBoost (if available).
        
        Args:
            features: Training features
            target_returns: Training targets
            prediction_features: Features for prediction (optional)
            
        Returns:
            Prediction results and model performance
        """
        if not XGBOOST_AVAILABLE:
            return {"error": "XGBoost not available. Install with: pip install xgboost"}
        
        try:
            # Prepare training data
            feature_df = pd.DataFrame(features)
            target = np.array(target_returns)
            
            # Clean data
            mask = ~(feature_df.isnull().any(axis=1) | np.isnan(target))
            X_train = feature_df[mask].values
            y_train = target[mask]
            
            if len(X_train) < 20:
                return {"error": "Insufficient training data"}
            
            # Train XGBoost model
            model = xgb.XGBRegressor(
                n_estimators=100,
                max_depth=6,
                learning_rate=0.1,
                random_state=42,
                eval_metric='rmse'
            )
            
            model.fit(X_train, y_train)
            
            # Get feature importance
            feature_importance = dict(zip(feature_df.columns, model.feature_importances_))
            
            results = {
                "model_score": float(model.score(X_train, y_train)),
                "feature_importance": {k: float(v) for k, v in feature_importance.items()},
                "n_training_samples": len(X_train),
                "model_type": "XGBoost"
            }
            
            # Make predictions if prediction features provided
            if prediction_features:
                pred_df = pd.DataFrame(prediction_features)
                if pred_df.shape[1] == feature_df.shape[1]:  # Same number of features
                    pred_clean = pred_df.fillna(0).values
                    predictions = model.predict(pred_clean)
                    results["predictions"] = predictions.tolist()
                    results["prediction_samples"] = len(predictions)
                else:
                    results["prediction_error"] = "Feature dimension mismatch"
            
            return results
            
        except Exception as e:
            return {"error": f"XGBoost prediction failed: {str(e)}"}
    
    def dimensionality_reduction_analysis(self, returns_data: Dict[str, List[float]], 
                                        n_components: int = 3) -> Dict[str, Any]:
        """
        Perform PCA analysis on stock returns using scikit-learn.
        
        Args:
            returns_data: Dictionary with symbol -> return series
            n_components: Number of principal components
            
        Returns:
            PCA analysis results
        """
        try:
            df = pd.DataFrame(returns_data).fillna(0)
            
            if df.empty or len(df.columns) < n_components:
                return {"error": "Insufficient data for PCA"}
            
            # Standardize data
            scaled_data = self.scaler.fit_transform(df.T)
            
            # Perform PCA
            pca = PCA(n_components=n_components, random_state=42)
            pca_result = pca.fit_transform(scaled_data)
            
            # Calculate explained variance
            explained_variance = pca.explained_variance_ratio_
            cumulative_variance = np.cumsum(explained_variance)
            
            # Get principal component loadings
            components = pca.components_
            feature_names = df.columns.tolist()
            
            # Create component analysis
            component_analysis = {}
            for i in range(n_components):
                # Find top contributing features for this component
                loadings = components[i]
                top_indices = np.argsort(np.abs(loadings))[-5:]  # Top 5 contributors
                
                component_analysis[f"PC{i+1}"] = {
                    "explained_variance": float(explained_variance[i]),
                    "cumulative_variance": float(cumulative_variance[i]),
                    "top_contributors": [
                        {
                            "symbol": feature_names[idx],
                            "loading": float(loadings[idx])
                        }
                        for idx in reversed(top_indices)
                    ]
                }
            
            return {
                "n_components": n_components,
                "total_explained_variance": float(cumulative_variance[-1]),
                "component_analysis": component_analysis,
                "pca_coordinates": pca_result.tolist(),
                "symbol_names": df.columns.tolist()
            }
            
        except Exception as e:
            return {"error": f"PCA analysis failed: {str(e)}"}


def create_ml_analytics_instance():
    """Factory function to create MLAnalytics instance."""
    return MLAnalytics()