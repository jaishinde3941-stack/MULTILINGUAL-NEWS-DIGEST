"""
Tagging & Taxonomy Service: High-precision editorial categorization and concept extraction.
Produces 2 to 4 attractive, context-aware, concise English tags per article.
"""
import re
from typing import List, Tuple, Set

# Acronyms that should remain fully capitalized
SPECIAL_ACRONYMS = {
    "isro": "ISRO",
    "nasa": "NASA",
    "ai": "AI",
    "bjp": "BJP",
    "congress": "Congress",
    "aap": "AAP",
    "tmc": "TMC",
    "tdp": "TDP",
    "ysrcp": "YSRCP",
    "rbi": "RBI",
    "sebi": "SEBI",
    "sensex": "Sensex",
    "nifty": "Nifty",
    "neet": "NEET",
    "upsc": "UPSC",
    "drdo": "DRDO",
    "gmc": "GMC",
    "nhm": "NHM",
    "imd": "IMD",
    "ipl": "IPL",
    "bcci": "BCCI",
    "icc": "ICC",
    "who": "WHO",
    "un": "UN",
    "ec": "Election Commission",
}

GENERIC_STOP_WORDS: Set[str] = {
    "news", "latest", "update", "updates", "important", "breaking",
    "general", "article", "report", "reports", "today", "yesterday",
    "story", "stories", "top stories", "daily", "bulletin", "feed",
    "information", "details", "headline", "post", "dispatch"
}

