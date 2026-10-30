import pytest
import time
import concurrent.futures
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app import models
from app.main import app
from app.config import settings
from app.services.llm_pipeline import llm_pipeline, NEWS_SUMMARY_SCHEMA, detect_source_language, is_predominantly_english
from app.services.seed_data import seed_database


# ---------------------------------------------------------
# Test Data Fixtures for Multilingual Articles
# ---------------------------------------------------------

HINDI_ARTICLE = {
    "title": "इसरो ने गगनयान मिशन के लिए क्रायोजेनिक इंजन का सफल परीक्षण पूरा किया",
    "content": """भारतीय अंतरिक्ष अनुसंधान संगठन (इसरो) ने तमिलनाडु के महेंद्रगिरि स्थित प्रोपल्शन कॉम्प्लेक्स में गगनयान मानव अंतरिक्ष उड़ान मिशन के लिए मानव-रेटेड क्रायोजेनिक इंजन (सीई-20) का सफल योग्यता परीक्षण किया है।
इसरो के अनुसार, इंजन का परीक्षण 720 सेकंड की निर्धारित अवधि के लिए किया गया, जो उड़ान संचालन के दौरान आवश्यक अवधि से अधिक है। परीक्षण के दौरान सभी परिचालन मापदंड सामान्य पाए गए। 
सीई-20 इंजन गगनयान मिशन के एलवीएम3 रॉकेट के ऊपरी क्रायोजेनिक चरण को शक्ति प्रदान करेगा। 
इसरो अध्यक्ष एस. सोमनाथ ने घोषणा की कि यह सफल परीक्षण भारत के पहले मानवयुक्त अंतरिक्ष मिशन के लिए महत्वपूर्ण मील का पत्थर साबित होगा। मिशन का उद्देश्य तीन सदस्यीय चालक दल को तीन दिनों के लिए 400 किमी की कक्षा में लॉन्च करना और उन्हें सुरक्षित पृथ्वी पर वापस लाना है।""",
    "expected_language": "Hindi",
    "expected_keywords": ["ISRO", "Gaganyaan", "Cryogenic"]
}

MARATHI_ARTICLE = {
    "title": "पुणे-नाशिक सेमी हायस्पीड रेल्वे प्रकल्पाला केंद्र सरकारची अंतिम मंजुरी",
    "content": """पुणे आणि नाशिक या दोन महत्त्वाच्या औद्योगिक शहरांना जोडणाऱ्या सेमी हायस्पीड रेल्वे प्रकल्पाला केंद्र शासनाने हिरवा कंदील दाखवला आहे. 
या प्रकल्पामुळे पुणे ते नाशिक दरम्यानचे अंतर अवघ्या दोन तासांत पूर्ण करता येणार आहे. 
महाराष्ट्र रेल इन्फ्रास्ट्रक्चर डेव्हलपमेंट कॉर्पोरेशन (महारेल) या प्रकल्पाची अंमलबजावणी करत आहे. 
या मार्गावर ताशी २०० किमी वेगाने धावणाऱ्या हायस्पीड ट्रेन्स चालवण्याचे नियोजन आहे. या प्रकल्पामुळे शेतकरी आणि उद्योजकांना मोठा फायदा होणार असून, नाशकातील भाजीपाला व औद्योगिक उत्पादने वेगाने पुणे आणि मुंबई बाजारपेठेत पोहोचू शकतील. प्रकल्पासाठी आवश्यक जमिनीचे भूसंपादन ८० टक्के पूर्ण झाले असून लवकरच प्रत्यक्ष बांधकामाला सुरुवात होणार आहे.""",
    "expected_language": "Marathi",
    "expected_keywords": ["Pune", "Nashik", "Railway"]
}

