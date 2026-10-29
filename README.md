# Multilingual News Digest

> Real-time global news aggregation, local Ollama LLM translation, executive summarization, and interest-graph personalization.

---

## 🌟 Overview

**Multilingual News Digest** is an intelligent news platform designed to dissolve language barriers. It ingests international journalism directly from non-English sources (e.g. *Le Monde*, *El País*, *Deutsche Welle*, *NHK World*, *Al Jazeera*), translates and summarizes articles into executive briefings via a **local Ollama LLM (`llama3.2`)**, and delivers them in a personalized **"For You"** feed driven by a **15-question onboarding interest questionnaire**.

All AI processing runs 100% locally on your machine via **Ollama**, ensuring complete data privacy, zero API costs, and full offline resilience.

---

## 🚀 Key Features

- **Local Ollama LLM Pipeline (`llama3.2`)**:
  - Automatically translates foreign articles into fluent English.
  - Generates executive bulleted briefings and contextual summaries.
  - Extracts structured metadata: Source Language, Continental Region, Subregion, Field/Category, Keywords, and Trending scores.
  - Configurable model (defaults to `llama3.2`, customizable via `OLLAMA_MODEL`).
  - Native JSON schema mode enforces clean structured outputs without hallucinations.
  - Offline/Dev fallback mode ensures instant functionality even if Ollama is starting up or temporarily offline.

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
│   │   ├── services/       # Scraper, Ollama LLM Pipeline, Recommendation Engine, Seed Data
│   │   ├── routers/        # Auth, Users, Articles, Ingest API endpoints
│   │   ├── config.py       # Pydantic Settings & environment variables
│   │   ├── database.py     # SQLite & PostgreSQL engine
│   │   └── main.py         # FastAPI application entrypoint
│   ├── tests/              # Pytest test suite
│   ├── requirements.txt    # Python dependencies
│   └── .env.example        # Environment template (Ollama config)
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
- **Ollama** installed on your system ([Download Ollama](https://ollama.com/download))

---

### 2. Ollama Local AI Setup

#### A. Install Ollama
- **Windows**: Download and run the installer from [ollama.com/download/windows](https://ollama.com/download/windows).
- **macOS**: Download from [ollama.com/download/mac](https://ollama.com/download/mac) or install via Homebrew: `brew install ollama`.
- **Linux**: Run `curl -fsSL https://ollama.com/install.sh | sh`.

#### B. Download the Recommended Model
Open a terminal and pull the lightweight `llama3.2` model (or `llama3.2:1b` for lower RAM):
```bash
ollama pull llama3.2
```

#### C. Start the Ollama Server
If not already running in the background as a service/desktop app:
```bash
ollama serve
```
Verify Ollama is reachable at `http://localhost:11434`:
```bash
# In PowerShell / Command Prompt / bash:
curl http://localhost:11434/api/tags
```

---

### 3. Backend Setup

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

# Configure environment variables (copy template):
# Windows:
copy .env.example .env
# macOS/Linux:
cp .env.example .env

# (Optional) Verify or change Ollama settings in .env:
# OLLAMA_BASE_URL=http://localhost:11434
# OLLAMA_MODEL=llama3.2

# Run the backend API server
uvicorn app.main:app --reload --port 8000
```

- Backend API: `http://127.0.0.1:8000`
- Interactive Swagger Docs: `http://127.0.0.1:8000/docs`
- Health check: `http://127.0.0.1:8000/` (returns Ollama connection and model status)

---

### 4. Frontend Setup

In a separate terminal:
```bash
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
Open `http://localhost:3000` in your browser.

---

## 🔧 Troubleshooting Ollama

| Issue | Cause | Solution |
| :--- | :--- | :--- |
| `connection_refused` / Server unreachable | Ollama daemon is not running | Run `ollama serve` in a terminal or launch the Ollama desktop app. |
| `model_not_found` | The requested model is not downloaded | Run `ollama pull llama3.2` in your terminal. |
| High RAM/CPU usage during ingestion | `llama3.2` 3B default is too heavy for older hardware | Change `OLLAMA_MODEL=llama3.2:1b` in `.env` and run `ollama pull llama3.2:1b`. |
| Port 11434 already in use | Another process is bound to port 11434 | Check running processes with `Get-Process ollama` (Windows) or `pkill ollama` (macOS/Linux). |

*Note: If Ollama is offline or unavailable, the backend automatically activates the built-in smart heuristic fallback engine so the application remains fully functional.*

---

## 🧪 Running Tests

To run the automated backend test suite:

```bash
cd backend
.\venv\Scripts\pytest -o pythonpath=. tests -v
```

Output:
```
tests/test_api.py::test_health_check PASSED
tests/test_api.py::test_onboarding_questions_count PASSED
tests/test_api.py::test_ollama_status_check PASSED
tests/test_api.py::test_llm_pipeline_attributes_validation PASSED
tests/test_api.py::test_tagging_quality PASSED
tests/test_api.py::test_interest_graph_calculation PASSED
tests/test_api.py::test_user_registration_and_login PASSED
tests/test_api.py::test_percentage_matching_rules PASSED
tests/test_api.py::test_filtering_endpoints PASSED
====== 9 passed in 3.10s ======
```

---

## 📜 License
MIT