CONCEPT_RULES: List[Tuple[str, str, str]] = [
    # (Regex pattern with strict word boundaries, Tag Name, Associated Field)
    # Space & Science
    (r"\bisro\b|\bchandrayaan\b|\bgaganyaan\b|\bsriharikota\b", "ISRO", "Technology & AI"),
    (r"\bsatellite launch\b|\blaunch vehicle\b|\bpslv\b|\bgslv\b|\bsslv\b|\brocket launch\b", "Satellite Launch", "Technology & AI"),
    (r"\bspace exploration\b|\bdeep space\b|\borbit insertion\b|\blunar mission\b", "Space Exploration", "Technology & AI"),
    (r"\bindian science\b|\bindigenous technology\b|\bspace research\b", "Indian Science", "Technology & AI"),
    (r"\bnasa\b|\bartemis\b|\bjames webb\b|\bspacex\b", "Space Exploration", "Technology & AI"),

    # Financial Markets & Economy
    (r"\bstock market\b|\bshare market\b|\bwall street\b|\bdalal street\b", "Stock Market", "Finance & Economics"),
    (r"\bsensex\b|\bbse index\b", "Sensex", "Finance & Economics"),
    (r"\bnifty\b|\bnifty 50\b|\bnse index\b", "Nifty", "Finance & Economics"),
    (r"\bmarket volatility\b|\bmarket crash\b|\bbear market\b|\bbull run\b|\bshares plunge\b|\bmarket rally\b", "Market Volatility", "Finance & Economics"),
    (r"\bfinancial markets\b|\bequity markets\b|\bmutual funds\b|\btrading session\b", "Financial Markets", "Finance & Economics"),
    (r"\breserve bank\b|\brbi\b|\brepo rate\b|\bmonetary policy\b", "Banking & RBI", "Finance & Economics"),
    (r"\binflation\b|\bcpi\b|\beconomic growth\b|\bgdp\b", "Macroeconomics", "Finance & Economics"),
    (r"\bgold rate\b|\bgold prices\b|\bbullion\b", "Gold Rate", "Finance & Economics"),
    (r"\bcommodity prices\b|\bprecious metals\b", "Commodities Market", "Finance & Economics"),

    # Weather & Climate
    (r"\bheavy rain\b|\bheavy rainfall\b|\btorrential downpour\b|\bwaterlogging\b|\bcloudburst\b", "Heavy Rainfall", "States & Regional"),
    (r"\bweather alert\b|\bred alert\b|\borange alert\b|\bcyclone alert\b", "Weather Alert", "States & Regional"),
    (r"\bchennai rain\b|\bchennai weather\b|\bmeenambakkam\b", "Chennai Weather", "States & Regional"),
    (r"\bmumbai rain\b|\bmumbai weather\b|\bcolaba rain\b", "Mumbai Weather", "States & Regional"),
    (r"\btamil nadu weather\b|\bcoastal tamil nadu\b", "Tamil Nadu", "States & Regional"),
    (r"\bmonsoon\b|\bsouthwest monsoon\b|\bnortheast monsoon\b|\bcyclone\b", "Monsoon & Climate", "States & Regional"),
    (r"\bheatwave\b|\bdrought\b", "Climate Alert", "States & Regional"),

    # Elections & Politics
    (r"\belection commission\b|\bassembly polls\b|\blok sabha\b|\bvoter turnout\b|\bpolling booth\b|\belection\b|\belections\b", "Elections", "Politics"),
    (r"\bpolitical developments\b|\bcoalition\b|\bfloor test\b|\bpolitical crisis\b|\bcabinet reshuffle\b", "Political Developments", "Politics"),
    (r"\bsupreme court\b|\bhigh court\b|\bverdict\b|\bbench\b|\bcji\b|\bconstitution bench\b|\bjudiciary\b", "Supreme Court", "Politics"),
    (r"\bdeepfake\b|\bdeepfakes\b|\bmisinformation\b", "Deepfake Regulation", "Technology & AI"),
    (r"\bycp\b|\bjagan\b|\bysrcp\b", "YSRCP", "Politics"),
    (r"\bchandrababu\b|\btdp\b", "TDP", "Politics"),
    (r"\bmahua moitra\b|\btrinamool\b|\btmc\b", "TMC", "Politics"),
    (r"\baap\b|\baam aadmi party\b|\barvind kejriwal\b", "Aam Aadmi Party", "Politics"),
    (r"\bbjp\b|\bbharatiya janata party\b|\bnda\b", "BJP", "Politics"),
    (r"\bcongress party\b|\brahul gandhi\b|\bmallikarjun kharge\b", "Congress Party", "Politics"),
    (r"\bakhilesh yadav\b|\bsamajwadi party\b", "Akhilesh Yadav", "Politics"),
    (r"\bthalapathy vijay\b|\btamizhaga vettri kazhagam\b", "Tamil Nadu Politics", "Politics"),
    (r"\bkerala politics\b|\bldf\b|\budf\b|\bpinarayi\b", "Kerala Politics", "States & Regional"),
    (r"\bmaharashtra politics\b|\bmahayuti\b|\bmaha vikas aghadi\b", "Maharashtra Politics", "States & Regional"),
    (r"\bcounter-terrorism\b|\bmasood azhar\b|\binfiltrator\b", "Counter-Terrorism", "Politics"),
    (r"\bforeign policy\b|\bdiplomatic ties\b|\bbilateral summit\b", "Foreign Policy", "Politics"),

    # Technology & AI
    (r"\bartificial intelligence\b|\bai\b|\bgenerative ai\b|\bllm\b|\bmachine learning\b", "Artificial Intelligence", "Technology & AI"),
    (r"\btraffic cameras\b|\bai surveillance\b|\bsmart camera\b|\bchallan controversy\b", "Smart Infrastructure", "Technology & AI"),
    (r"\bcyber security\b|\bransomware\b|\bdata breach\b|\bcyber attack\b", "Cybersecurity", "Technology & AI"),
    (r"\bsemiconductor\b|\bchip manufacturing\b|\bfab plant\b", "Semiconductors", "Technology & AI"),

    # Sports
    (r"\bcricket\b|\bipl\b|\btest match\b|\bbcci\b|\brohit sharma\b|\bvirat kohli\b", "Cricket", "Sports"),
    (r"\bchampions trophy\b|\bworld cup\b|\btournament\b", "Sports Championship", "Sports"),
    (r"\bfootball\b|\bfifa\b|\bpremier league\b|\bchampions league\b", "Football", "Sports"),
    (r"\bolympics\b|\bathletics\b|\bbadminton\b|\btennis\b", "Athletics", "Sports"),

    # Health & Wellness
    (r"\bkidney test\b|\bkft report\b|\bserum creatinine\b|\begfr\b|\bckd signs\b", "Kidney Health", "Health & Wellness"),
    (r"\bcreatinine\b|\bdiagnostic test\b|\bblood report\b", "Medical Diagnostics", "Health & Wellness"),
    (r"\bskincare\b|\baloe vera\b|\bglowing skin\b|\bface pack\b", "Skincare", "Health & Wellness"),
    (r"\bmental health\b|\bdepression\b|\btherapy\b|\bwellness\b", "Mental Health", "Health & Wellness"),
    (r"\bcardiac health\b|\bheart disease\b|\bcardiology\b", "Cardiology", "Health & Wellness"),
    (r"\bfirst aid\b|\bemergency care\b|\bbee sting\b", "Emergency Care", "Health & Wellness"),

    # Education & Careers
    (r"\bneet pg\b|\bmedical entrance\b|\baiims\b|\bafmc\b", "NEET PG", "Education & Jobs"),
    (r"\bupsc\b|\bcivil services\b|\bias officer\b|\bips officer\b", "Civil Services", "Education & Jobs"),
    (r"\brecruitment\b|\bjob vacancy\b|\bhiring notification\b|\bbtsc\b", "Government Recruitment", "Education & Jobs"),
    (r"\bstudy abroad\b|\bforeign universities\b|\bscholarship\b", "Higher Education", "Education & Jobs"),
    (r"\bdrdo internship\b|\bengineering students\b|\binternship\b", "STEM Careers", "Education & Jobs"),

    # Agriculture & Rural
    (r"\bfarmer suicide\b|\bdebt burden\b|\bcrop loss\b|\bagrarian\b", "Agrarian Crisis", "Agriculture & Rural"),
    (r"\bcrop cultivation\b|\bhorticulture\b|\bvegetable farming\b|\bseeds\b", "Crop Cultivation", "Agriculture & Rural"),
    (r"\bdairy farming\b|\bgir cow\b|\bindigenous cattle\b", "Dairy Farming", "Agriculture & Rural"),

    # Entertainment & Cinema
    (r"\bbox office\b|\badvance booking\b|\btheatrical release\b", "Box Office", "Entertainment & Cinema"),
    (r"\bdrishyam\b|\bmohanlal\b|\bjeethu joseph\b", "Cinema News", "Entertainment & Cinema"),
    (r"\btollywood\b|\btelugu cinema\b|\bss rajamouli\b", "Tollywood", "Entertainment & Cinema"),
    (r"\bkollywood\b|\btamil cinema\b|\bactor surya\b|\btrisha\b", "Kollywood", "Entertainment & Cinema"),
    (r"\bbollywood\b|\bhindi cinema\b|\blata mangeshkar\b", "Bollywood", "Entertainment & Cinema"),

    # Public Safety & Regional Incidents
    (r"\bhit and run\b|\bcar accident\b|\bfatal crash\b|\broad accident\b", "Road Safety", "States & Regional"),
    (r"\bdrowning incident\b|\btemple pool\b|\brescue operation\b", "Public Safety", "States & Regional"),
    (r"\bjewellery theft\b|\bburglary\b|\bpolice arrest\b", "Law & Order", "States & Regional"),
    (r"\bfire breakout\b|\bblaze\b|\bfirefighters\b", "Emergency Services", "States & Regional"),
]

