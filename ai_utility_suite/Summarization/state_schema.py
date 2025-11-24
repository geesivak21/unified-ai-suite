# Import necessary libraries
from typing import TypedDict, Annotated, List
import operator
from langchain_core.documents import Document

# Define overall state for the Graph workflow
class OverallState(TypedDict):
    contents: list[str]
    summaries: Annotated[list, operator.add]
    collapsed_summaries: list[Document]
    final_summary: str

# Define worker state
class SummaryState(TypedDict):
    content: str
