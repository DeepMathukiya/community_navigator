import os
from pathlib import Path
from PyPDF2 import PdfReader
import shutil
from config import PDF_STORAGE_PATH
from datetime import datetime


def save_uploaded_pdf(uploaded_file) -> str:
    """
    Save uploaded PDF file to local storage
    
    Args:
        uploaded_file: Streamlit uploaded file object
        
    Returns:
        str: Path to saved file
    """
    try:
        # Create filename with timestamp to avoid conflicts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
        filename = timestamp + uploaded_file.name
        file_path = os.path.join(PDF_STORAGE_PATH, filename)
        
        # Save file
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        return file_path
    except Exception as e:
        raise Exception(f"Error saving PDF: {str(e)}")


def extract_text_from_pdf(file_path: str) -> str:
    """
    Extract text from PDF file
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        str: Extracted text from PDF
    """
    try:
        text = ""
        pdf_reader = PdfReader(file_path)
        
        for page in pdf_reader.pages:
            text += page.extract_text()
        
        return text
    except Exception as e:
        raise Exception(f"Error extracting text from PDF: {str(e)}")


def get_pdf_info(file_path: str) -> dict:
    """
    Get PDF file information
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        dict: PDF information
    """
    try:
        pdf_reader = PdfReader(file_path)
        
        info = {
            "filename": os.path.basename(file_path),
            "file_path": file_path,
            "num_pages": len(pdf_reader.pages),
            "upload_time": datetime.now().isoformat(),
        }
        
        return info
    except Exception as e:
        raise Exception(f"Error getting PDF info: {str(e)}")


def delete_pdf_file(file_path: str) -> bool:
    """
    Delete PDF file from local storage
    
    Args:
        file_path: Path to PDF file
        
    Returns:
        bool: True if deleted successfully
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        raise Exception(f"Error deleting PDF: {str(e)}")
