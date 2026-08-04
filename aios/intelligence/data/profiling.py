from __future__ import annotations

import logging
import statistics
from datetime import datetime, timezone
from typing import Any, Dict, List

from .models import DataPayload, DataProfile

logger = logging.getLogger(__name__)


class DataProfiler:
    """
    Layer 2: Profiling.
    
    Validates data and calculates basic structural statistics.
    
    Responsibilities:
    - Count rows and columns.
    - Detect null/empty values per column.
    - Infer data types per column.
    - Calculate basic stats (min, max, mean, median, std) for numeric columns.
    
    Constraints:
    - NEVER analyzes meaning, trends, or correlations (Layer 3).
    - Pure structural analysis using standard library.
    """

    @staticmethod
    def profile(payload: DataPayload) -> DataProfile:
        """
        Generates a DataProfile from a DataPayload.
        """
        data = payload.data
        
        # Handle tabular data (List of Dicts)
        if isinstance(data, list) and len(data) > 0 and isinstance(data[0], dict):
            return DataProfiler._profile_tabular(data, payload.payload_id)
            
        # Handle single Dict
        elif isinstance(data, dict):
            return DataProfiler._profile_dict(data, payload.payload_id)
            
        # Handle raw text/string
        elif isinstance(data, str):
            return DataProfiler._profile_text(data, payload.payload_id)
            
        # Fallback for unsupported types
        else:
            logger.warning(f"Unsupported data type for profiling: {type(data)}")
            return DataProfile(
                payload_id=payload.payload_id,
                row_count=0,
                column_count=0,
                null_counts={},
                data_types={},
                basic_stats={},
                profiled_at=datetime.now(timezone.utc)
            )

    @staticmethod
    def _profile_tabular(rows: List[Dict[str, Any]], payload_id: str) -> DataProfile:
        """Profiles a list of dictionaries (tabular data)."""
        row_count = len(rows)
        columns = list(rows[0].keys()) if rows else []
        column_count = len(columns)
        
        null_counts = {col: 0 for col in columns}
        data_types = {col: set() for col in columns}
        numeric_values = {col: [] for col in columns}
        
        for row in rows:
            for col in columns:
                val = row.get(col)
                
                # Null detection
                if val is None or (isinstance(val, str) and val.strip() == ""):
                    null_counts[col] += 1
                else:
                    data_types[col].add(DataProfiler._get_type_name(val))
                    if DataProfiler._is_numeric(val):
                        numeric_values[col].append(float(val))
                        
        # Calculate basic stats for numeric columns
        basic_stats = {}
        for col in columns:
            vals = numeric_values[col]
            if len(vals) >= 2:
                basic_stats[col] = {
                    "min": round(min(vals), 4),
                    "max": round(max(vals), 4),
                    "mean": round(statistics.mean(vals), 4),
                    "median": round(statistics.median(vals), 4),
                    "std": round(statistics.stdev(vals), 4)
                }
            elif len(vals) == 1:
                basic_stats[col] = {
                    "min": round(vals[0], 4),
                    "max": round(vals[0], 4),
                    "mean": round(vals[0], 4),
                    "median": round(vals[0], 4),
                    "std": 0.0
                }
            else:
                basic_stats[col] = {}
                
        # Convert sets to sorted lists for serializability
        data_types_final = {col: sorted(list(types)) for col, types in data_types.items()}
        
        return DataProfile(
            payload_id=payload_id,
            row_count=row_count,
            column_count=column_count,
            null_counts=null_counts,
            data_types=data_types_final,
            basic_stats=basic_stats,
            profiled_at=datetime.now(timezone.utc)
        )

    @staticmethod
    def _profile_dict(data: Dict[str, Any], payload_id: str) -> DataProfile:
        """Profiles a single dictionary."""
        columns = list(data.keys())
        null_counts = {k: 1 if v is None else 0 for k, v in data.items()}
        data_types = {k: [DataProfiler._get_type_name(v)] for k, v in data.items() if v is not None}
        
        numeric_values = {k: [float(v)] for k, v in data.items() if DataProfiler._is_numeric(v)}
        basic_stats = {
            k: {"min": v[0], "max": v[0], "mean": v[0], "median": v[0], "std": 0.0} 
            for k, v in numeric_values.items()
        }
        
        return DataProfile(
            payload_id=payload_id,
            row_count=1,
            column_count=len(columns),
            null_counts=null_counts,
            data_types=data_types,
            basic_stats=basic_stats,
            profiled_at=datetime.now(timezone.utc)
        )

    @staticmethod
    def _profile_text(text: str, payload_id: str) -> DataProfile:
        """Profiles raw text content."""
        return DataProfile(
            payload_id=payload_id,
            row_count=1,
            column_count=1,
            null_counts={"content": 0 if text.strip() else 1},
            data_types={"content": ["str"]},
            basic_stats={
                "content": {
                    "char_count": len(text),
                    "word_count": len(text.split()),
                    "line_count": len(text.splitlines())
                }
            },
            profiled_at=datetime.now(timezone.utc)
        )

    @staticmethod
    def _is_numeric(val: Any) -> bool:
        """Checks if a value is numeric (excluding booleans)."""
        return isinstance(val, (int, float)) and not isinstance(val, bool)

    @staticmethod
    def _get_type_name(val: Any) -> str:
        """Returns a clean type name for a value."""
        if val is None:
            return "null"
        return type(val).__name__
