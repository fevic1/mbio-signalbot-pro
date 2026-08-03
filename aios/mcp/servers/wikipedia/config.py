from dataclasses import dataclass

@dataclass(slots=True)
class WikipediaConfig:
    language: str = "en"
    timeout: int = 15
