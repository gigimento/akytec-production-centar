import pyodbc
import pandas as pd
import warnings
from config import DB_SERVER, DB_NAME

warnings.filterwarnings("ignore", message="pandas only supports SQLAlchemy")


def get_connection():
    """Establish connection to SQL Server."""
    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={DB_SERVER};"
        f"DATABASE={DB_NAME};"
        f"Trusted_Connection=yes;"
    )
    return pyodbc.connect(conn_str)


def run_query(sql: str, params: tuple = None) -> pd.DataFrame:
    """Execute SQL query and return DataFrame."""
    try:
        conn = get_connection()
        df = pd.read_sql(sql, conn, params=params)
        conn.close()
        return df
    except Exception as e:
        print(f"DB Error: {e}")
        return pd.DataFrame()


def test_connection() -> bool:
    """Test database connectivity."""
    try:
        conn = get_connection()
        conn.close()
        return True
    except Exception:
        return False
