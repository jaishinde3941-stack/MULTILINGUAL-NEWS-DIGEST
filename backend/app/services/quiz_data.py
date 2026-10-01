from typing import List
from app.schemas.quiz import QuizQuestion, QuizOption, QuizListResponse

ONBOARDING_QUESTIONS: List[QuizQuestion] = [
    # --- DIMENSION 1: GEOGRAPHIC & REGIONAL PRIORITIES (Q1-Q5) ---
    QuizQuestion(
        id=1,
        dimension="region",
        title="What is your primary regional focus?",
        subtitle="Select the geographic area whose developments impact you most.",
        is_multi_select=False,
        options=[
            QuizOption(
                id="q1_west",
                label="Western India (Maharashtra & Gujarat)",
                description="Mumbai commercial hub, Ahmedabad industrial corridor, state governance",
                icon="landmark",
                weight_map={"region:Maharashtra": 1.0, "region:Gujarat": 1.0, "lang:Marathi": 0.8, "lang:Gujarati": 0.8}
            ),
            QuizOption(
                id="q1_south",
                label="South India (Tamil Nadu, Kerala, Andhra Pradesh/Telangana)",
                description="Southern political dynamics, tech corridors, cinema & agriculture",
                icon="compass",
                weight_map={"region:Tamil Nadu": 1.0, "region:Kerala": 1.0, "region:Telangana/Andhra Pradesh": 1.0, "lang:Tamil": 0.8, "lang:Malayalam": 0.8, "lang:Telugu": 0.8}
            ),
            QuizOption(
                id="q1_national",
                label="National & Pan-India Politics",
                description="Union governance, central exams, policy decisions, national security",
                icon="globe",
                weight_map={"region:India": 1.0, "lang:Hindi": 0.9}
            ),
            QuizOption(
                id="q1_global",
                label="International & Cross-Border Affairs",
                description="Foreign policy, international developments, global trade & geopolitics",
                icon="map-pin",
                weight_map={"region:India": 0.5, "tag:foreign policy": 1.0, "tag:counter-terrorism": 1.0}
            ),
        ]
    ),
    QuizQuestion(
        id=2,
        dimension="region",
        title="Which state administration matters most to you?",
        subtitle="Follow local policy, state assemblies, and regional governance.",
        is_multi_select=False,
        options=[
            QuizOption(
                id="q2_gujarat",
                label="Gujarat",
                description="Sandesh dispatches, civic elections, rural & infrastructure growth",
                icon="shield",
                weight_map={"region:Gujarat": 1.0, "lang:Gujarati": 1.0}
            ),
            QuizOption(
                id="q2_maharashtra",
                label="Maharashtra",
                description="Divya Marathi dispatches, Mumbai corporator news, state politics",
                icon="layers",
                weight_map={"region:Maharashtra": 1.0, "lang:Marathi": 1.0}
            ),
            QuizOption(
                id="q2_tamil_nadu",
                label="Tamil Nadu",
                description="Vikatan dispatches, DMK/AIADMK/TVK politics, cultural heritage",
                icon="flag",
                weight_map={"region:Tamil Nadu": 1.0, "lang:Tamil": 1.0}
            ),
            QuizOption(
                id="q2_kerala",
                label="Kerala",
                description="Malayalam One India dispatches, LDF vs UDF politics, bullion markets",
                icon="anchor",
                weight_map={"region:Kerala": 1.0, "lang:Malayalam": 1.0}
            ),
            QuizOption(
                id="q2_telangana_ap",
                label="Telangana & Andhra Pradesh",
                description="Telugu One India dispatches, YSRCP/TDP politics, coastal weather",
                icon="navigation",
                weight_map={"region:Telangana/Andhra Pradesh": 1.0, "lang:Telugu": 1.0}
            ),
        ]
    ),
    QuizQuestion(
        id=3,
        dimension="region",
        title="What scale of local news coverage do you prefer?",
        subtitle="Determine whether you read state capital dispatches or grassroots reporting.",
        is_multi_select=False,
        options=[
            QuizOption(
                id="q3_metro",
                label="Major Urban Hubs & Metros",
                description="Mumbai, Chennai, Hyderabad, Thiruvananthapuram, Ahmedabad civic news",
                icon="building",
                weight_map={"field:Politics": 0.8, "field:Technology & AI": 0.8}
            ),
            QuizOption(
                id="q3_district",
                label="District & Grassroots Reporting",
                description="Local town courts, district police updates, agricultural mandis",
                icon="map",
                weight_map={"field:States & Regional": 1.0, "field:Agriculture & Rural": 0.8}
            ),
            QuizOption(
                id="q3_pan_state",
                label="Statewide Policy & Legislative Analysis",
                description="Cabinet decisions, high court rulings, state development schemes",
                icon="landmark",
                weight_map={"field:Politics": 1.0, "field:Finance & Economics": 0.7}
            )
        ]
    ),
    QuizQuestion(
        id=4,
        dimension="region",
        title="Which key economic corridors do you monitor?",
        subtitle="Prioritize news on trade, bullion, and commercial hubs.",
        is_multi_select=False,
        options=[
            QuizOption(
                id="q4_finance_bullion",
                label="Bullion & Commodities (Gold, Silver, Trade)",
                description="Kerala jeweller trade, gold rate forecasts, commercial taxes",
                icon="trending-up",
                weight_map={"field:Finance & Economics": 1.0, "tag:gold rate": 1.0, "tag:bullion market": 1.0}
            ),
            QuizOption(
                id="q4_farming_dairy",
                label="Agrarian Belts & Rural Economy",
                description="Crop prices, dairy farming, seed preparation, kisan welfare",
                icon="leaf",
                weight_map={"field:Agriculture & Rural": 1.0, "tag:dairy farming": 1.0}
            ),
            QuizOption(
                id="q4_it_manufacturing",
                label="Technology & Smart Cities",
                description="AI traffic camera infrastructure, tech controversies, smart policing",
                icon="cpu",
                weight_map={"field:Technology & AI": 1.0}
            )
        ]
    ),
    QuizQuestion(
        id=5,
        dimension="region",
        title="How should multi-regional perspectives be presented?",
        subtitle="Choose how the digest contextualizes stories from different states.",
        is_multi_select=False,
        options=[
            QuizOption(
                id="q5_bilingual",
                label="Original Source with English Executive Brief",
                description="Read full English synthesis alongside original language excerpt",
                icon="columns",
                weight_map={"framing:bilingual": 1.0}
            ),
            QuizOption(
                id="q5_english_exec",
                label="Fast English Bullet Takeaways",
                description="Rapid 30-second bullet summaries for maximum efficiency",
                icon="zap",
                weight_map={"framing:fast": 1.0}
            ),
            QuizOption(
                id="q5_deep_read",
                label="Comprehensive Dual Perspective",
                description="Complete faithful English translation of entire dispatches",
                icon="book-open",
                weight_map={"framing:deep": 1.0}
            )
        ]
    ),

    # --- DIMENSION 2: TOPICAL FIELDS & DOMAINS (Q6-Q11) ---
    QuizQuestion(
        id=6,
        dimension="field",
        title="What is your primary editorial field?",
        subtitle="Articles matching this topic will receive top priority in your digest.",
        is_multi_select=False,
        options=[
            QuizOption(
                id="q6_politics",
                label="Politics & Governance",
                description="Elections, political rallies, assemblies, Supreme Court orders",
                icon="landmark",
                weight_map={"field:Politics": 1.0}
            ),
            QuizOption(
                id="q6_education_jobs",
                label="Education, Exams & Career Vacancies",
                description="NEET PG toppers, civil services, BTSC/IGNOU/DRDO government jobs",
                icon="book-open",
                weight_map={"field:Education & Jobs": 1.0}
            ),
            QuizOption(
                id="q6_cinema",
                label="Entertainment & Cinema",
                description="Kollywood, Bollywood, Tollywood, box office records, celebrities",
                icon="film",
                weight_map={"field:Entertainment & Cinema": 1.0}
            ),
            QuizOption(
                id="q6_health",
                label="Health, Medicine & Wellness",
                description="First aid, kidney diagnostics, natural remedies, fitness science",
                icon="activity",
                weight_map={"field:Health & Wellness": 1.0}
            ),
            QuizOption(
                id="q6_agriculture",
                label="Agriculture & Rural Development",
                description="Dairy farming, horticulture, kisan welfare, crop seasons",
                icon="leaf",
                weight_map={"field:Agriculture & Rural": 1.0}
            ),
            QuizOption(
                id="q6_tech",
                label="Technology & Artificial Intelligence",
                description="AI cameras, surveillance tech, digital governance, smart systems",
                icon="cpu",
                weight_map={"field:Technology & AI": 1.0}
            ),
        ]
    ),
    QuizQuestion(
        id=7,
        dimension="field",
        title="What career and education topics interest you most?",
        subtitle="Fine-tune your education & recruitment feed.",
        is_multi_select=False,
        options=[
            QuizOption(
                id="q7_competitive_exams",
                label="Competitive Exams & Medical/Engineering Entrances",
                description="NEET PG, AFMC, civil service topper interviews & guidance",
                icon="award",
                weight_map={"field:Education & Jobs": 0.9, "tag:neet pg": 1.0}
            ),
            QuizOption(
                id="q7_govt_jobs",
                label="Government Recruitment & Public Sector Vacancies",
                description="BTSC, IGNOU, NHM Nursing, DRDO internships & applications",
                icon="file-text",
                weight_map={"field:Education & Jobs": 0.9, "tag:government jobs": 1.0, "tag:btsc vacancy": 1.0}
            ),
            QuizOption(
                id="q7_study_abroad",
                label="Higher Education & Studying Abroad",
                description="Study in Germany, international student costs, visa & degrees",
                icon="globe-2",
                weight_map={"field:Education & Jobs": 0.8, "tag:study abroad": 1.0}
            )
        ]
    ),
    QuizQuestion(
        id=8,
        dimension="field",
        title="Which healthcare and wellness updates do you seek?",
        subtitle="Personalize your health intelligence stream.",
        is_multi_select=False,
        options=[
            QuizOption(
                id="q8_clinical",
                label="Medical Diagnostics & Emergency First Aid",
                description="Kidney tests (KFT, creatinine), bee sting protocols, clinical advice",
                icon="activity",
                weight_map={"field:Health & Wellness": 0.9, "tag:first aid": 1.0, "tag:kidney health": 1.0}
            ),
            QuizOption(
                id="q8_fitness_diet",
                label="Fitness Science & Weight Management",
                description="Workout sweating science, calorie burn, active lifestyle",
                icon="zap",
                weight_map={"field:Health & Wellness": 0.8, "tag:fitness science": 1.0}
            ),
            QuizOption(
                id="q8_natural_wellness",
                label="Natural Remedies & Skincare",
                description="Herbal hair conditioners, aloe vera & potato packs, home remedies",
                icon="sun",
                weight_map={"field:Health & Wellness": 0.8, "tag:skincare": 1.0, "tag:natural remedies": 1.0}
            )
        ]
    ),
    QuizQuestion(
        id=9,
        dimension="field",
        title="What cinema and cultural industries do you follow?",
        subtitle="Tailor your entertainment and arts dispatches.",
        is_multi_select=False,
        options=[
            QuizOption(
                id="q9_south_cinema",
                label="South Indian Cinema (Kollywood, Tollywood, Mollywood)",
                description="Thalapathy Vijay, SS Rajamouli, Fahadh Faasil, Mohan Babu",
                icon="film",
                weight_map={"field:Entertainment & Cinema": 0.9, "region:Tamil Nadu": 0.6, "region:Telangana/Andhra Pradesh": 0.6}
            ),
            QuizOption(
                id="q9_bollywood",
                label="Bollywood & Classic Indian Cinema",
                description="Drishyam box office, Lata Mangeshkar, Dilip Kumar retrospectives",
                icon="video",
                weight_map={"field:Entertainment & Cinema": 0.9, "region:India": 0.6}
            ),
            QuizOption(
                id="q9_heritage",
                label="Temple Architecture & Cultural Heritage",
                description="Ancient temples, spiritual festivals, Jain Paryushan Parva, Shaivism",
                icon="book-open",
                weight_map={"field:Culture & Society": 1.0}
            )
        ]
    ),
    QuizQuestion(
        id=10,
        dimension="field",
        title="Which financial & market reports do you track?",
        subtitle="Select macroeconomic and market intelligence priorities.",
        is_multi_select=False,
        options=[
            QuizOption(
                id="q10_gold",
                label="Gold, Silver & Bullion Trends",
                description="Daily gold rates, price crash/rally predictions, retail jewellery news",
                icon="trending-up",
                weight_map={"field:Finance & Economics": 1.0, "tag:gold rate": 1.0}
            ),
            QuizOption(
                id="q10_economy",
                label="Trade Policy & Business Regulations",
                description="Merchant protests, commercial tax rules, economic policy",
                icon="layers",
                weight_map={"field:Finance & Economics": 0.9}
            ),
            QuizOption(
                id="q10_consumer",
                label="Rural Finance & Agrarian Economics",
                description="Kisan loans, agricultural subsidies, dairy production value",
                icon="pie-chart",
                weight_map={"field:Agriculture & Rural": 0.8, "field:Finance & Economics": 0.6}
            )
        ]
    ),
    QuizQuestion(
        id=11,
        dimension="field",
        title="How should incident and regional stories be filtered?",
        subtitle="Manage alerts regarding weather, traffic safety, and law & order.",
        is_multi_select=False,
        options=[
            QuizOption(
                id="q11_weather",
                label="Extreme Weather & IMD Cyclone Alerts",
                description="Depression systems, rainfall warnings, coastal safety",
                icon="cloud-rain",
                weight_map={"field:States & Regional": 1.0, "tag:weather alert": 1.0}
            ),
            QuizOption(
                id="q11_safety",
                label="Road Safety & Law Enforcement",
                description="Hit-and-run accountability, police investigations, civic safety",
                icon="shield-alert",
                weight_map={"field:States & Regional": 1.0, "tag:road safety": 1.0, "tag:law & order": 1.0}
            ),
            QuizOption(
                id="q11_balanced",
                label="Balanced Mix with Constructive Highlights",
                description="Human interest, moral turnarounds, community resilience",
                icon="heart",
                weight_map={"field:States & Regional": 0.8, "field:Culture & Society": 0.6}
            )
        ]
    ),

    # --- DIMENSION 3: LANGUAGE & EDITORIAL DYNAMICS (Q12-Q15) ---
    QuizQuestion(
        id=12,
        dimension="language",
        title="Which source languages do you wish to explore?",
        subtitle="Articles from these vernacular publications will be translated to fluent English.",
        is_multi_select=False,
        options=[
            QuizOption(
                id="q12_western",
                label="Western Indian (Gujarati & Marathi)",
                description="Sandesh, Divya Marathi reporting translated instantly to English",
                icon="languages",
                weight_map={"lang:Gujarati": 1.0, "lang:Marathi": 1.0, "region:Gujarat": 0.8, "region:Maharashtra": 0.8}
            ),
            QuizOption(
                id="q12_hindi",
                label="Hindi (National Press)",
                description="ABP Live national dispatches translated into English briefings",
                icon="newspaper",
                weight_map={"lang:Hindi": 1.0, "region:India": 0.9}
            ),
            QuizOption(
                id="q12_southern",
                label="South Indian (Tamil, Telugu & Malayalam)",
                description="Vikatan, Telugu One India, Malayalam One India translated to English",
                icon="globe",
                weight_map={"lang:Tamil": 1.0, "lang:Telugu": 1.0, "lang:Malayalam": 1.0}
            ),
            QuizOption(
                id="q12_all",
                label="Full Multilingual Polyglot (All 6 Languages)",
                description="Equal exposure across Gujarati, Hindi, Marathi, Tamil, Telugu & Malayalam",
                icon="share-2",
                weight_map={"lang:Gujarati": 0.8, "lang:Hindi": 0.8, "lang:Marathi": 0.8, "lang:Tamil": 0.8, "lang:Telugu": 0.8, "lang:Malayalam": 0.8}
            )
        ]
    ),
    QuizQuestion(
        id=13,
        dimension="language",
        title="What editorial depth do you prefer?",
        subtitle="How should stories be structured in your feed?",
        is_multi_select=False,
        options=[
            QuizOption(
                id="q13_executive",
                label="Executive 3-Bullet Takeaways",
                description="High-velocity briefings with core facts and immediate context",
                icon="list",
                weight_map={"summary_style:bullets": 1.0}
            ),
            QuizOption(
                id="q13_investigative",
                label="In-Depth Investigative Translation",
                description="Full quotes, ground-level reporter accounts, comprehensive context",
                icon="search",
                weight_map={"summary_style:deep": 1.0}
            ),
            QuizOption(
                id="q13_comparative",
                label="Cross-Regional Contrast",
                description="Compare how different states report on parallel political and civic issues",
                icon="columns",
                weight_map={"summary_style:comparative": 1.0}
            )
        ]
    ),
    QuizQuestion(
        id=14,
        dimension="language",
        title="Which audio-visual features do you value?",
        subtitle="Select accessibility and audio preferences.",
        is_multi_select=False,
        options=[
            QuizOption(
                id="q14_audio",
                label="Audio Voice Narration",
                description="Listen to translated English briefings via text-to-speech",
                icon="volume-2",
                weight_map={"pref:audio": 1.0}
            ),
            QuizOption(
                id="q14_reader",
                label="Split Dual-Script Reader",
                description="Side-by-side view of original vernacular script and English translation",
                icon="book-open",
                weight_map={"pref:dual_reader": 1.0}
            ),
            QuizOption(
                id="q14_quick",
                label="Visual Headline Cards Only",
                description="Scan high-impact cards and tags with minimal distractions",
                icon="check-circle",
                weight_map={"pref:visual": 1.0}
            )
        ]
    ),
    QuizQuestion(
        id=15,
        dimension="language",
        title="How should your feed be prioritized?",
        subtitle="Set the rhythm of your news discovery.",
        is_multi_select=False,
        options=[
            QuizOption(
                id="q15_foryou",
                label="Strict Personalization First ('For You')",
                description="Rank stories strictly by your interest graph with match percentage",
                icon="sparkles",
                weight_map={"feed_preference:foryou": 1.0}
            ),
            QuizOption(
                id="q15_trending",
                label="Global & National Breaking Trends First",
                description="Surface viral high-impact political and emergency developments",
                icon="flame",
                weight_map={"feed_preference:trending": 1.0}
            ),
            QuizOption(
                id="q15_explore",
                label="Custom Exploratory Filter View",
                description="Browse by custom slice of region, language, and editorial field",
                icon="sliders",
                weight_map={"feed_preference:explore": 1.0}
            )
        ]
    )
]

