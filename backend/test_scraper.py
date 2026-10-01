import os
import sys
# Add backend dir to sys.path so app module can be found
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.scraper import scraper
import json

def test():
    print("Testing NewsScraper pipeline with newspaper3k...")
    
    # We will test on a single feed for faster response
    test_feed = {
        "name": "BBC World",
        "url": "https://feeds.bbci.co.uk/news/world/rss.xml",
        "language": "English",
        "region": "Global"
    }
    
    articles = scraper.fetch_feed(test_feed, max_items=2)
    
    for idx, art in enumerate(articles, 1):
        print(f"\n--- Article {idx} ---")
        print(f"Title: {art['title']}")
        print(f"URL: {art['source_url']}")
        print(f"Authors: {art.get('authors', [])}")
        
        content = art['content']
        content_preview = (content[:200] + '...') if len(content) > 200 else content
        print(f"Extracted Text Preview ({len(content)} chars): {content_preview}")
        
    print("\nTest completed.")

if __name__ == "__main__":
    test()
