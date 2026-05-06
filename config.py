import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Configuration
MONGODB_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "pdf_extraction_db")
MONGODB_COLLECTION_NAME = os.getenv("MONGODB_COLLECTION_NAME", "extracted_data")

# NVIDIA Nemotron Configuration
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

# PDF Storage Configuration
PDF_STORAGE_PATH = os.getenv("PDF_STORAGE_PATH", "./uploaded_pdfs")

# Ensure PDF storage directory exists
os.makedirs(PDF_STORAGE_PATH, exist_ok=True)

# NVIDIA Model Configuration
# Using Nemotron-3 Super 120B with advanced reasoning capabilities
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-super-120b-a12b")
