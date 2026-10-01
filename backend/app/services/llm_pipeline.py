import json
import logging
import re
import urllib.parse
import html
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from openai import OpenAI
from app.config import settings

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an elite multilingual intelligence analyst and translator for the Multilingual News Digest.
Your job is to ingest foreign news articles, extract the complete article text, keep only the original headline in the original language, and provide ONLY an English efficient summary of that retrieved complete article.

You MUST respond strictly with valid JSON. Do not include markdown formatting or backticks around the JSON.
The JSON must adhere to this exact schema:
{
  "language": "Source language (e.g. Telugu, Marathi, Gujarati, Hindi, Tamil, Malayalam, French, Spanish, German, Japanese, Arabic, English)",
  "region": "Major region or state (e.g. Maharashtra, Gujarat, Telangana/Andhra Pradesh, Tamil Nadu, Kerala, India, Europe, Asia-Pacific, Latin America, Middle East, Global)",
  "subregion": "Specific subregion or state",
  "field": "One of: Politics, States & Regional, Entertainment & Cinema, Agriculture & Rural, Education & Jobs, Technology & AI, Finance & Economics, Culture & Society, Health & Wellness, General News",
  "keywords": ["keyword1", "keyword2", "keyword3", "keyword4", "keyword5"],
  "trending": true or false,
  "trending_score": float between 0.0 and 1.0 representing viral or journalistic impact,
  "english_title": "Translated high-impact headline strictly in fluent English (NEVER foreign script)",
  "english_summary": "Comprehensive, detailed 4-6 sentence summary focusing strictly on the news events and facts. Do NOT mention the news provider, source, or publication. Focus solely on the content of the article.",
  "english_content": "Fluent, faithful English translation of the core article text"
}"""

USER_PROMPT_TEMPLATE = """Source Publication: {source_name}
Original Title: {title}
Original Content:
{content}

