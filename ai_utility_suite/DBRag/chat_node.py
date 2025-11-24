# Import necessary libraries
from typing import Union
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import AnyMessage
from .get_users_tables import get_tables_for_user
from .get_all_matched_tables import get_match_mismatch_tables
from langgraph.prebuilt.chat_agent_executor import AgentState
from .state_schema import (State, CustomState)
from langchain_openai import AzureChatOpenAI
from .config import (azure_openai_api_key, 
                    azure_api_version, azure_endpoint)

# Initialize the llm
llm = AzureChatOpenAI(azure_endpoint=azure_endpoint,
            api_version=azure_api_version,
            api_key=azure_openai_api_key)

# Define chat node
def chat_node(state: State) -> dict:
    """
    A chat node that creates an agent capable of answering user questions 
    or calling a tool to get the number of matched tables for the user.

    Args:
        state (State): A dictionary containing:
            - "user_name": (str) Name of the user.
            - "question": (list) List of message objects representing the conversation.

    Returns:
        dict: A dictionary with the assistant's final response message under the key "final_response".
    """

    user_name = state.get("user_name", "Guest")

    # === Define tool ===
    @tool
    def get_length_of_tables(user_name: str) -> Union[int, str]:
        """
        Return the number of matched tables available for the given user.
        """
        tables_list = get_tables_for_user(user_name=user_name)
        matched_tables, _ = get_match_mismatch_tables(tables_list_users=tables_list)
        if matched_tables:
            return len(matched_tables)
        return f"No matching tables found for the user: {user_name}."
    
    # === System Prompt Builder ===
    def prompt(state: CustomState) -> list[AnyMessage]:
        """
        Constructs the prompt for the assistant, including a system message.
        """

        user_name = state.get("user_name", "Guest")
        system_msg = {
            "role": "system",
            "content": (
                f"You are a helpful assistant. "
                f"User's name is {user_name}. "
                "If the user asks about the number of tables, call the get_length_of_tables tool. "
                "Otherwise, respond conversationally. "
                "Do not greet them with their email unless explicitly asked."
            )
        }
        return [system_msg] + state["messages"]

    # === Create a simple agent with tool ===
    model = create_react_agent(
        model=llm,
        tools=[get_length_of_tables],
        prompt=prompt,
        state_schema=CustomState
    )

    # Invoke the llm
    response = model.invoke({"messages": state["question"],
                             "user_name":user_name})

    return {"final_response": response["messages"][-1].content}
