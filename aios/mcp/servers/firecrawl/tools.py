
from .client import FirecrawlClient

fc = FirecrawlClient()

TOOLS = {

    "fc_scrape": {
        "intent": "scrape_url",
        "category": "research",
        "read_only": True,
        "required_args": ["url"],
        "handler": lambda a: fc.post(
            "/scrape",
            {
                "url": a["url"],
            },
        ),
    },

    "fc_crawl": {
        "intent": "crawl_url",
        "category": "research",
        "read_only": True,
        "required_args": ["url"],
        "handler": lambda a: fc.post(
            "/crawl",
            {
                "url": a["url"],
            },
        ),
    },

    "fc_map": {
        "intent": "map_url",
        "category": "research",
        "read_only": True,
        "required_args": ["url"],
        "handler": lambda a: fc.post(
            "/map",
            {
                "url": a["url"],
            },
        ),
    },

    "fc_extract": {
        "intent": "extract",
        "category": "research",
        "read_only": True,
        "required_args": ["urls","prompt"],
        "handler": lambda a: fc.post(
            "/extract",
            {
                "urls": a["urls"],
                "prompt": a["prompt"],
            },
        ),
    },

}
