from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, func
from typing import List, Optional

from app.database import get_db
from app.models.article import Article
from app.models.bookmark import Bookmark
from app.models.user import User
from app.models.profile import Profile
from app.schemas.article import ArticleResponse, ArticleListResponse, FilterMetaResponse
from app.services.recommendation import recommendation_engine
from app.auth.deps import get_optional_current_user, get_current_user

router = APIRouter(prefix="/api/articles", tags=["Articles & Feeds"])

def format_article_response(article: Article, user_id: Optional[int] = None, match_score: Optional[float] = None, db: Session = None) -> ArticleResponse:
    is_bookmarked = False
    if user_id and db:
        bm = db.query(Bookmark).filter(Bookmark.user_id == user_id, Bookmark.article_id == article.id).first()
        is_bookmarked = bm is not None

    return ArticleResponse(
        id=article.id,
        source_url=article.source_url,
        source_name=article.source_name,
        original_language=article.original_language,
        original_title=article.original_title,
        original_content=article.original_content,
        original_summary=article.original_summary,
        english_title=article.english_title,
        english_summary=article.english_summary,
        english_content=article.english_content,
        region=article.region,
        subregion=article.subregion,
        field=article.field,
        keywords=article.keywords or [],
        trending=article.trending,
        trending_score=article.trending_score,
        image_url=article.image_url,
        published_at=article.published_at,
        created_at=article.created_at,
        match_score=match_score,
        is_bookmarked=is_bookmarked
    )

