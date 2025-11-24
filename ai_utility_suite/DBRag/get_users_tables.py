# Import necessary libraries
from typing import List
import time
from .config import (db_name, db_user,
                    db_password, db_host,
                    db_port, ssl_mode)
import psycopg2

def get_tables_for_user(user_name:str,
                        max_retries:int=3, retry_delay:float=1.0) -> List[str]:
    """
    Retrieves a list of tables that a user has access to based on their roles and permissions.

    This function executes a series of queries to check the user's access rights and 
    fetch the tables they are allowed to access. It involves checking the user's information,
    associated group permissions, model access, and retrieving the relevant tables from the 
    database. If the user has no access, an exception is raised.

    Args:
        user_name (str): The login name (usually an email) of the user whose table access is being queried.
        max_retries (int): Max retry attempts on failure.
        retry_delay (float): Delay between retries (in seconds).

    Returns:
        List: 
            A list of strings representing the tables the user has access to. These tables 
            are derived from the `ir_model` table based on the user's group access.

    Raises:
        ValueError: 
            If the user has no access (i.e., their account status is inactive or they do not have 
            the necessary permissions), this exception is raised with a message indicating the lack 
            of access.
        
        Exception: 
            If there are any issues executing the queries (e.g., database errors, failed fetches), 
            an exception message is printed, and the transaction is rolled back.
    """

    # === Table 1 ===
    attempt=0
    while attempt < max_retries:
        try:
            print("\n\n-----Resource group users-------\n\n")

            # Connect to the PostgreSQL database using psycopg2
            conn = psycopg2.connect(
                dbname=db_name,         # Name of the database
                user=db_user,           # Database username
                password=db_password,   # User password
                host=db_host,           # Database host/IP
                port=db_port,           # Database port
                sslmode=ssl_mode  # SSL mode, defaulting to 'disable' if not set
            )

            cursor1 = conn.cursor()
            cursor1.execute(f"SELECT * FROM res_users WHERE login='{user_name}';")
            res_users_results = cursor1.fetchall()

            if not res_users_results:
                raise ValueError(f"User '{user_name}' not found in res_users table.")
            # Extract id and active
            user_id = res_users_results[0][0] # id → user id
            status = res_users_results[0][1] # active → account_status(True/False)

            columns = [desc[0] for desc in cursor1.description]
            print(f"\nColumns: {columns}\n")
            print(f"\nResults: {res_users_results}\n")
            print(f"\nUser ID: {user_id} and Account status: {status}\n")
            break
        except Exception as e:
            attempt += 1
            print(f"[Attempt {attempt}] Error fetching user info: {e}")

            try:
                conn.rollback()
            except Exception:
                pass
            
            if attempt >= max_retries:
                status = False
                raise RuntimeError(f"Failed to fetch user info after {max_retries} attempts: {e}")
            time.sleep(retry_delay)
        finally:
            try:
                conn.close()
            except Exception: 
                pass

    if status:
        # === Table 2 ====
        attempt = 0
        while attempt < max_retries:
            try:
                print("\n\n-----Resource group users relational table-------\n\n")

                # Connect to the PostgreSQL database using psycopg2
                conn = psycopg2.connect(
                    dbname=db_name,         # Name of the database
                    user=db_user,           # Database username
                    password=db_password,   # User password
                    host=db_host,           # Database host/IP
                    port=db_port,           # Database port
                    sslmode=ssl_mode  # SSL mode, defaulting to 'disable' if not set
                )

                cursor2 = conn.cursor()
                cursor2.execute(f"SELECT * FROM res_groups_users_rel where uid={user_id};")
                res_grp_users_rel_results = cursor2.fetchall()

                # Extract gid
                grp_ids = [gid for gid,_ in res_grp_users_rel_results] # gid → group ids

                columns = [desc[0] for desc in cursor2.description]
                print(f"\nColumns: {columns}\n")
                print(f"\nResults: {res_grp_users_rel_results}\n")
                print(f"\n Group ids: {grp_ids}\n")
                break
            except Exception as e:
                attempt += 1
                print(f"[Attempt {attempt}] Error fetching group IDs: {e}")

                try:
                    conn.rollback()
                except Exception:
                    pass

                if attempt >= max_retries:
                    raise RuntimeError(f"Failed to fetch group IDs after {max_retries} attempts: {e}")
                time.sleep(retry_delay)
            finally:
                try:
                    conn.close()
                except Exception: 
                    pass
        if not grp_ids:
            raise ValueError(f"User '{user_name}' does not belong to any groups.")


        # === Table 3 ====
        attempt = 0
        while attempt < max_retries:
            try:
                print("\n\n-----IR model Access-------\n\n")

                # Connect to the PostgreSQL database using psycopg2
                conn = psycopg2.connect(
                    dbname=db_name,         # Name of the database
                    user=db_user,           # Database username
                    password=db_password,   # User password
                    host=db_host,           # Database host/IP
                    port=db_port,           # Database port
                    sslmode=ssl_mode  # SSL mode, defaulting to 'disable' if not set
                )

                cursor3 = conn.cursor()
                # Convert group ids list to a comma-separated string
                # Generate %s placeholders for psycopg2
                placeholders = ','.join(['%s'] * len(grp_ids))
                # print(f"Placeholers: {placeholders}")
                query = f"SELECT * FROM ir_model_access WHERE group_id IN ({placeholders});"
                cursor3.execute(query, grp_ids)
                # print(f"Running query: {query}") 
                ir_model_access_results = cursor3.fetchall()

                # Extract model_id
                model_ids = [val[3] for val in ir_model_access_results] # model_id → model ids
                # Map model_id to respective crud access
                crud_access_map = {val[3]:{"create": val[7],
                                    "read": val[5],
                                    "update":val[6],
                                    "delete": val[8]} for val in ir_model_access_results} # CRUD access
                
                columns = [desc[0] for desc in cursor3.description]
                print(f"\nColumns: {columns}\n")
                print(f"\nResults: {ir_model_access_results[:2]}\n")
                print(f"\nModel IDs: {model_ids[:2]}, length: {len(model_ids)}\n")
                print(f"\nCRUD Access: {dict(list(crud_access_map.items())[:2])}, length: {len(crud_access_map)}\n")
                break
            except Exception as e:
                attempt += 1
                print(f"[Attempt {attempt}] Error fetching model access: {e}")

                try:
                    conn.rollback()
                except Exception:
                    pass

                if attempt >= max_retries:
                    raise RuntimeError(f"Failed to fetch model access after {max_retries} attempts: {e}")
                time.sleep(retry_delay)
            finally:
                try:
                    conn.close()
                except Exception: 
                    pass
        if not model_ids:
            raise ValueError(f"No model access found for user '{user_name}'.")


        # === Table 4 ====
        attempt=0
        while attempt < max_retries:
            try:
                print("\n\n-----IR model-------\n\n")
                # Connect to the PostgreSQL database using psycopg2
                conn = psycopg2.connect(
                    dbname=db_name,         # Name of the database
                    user=db_user,           # Database username
                    password=db_password,   # User password
                    host=db_host,           # Database host/IP
                    port=db_port,           # Database port
                    sslmode=ssl_mode  # SSL mode, defaulting to 'disable' if not set
                )

                cursor4 = conn.cursor()
                # Convert model ids list to a comma-separated string
                # Generate %s placeholders
                placeholders = ','.join(['%s'] * len(model_ids))
                query = f"SELECT * FROM ir_model WHERE id IN ({placeholders});"
                cursor4.execute(query, model_ids)
                ir_model_results = cursor4.fetchall()

                # Extract tables
                tables_list = [val[2].replace(".", "_") if isinstance(val[2], str) else val[2] 
                            for val in ir_model_results] # model → table name
                # Map model_id to respective tables
                tables_and_id_map = {val[0]: (val[2].replace(".", "_") if isinstance(val[2], str) else val[2]) 
                                    for val in ir_model_results} # model id map Table 

                columns = [desc[0] for desc in cursor4.description]
                print(f"\nColumns: {columns}\n")
                print(f"\nResults: {ir_model_results[:2]}\n")
                print(f"\nList of tables: {tables_list[:2]} and length: {len(tables_list)}\n")
                print(f"\nTables and ID map: {dict(list(tables_and_id_map.items())[:2])} and length: {len(tables_and_id_map)}\n")

                return tables_list # returns list of tables
            
            except Exception as e:
                attempt += 1
                print(f"[Attempt {attempt}] Error fetching model tables: {e}")

                try:
                    conn.rollback()
                except Exception:
                    pass

                if attempt >= max_retries:
                    raise RuntimeError(f"Failed to fetch table names after {max_retries} attempts: {e}")
                time.sleep(retry_delay)
            finally:
                try:
                    conn.close()
                except Exception: 
                    pass
    else:
        tables_list = None
        print(f"User {user_name} has no access.")
        return tables_list