def format_word_part(part: str) -> str:
    pl = part.lower()
    if pl in SPECIAL_ACRONYMS:
        return SPECIAL_ACRONYMS[pl]
    if len(pl) > 1 and part.isupper():
        return part
    return part.capitalize()

def format_tag_casing(tag: str) -> str:
    """Format tag into Title Case while preserving recognized acronyms, slashes, and hyphens."""
    words = tag.strip().split()
    formatted = []
    for w in words:
        if "/" in w:
            formatted.append("/".join(format_word_part(sub) for sub in w.split("/")))
        elif "-" in w:
            formatted.append("-".join(format_word_part(sub) for sub in w.split("-")))
        else:
            formatted.append(format_word_part(w))
    return " ".join(formatted)

def clean_and_normalize_tag(raw: str) -> str:
    """Strip hashtags, special characters, and extra spaces from a tag."""
    cleaned = re.sub(r'^[#@\*\-_]+', '', raw)
    cleaned = re.sub(r'[^\w\s\-/&]', '', cleaned)
    cleaned = " ".join(cleaned.split())
    if not cleaned:
        return ""
    return format_tag_casing(cleaned)

def is_valid_tag(tag: str) -> bool:
    """Validate that tag is meaningful, concise (1-3 words), and non-generic."""
    if not tag or len(tag) < 2 or len(tag) > 35:
        return False
    words = tag.split()
    if len(words) > 4:
        return False
    if tag.lower() in GENERIC_STOP_WORDS:
        return False
    if len(words) == 1 and words[0].lower() in GENERIC_STOP_WORDS:
        return False
    return True

