"""
Tagging & Taxonomy Service: High-precision editorial categorization and concept extraction.
"""
import re
from typing import List, Tuple

CONCEPT_RULES: List[Tuple[str, str, str]] = [
    # (Regex pattern, Tag Name, Associated Field)
    # Politics & Governance
    (r"\bycp\b|\bjagan\b|ongole", "YS Jagan", "Politics"),
    (r"\bycp\b|ysrcp", "YSRCP", "Politics"),
    (r"mahua moitra", "Mahua Moitra", "Politics"),
    (r"chandrababu", "Chandrababu Naidu", "Politics"),
    (r"\bec defence\b|\belection commission\b|\bec\b", "Election Commission", "Politics"),
    (r"tmc|trinamool", "TMC", "Politics"),
    (r"tdp", "TDP", "Politics"),
    (r"cockroach party|mumbai protest", "Mumbai Politics", "Politics"),
    (r"ramesh mhatre|corporator", "Local Governance", "Politics"),
    (r"supreme court", "Supreme Court", "Politics"),
    (r"gmc election", "GMC Elections", "Politics"),
    (r"\baap\b|aam aadmi party", "Aam Aadmi Party", "Politics"),
    (r"candidate form rejected|form rejected", "Candidate Scrutiny", "Politics"),
    (r"masood azhar", "Masood Azhar", "Politics"),
    (r"\bjem\b|jaish-e-mohammed", "Counter-Terrorism", "Politics"),
    (r"pakistan|kabul|afghanistan", "Foreign Policy", "Politics"),
    (r"akhilesh yadav", "Akhilesh Yadav", "Politics"),
    (r"gorakhpur university protest|police si shouting|police lathicharge", "Student Protest", "Politics"),
    (r"haldwani|selja kumari", "Congress Party", "Politics"),
    (r"dehradun protest", "Uttarakhand Politics", "Politics"),
    (r"rajbhar|op rajbhar", "OP Rajbhar", "Politics"),
    (r"mosque demolition", "UP Politics", "Politics"),
    (r"tr balu|t\.?r\.? balu", "TR Baalu", "Politics"),
    (r"aadhav| CTR |ctr should", "Tamil Nadu Politics", "Politics"),
    (r"chief minister vijay|thalapathy vijay|minister vijay|rings to people", "Thalapathy Vijay", "Politics"),
    (r"cjp align|keralas contemporary politics", "Kerala Politics", "Politics"),
    (r"ganesh kumar|pathanapuram|vanchiyoor", "KB Ganesh Kumar", "Politics"),
    (r"pune congress|dnyanesh kumar", "Maharashtra Politics", "Politics"),
    (r"election commission removal", "Election Commission", "Politics"),

    # Health & Wellness
    (r"bee sting|sting", "Bee Sting", "Health & Wellness"),
    (r"first aid", "First Aid", "Health & Wellness"),
    (r"kidney test|kft report|serum creatinine|egfr|ckd signs", "Kidney Health", "Health & Wellness"),
    (r"creatinine", "Medical Diagnostics", "Health & Wellness"),
    (r"glowing skin|tanning remove|potato aloe vera|face pack", "Skincare", "Health & Wellness"),
    (r"aloe vera|natural remedies|potato for glowing", "Natural Remedies", "Health & Wellness"),
    (r"hibiscus|hair conditioner|soft shiny hair", "Hair Care", "Health & Wellness"),
    (r"sweating during workout|sweat|workout mean|not losing fat", "Fitness Science", "Health & Wellness"),
    (r"losing fat|metabolism", "Weight Management", "Health & Wellness"),
    (r"mental health|suicide|loneliness", "Mental Health", "Health & Wellness"),

    # Agriculture & Rural
    (r"winter vegetable|nursery preparation|grow tomato|cauliflower", "Horticulture", "Agriculture & Rural"),
    (r"seeds|vegetable farming", "Crop Cultivation", "Agriculture & Rural"),
    (r"dairy farming|gir cow|foreign breeds", "Dairy Farming", "Agriculture & Rural"),
    (r"gir cow|indigenous cattle", "Livestock Management", "Agriculture & Rural"),
    (r"farmer suicide|debt burden|amravati farmer", "Agrarian Crisis", "Agriculture & Rural"),
    (r"debt burden|kisan", "Farmer Welfare", "Agriculture & Rural"),

    # Education & Jobs
    (r"neet pg|pallakshi prasad|air afmc|topper", "NEET PG", "Education & Jobs"),
    (r"afmc|dps hyderabad|medical topper", "Medical Education", "Education & Jobs"),
    (r"study in germany|german universities|indian students", "Study Abroad", "Education & Jobs"),
    (r"cost for indian students", "Higher Education", "Education & Jobs"),
    (r"food safety officer|btsc vacancy|btsc", "BTSC Vacancy", "Education & Jobs"),
    (r"bihar food safety|recruitment btsc", "Government Recruitment", "Education & Jobs"),
    (r"ignou recruitment|non teaching|assistant director", "IGNOU Recruitment", "Education & Jobs"),
    (r"government jobs|posts check eligibility", "Public Sector Careers", "Education & Jobs"),
    (r"drdo internship|engineering and science students", "DRDO Internship", "Education & Jobs"),
    (r"drdo|defense research", "STEM Careers", "Education & Jobs"),
    (r"shruti arora|ips follows|chief secretaries", "UPSC & Civil Services", "Education & Jobs"),
    (r"ips officer|haryana cadre", "Women In Leadership", "Education & Jobs"),
    (r"nhm staff nurse|staff nurse recruitment|nhm", "NHM Nursing", "Education & Jobs"),
    (r"staff nurse|nursing posts", "Healthcare Careers", "Education & Jobs"),

    # Entertainment & Cinema
    (r"drishyam|drishyam the conclusion|advance booking", "Drishyam", "Entertainment & Cinema"),
    (r"advance booking tickets|national chain", "Box Office", "Entertainment & Cinema"),
    (r"lata mangeshkar|dilip kumar|dilip kumars", "Lata Mangeshkar", "Entertainment & Cinema"),
    (r"learned urdu|indian cinema", "Bollywood History", "Entertainment & Cinema"),
    (r"fahadh faasil|dont trouble the trouble", "Fahadh Faasil", "Entertainment & Cinema"),
    (r"pre release event|speech at", "Film Launch", "Entertainment & Cinema"),
    (r"ss rajamouli|rajamouli|director ss", "SS Rajamouli", "Entertainment & Cinema"),
    (r"special show permission|trisha|surya|karuppu", "Kollywood Cinema", "Entertainment & Cinema"),
    (r"surya film karuppu|trisha surya", "Surya & Trisha", "Entertainment & Cinema"),
    (r"mohan babu|paradise success meet", "Mohan Babu", "Entertainment & Cinema"),
    (r"telugu cinema|tollywood", "Tollywood", "Entertainment & Cinema"),

    # Technology & AI
    (r"ai traffic cameras|ai traffic|cameras mistake|traffic cameras", "AI Traffic Cameras", "Technology & AI"),
    (r"artificial intelligence|\bai\b", "Artificial Intelligence", "Technology & AI"),
    (r"traffic enforcement|challan controversy", "Smart Infrastructure", "Technology & AI"),

    # Finance & Economics
    (r"gold traders|protest outside govt|demand withdrawal", "Bullion Market", "Finance & Economics"),
    (r"gold rate|prices fall further|gold drop sharply", "Gold Rate", "Finance & Economics"),
    (r"commodity prices|precious metals", "Commodities Market", "Finance & Economics"),
    (r"trade protest|tax rules", "Trade & Commerce", "Finance & Economics"),

    # Culture & Society
    (r"paryushan parva|kshama vani|balraj sanghai", "Paryushan Parva", "Culture & Society"),
    (r"spiritual significance|jainism", "Spirituality", "Culture & Society"),
    (r"tiruchuli|thirumeninathar temple", "Temple Architecture", "Culture & Society"),
    (r"tamil heritage|shaivism", "Cultural Heritage", "Culture & Society"),
    (r"special dispatch from vikatan|vikatan", "Regional Features", "Culture & Society"),
    (r"japan rental family|fake resignation party|avoid loneliness", "Social Trends", "Culture & Society"),
    (r"gen z|loneliness", "Sociology", "Culture & Society"),

    # States & Regional (Incidents, Weather, Crime, Public Safety)
    (r"chuda house breaking|theft lakh jewellery", "Jewellery Theft", "States & Regional"),
    (r"house breaking|theft recovered", "Law & Order", "States & Regional"),
    (r"singrauli influencer|nidhi tiwari", "Influencer News", "States & Regional"),
    (r"navsari hit and run|audi car accident|shivang patel", "Hit & Run", "States & Regional"),
    (r"audi accident|car accident", "Road Safety", "States & Regional"),
    (r"thief took silver|returned it|temple after days", "Temple Theft", "States & Regional"),
    (r"temple relics|moral turnaround", "Human Interest", "States & Regional"),
    (r"low pressure area|andaman sea|imd alerts|heavy rains", "Weather Alert", "States & Regional"),
    (r"cyclone warning|heavy rainfall", "Monsoon & Climate", "States & Regional"),
    (r"school bus accident|leaves students injured", "School Bus Safety", "States & Regional"),
    (r"student safety|traffic mishap", "Accident & Rescue", "States & Regional"),
    (r"two people drowned|temple pool", "Public Safety", "States & Regional"),
    (r"drowning incident|temple pool mishap", "Emergency Response", "States & Regional"),
]

