# 📄 PDF Information Extractor

A Streamlit-based application that extracts key information from PDF documents using NVIDIA's Nemotron-3 API with advanced reasoning capabilities and stores the extracted data in MongoDB.

## 🎯 Features

- **PDF Upload**: Upload PDF files through an intuitive web interface
- **Local Storage**: Automatically saves PDFs locally with timestamped filenames
- **AI-Powered Extraction**: Uses NVIDIA Nemotron-3 Super 120B with extended thinking to extract:
  - Summary
  - Eligibility criteria
  - Benefits
  - Application date
  - Application process
- **MongoDB Integration**: Stores all extracted data in MongoDB for easy retrieval
- **Web Dashboard**: View, manage, and analyze extracted data
- **Database Statistics**: Track processing statistics and recent uploads

## ⚡ Quick Start (3 Steps)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment
```bash
# Copy the example file
cp .env.example .env

# Edit .env with your credentials:
MONGODB_URI=mongodb://localhost:27017
NVIDIA_API_KEY=your_nvidia_api_key_here
MONGODB_DB_NAME=pdf_extraction_db
```

### Step 3: Run the Application
```bash
streamlit run app.py
```
The app opens at: `http://localhost:8501`

## 📋 Prerequisites

- Python 3.8+
- MongoDB (local or cloud-based)
- NVIDIA API key (from https://developer.nvidia.com/ai-api)
- pip (Python package manager)

## 🚀 Detailed Installation & Setup

### 1. Navigate to Project

```bash
cd d:\HACKTHON\nvidianemotron
```

### 2. Create Virtual Environment (Optional but Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and fill in your configuration:

```bash
cp .env.example .env
```

Edit `.env` file with your actual values:

```
MONGODB_URI=mongodb://localhost:27017
MONGODB_DB_NAME=pdf_extraction_db
MONGODB_COLLECTION_NAME=extracted_data
NVIDIA_API_KEY=your_actual_nvidia_api_key
PDF_STORAGE_PATH=./uploaded_pdfs
NVIDIA_MODEL=nvidia/nemotron-3-super-120b-a12b
```

### 5. Setup MongoDB

**Option A: Local MongoDB**
```bash
# Install MongoDB Community Edition from https://www.mongodb.com/try/download/community
# Start MongoDB service
# Use: MONGODB_URI=mongodb://localhost:27017
```

**Option B: MongoDB Atlas (Cloud)**
1. Create account at https://www.mongodb.com/cloud/atlas
2. Create a free cluster
3. Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`
4. Update `MONGODB_URI` in `.env`

### 6. Get NVIDIA API Key

1. Go to https://developer.nvidia.com/ai-api
2. Sign up or log in to your account
3. Create an API key
4. Copy it to `.env` file as `NVIDIA_API_KEY`

### 7. Verify Setup (Optional)

Simply run the app and ensure it connects successfully:

```bash
streamlit run app.py
```

## 🏃 Running the Application

```bash
streamlit run app.py
```

The application will open in your default browser at `http://localhost:8501`

## 📖 Usage Guide

### Workflow Overview

```
User Uploads PDF
    ↓
File Saved Locally (with timestamp)
    ↓
Text Extracted from PDF
    ↓
ChatGPT API Analyzes Content
    ↓
Extracts: Summary, Eligibility, Benefits, Date, Process
    ↓
Data Stored in MongoDB
    ↓
User Views/Manages in Web Dashboard
```

### 🎯 Three Main Pages

#### 1. Upload & Extract

1. Click on the file uploader to select a PDF
2. Click **"Process PDF"** button
3. Wait for the AI to extract information
4. Review the extracted data in tabs:
   - **Summary** - Brief overview (2-3 sentences)
   - **Eligibility** - Who can apply/benefit
   - **Benefits** - What benefits are provided
   - **Apply Date** - Deadline or application date
   - **Application Process** - Step-by-step instructions
5. Click **"Save to Database"** to store the data

#### 2. View Extracted Data

1. Navigate to "View Extracted Data" page
2. Scroll through all stored documents
3. Click on a document to expand and view details
4. Delete old documents as needed

#### 3. Database Statistics

1. Navigate to "Database Statistics" page
2. View metrics:
   - Total documents processed
   - Total pages processed
   - Average pages per PDF
   - Recent uploads table

### Usage Examples

**Example 1: Government Benefits Document**
- Upload government program PDF
- System extracts: eligibility, benefits, application date
- Data stored for reference
- Easy access to benefits information

**Example 2: Loan Application Document**
- Upload bank loan form
- Extract: requirements, benefits, application process
- Store for later reference
- Compare multiple loan options

**Example 3: Insurance Policy**
- Upload insurance document
- Extract: benefits, eligibility, coverage dates
- Store in database
- Quick reference for policy details

## 📁 Project Structure

```
nvidianemotron/
├── app.py                      # Main Streamlit application (550+ lines)
├── config.py                   # Configuration management
├── pdf_handler.py              # PDF processing utilities
├── chatgpt_extractor.py        # NVIDIA Nemotron API integration
├── mongodb_handler.py          # MongoDB operations
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .env                       # Actual environment variables (create from .env.example)
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
└── uploaded_pdfs/             # Local PDF storage (auto-created)
```

### File Descriptions

**app.py** - Main Streamlit Application
- 550+ lines of Streamlit code
- Three main pages: Upload, View Data, Statistics
- Beautiful UI with tabs and expanders
- Real-time processing and feedback

**pdf_handler.py** - PDF Operations
- Save uploaded PDFs locally with timestamps
- Extract text from PDF pages
- Get PDF metadata (pages, filename, etc.)
- Delete PDFs when needed

**chatgpt_extractor.py** - AI Processing
- Call NVIDIA Nemotron API with PDF text
- Parse JSON responses with reasoning
- Validate extracted data
- Error handling and fallbacks

**mongodb_handler.py** - Database Operations
- Connect to MongoDB
- Insert extracted data
- Retrieve documents
- Update/Delete operations
- Connection management

**config.py** - Settings
- Load environment variables
- Set default values
- Create storage directories
- Centralized configuration

## 🔧 Configuration Details

### MongoDB Connection

- **Local**: `mongodb://localhost:27017`
- **Atlas**: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`

### NVIDIA Nemotron Model

**Model**: `nvidia/nemotron-3-super-120b-a12b`

- **Capabilities**: Advanced reasoning with extended thinking
- **Max tokens**: 16384 for reasoning budget
- **Specialization**: Document analysis and information extraction

## 🐛 Troubleshooting

### "Module not found" Error
```bash
# Ensure you're in the virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

# Then reinstall
pip install -r requirements.txt
```

### MongoDB Connection Error
- Ensure MongoDB is running
- Check `MONGODB_URI` in `.env`
- For Atlas, verify IP whitelist includes your machine
- Try running the app to test connection: `streamlit run app.py`

### NVIDIA API Error
- Verify API key is valid and active
- Check NVIDIA account has API quota/credits
- Ensure model name in `.env` is correct: `nvidia/nemotron-3-super-120b-a12b`
- Check NVIDIA API status and rate limits

### PDF Extraction Issues
- Ensure PDF contains extractable text (not image-based)
- Very large PDFs are truncated (first 4000 chars used)
- Check NVIDIA API rate limits on your dashboard
- Test with a small PDF first

### Port 8501 Already in Use
```bash
streamlit run app.py --server.port 8502
```

### "AttributeError" or Import Errors
```bash
# Reinstall all packages
pip install --upgrade -r requirements.txt

# Or recreate virtual environment
rm -r venv  # or: rmdir /s venv (Windows)
python -m venv venv
venv\Scripts\activate  # or: source venv/bin/activate
pip install -r requirements.txt
```

## 📊 Database Schema

Your MongoDB collection stores documents in this format:

```json
{
  "_id": "MongoDB ObjectId",
  "filename": "document_20240115_103045.pdf",
  "num_pages": 12,
  "upload_time": "2024-01-15T10:30:45.123Z",
  "created_at": "2024-01-15T10:35:20.456Z",
  "extracted_info": {
    "summary": "This document provides information about...",
    "eligibility": ["Must be 18+", "Valid ID required", "..."],
    "benefits": ["Free access", "Tax benefits", "..."],
    "apply_date": "2024-12-31",
    "application_process": [
      "Step 1: Register online",
      "Step 2: Submit documents",
      "..."
    ]
  }
}
```

## 💡 Tips for Best Results

✅ **Use text-based PDFs** (not scanned images or screenshots)
✅ **Clear, readable documents** work best for extraction
✅ **Shorter documents** extract more accurately
✅ **Check extracted data** before saving to database
✅ **Use NVIDIA Nemotron** with extended thinking for accurate extraction
✅ **Test your setup** by running the app: `streamlit run app.py`

## 💰 API Availability

- **NVIDIA Nemotron**: Free API access (up to rate limits)
- **MongoDB Atlas**: Free tier - Up to 512MB storage

## 🎓 Pro Tips

1. **Batch Processing**: Upload multiple PDFs sequentially
2. **NVIDIA Extended Thinking**: Uses advanced reasoning for better accuracy
3. **Data Export**: Use MongoDB tools for backups
4. **PDF Quality**: Use clear, text-based PDFs for best results
5. **API Limits**: Check NVIDIA API rate limits on your dashboard
6. **Virtual Environment**: Always activate before running
7. **Regular Backups**: Backup MongoDB data regularly

## 🔐 Security Best Practices

### 1. Protect Your Credentials
```bash
# NEVER commit .env file
echo ".env" >> .gitignore
```

### 2. API Key Safety
- Rotate API keys regularly
- Use separate keys for different environments
- Never share your .env file
- Keep keys secret in version control

### 3. MongoDB Security
- Use strong, unique passwords
- Enable IP whitelist (for Atlas)
- Regular backups of your database
- Monitor access and usage

### 4. File Storage
- Review uploaded PDFs regularly
- Clean up old files periodically
- Consider encryption for sensitive documents
- Secure your local storage folder

## ✅ Verification Checklist

Before running the app, verify:

- [ ] Python 3.8+ installed: `python --version`
- [ ] All packages installed: `pip list | grep -E "streamlit|pymongo|openai"`
- [ ] MongoDB running (local or cloud configured)
- [ ] NVIDIA API key obtained and valid
- [ ] .env file created with all required variables
- [ ] uploaded_pdfs directory exists (auto-created on first run)

## 📞 Support & Resources

### Documentation
- [Streamlit Documentation](https://docs.streamlit.io)
- [MongoDB Documentation](https://docs.mongodb.com)
- [NVIDIA API Documentation](https://docs.api.nvidia.com)
- [PyPDF2 Documentation](https://pypdf2.readthedocs.io)

### Debugging
```bash
# Run with debug logging
streamlit run app.py --logger.level=debug

# Check Python version
python --version

# Check installed packages
pip list
```

## 🎓 Learning Path

1. Read this README (15 minutes)
2. Install dependencies and run app (10 minutes): `streamlit run app.py`
3. Upload your first PDF (2 minutes)
4. Review the code in app.py (15 minutes)
5. Customize extraction prompts (optional)
6. Build production features (as needed)

## 📝 License

This project is provided as-is for educational and commercial use.

## 🎓 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [MongoDB Documentation](https://docs.mongodb.com)
- [NVIDIA Nemotron API Guide](https://docs.api.nvidia.com)
- [PyPDF2 Documentation](https://pypdf2.readthedocs.io)

---

**Happy PDF Processing! 🚀**
