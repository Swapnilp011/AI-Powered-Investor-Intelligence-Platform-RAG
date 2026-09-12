# 📘 AI-Powered Investor Intelligence Platform — Master Technical Documentation

---

## 1. Executive Summary & Overview

The **AI-Powered Investor Intelligence Platform** is a enterprise-grade, self-hosted Retrieval-Augmented Generation (RAG) system. It automates the parsing, extraction, indexing, and analysis of complex corporate financial documents (e.g., Annual Reports, 10-K/10-Q filings, Financial Summaries).

### Core Platform Capabilities
* **High-Fidelity PDF Ingestion**: Converts multi-column financial PDFs to structured Markdown using `pymupdf4llm`.
* **Semantic Document Chunking**: Distance-based semantic text splitting to preserve contextual cohesion across financial tables and commentary.
* **Dual Storage Architecture**:
  * **Unstructured Data**: Persistent local vector search via **ChromaDB** with HNSW indexing and metadata filtering (`company`, `year`).
  * **Structured Data**: Relational persistence in **Microsoft SQL Server (SSMS)** for financial metrics and qualitative insights.
* **LLM-Powered Extraction & RAG Chat**: Uses Google Gemini API (`gemini-3.6-flash` and `gemini-embedding-001`) with rate-limiting pacing and Pydantic v2 structured validation.
* **Web Dashboard & API**: FastAPI backend providing a dark-mode interactive dashboard, metric REST APIs, and an interactive financial Q&A chatbot.

---

## 2. System Architecture & Data Flow

```text
                                +-----------------------------------+
                                |      PDF Report Upload (UI/API)   |
                                +-----------------------------------+
                                                  |
                                                  v
                                +-----------------------------------+
                                |    PDF to Markdown Conversion     |
                                |       (pymupdf4llm converter)     |
                                +-----------------------------------+
                                                  |
                                                  v
                                +-----------------------------------+
                                |    Semantic Document Chunking     |
                                |     (ingestion/semantic_chunker)  |
                                +-----------------------------------+
                                                  |
                                 +----------------+----------------+
                                 |                                 |
                                 v                                 v
               +-----------------------------------+   +-----------------------------------+
               |    ChromaDB Vector Store (Local)  |   |    Google Gemini API Extraction   |
               |  (gemini-embedding-001 vectors)   |   |        (gemini-3.6-flash)          |
               +-----------------------------------+   +-----------------------------------+
                                 |                                 |
                                 v                                 v
               +-----------------------------------+   +-----------------------------------+
               |      Contextual RAG Chatbot       |   |   Microsoft SQL Server (SSMS)     |
               |    (FastAPI /api/chat Endpoint)   |   |   (financial_metrics Table)       |
               +-----------------------------------+   +-----------------------------------+
                                 \                                 /
                                  \                               /
                                   v                             v
                                +------------------------------------+
                                |    Interactive Dashboard Web UI    |
                                |        (http://localhost:8000)     |
                                +------------------------------------+
```

---

## 3. System Prerequisites & Environment Setup

### 3.1 Software Requirements
| Component | Minimum Requirement | Recommended Version |
| :--- | :--- | :--- |
| **Operating System** | Windows 10/11, macOS, Linux | Windows 11 (for local SSMS) |
| **Python** | 3.10+ | Python 3.11 or 3.12 |
| **Database Server** | Microsoft SQL Server 2017+ | SQL Server Express 2025 / Developer |
| **Database Tool** | SSMS | SQL Server Management Studio v19+ |
| **ODBC Driver** | ODBC Driver for SQL Server | ODBC Driver 17 or 18 for SQL Server |
| **LLM Provider** | Google Gemini API Key | Google AI Studio API Key |

---

## 4. Step-by-Step Installation & Command Reference

### Step 1: Clone Repository & Setup Virtual Environment

