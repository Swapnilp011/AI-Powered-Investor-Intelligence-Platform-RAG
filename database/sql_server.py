import os
from urllib.parse import quote_plus
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

load_dotenv()


def get_engine(database: str | None = None):
    """
    Create SQLAlchemy engine for SQL Server with fallback support.
    Supports pyodbc (with native odbc_connect), pymssql, and SQLite fallback.
    """
    db_name = database or os.getenv("SQLSERVER_DATABASE", "investor_intelligence")
    db_type = os.getenv("DB_TYPE", "sqlserver").lower()

    if db_type == "sqlite":
        os.makedirs("./data", exist_ok=True)
        return create_engine(f"sqlite:///./data/{db_name}.db")

    host = os.getenv("SQLSERVER_HOST", "localhost")
    port = os.getenv("SQLSERVER_PORT", "1433")
    user = os.getenv("SQLSERVER_USER", "sa")
    password = os.getenv("SQLSERVER_PASSWORD", "")
    driver = os.getenv("SQLSERVER_DRIVER", "ODBC Driver 17 for SQL Server")
    trusted_conn = os.getenv("SQLSERVER_TRUSTED_CONNECTION", "no").lower() in ("yes", "true", "1")

    # Build server specification string
    if "\\" in host:
        # Named instance e.g. localhost\SQLEXPRESS
        server_spec = host
    elif port and port != "1433":
        server_spec = f"{host},{port}"
    else:
        server_spec = host

    # Try pyodbc first
    try:
        import pyodbc
        if trusted_conn:
            odbc_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server_spec};"
                f"DATABASE={db_name};"
                f"Trusted_Connection=yes;"
                f"TrustServerCertificate=yes;"
            )
        else:
            odbc_str = (
                f"DRIVER={{{driver}}};"
                f"SERVER={server_spec};"
                f"DATABASE={db_name};"
                f"UID={user};"
                f"PWD={password};"
                f"TrustServerCertificate=yes;"
            )
        
        quoted_odbc_str = quote_plus(odbc_str)
        return create_engine(f"mssql+pyodbc:///?odbc_connect={quoted_odbc_str}", fast_executemany=True)

    except ImportError:
        # Fallback to pymssql driver
        encoded_user = quote_plus(user)
        encoded_password = quote_plus(password)
        if trusted_conn:
            conn_url = f"mssql+pymssql://@{server_spec}/{db_name}"
        else:
            conn_url = f"mssql+pymssql://{encoded_user}:{encoded_password}@{server_spec}/{db_name}"
        return create_engine(conn_url)


def create_database() -> None:
    """
    Create the target SQL Server database if it does not exist.
    Connects to 'master' database first.
    """
    db_type = os.getenv("DB_TYPE", "sqlserver").lower()
    if db_type == "sqlite":
        os.makedirs("./data", exist_ok=True)
        return

    target_db = os.getenv("SQLSERVER_DATABASE", "investor_intelligence")
    
    try:
        master_engine = get_engine(database="master").execution_options(
            isolation_level="AUTOCOMMIT"
        )

        query = f"""
        IF NOT EXISTS (SELECT name FROM sys.databases WHERE name = N'{target_db}')
        BEGIN
            CREATE DATABASE [{target_db}];
        END
        """

        with master_engine.connect() as conn:
            conn.execute(text(query))

        print(f"Database '{target_db}' checked / created successfully in SQL Server.")
    except Exception as exc:
        print(f"Warning: Could not check/create SQL Server database '{target_db}': {exc}")
