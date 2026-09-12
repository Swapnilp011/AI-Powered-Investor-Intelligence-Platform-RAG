# AI-Powered Investor Intelligence Platform (Self-Hosted / Local Architecture)


This repository contains the Python backend for an **AI-powered Investor Intelligence Platform**, including PDF document ingestion, PyMuPDF4LLM markdown parsing, semantic chunking, **Google Gemini API / Ollama / OpenAI** LLM integration, **ChromaDB** vector storage, **Microsoft SQL Server (SSMS)** KPI storage, and an interactive FastAPI web dashboard.

---

## Technical Architecture

* **LLM & Embeddings**: Google Gemini API (`gemini-2.5-flash` / `text-embedding-004`) with multi-provider support for Ollama (`llama3` / `nomic-embed-text`) and OpenAI (`gpt-4o`).
* **Vector Store**: ChromaDB (local persistent vector store with HNSW indexing and metadata filtering).
* **Database**: Local Microsoft SQL Server (SSMS) via SQLAlchemy + `pyodbc` / `pymssql`.
* **Backend API**: FastAPI & Uvicorn.
* **Document Ingestion**: PyMuPDF4LLM + LangChain `SemanticChunker`.
* **Package Manager**: UV (`astral.sh/uv`).

---

## Prerequisites

* Python 3.12+
* UV Package Manager (`astral.sh/uv`)
* Local Microsoft SQL Server / SSMS (SQL Server Express or Developer edition)
* Google Gemini API key (or local Ollama instance / OpenAI key)

---

## Setup & Running Locally

### 1. Install UV Package Manager

#### Windows (PowerShell)
```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### macOS / Linux
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

### 2. Environment Configuration

Copy the sample environment file `.env.example` to `.env`:

```bash
copy .env.example .env   # Windows
# or: cp .env.example .env (Linux/macOS)
```

Configure your credentials in `.env`:
```env
# LLM Provider Configuration (gemini / ollama / openai)
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_gemini_api_key_here

# Local SQL Server / SSMS Credentials
SQLSERVER_HOST=localhost
SQLSERVER_PORT=1433
SQLSERVER_DATABASE=investor_intelligence
SQLSERVER_USER=sa
SQLSERVER_PASSWORD=YourPassword123!
SQLSERVER_DRIVER=ODBC Driver 17 for SQL Server
```

---

### 3. Create Virtual Environment & Install Dependencies

```bash
uv venv
.venv\Scripts\activate      # Windows PowerShell/CMD
# source .venv/bin/activate # Linux/macOS

uv pip install -r requirements.txt
```

---

### 4. Run the Application

```bash
python app.py
```

Access the interactive dashboard UI at `http://localhost:8000`.

---

## Project Features

* **Annual Report Upload & Ingestion**: Drag-and-drop 10-K/10-Q PDF reports.
* **PDF to Markdown Parsing**: High-fidelity structure extraction using `pymupdf4llm`.
* **Semantic Document Chunking**: Distance-based semantic text splitting.
* **ChromaDB Vector Indexing**: Local persistent vector search with metadata filtering (`company` and `year`).
* **KPI Extraction**: Automated extraction of Revenue, Net Income, Operating Income, Cash Flow, Assets, Liabilities, Risks, and Growth Drivers.
* **Local SQL Server Persistence**: Deduplicated metric storage using SQL Server window functions.
* **Interactive AI Chatbot**: Contextual RAG Q&A over ingested corporate filings.

---

## API Endpoints

* `GET /` — Renders Dashboard UI
* `GET /health` — Health check endpoint
* `GET /api/metrics` — Returns extracted financial KPI metrics
* `POST /api/upload` — Uploads PDF report and runs full ingestion pipeline
* `POST /api/chat` — Contextual AI Chat Q&A endpoint

---

## How to View Data in SSMS (SQL Server Management Studio)

Follow these steps to inspect the extracted financial metrics directly inside Microsoft SQL Server Management Studio:

### Step 1: Connect to SQL Server
1. Open **SQL Server Management Studio (SSMS)**.
2. In the **Connect to Server** dialog:
   - **Server type**: Database Engine
   - **Server name**: `localhost\SQLEXPRESS2025` (or your local server instance)
   - **Authentication**: Windows Authentication (or SQL Server Authentication)
3. Click **Connect**.

### Step 2: Open Query Window
Click **New Query** in the top toolbar.

### Step 3: Run Useful SQL Queries

#### 1. View All Extracted Metrics (Latest per Company)
```sql
USE investor_intelligence;
GO

SELECT 
    id,
    company,
    year,
    revenue,
    net_income,
    operating_income,
    cash_flow,
    total_assets,
    total_liabilities,
    created_at
FROM financial_metrics
ORDER BY company, year DESC;
GO
```

#### 2. Inspect Top Risk Factors & Growth Drivers
```sql
USE investor_intelligence;
GO

SELECT 
    company,
    year,
    risk_factors,
    growth_drivers
FROM financial_metrics;
GO
```

#### 3. View Full Detailed Record for a Specific Company (e.g. Flipkart or Tata Motors)
```sql
USE investor_intelligence;
GO

SELECT * 
FROM financial_metrics
WHERE company LIKE '%Flipkart%';
GO
```
