import json
import logging
import re
import urllib.parse
import html
import time
import threading
from typing import Dict, Any, Optional, List, Tuple, Generator
from bs4 import BeautifulSoup
import requests
from app.config import settings

logger = logging.getLogger(__name__)

# Strict JSON Schema enforced by Ollama's grammar-constrained sampler
NEWS_SUMMARY_SCHEMA = {
    "type": "object",
    "properties": {
        "english_title": {
            "type": "string",
            "description": "Clear, accurate, factual headline strictly in fluent English"
        },
        "english_summary": {
            "type": "string",
            "description": "Objective, factual English summary of approximately 80 to 120 words"
        },
        "field": {
            "type": "string",
            "description": "One of: Politics, States & Regional, Entertainment & Cinema, Agriculture & Rural, Education & Jobs, Technology & AI, Finance & Economics, Culture & Society, Health & Wellness, General News"
        },
        "region": {
            "type": "string",
            "description": "Geographical state or region (e.g. Maharashtra, Gujarat, Telangana/Andhra Pradesh, Tamil Nadu, Kerala, India, Europe, Asia-Pacific, Latin America, Middle East, Global)"
        },
        "subregion": {
            "type": "string",
            "description": "Specific subregion or city"
        },
        "keywords": {
            "type": "array",
            "items": {"type": "string"},
            "description": "3 to 5 key entity keywords or proper nouns"
        },
        "trending": {
            "type": "boolean",
            "description": "True if breaking news, high impact, or major announcement"
        },
        "trending_score": {
            "type": "number",
            "description": "Impact score between 0.0 and 1.0"
        }
    },
    "required": ["english_title", "english_summary"]
}

SYSTEM_PROMPT = """You are an elite multilingual intelligence analyst and executive news summarizer.
Your goal is to ingest foreign news articles, analyze the facts, and generate:
1. "english_title": An accurate, factual headline strictly in fluent English (Latin script).
2. "english_summary": A factual, cohesive English executive summary of approximately 80 to 120 words when sufficient source details exist.

CRITICAL OPERATIONAL RULES:
- Do NOT translate the full article text. Generate ONLY the English headline and summary.
- Strictly output in English (Latin alphabet). NEVER echo foreign scripts into the English fields.
- Strictly adhere to facts explicitly stated in the source. NEVER invent, extrapolate, or speculate.
- If an article is very brief, summarize all stated facts concisely without adding filler or imaginary details.
- Do NOT include editorial commentary, opinions, or mentions of the publisher/news outlet.
- You must strictly respond with valid JSON adhering to the provided schema."""

USER_PROMPT_TEMPLATE = """Source Publication: {source_name}
Detected Source Language: {language}
Original Headline: {title}

Article Text:
{content}

Generate the factual English headline and 80-120 word English summary adhering strictly to the schema."""

CHUNK_EXTRACT_PROMPT = """Analyze the following excerpt from a long news article in {language}.
Extract 3 to 5 key factual bullet points in English covering specific events, names, numbers, and decisions.
Do not invent facts."""

def clean_text(raw_html: str) -> str:
    """Thoroughly strip HTML tags and decode entities."""
    if not raw_html:
        return ""
    decoded = html.unescape(raw_html)
    soup = BeautifulSoup(decoded, "html.parser")
    for el in soup(["script", "style", "noscript", "iframe"]):
        el.decompose()
    text = soup.get_text(separator=" ", strip=True)
    text = re.sub(r'<[^>]+>', ' ', text)
    return " ".join(text.split())

def is_predominantly_english(text: str, min_ratio: float = 0.70) -> bool:
    """
    Check if the text is predominantly English/Latin characters, numbers, and standard punctuation.
    Prevents foreign script leakage or model hallucinations echoing non-English text.
    """
    if not text or not text.strip():
        return False
    # Strip spaces and standard punctuation
    cleaned = re.sub(r'[\s\d\.,!?;:\'\"–—\(\)\[\]\/\-_+@#\$%&*=<>`~]', '', text)
    if not cleaned:
        return True
    # Count basic Latin alphabet characters (a-z, A-Z) plus common accented Latin (é, à, etc.)
    latin_chars = sum(1 for c in cleaned if ('a' <= c <= 'z') or ('A' <= c <= 'Z') or (0x00C0 <= ord(c) <= 0x017F))
    ratio = latin_chars / len(cleaned)
    return ratio >= min_ratio

