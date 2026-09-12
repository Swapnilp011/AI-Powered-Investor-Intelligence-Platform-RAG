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

        query = """
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

        risk_factors = metrics.get("Top Risk Factors") or metrics.get("risk_factors") or []
        growth_drivers = metrics.get("Top Growth Drivers") or metrics.get("growth_drivers") or []

        if isinstance(risk_factors, list):
            risk_str = "\n".join(str(r) for r in risk_factors)
        else:
            risk_str = str(risk_factors)

        if isinstance(growth_drivers, list):
            growth_str = "\n".join(str(g) for g in growth_drivers)
        else:
            growth_str = str(growth_drivers)

        params = {
            "company": str(company),
            "year": str(year),
            "revenue": str(metrics.get("Revenue") or metrics.get("revenue") or ""),
            "net_income": str(metrics.get("Net Income") or metrics.get("net_income") or ""),
            "operating_income": str(metrics.get("Operating Income") or metrics.get("operating_income") or ""),
            "cash_flow": str(metrics.get("Cash Flow from Operating Activities") or metrics.get("cash_flow") or ""),
            "total_assets": str(metrics.get("Total Assets") or metrics.get("total_assets") or ""),
            "total_liabilities": str(metrics.get("Total Liabilities") or metrics.get("total_liabilities") or ""),
            "risk_factors": risk_str,
            "growth_drivers": growth_str
        }

        with engine.begin() as connection:
            connection.execute(text(query), params)

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