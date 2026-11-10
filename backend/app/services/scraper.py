import feedparser
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import concurrent.futures
import logging

from app.services.dedup import normalize_canonical_url, compute_article_fingerprint

logger = logging.getLogger(__name__)

# Check for newspaper3k and compatible lxml cleaner availability
try:
    import newspaper
    from newspaper import Article as NewspaperArticle, Config as NewspaperConfig
    HAS_NEWSPAPER = True
except (ImportError, ModuleNotFoundError) as err:
    HAS_NEWSPAPER = False
    logger.warning(
        f"newspaper3k is not available in the active Python environment ({err}). "
        "RSS feed description text will be used as fallback content."
    )

CURATED_RSS_FEEDS = [
    {
        "name": "Le Monde",
        "url": "https://www.lemonde.fr/rss/une.xml",
        "language": "French",
        "region": "Europe"
    },
    {
        "name": "El País",
        "url": "https://feeds.elpais.com/mrss-s/pages/ep/site/elpais.com/portada",
        "language": "Spanish",
        "region": "Europe"
    },
    {
        "name": "BBC Mundo",
        "url": "https://feeds.bbci.co.uk/mundo/rss.xml",
        "language": "Spanish",
        "region": "Latin America"
    },
    {
        "name": "Deutsche Welle",
        "url": "https://rss.dw.com/rdf/rss-de-all",
        "language": "German",
        "region": "Europe"
    },
    {
        "name": "NHK World News",
        "url": "https://www.nhk.or.jp/rss/news/cat0.xml",
        "language": "Japanese",
        "region": "Asia-Pacific"
    },
    {
        "name": "Al Jazeera",
        "url": "https://www.aljazeera.net/aljazeerarss/a7c6e2fb-8371-47bb-8315-4f06abb1e959/732e43be-5668-4e1d-8422-50e0489a8e38",
        "language": "Arabic",
        "region": "Middle East"
    },
    {
        "name": "BBC World",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "language": "English",
        "region": "Global"
    }
]

import os
import json

def get_configured_feeds() -> List[Dict[str, str]]:
    """Load feeds from backend/rss_feeds.json if present, else fallback to default feeds."""
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    feeds_file = os.path.join(base_dir, "rss_feeds.json")
    if os.path.exists(feeds_file):
        try:
            with open(feeds_file, "r", encoding="utf-8") as f:
                feeds = json.load(f)
                if isinstance(feeds, list) and len(feeds) > 0:
                    return feeds
        except Exception as e:
            logger.warning(f"Error reading rss_feeds.json: {e}")
    return CURATED_RSS_FEEDS

def clean_html(raw_html: str) -> str:
    """Strip HTML tags, decode entities, and convert whitespace to clean readable text."""
    if not raw_html:
        return ""
    import html
    import re
    decoded = html.unescape(raw_html)
    soup = BeautifulSoup(decoded, "html.parser")
    for el in soup(["script", "style", "noscript", "iframe"]):
        el.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r'<[^>]+>', ' ', text)
    return " ".join(text.split())

