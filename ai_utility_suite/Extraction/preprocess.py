# -------------------------------
# 🧩 Core Function: Analyze Document
# -------------------------------
from .get_document_type import detect_document_type
from .llm_output import extract_with_llm_structured
import streamlit as st


def analyze_document(file_path: str, model_id: str, 
                     client_azure, client_llm, 
                     deployment_name: str):
    
    print(f"----Model id: {model_id}----")

    # Step 1 — Auto Detect Mode
    if model_id == "auto":
        print("Step 1")
        with open(file_path, "rb") as f:
            layout_poller = client_azure.begin_analyze_document(model_id="prebuilt-layout", body=f)
            layout_result = layout_poller.result()
            text_content = " ".join([line.content for page in layout_result.pages for line in page.lines])

        doc_type = detect_document_type(text_content)
        st.info(f"📘 Auto-detected document type: {doc_type.upper()}")
        print(f"📘 Auto-detected document type: {doc_type.upper()}")

        if doc_type == "id":
            model_id = "prebuilt-idDocument"
        elif doc_type == "invoice":
            model_id = "prebuilt-invoice"
        elif doc_type == "receipt":
            model_id = "prebuilt-receipt"
        elif doc_type == "contract":
            model_id = "prebuilt-contract"
        else:
            model_id = "prebuilt-layout"


    # Step 2 — Analyze Using Selected Model
    with open(file_path, "rb") as f:
        print("Step 2")
        poller = client_azure.begin_analyze_document(model_id=model_id, body=f)
        result = poller.result()
    
    # Step 3 — Process Results
    if model_id in ["prebuilt-idDocument", "prebuilt-invoice", "prebuilt-receipt", "prebuilt-contract"]:
        print("Step 3")
        filtered_output = []
        for doc in result.documents:
            doc_summary = {
                "docType": doc.doc_type,
                "fields": {
                    name: {
                        "value": getattr(field, "value_string", None)
                                 or getattr(field, "value_date", None)
                                 or getattr(field, "value_integer", None)
                                 or field.content,
                    }
                    for name, field in doc.fields.items()
                }
            }
            filtered_output.append(doc_summary)

        print(f"Filtered output:\n{filtered_output}\n\n")
        return filtered_output

    else:
        print("Step 3")
        print("Proceeding to llm extraction")
        # Prebuilt Layout — use LLM for structured extraction
        text = "\n".join([line.content for page in result.pages for line in page.lines])
        llm_output = extract_with_llm_structured(raw_text=text, client_llm=client_llm, deployment_name=deployment_name)
        return [{"docType": "generic_document", "llm_output": llm_output}]