def get_quiz_response() -> QuizListResponse:
    """Return the structured 15-question quiz."""
    return QuizListResponse(
        total_questions=len(ONBOARDING_QUESTIONS),
        questions=ONBOARDING_QUESTIONS
    )

def calculate_interest_graph(answers: list) -> dict:
    """
    Calculate normalized interest weights, preferred languages, regions, and fields
    from the user's submitted onboarding answers.
    """
    question_lookup = {q.id: q for q in ONBOARDING_QUESTIONS}
    accumulated_weights = {}
    preferred_languages = set()
    preferred_regions = set()
    preferred_fields = set()

    for ans in answers:
        q = question_lookup.get(ans.question_id)
        if not q:
            continue
        for opt_id in ans.selected_option_ids:
            for opt in q.options:
                if opt.id == opt_id:
                    for key, val in opt.weight_map.items():
                        accumulated_weights[key] = round(accumulated_weights.get(key, 0.0) + val, 3)
                        # Extract tags
                        if key.startswith("lang:"):
                            preferred_languages.add(key.replace("lang:", ""))
                        elif key.startswith("region:"):
                            preferred_regions.add(key.replace("region:", ""))
                        elif key.startswith("field:"):
                            preferred_fields.add(key.replace("field:", ""))

    # Normalize max weight to 1.0
    if accumulated_weights:
        max_val = max(accumulated_weights.values())
        if max_val > 0:
            for k in accumulated_weights:
                accumulated_weights[k] = round(accumulated_weights[k] / max_val, 3)

    return {
        "interest_weights": accumulated_weights,
        "preferred_languages": sorted(list(preferred_languages)),
        "preferred_regions": sorted(list(preferred_regions)),
        "preferred_fields": sorted(list(preferred_fields))
    }