#### Option A: Using Standard Python `venv`
```powershell
# Open PowerShell in project directory
python -m venv .venv

# Activate Virtual Environment (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate Virtual Environment (Linux/macOS)
# source .venv/bin/activate
```

#### Option B: Using `uv` Package Manager (Fast Alternative)
```powershell
# Install UV if not installed
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Initialize & Create virtual environment
uv venv
.\.venv\Scripts\Activate.ps1
```

---

### Step 2: Install Required Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 3: Environment Configuration (`.env`)

Create a `.env` file in the root directory:

```env
# LLM Provider Configuration
LLM_PROVIDER=gemini
DB_TYPE=sqlserver

# Google Gemini API Key & Models
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_CHAT_MODEL=gemini-3.6-flash
GEMINI_EMBED_MODEL=gemini-embedding-001

# ChromaDB Vector Store Configuration
VECTOR_STORE_PATH=./data/vectorstore
VECTOR_STORE_COLLECTION=investor-intelligence

# Local SQL Server / SSMS Configuration
SQLSERVER_HOST=localhost\SQLEXPRESS2025
SQLSERVER_PORT=1433
SQLSERVER_DATABASE=investor_intelligence
SQLSERVER_USER=sa
SQLSERVER_PASSWORD=YourPassword123!
SQLSERVER_DRIVER=ODBC Driver 17 for SQL Server
SQLSERVER_TRUSTED_CONNECTION=yes
```

---

### Step 4: Initialize SQL Database & Tables

Execute the table creation script:

```powershell
python database/create_table.py
```

*Console Output:*
```text
Database 'investor_intelligence' checked / created successfully in SQL Server.
financial_metrics table checked/created in SQLSERVER.
```

---

### Step 5: Launch the Application

Start the web application server:

```powershell
python app.py
```

Or run with live reload:
```powershell
uvicorn app:app --reload --port 8000
```

Access points:
* **Web UI Dashboard**: `http://localhost:8000`
* **Swagger API Docs**: `http://localhost:8000/docs`

---

## 5. Database Architecture & SSMS Queries

### 5.1 SQL Server Table Schema (`financial_metrics`)

```sql
CREATE TABLE financial_metrics (
    id INT IDENTITY(1,1) PRIMARY KEY,
    company NVARCHAR(100),
    year NVARCHAR(10),
    revenue NVARCHAR(MAX),
    net_income NVARCHAR(MAX),
    operating_income NVARCHAR(MAX),
    cash_flow NVARCHAR(MAX),
    total_assets NVARCHAR(MAX),
    total_liabilities NVARCHAR(MAX),
    risk_factors NVARCHAR(MAX),
    growth_drivers NVARCHAR(MAX),
    created_at DATETIME DEFAULT GETDATE()
);
```

---

### 5.2 Essential SQL Queries for SSMS

Open **SSMS**, connect to `localhost\SQLEXPRESS2025`, click **New Query**, and execute:

#### 1. Retrieve Latest Metrics for All Ingested Companies
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

#### 2. Query Qualitative Risk Factors & Growth Drivers
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

#### 3. Search Records for a Specific Company
```sql
USE investor_intelligence;
GO

SELECT * 
FROM financial_metrics
WHERE company LIKE '%Flipkart%' OR company LIKE '%Tata Motors%';
GO
```

---

## 6. Advanced Technical Implementation Details

### 6.1 Pydantic v2 Structured JSON Validation (`rag/kpi_extractor_rag.py`)
To guarantee that Gemini JSON responses match Python dictionary lookups seamlessly without dropping values, `FinancialMetrics` uses `ConfigDict(populate_by_name=True)`:

