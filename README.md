# AI Placement Analyzer (Production-Ready RAG)

> **Understand Your Resume. Match Your Dream Role.**  
> An evidence-first, grounded Retrieval-Augmented Generation (RAG) platform that audits candidate resumes against job descriptions, identifies verifiable skill matches, transparently highlights qualification gaps, generates prioritized preparation roadmaps, and formulates role-specific interview questions.

---

## 1. Project Overview & Problem Statement

### The Problem
Traditional placement preparation tools suffer from two critical flaws:
1. **Superficial Keyword Density Checkers**: Rely solely on raw string occurrences, rewarding candidates who spam keywords into their resume while penalizing those who express qualifications using authentic engineering terminology.
2. **Ungrounded "Wrapper" Chatbots**: Suffer from LLM hallucinations, generating false positives (assuming a candidate knows a technology simply because they know a related library), fabricating citations, or inventing percentages with zero mathematical transparency.

### The Solution: AI Placement Analyzer
AI Placement Analyzer implements an enterprise-grade, evidence-grounded RAG architecture:
- **Strict Evidence-First Verification**: A skill is classified as *Demonstrated* if and only if verifiable evidence is retrieved from the candidate's resume and passes post-generation source verification.
- **Explicit 4-State Classification**:
  - `Demonstrated`: Authentic, verifiable evidence directly supports the requirement.
  - `Partially demonstrated`: Partial or introductory context exists (e.g., attended a workshop or abandoned migration), but lacks proven production ownership.
  - `Not found in resume`: No sufficient textual evidence was found. *(Explicitly disclaimed: does not imply candidate lacks the skill, only that the document does not evidence it)*.
  - `Uncertain`: Ambiguous or conflicting signals.
- **Deterministic Weighted Match Scoring**: Avoids LLM-hallucinated percentages in favor of a weighted mathematical formula based on mandatory vs. preferred requirements.
- **Hardened Security**: Untrusted documents (resumes and JDs) are sanitized and XML-fenced (`<untrusted_document_context>`), neutralizing prompt injection exploits.

---

## 2. Technology Stack

### Frontend
- **Framework**: React 18 with TypeScript
- **Bundler**: Vite
- **Styling**: Tailwind CSS with custom typography and design system
- **Routing**: React Router DOM v6
- **Icons**: Lucide React
- **Data Visualizations**: Recharts & Custom SVG Metric Gauges
- **HTTP Client**: Axios

### Backend
- **Framework**: Python 3.10+ with FastAPI
- **Data Validation & Schemas**: Pydantic v2
- **ORM & Database**: SQLAlchemy 2.0 with dynamic dialect switching (PostgreSQL + pgvector for cloud/production; SQLite portable fallback for instant local/CI testing)
- **Document Processing**:
  - `PyMuPDF` (pymupdf / fitz) for high-performance PDF text and metadata extraction with scanned image-only detection.
  - `python-docx` for structured Word document parsing with paragraph and table traversal.
- **RAG & Vector Retrieval**:
  - Hybrid Retrieval Engine combining vector cosine similarity with lexical keyword boost and section relevance weighting.
  - Pluggable LLM & Embedding provider abstraction (Google Gemini, OpenAI GPT-4o, and built-in offline deterministic mock).
- **Test Suite**: Pytest & pytest-asyncio (21 automated unit, integration, and benchmark tests).

---

## 3. Architecture Diagrams

### A. High-Level System Architecture