def detect_source_language(title: str, content: str, expected_language: Optional[str] = None) -> Tuple[str, str, str]:
    """
    Robust source language and regional bloc detector using Unicode block boundaries
    and lexical disambiguation markers for Indic scripts (Hindi vs Marathi).
    Returns (language, default_region, default_subregion).
    """
    sample = f"{title} {content[:400]}"
    
    # 1. Unicode Script Checks
    has_telugu = any(0x0C00 <= ord(c) <= 0x0C7F for c in sample)
    has_tamil = any(0x0B80 <= ord(c) <= 0x0BFF for c in sample)
    has_gujarati = any(0x0A80 <= ord(c) <= 0x0AFF for c in sample)
    has_malayalam = any(0x0D00 <= ord(c) <= 0x0D7F for c in sample)
    has_devanagari = any(0x0900 <= ord(c) <= 0x097F for c in sample)
    has_arabic = any(0x0600 <= ord(c) <= 0x06FF for c in sample)
    has_japanese = any(0x3040 <= ord(c) <= 0x30FF or 0x4E00 <= ord(c) <= 0x9FFF for c in sample)

    if has_telugu or expected_language == "Telugu":
        return "Telugu", "Telangana/Andhra Pradesh", "South India"
    if has_tamil or expected_language == "Tamil":
        return "Tamil", "Tamil Nadu", "South India"
    if has_gujarati or expected_language == "Gujarati":
        return "Gujarati", "Gujarat", "Western India"
    if has_malayalam or expected_language == "Malayalam":
        return "Malayalam", "Kerala", "South India"
    if has_devanagari:
        # Disambiguate Marathi vs Hindi using Marathi distinctive grammatical morphemes & vocabulary
        marathi_markers = {"आहे", "नाही", "झाले", "केले", "यांनी", "म्हणाले", "उपमुख्यमंत्री", "मुंबई", "पुणे", "ठाणे", "महाराष्ट्र", "तर्फे", "पोलीस", "येथे", "रोजी"}
        words = set(re.findall(r'[\u0900-\u097F]+', sample))
        is_marathi = bool(words & marathi_markers) or expected_language == "Marathi"
        if is_marathi:
            return "Marathi", "Maharashtra", "Western India"
        return "Hindi", "India", "National"
    if has_arabic or expected_language == "Arabic":
        return "Arabic", "Middle East", "Gulf Region"
    if has_japanese or expected_language == "Japanese":
        return "Japanese", "Asia-Pacific", "East Asia"

    # Latin-script European Languages
    sample_lower = f" {sample.lower()} "
    if expected_language == "French" or any(w in sample_lower for w in [" le ", " la ", " les ", " gouvernement ", "france", "paris"]):
        return "French", "Europe", "Western Europe"
    if expected_language == "Spanish" or any(w in sample_lower for w in [" el ", " la ", " los ", " gobierno ", "españa", "madrid"]):
        return "Spanish", "Europe", "Southern Europe"
    if expected_language == "German" or any(w in sample_lower for w in [" der ", " die ", " das ", " bundeskanzler ", "berlin", "deutschland"]):
        return "German", "Europe", "Central Europe"

    if expected_language:
        return expected_language, "Global", "International"

    return "English", "Global", "International"


