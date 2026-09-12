# 🚀 AI-Powered Investor Intelligence Platform (RAG + Local SSMS + Gemini API)

An enterprise-grade **AI Investor Intelligence Platform** that ingests corporate annual reports (10-K/10-Q PDFs), performs high-fidelity Markdown structure parsing, generates vector embeddings stored in **ChromaDB**, extracts key financial metrics & qualitative insights via **Google Gemini API**, stores structured financial data in **Microsoft SQL Server (SSMS)**, and provides an interactive web dashboard with a RAG-powered chatbot.

---

## 🏗️ Technical Architecture

```
                                  +------------------------------------+
                                  |     PDF Document Upload (UI/API)   |
                                  +------------------------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  |     PyMuPDF4LLM Markdown Parser    |
                                  +------------------------------------+
                                                    |
                                                    v
                                  +------------------------------------+
                                  |      Semantic Text Chunker         |
                                  +------------------------------------+
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

## Key Features

* 📄 **PDF Report Ingestion & Conversion**: High-fidelity structure extraction using `pymupdf4llm`.
* 🧩 **Semantic Document Chunking**: Intelligent distance-based text splitting for optimal context retrieval.
* 🔍 **ChromaDB Vector Indexing**: Local persistent vector search with metadata filtering (`company` and `year`).
* 📊 **Automated Financial KPI Extraction**: Gemini-powered extraction of:
  * **Revenue**
  * **Net Income**
  * **Operating Income**
  * **Cash Flow from Operations**
  * **Total Assets & Total Liabilities**
  * **Top Risk Factors & Growth Drivers**
* 🗄️ **Relational SSMS Persistence**: Automatic database/table creation and metric persistence in Microsoft SQL Server.
* 💬 **Contextual Financial Chatbot**: RAG-driven financial assistant answering report-specific questions.
* 🎨 **Modern Dark-Mode Dashboard**: Clean financial overview rendering key KPIs and qualitative intelligence.

---

## 📋 Prerequisites & System Requirements

Before running this project, ensure your environment meets the following requirements:

### 1. System Hardware & Operating System
* **Operating System**: Windows 10/11 (Recommended for local SSMS), macOS, or Linux.
* **Python**: Python **3.10** or higher.

### 2. Microsoft SQL Server & SSMS Setup (Local Database)
* **SQL Server**: Microsoft SQL Server Express (e.g. `SQLEXPRESS2025` or `SQLEXPRESS`) or SQL Server Developer edition installed locally.
* **SQL Server Management Studio (SSMS)**: Installed to query and manage your database.
* **ODBC Driver**: **ODBC Driver 17 for SQL Server** (or ODBC Driver 18) installed on your system.

### 3. API Key Requirements
* **Google Gemini API Key**: Free API key from [Google AI Studio](https://aistudio.google.com/).
* *(Optional)*: Support for local Ollama models (`llama3`) or OpenAI API (`gpt-4o`).

---

## ⚡ Quick Setup & Installation Guide

### Step 1: Clone Repository & Create Virtual Environment

Open PowerShell or Terminal in your project directory:
    
```powershell
# 1. Create a Python virtual environment
python -m venv .venv

# If venv is create then run .
uv init
uv venv

# 2. Activate the virtual environment
# On Windows PowerShell:
.venv\Scripts\Activate.ps1

# On macOS/Linux:
# source .venv/bin/activate
```

---

### Step 2: Install Python Dependencies

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

---

### Step 3: Configure Environment Variables (`.env`)

Create a `.env` file in the root directory (you can copy from `.env.example`):

```env
# LLM Provider (gemini / ollama / openai)
LLM_PROVIDER=gemini
DB_TYPE=sqlserver

# Google Gemini API Configuration
GEMINI_API_KEY=your_actual_gemini_api_key_here
GEMINI_CHAT_MODEL=gemini-3.6-flash
GEMINI_EMBED_MODEL=gemini-embedding-001

# Vector Store (ChromaDB) Path
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

> **Note for Windows Authentication**: Set `SQLSERVER_HOST` to your local instance (e.g. `localhost\SQLEXPRESS2025` or `.\SQLEXPRESS`) and set `SQLSERVER_TRUSTED_CONNECTION=yes`.

---

### Step 4: Initialize Database & SQL Tables

Run the database setup script to automatically create the `investor_intelligence` database and `financial_metrics` table in SQL Server:

```powershell
python database/create_table.py
```

*Expected Output:*
```text
Database 'investor_intelligence' checked / created successfully in SQL Server.
financial_metrics table checked/created in SQLSERVER.
```

---

### Step 5: Start the Web Application

Launch the FastAPI server:

```powershell
python app.py
```

Open your browser and navigate to:
👉 **Dashboard**: [http://localhost:8000](http://localhost:8000)  
👉 **API Docs (Swagger)**: [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🗄️ How to View & Query Data in SSMS

To inspect the extracted financial metrics directly inside Microsoft SQL Server Management Studio:

### 1. Connect in SSMS
1. Open **SSMS**.
2. **Server name**: `localhost\SQLEXPRESS2025` (or `.\SQLEXPRESS`).
3. **Authentication**: Windows Authentication.
4. Click **Connect**.

### 2. Run SQL Queries

#### A. View All Extracted Financial Metrics
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

#### B. Inspect Qualitative Risk Factors & Growth Drivers
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

#### C. Search Specific Company Record (e.g. Flipkart / Tata Motors)
```sql
USE investor_intelligence;
GO

SELECT * 
FROM financial_metrics
WHERE company LIKE '%Flipkart%';
GO
```

---

## 📁 Repository Directory Structure

```text
AI-Powered-Investor-Intelligence-Platform/
├── app.py                      # Main FastAPI web server & dashboard routes
├── requirements.txt            # Python package dependencies
├── .env.example                # Example environment configuration template
├── database/
│   ├── sql_server.py           # SQLAlchemy connection manager for SQL Server
│   ├── create_table.py         # Table & Database initialization script
│   ├── save_metrics.py         # Inserts/updates KPI records in SQL Server
│   └── metrics.py              # Queries metrics from SQL Server for UI
├── ingestion/
│   ├── pdf_to_markdown.py      # PDF parsing using pymupdf4llm
│   ├── semantic_chunker.py     # Document text chunking logic
│   └── ingest_documents.py     # Document ingestion orchestrator
├── vectorstore/
│   ├── chroma_store.py         # ChromaDB local vector storage & retriever
│   └── create_index.py         # Vector index initialization
├── llm/
│   └── llm_client.py           # Gemini API rate-limiting wrapper & structured JSON
├── rag/
│   └── kpi_extractor_rag.py    # RAG pipeline for financial KPI extraction
├── routes/
│   ├── chat.py                 # FastAPI router for Chatbot API (/api/chat)
│   └── ingestion.py            # FastAPI router for PDF upload (/api/upload)
├── templates/
│   └── dashboard.html          # Jinja2 dashboard UI template
└── static/
    └── style.css               # Modern dark-mode dashboard styling
```

---

## 📡 API Endpoints Summary

| Endpoint | Method | Description |
| :--- | :--- | :--- |
| `GET /` | `GET` | Renders interactive web dashboard |
| `GET /health` | `GET` | System health check (database, vectorstore, LLM provider status) |
| `GET /api/metrics` | `GET` | Returns stored financial KPI records as JSON |
| `POST /api/upload` | `POST` | Uploads PDF report and runs full ingestion & extraction pipeline |
| `POST /api/chat` | `POST` | RAG-powered chatbot Q&A endpoint |

---

## 🛡️ License

This project is open-source so use it and learn.
