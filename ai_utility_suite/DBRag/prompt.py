# Import necessary library
from langchain_core.prompts import ChatPromptTemplate

# Define prompt for router node
def get_router_prompt(user_input: str) -> ChatPromptTemplate:
    """
    Constructs a prompt for an LLM to classify whether a user's input requires SQL query generation 
    or a simple chat response.
    
    Args:
        user_input (str): The user's natural language question.

    Returns:
        ChatPromptTemplate: A prompt object containing system and user messages,
                            ready to be sent to an LLM for table relevance identification.
    """

    system_template = (
        "You are a classifier. Your job is to decide if the user's question "
        "requires database/table/account operations (handled by 'get_tables') "
        "or if it just needs a simple conversational response (handled by 'chat').\n\n"
        "Classification Rules:\n"
        "- If the question asks about *tables, accounts, users, database details,* "
        "or anything requiring fetching/matching user data → return 'get_tables'.\n"
        "- If it is a general conversation, basic question, or about number/length of tables, return 'chat'.\n\n"
    )

    user_template = "{user_input}"

    # Prompt template
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", system_template),
        ("human", user_template)
    ])
    prompt = prompt_template.invoke({"user_input":user_input})
    return prompt

# Define prompt for getting list of tables
def get_tables_list_prompt(table_names:list[str], user_input:str) -> ChatPromptTemplate:
    """
    Constructs a chat-based prompt to identify potentially relevant SQL tables 
    based on a user's natural language question.

    Args:
        table_names (list[str]): A list of available SQL table names.
        user_input (str): The user's natural language question.

    Returns:
        ChatPromptTemplate: A prompt object containing system and user messages,
                            ready to be sent to an LLM for table relevance identification.
    """
    
    system_prompt = ("Return the names of ALL the SQL tables that MIGHT be relevant to the user question.\n"
                     "The tables are:\n\n"
                     "{table_names}\n\n"
                     "Remember to include ALL POTENTIALLY RELEVANT tables, even if you're not sure that they're needed.")
    
    user_prompt = "Question: {user_input}"
    
    prompt_template = ChatPromptTemplate([
        ("system", system_prompt),
        ("human", user_prompt),
    ])
    prompt = prompt_template.invoke({"table_names":table_names,
                                     "user_input":user_input})
    return prompt

# Define query generation prompt with schema
def get_query_generation_prompt_with_schema(dialect:str, top_k:int, table_info:str, user_input:str) -> ChatPromptTemplate:
    """
    Constructs a chat-based prompt template for generating SQL queries in a given dialect.

    This function creates a system and user prompt that guides an LLM to generate a 
    syntactically correct SQL query based on a natural language question. The generated 
    query is constrained by the provided SQL dialect, a limit on the number of results (top_k), 
    and a schema description (table_info).

    The system prompt enforces rules such as:
    - Using only available columns and tables.
    - Not selecting all columns.
    - Limiting results unless the user specifies otherwise.

    Args:
        dialect (str): The SQL dialect to be used (e.g.,"SQLite", "PostgreSQL", "MySQL").
        top_k (int): The maximum number of results the query should return by default.
        table_info (str): Schema description listing available tables and columns.
        input (str): User input.

    Returns:
        ChatPromptTemplate: A prompt template ready to be used with an LLM for SQL query generation.
    """

    system_prompt = """
    Given an input question, create a syntactically correct {dialect} query to
    run to help find the answer. Unless the user specifies in his question a
    specific number of examples they wish to obtain, always limit your query to
    at most {top_k} results. You can order the results by a relevant column to
    return the most interesting examples in the database.

    Never query for all the columns from a specific table, only ask for a
    few relevant columns given the question.

    Pay attention to use only the column names that you can see in the schema
    description. Be careful to not query for columns that do not exist. Also,
    pay attention to which column is in which table.

    Only use the following tables:
    {table_info}
    """

    user_prompt = "Question: {user_input}"

    query_prompt_template = ChatPromptTemplate(
        [("system", system_prompt), ("user", user_prompt)]
    )

    query_prompt = query_prompt_template.invoke({"dialect":dialect,
                                                 "top_k":top_k,
                                                 "table_info":table_info,
                                                 "user_input":user_input})
    return query_prompt