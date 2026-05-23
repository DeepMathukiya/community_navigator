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
- **Vector Embeddings**: Generate 768-dimensional embeddings using sentence-transformers for semantic search
- **RAG Chatbot**: Query documents using natural language with AI-powered answers and automatic citations
- **Web Dashboard**: View, manage, and analyze extracted data
- **Database Statistics**: Track processing statistics and recent uploads
- **Comprehensive Logging**: DEBUG/INFO/WARNING level logging for all operations

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

### 🎯 Four Main Pages

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
5. Click **"Save to Database"** to store the data (auto-generates embedding)
6. Click **"🧠 Generate Embedding for Document X"** to manually create embeddings

#### 2. View Extracted Data

1. Navigate to "View Extracted Data" page
2. Scroll through all stored documents
3. Click on a document to expand and view details
4. Generate embeddings for each document
5. Delete old documents as needed

#### 3. Database Statistics

1. Navigate to "Database Statistics" page
2. View metrics:
   - Total documents processed
   - Total pages processed
   - Average pages per PDF
   - Recent uploads table

#### 4. 💬 Chatbot (NEW)

1. Navigate to "💬 Chatbot" page
2. Enter your natural language query in the text box
3. Click **"🔍 Search & Answer"** to:
   - Find semantically related documents (top 5)
   - Generate AI answer using NVIDIA Nemotron
   - Extract citations automatically
4. View the formatted answer with:
   - Main answer text
   - Citations with document names and relevance scores
   - Related documents list
5. Use **"Clear Chat"** to reset conversation history

**How It Works**:
- Your query is converted to a 768-dimensional embedding
- Milvus searches for semantically similar document summaries (COSINE similarity)
- NVIDIA Nemotron generates answer based on retrieved documents
- Citations are automatically extracted and linked to source documents
- Chat history persists during your session

### Usage Examples

**Example 1: Government Benefits Document**
- Upload government program PDF
- Extract: eligibility, benefits, application date
- Save to database (auto-generates embedding)
- Query: "Who is eligible for this program?"
- Result: AI answers with citations from extracted documents
- Data stored for reference
- Easy access to benefits information

**Example 2: Loan Application Document**
- Upload bank loan form
- Extract: requirements, benefits, application process
- Query: "What are the requirements?"
- Result: Answer with [Document 1] citation
- Store for later comparison
- Compare multiple loan options using chatbot

**Example 3: Insurance Policy**
- Upload insurance document
- Extract: benefits, eligibility, coverage dates
- Query: "What is covered by this policy?"
- Result: AI references specific policy sections
- Store in database
- Quick reference for policy details

**Example 4: Semantic Search Across Multiple Documents**
- Upload 5 different benefit program PDFs
- Generate embeddings for all
- Query: "Which programs help with housing?"
- Result: Chatbot finds relevant documents using semantic similarity
- Answer synthesized from top results
- Citations show which documents were used

## 📁 Project Structure

```
nvidianemotron/
├── app.py                      # Main Streamlit application (500+ lines)
├── rag_chatbot.py              # RAG-based chatbot with semantic search & citations
├── config.py                   # Configuration management
├── logger_config.py            # Logging setup (DEBUG/INFO/WARNING levels)
├── pdf_handler.py              # PDF processing utilities
├── chatgpt_extractor.py        # NVIDIA Nemotron API integration
├── embedding_utils.py          # Embedding generation (sentence-transformers)
├── mongodb_handler.py          # MongoDB operations
├── milvus_handler.py           # Milvus vector database operations
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .env                       # Actual environment variables (create from .env.example)
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
└── uploaded_pdfs/             # Local PDF storage (auto-created)
```

### File Descriptions

**app.py** - Main Streamlit Application (500+ lines)
- Four main pages: Upload & Extract, View Extracted Data, Database Statistics, Chatbot
- PDF upload and processing
- Data viewing and management
- Statistics dashboard
- RAG chatbot interface

