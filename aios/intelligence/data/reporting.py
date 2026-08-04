from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

from .models import (
    DataPayload,
    DataProfile,
    AnalyticalInsight,
    AnalysisScore,
    AnalysisReport,
    SignificanceLevel
)

logger = logging.getLogger(__name__)


class DataReporter:
    """
    Layer 5: Reporting.
    
    Synthesizes analyzed data and scores into a final Analysis Report.
    
    Responsibilities:
    - Generate a deterministic summary.
    - Compile key findings.
    - Structure chart data for frontend visualization.
    - Suggest analytical/research actions (NEVER trading signals).
    
    Constraints:
    - NEVER generates trading signals (Buy/Sell/Long/Short).
    - NEVER fetches data, profiles, analyzes, or scores (Layers 1-4).
    - Pure synthesis and formatting.
    """

    @staticmethod
    def generate(
        payload: DataPayload,
        profile: DataProfile,
        insights: List[AnalyticalInsight],
        score: AnalysisScore,
    ) -> AnalysisReport:
        """
        Produces the final AnalysisReport.
        """
        now = datetime.now(timezone.utc)
        
        # 1. Generate Summary
        summary = DataReporter._generate_summary(payload.source_type.value, profile, score)
        
        # 2. Suggest Actions (Analytical only)
        suggested_actions = DataReporter._suggest_actions(score, insights)
        
        # 3. Generate Chart Data Structure
        chart_data = DataReporter._generate_chart_data(payload.data, profile)
        
        return AnalysisReport(
            payload_id=payload.payload_id,
            summary=summary,
            key_findings=insights,
            score=score,
            chart_data=chart_data,
            suggested_actions=suggested_actions,
            generated_at=now
        )

    @staticmethod
    def _generate_summary(source_type: str, profile: DataProfile, score: AnalysisScore) -> str:
        """Creates a concise, non-trading summary based on profile and score metrics."""
        return (
            f"Data analysis of {source_type} source ({profile.row_count} rows, {profile.column_count} columns) "
            f"indicates a {score.significance_level.value} significance level. "
            f"Trend strength: {score.trend_strength:.0%}, Statistical significance: {score.statistical_significance:.0%}."
        )

    @staticmethod
    def _suggest_actions(
        score: AnalysisScore, 
        insights: List[AnalyticalInsight]
    ) -> List[str]:
        """Suggests analytical research actions based on score and insights. STRICTLY NO TRADING SIGNALS."""
        actions = []
        
        if score.anomaly_score == 1.0:
            actions.append("Investigate the root cause of detected statistical outliers before proceeding.")
            
        if score.trend_strength > 0.7:
            actions.append("Review external market drivers or data collection methodology for strong trend validation.")
            
        if score.statistical_significance < 0.5:
            actions.append("Collect additional data points to improve statistical confidence and correlation reliability.")
            
        if not actions:
            actions.append("Continue routine data monitoring and periodic re-profiling.")
            
        return actions

    @staticmethod
    def _generate_chart_data(data: Any, profile: DataProfile) -> List[Dict[str, Any]]:
        """
        Structures raw data into a format suitable for frontend charting libraries (e.g., Recharts, Chart.js).
        Only processes tabular data (list of dicts).
        """
        if not isinstance(data, list) or not data or not isinstance(data[0], dict):
            return []
            
        # Identify numeric columns for charting
        numeric_cols = [
            col for col, stats in profile.basic_stats.items() 
            if "mean" in stats
        ]
        
        if not numeric_cols:
            return []
            
        # Use the first column as the X-axis (usually time, index, or category)
        x_axis = list(data[0].keys())[0]
        
        chart_data = []
        for row in data:
            point = {"x": str(row.get(x_axis, "Unknown"))}
            for col in numeric_cols[1:] if len(numeric_cols) > 1 else numeric_cols:
                val = row.get(col)
                point[col] = float(val) if val is not None and str(val).strip() != "" else 0.0
            chart_data.append(point)
            
        return chart_data
