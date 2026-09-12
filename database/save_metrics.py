import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from database.sql_server import get_engine


def save_metrics(
    company: str,
    year: int | str,
    metrics: dict
) -> None:
    """
    Save extracted financial metrics to the database (SQL Server or SQLite fallback).

    Args:
        company: Company name.
        year: Fiscal year.
        metrics: Extracted KPI dictionary.
    """
    try:
        engine = get_engine()

        delete_query = """
        DELETE FROM financial_metrics WHERE company = :company AND year = :year
        """

        insert_query = """
        INSERT INTO financial_metrics (
            company,
            year,
            revenue,
            net_income,
            operating_income,
            cash_flow,
            total_assets,
            total_liabilities,
            risk_factors,
            growth_drivers
        )
        VALUES (
            :company,
            :year,
            :revenue,
            :net_income,
            :operating_income,
            :cash_flow,
            :total_assets,
            :total_liabilities,
            :risk_factors,
            :growth_drivers
        )
        """

        def get_val(key1, key2):
            v = metrics.get(key1)
            if v is None:
                v = metrics.get(key2)
            if v is None or v == "None":
                return ""
            return str(v)

        risk_factors = metrics.get("Top Risk Factors")
        if risk_factors is None:
            risk_factors = metrics.get("risk_factors") or []

        growth_drivers = metrics.get("Top Growth Drivers")
        if growth_drivers is None:
            growth_drivers = metrics.get("growth_drivers") or []

        if isinstance(risk_factors, list):
            risk_str = "\n".join(str(r) for r in risk_factors)
        else:
            risk_str = str(risk_factors) if risk_factors else ""

        if isinstance(growth_drivers, list):
            growth_str = "\n".join(str(g) for g in growth_drivers)
        else:
            growth_str = str(growth_drivers) if growth_drivers else ""

        params = {
            "company": str(company),
            "year": str(year),
            "revenue": get_val("Revenue", "revenue"),
            "net_income": get_val("Net Income", "net_income"),
            "operating_income": get_val("Operating Income", "operating_income"),
            "cash_flow": get_val("Cash Flow from Operating Activities", "cash_flow"),
            "total_assets": get_val("Total Assets", "total_assets"),
            "total_liabilities": get_val("Total Liabilities", "total_liabilities"),
            "risk_factors": risk_str,
            "growth_drivers": growth_str
        }

        with engine.begin() as connection:
            connection.execute(text(delete_query), {"company": str(company), "year": str(year)})
            connection.execute(text(insert_query), params)

        print(f"Successfully saved metrics for {company} {year}.")
    except Exception as exc:
        print(f"Warning: Could not save metrics to database: {exc}")


if __name__ == "__main__":
    sample_metrics = {
        "Revenue": "$391,035",
        "Net Income": "$93,736",
        "Operating Income": "$123,216",
        "Cash Flow from Operating Activities": "$118,254",
        "Total Assets": "$364,980",
        "Total Liabilities": "$308,030",
        "Top Risk Factors": [
            "Macroeconomic conditions including inflation and currency fluctuations.",
            "High competition and rapid technological changes."
        ],
        "Top Growth Drivers": [
            "Increased Services revenue from advertising and cloud services.",
            "Continued strong product sales performance."
        ]
    }

    save_metrics(
        company="Apple",
        year=2024,
        metrics=sample_metrics
    )