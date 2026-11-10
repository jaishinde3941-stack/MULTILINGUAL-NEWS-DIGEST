# अख़बार वाले — Global News Briefing in Clear English

> A premium, production-grade digital newspaper platform that synthesizes multilingual foreign journalism into factual, fluent English executive briefings powered by local AI (**Ollama / Llama 3.2**).

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/backend-FastAPI-009688.svg)](https://fastapi.tiangolo.com/)
[![Next.js 16](https://img.shields.io/badge/frontend-Next.js%2016%20(Turbopack)-black.svg)](https://nextjs.org/)
[![Tailwind CSS v4](https://img.shields.io/badge/styling-Tailwind%20v4-38B2AC.svg)](https://tailwindcss.com/)
[![Ollama](https://img.shields.io/badge/AI-Ollama%20(Llama%203.2)-orange.svg)](https://ollama.com/)
[![Tests](https://img.shields.io/badge/tests-41%20passing-brightgreen.svg)]()

---

## 🌟 Overview

**अख़बार वाले** (*"The Newspaper Vendors"*) is a modern international news reading platform designed to dissolve linguistic barriers in global journalism. 

The platform continuously aggregates primary foreign journalism in diverse regional and international languages (**Marathi, Telugu, Gujarati, Hindi, Tamil, Malayalam, French, Spanish, German, Japanese, Arabic**), feeds them through an on-device local AI pipeline using **Ollama with Llama 3.2**, and delivers authoritative **English headlines** and **English executive briefings (~80–120 words)**.

Rather than presenting machine-translated verbatim text or cluttered dashboards, **अख़बार वाले** adopts the typographic elegance, discipline, and restraint of world-class digital broadsheets (*The New York Times*, *The Financial Times*, *The Guardian*).

All AI inference runs **100% locally on your machine via Ollama**, ensuring complete privacy, zero third-party API token costs, and full offline resilience.

---

## 🚀 Key Features & Implementation

### 1. Local AI Summarization Pipeline (Ollama / Llama 3.2)
- **Executive Synthesis**: Generates crisp, factual English headlines and executive summaries directly from non-English articles without translating entire texts.
- **Strict Grammar & JSON Schema**: Uses Ollama's structured schema format to guarantee deterministic, non-empty outputs without hallucinations or generic filler.
- **Script & Purity Detection**: Distinguishes Devanagari Hindi vs. Marathi lexical markers, Dravidian Telugu & Tamil, and ensures English output purity (≥70% Latin characters).
- **Hierarchical Chunking**: Automatically fragments long-form investigative journalism (>2,000 words) to fit model context windows smoothly.
- **Hardware & VRAM Protection**: Thread semaphores regulate inference concurrency to prevent GPU memory exhaustion.
- **Resilient Fallback**: Automatically activates a smart heuristic summarization engine if Ollama is starting up or temporarily offline.
- **Reprocessing Controls**: In-modal and global batch re-summarization buttons (`POST /api/articles/{id}/reprocess`) with bounded network retry logic.

### 2. Active / Reserve 100-Article Batch Architecture
- **Continuous Ingestion**: Collects 100 fresh multilingual articles per cycle from vetted international and regional RSS dispatches.
- **Pool Partitioning**: Partitions ingested stories into **50 Active Articles** (currently rendered on the feed) and **50 Reserve Articles** (pre-summarized and held in reserve).
- **Sub-50ms Rotation**: 1-click **"Ingest News"** rotation (`POST /api/ingest/batch-rotate`) instantly swaps the active batch with the prepared reserve batch.
- **Autonomous Background Refill**: Rotating immediately kicks off an asynchronous background refill job (`POST /api/ingest/refill-reserve`) to replenish the reserve pool without blocking user reading.
- **Live Header Indicator**: The navigation bar displays live batch readiness status, e.g., `Ingest News (50/50)`.

### 3. Editorial Typography System
Loaded reliably via `next/font/google` and Google Fonts fallbacks:
- **Primary Interface**: **Inter** (weights 400, 500, 600, 700) for navigation (14px), buttons (14px), filter labels (12px), card headlines (19–20px bold), and executive summaries (14–15px).
- **Editorial Headlines**: **Newsreader Serif** for broadsheet hero headings (44–48px, weight 600) and article modal headlines (36–40px, weight 650).
- **Brand Identity**: **Noto Sans Devanagari** (weight 800) for the Hindi platform title **अख़बार वाले**.

### 4. Semantic Design Token System (Light & Dark)
A cohesive design-token architecture using semantic CSS variables in `globals.css`:
- **Light Theme**: Warm newspaper off-white background (`#F7F7F5`), crisp white cards (`#FFFFFF`), secondary panel surfaces (`#F1F1EF`), high-contrast near-black typography (`#191919`), muted dateline grey (`#707070`), subtle hairline borders (`#E6E6E3`), and editorial red accents (`#D92D35`).
- **Dark Theme**: Deep neutral charcoal background (`#111318`), elevated dark surface (`#191C23`), secondary surface (`#20242D`), soft white typography (`#F5F5F5`), muted metadata grey (`#A1A1AA`), dark borders (`#2C303A`), and night red accents (`#F05252`).
- **Instant Switching**: Theme toggles update immediately across cards, dropdowns, inputs, and modals with `localStorage` persistence (`akhbar_theme`).

### 5. Refined Broadsheet Navigation & Hero Section
- **Sticky Top Bar (68px)**: Centered layout (max 1300px) featuring the Hindi brand title with a red accent mark, hairline separator, uppercase subtitle `GLOBAL STORIES · CLEAR ENGLISH`, navigation tabs (`Trending`, `Explore`, `Search`), standardized Ingest button with progress counter, and theme toggle.
- **Understated Editorial Hero**: Real-time uppercase dateline (`SUNDAY, NOVEMBER 01, 2026`), Newsreader headline `Your Daily News Briefing`, subtitle `Global stories. Clear English. One place.`, and live article counter (`50 Stories`).
- **Compact Search & Filter Panel**:
  - Full-width search input (42px) with live result count (`Showing 50 articles`).
  - Three equal-width dropdowns (`REGION`, `ORIGINAL LANGUAGE`, `CATEGORY`) with custom SVG chevrons, smooth focus rings, and zero native OS styling artifacts.

### 6. Responsive News Card Grid
- **Broadsheet Layout**: Responsive 3-column desktop, 2-column tablet, and 1-column mobile grid with 24px gaps (`gap-6`).
- **16:9 Editorial Media**: Full-width cover images with smooth fade-in loading and subtle 1.02 hover zoom limit.
- **Clear Information Hierarchy**: Editorial category and region kicker, 19–20px bold headlines (max 3 lines), 14–15px executive summaries (3 lines), and publication date.
- **Quick Controls**: Bookmark toggle, direct external source link, and "Read Full" modal trigger.

### 7. Expanded Article Detail Modal
- **Cinematic Reading Experience**: Centered 850px modal with 85vh max-height, 16px radius, and soft-focus background dissolve (`backdrop-blur-md`).
- **Compact Header Toolbar**: Publisher name, language indicator (`Marathi → English`), date, and 32px controls:
  - **Listen / Voice Reader**: Web Speech API text-to-speech for the English headline and summary with animated wave feedback.
  - **Copy**: One-click clipboard copy of the headline, executive summary, and attribution with "Copied" feedback.
  - **Source Link**: Direct link opening the authentic publisher URL.
  - **Close**: Accessible button with `X` icon and `Escape` key handler.
- **Prominent Newsreader Headline**: Set in 36–40px serif typography as the central commanding element.
- **Expandable Original Headline**: The vernacular headline is hidden by default and cleanly revealed via a dynamic text button: `"View Original Headline (Marathi)"`.
- **Central Executive Summary**: Distinct `ENGLISH EXECUTIVE SUMMARY` section in Inter 17px with 1.75 line-height, comfortable `max-w-prose` width, and word count metadata.
- **Compact Source Footer**: Byline displaying publication name, original language, region, and `Read Full Story` link.
- **Contextual Tags**: 2–4 relevant uppercase tags (e.g. `ELECTION`, `LEADERSHIP`, `ECONOMY`, `TECHNOLOGY`, `DIPLOMACY`) with neutral badges and a subtle red accent on the primary tag.

### 8. Zero-CLS Fluidity & Smooth Micro-Interactions
- **`scrollbar-gutter: stable`**: Prevents the entire 1300px layout from horizontally jumping ~16px when modals open or close on Windows.
- **Fixed Shimmer Progress Line**: Replaced layout-shifting inline progress divs with a zero-height fixed progress line (`h-[2px]`) right beneath the header.
- **GPU-Accelerated Card Elevation**: Smooth transforms (`transform-gpu will-change-transform`) and spring easing curves (`cubic-bezier(0.16, 1, 0.3, 1)`) for 60/120fps scrolling.
- **Custom Floating Scrollbars**: Rounded pill scrollbars with transparent borders.

---

## 🏗️ System Architecture

```
multilingual_news_digest/
├── backend/
│   ├── app/
│   │   ├── auth/           # Password hashing & JWT dependencies
│   │   ├── models/         # SQLAlchemy models (User, Profile, Article, Bookmark, History)
│   │   ├── schemas/        # Pydantic v2 schemas
│   │   ├── services/       # Scraper, Ollama LLM Pipeline, Ingestion Manager, Dedup, Tagging
│   │   ├── routers/        # Articles, Ingest, Auth, Users endpoints
│   │   ├── config.py       # Pydantic Settings & environment variables
│   │   ├── database.py     # SQLite & PostgreSQL database engine
│   │   └── main.py         # FastAPI application entrypoint
│   ├── tests/              # Pytest test suite (41 tests)
│   ├── requirements.txt    # Python backend dependencies
│   ├── run_server.py       # Backend process manager
│   ├── run_backend.bat     # Windows backend launcher
│   └── .env.example        # Environment configuration template
│
├── frontend/
│   ├── app/
│   │   ├── layout.tsx      # Root layout with font loading (Inter, Newsreader, Noto Sans Devanagari)
│   │   ├── globals.css     # Semantic tokens, typography classes, smooth animations
│   │   └── page.tsx        # Main news grid, search orchestration, batch rotation
│   ├── components/
│   │   ├── Header.tsx             # 68px sticky navigation bar with batch progress counter
│   │   ├── HeroStats.tsx          # Understated editorial hero with dynamic dateline
│   │   ├── FilterBar.tsx          # 2-row search and 3-column filter controls with custom SVG chevrons
│   │   ├── ArticleCard.tsx        # 16:9 news card with GPU hover elevation and image fade-in
│   │   ├── ArticleReaderModal.tsx # Redesigned editorial modal with Web Speech TTS and dynamic toggle
│   │   ├── AuthModal.tsx          # Sign-in & registration dialog
│   │   └── ProfileDrawer.tsx      # User profile slide-over drawer
│   ├── lib/                       # Typed TypeScript API client
│   ├── test_modal.mjs             # Component test suite
│   ├── test_interactive_modal.mjs # Live multilingual test suite across 6 languages
│   └── package.json               # Next.js 16 + Tailwind CSS v4 dependencies
│
├── start.bat               # One-click Windows startup orchestrator
├── start.ps1               # PowerShell cross-platform runner
├── stop.bat                # Graceful service shutdown script
└── stop.ps1                # PowerShell shutdown script
```

---

## 🛠️ Quickstart Guide

### ⚡ One-Click Startup (Recommended)

To launch all 3 services (**Ollama**, **FastAPI Backend**, and **Next.js Frontend**) automatically:

#### Option A: Windows Batch Launcher
Double-click **`start.bat`** (or execute `start.bat` in Command Prompt).
- Automatically verifies Node.js, Python, and Ollama.
- Creates virtual environments and installs missing packages automatically.
- Reuses already-running instances without creating duplicate processes.
- Verifies if the AI model (`llama3.2`) is installed.
- Opens your default web browser to `http://localhost:3000`.

#### Option B: PowerShell Runner
```powershell
# Standard mode (separate console windows)
.\start.ps1

# Single-Terminal mode (background job management)
.\start.ps1 -SingleTerminal
```

#### Stopping Services
Double-click **`stop.bat`** or run `.\stop.ps1` in PowerShell to immediately free ports 8000, 3000, and related background processes.

---

### Manual Setup Step-by-Step

#### 1. Prerequisites
- **Python 3.10+** (Tested on Python 3.14)
- **Node.js 18+** & **npm**
- **Ollama** installed on your system ([Download Ollama](https://ollama.com/download))

---

#### 2. Local AI Setup (Ollama)

1. **Install Ollama**: Follow instructions for Windows, macOS, or Linux at [ollama.com](https://ollama.com).
2. **Pull the Model**:
   ```bash
   ollama pull llama3.2
   ```
   *(For systems with constrained RAM/VRAM, use `ollama pull llama3.2:1b`)*
3. **Start the Service**:
   ```bash
   ollama serve
   ```
   Verify readiness at `http://localhost:11434`:
   ```bash
   curl http://localhost:11434/api/tags
   ```

---

#### 3. Backend Setup

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

# Copy environment configuration
copy .env.example .env    # Windows
cp .env.example .env      # macOS/Linux

# Start FastAPI backend
python run_server.py
```

- **API Base URL**: `http://127.0.0.1:8000`
- **Swagger Documentation**: `http://127.0.0.1:8000/docs`
- **Batch Status Endpoint**: `http://127.0.0.1:8000/api/ingest/batch-status`

---

#### 4. Frontend Setup

In a separate terminal window:
```bash
cd frontend

# Install dependencies
npm install

# Start Next.js development server
npm run dev
```
Open **`http://localhost:3000`** in your browser.

---

## 🧪 Testing & Verification

### 1. Backend Test Suite (Pytest)
Runs 41 comprehensive tests covering REST endpoints, batch rotation, scraper HTML cleaning, dedup hashing, and multilingual summarization:

```bash
cd backend
.\venv\Scripts\pytest tests -v
```

Output:
```
tests/test_api.py ......................... [ 19%]
tests/test_batch_rotation.py .............. [ 51%]
tests/test_multilingual_summary.py ........ [ 90%]
tests/test_scraper.py ..................... [100%]
====================== 41 passed in 106.48s ======================
```

### 2. Frontend Multilingual & Modal Test Suite (Node.js)
Validates rendering, dynamic original-headline toggling, executive summary formatting, word counts, and context tags against live articles across all 6 supported languages:

```bash
# Verify component rendering and fallbacks
node frontend/test_modal.mjs

# Verify live articles from database (Telugu, Marathi, Tamil, Malayalam, Hindi, Gujarati)
node frontend/test_interactive_modal.mjs
```

Output:
```
=== Premium Editorial Modal Test Suite ===
Retrieved 30 live articles from backend API.
Found live languages: Telugu, Marathi, Tamil, Malayalam, Hindi, Gujarati

Testing Real Article in Telugu: ID #660 (Telugu One India) -> PASSED
Testing Real Article in Marathi: ID #661 (Divya Marathi) -> PASSED
Testing Real Article in Tamil: ID #663 (Vikatan) -> PASSED
Testing Real Article in Malayalam: ID #664 (Malayalam One India) -> PASSED
Testing Real Article in Hindi: ID #665 (ABP Live) -> PASSED
Testing Real Article in Gujarati: ID #670 (Sandesh) -> PASSED
Testing Tag Fallback and Synthesis for sparse article -> PASSED
==========================================
ALL REAL ARTICLE AND UNIT TESTS PASSED!
==========================================
```

### 3. Frontend Production Build
```bash
npm --prefix frontend run build
```
Compiles with Turbopack in ~500ms with **0 errors and 0 warnings**.

---

## 🔧 Configuration & Environment Variables

Key parameters configured in `backend/.env`:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama service endpoint |
| `OLLAMA_MODEL` | `llama3.2` | Configured LLM model (`llama3.2`, `llama3.2:1b`) |
| `DATABASE_URL` | `sqlite:///./news_digest.db` | SQLite database file location |
| `BATCH_SIZE` | `50` | Target size for active and reserve pools |
| `SECRET_KEY` | `your-secret-key-change-in-production` | JWT signing secret |
| `PORT` | `8000` | FastAPI server port |

---

## 📜 Editorial Credibility & AI Ethics
- **English Synthesis Only**: The platform generates concise executive briefings (~80–120 words) and English headlines; it does not present machine translation as verbatim full-article texts.
- **Anti-Hallucination Constraints**: Preserves critical names, dates, numbers, geographical entities, and quoted statements without inventing unsupported claims.
- **Source Attribution**: Every story features a persistent citation and an active external link directing readers to the original foreign-language publisher.

---

## 📄 License
This project is open-source software licensed under the **MIT License**.
