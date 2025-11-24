from pydantic import BaseModel, Field
from typing import Optional, List

class DocumentInformation(BaseModel):
    """Structured information extracted from any document."""
    
    name: Optional[str] = Field(None, description="Full name of the individual or entity")
    date_of_birth: Optional[str] = Field(None, description="Date of birth if applicable")
    id_number: Optional[str] = Field(None, description="ID card number such as Aadhaar, PAN, or Passport")
    invoice_number: Optional[str] = Field(None, description="Invoice or bill number, if applicable")
    total_amount: Optional[str] = Field(None, description="Total amount from invoice or bill")
    address: Optional[str] = Field(None, description="Full address extracted from the document")
    organization: Optional[str] = Field(None, description="Organization or university name")
    marks_or_grades: Optional[str] = Field(None, description="Marks or grades if the document is a marksheet")
    date: Optional[str] = Field(None, description="Relevant date such as issue date or transaction date")
    document_type: Optional[str] = Field(None, description="Type of document detected (ID, Invoice, Marksheet, etc.)")
    page_number: Optional[int] = Field(None, description="Page number within the uploaded file.")
    
class MultiDocumentInformation(BaseModel):
    """Structured information extracted from multiple documents or pages."""
    documents: List[DocumentInformation] = Field(..., description="List of extracted document information.")