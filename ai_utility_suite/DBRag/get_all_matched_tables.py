# Import necessary libraries
from typing import List, Tuple
import time
from .config import (db_name, db_user,
                    db_password, db_host,
                    db_port, ssl_mode)
import psycopg2

# Define a function to get a list of match and mismatch tables
def get_match_mismatch_tables(tables_list_users:List, max_retries: int=3, 
                              retry_delay:float = 1.0) -> Tuple[List[str], List[str]]:
    """
    Compares a user-provided list of table names with the actual tables in the database.

    Args:
        tables_list_users (List[str]): List of table names provided by the user.
        max_retries (int): Max retry attempts on failure.
        retry_delay (float): Delay between retries (in seconds).

    Returns:
        Tuple[List[str], List[str]]: A tuple containing two lists:
            - matched_tables: Tables that exist in the database.
            - mismatched_tables: Tables that do not exist in the database.
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
            # Create a cursor object to execute SQL queries and fetch results
            cursor = conn.cursor()
            cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' AND table_type = 'BASE TABLE';")
            
            # Extract the actual table names from query results
            tables = cursor.fetchall()
            main_tables_list = [table[0] for table in tables]

            print(f"Length of all tables in DB: {len(main_tables_list)}")

            matched_tables = [table for table in tables_list_users if table in main_tables_list]
            mismatched_tables = [table for table in tables_list_users if table not in main_tables_list]

            print(f"Matched tables: {matched_tables[:5]} ,Length of Matched tables: {len(matched_tables)}")
            print(f"Mismatched tables: {mismatched_tables[:5]}, Length of Mismatched tables: {len(mismatched_tables)}")
            
            return matched_tables, mismatched_tables
        
        except Exception as e:
            attempt += 1
            print(f"[Attempt {attempt}] Error fetching table metadata: {e}")

            try:
                conn.rollback()
            except Exception:
                pass

            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...\n")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Raising exception.")
                raise RuntimeError(
                    f"Failed to fetch table metadata after {max_retries} attempts. "
                    f"Last error: {str(e)}"
                )
        finally:
            try:
                conn.close()
            except Exception:
                pass