class NewsScraper:
    def __init__(self, headers: dict = None):
        self.headers = headers or {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) MultilingualNewsDigest/1.0"
        }

    def fetch_feed(self, feed_meta: Dict[str, str], max_items: int = 5) -> List[Dict[str, Any]]:
        """Fetch and parse articles from a single RSS feed with timeout."""
        name = feed_meta["name"]
        url = feed_meta["url"]
        articles = []
        try:
            logger.info(f"Fetching RSS feed for {name} from {url}")
            resp = requests.get(url, headers=self.headers, timeout=(5.0, 10.0))
            if resp.status_code != 200:
                logger.warning(f"Feed {name} responded with status {resp.status_code}")
                return []
            
            feed = feedparser.parse(resp.content)
            
            for entry in feed.entries[:max_items]:
                title = clean_html(getattr(entry, "title", ""))
                link = getattr(entry, "link", "")
                
                if not link or not title:
                    continue

                # Content / Description extraction (Fallback)
                summary_raw = getattr(entry, "summary", "") or getattr(entry, "description", "")
                fallback_content = clean_html(summary_raw)
                
                # Image extraction (Fallback)
                image_url = None
                if "media_content" in entry and entry.media_content:
                    image_url = entry.media_content[0].get("url")
                elif "enclosures" in entry and entry.enclosures:
                    image_url = entry.enclosures[0].get("href")

                # Try Newspaper3k Extraction Module
                extracted_content = ""
                extracted_image = ""
                extracted_authors = []
                if HAS_NEWSPAPER:
                    try:
                        config = NewspaperConfig()
                        config.browser_user_agent = self.headers.get("User-Agent", "Mozilla/5.0")
                        config.request_timeout = 7
                        article = NewspaperArticle(link, config=config)
                        article.download()
                        article.parse()
                        extracted_content = article.text or ""
                        extracted_image = article.top_image or ""
                        extracted_authors = article.authors or []
                    except Exception as ex:
                        logger.warning(f"newspaper3k failed for {link}: {ex}")

                # Choose best content and image
                final_content = extracted_content if extracted_content and len(extracted_content) > 100 else fallback_content
                if not final_content or len(final_content) < 40:
                    final_content = title
                    
                final_image = extracted_image if extracted_image else image_url

                # Publication date
                pub_date = datetime.utcnow()
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        pub_date = datetime(*entry.published_parsed[:6])
                    except Exception:
                        pass

                canonical_url = normalize_canonical_url(link)
                fingerprint = compute_article_fingerprint(title, name, canonical_url)

                articles.append({
                    "source_url": link,
                    "canonical_url": canonical_url,
                    "fingerprint": fingerprint,
                    "source_name": name,
                    "title": title,
                    "content": final_content,
                    "image_url": final_image,
                    "authors": extracted_authors,
                    "published_at": pub_date,
                    "expected_language": feed_meta.get("language", "English"),
                    "expected_region": feed_meta.get("region", "Global")
                })
        except Exception as e:
            logger.warning(f"Could not scrape feed {name} ({url}): {e}")

        return articles

    def scrape_all(self, max_per_feed: int = 4, max_workers: int = 8) -> List[Dict[str, Any]]:
        """
        Scrape articles across all configured international sources in parallel
        for fast RSS extraction.
        """
        feeds = get_configured_feeds()
        all_articles = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_feed = {executor.submit(self.fetch_feed, feed, max_items=max_per_feed): feed for feed in feeds}
            for future in concurrent.futures.as_completed(future_to_feed):
                try:
                    feed_articles = future.result()
                    if feed_articles:
                        all_articles.extend(feed_articles)
                except Exception as ex:
                    feed_name = future_to_feed[future].get("name", "Unknown")
                    logger.warning(f"Parallel fetch failed for feed {feed_name}: {ex}")
        
        # If all live feeds failed (e.g. offline/network blocked), fallback to sample seed items
        if len(all_articles) == 0:
            logger.info("All live RSS feeds timed out or returned empty. Using fallback sample dispatches.")
            from app.services.seed_data import SAMPLE_ARTICLES
            for s in SAMPLE_ARTICLES:
                c_url = normalize_canonical_url(s["source_url"])
                fg = compute_article_fingerprint(s["original_title"], s["source_name"], c_url)
                all_articles.append({
                    "source_url": s["source_url"],
                    "canonical_url": c_url,
                    "fingerprint": fg,
                    "source_name": s["source_name"],
                    "title": s["original_title"],
                    "content": s["original_content"],
                    "image_url": s.get("image_url"),
                    "published_at": s.get("published_at", datetime.now(timezone.utc)),
                    "expected_language": s["original_language"],
                    "expected_region": s["region"],
                })

        return all_articles

        return all_articles

scraper = NewsScraper()
