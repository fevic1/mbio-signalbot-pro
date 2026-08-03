
import os
from dataclasses import dataclass

@dataclass(slots=True)
class FirecrawlConfig:
    api_key = os.getenv("FIRECRAWL_API_KEY","")
    base_url = "https://api.firecrawl.dev/v1"
    timeout = 30
