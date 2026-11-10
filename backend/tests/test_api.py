import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app import models
from app.main import app
from app.config import settings
from app.services.llm_pipeline import llm_pipeline
from app.services.seed_data import seed_database
from app.services.tagging import classify_and_tag, clean_and_normalize_tag, is_valid_tag

# Use in-memory SQLite for testing with StaticPool so all connections share the memory DB
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

def test_health_check(client):
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["llm_provider"] == "Ollama"
    assert data["llm_model"] == settings.OLLAMA_MODEL
    assert "ollama_connected" in data

def test_ollama_status_check():
    """Verify Ollama status checker returns a valid status dictionary."""
    status = llm_pipeline.check_ollama_status()
    assert isinstance(status, dict)
    assert "available" in status
    assert isinstance(status["available"], bool)
    if not status["available"]:
        assert "error" in status
        assert "message" in status

def test_llm_pipeline_attributes_validation():
    """Verify LLM pipeline strictly produces all 6 core attributes plus English content (with offline fallback)."""
    mock_title = "AI Traffic Cameras Mistake Fine Controversy in State"
    mock_content = "Traffic authorities reported that newly installed artificial intelligence traffic cameras experienced technical calibration disputes."
    
    result = llm_pipeline.process_article(mock_title, mock_content, "Divya Marathi", expected_region="Maharashtra", expected_language="Marathi")
    
    required_keys = ["language", "region", "subregion", "field", "keywords", "trending", "trending_score", "english_title", "english_summary"]
    for key in required_keys:
        assert key in result, f"Missing required key: {key}"
    
    assert isinstance(result["keywords"], list)
    assert len(result["keywords"]) >= 2
    assert isinstance(result["trending"], bool)
    assert isinstance(result["trending_score"], float)

def test_tagging_quality_and_context():
    """Verify intelligent tagging extracts clean, context-aware concepts without noise words."""
    # Test 1: Space / ISRO
    f1, tags1 = classify_and_tag(
        title="ISRO launches communication satellite with PSLV rocket from Sriharikota",
        content="Indian space agency successfully achieved orbital insertion for scientific mission.",
        region="India"
    )
    assert f1 == "Technology & AI"
    assert "ISRO" in tags1 or "Satellite Launch" in tags1
    assert 2 <= len(tags1) <= 4

    # Test 2: Stock Market / Financial Markets
    f2, tags2 = classify_and_tag(
        title="Sensex crashes 1000 points as stock market plunges on global volatility",
        content="Equity investors saw heavy selloff as financial markets reacted to inflation data.",
        region="India"
    )
    assert f2 == "Finance & Economics"
    assert "Stock Market" in tags2 or "Sensex" in tags2
    assert 2 <= len(tags2) <= 4

    # Test 3: Weather Alert / Heavy Rainfall
    f3, tags3 = classify_and_tag(
        title="Heavy rainfall in Chennai triggers weather alert and waterlogging",
        content="Tamil Nadu coastal districts declared holiday amid cyclone warning and downpour.",
        region="Tamil Nadu"
    )
    assert "Heavy Rainfall" in tags3 or "Weather Alert" in tags3
    assert 2 <= len(tags3) <= 4

    # Test 4: Elections
    f4, tags4 = classify_and_tag(
        title="Election Commission announces assembly polls date and voter schedule",
        content="Political parties gearing up for state election battle with model code in effect.",
        region="India"
    )
    assert f4 == "Politics"
    assert "Elections" in tags4
    assert 2 <= len(tags4) <= 4

    # Ensure no generic stop words appear
    all_tags = tags1 + tags2 + tags3 + tags4
    for t in all_tags:
        assert t.lower() not in {"news", "latest", "update", "important", "breaking", "general", "article", "report"}

def test_tag_normalization_helper():
    """Verify tag cleaning and casing helper preserves acronyms and title casing."""
    assert clean_and_normalize_tag("#isro") == "ISRO"
    assert clean_and_normalize_tag("stock market") == "Stock Market"
    assert clean_and_normalize_tag("ai technology") == "AI Technology"
    assert is_valid_tag("ISRO") is True
    assert is_valid_tag("News") is False
    assert is_valid_tag("Update") is False

def test_user_registration_and_login(client):
    email = "testuser@example.com"
    password = "SecurePassword123!"
    
    # 1. Register
    reg_res = client.post("/api/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test Reader"
    })
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["email"] == email

    # 2. Login
    login_res = client.post("/api/auth/login", json={
        "email": email,
        "password": password
    })
    assert login_res.status_code == 200
    token = login_res.json()["access_token"]

    # 3. Check /me
    me_res = client.get("/api/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert me_res.status_code == 200
    assert me_res.json()["email"] == email

def test_standard_trending_news_feed(client):
    """
    Verify standard trending news feed returns articles without personal match percentage.
    All users receive the standard news feed.
    """
    res = client.get("/api/articles/trending")
    assert res.status_code == 200
    data = res.json()
    assert "items" in data
    assert len(data["items"]) > 0
    for item in data["items"]:
        assert item["match_score"] is None
        assert "english_title" in item
        assert "english_summary" in item
        assert "keywords" in item

def test_filtering_endpoints(client):
    """
    Verify region, language, and field filters work without personalization requirements.
    """
    # 1. Filter metadata endpoint
    meta_res = client.get("/api/articles/meta/filters")
    assert meta_res.status_code == 200
    meta = meta_res.json()
    assert "regions" in meta and len(meta["regions"]) > 0
    assert "languages" in meta and len(meta["languages"]) > 0
    assert "fields" in meta and len(meta["fields"]) > 0

    # 2. Filter by field
    field_res = client.get("/api/articles?field=Technology & AI")
    assert field_res.status_code == 200
    for item in field_res.json()["items"]:
        assert "technology" in item["field"].lower()
        assert item["match_score"] is None

    # 3. Filter by language
    lang_res = client.get("/api/articles?language=French")
    assert lang_res.status_code == 200
    for item in lang_res.json()["items"]:
        assert item["original_language"].lower() == "french"

    # 4. Filter by region
    reg_res = client.get("/api/articles?region=Europe")
    assert reg_res.status_code == 200
    for item in reg_res.json()["items"]:
        assert "europe" in item["region"].lower()
