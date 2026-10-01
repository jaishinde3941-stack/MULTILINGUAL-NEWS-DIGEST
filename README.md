# Multilingual News Digest

> Real-time global news aggregation, NVIDIA Nemotron LLM translation, executive summarization, and interest-graph personalization.

---

## 🌟 Overview

**Multilingual News Digest** is an intelligent news platform designed to dissolve language barriers. It ingests international journalism directly from non-English sources (e.g. *Le Monde*, *El País*, *Deutsche Welle*, *NHK World*, *Al Jazeera*), translates and summarizes articles into executive briefings via **NVIDIA Nemotron**, and delivers them in a personalized **"For You"** feed driven by a **15-question onboarding interest questionnaire**.

---

## 🚀 Key Features

- **NVIDIA Nemotron LLM Pipeline**:
  - Automatically translates foreign articles into fluent English.
  - Generates executive bulleted briefings and contextual summaries.
  - Extracts structured metadata: Source Language, Continental Region, Subregion, Field/Category, Keywords, and Trending scores.
  - Offline/Dev fallback mode ensures instant functionality even before configuring an API key.

- **15-Question Onboarding Interest Graph**:
  - Calibrates user preferences across 3 key dimensions:
    1. **Geographic Priorities (Q1–Q5)**: Europe, Asia-Pacific, Latin America, Middle East, Regional Blocs.
    2. **Topical Domains (Q6–Q11)**: AI & Tech, Geopolitics, Global Finance, Clean Energy, Culture & Ideas, Biotech.
    3. **Language & Editorial Dynamics (Q12–Q15)**: Source languages (French, Spanish, German, Japanese, Arabic), executive bullet density, and feed pacing.
  - Generates normalized affinity weights saved directly to the user profile.

- **Dual Feed Architecture**:
  - **For You**: Re-ranked in real time using the user's Interest Graph affinity scores.
  - **Trending**: High-velocity global breaking developments and viral geopolitical movements.
  - **Dynamic Filters**: Real-time cross-section filtering by Region, Language, Topic, and keyword search.

- **Bilingual Reader & Speech Engine**:
  - Full article reader modal with tabbed views: English Translation, Original Source Text, and Side-by-Side comparison.
  - Integrated Text-to-Speech audio reader so users can listen to translated foreign news.

- **Authentication & Bookmarking**:
  - FastAPI JWT Bearer token authentication with bcrypt password hashing.
  - One-click article bookmarking.

---

## 🏗️ Architecture

```
multilingual_news_digest/
├── backend/
│   ├── app/
│   │   ├── auth/           # Password hashing & JWT dependencies
│   │   ├── models/         # SQLAlchemy models (User, Profile, Article, Bookmark)
│   │   ├── schemas/        # Pydantic v2 schemas
│   │   ├── services/       # Scraper, LLM Pipeline, Recommendation Engine, Seed Data
│   │   ├── routers/        # Auth, Users, Articles, Ingest API endpoints
│   │   ├── config.py       # Pydantic Settings & environment variables
│   │   ├── database.py     # SQLite & PostgreSQL engine
│   │   └── main.py         # FastAPI application entrypoint
│   ├── tests/              # Pytest test suite
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment template
│
└── frontend/
    ├── app/                # Next.js 15 App Router (layout, globals.css, page.tsx)
    ├── components/         # Header, HeroStats, FilterBar, ArticleCard, ArticleReaderModal, OnboardingModal, AuthModal, ProfileDrawer
    ├── lib/                # Typed API client
    └── package.json        # Next.js + Tailwind CSS v4 dependencies
```

---

## 🛠️ Quickstart Guide

### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.14)
- **Node.js 18+** & **npm**

### 2. Backend Setup
```bash
cd backend

# Create virtual environment and activate
python -m venv venv
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Set your NVIDIA NIM API Key in .env:
# NVIDIA_API_KEY=your_key_here
# NVIDIA_MODEL=nvidia/llama-3.1-nemotron-70b-instruct

# Run the backend API server
uvicorn app.main:app --reload --port 8000
```
Backend API will be accessible at `http://127.0.0.1:8000` with interactive Swagger docs at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 🧪 Running Tests

To run the automated backend test suite verifying authentication, the 15-question onboarding scoring, LLM metadata output, and feed endpoints:

```bash
cd backend
.\venv\Scripts\pytest -o pythonpath=. tests -v
```
Output:
```
tests/test_api.py::test_health_check PASSED
tests/test_api.py::test_onboarding_questions_count PASSED
tests/test_api.py::test_llm_pipeline_attributes_validation PASSED
tests/test_api.py::test_interest_graph_calculation PASSED
tests/test_api.py::test_user_registration_and_login PASSED
tests/test_api.py::test_articles_endpoints PASSED
====== 6 passed in 2.92s ======
```

---

## 📜 License
MIT