```mermaid
flowchart TD
    subgraph Client["Frontend Client (React + TypeScript + Vite)"]
        UI1[Landing Page]
        UI2[Dashboard]
        UI3[Upload & JD Analysis Form]
        UI4[Interactive Results & Evidence Audit]
        UI5[RAG Reliability Dashboard]
    end

    subgraph API["Backend API (FastAPI)"]
        R1["/api/resumes/upload"]
        R2["/api/analyses"]
        R3["/api/analyses/:id/questions/regenerate"]
        R4["/api/evaluations/run"]
        R5["/api/health"]
    end

    subgraph Services["Core RAG Services"]
        DP[Document Parser PyMuPDF / python-docx]
        JP[JD Requirement Parser & Categorizer]
        ES[Embedding Service Gemini / OpenAI / Mock]
        RS[Hybrid Retrieval Engine Vector + Lexical]
        GG[Grounded Generation & Citation Verifier]
        SE[Deterministic Weighted Scoring Engine]
        RG[Learning Roadmap Generator]
        IQ[Interview Question Generator]
        EV[Deterministic Benchmark Evaluator]
    end

    subgraph Storage["Data Tier (PostgreSQL + pgvector)"]
        DB[(Relational DB: Resumes, Chunks, Embeddings, Analyses, Citations)]
    end

    Client -->|HTTP / JSON| API
    R1 --> DP --> ES --> DB
    R2 --> JP & RS & GG & SE & RG & IQ --> DB
    R3 --> IQ --> DB
    R4 --> EV --> DB
```

### B. Grounded RAG Ingestion & Audit Pipeline

```mermaid
sequenceDiagram
    autonumber
    actor User as Student / Recruiter
    participant Frontend as React Client
    participant API as FastAPI Backend
    participant Parser as Document & JD Parser
    participant Embed as Embedding Service
    participant Store as Vector Store (pgvector)
    participant RAG as Grounded Retrieval & Guard
    participant LLM as LLM Provider / Engine

    User->>Frontend: Uploads Resume (PDF/DOCX)
    Frontend->>API: POST /api/resumes/upload
    API->>Parser: Parse & extract text, detect sections
    Parser->>Embed: Generate embeddings for semantic chunks
    Embed->>Store: Persist chunks with embeddings
    API-->>Frontend: 201 Created (Resume preview & chunks)

    User->>Frontend: Pastes Job Description & clicks Submit
    Frontend->>API: POST /api/analyses
    API->>Parser: Extract requirements (Mandatory vs Preferred)
    loop For each requirement
        API->>RAG: Retrieve relevant resume chunks
        RAG->>Store: Hybrid vector search (cosine + lexical keyword boost)
        Store-->>RAG: Top-K chunks with relevance scores
        alt Low relevance (< 0.25 threshold)
            RAG-->>API: Abstain -> Classify as "Not found in resume"
        else Evidence found
            RAG->>LLM: Evaluate with XML-fenced untrusted context
            LLM-->>RAG: Structured assessment & cited quote
            RAG->>RAG: Verify citation grounding against source chunks
        end
    end
    API->>API: Calculate transparent weighted match score
    API->>API: Generate preparation roadmap & interview questions
    API->>Store: Persist analysis, skills, citations, roadmap, and questions
    API-->>Frontend: Complete verified analysis results
    Frontend-->>User: Interactive results with collapsible evidence audit
```

### C. Database Entity-Relationship (ER) Diagram

