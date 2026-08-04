from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Union

from .models import DataPayload, DataType

logger = logging.getLogger(__name__)


class DataIngestor:
    """
    Layer 1: Ingestion.
    
    Standardizes raw inputs into a unified DataPayload.
    
    Responsibilities:
    - Read and parse CSV, JSON, and raw text files.
    - Wrap structured in-memory data (Market, Portfolio, Performance) directly.
    - Tag payloads with the correct DataType.
    
    Constraints:
    - NEVER analyzes or profiles data (Layers 2 & 3).
    - Pure I/O and standardization using standard libraries.
    """

    @staticmethod
    def ingest(
        source: Union[str, Path, List[Dict[str, Any]], Dict[str, Any]], 
        data_type: DataType = None
    ) -> DataPayload:
        """
        Ingests raw data from a file path or in-memory structure.
        """
        # 1. File Path Ingestion
        if isinstance(source, (str, Path)):
            path = Path(source)
            if not path.exists():
                raise FileNotFoundError(f"Data source not found: {path}")
            
            # Auto-detect type if not provided
            if data_type is None:
                data_type = DataIngestor._detect_type(path.suffix)
                
            data = DataIngestor._read_file(path, data_type)
            metadata = {"source_path": str(path), "filename": path.name}
            
        # 2. In-Memory Ingestion
        else:
            if data_type is None:
                data_type = DataIngestor._infer_memory_type(source)
            data = source
            metadata = {"source": "memory"}
            
        return DataPayload(
            source_type=data_type,
            data=data,
            metadata=metadata
        )

    @staticmethod
    def _detect_type(suffix: str) -> DataType:
        """Maps file extensions to DataTypes."""
        mapping = {
            ".csv": DataType.CSV,
            ".json": DataType.JSON,
            ".xlsx": DataType.EXCEL,
            ".xls": DataType.EXCEL,
            ".pdf": DataType.PDF,
            ".sql": DataType.SQL,
            ".txt": DataType.PDF, # Treat text files as raw content
        }
        return mapping.get(suffix.lower(), DataType.JSON)

    @staticmethod
    def _infer_memory_type(source: Any) -> DataType:
        """Infers DataType from Python object type."""
        if isinstance(source, list):
            return DataType.MEMORY
        if isinstance(source, dict):
            return DataType.JSON
        if isinstance(source, str):
            return DataType.PDF # Treat raw string as text content
        return DataType.JSON

    @staticmethod
    def _read_file(path: Path, data_type: DataType) -> Any:
        """Reads and parses file contents based on DataType."""
        try:
            if data_type == DataType.CSV:
                with open(path, mode='r', encoding='utf-8') as f:
                    return list(csv.DictReader(f))
                    
            elif data_type == DataType.JSON:
                with open(path, mode='r', encoding='utf-8') as f:
                    return json.load(f)
                    
            elif data_type in (DataType.PDF, DataType.MARKET_DATA, DataType.PORTFOLIO, DataType.PERFORMANCE):
                # Pure python text read. Real PDF parsing requires external libs.
                with open(path, mode='r', encoding='utf-8', errors='ignore') as f:
                    return f.read()
                    
            elif data_type in (DataType.EXCEL, DataType.SQL):
                raise NotImplementedError(
                    f"Ingestion for {data_type.value} requires external libraries (e.g., openpyxl, sqlite3). "
                    "Please parse externally and pass as in-memory data to maintain pure core layer."
                )
            else:
                with open(path, mode='r', encoding='utf-8') as f:
                    return f.read()
                    
        except Exception as e:
            logger.error(f"Failed to ingest {path}: {e}")
            raise
