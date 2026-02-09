"""MySQL connection and safe execution for RetailGPT."""
import mysql.connector
from typing import Any, List, Optional

from config import get_db_config

# Schema description for the LLM (critical for accuracy)
SCHEMA_DESCRIPTION = """
Tables:
- products: id (INT PK), sku (VARCHAR), name (VARCHAR), brand (VARCHAR), category (VARCHAR), unit_price (DECIMAL), created_at (TIMESTAMP)
- inventory: id (INT PK), product_id (INT FK -> products.id), quantity (INT), warehouse (VARCHAR), updated_at (TIMESTAMP)
- sales: id (INT PK), product_id (INT FK -> products.id), quantity (INT), unit_price (DECIMAL), total_amount (DECIMAL), sale_date (DATE), region (VARCHAR), created_at (TIMESTAMP)

Brands in data: Adidas, Nike.
Use sale_date for time filters. Use products.brand for brand filters. Join sales/product via product_id.
"""


def get_connection():
    return mysql.connector.connect(**get_db_config())


def run_read_only_query(sql: str, params: Optional[tuple] = None) -> List[Any]:
    """Execute a SELECT query and return rows. Rejects non-SELECT for safety."""
    sql_stripped = sql.strip().upper()
    if not sql_stripped.startswith("SELECT"):
        raise ValueError("Only SELECT queries are allowed.")
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return rows
    finally:
        conn.close()
