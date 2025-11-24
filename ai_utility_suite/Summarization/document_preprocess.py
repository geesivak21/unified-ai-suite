# Import necessary libraries
from langchain_community.document_loaders import PDFPlumberLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from typing import List

# Define function to generate document chunks
def get_document_chunks(file_name: str) -> List[Document]:
    """
    Generate document chunks.

    Args:
        file_name (str): The name of the PDF file inside the 'datasets' folder.

    Returns:
        List[Document]: Document objects containing the document chunks.
    """

    # Load the pdf document
    docs = PDFPlumberLoader(file_path=file_name).load()

    # Initialize the text splitter
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500,
                                                chunk_overlap=200,
                                                separators=["\n\n", "\n", ".", ""])
    split_docs = text_splitter.split_documents(documents=docs)
    print("\n----Preprocessing successful------\n")
    print(f"\n-----{split_docs[:2]}-----\n")
    return split_docs