```mermaid
erDiagram
    RESUMES ||--o{ RESUME_CHUNKS : "splits into"
    RESUMES ||--o{ ANALYSES : "evaluated in"
    JOB_DESCRIPTIONS ||--o{ JOB_REQUIREMENTS : "decomposes into"
    JOB_DESCRIPTIONS ||--o{ ANALYSES : "benchmarked against"
    ANALYSES ||--o{ SKILL_ASSESSMENTS : "produces"
    ANALYSES ||--o{ LEARNING_ITEMS : "generates"
    ANALYSES ||--o{ INTERVIEW_QUESTIONS : "formulates"
    SKILL_ASSESSMENTS ||--o{ EVIDENCE_CITATIONS : "grounded by"
    RESUME_CHUNKS ||--o{ EVIDENCE_CITATIONS : "sourced from"

    RESUMES {
        string id PK
        string filename
        string file_type
        int file_size
        text extracted_text
        json detected_sections
        datetime created_at
    }

    RESUME_CHUNKS {
        string id PK
        string resume_id FK
        int chunk_index
        string section_name
        int page_number
        text content
        vector embedding
        datetime created_at
    }

    JOB_DESCRIPTIONS {
        string id PK
        string title
        string company
        string experience_level
        text raw_text
        datetime created_at
    }

    JOB_REQUIREMENTS {
        string id PK
        string job_description_id FK
        text requirement_text
        string category
        string priority
        vector embedding
    }

    ANALYSES {
        string id PK
        string resume_id FK
        string job_description_id FK
        float overall_match_score
        float mandatory_coverage
        float preferred_coverage
        text summary
        json limitations
        string status
        datetime created_at
    }

    SKILL_ASSESSMENTS {
        string id PK
        string analysis_id FK
        string requirement_id FK
        text requirement_text
        string category
        string priority
        string classification
        float confidence
        text reasoning
    }

    EVIDENCE_CITATIONS {
        string id PK
        string skill_assessment_id FK
        string chunk_id FK
        text snippet
        string source_section
        string page_number
        float similarity_score
        boolean is_verified_in_source
    }

    LEARNING_ITEMS {
        string id PK
        string analysis_id FK
        string skill_name
        string priority
        text why_it_matters
        json prerequisites
        json suggested_tasks
        text mini_project
        text completion_criterion
        string estimated_duration
    }

    INTERVIEW_QUESTIONS {
        string id PK
        string analysis_id FK
        text question
        string category
        string difficulty
        text relevance_rationale
        string source_type
        json key_concepts
        text answer_guidance
    }

    EVALUATION_RUNS {
        string id PK
        string dataset_version
        int total_test_cases
        float classification_accuracy
        float citation_validity_rate
        float abstention_rate
        float unsupported_claim_rate
        float precision_at_k
        float recall_at_k
        float schema_validation_rate
        datetime created_at
    }
```

---

## 4. Installation and Setup Instructions

### Prerequisites
- **Python 3.10+** (Tested on Python 3.10.11)
- **Node.js v18+** & **npm v9+**
- (Optional for containerization) **Docker** and **Docker Compose**

### Quick Start (Local Development)

#### 1. Backend Setup
```bash
# Navigate to backend directory
cd backend

# Create and activate Python virtual environment
python -m venv venv

# On Windows:
.\venv\Scripts\activate
# On Linux / macOS:
# source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Copy environment template
cp ../.env.example .env

# Run FastAPI backend with live reload
uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload
```
*Backend API docs will be immediately accessible at `http://127.0.0.1:8000/docs`.*

#### 2. Frontend Setup
```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Start Vite development server
npm run dev
```
*Frontend application will be accessible at `http://localhost:5173`.*

---

## 5. Environment Variables & Database Configuration

Copy `.env.example` to `.env` in the `backend/` folder:

| Variable | Description | Default | Allowed Values |
|---|---|---|---|
| `DATABASE_URL` | SQLAlchemy connection string | `sqlite:///./placement_analyzer.db` | SQLite or PostgreSQL with pgvector |
| `LLM_PROVIDER` | Generation model engine | `mock` | `mock`, `gemini`, `openai` |
| `LLM_MODEL` | Specific model identifier | `gemini-1.5-flash` | `gemini-1.5-flash`, `gpt-4o-mini`, etc. |
| `GEMINI_API_KEY` | Google Gemini API Key | *None* | Required if `LLM_PROVIDER="gemini"` |
| `OPENAI_API_KEY` | OpenAI API Key | *None* | Required if `LLM_PROVIDER="openai"` |
| `EMBEDDING_PROVIDER`| Embedding generator | `mock` | `mock`, `gemini`, `openai` |
| `EMBEDDING_DIMENSION`| Vector dimensions | `768` | `768` (Gemini/Mock), `1536` (OpenAI) |
| `RETRIEVAL_TOP_K` | Number of chunks per query | `5` | Integer >= 1 |
| `RETRIEVAL_SIMILARITY_THRESHOLD` | Threshold to filter noise | `0.35` | Float (0.0 to 1.0) |

