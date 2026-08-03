
from .client import TavilyClient

tv = TavilyClient()

TOOLS = {

    "tv_search": {
        "intent": "web_search",
        "category": "research",
        "read_only": True,
        "required_args": ["query"],
        "handler": lambda a: tv.post(
            "/search",
            {
                "query": a["query"],
            },
        ),
    },

    "tv_extract": {
        "intent": "web_extract",
        "category": "research",
        "read_only": True,
        "required_args": ["url"],
        "handler": lambda a: tv.post(
            "/extract",
            {
                "urls": [a["url"]],
            },
        ),
    },

}
