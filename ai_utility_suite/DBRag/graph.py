# Import necessary libraries
from langgraph.graph import StateGraph, START, END
from .state_schema import State
from .nodes import (get_tables, check_status, 
                   write_query, execute_query, 
                   generate_answer, check_read_access_only)
from .router_node import (router_node, route_decision)
from .chat_node import chat_node

# Define the graph
def build_graph():
    """
    Constructs and compiles a LangGraph pipeline for handling natural language questions
    over a SQL database. The pipeline includes the following steps:

    1. get_tables: Retrieves the list of relevant tables accessible to the user.
    2. write_query: Converts the user's natural language question into an SQL query.
    3. check_read_access_only: Validates the SQL query is a SELECT (read-only) query.
    4. execute_query: Executes the validated SQL query.
    5. generate_answer: Converts the SQL query result into a natural language answer.

    Conditional transitions:
    - If no relevant tables are found → END
    - If the SQL query is not read-only → END

    Returns:
        graph (StateGraph): A compiled LangGraph object ready to be invoked with user input.
    """
    
    # Create the graph builder with the shared state schema
    builder = StateGraph(State)

    # Add the core nodes to the pipeline
    builder.add_node("router_node", router_node)
    builder.add_node("chat_node", chat_node)
    builder.add_node("get_tables", get_tables)
    builder.add_node("write_query", write_query)
    builder.add_node("execute_query", execute_query)
    builder.add_node("generate_answer", generate_answer)

    # Define flow from start to first node
    builder.set_entry_point("router_node")

    # Conditional routing from router node
    builder.add_conditional_edges("router_node", route_decision,
                                  {"chat":"chat_node",
                                   "get_tables":"get_tables"})
    builder.add_edge("chat_node", END)
    
    # Conditional routing from get_tables
    builder.add_conditional_edges(
        "get_tables", check_status, 
        {
            "write_query": "write_query",
            "END": END
        }
    )

    # Conditional routing from write_query
    builder.add_conditional_edges(
        "write_query", check_read_access_only, 
        {
            "execute_query": "execute_query",
            "END": END
        }
    )

    # Final linear steps
    builder.add_edge("execute_query", "generate_answer")
    builder.add_edge("generate_answer", END)

    # Compile and return the graph
    return builder.compile()