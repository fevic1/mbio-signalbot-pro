from dataclasses import dataclass

@dataclass(slots=True)
class KnowledgeReaderConfig:
    chunk_size: int = 1200
    overlap: int = 200
    max_file_size_mb: int = 100