@router.get("/trending", response_model=ArticleListResponse)
def get_trending_articles(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Retrieve global trending articles ordered by viral/geopolitical impact.
    Note: Trending feed does NOT show personal match percentage.
    """
    query = db.query(Article).order_by(
        desc(Article.trending),
        desc(Article.trending_score),
        desc(Article.published_at)
    )
    articles = query.limit(limit).all()
    user_id = current_user.id if current_user else None

    # Never show match_score in trending feed; match score is personal to onboarding quiz
    items = [format_article_response(a, user_id=user_id, match_score=None, db=db) for a in articles]
    return ArticleListResponse(total=len(items), items=items)

@router.get("/foryou", response_model=ArticleListResponse)
def get_for_you_articles(
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Personalized 'For You' feed using interest graph weights from the 15-question quiz.
    CRITICAL: Only shows match percentage if user is authenticated AND has completed the onboarding quiz.
    """
    profile = None
    user_id = None
    has_completed_quiz = False

    if current_user:
        user_id = current_user.id
        profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
        if profile and profile.completed_onboarding:
            has_completed_quiz = True

    all_articles = db.query(Article).all()
    ranked = recommendation_engine.rank_for_you(all_articles, profile, limit=limit)

    items = [
        format_article_response(
            art,
            user_id=user_id,
            match_score=score if has_completed_quiz else None,
            db=db
        )
        for art, score in ranked
    ]
    return ArticleListResponse(total=len(items), items=items)

@router.get("", response_model=ArticleListResponse)
def filter_articles(
    region: Optional[str] = Query(None),
    language: Optional[str] = Query(None),
    field: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """
    Dynamically filter articles across Region, Language, Category/Field, and Full-Text Search.
    Case-insensitive matching with whitespace trimming and flexible multi-term matching.
    Only computes personal match_score if user is logged in AND completed the onboarding quiz.
    """
    from sqlalchemy import cast, String
    query = db.query(Article)

    if region and region.strip() and region.strip().lower() != "all":
        reg = region.strip().lower()
        if "/" in reg:
            parts = [p.strip() for p in reg.split("/") if p.strip()]
            query = query.filter(or_(*[Article.region.ilike(f"%{p}%") for p in parts]))
        else:
            query = query.filter(
                or_(
                    func.lower(func.trim(Article.region)) == reg,
                    Article.region.ilike(f"%{reg}%"),
                    Article.subregion.ilike(f"%{reg}%") if Article.subregion is not None else False
                )
            )
    
    if language and language.strip() and language.strip().lower() != "all":
        lang = language.strip().lower()
        query = query.filter(func.lower(func.trim(Article.original_language)) == lang)
        
    if field and field.strip() and field.strip().lower() != "all":
        fld = field.strip().lower()
        query = query.filter(
            or_(
                func.lower(func.trim(Article.field)) == fld,
                Article.field.ilike(f"%{fld}%")
            )
        )

    if search and search.strip():
        search_pattern = f"%{search.strip()}%"
        query = query.filter(
            or_(
                Article.english_title.ilike(search_pattern),
                Article.original_title.ilike(search_pattern),
                Article.english_summary.ilike(search_pattern),
                Article.original_summary.ilike(search_pattern),
                Article.source_name.ilike(search_pattern),
                Article.field.ilike(search_pattern),
                Article.region.ilike(search_pattern),
                cast(Article.keywords, String).ilike(search_pattern)
            )
        )

    total = query.count()
    articles = query.order_by(desc(Article.published_at)).offset(offset).limit(limit).all()

    # CRITICAL: Only compute match_score if user is authenticated AND has completed the quiz
    profile = None
    has_completed_quiz = False
    user_id = None
    if current_user:
        user_id = current_user.id
        profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()
        if profile and profile.completed_onboarding:
            has_completed_quiz = True

    items = []
    for a in articles:
        match_score = None
        if has_completed_quiz and profile:
            match_score = recommendation_engine.score_article(a, profile)
        items.append(format_article_response(a, user_id=user_id, match_score=match_score, db=db))

    return ArticleListResponse(total=total, items=items)

@router.get("/meta/filters", response_model=FilterMetaResponse)
def get_filter_metadata(db: Session = Depends(get_db)):
    """Return available distinct regions, languages, and fields present in the database."""
    regions = sorted(list(set(r[0].strip() for r in db.query(Article.region).distinct().all() if r[0] and r[0].strip())))
    languages = sorted(list(set(l[0].strip() for l in db.query(Article.original_language).distinct().all() if l[0] and l[0].strip())))
    fields = sorted(list(set(f[0].strip() for f in db.query(Article.field).distinct().all() if f[0] and f[0].strip())))

    # Sensible fallback defaults if database has not yet ingested articles
    if not regions:
        regions = ["Gujarat", "India", "Kerala", "Maharashtra", "Tamil Nadu", "Telangana/Andhra Pradesh"]
    if not languages:
        languages = ["Gujarati", "Hindi", "Malayalam", "Marathi", "Tamil", "Telugu"]
    if not fields:
        fields = [
            "Agriculture & Rural",
            "Culture & Society",
            "Education & Jobs",
            "Entertainment & Cinema",
            "Finance & Economics",
            "Health & Wellness",
            "Politics",
            "States & Regional",
            "Technology & AI"
        ]

    return FilterMetaResponse(
        regions=regions,
        languages=languages,
        fields=fields
    )

@router.get("/{article_id}", response_model=ArticleResponse)
def get_article(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: Optional[User] = Depends(get_optional_current_user)
):
    """Retrieve full article detail with original text and English translation."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")
        
    user_id = current_user.id if current_user else None
    return format_article_response(article, user_id=user_id, db=db)

@router.post("/{article_id}/bookmark")
def toggle_bookmark(
    article_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle bookmark saved state for an article."""
    article = db.query(Article).filter(Article.id == article_id).first()
    if not article:
        raise HTTPException(status_code=404, detail="Article not found")

    existing = db.query(Bookmark).filter(
        Bookmark.user_id == current_user.id,
        Bookmark.article_id == article_id
    ).first()

    if existing:
        db.delete(existing)
        db.commit()
        return {"bookmarked": False, "message": "Bookmark removed"}
    else:
        new_bm = Bookmark(user_id=current_user.id, article_id=article_id)
        db.add(new_bm)
        db.commit()
        return {"bookmarked": True, "message": "Article saved to bookmarks"}