class LLMPipeline:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip('/')
        self.model = settings.OLLAMA_MODEL
        self.num_ctx = getattr(settings, "OLLAMA_NUM_CTX", 4096)
        self.num_predict = getattr(settings, "OLLAMA_NUM_PREDICT", 400)
        self.temperature = getattr(settings, "OLLAMA_TEMPERATURE", 0.1)
        self.timeout = getattr(settings, "OLLAMA_TIMEOUT", 45.0)
        concurrency_limit = getattr(settings, "OLLAMA_CONCURRENCY_LIMIT", 1)
        self._semaphore = threading.Semaphore(concurrency_limit)

    def check_ollama_status(self) -> Dict[str, Any]:
        """Verify Ollama server connectivity and model availability."""
        try:
            res = requests.get(f"{self.base_url}/api/tags", timeout=3.0)
            if res.status_code != 200:
                return {
                    "available": False,
                    "error": "http_error",
                    "message": f"Ollama server returned HTTP {res.status_code} at {self.base_url}."
                }
            data = res.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            model_match = any(m == self.model or m.startswith(f"{self.model}:") for m in models)
            if not model_match:
                return {
                    "available": False,
                    "error": "model_not_found",
                    "message": f"Ollama model '{self.model}' is not installed at {self.base_url}. Please run 'ollama pull {self.model}'.",
                    "available_models": models
                }
            return {
                "available": True,
                "model": self.model,
                "available_models": models
            }
        except requests.exceptions.ConnectionError:
            return {
                "available": False,
                "error": "connection_refused",
                "message": f"Ollama server is not running or unreachable at {self.base_url}. Please start Ollama via 'ollama serve'."
            }
        except Exception as e:
            return {
                "available": False,
                "error": "unknown_error",
                "message": f"Unable to reach Ollama server at {self.base_url}: {str(e)}"
            }

    def process_article(
        self,
        title: str,
        content: str,
        source_name: str,
        source_url: str = "",
        expected_language: Optional[str] = None,
        expected_region: Optional[str] = None,
        article_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Process an ingested raw foreign article:
        Generates ONLY an accurate English headline and an English summary (approx 80-120 words).
        Does NOT translate the entire article.
        Tied explicitly to article_id with concurrency protection.
        """
        title_clean = clean_text(title)
        content_clean = clean_text(content)

        detected_lang, def_region, def_subregion = detect_source_language(
            title_clean, content_clean, expected_language
        )
        region = expected_region or def_region

        # Handle empty/unintelligible source
        if not title_clean and not content_clean:
            return {
                "article_id": article_id,
                "language": detected_lang,
                "region": region,
                "subregion": def_subregion,
                "field": "General News",
                "keywords": [],
                "trending": False,
                "trending_score": 0.5,
                "english_title": "Untitled Dispatch",
                "english_summary": "No content available in the original source dispatch to summarize.",
                "english_content": "No content available.",
                "processing_status": "failed",
                "processing_error": "Empty source text",
                "summary_word_count": 0
            }

        # Concurrency protection for local GPU inference
        with self._semaphore:
            try:
                result = self._generate_with_retry(
                    title=title_clean,
                    content=content_clean,
                    source_name=source_name,
                    language=detected_lang,
                    region=region,
                    subregion=def_subregion,
                    article_id=article_id
                )
                return result
            except Exception as e:
                logger.warning(f"Ollama inference notice for article {article_id or title_clean[:30]}: {e}. Activating smart fallback.")
                fallback = self._smart_fallback(
                    title=title_clean,
                    content=content_clean,
                    source_name=source_name,
                    source_url=source_url,
                    language=detected_lang,
                    region=region,
                    subregion=def_subregion,
                    article_id=article_id,
                    error_msg=str(e)
                )
                return fallback

    def _generate_with_retry(
        self,
        title: str,
        content: str,
        source_name: str,
        language: str,
        region: str,
        subregion: str,
        article_id: Optional[int] = None,
        max_retries: int = 2
    ) -> Dict[str, Any]:
        """
        Execute Ollama generation with bounded retries, chunking for long articles,
        and strict output validation.
        """
        # Long article context-aware hierarchical summarization
        processed_content = content
        word_count = len(content.split())
        if word_count > 2000:
            logger.info(f"Article is long ({word_count} words). Performing hierarchical chunk summarization.")
            processed_content = self._hierarchical_chunk_summary(content, language)

        prompt = USER_PROMPT_TEMPLATE.format(
            source_name=source_name,
            language=language,
            title=title,
            content=processed_content[:7000]
        )

        current_predict = self.num_predict
        last_error = None

        for attempt in range(max_retries + 1):
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                "format": NEWS_SUMMARY_SCHEMA,
                "stream": False,
                "options": {
                    "temperature": self.temperature,
                    "num_ctx": self.num_ctx,
                    "num_predict": current_predict
                }
            }

            try:
                res = requests.post(
                    f"{self.base_url}/api/chat",
                    json=payload,
                    timeout=self.timeout
                )
            except requests.exceptions.ConnectionError as ce:
                raise RuntimeError(f"Ollama server connection refused at {self.base_url}.") from ce
            except requests.exceptions.Timeout as te:
                last_error = f"Request timed out after {self.timeout}s"
                logger.warning(f"Attempt {attempt + 1}: {last_error}")
                time.sleep(1.0 * (attempt + 1))
                continue

            if res.status_code != 200:
                last_error = f"Ollama HTTP {res.status_code}: {res.text[:200]}"
                logger.warning(f"Attempt {attempt + 1}: {last_error}")
                time.sleep(1.0 * (attempt + 1))
                continue

            resp_json = res.json()
            done_reason = resp_json.get("done_reason")
            raw_text = resp_json.get("message", {}).get("content", "").strip()

            # Check for generation truncation
            if done_reason == "length":
                current_predict += 150
                last_error = "Response was truncated by token limit"
                logger.warning(f"Attempt {attempt + 1}: {last_error}. Increasing num_predict to {current_predict}.")
                time.sleep(0.5)
                continue

            if not raw_text:
                last_error = "Empty response from Ollama"
                logger.warning(f"Attempt {attempt + 1}: {last_error}")
                time.sleep(1.0)
                continue

            # Parse JSON
            try:
                data = json.loads(raw_text)
            except Exception as pe:
                last_error = f"JSON parse error: {pe}"
                logger.warning(f"Attempt {attempt + 1}: {last_error}")
                time.sleep(1.0)
                continue

            # Validate fields
            eng_title = str(data.get("english_title", "")).strip()
            eng_summary = str(data.get("english_summary", "")).strip()

            if not eng_title or len(eng_title) < 5:
                last_error = "Generated english_title is empty or too short"
                logger.warning(f"Attempt {attempt + 1}: {last_error}")
                time.sleep(1.0)
                continue

            if not eng_summary or len(eng_summary) < 30:
                last_error = "Generated english_summary is empty or too short"
                logger.warning(f"Attempt {attempt + 1}: {last_error}")
                time.sleep(1.0)
                continue

            # Script / Language validation: ensure output is truly in English (Latin alphabet)
            if not is_predominantly_english(eng_title) or not is_predominantly_english(eng_summary):
                last_error = "Output contains un-translated foreign script echoing source language"
                logger.warning(f"Attempt {attempt + 1}: {last_error}")
                time.sleep(1.0)
                continue

            # Successful valid generation!
            summary_words = len(eng_summary.split())
            field = str(data.get("field", "General News")).strip()
            keywords = [str(k).strip() for k in data.get("keywords", []) if str(k).strip()][:5]
            if not keywords:
                from app.services.tagging import classify_and_tag
                _, keywords = classify_and_tag(eng_title, eng_summary, "", region)

            trending = bool(data.get("trending", False))
            trending_score = float(data.get("trending_score", 0.65 if trending else 0.5))

            # Flag if summary is unexpectedly sparse for a rich article
            status = "completed"
            error_note = None
            if word_count > 100 and summary_words < 35:
                status = "flagged"
                error_note = f"Summary is brief ({summary_words} words). Flagged for review."

            return {
                "article_id": article_id,
                "language": language,
                "region": str(data.get("region", region)),
                "subregion": str(data.get("subregion", subregion)),
                "field": field,
                "keywords": keywords,
                "trending": trending,
                "trending_score": trending_score,
                "english_title": eng_title,
                "english_summary": eng_summary,
                "english_content": eng_summary, # Strictly headline and summary, no full-article translation!
                "processing_status": status,
                "processing_error": error_note,
                "summary_word_count": summary_words
            }

        # If all retries exhausted, raise to trigger smart fallback
        raise RuntimeError(f"Ollama generation failed after {max_retries + 1} attempts: {last_error}")

    def _hierarchical_chunk_summary(self, text: str, language: str) -> str:
        """
        Divide long text into sections, extract key factual points from each,
        and combine them for final synthesis.
        """
        paragraphs = [p.strip() for p in text.split("\n") if len(p.strip()) > 30]
        if not paragraphs:
            paragraphs = [text[i:i+3000] for i in range(0, len(text), 3000)]

        chunks = []
        current_chunk = []
        current_len = 0
        for p in paragraphs:
            current_chunk.append(p)
            current_len += len(p)
            if current_len >= 3000:
                chunks.append("\n".join(current_chunk))
                current_chunk = []
                current_len = 0
        if current_chunk:
            chunks.append("\n".join(current_chunk))

        extracted_points = []
        for i, chunk in enumerate(chunks[:4]): # Max 4 chunks
            try:
                res = requests.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": [
                            {"role": "system", "content": CHUNK_EXTRACT_PROMPT.format(language=language)},
                            {"role": "user", "content": chunk[:3000]}
                        ],
                        "stream": False,
                        "options": {
                            "temperature": 0.1,
                            "num_predict": 180,
                            "num_ctx": self.num_ctx
                        }
                    },
                    timeout=25.0
                )
                if res.status_code == 200:
                    pts = res.json().get("message", {}).get("content", "").strip()
                    if pts:
                        extracted_points.append(pts)
            except Exception as e:
                logger.warning(f"Chunk {i+1} extraction notice: {e}")

        if extracted_points:
            return "\n---\n".join(extracted_points)
        return text[:4500]

    def _smart_fallback(
        self,
        title: str,
        content: str,
        source_name: str,
        source_url: str,
        language: str,
        region: str,
        subregion: str,
        article_id: Optional[int] = None,
        error_msg: str = ""
    ) -> Dict[str, Any]:
        """
        Failsafe fallback when Ollama is unavailable or retries failed.
        Extracts clean metadata and marks the article as 'failed' or 'flagged' for review.
        """
        from app.services.tagging import classify_and_tag

        english_title = title
        if not is_predominantly_english(title):
            slug_title = self._derive_title_from_slug(source_url)
            if slug_title and len(slug_title) > 10:
                english_title = slug_title
            else:
                english_title = f"{source_name}: {title[:75]}"

        field, keywords = classify_and_tag(
            title=english_title,
            content=content,
            url=source_url,
            region=region
        )

        # Build informative factual overview instead of fake filler
        is_conn_or_timeout = any(kw in error_msg.lower() for kw in ["connection refused", "timeout", "timed out", "retries failed", "offline", "unavailable"])
        status = "failed" if is_conn_or_timeout else "flagged"

        if language == "English":
            sentences = [s.strip() for s in content.split(".") if len(s.strip()) > 15]
            if sentences:
                english_summary = ". ".join(sentences[:3]) + "."
            else:
                english_summary = content[:250].strip() + ("..." if len(content) > 250 else "")
        else:
            english_summary = (
                f"Dispatch from {source_name} reported in {language}.\n\n"
                f"Headline: {english_title}.\n\n"
                f"The AI summary is currently queued for local model processing. Consult the original source link for complete reporting."
            )

        return {
            "article_id": article_id,
            "language": language,
            "region": region,
            "subregion": subregion,
            "field": field,
            "keywords": keywords,
            "trending": False,
            "trending_score": 0.5,
            "english_title": english_title,
            "english_summary": english_summary,
            "english_content": english_summary,
            "processing_status": status,
            "processing_error": error_msg or "Ollama processing unavailable",
            "summary_word_count": len(english_summary.split())
        }

    def _derive_title_from_slug(self, url: str) -> Optional[str]:
        """Derive a natural English headline from publication URL slugs."""
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
                acronyms = {"ai", "bjp", "aap", "tmc", "mp", "mla", "ec", "neet", "pg", "air", "dps", "afmc", 
                            "btsc", "fso", "ignou", "upi", "eu", "ecb", "cjp", "kft", "ckd", "egfr", "gmc", "jem"}
                formatted_words = []
                for w in words:
                    w_lower = w.lower()
                    if w_lower in acronyms:
                        formatted_words.append(w_lower.upper())
                    else:
                        formatted_words.append(w.capitalize())
                return " ".join(formatted_words)[:95]
        except Exception:
            pass
        return None

    def stream_ollama(self, prompt: str, system_prompt: str = SYSTEM_PROMPT) -> Generator[str, None, None]:
        """Streaming response generator via local Ollama API."""
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "stream": True,
            "options": {
                "temperature": self.temperature,
                "num_ctx": self.num_ctx
            }
        }
        res = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            stream=True,
            timeout=self.timeout
        )
        res.raise_for_status()
        for line in res.iter_lines():
            if line:
                chunk = json.loads(line.decode("utf-8"))
                content = chunk.get("message", {}).get("content", "")
                if content:
                    yield content

llm_pipeline = LLMPipeline()
