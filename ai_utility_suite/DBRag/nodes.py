# Import necessary libraries
from typing import List
from .state_schema import (State, Table, QueryOutput)
from .prompt import (get_tables_list_prompt,
                    get_query_generation_prompt_with_schema)
from langchain_openai import AzureChatOpenAI
from .config import (connection_string, azure_openai_api_key, 
                    azure_api_version, azure_endpoint)
from .get_table_info import get_filtered_table_info
from .get_users_tables import get_tables_for_user
import re
from .get_all_matched_tables import get_match_mismatch_tables
from sqlalchemy import create_engine
from langchain_community.utilities import SQLDatabase
import time

# Initialize the llm
llm = AzureChatOpenAI(azure_endpoint=azure_endpoint,
            api_version=azure_api_version,
            api_key=azure_openai_api_key)

#=== Define node 1 ===
def get_tables(state:State) -> List[str]:
    """
    Retrieves the list of tables based on user's access permissions and table relevance.

    Args:
        state (State): A dictionary containing:
            - "user_name": The user for whom table access is checked.
            - "question": The natural language question from the user.

    Returns:
        dict: A dictionary with:
            - "tables": List of relevant table names (if any).
            - "status": Boolean indicating whether relevant tables were found.
    """

    print("\n\n----------Get_tables node----------\n\n")
    status = False
    table_names_users = get_tables_for_user(user_name=state["user_name"])
    if table_names_users:
        status = True
        return {"tables":table_names_users,
                "status":status}
    
    return {"status":status}

# === Define conditonal edge ===
def check_status(state:State) -> dict:
    """
    Determines the next node in the flow based on whether relevant tables were found.

    Args:
        state (State): A dictionary containing the "status" key.

    Returns:
        str: The name of the next node. 
             Returns "write_query" if status is True, otherwise "END".
    """

    return "write_query" if state.get("status") else "END"

#=== Define node 2 ===
def write_query(state:State) -> dict:
    """
    Generates a SQL query based on user question.

    Args:
        state (State): A dictionary containing the user's natural language question under the key "question".

    Returns:
        dict: A dictionary with the key "query" containing the generated SQL query as a string.
    """

    print("\n\n------Write query node--------\n\n")

    # Step 1: Retrieve the list of relevant tables passed from the previous node
    tables_list = state.get("tables")
    
    # Step 2: Choose the matching tables
    final_matched_tables_list, _ = get_match_mismatch_tables(tables_list_users=tables_list)

    # Step 3: Filter the user tables → select only the relevant tables from a given set of tables
    prompt = get_tables_list_prompt(table_names=final_matched_tables_list, 
                                    user_input=state["question"])

    llm_structured_output = llm.with_structured_output(Table)
    response = llm_structured_output.invoke(prompt)
    tables = response.name
    print(f"\n\n------Selected list of tables: {tables}, length: {len(tables)}--------\n\n")

    if tables:
        # get the table schema → table name + column names
        table_info = get_filtered_table_info(tables_list=tables[:50])

        print(f"\n\n---Table schema: {table_info[:100]}---\n\n")

        prompt = get_query_generation_prompt_with_schema(dialect="postgresql",
                                            top_k=5,
                                            table_info=table_info,
                                            user_input=state["question"])
    else:
        print("------No relevant tables found---------")
        return {"query":"No relevant tables found."}
    

    # Step 4: Use the LLM to generate a structured SQL query    
    llm_structured = llm.with_structured_output(QueryOutput)
    response = llm_structured.invoke(prompt)

    # Step 5: Return the generated query
    return {"query":response.query,
            "matched_tables":final_matched_tables_list}

# === Define conditonal edge ===
def check_read_access_only(state:State) -> dict:
    """
    Validates that the generated SQL query is a READ (SELECT) query.
    
    Args:
        state (dict): Dictionary containing the generated SQL query.
    
    Returns:
        dict: Dictionary with the same SQL query if it passes the check.
    """

    query = state["query"].strip().lower()
    print(f"Query Generated: {query}")
    # Remove comments and leading whitespace
    query_no_comments = re.sub(r"--.*?(\n|$)", "", query).strip()

    # Check if it starts with SELECT
    if not query_no_comments.startswith("select"):
       return "END"

    return "execute_query"  #goto execute_query node


# === Define node 3 ===
def execute_query(state:State, max_retries: int = 3, retry_delay: float = 1.0) -> dict:
    """
    Executes the SQL query stored in the state and returns the result.

    Args:
        state (dict): Must contain:
            - "query": SQL string to execute
            - "matched_tables": list of allowed table names
        max_retries (int): Number of retry attempts on failure
        retry_delay (float): Delay between retries in seconds

    Returns:
        dict: A dictionary containing the key `"query_result"` with the result 
              of the query execution.
    """
    
    print("\n\n-------Execute query node--------\n\n")
    attempt = 0
    while attempt < max_retries:
        try:
            # Set up the engine with pool_pre_ping to avoid dead connections
            engine = create_engine(connection_string, pool_pre_ping=True)

            # Create SQLDatabase object with allowed tables only
            db = SQLDatabase(engine, include_tables=state["matched_tables"])

            # Run the query
            result = db.run(command=state["query"])
            print(f"Query Result:\n{result}")
            return {"query_result": result}

        except Exception as e:
            attempt += 1
            print(f"[Attempt {attempt}] Error executing query: {e}")

            if attempt < max_retries:
                print(f"Retrying in {retry_delay} seconds...\n")
                time.sleep(retry_delay)
            else:
                print("Max retries reached. Failing gracefully.")
                return {"query_result": f"Execution failed after {max_retries} attempts. Error: {str(e)}"}

#=== Define node 4 ===
def generate_answer(state: State):
    """
    Generates a response to the user's question based on the SQL query and its result.

    Args:
        state (State): A dictionary containing:
            - "question": The user's natural language question.
            - "query": The SQL query generated to answer the question.
            - "query_result": The result of executing the SQL query.

    Returns:
        dict: A dictionary with the key "answer" containing the LLM-generated response.
    """
    
    print("\n\n---------Execute Node-------------\n\n")
    prompt = (
        "Given the following user question, corresponding SQL query, "
        "and SQL result, answer the user question.\n\n"
        f"Question: {state['question']}\n"
        f"SQL Query: {state['query']}\n"
        f"SQL Result: {state['query_result']}"
    )
    response = llm.invoke(prompt)
    return {"final_response": response.content}