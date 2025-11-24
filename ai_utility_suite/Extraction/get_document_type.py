# -------------------------------
# ⚙️ Helper: Document Type Detection
# -------------------------------
def detect_document_type(text: str) -> str:
    """
    Detects the type of document based on the text content.

    Parameters:
        text (str): The input text extracted from a document.

    Returns:
        str: The detected document type.
    """
    text_lower = text.lower()
    if len(text_lower.split()) < 15:  # count words, not characters
        return "generic"

    if any(k in text_lower for k in ["aadhaar", "pan", "passport", "identity", "dob", "govt"]):
        return "id"
    elif any(k in text_lower for k in ["invoice", "bill", "gst", "amount", "subtotal", "total due"]):
        return "invoice"
    elif any(k in text_lower for k in ["receipt", "paid", "total due", "cash", "pos"]):
        return "receipt"
    elif any(k in text_lower for k in ["contract", "agreement", "party", "signature"]):
        return "contract"
    elif any(k in text_lower for k in ["university", "marks", "grade", "subject", "roll no"]):
        return "marksheet"
    else:
        return "generic"