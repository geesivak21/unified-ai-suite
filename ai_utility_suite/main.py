def run():
    import sys, os
    sys.path.append(os.path.dirname(__file__))

    import streamlit as st
    from Extraction import azure_doc_ocr
    from DBRag import smart_qa_assistant
    from Summarization import rfp_summarizer

    st.set_page_config(page_title="AI Utility Suite", layout="wide")

    st.sidebar.title("GainHub")
    page = st.sidebar.radio(
        "Go to:",
        (
            "📄 Document Summarizer",
            "🧾 Document Extractor",
            "🧠 Smart Q&A Assistant"
        )
    )

    if page == "📄 Document Summarizer":
        rfp_summarizer.run()

    elif page == "🧾 Document Extractor":
        azure_doc_ocr.run()

    elif page == "🧠 Smart Q&A Assistant":
        smart_qa_assistant.run()
