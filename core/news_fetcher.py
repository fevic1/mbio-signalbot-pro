import requests
import xml.etree.ElementTree as ET
import logging
import os

logger = logging.getLogger(__name__)

def fetch_headlines(asset: str = "BTC", limit: int = 5):
    """
    Fetches recent crypto headlines.
    Uses CryptoPanic API if token is available, otherwise falls back to public RSS feeds.
    """
    headlines = []
    
    # 1. Try CryptoPanic API if token is available (Best for asset-specific news)
    token = os.getenv("CRYPTOPANIC_TOKEN")
    if token:
        try:
            url = f"https://cryptopanic.com/api/v1/posts/?auth_token={token}&public=true&currencies={asset}&kind=news"
            resp = requests.get(url, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                for item in data.get("results", [])[:limit]:
                    headlines.append(item.get("title", ""))
                if headlines:
                    return headlines
        except Exception as e:
            logger.debug(f"CryptoPanic API failed: {e}")

    # 2. Fallback to Public RSS Feeds (No API key required, general market sentiment)
    rss_urls = [
        "https://cointelegraph.com/rss",
        "https://www.coindesk.com/arc/outboundfeeds/rss/"
    ]
    
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    
    for url in rss_urls:
        try:
            resp = requests.get(url, headers=headers, timeout=5)
            if resp.status_code == 200:
                root = ET.fromstring(resp.content)
                for item in root.findall('.//item'):
                    title = item.find('title')
                    if title is not None and title.text:
                        headlines.append(title.text)
                        if len(headlines) >= limit:
                            break
            if len(headlines) >= limit:
                break
        except Exception as e:
            logger.debug(f"RSS feed {url} failed: {e}")
            continue

    return headlines
