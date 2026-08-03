
from dataclasses import dataclass

@dataclass(slots=True)
class DefiLlamaConfig:
    base_url="https://api.llama.fi"
    timeout=20