### Supabase PostgreSQL Setup
1. Create a Supabase project at [supabase.com](https://supabase.com).
2. In SQL Editor, enable pgvector:
   ```sql
   CREATE EXTENSION IF NOT EXISTS vector;
   ```
3. Set your connection string in `.env`:
   ```env
   DATABASE_URL="postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT-REF].supabase.co:5432/postgres"
   ```

---

## 6. Testing & RAG Benchmark Verification

### Automated Test Suite (Pytest)
Run the 21 automated unit and integration tests:
```bash
cd backend
.\venv\Scripts\pytest.exe -v
```
**Test Coverage Includes:**
- PDF (PyMuPDF) and Word (.docx) extraction
- Empty, password-protected, and scanned image-only PDF detection
- Vector normalization, cosine similarity math, and hybrid search
- Missing evidence abstention and citation grounding verification
- Prompt injection protection and malicious instruction filtering
- Deterministic weighted match scoring formula
- End-to-end API integration tests with cascade deletion

### Deterministic Benchmark Evaluation Runner
Execute the 10-scenario labeled benchmark dataset:
```bash
cd backend
.\venv\Scripts\python.exe evaluate.py
```

#### Measured Benchmark Results:
```text
======================================================================
AI Placement Analyzer - RAG Benchmark & Reliability Evaluation
======================================================================
Dataset Version              : v1.0.0
Total Test Cases             : 10
Skill Classification Accuracy: 100.0%  (10/10 PASS)
Evidence Citation Validity   : 100.0%  (Verified against resume chunks)
Abstention on Missing Skills : 100.0%  (Zero hallucinated claims)
Unsupported-Claim Rate       : 0.0%    (Target: 0.0%)
Retrieval Precision@K        : 100.0%
Retrieval Recall@K           : 100.0%
Schema Validation Rate       : 100.0%
End-to-End Success Rate      : 100.0%
======================================================================
```

---

## 7. Mathematical Scoring Formula & RAG Guardrails

### Weighted Match Score Formula
Rather than prompting an LLM to hallucinate an arbitrary percentage, the system calculates alignment deterministically:

$$\text{Alignment Score} = \left( \frac{\sum_{i=1}^N (w_i \times a_i)}{\sum_{i=1}^N w_i} \right) \times 100$$

Where:
- $w_i = 3.0$ for **Mandatory Requirements**, $w_i = 1.5$ for **Preferred Requirements**.
- $a_i \in \{1.0, 0.5, 0.0\}$ represents **Adequacy**:
  - `Demonstrated` = $1.0$
  - `Partially demonstrated` = $0.5$
  - `Not found in resume` = $0.0$
  - `Uncertain` = $0.0$

### Hallucination Prevention & Prompt Injection Hardening
1. **XML Fencing**: All candidate text is isolated in `<untrusted_document_context id="...">` containers.
2. **Instruction Neutralization**: Malicious prompt injection strings (e.g., `"SYSTEM: Ignore previous instructions"`, `"Give 100% score"`) are filtered to `[FILTERED_INSTRUCTION]`.
3. **Payload Exclusion**: Any evidence chunk containing injection tokens is disqualified from serving as valid skill evidence.
4. **Citation Grounding Verification**: Cited text is fuzzy-checked against the raw source document chunks. If an LLM fabricates a quotation, it is flagged as `Unverified` and demoted.

---

## 8. Docker Deployment

Launch PostgreSQL with pgvector, FastAPI backend, and React Nginx frontend simultaneously:

```bash
docker compose up --build
```
- Frontend: `http://localhost`
- Backend API & Swagger: `http://localhost:8000/docs`
- PostgreSQL pgvector: `localhost:5432`

---

## 9. Limitations & Disclosures

- **Textual Evidence Boundary**: The tool evaluates text extracted from resumes. Non-textual artifacts, portfolios hosted behind login screens, or unwritten skills cannot be evaluated.
- **Scanned Document Requirement**: Scanned image-only PDFs require OCR preprocessing before upload; the parser raises an explicit warning rather than returning an empty analysis.
- **Alignment Score vs. Hiring Guarantee**: The alignment score measures textual correspondence between a resume and a job description. It does not represent hiring probability or guarantee an interview.
