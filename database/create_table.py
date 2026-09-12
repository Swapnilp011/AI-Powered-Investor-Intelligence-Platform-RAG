import os
import sys
from pathlib import Path

# Ensure root directory is on sys.path for direct script execution
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from database.sql_server import get_engine, create_database


def create_tables() -> None:
    engine = get_engine()
    db_type = os.getenv("DB_TYPE", "sqlserver").lower()

    if db_type == "sqlite":
        query = """
        CREATE TABLE IF NOT EXISTS financial_metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            company TEXT,
            year TEXT,
            revenue TEXT,
            net_income TEXT,
            operating_income TEXT,
            cash_flow TEXT,
            total_assets TEXT,
            total_liabilities TEXT,
            risk_factors TEXT,
            growth_drivers TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
    else:
        query = """
        IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'financial_metrics')
        BEGIN
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
        END
        """

    with engine.begin() as connection:
        connection.execute(text(query))

    print(f"financial_metrics table checked/created in {db_type.upper()}.")


if __name__ == "__main__":
    create_database()
    create_tables()