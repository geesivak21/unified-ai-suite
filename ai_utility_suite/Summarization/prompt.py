# Import necessary libraries
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.documents import Document

# Define summary prompt
def get_summary_prompt(context:str) -> ChatPromptTemplate:
    """
    Generates a summary prompt for a single page of document content.

    Args:
        context (str): The textual content of a single page from the document.

    Returns:
        ChatPromptTemplate: A prompt template used to summarize the page content.
    """
    
    summary_system_prompt = "Write a concise summary of the following:\n" \
                    "{context}"
    prompt = ChatPromptTemplate([
                                ("system", summary_system_prompt)
                                ])
    summary_prompt = prompt.invoke({"context":context})
    return summary_prompt

# Define consoliated summary prompt
def get_consolidated_summary_prompt(input: Document) -> ChatPromptTemplate:
    """
    Generates a consolidated summary prompt based on the provided document.

    Args:
        input (Document): A document object containing summaries, typically one per page.
        
    Returns:
        ChatPromptTemplate: A prompt template used to generate a summary across the document's content.
    """

    reduce_human_template = "The following is a set of summaries:\n" \
                            "{docs}\n" \
                            "Take these and distil into a final, consolidated summary " \
                            "of the main themes."
    prompt = ChatPromptTemplate([
        ("human", reduce_human_template)
    ])
    reducer_prompt = prompt.invoke(input)
    return reducer_prompt