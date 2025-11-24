import streamlit as st
from langgraph.graph import StateGraph, START, END
from .state_schema import OverallState
from .nodes import (
    map_summaries,
    generate_summary, 
    collect_summaries,
    should_collapse, 
    collapse_summaries, 
    generate_final_summary
)
from .document_preprocess import get_document_chunks
import time
import os
import json

# ---------------- Utility Functions ----------------
def stream_text(full_text, delay: float = 0.05):
    """Stream tokens safely, then show as markdown at the end."""
    placeholder = st.empty()
    output = ""
    for token in full_text.split():
        output += token + " "
        placeholder.text(output)   # live update
        time.sleep(delay)

    placeholder.markdown(full_text)  # final clean render

def run():
    """Run the RFP Summarizer Streamlit UI."""

    # ---------------- Streamlit UI ----------------
    st.set_page_config(page_title="Document Summarizer", layout="wide")
    st.title("📄 Document Summarizer")

    # Folder setup
    UPLOAD_DIR = "datasets"
    UPLOAD_CACHE = "cache"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    os.makedirs(UPLOAD_CACHE, exist_ok=True)

    # Initialize key if not already
    if "uploader_key" not in st.session_state:
        st.session_state["uploader_key"] = "file_uploader_1"

    # File uploader with dynamic key
    uploaded_file = st.file_uploader(
        "Upload your RFP (PDF)", 
        type=["pdf"], 
        key=st.session_state["uploader_key"]
    )

    # Clear button
    if st.button("🗑️ Clear File & Reset"):
        # Reset file uploader by changing its key
        st.session_state["uploader_key"] = f"file_uploader_{time.time()}"
        st.rerun()
        
    # Early exit if no file uploaded
    if uploaded_file is None:
        st.info("Please upload a PDF file to start summarizing.")
        st.stop()

    # Set paths and attempt to load cache
    save_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
    json_path = os.path.join(UPLOAD_CACHE, f"{uploaded_file.name}.json")

    file = None
    final_response = None

    if os.path.exists(json_path):
        try:
            with open(json_path, "r") as f:
                data = json.load(f)
                file = data.get("file_name")
                final_response = data.get("response")
        except Exception as e:
            st.warning(f"⚠️ Failed to load cache: {e}")

    # Save uploaded file
    if not os.path.exists(save_path):
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"✅ File saved to `{save_path}`")
    else:
        st.info(f"ℹ️ File already exists at `{save_path}`")

    # Show "Use Cache" checkbox if cache exists
    use_cache = False
    if file == uploaded_file.name and final_response is not None:
        use_cache = st.checkbox("Use Cached Results", value=False)

    # Button to generate summary
    if st.button("Generate Summary"):

        if not use_cache:
            # Preprocess the document
            with st.spinner("🔍 Preprocessing document..."):
                try:
                    split_docs = get_document_chunks(file_name=save_path)
                except Exception as e:
                    st.error(f"❌ Error while splitting document: {e}")
                    st.stop()

            st.success(f"✅ Document loaded and split into {len(split_docs)} chunks")

            with st.spinner("🧠 Summarizing document... this may take a while ⏳"):
                # Build the summarization graph
                builder = StateGraph(OverallState)
                builder.add_node("generate_summary", generate_summary) 
                builder.add_node("collect_summaries", collect_summaries)
                builder.add_node("collapse_summaries", collapse_summaries)
                builder.add_node("generate_final_summary", generate_final_summary)

                # Define edges
                builder.add_conditional_edges(START, map_summaries, ["generate_summary"])
                builder.add_edge("generate_summary", "collect_summaries")
                builder.add_conditional_edges("collect_summaries", should_collapse)
                builder.add_conditional_edges("collapse_summaries", should_collapse)
                builder.add_edge("generate_final_summary", END)

                # Compile graph
                graph = builder.compile()

                # Run graph on content chunks
                try:
                    response = graph.invoke(
                        {"contents": [doc.page_content for doc in split_docs]}
                    )
                except Exception as e:
                    st.error(f"❌ Error during summarization: {e}")
                    st.stop()

            st.subheader("📌 Final Summary")
            stream_text(response["final_summary"])

            # Save cache
            final_response = {
                "file_name": uploaded_file.name,
                "response": response["final_summary"]
            }

            try:
                with open(json_path, "w") as f:
                    json.dump(final_response, f, indent=4)
                st.success(f"✅ Summary cached at `{json_path}`")
            except Exception as e:
                st.warning(f"⚠️ Failed to save cache: {e}")

        else:
            st.warning("⚡ Using cached response")
            st.subheader("📌 Final Summary")
            stream_text(final_response)