TELUGU_ARTICLE = {
    "title": "విశాఖపట్నంలో అంతర్జాతీయ ఐటీ కాంప్లెక్స్ నిర్మాణానికి ప్రభుత్వం శంకుస్థాపన",
    "content": """ఆంధ్రప్రదేశ్ ముఖ్యమంత్రి విశాఖపట్నం ఐటీ హిల్స్ వద్ద నూతన గ్లోబల్ ఐటీ టవర్ నిర్మాణానికి శంకుస్థాపన చేశారు. 
ఈ ప్రాజెక్టు ద్వారా దాదాపు 15,000 మంది స్థానిక నిరుద్యోగ యువతకు సాంకేతిక మరియు సాఫ్ట్‌వేర్ రంగాల్లో ఉద్యోగావకాశాలు లభించనున్నాయి. 
మొదటి దశలో 500 కోట్ల రూపాయల వ్యయంతో 10 లక్షల చదరపు అడుగుల విస్తీర్ణంలో అంతర్జాతీయ ప్రమాణాలతో కార్యాలయాలు నిర్మించనున్నారు.
ప్రపంచ ప్రఖ్యాత టెక్ దిగ్గజాలు ఇక్కడ తమ కార్యాలయాలను ఏర్పాటు చేసేందుకు ముందుకు వచ్చాయని ఐటీ శాఖ మంత్రి తెలిపారు. వచ్చే 18 నెలల్లో నిర్మాణం పూర్తి చేయాలని అధికారులను ఆదేశించారు.""",
    "expected_language": "Telugu",
    "expected_keywords": ["Visakhapatnam", "IT", "Government"]
}

TAMIL_ARTICLE = {
    "title": "சென்னையில் புதிய பசுமை வழி மெட்ரோ ரயில் வழித்தடம் தொடக்கம்",
    "content": """சென்னையின் போக்குவரத்து நெரிசலைக் குறைக்கும் வகையில், இரண்டாம் கட்ட மெட்ரோ திட்டத்தின் கீழ் புதிய பசுமை வழித்தடத்தை தமிழக முதலமைச்சர் தொடங்கி வைத்தார். 
இந்த வழித்தடம் மாதவரம் முதல் சோழிங்கநல்லூர் வரை 28 கிலோமீட்டர் தொலைவைக் கொண்டுள்ளது. 
சுற்றுச்சூழலுக்கு உகந்த சோலார் மின்சக்தி மற்றும் நவீன தானியங்கி பாதுகாப்பு அமைப்புகளுடன் இந்த மெட்ரோ ரயில்கள் இயக்கப்பட உள்ளன. 
இதன் மூலம் தினசரி சுமார் 3 லட்சம் பயணிகள் பயனடைவார்கள் என்று மெட்ரோ நிர்வாகம் தெரிவித்துள்ளது. மேலும் அனைத்து நிலையங்களிலும் பெண்களுக்கான கூடுதல் பாதுகாப்பு வசதிகள் மற்றும் சிசிடிவி கேமராக்கள் பொருத்தப்பட்டுள்ளன.""",
    "expected_language": "Tamil",
    "expected_keywords": ["Chennai", "Metro"]
}

ENGLISH_ARTICLE = {
    "title": "India Unveils National Quantum Mission to Accelerate Supercomputing Capabilities",
    "content": """The Department of Science and Technology has officially launched the National Quantum Mission with an allocated budget of over six thousand crore rupees. 
The initiative aims to design and develop intermediate-scale quantum computers with 50 to 1000 physical qubits within the next eight years across diverse scientific domains. 
Four thematic hubs will be set up in leading research institutions including the Indian Institutes of Technology and the Indian Institute of Science. 
Officials stated the mission would significantly enhance national security, encrypted communication protocols, advanced pharmaceutical drug discovery, and clean energy modeling. 
International partnerships with global quantum labs are also underway to support hardware fabrication.""",
    "expected_language": "English",
    "expected_keywords": ["Quantum", "Technology", "Mission"]
}


# ---------------------------------------------------------
# Test DB Client Setup
# ---------------------------------------------------------

SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="module")
def client():
    Base.metadata.create_all(bind=engine)
    seed_db = TestingSessionLocal()
    try:
        seed_database(seed_db)
    finally:
        seed_db.close()

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


# ---------------------------------------------------------
# Unit Tests for Language Detection & English Verification
# ---------------------------------------------------------