**rag_chatbot.py** - RAG Chatbot Module (~200 lines)
- Semantic document search using Milvus
- NVIDIA Nemotron answer generation
- Automatic citation extraction from answers
- Comprehensive logging (DEBUG/INFO/WARNING levels)
- End-to-end chat pipeline with document retrieval

**embedding_utils.py** - Embedding Generation
- Generate 768-dimensional embeddings using sentence-transformers
- Lazy model loading (all-mpnet-base-v2)
- CPU-only execution for Windows compatibility
- Query and document embedding generation

**milvus_handler.py** - Vector Database
- Milvus 2.3.0 integration
- Vector collection management (pdf_embeddings)
- Semantic similarity search using COSINE metric
- IVF_FLAT indexing for fast retrieval
- CRUD operations for embeddings

**logger_config.py** - Logging Configuration
- Centralized logging setup
- DEBUG: Detailed execution flow and data tracking
- INFO: Major operations and summaries
- WARNING: Potential issues and edge cases
- Exception: Full error traces with context

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
- Insert extracted data and document metadata
- Retrieve documents by ID
- Update/Delete operations
- Connection management

**config.py** - Settings
- Load environment variables
- Set default values
- Create storage directories
- Centralized configuration

## 🏗️ RAG Architecture

The application uses a **Retrieval-Augmented Generation (RAG)** pattern for intelligent document querying:

```
User Query
    ↓
[Embedding Generation] - Convert query to 768-dim vector
    ↓
[Vector Search] - Find semantically similar documents in Milvus (COSINE similarity)
    ↓
[Context Retrieval] - Fetch full document content from MongoDB
    ↓
[LLM Processing] - NVIDIA Nemotron generates answer with citations
    ↓
[Citation Extraction] - Parse [Document X] references from response
    ↓
Formatted Answer with Citations & Sources
```

**Key Components**:

1. **Embedding Model**: sentence-transformers (all-mpnet-base-v2)
   - Generates 768-dimensional vectors
   - Lazy-loaded on first use
   - CPU-only execution for Windows compatibility

2. **Vector Database**: Milvus 2.3.0
   - Stores embeddings in 'pdf_embeddings' collection
   - Uses IVF_FLAT index with COSINE similarity metric
   - Returns top-K most relevant documents (~5 by default)

3. **Context Store**: MongoDB
   - Stores full document metadata
   - Maintains extracted information (summary, eligibility, benefits, etc.)
   - Enables citation retrieval and attribution

4. **Answer Generation**: NVIDIA Nemotron API
   - Receives context from Milvus + MongoDB
   - Generates citations in [Document X] format
   - Instructed to state when info is unavailable

## 📝 Logging System

All modules use comprehensive logging with multiple levels for debugging and monitoring:

### Log Levels

- **🔵 DEBUG**: Detailed execution flow
  - Query embedding generation and dimensions
  - Vector search results and similarity scores
  - MongoDB document lookups
  - API call parameters and response handling
  - Citation pattern matching

- **ℹ️ INFO**: Major operations and summaries
  - Handler initialization (Milvus, MongoDB, NVIDIA)
  - Document search completion with result counts
  - Answer generation success with citation counts
  - Chat session start/completion

- **⚠️ WARNING**: Potential issues
  - Missing documents in MongoDB
  - Invalid citation numbers in answers
  - Unavailable API keys or misconfiguration

- **❌ EXCEPTION**: Error conditions
  - Full stack traces with context
  - Search failures
  - API errors
  - Connection issues

### Accessing Logs

Logs are configured in **logger_config.py** and can be:

1. **Viewed in Console**: Streamlit displays logs in terminal
2. **Captured to File**: Configure in logger_config.py
3. **Filtered by Level**: Set `logger.setLevel()` in code

**Example Usage**:
```python
from logger_config import get_logger

logger = get_logger(__name__)
logger.debug("Detailed info: %s", variable)
logger.info("Operation completed")
logger.warning("Potential issue: %s", problem)
logger.exception("Error occurred: %s", error)
```

## 🔧 Configuration Details

### Milvus Vector Database

**Connection**: `localhost:19530` (default)

**Collection**: `pdf_embeddings`

