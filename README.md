# 🚀 Innovation Scout — R&D Intelligence Engine

> **Scan the frontier of science and markets in seconds.** Innovation Scout is a multi-agent AI engine that performs 3-way parallel scans across academic literature, live web intelligence, and a local vector knowledge base — then pauses for human review before synthesising a publication-grade research briefing.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-innovation--scout--ui.onrender.com-6366f1?style=for-the-badge&logo=render&logoColor=white)](https://innovation-scout-ui.onrender.com/)

---

## ✨ What It Does

**Innovation Scout** is an advanced multi-agent R&D intelligence platform built for technology scouts, research directors, and scientists. Given a single high-level research question it:

1. **Parses & expands** the query into precise academic and market keywords using Gemini 2.5 Flash.
2. **Scans 3 sources in parallel** — arXiv academic papers, a local pgvector knowledge base, and live web results via Google Search grounding.
3. **Ranks & scores** every discovered asset on a strict 0.0–1.0 relevance and credibility scale with AI-generated engineering rationales.
4. **Pauses for human review** (HITL gate) — letting you approve, inspect, or reject gathered intelligence before the final report is compiled.
5. **Synthesises a markdown briefing** — a polished, citation-rich R&D report ready to share.

New arXiv papers and live web articles are **automatically embedded and stored** in the pgvector database, continuously enriching the knowledge base for future queries.

---

## 🏗️ Architecture Diagram

```mermaid
graph TD
    subgraph React Frontend["⚛️ React + Tailwind Frontend (Static Site)"]
        UI[User Input: Research Query]
        REV[Human-in-the-Loop Review Screen]
        REP[Final R&D Synthesis Report]
    end

    subgraph FastAPI Backend["⚡ FastAPI Backend (Docker)"]
        API_S[POST /search]
        API_A[POST /approve]
    end

    subgraph LangGraph["🧠 LangGraph State Machine"]
        START((START))
        PARSER[Query Parser Agent<br>gemini-2.5-flash]
        SEARCH[Parallel Searcher Agent<br>ThreadPoolExecutor]
        RANKER[Ranker Agent<br>gemini-2.5-flash]
        HITL[Human Review Gate<br>MemorySaver Checkpoint]
        REPORTER[Reporter Agent<br>gemini-2.5-flash]
        END((END))
    end

    subgraph Sources["📚 Knowledge Sources"]
        ARXIV[arXiv API]
        PGV[pgvector DB<br>all-MiniLM-L6-v2]
        WEB[Google Web Search<br>Gemini Grounding]
    end

    UI --> API_S --> START
    START --> PARSER
    PARSER -->|Refined Query & Keywords| SEARCH

    SEARCH ==>|Thread 1| ARXIV
    SEARCH ==>|Thread 2| PGV
    SEARCH ==>|Thread 3| WEB

    ARXIV -.->|Auto-Ingest| PGV
    WEB -.->|Auto-Ingest| PGV

    SEARCH -->|Raw Combined Results| RANKER
    RANKER -->|Ranked & Scored Results| HITL

    HITL -->|State Paused| REV
    REV -->|Approve / Reject| API_A --> HITL

    HITL -->|If Approved| REPORTER
    REPORTER -->|Markdown Briefing| END
    END --> REP
```

---

## 🛠️ Tech Stack

### Backend
![Python](https://img.shields.io/badge/Python_3.10+-3776AB?style=flat-square&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=flat-square&logo=fastapi&logoColor=white)
![LangGraph](https://img.shields.io/badge/LangGraph-0D0D0D?style=flat-square&logo=langchain&logoColor=white)
![Google Gemini](https://img.shields.io/badge/Gemini_2.5_Flash-4285F4?style=flat-square&logo=google&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL_pgvector-336791?style=flat-square&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=flat-square&logo=docker&logoColor=white)

### Frontend
![React](https://img.shields.io/badge/React_19-61DAFB?style=flat-square&logo=react&logoColor=black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=flat-square&logo=typescript&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS_v4-06B6D4?style=flat-square&logo=tailwindcss&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=flat-square&logo=vite&logoColor=white)

### Deployment
![Render](https://img.shields.io/badge/Render-46E3B7?style=flat-square&logo=render&logoColor=black)
![Supabase](https://img.shields.io/badge/Supabase_pgvector-3ECF8E?style=flat-square&logo=supabase&logoColor=white)

---

## 📸 Screenshots

| Search & Query | Agent Scanning | HITL Review |
|:-:|:-:|:-:|
| ![Search stage](https://raw.githubusercontent.com/AayushShah-904/innovation-scout/refs/heads/main/assets/screenshot_search_stage.png) | ![Scanning stage](https://raw.githubusercontent.com/AayushShah-904/innovation-scout/refs/heads/main/assets/screenshot_scanning_stage.png) | ![HITL review stage](https://raw.githubusercontent.com/AayushShah-904/innovation-scout/refs/heads/main/assets/screenshot_review_stage.png) |

> 💡 Try it live at **[innovation-scout-ui.onrender.com](https://innovation-scout-ui.onrender.com/)**

---

## 📁 Project Structure

```text
innovation-scout/
├── agents/
│   ├── query_parser.py     # LLM node: transforms raw queries into structured keywords
│   ├── searcher.py         # Multi-threaded parallel search across arXiv, DB & Web
│   ├── ranker.py           # AI evaluator scoring relevance & credibility (0.0–1.0)
│   └── reporter.py         # Final synthesis node generating markdown briefing reports
├── graph/
│   ├── pipeline.py         # LangGraph state graph assembly, compilation & checkpointer
│   └── state.py            # TypedDict defining shared state across all agent nodes
├── hitl/
│   └── human_review.py     # HITL checkpoint pause node
├── tools/
│   ├── arxiv_tool.py       # Wrapper for querying the arXiv academic paper API
│   ├── init_db.py          # PostgreSQL table initialisation & pgvector extension setup
│   ├── vector_store.py     # sentence-transformers embedding & pgvector cosine search
│   └── web_search_tool.py  # Gemini-powered live web search with Google grounding
├── frontend/               # React + TypeScript + Tailwind CSS SPA
│   └── src/
│       ├── App.tsx          # Main application shell & routing
│       ├── components/      # Reusable UI components
│       └── hooks/           # Custom React hooks
├── main.py                 # FastAPI backend — session management & graph execution
├── Dockerfile              # Docker image for the FastAPI backend
├── docker-compose.yml      # Local pgvector database container
├── render.yaml             # Render Blueprint (deploys API + static frontend)
└── requirements.txt        # Python dependencies
```

---

## ⚙️ How to Run Locally

### Prerequisites
- **Python 3.10+**
- **Node.js 18+** & npm
- **Docker & Docker Compose** (for the local pgvector database)
- **Google Gemini API Key** (access to `gemini-2.5-flash` + Google Search grounding)

---

### 1 · Clone & create virtual environment

```bash
git clone https://github.com/your-username/innovation-scout.git
cd innovation-scout

python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 2 · Configure environment variables

Copy `.env.example` to `.env` and fill in your keys:

```bash
cp .env.example .env
```

```env
# .env
GEMINI_API_KEY=your_gemini_api_key_here
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/innovationscout
```

### 3 · Start the local vector database

```bash
docker-compose up -d
```

Verify the container is healthy on port `5432`, then initialise the schema:

```bash
python tools/init_db.py
# Expected: Database initialized successfully
```

### 4 · Start the FastAPI backend

```bash
python main.py
# API available at http://127.0.0.1:8000
# Interactive docs at http://127.0.0.1:8000/docs
```

### 5 · Start the React frontend

Open a **new terminal**:

```bash
cd frontend
npm install
npm run dev
# Frontend available at http://localhost:5173
```

---

## 🔌 API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/search` | Initiate a new LangGraph research session |
| `POST` | `/approve` | Submit human review decision (approve / reject) |
| `GET` | `/` | Health check |

**`POST /search`**
```json
{ "query": "eco-friendly bio-plastics for protective phone cases" }
```
Returns: `session_id`, expanded keywords, and ranked research results.

**`POST /approve`**
```json
{ "session_id": "uuid", "approve": true }
```
Returns: final compiled markdown briefing report.

---

## 🧪 Testing Individual Agents

You can independently verify each pipeline node:

```bash
python agents/query_parser.py   # Query Parser Agent
python agents/searcher.py       # 3-Way Parallel Searcher
python agents/ranker.py         # Ranker & Credibility Scorer
python graph/pipeline.py        # Full LangGraph flow + saves graph_flowchart.png
```

---

## 🌐 Live Demo

**[https://innovation-scout-ui.onrender.com/](https://innovation-scout-ui.onrender.com/)**

> The live demo runs the React frontend as a static site on Render, connected to a FastAPI backend deployed via Docker. The vector database is hosted on Supabase.

---

## 📄 License

This project is licensed under the **MIT License**. See the `LICENSE` file for details.