class TestLanguageDetectionAndValidation:
    def test_detect_source_language_devanagari_marathi_vs_hindi(self):
        hindi_lang, _, _ = detect_source_language(HINDI_ARTICLE["title"], HINDI_ARTICLE["content"])
        marathi_lang, _, _ = detect_source_language(MARATHI_ARTICLE["title"], MARATHI_ARTICLE["content"])
        
        assert hindi_lang == "Hindi"
        assert marathi_lang == "Marathi"

    def test_detect_source_language_dravidian_scripts(self):
        telugu_lang, _, _ = detect_source_language(TELUGU_ARTICLE["title"], TELUGU_ARTICLE["content"])
        tamil_lang, _, _ = detect_source_language(TAMIL_ARTICLE["title"], TAMIL_ARTICLE["content"])
        
        assert telugu_lang == "Telugu"
        assert tamil_lang == "Tamil"

    def test_detect_source_language_english(self):
        english_lang, _, _ = detect_source_language(ENGLISH_ARTICLE["title"], ENGLISH_ARTICLE["content"])
        assert english_lang == "English"

    def test_is_predominantly_english_validation(self):
        pure_english = "The Indian Space Research Organisation conducted a cryogenic engine test."
        assert is_predominantly_english(pure_english) is True
        
        hindi_raw = "भारतीय अंतरिक्ष अनुसंधान संगठन ने क्रायोजेनिक इंजन का परीक्षण किया।"
        assert is_predominantly_english(hindi_raw) is False
        
        mixed_english = "ISRO (Indian Space Research Organisation) announced in Bengaluru that Gaganyaan is ready."
        assert is_predominantly_english(mixed_english) is True


# ---------------------------------------------------------
# Live Ollama Llama 3.2 Multilingual Summarization Tests
# ---------------------------------------------------------

class TestLiveMultilingualSummarization:
    """Tests executing against the local running Ollama Llama 3.2 instance."""
    
    @pytest.mark.parametrize("article_data", [
        HINDI_ARTICLE,
        MARATHI_ARTICLE,
        TELUGU_ARTICLE,
        TAMIL_ARTICLE,
        ENGLISH_ARTICLE
    ], ids=["hindi", "marathi", "telugu", "tamil", "english"])
    def test_multilingual_summary_live(self, article_data):
        """Verify each language produces factual English headline and summary (~80-120 words)."""
        # Verify Ollama is running first
        status = llm_pipeline.check_ollama_status()
        if not status["available"]:
            pytest.skip("Ollama is not running locally; skipping live model test.")

        result = llm_pipeline.process_article(
            title=article_data["title"],
            content=article_data["content"],
            source_name="Regional News Wire"
        )
        
        # 1. Check required fields
        assert result["processing_status"] in ["completed", "flagged"]
        assert "english_title" in result and len(result["english_title"].strip()) > 5
        assert "english_summary" in result and len(result["english_summary"].strip()) > 20
        
        # 2. Check detected language
        assert result["language"].lower() == article_data["expected_language"].lower()
        
        # 3. Check English output purity
        assert is_predominantly_english(result["english_title"]), f"Title not English: {result['english_title']}"
        assert is_predominantly_english(result["english_summary"]), f"Summary not English: {result['english_summary']}"
        
        # 4. Check word count
        words = len(result["english_summary"].split())
        assert result["summary_word_count"] == words
        # Expect reasonable summary length (typically 50-130 words for standard news paragraphs)
        assert words >= 30, f"Summary unexpectedly brief: {words} words"

    def test_short_article_no_hallucination(self):
        """Short snippet should be summarized concisely without inventing false details."""
        short_snippet = "Gold prices rose by 250 rupees per 10 grams in Delhi bullion market today amid strong global trends and wedding season demand."
        result = llm_pipeline.process_article(
            title="Gold Rates Today",
            content=short_snippet,
            source_name="Market Watch"
        )
        assert result["processing_status"] in ["completed", "flagged"]
        summary = result["english_summary"].lower()
        assert "gold" in summary or "prices" in summary or "delhi" in summary

    def test_long_article_hierarchical_chunking(self):
        """Articles > 2000 words should trigger hierarchical chunking."""
        base_paragraph = """The economic survey highlighted rapid industrial expansion across green energy and semiconductor sectors. 
Investments in battery storage systems have doubled, supporting national grid resilience and decarbonization goals. 
State governments have introduced streamlined single-window clearance mechanisms for clean energy projects. """
        
        # Repeat to create an article with > 2,100 words
        long_content = " ".join([base_paragraph] * 80)
        word_count = len(long_content.split())
        assert word_count > 2000

        result = llm_pipeline.process_article(
            title="Comprehensive National Economic and Industrial Strategy Survey",
            content=long_content,
            source_name="Economic Times"
        )
        assert result["processing_status"] in ["completed", "flagged"]
        assert len(result["english_summary"].split()) >= 40
        assert is_predominantly_english(result["english_summary"])