**Schema**:
- `pk` (Primary Key): Auto-generated unique ID
- `doc_id` (VARCHAR): Reference to MongoDB document
- `summary` (VARCHAR): Document summary text
- `embedding` (FLOAT_VECTOR): 768-dimensional vector

**Index**: IVF_FLAT with COSINE metric
- `nlist`: 1024 (number of clusters)
- `metric_type`: COSINE (similarity calculation)
- `index_type`: IVF_FLAT (approximate nearest neighbor search)

**Setup**:
```bash
# Milvus is expected to run on localhost:19530
# Docker: docker run -d -p 19530:19530 -p 9091:9091 milvusdb/milvus:v2.3.0 milvus run standalone
```

### Sentence-Transformers (Embeddings)

**Model**: `all-mpnet-base-v2`
- **Dimensions**: 768
- **Context Length**: 384 tokens
- **Performance**: Fast, high-quality semantic embeddings
- **Execution**: CPU-only mode (Windows compatible)

**Features**:
- Lazy-loaded on first embedding generation
- Cached in memory for subsequent calls
- Returns normalized float vectors

### MongoDB Connection

- **Local**: `mongodb://localhost:27017`
- **Atlas**: `mongodb+srv://username:password@cluster.mongodb.net/?retryWrites=true&w=majority`

**Database**: Configurable in `.env` (default: `pdf_extraction_db`)

**Collection**: Configurable in `.env` (default: `extracted_data`)

### NVIDIA Nemotron Model

**Model**: `nvidia/nemotron-3-super-120b-a12b`

- **Capabilities**: Advanced reasoning with extended thinking
- **Max tokens**: 16384 for reasoning budget
- **Specialization**: Document analysis and information extraction

## 🐛 Troubleshooting

### Milvus Connection Error
```
Error: Failed to connect to Milvus at localhost:19530
```
**Solution**:
1. Ensure Milvus is running: `docker ps | grep milvus`
2. Check port 19530 is accessible
3. Start Milvus: `docker run -d -p 19530:19530 -p 9091:9091 milvusdb/milvus:v2.3.0 milvus run standalone`
4. Verify connection in terminal: Test Milvus handler import

### Embedding Generation Fails (Windows DLL Error)
```
OSError: [WinError 1114] ... Error loading "C:\...\torch\lib\c10.dll"
```
**Solution**:
1. Ensure CPU-only PyTorch is installed (not CUDA-enabled)
2. Reinstall torch: `pip install torch --index-url https://download.pytorch.org/whl/cpu`
3. Verify app.py line 1 has: `os.environ["CUDA_VISIBLE_DEVICES"] = ""`
4. Test embedding: `python -c "from embedding_utils import get_embedding; get_embedding('test')"`

### Chatbot Returns "Document Not Found"
**Solution**:
1. Ensure PDFs have been uploaded and saved to database
2. Check MongoDB contains documents: Click "View Extracted Data"
3. Generate embeddings for documents using "🧠 Generate Embedding" button
4. Verify Milvus collection has embeddings: Check milvus_handler logs
5. Try simple query: "What is this document about?"

### No Citations in Chatbot Answer
**Problem**: Answer generated but citations [Document X] not showing

**Solution**:
1. Check logs for citation extraction (DEBUG level)
2. Verify NVIDIA response format includes [Document X]
3. Check regex pattern in rag_chatbot.py: `r'\[Document (\d+)\]'`
4. Test with simple query to verify NVIDIA API working
5. Enable DEBUG logging to see citation patterns

### Marshmallow/Pymilvus Version Conflict
```
AttributeError: module 'marshmallow' has no attribute '__version_info__'
```
**Solution**:
- Already handled in requirements.txt:
  - `pymilvus==2.3.0` (pinned)
  - `marshmallow==3.20.0` (pinned)
- Reinstall: `pip install --upgrade -r requirements.txt`

### Sentence-Transformers Download Fails
```
Error downloading model: Connection refused
```
**Solution**:
1. Check internet connection
2. Model will download on first use (~400MB)
3. Use offline mode if cached: Model stored in `~/.cache/huggingface/hub/`
4. Manually download: `python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-mpnet-base-v2')"`

