from sqlalchemy import text
from database.sql_server import get_engine


def get_metrics():
    """
    Fetch deduplicated financial metrics from SQL Server.
    """
    engine = get_engine()

    query = """
    SELECT id, company, year, revenue, net_income, operating_income, cash_flow, total_assets, total_liabilities, risk_factors, growth_drivers, created_at
    FROM (
        SELECT *,
               ROW_NUMBER() OVER (
                   PARTITION BY company, year
                   ORDER BY created_at DESC
               ) AS rn
        FROM financial_metrics
    ) t
    WHERE rn = 1
    ORDER BY company
    """

    with engine.connect() as connection:
        result = connection.execute(text(query))
        rows = [dict(row._mapping) for row in result]

    return rows