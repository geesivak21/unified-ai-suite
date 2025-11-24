# Import necessary libraries
from typing import TypedDict, List
from pydantic import BaseModel, Field
from enum import Enum
from langgraph.prebuilt.chat_agent_executor import AgentState

# Define state for Graph
class State(TypedDict):
    question:str
    user_name:str
    route:str
    tables:List[str]
    status:bool
    query:str
    matched_tables:List[str]
    query_result:str
    final_response:str

# Define the state for chat node
class CustomState(AgentState): 
    user_name: str

# === Define Enum for routing ===
class RouteNode(str, Enum):
    get_tables = "get_tables"
    chat = "chat"

# === Define structured output schema ===
class Router(BaseModel):
    route: RouteNode = Field(description="Route decision for the user query")

# Define structure output format for table extraction
class Table(BaseModel):
    """Table in SQL database."""

    name: List[str]|None = Field(default=None, description="Name of a table or tables in SQL database.")

# Define structure output format for query generation
class QueryOutput(BaseModel):
    """
    Structured output representing a generated SQL query.
    """
     
    query: str = Field(description="Syntatically valid SQL query.")