### "Module not found" Error
```bash
# Ensure you're in the virtual environment
# Windows:
.\.venv\Scripts\activate
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
rm -r .venv  # or: rmdir /s .venv (Windows)
python -m venv .venv
.\.venv\Scripts\activate  # or: source .venv/bin/activate (macOS/Linux)
pip install -r requirements.txt
```

## 📊 Database Schema

### MongoDB Collection Storage

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

### Milvus Vector Storage

Embeddings are stored in Milvus with the following schema:

```
Collection: pdf_embeddings
├── pk (Primary Key): Auto-generated integer ID
├── doc_id (VARCHAR): Reference to MongoDB _id
├── summary (VARCHAR): Document summary (up to 1000 chars)
└── embedding (FLOAT_VECTOR[768]): 768-dimensional vector
    └── Generated from: summary text using sentence-transformers
    └── Similarity Metric: COSINE (values: -1 to 1, higher = more similar)
    └── Search Type: IVF_FLAT approximate nearest neighbor
    └── Top-K Default: 5 results
```

**Example Search Result**:
```
Query: "What are the benefits?"
↓
Search Results (Top 3):
1. doc_id: "64f1c2a..." | similarity: 0.87 | file: "benefits_guide.pdf"
2. doc_id: "64f1c2b..." | similarity: 0.82 | file: "program_overview.pdf"  
3. doc_id: "64f1c2c..." | similarity: 0.76 | file: "faq.pdf"
```

## 💡 Tips for Best Results

### PDF Extraction Tips
✅ **Use text-based PDFs** (not scanned images or screenshots)
✅ **Clear, readable documents** work best for extraction
✅ **Shorter documents** extract more accurately
✅ **Check extracted data** before saving to database
✅ **Use NVIDIA Nemotron** with extended thinking for accurate extraction
✅ **Test your setup** by running the app: `streamlit run app.py`

### Chatbot & Embedding Tips
✅ **Generate embeddings** for documents after extraction (speeds up future queries)
✅ **Use natural language queries** - Semantic search understands context
✅ **Clear, specific questions** get better results
✅ **Check document count** - More relevant documents = better answers
✅ **Review citations** - Verify sources before trusting answers
✅ **Monitor logs** - Enable DEBUG logging to see search scores and API calls
✅ **Query variations** - Try rephrasing questions for different results

### Performance Optimization
✅ **Batch uploads** - Process multiple PDFs in succession
✅ **Milvus indexing** - IVF_FLAT is optimized for your scale
✅ **Embedding caching** - Models cached after first generation
✅ **Vector similarity** - COSINE metric provides semantic meaning
✅ **Top-K tuning** - Adjust from default 5 results as needed

## 💰 API Availability

- **NVIDIA Nemotron**: Free API access (up to rate limits)
- **MongoDB Atlas**: Free tier - Up to 512MB storage

## 🎓 Pro Tips

### Document Processing
1. **Batch Processing**: Upload multiple PDFs sequentially to build knowledge base
2. **NVIDIA Extended Thinking**: Uses advanced reasoning for better accuracy
3. **Data Export**: Use MongoDB tools for backups

### RAG Chatbot Advanced Usage
4. **Semantic Search**: Query with natural language - embeddings handle context
5. **Citation Verification**: Cross-reference sources in MongoDB
6. **Multi-document QA**: Chatbot automatically synthesizes from top-5 results
7. **Similarity Scores**: DEBUG logs show relevance (0-1 scale)

### Performance & Maintenance
8. **Vector Database**: Milvus caches vectors - searches get faster over time
9. **Embedding Generation**: Lazy-load model saves startup time
10. **Logging Levels**: Use DEBUG for detailed troubleshooting, INFO for production
11. **API Limits**: Check NVIDIA dashboard for rate limits and quota
12. **Virtual Environment**: Always activate before running
13. **Regular Backups**: Backup both MongoDB and Milvus data

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