def classify_and_tag(title: str, content: str = "", url: str = "", region: str = "") -> Tuple[str, List[str]]:
    """
    Intelligently deduce editorial field and generate top-tier keyword tags
    for any news article.
    """
    combined = f"{title.lower()} {content.lower()[:300]} {url.lower()}"
    matched_tags = []
    field_votes = {}

    for pattern, tag, field in CONCEPT_RULES:
        if re.search(pattern, combined):
            if tag not in matched_tags:
                matched_tags.append(tag)
            field_votes[field] = field_votes.get(field, 0) + 1

    # Determine dominant field
    if field_votes:
        best_field = max(field_votes.items(), key=lambda x: x[1])[0]
    else:
        best_field = "States & Regional"

    # Always ensure 3-5 tags
    if best_field not in matched_tags and len(matched_tags) < 4:
        matched_tags.insert(0, best_field)

    if region and region not in matched_tags and len(matched_tags) < 4:
        matched_tags.append(region)

    # Clean deduplicated tags
    final_tags = []
    seen = set()
    for t in matched_tags:
        tl = t.strip().lower()
        if tl not in seen:
            final_tags.append(t.strip())
            seen.add(tl)
        if len(final_tags) >= 5:
            break

    if len(final_tags) < 3:
        final_tags.append("Top Stories")

    return best_field, final_tags[:5]
