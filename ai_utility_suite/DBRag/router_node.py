# Import necessary libraries
from langchain_openai import AzureChatOpenAI
from .config import (azure_openai_api_key, 
                    azure_api_version, azure_endpoint)
from .state_schema import (State, Router)
from .prompt import get_router_prompt

# Initialize the llm
llm = AzureChatOpenAI(azure_endpoint=azure_endpoint,
            api_version=azure_api_version,
            api_key=azure_openai_api_key)

# === Define Router Node ===
def router_node(state: State) -> str:
    """
    Uses LLM to decide whether to route to SQL flow (get_tables) 
    or chat flow (chat).

    Args:
        state (State): A dictionary containing:
            - "question": The natural language question from the user.

    Returns:
        dict: A dictionary with:
            - "route" (str): The routing decision, which will be either:
                - "get_tables" (if SQL flow is required), or
                - "chat" (if a chat-based response is required).
    """

    print("\n\n------Router Node (LLM-based)------\n\n")

    prompt = get_router_prompt(user_input=state["question"])

    # Invoke LLM with structured output
    llm_structured_output = llm.with_structured_output(Router)
    response: Router = llm_structured_output.invoke(prompt)

    print(f"Router decision: {response.route}")
    return {"route":response.route.value}   # return "get_tables" or "chat"

# === Define router conditional edge ===
def route_decision(state: State) -> str:
    """
    Decides the next route based on the current route in the state.

    Args:
        state (State): A dictionary containing the key "route" (str), which can be either:
            - "get_tables" (SQL flow), or
            - "chat" (chat flow).

    Returns:
        str: The next route, either "get_tables" or "chat".
    """

    goto = state["route"]
    if goto == "get_tables":
        return "get_tables"
    return "chat"