from dataclasses import dataclass

@dataclass(slots=True)
class WikiArticle:
    title: str
    summary: str
    url: str
