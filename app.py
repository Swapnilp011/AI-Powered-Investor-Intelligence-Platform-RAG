import os
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from database.metrics import get_metrics
from database.sql_server import create_database
from database.create_table import create_tables
from vectorstore.create_index import create_index
from routes.ingestion import router as ingestion_router
from routes.chat import router as chat_router

load_dotenv()

from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initialize database and vector index on app startup.
    """
    try:
        create_database()
        create_tables()
    except Exception as e:
        print(f"Warning: Could not initialize database/tables automatically: {e}")

    try:
        create_index()
    except Exception as e:
        print(f"Warning: Could not initialize ChromaDB vector index: {e}")
    
    yield

app = FastAPI(
    title="AI-Powered Investor Intelligence Platform (Local Architecture)",
    lifespan=lifespan
)


app.include_router(
    ingestion_router,
    prefix="/api",
    tags=["Ingestion"]
)

app.include_router(
    chat_router,
    prefix="/api",
    tags=["Chat"]
)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)

templates = Jinja2Templates(
    directory="templates"
)


@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    from fastapi.responses import Response
    return Response(status_code=204)


@app.get("/")
def dashboard(request: Request):
    """
    Render dashboard UI.
    """
    try:
        metrics = get_metrics()
    except Exception as exc:
        print(f"Warning: Could not fetch metrics for dashboard: {exc}")
        metrics = []

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "metrics": metrics,
            "total_companies": len(metrics),
            "total_reports": len(metrics)
        }
    )


@app.get("/api/metrics")
def metrics():
    """
    Return KPI metrics as JSON.
    """
    try:
        data = get_metrics()
    except Exception as exc:
        print(f"Warning: Could not fetch metrics API: {exc}")
        data = []

    return JSONResponse(content=data)


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "provider": os.getenv("LLM_PROVIDER", "gemini"),
        "vector_store": "ChromaDB",
        "database": os.getenv("DB_TYPE", "sqlserver")
    }


if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 60)
    print("🚀 Application starting!")
    print("Open the platform in your browser at:")
    print("👉 http://localhost:8000")
    print("👉 http://127.0.0.1:8000")
    print("=" * 60 + "\n")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000
    )