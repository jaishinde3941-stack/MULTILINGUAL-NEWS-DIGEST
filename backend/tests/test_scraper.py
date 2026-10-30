import pytest
from app.services.scraper import scraper, HAS_NEWSPAPER, clean_html

def test_newspaper_imports_and_cleaner():
    """Verify newspaper3k and lxml_html_clean are properly imported in backend venv."""
    import newspaper
    from newspaper import Article, Config
    import lxml
    import lxml_html_clean
    from lxml.html.clean import Cleaner

    assert HAS_NEWSPAPER is True
    assert newspaper is not None
    assert Article is not None
    assert Config is not None
    assert Cleaner is not None

def test_newspaper_article_extraction():
    """Verify newspaper.Article parses html structure correctly."""
    from newspaper import Article, Config

    sample_url = "https://example.com/test-article"
    sample_html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Global Renewable Energy Breakthrough Announced</title>
        <meta name="author" content="Jane Doe, John Smith">
        <meta property="og:image" content="https://example.com/images/solar.jpg">
    </head>
    <body>
        <h1>Global Renewable Energy Breakthrough Announced</h1>
        <p>Scientists and energy engineers announced a major advancement in photovoltaic efficiency today.</p>
        <p>The novel tandem cell architecture achieves 34 percent solar-to-electric conversion in lab conditions.</p>
        <p>Commercial deployment is projected to begin in late 2027 following industrial durability evaluations.</p>
    </body>
    </html>
    """

    config = Config()
    config.request_timeout = 5
    article = Article(sample_url, config=config)
    article.set_html(sample_html)
    article.parse()

    assert "Global Renewable Energy Breakthrough Announced" in article.title
    assert "photovoltaic efficiency" in article.text
    assert len(article.text) > 50
    assert article.top_image == "https://example.com/images/solar.jpg"

def test_scraper_clean_html():
    """Verify clean_html removes unwanted tags and normalizes whitespace."""
    raw = "<p>Breaking News: <b>Markets Rally</b></p><script>alert('bad');</script>"
    cleaned = clean_html(raw)
    assert cleaned == "Breaking News: Markets Rally"

def test_scraper_fetch_feed_with_newspaper_mock(monkeypatch):
    """Verify scraper.fetch_feed integrates with newspaper3k extraction."""
    from unittest.mock import MagicMock
    import requests

    sample_rss = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Test Global News</title>
            <link>https://example.com/rss</link>
            <description>Sample Feed</description>
            <item>
                <title>Autonomous Electric Aviation Project Launches</title>
                <link>https://example.com/article/1</link>
                <description>Brief snippet about electric aviation test flights.</description>
            </item>
        </channel>
    </rss>"""

    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.content = sample_rss.encode("utf-8")

    monkeypatch.setattr(requests, "get", lambda *args, **kwargs: mock_resp)

    # Mock NewspaperArticle parse to return enriched article text
    class MockArticle:
        def __init__(self, url, config=None):
            self.url = url
            self.text = "Aerospace consortium unveiled commercial autonomous electric aircraft flight trials across multiple continental flight corridors following regulatory approval."
            self.top_image = "https://example.com/plane.jpg"
            self.authors = ["Aviation Correspondent"]

        def download(self):
            pass

        def parse(self):
            pass

    import sys
    scraper_module = sys.modules["app.services.scraper"]
    monkeypatch.setattr(scraper_module, "NewspaperArticle", MockArticle)

    feed_meta = {
        "name": "Global Aerospace",
        "url": "https://example.com/rss.xml",
        "language": "English",
        "region": "Global"
    }

    articles = scraper.fetch_feed(feed_meta, max_items=1)
    assert len(articles) == 1
    art = articles[0]
    assert art["title"] == "Autonomous Electric Aviation Project Launches"
    assert "Aerospace consortium" in art["content"]
    assert art["image_url"] == "https://example.com/plane.jpg"
    assert "Aviation Correspondent" in art["authors"]
