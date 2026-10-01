from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
from app.models.article import Article
from app.models.profile import Profile

class RecommendationEngine:
    def score_article(self, article: Article, profile: Optional[Profile]) -> float:
        """
        Calculate personalized match score (0.0 to 1.0) between an article and user profile.
        """
        if not profile or not profile.interest_weights:
            # Baseline score for unauthenticated or un-onboarded users
            recency_bonus = 0.2
            return round((article.trending_score * 0.7) + recency_bonus, 3)

        weights: Dict[str, float] = profile.interest_weights or {}
        score = 0.0
        match_factors = 0

        # 1. Region match
        region_key = f"region:{article.region}"
        if region_key in weights:
            score += weights[region_key] * 2.0
            match_factors += 2
        elif "/" in article.region:
            for p in article.region.split("/"):
                pk = f"region:{p.strip()}"
                if pk in weights:
                    score += weights[pk] * 2.0
                    match_factors += 2
                    break

        # 2. Subregion match
        if article.subregion:
            subregion_key = f"subregion:{article.subregion}"
            if subregion_key in weights:
                score += weights[subregion_key] * 1.5
                match_factors += 1.5

        # 3. Field / Topic match
        field_key = f"field:{article.field}"
        if field_key in weights:
            score += weights[field_key] * 2.5
            match_factors += 2.5

        # 4. Language match
        lang_key = f"lang:{article.original_language}"
        if lang_key in weights:
            score += weights[lang_key] * 2.0
            match_factors += 2

        # 5. Keywords match
        if article.keywords:
            for kw in article.keywords:
                kw_key = f"tag:{kw.lower()}"
                if kw_key in weights:
                    score += weights[kw_key] * 1.5
                    match_factors += 1.5

        normalized_affinity = (score / match_factors) if match_factors > 0 else 0.45

        # Trending multiplier (blend personalization with global buzz)
        trending_weight = 0.20
        affinity_weight = 0.70
        recency_weight = 0.10

        # Recency calculation (decay over 7 days)
        now = datetime.now(timezone.utc)
        pub = article.published_at
        if pub.tzinfo is None:
            now = now.replace(tzinfo=None)
        hours_old = max(0, (now - pub).total_seconds() / 3600.0)
        recency_score = max(0.1, 1.0 - (hours_old / 168.0))

        final_score = (
            (normalized_affinity * affinity_weight) +
            (article.trending_score * trending_weight) +
            (recency_score * recency_weight)
        )

        return round(min(1.0, max(0.0, final_score)), 3)

    def rank_for_you(self, articles: List[Article], profile: Optional[Profile], limit: int = 20) -> List[tuple[Article, float]]:
        """Rank articles for the user's personalized 'For You' feed."""
        scored = []
        for art in articles:
            s = self.score_article(art, profile)
            scored.append((art, s))
        
        # Sort by descending score
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:limit]

recommendation_engine = RecommendationEngine()
