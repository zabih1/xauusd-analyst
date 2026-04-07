"""
News fetcher — pulls gold/USD headlines from RSS feeds + optional NewsAPI.
No paid subscription required for basic RSS feeds.
"""
import httpx
import logging
from datetime import datetime, timezone
from typing import List
from xml.etree import ElementTree as ET

from models.schemas import NewsItem
from config import settings

logger = logging.getLogger(__name__)

# Free RSS sources for forex/gold news
RSS_FEEDS = [
    {
        "url": "https://www.forexfactory.com/news?rss",
        "source": "ForexFactory",
    },
    {
        "url": "https://www.fxstreet.com/rss/news",
        "source": "FXStreet",
    },
    {
        "url": "https://feeds.content.dowjones.io/public/rss/mw_marketpulse",
        "source": "MarketWatch",
    },
]

GOLD_KEYWORDS = [
    "gold", "xauusd", "XAU", "bullion", "precious metals",
    "DXY", "dollar index", "fed", "federal reserve", "inflation",
    "cpi", "interest rate", "treasury", "safe haven", "geopolit"
]


async def fetch_rss_feed(url: str, source: str) -> List[NewsItem]:
    """Parse an RSS feed and filter for gold-relevant headlines."""
    items = []
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, follow_redirects=True)
            resp.raise_for_status()

        root = ET.fromstring(resp.text)
        channel = root.find("channel")
        if channel is None:
            return []

        for item in channel.findall("item")[:20]:
            title = item.findtext("title", "").strip()
            link  = item.findtext("link", "").strip()
            pub   = item.findtext("pubDate", "")

            # filter for gold/macro relevant news
            title_lower = title.lower()
            if not any(kw.lower() in title_lower for kw in GOLD_KEYWORDS):
                continue

            try:
                from email.utils import parsedate_to_datetime
                pub_dt = parsedate_to_datetime(pub).astimezone(timezone.utc)
            except Exception:
                pub_dt = datetime.now(timezone.utc)

            items.append(NewsItem(
                title=title,
                source=source,
                published_at=pub_dt,
                url=link,
                impact=_guess_impact(title),
            ))

    except Exception as e:
        logger.warning("RSS fetch failed for %s: %s", source, e)

    return items


async def fetch_newsapi(query: str = "gold price XAU USD") -> List[NewsItem]:
    """Fetch from NewsAPI (requires free API key at newsapi.org)."""
    if not settings.NEWS_API_KEY:
        return []
    try:
        url = "https://newsapi.org/v2/everything"
        params = {
            "q": query,
            "sortBy": "publishedAt",
            "pageSize": 10,
            "apiKey": settings.NEWS_API_KEY,
            "language": "en",
        }
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
            resp.raise_for_status()
            data = resp.json()

        items = []
        for a in data.get("articles", []):
            pub = a.get("publishedAt", "")
            try:
                pub_dt = datetime.fromisoformat(pub.replace("Z", "+00:00"))
            except Exception:
                pub_dt = datetime.now(timezone.utc)

            items.append(NewsItem(
                title=a.get("title", ""),
                source=a.get("source", {}).get("name", "NewsAPI"),
                published_at=pub_dt,
                url=a.get("url"),
                impact=_guess_impact(a.get("title", "")),
            ))
        return items

    except Exception as e:
        logger.warning("NewsAPI fetch failed: %s", e)
        return []


def _guess_impact(title: str) -> str:
    """Heuristic impact labeling based on keywords."""
    title_lower = title.lower()
    high_impact = ["fed", "fomc", "cpi", "nfp", "payroll", "rate decision",
                   "inflation", "war", "sanction", "crisis", "emergency"]
    medium_impact = ["gdp", "pmi", "unemployment", "retail sales", "speech", "statement"]

    if any(kw in title_lower for kw in high_impact):
        return "HIGH"
    if any(kw in title_lower for kw in medium_impact):
        return "MEDIUM"
    return "LOW"


async def get_all_news() -> List[NewsItem]:
    """Aggregate all news sources, deduplicated and sorted by time."""
    all_items: List[NewsItem] = []

    for feed in RSS_FEEDS:
        items = await fetch_rss_feed(feed["url"], feed["source"])
        all_items.extend(items)

    newsapi_items = await fetch_newsapi()
    all_items.extend(newsapi_items)

    # deduplicate by title prefix
    seen = set()
    unique = []
    for item in all_items:
        key = item.title[:40].lower()
        if key not in seen:
            seen.add(key)
            unique.append(item)

    # sort newest first
    unique.sort(key=lambda x: x.published_at, reverse=True)
    return unique[:15]
