# Import necessary libraries
from langchain_openai import AzureChatOpenAI
from .config import (azure_openai_api_key, azure_api_version, 
                     azure_endpoint, azure_deployment_name)
from langgraph.types import Send
from .state_schema import OverallState, SummaryState
from .prompt import get_summary_prompt, get_consolidated_summary_prompt
from langchain_core.documents import Document
from langchain.chains.combine_documents.reduce import split_list_of_docs, collapse_docs
from typing import Literal
import tiktoken

# Initialize the llm model
llm = AzureChatOpenAI(azure_endpoint=azure_endpoint,
            api_version=azure_api_version,
            api_key=azure_openai_api_key,
            azure_deployment=azure_deployment_name)

# Define token max
token_max = 1500

#=== Define node 1 - generate summary node ===
def generate_summary(state:SummaryState) -> dict:
    """Call node 1."""

    print("\n\n--------Node 1: generate summary - worker state---------------\n\n")
    prompt = get_summary_prompt(context=state["content"])
    response = llm.invoke(prompt)
    return {"summaries":[response.content]}

# Define conditional edge → send each page content to the generate summary node
def map_summaries(state:OverallState):
    print("\n\n--------Summary node---------------\n\n")
    return [Send("generate_summary", {"content":content}) for content in state["contents"]]

#=== Define node 2 - collect summaries ===
def collect_summaries(state:OverallState):
    """Call node 2."""
    print("\n\n--------Node 2: Collect summaries---------------\n\n")
    summary = state["summaries"][0]
    print(f"\n\n----summaries: {summary}-------\n\n")
    return {"collapsed_summaries": [Document(page_content=summary) for summary in state["summaries"]]}

#=== Define node 3 - collapse summaries ===
# Define a function to get the total tokens
def get_token_length(docs:Document) -> int:
    """Get number of tokens for input contents."""
    model = azure_deployment_name
    encoder = tiktoken.encoding_for_model(model)
    # return sum([llm.get_num_tokens(doc.page_content) for doc in docs])
    return sum(len(encoder.encode(doc.page_content)) for doc in docs)

# Define reducer function → consolidates summary
def _reducer(input:dict):
    # print(f"\n\n------Input to consolidation prompt: {input}-------------\n\n")
    prompt = get_consolidated_summary_prompt(input)
    response = llm.invoke(prompt)
    # print(f"\n\n------Reducer response: {response}------\n\n")
    return response.content

# Define node 3
def collapse_summaries(state:OverallState):
    """Call node 3."""
    print("\n\n--------Collapse summary node---------------\n\n")
    doc_lits = split_list_of_docs(state["collapsed_summaries"],
                                    length_func=get_token_length,
                                    token_max=token_max)
    results = []
    for docs_list in doc_lits:
        results.append(collapse_docs(docs_list, _reducer))
    
    return {"collapsed_summaries":results}

#=== Define conditional edge → to decide whether to collapse or generate summary ===#
def should_collapse(state: OverallState,) -> Literal["collapse_summaries", "generate_final_summary"]:
    print("\n\n--------Conditional edge: should collapse---------------\n\n")
    num_tokens = get_token_length(state["collapsed_summaries"])
    if num_tokens > token_max:
        return "collapse_summaries"
    else:
        return "generate_final_summary"

#=== Define node 4 → generate final summary ===
def generate_final_summary(state: OverallState):
    """Call node 4."""
    response = _reducer(state["collapsed_summaries"])
    return {"final_summary": response}

