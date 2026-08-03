from dataclasses import dataclass

@dataclass(slots=True)
class DexConfig:
    base_url: str = "https://api.dexscreener.com/latest"
    timeout: int = 15
