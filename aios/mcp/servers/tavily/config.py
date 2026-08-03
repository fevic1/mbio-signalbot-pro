
import os
from dataclasses import dataclass

@dataclass(slots=True)
class TavilyConfig:
    api_key=os.getenv("TAVILY_API_KEY","")
    base_url="https://api.tavily.com"
    timeout=30