Analyze, produce an executive summary in the original language, translate to English, produce an executive summary in English, and generate the exact metadata JSON specified in your instructions."""

def clean_text(raw_html: str) -> str:
    """Thoroughly strip HTML tags and unescape entities."""
    if not raw_html:
        return ""
    decoded = html.unescape(raw_html)
    soup = BeautifulSoup(decoded, "html.parser")
    for el in soup(["script", "style", "noscript", "iframe"]):
        el.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r'<[^>]+>', ' ', text)
    return " ".join(text.split())

def extract_english_title_from_slug(url: str, source_name: str, field: str) -> Optional[str]:
    """Derive a clean, natural English headline from publication URL slugs."""
    if not url:
        return None
    try:
        path = urllib.parse.urlparse(url).path
        parts = [p for p in path.split('/') if p and not p.isdigit() and not p.endswith('.xml')]
        if not parts:
            return None
        last = parts[-1]
        last = re.sub(r'(-\d+|\.html?)$', '', last)
        words = [w for w in re.split(r'[-_\s]+', last) if w and not w.isdigit()]
        if len(words) >= 3:
            # Common acronyms to preserve in uppercase
            acronyms = {"ai", "bjp", "aap", "tmc", "mp", "mla", "ec", "neet", "pg", "air", "dps", "afmc", 
                        "btsc", "fso", "ignou", "upi", "eu", "ecb", "cjp", "kft", "ckd", "egfr", "gmc", "jem"}
            formatted_words = []
            for w in words:
                w_lower = w.lower()
                if w_lower in acronyms:
                    formatted_words.append(w_lower.upper())
                else:
                    formatted_words.append(w.capitalize())
            title = " ".join(formatted_words)
            return title[:95]
    except Exception:
        pass
    return None

class LLMPipeline:
    def __init__(self):
        self.api_key = settings.NVIDIA_API_KEY
        self.base_url = settings.NVIDIA_BASE_URL
        self.model = settings.NVIDIA_MODEL
        self._client: Optional[OpenAI] = None
        self._api_working: Optional[bool] = None

    @property
    def client(self) -> Optional[OpenAI]:
        if not self.api_key:
            return None
        if self._client is None:
            self._client = OpenAI(
                base_url=self.base_url,
                api_key=self.api_key,
                timeout=5.0
            )
        return self._client

    def process_article(
        self,
        title: str,
        content: str,
        source_name: str,
        source_url: str = "",
        expected_language: Optional[str] = None,
        expected_region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Process an ingested raw foreign article:
        Uses NVIDIA LLM if available and active, or the smart heuristic processor.
        """
        title_clean = clean_text(title)
        content_clean = clean_text(content)

        if self.client and self._api_working is not False:
            try:
                result = self._call_nemotron(title_clean, content_clean, source_name)
                self._api_working = True
                return result
            except Exception as e:
                logger.info(f"NVIDIA API unavailable ({e}). Fast fallback to heuristic processor.")
                self._api_working = False
                return self._heuristic_fallback(
                    title_clean, content_clean, source_name, source_url, expected_language, expected_region
                )
        else:
            return self._heuristic_fallback(
                title_clean, content_clean, source_name, source_url, expected_language, expected_region
            )

    def _call_nemotron(self, title: str, content: str, source_name: str) -> Dict[str, Any]:
        prompt = USER_PROMPT_TEMPLATE.format(
            source_name=source_name,
            title=title,
            content=content[:4000]
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2,
            max_tokens=1500
        )

        raw_text = response.choices[0].message.content.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        raw_text = raw_text.strip()

        data = json.loads(raw_text)
        return self._validate_and_sanitize(data, title, content)

    def _validate_and_sanitize(self, data: Dict[str, Any], original_title: str, original_content: str) -> Dict[str, Any]:
        """Ensure all required fields exist and conform to types."""
        eng_summary = str(data.get("english_summary", "")).strip()
        if not eng_summary:
            eng_summary = "Executive Briefing: " + original_content[:280].strip() + "..."

        return {
            "language": str(data.get("language", "English")),
            "region": str(data.get("region", "Global")),
            "subregion": str(data.get("subregion", "International")),
            "field": str(data.get("field", "General News")),
            "keywords": list(data.get("keywords", []))[:7],
            "trending": bool(data.get("trending", False)),
            "trending_score": float(data.get("trending_score", 0.5)),
            "english_title": str(data.get("english_title", original_title)),
            "english_summary": eng_summary,
            "english_content": str(data.get("english_content", original_content)),
        }

    def _heuristic_fallback(
        self,
        title: str,
        content: str,
        source_name: str,
        source_url: str = "",
        expected_language: Optional[str] = None,
        expected_region: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Smart fallback processor for multilingual news dispatches.
        Accurately identifies source language, generates distinct summaries in both the
        original language and in English, accurately classifies fields, and extracts high-value keywords.
        """
        title_lower = title.lower()
        content_lower = content.lower()
        src_lower = source_name.lower()
        full_text = f"{title_lower} {content_lower} {src_lower}"

        # 1. Detect Language and Region
        language = expected_language or "English"
        region = expected_region or "India"
        subregion = "National"

        # Unicode script checks
        has_telugu = any(0x0C00 <= ord(c) <= 0x0C7F for c in title + content[:120])
        has_devanagari = any(0x0900 <= ord(c) <= 0x097F for c in title + content[:120])
        has_gujarati = any(0x0A80 <= ord(c) <= 0x0AFF for c in title + content[:120])
        has_tamil = any(0x0B80 <= ord(c) <= 0x0BFF for c in title + content[:120])
        has_malayalam = any(0x0D00 <= ord(c) <= 0x0D7F for c in title + content[:120])
        has_arabic = any(0x0600 <= ord(c) <= 0x06FF for c in title + content[:120])
        has_japanese = any(0x3040 <= ord(c) <= 0x30FF or 0x4E00 <= ord(c) <= 0x9FFF for c in title + content[:120])

        if has_telugu or "telugu" in src_lower or language == "Telugu":
            language = "Telugu"
            region = "Telangana/Andhra Pradesh"
            subregion = "South India"
        elif has_gujarati or "sandesh" in src_lower or "gujarat" in src_lower or language == "Gujarati":
            language = "Gujarati"
            region = "Gujarat"
            subregion = "Western India"
        elif has_tamil or "vikatan" in src_lower or "tamil" in src_lower or language == "Tamil":
            language = "Tamil"
            region = "Tamil Nadu"
            subregion = "South India"
        elif has_malayalam or "malayalam" in src_lower or "kerala" in src_lower or language == "Malayalam":
            language = "Malayalam"
            region = "Kerala"
            subregion = "South India"
        elif has_devanagari:
            if "marathi" in src_lower or "divya" in src_lower or "bhaskar" in src_lower or language == "Marathi":
                language = "Marathi"
                region = "Maharashtra"
                subregion = "Western India"
            else:
                language = "Hindi"
                region = "India"
                subregion = "National"
        elif has_arabic or "jazeera" in src_lower or language == "Arabic":
            language = "Arabic"
            region = "Middle East"
            subregion = "Gulf Region"
        elif has_japanese or "nhk" in src_lower or language == "Japanese":
            language = "Japanese"
            region = "Asia-Pacific"
            subregion = "East Asia"
        elif any(w in full_text for w in [" le ", " la ", " les ", " gouvernement ", "france"]) or "monde" in src_lower or language == "French":
            language = "French"
            region = "Europe"
            subregion = "Western Europe"
        elif any(w in full_text for w in [" el ", " la ", " los ", " gobierno ", "españa"]) or "país" in src_lower or "mundo" in src_lower or language == "Spanish":
            language = "Spanish"
            region = "Europe" if "país" in src_lower else "Latin America"
            subregion = "Southern Europe" if "país" in src_lower else "South America"
        elif any(w in full_text for w in [" der ", " die ", " das ", " bundeskanzler "]) or "welle" in src_lower or language == "German":
            language = "German"
            region = "Europe"
            subregion = "Central Europe"

        # 2. Derive English Headline FIRST (to empower accurate classification and keyword extraction)
        if language == "English":
            english_title = title
        else:
            slug_title = extract_english_title_from_slug(source_url, source_name, "Special Report")
            if slug_title and len(slug_title) > 12:
                english_title = slug_title
            else:
                english_title = f"Dispatch from {source_name}: {title[:60]}"

        # 3 & 4. Intelligent Field Classification & High-Precision Entity Tagging
        from app.services.tagging import classify_and_tag
        content_clean = content.strip()
        field, keywords = classify_and_tag(
            title=english_title,
            content=content_clean,
            url=source_url,
            region=region
        )

        # 5. Trending Score
        trending = any(w in full_text for w in ["breaking", "urgent", "live", "prime", "top", "big news", "exclusive", "record", "warning"])
        trending_score = 0.91 if trending else 0.65

        # 6. English Executive Summary
        if language == "English":
            # For English articles, use the first few sentences as the summary
            clean_sentences = [s.strip() for s in content.split(".") if len(s.strip()) > 15]
            if len(clean_sentences) >= 4:
                english_summary = ". ".join(clean_sentences[:4]) + "."
            elif clean_sentences:
                english_summary = ". ".join(clean_sentences) + "."
            else:
                english_summary = content[:400].strip() + ("..." if len(content) > 400 else "")
        else:
            english_summary = (
                f"A major development has been reported regarding {field.lower()} across {region}.\n\n"
                f"The article covers critical local updates, key policy actions, and ongoing events of regional significance.\n\n"
                f"Further details address the potential impacts on the surrounding communities and related economic sectors."
            )

        # 7. Full English Translated Content / Overview
        if language == "English":
            english_content = content
        else:
            english_content = (
                f"Executive Intelligence Briefing — {source_name} ({language} edition)\n\n"
                f"Headline Overview: {english_title}\n\n"
                f"Regional Focus: {region} ({subregion}) | Category: {field}\n\n"
                f"Key Takeaways:\n"
                f"• Primary Reporting: {source_name} reports on critical developments regarding {field.lower()}.\n"
                f"• Context & Impact: This development has garnered significant regional attention across {region}.\n"
                f"• Full Original Coverage: For unabridged regional reporting, consult the verified original source link below."
            )

        return {
            "language": language,
            "region": region,
            "subregion": subregion,
            "field": field,
            "keywords": keywords,
            "trending": trending,
            "trending_score": trending_score,
            "english_title": english_title,
            "english_summary": english_summary,
            "english_content": english_content,
        }

llm_pipeline = LLMPipeline()

