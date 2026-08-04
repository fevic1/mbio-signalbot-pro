from __future__ import annotations

import logging
import math
import statistics
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

from .models import (
    DataPayload, DataProfile, AnalyticalInsight, 
    AnalysisType, TrendDirection
)

logger = logging.getLogger(__name__)


class DataAnalyzer:
    """
    Layer 3: Analysis.
    
    Runs statistical models, trend detection, and correlation analysis.
    
    Responsibilities:
    - Detect trend direction (UP, DOWN, FLAT, VOLATILE) for numeric columns.
    - Identify anomalies using Z-score analysis.
    - Calculate Pearson correlation between numeric columns.
    
    Constraints:
    - NEVER calculates significance scores or p-values (Layer 4).
    - NEVER generates final reports or chart data (Layer 5).
    - Pure deterministic logic using standard library.
    """

    # Thresholds for deterministic analysis
    _TREND_THRESHOLD = 0.05  # 5% change to consider UP/DOWN
    _VOLATILITY_THRESHOLD = 0.15 # 15% std dev relative to mean
    _ANOMALY_Z_SCORE = 2.0

    def analyze(
        self, 
        payload: DataPayload, 
        profile: DataProfile
    ) -> List[AnalyticalInsight]:
        """
        Generates AnalyticalInsights from raw data and its profile.
        """
        insights: List[AnalyticalInsight] = []
        data = payload.data
        
        # Only tabular data (list of dicts) supports deep analysis in this version
        if isinstance(data, list) and len(data) >= 2 and isinstance(data[0], dict):
            insights.extend(self._analyze_tabular(data, profile, payload.payload_id))
            
        return insights

    def _analyze_tabular(
        self, 
        rows: List[Dict[str, Any]], 
        profile: DataProfile, 
        payload_id: str
    ) -> List[AnalyticalInsight]:
        """Performs trend, anomaly, and correlation analysis on tabular data."""
        insights = []
        now = datetime.now(timezone.utc)
        
        # Identify numeric columns from profile
        numeric_cols = [
            col for col, stats in profile.basic_stats.items() 
            if "mean" in stats and stats.get("std", 0) > 0
        ]
        
        if not numeric_cols:
            return insights

        # 1. Trend Analysis (Time-Series Decomposition approximation)
        for col in numeric_cols:
            values = [float(row.get(col, 0)) for row in rows if row.get(col) is not None]
            if len(values) < 4:
                continue
                
            mid = len(values) // 2
            first_half_mean = statistics.mean(values[:mid])
            second_half_mean = statistics.mean(values[mid:])
            
            if first_half_mean == 0:
                continue
                
            change_pct = (second_half_mean - first_half_mean) / first_half_mean
            std_dev = statistics.stdev(values)
            volatility = std_dev / abs(first_half_mean) if first_half_mean != 0 else 0
            
            if volatility > self._VOLATILITY_THRESHOLD:
                trend = TrendDirection.VOLATILE
                finding = f"Column '{col}' exhibits high volatility ({volatility:.2%})."
            elif change_pct > self._TREND_THRESHOLD:
                trend = TrendDirection.UP
                finding = f"Column '{col}' shows a strong upward trend ({change_pct:.2%})."
            elif change_pct < -self._TREND_THRESHOLD:
                trend = TrendDirection.DOWN
                finding = f"Column '{col}' shows a strong downward trend ({change_pct:.2%})."
            else:
                trend = TrendDirection.FLAT
                finding = f"Column '{col}' remains relatively flat ({change_pct:.2%})."
                
            insights.append(AnalyticalInsight(
                payload_id=payload_id,
                analysis_type=AnalysisType.TREND,
                finding=finding,
                trend_direction=trend,
                supporting_metrics={
                    "change_pct": round(change_pct, 4),
                    "volatility": round(volatility, 4)
                },
                analyzed_at=now
            ))

        # 2. Anomaly Detection (Z-Score)
        for col in numeric_cols:
            values = [float(row.get(col, 0)) for row in rows if row.get(col) is not None]
            mean = statistics.mean(values)
            stdev = statistics.stdev(values)
            
            anomalies = [v for v in values if abs((v - mean) / stdev) > self._ANOMALY_Z_SCORE]
            
            if anomalies:
                insights.append(AnalyticalInsight(
                    payload_id=payload_id,
                    analysis_type=AnalysisType.ANOMALY,
                    finding=f"Column '{col}' contains {len(anomalies)} statistical outlier(s).",
                    trend_direction=None,
                    supporting_metrics={
                        "anomaly_count": len(anomalies),
                        "max_anomaly": max(anomalies),
                        "min_anomaly": min(anomalies)
                    },
                    analyzed_at=now
                ))

        # 3. Correlation Analysis (Pearson)
        if len(numeric_cols) >= 2:
            col_x, col_y = numeric_cols[0], numeric_cols[1]
            x_vals = [float(row.get(col_x, 0)) for row in rows if row.get(col_x) is not None and row.get(col_y) is not None]
            y_vals = [float(row.get(col_y, 0)) for row in rows if row.get(col_x) is not None and row.get(col_y) is not None]
            
            if len(x_vals) >= 2:
                correlation = DataAnalyzer._pearson_correlation(x_vals, y_vals)
                strength = "strong" if abs(correlation) > 0.7 else "moderate" if abs(correlation) > 0.4 else "weak"
                direction = "positive" if correlation > 0 else "negative"
                
                insights.append(AnalyticalInsight(
                    payload_id=payload_id,
                    analysis_type=AnalysisType.CORRELATION,
                    finding=f"{strength.capitalize()} {direction} correlation detected between '{col_x}' and '{col_y}'.",
                    trend_direction=None,
                    supporting_metrics={
                        "correlation_coefficient": round(correlation, 4),
                        "column_x": col_x,
                        "column_y": col_y
                    },
                    analyzed_at=now
                ))

        return insights

    @staticmethod
    def _pearson_correlation(x: List[float], y: List[float]) -> float:
        """Calculates Pearson correlation coefficient."""
        n = len(x)
        if n < 2:
            return 0.0
            
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        num = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        den_x = math.sqrt(sum((x[i] - mean_x) ** 2 for i in range(n)))
        den_y = math.sqrt(sum((y[i] - mean_y) ** 2 for i in range(n)))
        
        if den_x == 0 or den_y == 0:
            return 0.0
            
        return num / (den_x * den_y)
