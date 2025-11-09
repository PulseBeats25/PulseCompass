"""
Upload processing jobs - Async tasks for PDF and Excel parsing
"""
import time
from typing import Dict, Any


def process_pdf_job(file_content: bytes, filename: str, company_id: str = None) -> Dict[str, Any]:
    """
    Async job to process PDF transcript.
    Simulates heavy work; replace with real PDF parsing logic.
    """
    # Simulate processing time
    time.sleep(3)
    
    return {
        "type": "pdf",
        "filename": filename,
        "company_id": company_id,
        "status": "processed",
        "pages": 10,
        "text_length": 5000,
        "message": f"Successfully processed PDF: {filename}"
    }


def process_excel_job(file_content: bytes, filename: str, company_id: str = None) -> Dict[str, Any]:
    """
    Async job to process Excel financial data.
    Simulates heavy work; replace with real Excel parsing logic.
    """
    # Simulate processing time
    time.sleep(2)
    
    return {
        "type": "excel",
        "filename": filename,
        "company_id": company_id,
        "status": "processed",
        "rows": 100,
        "columns": 15,
        "message": f"Successfully processed Excel: {filename}"
    }
