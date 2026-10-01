import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app import models
from app.main import app
from app.services.llm_pipeline import llm_pipeline
from app.services.quiz_data import ONBOARDING_QUESTIONS, calculate_interest_graph
from app.services.seed_data import seed_database
from app.services.tagging import classify_and_tag
from app.schemas.profile import OnboardingAnswer

from sqlalchemy.pool import StaticPool

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
    assert data["llm_provider"] == "NVIDIA Nemotron"

def test_onboarding_questions_count(client):
    response = client.get("/api/onboarding/questions")
    assert response.status_code == 200
    data = response.json()
    assert data["total_questions"] == 15
    assert len(data["questions"]) == 15

def test_llm_pipeline_attributes_validation():
    """Verify LLM pipeline strictly produces all 6 core attributes plus English content."""
    mock_title = "AI Traffic Cameras Mistake Fine Controversy in State"
    mock_content = "Traffic authorities reported that newly installed artificial intelligence traffic cameras experienced technical calibration disputes."
    
    result = llm_pipeline.process_article(mock_title, mock_content, "Divya Marathi", expected_region="Maharashtra", expected_language="Marathi")
    
    required_keys = ["language", "region", "subregion", "field", "keywords", "trending", "trending_score", "english_title", "english_summary"]
    for key in required_keys:
        assert key in result, f"Missing required key: {key}"
    
    assert isinstance(result["keywords"], list)
    assert len(result["keywords"]) >= 1
    assert isinstance(result["trending"], bool)
    assert isinstance(result["trending_score"], float)

def test_tagging_quality():
    """Verify intelligent tagging extracts clean concepts without noise words."""
    field, tags = classify_and_tag(
        title="Dr Pallakshi Prasad NEET PG Topper AIR AFMC DPS Hyderabad Success Story",
        content="Dr Pallakshi Prasad achieved All India Rank 1 in NEET PG examination from Armed Forces Medical College.",
        region="India"
    )
    assert field == "Education & Jobs"
    assert any("NEET PG" in t for t in tags)
    # Ensure no fragmented noise words like 'During', 'Neither', 'Youre'
    for t in tags:
        assert t.lower() not in {"during", "mean", "youre", "neither", "side", "align", "took", "days"}

def test_interest_graph_calculation():
    """Verify onboarding answers map correctly to normalized interest graph."""
    answers = [
        OnboardingAnswer(question_id=1, selected_option_ids=["q1_west"]),
        OnboardingAnswer(question_id=6, selected_option_ids=["q6_tech"])
    ]
    graph = calculate_interest_graph(answers)
    weights = graph["interest_weights"]
    
    assert "region:Maharashtra" in weights or "region:Gujarat" in weights
    assert "field:Technology & AI" in weights
    assert 0.0 <= weights["field:Technology & AI"] <= 1.0

def test_user_registration_and_login(client):
    email = "testuser@example.com"
    password = "SecurePassword123!"
    
    # 1. Register
    reg_res = client.post("/api/auth/register", json={
        "email": email,
        "password": password,
        "full_name": "Test Diplomat"
    })
    assert reg_res.status_code == 201
    reg_data = reg_res.json()
    assert "access_token" in reg_data
    assert reg_data["email"] == email
    assert reg_data["completed_onboarding"] is False

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

def test_percentage_matching_rules(client):
    """
    CRITICAL TEST FOR ISSUE 3:
    1. Unauthenticated users NEVER receive match_score.
    2. Authenticated user who hasn't completed quiz receives match_score == None.
    3. Authenticated user who completed quiz receives populated match_score.
    """
    # 1. Unauthenticated user on foryou and filter
    guest_fy = client.get("/api/articles/foryou")
    assert guest_fy.status_code == 200
    for item in guest_fy.json()["items"]:
        assert item["match_score"] is None

    guest_filter = client.get("/api/articles?region=Europe")
    assert guest_filter.status_code == 200
    for item in guest_filter.json()["items"]:
        assert item["match_score"] is None

    # 2. Registered user who has NOT taken quiz
    reg = client.post("/api/auth/register", json={
        "email": "noquiz_user@example.com",
        "password": "Password123!",
        "full_name": "No Quiz User"
    })
    token = reg.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    noquiz_fy = client.get("/api/articles/foryou", headers=headers)
    assert noquiz_fy.status_code == 200
    for item in noquiz_fy.json()["items"]:
        assert item["match_score"] is None

    noquiz_filter = client.get("/api/articles?field=Technology & AI", headers=headers)
    assert noquiz_filter.status_code == 200
    for item in noquiz_filter.json()["items"]:
        assert item["match_score"] is None

    # 3. User completes quiz
    answers = [
        {"question_id": 1, "selected_option_ids": ["q1_west"]},
        {"question_id": 6, "selected_option_ids": ["q6_tech"]},
        {"question_id": 12, "selected_option_ids": ["q12_western"]}
    ]
    sub = client.post("/api/onboarding/submit", json={"answers": answers}, headers=headers)
    assert sub.status_code == 200
    assert sub.json()["completed_onboarding"] is True

    # 4. Now user SHOULD receive match_score
    quiz_fy = client.get("/api/articles/foryou", headers=headers)
    assert quiz_fy.status_code == 200
    fy_items = quiz_fy.json()["items"]
    assert len(fy_items) > 0
    for item in fy_items:
        assert item["match_score"] is not None
        assert 0.0 <= item["match_score"] <= 1.0

def test_filtering_endpoints(client):
    """
    CRITICAL TEST FOR ISSUE 1:
    Verify region, language, and field filters work.
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
