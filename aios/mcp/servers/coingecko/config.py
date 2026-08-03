
from dataclasses import dataclass

@dataclass(slots=True)
class CoinGeckoConfig:
    base_url="https://api.coingecko.com/api/v3"
    timeout=20
