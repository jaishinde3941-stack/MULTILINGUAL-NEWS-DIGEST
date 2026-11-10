import hashlib
import re
import urllib.parse
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.models.article import Article
from app.models.history import ArticleHistory

# Tracking and query parameters to strip for canonical URL matching
TRACKING_PARAMS = {
    "utm_source", "utm_medium", "utm_campaign", "utm_term", "utm_content",
    "fbclid", "gclid", "msclkid", "ref", "ref_src", "source", "ncid",
    "cmp", "ito", "from", "at_custom1", "at_custom2", "feature", "time-period"
}

def normalize_canonical_url(url: str) -> str:
    """
    Standardize a source URL by stripping tracking parameters, fragments,
    lowercasing domain/scheme, and removing trailing slashes.
    """
    if not url:
        return ""
    try:
        parsed = urllib.parse.urlparse(url.strip())
        # Lowercase scheme and netloc
        scheme = parsed.scheme.lower()
        netloc = parsed.netloc.lower()
        
        # Strip tracking queries
        query_pairs = urllib.parse.parse_qsl(parsed.query, keep_blank_values=False)
        clean_pairs = [(k, v) for k, v in query_pairs if k.lower() not in TRACKING_PARAMS]
        clean_query = urllib.parse.urlencode(clean_pairs)

        # Normalize path
        path = parsed.path
        if path != "/" and path.endswith("/"):
            path = path[:-1]

        canonical = urllib.parse.urlunparse((scheme, netloc, path, parsed.params, clean_query, ""))
        return canonical
    except Exception:
        return url.strip().split("#")[0].rstrip("/")

def compute_article_fingerprint(title: str, source_name: str, canonical_url: str) -> str:
    """
    Generate a stable SHA-256 fingerprint from the normalized title,
    source publisher, and canonical URL.
    """
    # Normalize title: lowercase and collapse whitespace/punctuation
    norm_title = re.sub(r'[\s\W_]+', ' ', (title or "").lower()).strip()
    norm_source = re.sub(r'[\s\W_]+', ' ', (source_name or "").lower()).strip()
    norm_url = (canonical_url or "").lower().strip()
    
    token = f"{norm_source}::{norm_title}::{norm_url}"
    return hashlib.sha256(token.encode("utf-8")).hexdigest()

def is_duplicate_article(db: Session, canonical_url: str, fingerprint: str, source_url: Optional[str] = None) -> bool:
    """
    Fast pre-check to detect duplicates across:
    1. Permanent ArticleHistory deduplication records.
    2. Current active, reserve, or consumed Article table records.
    """
    if not fingerprint and not canonical_url:
        return False

    # 1. Check permanent history
    hist_match = db.query(ArticleHistory.id).filter(
        or_(
            ArticleHistory.fingerprint == fingerprint,
            ArticleHistory.canonical_url == canonical_url
        )
    ).first()
    if hist_match:
        return True

    # 2. Check current articles table (active, reserve, or consumed)
    filters = []
    if fingerprint:
        filters.append(Article.article_fingerprint == fingerprint)
    if canonical_url:
        filters.append(Article.canonical_url == canonical_url)
    if source_url:
        filters.append(Article.source_url == source_url)

    if filters:
        art_match = db.query(Article.id).filter(or_(*filters)).first()
        if art_match:
            return True

    return False