```python
from pydantic import BaseModel, ConfigDict, Field

class FinancialMetrics(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    revenue: str | int | None = Field(None, alias="Revenue")
    net_income: str | int | None = Field(None, alias="Net Income")
    operating_income: str | int | None = Field(None, alias="Operating Income")
    cash_flow: str | int | None = Field(None, alias="Cash Flow from Operating Activities")
    total_assets: str | int | None = Field(None, alias="Total Assets")
    total_liabilities: str | int | None = Field(None, alias="Total Liabilities")
    risk_factors: str | list | None = Field(None, alias="Top Risk Factors")
    growth_drivers: str | list | None = Field(None, alias="Top Growth Drivers")
```

### 6.2 Rate Limit Pacing (`llm/llm_client.py`)
To respect Google Gemini AI Studio's **15 Requests Per Minute (RPM)** free tier limit:
* Embeddings use a batch size of `20`.
* A proactive `1.2s` pacing delay is added between batch requests.
* Retries use exponential backoff (`4s * attempt`) to avoid rate limit spikes.

---

## 7. API Reference

| Endpoint | Method | Description | Request Payload / Params |
| :--- | :--- | :--- | :--- |
| `/` | `GET` | Renders HTML Dashboard UI | None |
| `/health` | `GET` | Health check endpoint | None |
| `/api/metrics` | `GET` | Fetches JSON metrics from SQL Server | None |
| `/api/upload` | `POST` | Ingests PDF file, runs RAG & saves to SQL Server | `file: UploadFile` (Multipart) |
| `/api/chat` | `POST` | RAG Chatbot Q&A | `{"question": "...", "company": "...", "year": 2024}` |

---

## 8. Troubleshooting & Common Issues

### Issue 1: `pyodbc.OperationalError (08001)` Connection Failure
* **Cause**: Incorrect SQL Server instance name or authentication mode in `.env`.
* **Fix**: Ensure `SQLSERVER_HOST=localhost\SQLEXPRESS2025` (or your exact instance name from Windows `Get-Service -Name '*SQL*'`) and `SQLSERVER_TRUSTED_CONNECTION=yes`.

### Issue 2: `ModuleNotFoundError: No module named 'database'`
* **Cause**: Running script directly without adding project root to `sys.path`.
* **Fix**: Run via module format `python -m database.create_table` or run script directly (sys.path insertion is auto-configured).

### Issue 3: `429 Rate Limit Exceeded` during PDF ingestion
* **Cause**: Exceeding 15 RPM quota on Gemini API.
* **Fix**: Handled automatically by `RateLimitedGeminiEmbeddings` pacing.

---

## 9. Project Directory Tree

```text
AI-Powered-Investor-Intelligence-Platform/
├── app.py                      # Main FastAPI application server
├── requirements.txt            # Python dependencies
├── .env                        # Active environment configuration
├── .env.example                # Template configuration file
├── PROJECT_MASTER_DOCUMENTATION.md # Complete technical documentation
├── database/
│   ├── sql_server.py           # SQLAlchemy database engine connection builder
│   ├── create_table.py         # SQL database & table creation script
│   ├── save_metrics.py         # Upserts extracted KPI metrics to SQL Server
│   └── metrics.py              # Queries deduplicated metrics for UI/API
├── ingestion/
│   ├── pdf_to_markdown.py      # PDF parsing via pymupdf4llm
│   ├── semantic_chunker.py     # Semantic text chunking algorithm
│   └── ingest_documents.py     # Document ingestion orchestrator
├── vectorstore/
│   ├── chroma_store.py         # ChromaDB vector store client & retriever
│   └── create_index.py         # Vector index startup checker
├── llm/
│   └── llm_client.py           # Gemini API rate-limiting wrapper & structured JSON
├── rag/
│   └── kpi_extractor_rag.py    # RAG pipeline for financial KPI extraction
├── routes/
│   ├── chat.py                 # FastAPI router for Chatbot API (/api/chat)
│   └── ingestion.py            # FastAPI router for PDF upload (/api/upload)
├── templates/
│   └── dashboard.html          # Jinja2 Dashboard UI template
└── static/
    └── style.css               # Modern dark-mode UI styling
```
