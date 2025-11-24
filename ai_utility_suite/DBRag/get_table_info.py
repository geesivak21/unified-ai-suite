# Import necessary libraries
from typing import List
from .config import (db_name, db_user,
                    db_password, db_host,
                    db_port, ssl_mode)
import psycopg2
import time

# Define function to return the schema of the table
def get_filtered_table_info(tables_list:List[str], schema='public',
                            max_retries: int = 3, retry_delay: float = 1.0) -> str:
    """
    Fetch column info for a filtered list of tables from PostgreSQL.

    Args:
        tables_list (list): List of table names to include
        schema (str): Schema to search (default = 'public')
        max_retries (int): Max retry attempts on failure
        retry_delay (float): Delay between retries (in seconds)

    Returns:
        str: A string representation of table schemas to feed into LLM
    """

    if not tables_list:
        return "No tables provided."

    def normalize_type(dtype):
        if dtype in ('character varying', 'varchar'):
            return 'text'
        elif dtype.startswith('timestamp'):
            return 'timestamp'
        elif dtype.startswith('character'):
            return 'char'
        return dtype

    placeholders = ','.join(['%s'] * len(tables_list))
    query = f"""
    SELECT table_name, column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = %s
      AND table_name IN ({placeholders})
    ORDER BY table_name, ordinal_position
    """

    attempt = 0
    while attempt < max_retries:
        try:
            # Connect to the PostgreSQL database using psycopg2
            conn = psycopg2.connect(
                dbname=db_name,         # Name of the database
                user=db_user,           # Database username
                password=db_password,   # User password
                host=db_host,           # Database host/IP
                port=db_port,           # Database port
                sslmode=ssl_mode  # SSL mode, defaulting to 'disable' if not set
            )
            
            cursor = conn.cursor()
            cursor.execute(query, [schema] + tables_list)
            rows = cursor.fetchall()

            table_columns = {}
            for table, column, dtype in rows:
                simple_type = normalize_type(dtype)
                table_columns.setdefault(table, []).append(f"{column} ({simple_type})")

            schema_info_str = ""
            for table in sorted(table_columns.keys()):
                columns = table_columns[table]
                schema_info_str += f"Table: {table}\nColumns: {', '.join(columns)}\n\n"

            return schema_info_str.strip()
        except Exception as e:
            attempt += 1
            print(f"[Attempt {attempt}] Error fetching table info: {e}")
            if conn:
                try:
                    conn.rollback()
                except Exception:
                    pass
            if attempt >= max_retries:
                raise RuntimeError(f"Failed to fetch table info after {max_retries} attempts: {e}")
            time.sleep(retry_delay)

        finally:
            try:
                conn.close()
            except Exception:
                pass
