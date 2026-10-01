from datetime import datetime, timedelta, timezone
from typing import List, Dict, Any

def utc_now():
    return datetime.now(timezone.utc)

SEED_ARTICLES: List[Dict[str, Any]] = [
    {
        "source_url": "https://www.lemonde.fr/economie/article/2026/09/24/ia-et-souverainete-numerique-la-france-et-l-europe-intensifient-leurs-investissements_6234912_3234.html",
        "source_name": "Le Monde",
        "original_language": "French",
        "original_title": "IA et souveraineté numérique : La France et l'Union européenne intensifient leurs investissements dans les supercalculateurs",
        "original_content": "Le président Emmanuel Macron et la Commission européenne ont dévoilé un nouveau plan d'investissement de 10 milliards d'euros pour accélérer le déploiement de supercalculateurs exaflopiques sur le sol européen. Face à la domination des géants technologiques américains et chinois, l'initiative vise à héberger l'entraînement des modèles de langage ouverts de prochaine génération au sein de centres de données neutres en carbone en Bretagne et en Rhénanie.",
        "original_summary": "La France et l'Union européenne annoncent un investissement de 10 milliards d'euros pour développer des supercalculateurs exaflopiques souverains. Ce programme vise à garantir l'indépendance de l'entraînement des modèles d'IA européens avec une empreinte carbone neutre.",
        "english_title": "AI & Digital Sovereignty: France and the EU Ramp Up €10B Investment in Sovereign Supercomputing",
        "english_summary": "• European leaders unveil a €10 billion initiative to build exascale supercomputing infrastructure in France and Germany.\n• Aims to secure sovereign training capabilities for open-source AI models independent of US hyperscalers.\n• Emphasizes green data center operations with 100% renewable power guarantees.",
        "english_content": "French President Emmanuel Macron and the European Commission have unveiled an ambitious €10 billion investment package aimed at deploying exascale AI supercomputing clusters across Europe. Facing intensifying competition from American and Asian tech conglomerates, the initiative seeks to establish an independent computational foundation for next-generation open foundational models. Strategic compute clusters will be located in Brittany and Rhineland, powered directly by dedicated nuclear and offshore wind generation.",
        "region": "Europe",
        "subregion": "Western Europe",
        "field": "Technology & AI",
        "keywords": ["ai", "supercomputing", "sovereignty", "france", "europe", "cleantech"],
        "trending": True,
        "trending_score": 0.94,
        "image_url": "https://images.unsplash.com/photo-1518770660439-4636190af475?auto=format&fit=crop&w=800&q=80",
        "published_at": utc_now() - timedelta(hours=3)
    },
    {
        "source_url": "https://elpais.com/tecnologia/2026-09-23/el-banco-de-espana-impulsa-el-euro-digital-en-pruebas-con-comercios-minoristas.html",
        "source_name": "El País",
        "original_language": "Spanish",
        "original_title": "El Banco de España y el BCE aceleran las pruebas piloto del euro digital para pagos sin conexión",
        "original_content": "El Banco de España ha comenzado hoy en Madrid una fase piloto decisiva para probar la resiliencia del euro digital en transacciones minoristas sin conexión a internet (offline). La iniciativa, supervisada por el Banco Central Europeo, permite a los usuarios transferir moneda digital soberana de dispositivo a dispositivo con total privacidad y sin comisiones de intermediarios financieros.",
        "original_summary": "El Banco de España y el Banco Central Europeo inician pruebas clave en Madrid para validar el euro digital en pagos minoristas sin conexión a internet. La tecnología garantiza privacidad equivalente al dinero en efectivo y suprime comisiones bancarias para comercios.",
        "english_title": "Bank of Spain & ECB Accelerate Digital Euro Pilot for Offline Retail Payments",
        "english_summary": "• Bank of Spain initiates live trial of the digital euro in Madrid, focusing on peer-to-peer offline transactions.\n• Designed to guarantee privacy equivalent to physical cash without commercial card interchange fees.\n• Represents Europe's key response to private stablecoins and cross-border payment frictions.",
        "english_content": "The Bank of Spain launched an operational pilot phase in Madrid testing the digital euro's performance in offline retail environments. Conducted under the auspices of the European Central Bank, the trial examines direct hardware-to-hardware currency transfers without active network connectivity, assuring physical-cash equivalence in privacy while eliminating card-processing transaction fees for merchants.",
        "region": "Europe",
        "subregion": "Southern Europe",
        "field": "Finance & Economics",
        "keywords": ["fintech", "digital-euro", "spain", "ecb", "central-banking", "payments"],
        "trending": True,
        "trending_score": 0.88,
        "image_url": "https://images.unsplash.com/photo-1559526324-4b87b5e36e44?auto=format&fit=crop&w=800&q=80",
        "published_at": utc_now() - timedelta(hours=6)
    },
    {
        "source_url": "https://www.dw.com/de/energiewende-deutschland-erreicht-neuen-rekord-bei-windkraft-auf-see/a-71829304",
        "source_name": "Deutsche Welle",
        "original_language": "German",
        "original_title": "Energiewende: Deutschland bricht neuen Rekord bei Offshore-Windkraft in Nord- und Ostsee",
        "original_content": "Die Bundesnetzagentur hat für das zurückliegende Quartal einen historischen Höchststand bei der Einspeisung von Windenergie gemeldet. Mehr als 62 Prozent des industriellen Strombedarfs wurden zeitweise durch neue schwimmende Windparks in der Nordsee gedeckt. Bundeswirtschaftsminister Habeck betonte, dass der zügige Ausbau der Gleichstromtrassen nach Süddeutschland die Energiekosten für den Mittelstand spürbar senken werde.",
        "original_summary": "Deutschland erzielt einen neuen Rekord bei der Offshore-Windenergieerzeugung in der Nordsee, die zeitweise über 62 Prozent des industriellen Strombedarfs deckt. Der zügige Ausbau der Gleichstromleitungen soll die Energiepreise für den Mittelstand stabilisieren.",
        "english_title": "Energy Transition: Germany Hits All-Time Record in North Sea Offshore Wind Power",
        "english_summary": "• Germany's Federal Network Agency reports over 62% of industrial peak electricity sourced from North Sea wind.\n• Floating offshore turbine capacity expands ahead of schedule along northern coastal grids.\n• Completion of high-voltage DC transmission lines brings cheaper renewable power to southern manufacturing hubs.",
        "english_content": "Germany's Federal Network Agency recorded an unprecedented surge in offshore wind electricity generation in the North and Baltic Seas. During peak production periods, offshore turbines covered over 62% of industrial electricity demand nationwide. Officials confirmed that expedited completion of high-voltage direct current (HVDC) corridors will significantly diminish energy price volatility for German heavy manufacturing.",
        "region": "Europe",
        "subregion": "Central Europe",
        "field": "Climate & Energy",
        "keywords": ["energy", "windpower", "germany", "renewables", "grid", "clean-tech"],
        "trending": False,
        "trending_score": 0.72,
        "image_url": "https://images.unsplash.com/photo-1466611653911-95081537e5b7?auto=format&fit=crop&w=800&q=80",
        "published_at": utc_now() - timedelta(hours=12)
    },
    {
        "source_url": "https://www3.nhk.or.jp/news/html/20260924/k10014589201000.html",
        "source_name": "NHK World News",
        "original_language": "Japanese",
        "original_title": "次世代半導体Rapidus、2ナノメートル量産試作ラインの全自動化を完了 北海道工場で稼働開始",
        "original_content": "日本の次世代半導体製造企業ラピダスは、北海道千歳市に建設中の新工場において、最先端2ナノメートルプロセスの試作生産ラインで完全自動化を達成したと発表しました。AI制御のロボット搬送システムと極端紫外線（EUV）露光装置が連携し、世界最高水準の歩留まりを目指します。政府は追加の支援策を検討しており、国内外の自動車およびAIサーバーメーカーからの受注獲得を急ぎます。",
        "original_summary": "次世代半導体メーカーのラピダスが北海道千歳市の新工場で、最先端2ナノメートル試作ラインの全自動化を完了しました。AI搬送とEUV露光を組み合わせ、自動運転や次世代AI向け半導体の量産化を目指します。",
        "english_title": "Next-Gen Chipmaker Rapidus Fully Automates 2nm Pilot Line at Hokkaido Gigafab",
        "english_summary": "• Japanese chipmaker Rapidus completes full robotic automation of its 2nm trial production in Chitose, Hokkaido.\n• Combines EUV lithography with AI-driven material transport to challenge Asian foundries.\n• Targets high-margin compute silicon for autonomous mobility and generative AI server infrastructure.",
        "english_content": "Japanese next-generation semiconductor venture Rapidus announced the completion and automated commissioning of its advanced 2-nanometer pilot manufacturing facility in Chitose, Hokkaido. Integrating AI-orchestrated wafer handling robotics with high-numerical-aperture EUV lithography systems, the enterprise aims to establish competitive yields ahead of 2027 commercial volume manufacturing for automotive autonomous driving chips and next-gen server acceleration modules.",
        "region": "Asia-Pacific",
        "subregion": "East Asia",
        "field": "Technology & AI",
        "keywords": ["semiconductors", "rapidus", "japan", "chips", "hardware", "ai"],
        "trending": True,
        "trending_score": 0.96,
        "image_url": "https://images.unsplash.com/photo-1581091226825-a6a2a5aee158?auto=format&fit=crop&w=800&q=80",
        "published_at": utc_now() - timedelta(hours=4)
    },
    {
        "source_url": "https://www.aljazeera.net/economy/2026/9/23/gulf-green-hydrogen-investments-surpass-50-billion",
        "source_name": "Al Jazeera",
        "original_language": "Arabic",
        "original_title": "استثمارات الهيدروجين الأخضر في منطقة الخليج تتجاوز 50 مليار دولار ضمن خطط تنويع الاقتصاد",
        "original_content": "أعلنت دول مجلس التعاون الخليجي، بقيادة المملكة العربية السعودية وسلطنة عمان، عن وصول إجمالي الالتزامات الاستثمارية في مشاريع الهيدروجين الأخضر والأمونيا النظيفة إلى أكثر من 50 مليار دولار بحلول عام 2026. وتهدف هذه المشاريع العملاقة إلى تزويد الأسواق الأوروبية والآسيوية بوقود خالٍ من الانبعاثات الكربونية، مع الاستفادة من وفرة الطاقة الشمسية والرياح على مدار العام في الصحاري الخليجية.",
        "original_summary": "تجاوزت استثمارات دول مجلس التعاون الخليجي في مشاريع الهيدروجين الأخضر والأمونيا النظيفة 50 مليار دولار بقيادة السعودية وعُمان، بهدف تزويد الأسواق العالمية بوقود مستدام والاستفادة من موارد الطاقة المتجددة.",
        "english_title": "Gulf Green Hydrogen Commitments Expass $50 Billion in Post-Oil Economic Transformation",
        "english_summary": "• GCC sovereign funds and utilities commit over $50B to green hydrogen and clean ammonia megaprojects.\n• Saudi Arabia and Oman lead export corridors targeting European and Asian industrial buyers.\n• Capitalizes on year-round solar irradiance and strategic maritime shipping access.",
        "english_content": "Gulf Cooperation Council nations, spearheaded by Saudi Arabia and the Sultanate of Oman, have surpassed $50 billion in cumulative allocated capital for industrial green hydrogen and clean ammonia facilities. Leveraging ultra-low solar generation costs in desert corridors and deep-water port access, these megaprojects aim to position the Gulf as the primary supplier of zero-carbon fuels to European and East Asian heavy industrial conglomerates seeking compliance with carbon border mandates.",
        "region": "Middle East",
        "subregion": "Gulf Region",
        "field": "Climate & Energy",
        "keywords": ["hydrogen", "clean-energy", "gulf", "saudi", "oman", "economy"],
        "trending": False,
        "trending_score": 0.78,
        "image_url": "https://images.unsplash.com/photo-1509391365360-2e959784a276?auto=format&fit=crop&w=800&q=80",
        "published_at": utc_now() - timedelta(hours=14)
    },
    {
        "source_url": "https://www.bbc.com/mundo/noticias-america-latina-68932401",
        "source_name": "BBC Mundo",
        "original_language": "Spanish",
        "original_title": "El 'triángulo del litio' en Sudamérica define un nuevo marco regulatorio conjunto para la agregación de valor",
        "original_content": "Representantes de los ministerios de minería de Argentina, Bolivia y Chile concluyeron en Santiago una cumbre de tres días en la que acordaron una hoja de ruta común para la industrialización local del litio. El acuerdo busca superar la exportación exclusiva de materia prima en bruto mediante incentivos fiscales para el ensamblaje de celdas de baterías y componentes electrónicos dentro de la región andina.",
        "original_summary": "Argentina, Bolivia y Chile firman un acuerdo clave en Santiago para coordinar la industrialización local del litio. El tratado establece incentivos fiscales conjuntos para la fabricación de baterías de vehículos eléctricos en la región andina.",
        "english_title": "South America's 'Lithium Triangle' Unifies Framework for Domestic Battery Value Addition",
        "english_summary": "• Argentina, Bolivia, and Chile conclude Santiago summit establishing unified value-add lithium policies.\n• Shifts strategy away from unrefined raw brine exports toward domestic battery cell production.\n• Offers coordinated tax incentives for EV supply chain factories locating in the Andean bloc.",
        "english_content": "Mining ministers and industrial delegates from Argentina, Bolivia, and Chile finalized a landmark multilateral agreement in Santiago harmonizing regulatory standards across the 'Lithium Triangle'. The treaty establishes joint technical certifications and preferential fiscal zones designed to attract global electric mobility manufacturers, mandating domestic processing and battery component fabrication rather than straightforward raw mineral extraction.",
        "region": "Latin America",
        "subregion": "South America",
        "field": "Finance & Economics",
        "keywords": ["lithium", "latin-america", "batteries", "mining", "ev", "trade"],
        "trending": True,
        "trending_score": 0.89,
        "image_url": "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?auto=format&fit=crop&w=800&q=80",
        "published_at": utc_now() - timedelta(hours=8)
    },
    {
        "source_url": "https://www.lemonde.fr/culture/article/2026/09/22/le-musee-du-louvre-inaugure-son-espace-dedie-a-l-art-numerique-et-a-l-archeologie-virtuelle_6234091_3246.html",
        "source_name": "Le Monde",
        "original_language": "French",
        "original_title": "Le musée du Louvre inaugure une aile révolutionnaire dédiée à l'archéologie immersive et aux arts numériques",
        "original_content": "Le plus célèbre musée du monde a ouvert hier les portes de sa nouvelle aile interactive dans le pavillon de Flore. Utilisant la restitution volumétrique par laser et la réalité mixte, les visiteurs peuvent déambuler au cœur de cités mésopotamiennes disparues et observer des chefs-d'œuvre de la Renaissance reconstitués dans leurs couleurs originelles exactes, telles qu'elles étaient au XVIe siècle.",
        "original_summary": "Le musée du Louvre inaugure un espace interactif dans le pavillon de Flore alliant réalité mixte et restitution volumétrique pour faire revivre des cités antiques et des chefs-d'œuvre de la Renaissance dans leurs couleurs d'époque.",
        "english_title": "Louvre Opens Immersive Wing Dedicated to Volumetric Archaeology and Digital Heritage",
        "english_summary": "• Musée du Louvre inaugurates revolutionary interactive pavilion Flore in Paris.\n• Combines LIDAR scans and volumetric reconstruction to let visitors walk through ancient Mesopotamian cities.\n• Restores Renaissance masterworks to their scientifically verified original 16th-century pigment hues.",
        "english_content": "The Musée du Louvre in Paris opened a groundbreaking permanent exhibition space inside the Pavillon de Flore, merging fine art preservation with volumetric digital technology. Through spatial computing and historical lidar models, visitors can physically explore ancient Mesopotamian cityscapes and view Renaissance masterworks digitally restored to their precise 16th-century chromatic luminosity.",
        "region": "Europe",
        "subregion": "Western Europe",
        "field": "Culture & Society",
        "keywords": ["louvre", "art", "museum", "paris", "digital-heritage", "archaeology"],
        "trending": False,
        "trending_score": 0.65,
        "image_url": "https://images.unsplash.com/photo-1499856871958-5b9627545d1a?auto=format&fit=crop&w=800&q=80",
        "published_at": utc_now() - timedelta(hours=18)
    },
    {
        "source_url": "https://www.bbc.com/news/world-asia-68994512",
        "source_name": "BBC World",
        "original_language": "English",
        "original_title": "Global Treaty on AI Safety Verification Signed by 42 Nations in Geneva",
        "original_content": "Delegates from 42 countries have ratified the Geneva Accord on Autonomous Artificial Intelligence Verification. The treaty mandates independent third-party algorithmic audits for frontier foundation models exceeding 10^26 floating-point training operations, establishing a shared diplomatic incident response framework for critical digital infrastructure.",
        "original_summary": "42 sovereign nations have signed the Geneva Accord on Frontier AI Verification, introducing mandatory third-party audits and diplomatic incident response protocols for large-scale foundation models.",
        "english_title": "Global Treaty on AI Safety Verification Signed by 42 Nations in Geneva",
        "english_summary": "• 42 countries ratify the Geneva Accord establishing mandatory third-party audits for frontier AI models.\n• Sets up a multilateral digital inspection protocol akin to international civil aviation monitoring.\n• Balances innovation safeguards with unified compliance procedures across major economies.",
        "english_content": "In a historic diplomatic milestone, representatives from 42 sovereign states signed the Geneva Accord on Frontier Artificial Intelligence Verification. The framework imposes mutual inspection mechanisms for models trained with unprecedented compute thresholds, establishing international incident notification desks and shared cybersecurity stress-testing protocols.",
        "region": "Global",
        "subregion": "International",
        "field": "Geopolitics",
        "keywords": ["ai-safety", "diplomacy", "geneva", "treaty", "regulation", "governance"],
        "trending": True,
        "trending_score": 0.98,
        "image_url": "https://images.unsplash.com/photo-1541872703-74c5e44368f9?auto=format&fit=crop&w=800&q=80",
        "published_at": utc_now() - timedelta(hours=1)
    }
]

SAMPLE_ARTICLES = SEED_ARTICLES

def seed_database(db):
    """Seed initial high-quality multilingual articles if database is empty."""
    from app.models.article import Article
    
    count = db.query(Article).count()
    if count == 0:
        for item in SEED_ARTICLES:
            art = Article(
                source_url=item["source_url"],
                source_name=item["source_name"],
                original_language=item["original_language"],
                original_title=item["original_title"],
                original_content=item["original_content"],
                original_summary=item.get("original_summary"),
                english_title=item["english_title"],
                english_summary=item["english_summary"],
                english_content=item["english_content"],
                region=item["region"],
                subregion=item["subregion"],
                field=item["field"],
                keywords=item["keywords"],
                trending=item["trending"],
                trending_score=item["trending_score"],
                image_url=item["image_url"],
                published_at=item["published_at"],
                created_at=utc_now()
            )
            db.add(art)
        db.commit()
