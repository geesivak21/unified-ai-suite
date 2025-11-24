# Import necessary libraries
import streamlit as st
import os
from azure.core.credentials import AzureKeyCredential
from azure.ai.documentintelligence import DocumentIntelligenceClient
from openai import AzureOpenAI
from .config import (AZURE_KEY, AZURE_ENDPOINT, 
                    OPENAI_API_KEY, OPENAI_API_VERSION,
                    OPENAI_ENDPOINT, DEPLOYMENT)
from .preprocess import analyze_document

def run():

    # Load configuration
    client_azure = DocumentIntelligenceClient(
        endpoint=AZURE_ENDPOINT,
        credential=AzureKeyCredential(AZURE_KEY)
    )

    client_llm = AzureOpenAI(
        api_version=OPENAI_API_VERSION,
        azure_endpoint=OPENAI_ENDPOINT,
        api_key=OPENAI_API_KEY  
    )


    # Streamlit UI
    st.set_page_config(page_title="📄 Document Extractor", layout="centered")
    st.title("🧾 Document Extractor")
    st.write("Upload Aadhaar, PAN, Invoices, Certificates, etc. — auto processed using Azure + LLMs.")

    # Document Type Selection
    MODEL_MAP = {
        "Auto Detect": "auto",
        "ID Card (Aadhaar/PAN/Passport)": "prebuilt-idDocument",
        "Invoice/Bill": "prebuilt-invoice",
        "Receipt": "prebuilt-receipt",
        "Contract / Legal Document": "prebuilt-contract",
        "Marksheet / Certificate / Other": "prebuilt-layout",
    }

    doc_type_choice = st.selectbox("Select Document Type:", list(MODEL_MAP.keys()))
    model_id = MODEL_MAP[doc_type_choice]

    # File Upload
    uploaded_file = st.file_uploader("📤 Upload your document (PDF/Image)", type=["pdf", "jpg", "jpeg", "png"])

    UPLOAD_DIR = "uploaded_docs"
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    results = None
    if uploaded_file:
        file_path = os.path.join("uploaded_docs", uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.read())

        st.success(f"✅ File uploaded: `{uploaded_file.name}`")
        with st.spinner("🔍 Analyzing document..."):
            try:
                results = analyze_document(file_path=file_path, 
                                        model_id=model_id,
                                        client_azure=client_azure,
                                        client_llm=client_llm,
                                        deployment_name=DEPLOYMENT)
            except Exception as e:
                st.error(f"⚠️ Error during analysis: {e}")
            
        print(f"results:\n{results}\n\n")
        if results:
            # Display Results
            for doc in results:
                print(f'doc:\n{doc}\n')
                document_type = doc.get('docType', '')
                
                st.subheader(f"📘 Document Type: {document_type}")
            
                # For prebuilt models (ID, Invoice, Business Card)
                if "fields" in doc:
                    for name, field in doc["fields"].items():
                        st.write(f"**{name}:** {field['value']}")
                
                elif "llm_output" in doc:
                    st.subheader("🧠 LLM Structured Extraction")

                    llm_data = doc["llm_output"]

                    if isinstance(llm_data, dict) and "documents" in llm_data:
                        documents = llm_data["documents"]
                    elif isinstance(llm_data, list):
                        documents = llm_data
                    else:
                        documents = [llm_data]

                    for i, d in enumerate(documents, start=1):
                        st.markdown(f"### 📄 Document {i}")
                        for key, value in d.items():
                            if value not in [None, "", "null"]:
                                formatted_key = key.replace("_", " ").capitalize()
                                st.markdown(f"**{formatted_key}:** {value}")
                        with st.expander("🧾 Raw JSON"):
                            st.json(d)
                        st.markdown("---")
        else:
            st.warning("No results were returned from analysis.")    