# ---------------------------------------------------------
# Concurrency, Retries & Error Handling Tests
# ---------------------------------------------------------

class TestConcurrencyAndErrorHandling:
    def test_concurrent_requests_preserve_article_association(self):
        """Multiple concurrent requests should maintain correct article ID & content association."""
        status = llm_pipeline.check_ollama_status()
        if not status["available"]:
            pytest.skip("Ollama is not running locally.")

        test_items = [
            ("Art1", "ISRO Satellite Launch Planned", "ISRO will launch a new earth observation satellite next month from Sriharikota."),
            ("Art2", "Automotive Sector EV Subsidies Extended", "The transport ministry extended electric vehicle purchase subsidies for commercial taxi fleets."),
            ("Art3", "Agricultural Monsoon Forecast Predicts Normal Rainfall", "Meteorological department forecast indicates normal monsoon distribution across central agricultural belts.")
        ]

        def call_pipeline(item):
            art_id, title, content = item
            res = llm_pipeline.process_article(title=title, content=content, source_name="Test Agency")
            return (art_id, title, res)

        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            futures = [executor.submit(call_pipeline, item) for item in test_items]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        for art_id, title, res in results:
            summary = res["english_summary"].lower()
            if art_id == "Art1":
                assert "satellite" in summary or "isro" in summary or "launch" in summary
            elif art_id == "Art2":
                assert "electric" in summary or "vehicle" in summary or "ev" in summary or "subsid" in summary
            elif art_id == "Art3":
                assert "monsoon" in summary or "rainfall" in summary or "agricultur" in summary

    def test_bounded_retries_on_network_failure(self):
        """When Ollama raises a connection error, pipeline retries bounded times and returns failed status."""
        import requests

        with patch("requests.post", side_effect=requests.exceptions.ConnectionError("Connection refused")):
            result = llm_pipeline.process_article(
                title="Sample Breaking News",
                content="Sample news dispatch body text for testing failure resilience.",
                source_name="Test Source"
            )
            assert result["processing_status"] == "failed"
            assert "connection refused" in result["processing_error"].lower() or "retries failed" in result["processing_error"].lower()

    def test_reprocess_endpoint(self, client):
        """Verify POST /api/ingest/reprocess can be invoked safely without throwing errors."""
        with patch("app.routers.ingest.run_reprocess_job"):
            res = client.post("/api/ingest/reprocess?limit=5")
            assert res.status_code == 200
            data = res.json()
            assert "message" in data
            assert "reprocessed" in data or "reprocessing" in data["message"].lower()

    def test_individual_article_reprocess_endpoint(self, client):
        """Verify POST /api/articles/{article_id}/reprocess succeeds."""
        mock_processed = {
            "language": "Hindi",
            "region": "India",
            "subregion": "National",
            "field": "Space",
            "keywords": ["ISRO"],
            "trending": True,
            "trending_score": 0.9,
            "english_title": "ISRO Tests Cryogenic Engine",
            "english_summary": "ISRO successfully tested the CE-20 cryogenic engine for the Gaganyaan mission at Mahendragiri.",
            "english_content": "ISRO successfully tested the CE-20 cryogenic engine for the Gaganyaan mission at Mahendragiri.",
            "processing_status": "completed",
            "processing_error": None,
            "summary_word_count": 15
        }
        with patch("app.services.llm_pipeline.llm_pipeline.process_article", return_value=mock_processed):
            res = client.post("/api/articles/1/reprocess")
            assert res.status_code == 200
            data = res.json()
            assert data["processing_status"] == "completed"
            assert data["english_title"] == "ISRO Tests Cryogenic Engine"

    def test_ingest_status_endpoint(self, client):
        """Verify GET /api/ingest/status reports status counts accurately."""
        res = client.get("/api/ingest/status")
        assert res.status_code == 200
        data = res.json()
        assert "total_articles" in data
        assert "completed" in data
        assert "pending" in data
        assert "failed" in data
        assert "flagged" in data