def classify_and_tag(title: str, content: str = "", url: str = "", region: str = "") -> Tuple[str, List[str]]:
    """
    Intelligently deduce editorial field and generate 2 to 4 high-precision,
    context-aware English tags for any news article.
    """
    combined = f"{title.lower()} {content.lower()[:600]} {url.lower()}"
    matched_tags: List[str] = []
    field_votes = {}

    for pattern, tag, field in CONCEPT_RULES:
        if re.search(pattern, combined, re.IGNORECASE):
            clean_tag = format_tag_casing(tag)
            if clean_tag not in matched_tags and is_valid_tag(clean_tag):
                matched_tags.append(clean_tag)
            field_votes[field] = field_votes.get(field, 0) + 1

    # Determine dominant field
    if field_votes:
        best_field = max(field_votes.items(), key=lambda x: x[1])[0]
    else:
        best_field = "States & Regional"

    # If few specific matches found, derive contextual tags from region
    if len(matched_tags) < 2 and region and region.lower() != "global":
        region_tag = format_tag_casing(region)
        if region_tag not in matched_tags and is_valid_tag(region_tag):
            matched_tags.append(region_tag)

    if len(matched_tags) < 2 and best_field and best_field not in matched_tags:
        field_tag = format_tag_casing(best_field)
        if is_valid_tag(field_tag):
            matched_tags.append(field_tag)

    # Final cleanup: deduplicate and guarantee 2 to 4 tags
    final_tags: List[str] = []
    seen: Set[str] = set()
    for t in matched_tags:
        cleaned = clean_and_normalize_tag(t)
        tl = cleaned.lower()
        if cleaned and is_valid_tag(cleaned) and tl not in seen:
            final_tags.append(cleaned)
            seen.add(tl)
        if len(final_tags) >= 4:
            break

    # Guarantee at least 2 context-aware tags
    if len(final_tags) < 2:
        if best_field == "Technology & AI":
            final_tags.extend([t for t in ["Technology", "Innovation"] if t.lower() not in seen])
        elif best_field == "Finance & Economics":
            final_tags.extend([t for t in ["Financial Markets", "Economy"] if t.lower() not in seen])
        elif best_field == "Politics":
            final_tags.extend([t for t in ["Politics", "Governance"] if t.lower() not in seen])
        elif best_field == "Sports":
            final_tags.extend([t for t in ["Sports", "Athletics"] if t.lower() not in seen])
        else:
            final_tags.extend([t for t in ["Regional Affairs", "Public Policy"] if t.lower() not in seen])

    return best_field, final_tags[:4]
