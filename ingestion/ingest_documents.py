import os
import sys
from pathlib import Path

# Ensure root directory is on sys.path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from dotenv import load_dotenv

from ingestion.pdf_to_markdown import PDFToMarkdownConverter
from ingestion.semantic_chunker import chunk_markdown
from vectorstore.chroma_store import ChromaVectorStore, Retriever
from rag.kpi_extractor_rag import extract_financial_metrics
from database.save_metrics import save_metrics
from llm.llm_client import get_embedding_client

load_dotenv()


def parse_company_year(pdf_file: Path) -> tuple[str, str]:
    """Parse company and year from a PDF filename.

    Supports names like `Tata_Motors_Enterprise_Financial_Analysis_Report.pdf`,
    `2024_Apple.pdf`, and `Reliance_FY23_Annual_Report.pdf`.
    """
    import re
    stem = pdf_file.stem
    year_match = re.search(r'(19\d{2}|20\d{2})', stem)
    if year_match:
        year = year_match.group(1)
        raw_year_str = year_match.group(0)
    else:
        fy_match = re.search(r'FY(\d{2})', stem, re.IGNORECASE)
        year = f"20{fy_match.group(1)}" if fy_match else "2024"
        raw_year_str = fy_match.group(0) if fy_match else ""

    cleaned_name = stem
    if raw_year_str:
        cleaned_name = cleaned_name.replace(raw_year_str, "")

    cleaned_name = re.sub(r'(?i)[_\s]*(enterprise|financial|analysis|report|annual|statement)[_\s]*', ' ', cleaned_name)
    cleaned_name = cleaned_name.replace("_", " ").strip()
    company = " ".join(cleaned_name.split()) if cleaned_name else "Unknown Company"

    return company, year


def ingest_document(
    pdf_path: str,
    embeddings,
    vector_store: ChromaVectorStore
) -> None:
    """
    Ingest a single PDF document.
    """
    pdf_file = Path(pdf_path)

    company, year = parse_company_year(pdf_file)
    print(f"Ingesting {pdf_file.name} as company={company!r}, year={year!r}")

    converter = PDFToMarkdownConverter()

    markdown_file = converter.convert_pdf(
        pdf_path=pdf_path,
        output_dir="data/markdown"
    )

    chunks = chunk_markdown(
        markdown_file=markdown_file,
        embeddings=embeddings
    )

    print(f"Generated {len(chunks)} chunks for {pdf_file.name}")

    vector_store.upload_chunks(
        chunks=chunks,
        embeddings=embeddings,
        company=company,
        year=year,
        source_file=pdf_file.name
    )

    # Extract financial metrics using the newly ingested data
    retriever = Retriever(embeddings=embeddings)
    metrics = extract_financial_metrics(
        retriever=retriever,
        company=company,
        year=int(year) if year.isdigit() else None
    )

    # Persist metrics to SQL Server database
    if metrics:
        save_metrics(
            company=company,
            year=int(year) if str(year).isdigit() else year,
            metrics=metrics
        )


def ingest_directory(input_dir: str) -> None:
    """
    Ingest all PDFs from a directory.
    """
    embeddings = get_embedding_client()
    vector_store = ChromaVectorStore()

    pdf_files = list(Path(input_dir).glob("*.pdf"))

    print(f"Found {len(pdf_files)} PDF(s)")

    for pdf_file in pdf_files:
        ingest_document(
            pdf_path=str(pdf_file),
            embeddings=embeddings,
            vector_store=vector_store
        )


if __name__ == "__main__":
    ingest_directory("data/raw_pdfs")