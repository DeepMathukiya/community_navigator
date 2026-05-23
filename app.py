import os
# Force CPU mode globally before any torch/cuda imports
os.environ["CUDA_VISIBLE_DEVICES"] = ""

import streamlit as st
from pdf_handler import save_uploaded_pdf, extract_text_from_pdf, get_pdf_info, delete_pdf_file
from chatgpt_extractor import extract_information_from_pdf, validate_extracted_data
from mongodb_handler import MongoDBHandler
from milvus_handler import MilvusHandler
from embedding_utils import get_embedding
from rag_chatbot import RAGChatbot
import json
from datetime import datetime
from logger_config import get_logger

logger = get_logger(__name__)

# Page configuration
st.set_page_config(
    page_title="PDF Information Extractor",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .info-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        color: #155724;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .error-box {
        background-color: #f8d7da;
        border: 1px solid #f5c6cb;
        color: #721c24;
        padding: 1rem;
        border-radius: 0.5rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'db_handler' not in st.session_state:
    try:
        st.session_state.db_handler = MongoDBHandler()
        st.session_state.db_connected = True
    except Exception as e:
        st.session_state.db_connected = False
        st.session_state.db_error = str(e)
        logger.exception("Failed to initialize MongoDBHandler: %s", st.session_state.db_error)

# Initialize Milvus handler (optional)
if 'milvus_handler' not in st.session_state:
    try:
        logger.info("Initializing Milvus handler with collection 'pdf_embeddings'...")
        st.session_state.milvus_handler = MilvusHandler()
        st.session_state.milvus_connected = True
        logger.info("Milvus handler initialized successfully. Collection 'pdf_embeddings' is ready.")
    except Exception as e:
        st.session_state.milvus_connected = False
        st.session_state.milvus_error = str(e)
        logger.warning("Milvus not available: %s", st.session_state.milvus_error)

# Initialize RAG Chatbot
if 'rag_chatbot' not in st.session_state:
    try:
        st.session_state.rag_chatbot = RAGChatbot(
            milvus_handler=st.session_state.milvus_handler if st.session_state.get('milvus_connected') else None,
            mongo_handler=st.session_state.db_handler if st.session_state.get('db_connected') else None
        )
        st.session_state.chatbot_ready = True
    except Exception as e:
        st.session_state.chatbot_ready = False
        st.session_state.chatbot_error = str(e)
        logger.warning("RAG Chatbot initialization failed: %s", e)

# Initialize chat message history
if 'chat_messages' not in st.session_state:
    st.session_state.chat_messages = []

# Sidebar
st.sidebar.title("📋 Navigation")
page = st.sidebar.radio(
    "Select a page:",
    ["Upload & Extract", "View Extracted Data", "Database Statistics", "💬 Chatbot"]
)

st.sidebar.markdown("---")
st.sidebar.info(
    "**PDF Extraction System**\n\n"
    "This tool extracts key information from PDFs using AI:\n"
    "- Summary\n"
    "- Eligibility\n"
    "- Benefits\n"
    "- Application Date\n"
    "- Application Process"
)

# Main content
st.markdown("<h1 class='main-header'>📄 PDF Information Extractor</h1>", unsafe_allow_html=True)

# Check database connection
if not st.session_state.db_connected:
    st.error(f"⚠️ Database Connection Error: {st.session_state.db_error}")
    st.info("Please ensure MongoDB is running and connection details are correct in the .env file")

if page == "Upload & Extract":
    st.header("📤 Upload PDF & Extract Information")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        uploaded_file = st.file_uploader(
            "Choose a PDF file",
            type="pdf",
            help="Upload a PDF document to extract information"
        )
    
    with col2:
        st.write("")
        st.write("")
        if st.button("ℹ️ Instructions", use_container_width=True):
            st.info(
                "**Steps:**\n"
                "1. Upload a PDF file\n"
                "2. Click 'Process PDF'\n"
                "3. Review extracted information\n"
                "4. Save to database if needed"
            )
    
    if uploaded_file is not None:
        st.markdown("---")
        
        # Display file info
        with st.expander("📋 File Information", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("File Name", uploaded_file.name)
            with col2:
                st.metric("File Size", f"{uploaded_file.size / 1024:.2f} KB")
            with col3:
                st.metric("Upload Time", datetime.now().strftime("%H:%M:%S"))
        
        # Process button
        if st.button("🔄 Process PDF", use_container_width=True, type="primary"):
            with st.spinner("Processing PDF..."):
                try:
                    # Step 1: Save PDF
                    st.info("📥 Saving PDF file...")
                    file_path = save_uploaded_pdf(uploaded_file)
                    st.success(f"✓ PDF saved to: {file_path}")
                    
                    # Step 2: Get PDF info
                    st.info("📊 Analyzing PDF...")
                    pdf_info = get_pdf_info(file_path)
                    st.success(f"✓ PDF loaded - Pages: {pdf_info['num_pages']}")
                    
                    # Step 3: Extract text
                    st.info("📖 Extracting text from PDF...")
                    pdf_text = extract_text_from_pdf(file_path)
                    if len(pdf_text) > 100:
                        st.success(f"✓ Extracted {len(pdf_text)} characters")
                    else:
                        st.warning("⚠️ Very little text extracted. PDF might be image-based.")
                    
                    # Step 4: Extract info using ChatGPT
                    st.info("🤖 Using AI to extract information...")
                    extracted_data = extract_information_from_pdf(pdf_text)
                    # logger.info("Raw extracted data: %s", str(extracted_data)[:1000])
                    extracted_data = validate_extracted_data(extracted_data)
                    st.success("✓ Information extracted successfully!")
                    
                    # Store in session for display
                    st.session_state.extracted_data = {
                        **pdf_info,
                        "extracted_info": extracted_data,
                        "file_path": file_path
                    }
                    
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    logger.exception("Error processing uploaded PDF: %s", getattr(uploaded_file, 'name', 'unknown'))
        
        # Display extracted data
        if 'extracted_data' in st.session_state:
            st.markdown("---")
            st.header("📋 Extracted Information")
            
            data = st.session_state.extracted_data
            extracted_info = data['extracted_info']
            
            # Create tabs for different information
            tab1, tab2, tab3, tab4, tab5 = st.tabs([
                "📝 Summary",
                "✅ Eligibility",
                "🎁 Benefits",
                "📅 Apply Date",
                "📋 Application Process"
            ])
            
            with tab1:
                st.write(extracted_info.get('summary', 'Not mentioned'))
            
            with tab2:
                eligibility = extracted_info.get('eligibility', 'Not mentioned')
                if isinstance(eligibility, list):
                    for item in eligibility:
                        st.write(f"• {item}")
                else:
                    st.write(eligibility)
            
            with tab3:
                benefits = extracted_info.get('benefits', 'Not mentioned')
                if isinstance(benefits, list):
                    for item in benefits:
                        st.write(f"• {item}")
                else:
                    st.write(benefits)
            
            with tab4:
                st.write(extracted_info.get('apply_date', 'Not mentioned'))
            
            with tab5:
                process = extracted_info.get('application_process', 'Not mentioned')
                if isinstance(process, list):
                    for i, step in enumerate(process, 1):
                        st.write(f"{i}. {step}")
                else:
                    st.write(process)
            
            # Save to database button
            st.markdown("---")
            if st.session_state.db_connected:
                if st.button("💾 Save to Database", use_container_width=True, type="primary"):
                    try:
                        with st.spinner("Saving to database..."):
                            db_data = {
                                "filename": data['filename'],
                                "num_pages": data['num_pages'],
                                "upload_time": data['upload_time'],
                                "extracted_info": extracted_info
                            }
                            doc_id = st.session_state.db_handler.insert_extracted_data(db_data)
                            # make string id for external systems
                            doc_id_str = str(doc_id)
                            st.success(f"✓ Data saved to database! Document ID: {doc_id_str}")
                            logger.info("Saved extracted data to DB: %s", doc_id_str)

                            # Insert embedding into Milvus if available
                            try:
                                if st.session_state.get('milvus_connected'):
                                    summary_text = extracted_info.get('summary', '') or ''
                                    if summary_text:
                                        emb = get_embedding(summary_text)
                                        st.session_state.milvus_handler.insert_embedding(doc_id_str, summary_text, emb)
                                        st.success("✓ Embedding inserted into Milvus")
                                    else:
                                        logger.info("No summary text found to create embedding for doc %s", doc_id_str)
                                else:
                                    logger.info("Skipping Milvus insert; Milvus not connected: %s", st.session_state.get('milvus_error'))
                            except Exception as me:
                                logger.exception("Failed to insert embedding into Milvus: %s", me)
                                st.warning("Saved to DB but failed to insert embedding into Milvus")
                    except Exception as e:
                        st.error(f"❌ Error saving to database: {str(e)}")
                        logger.exception("Error saving extracted data to DB for file %s", data.get('filename'))
            else:
                st.warning("⚠️ Database not connected. Cannot save data.")

elif page == "View Extracted Data":
    st.header("📊 View Extracted Data")
    
    if st.session_state.db_connected:
        try:
            with st.spinner("Loading data from database..."):
                documents = st.session_state.db_handler.get_all_documents(limit=100)
            
            if documents:
                st.success(f"✓ Loaded {len(documents)} documents")
                
                # Display documents in a table format
                for idx, doc in enumerate(documents, 1):
                    with st.expander(f"📄 Document {idx} - {doc.get('filename', 'Unknown')}"):
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            st.write(f"**ID:** {doc['_id']}")
                            st.write(f"**File:** {doc.get('filename', 'N/A')}")
                        
                        with col2:
                            st.write(f"**Pages:** {doc.get('num_pages', 'N/A')}")
                            st.write(f"**Uploaded:** {doc.get('upload_time', 'N/A')}")
                        
                        with col3:
                            st.write(f"**Stored:** {doc.get('created_at', 'N/A')}")
                        
                        st.markdown("**Extracted Information:**")
                        
                        info = doc.get('extracted_info', {})
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.write(f"**Summary:** {info.get('summary', 'N/A')}")
                            st.write(f"**Apply Date:** {info.get('apply_date', 'N/A')}")
                        
                        with col2:
                            st.write(f"**Eligibility:** {info.get('eligibility', 'N/A')}")
                            st.write(f"**Benefits:** {info.get('benefits', 'N/A')}")
                        
                        st.write(f"**Application Process:** {info.get('application_process', 'N/A')}")
                        
                        # Generate Embedding button
                        if st.button(f"🧠 Generate Embedding for Document {idx}", key=f"gen_emb_{doc['_id']}"):
                            try:
                                if st.session_state.get('milvus_connected'):
                                    summary_text = info.get('summary', '') or ''
                                    if not summary_text:
                                        st.warning("⚠️ No summary available to generate embedding.")
                                    else:
                                        with st.spinner("Generating embedding and inserting into Milvus..."):
                                            emb = get_embedding(summary_text)
                                            pk = st.session_state.milvus_handler.insert_embedding(str(doc['_id']), summary_text, emb)
                                        st.success(f"✓ Embedding inserted into Milvus (pk={pk})")
                                else:
                                    st.warning(f"⚠️ Milvus not connected: {st.session_state.get('milvus_error')}")
                            except Exception as e:
                                logger.exception("Failed to generate/insert embedding for doc %s: %s", doc.get('_id'), e)
                                st.error("❌ Failed to generate embedding. Check logs.")

                        # Delete button
                        if st.button(f"🗑️ Delete Document {idx}", key=f"delete_{doc['_id']}"):
                            try:
                                if st.session_state.db_handler.delete_document(doc['_id']):
                                    st.success("✓ Document deleted successfully!")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error deleting document: {str(e)}")
                                logger.exception("Error deleting document %s", doc.get('_id'))
            else:
                st.info("No documents found in database.")
        
        except Exception as e:
                st.error(f"❌ Error loading data: {str(e)}")
                logger.exception("Error loading data from DB")
    else:
        st.warning("⚠️ Database not connected. Cannot retrieve data.")

elif page == "Database Statistics":
    st.header("📈 Database Statistics")
    
    if st.session_state.db_connected:
        try:
            documents = st.session_state.db_handler.get_all_documents(limit=1000)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Documents", len(documents))
            
            with col2:
                total_pages = sum(doc.get('num_pages', 0) for doc in documents)
                st.metric("Total Pages Processed", total_pages)
            
            with col3:
                st.metric("Avg Pages per PDF", round(total_pages / len(documents), 2) if documents else 0)
            
            # File types distribution
            st.markdown("---")
            st.subheader("📊 Recent Uploads")
            
            if documents:
                recent_docs = sorted(documents, key=lambda x: x.get('created_at', ''), reverse=True)[:10]
                
                display_data = []
                for doc in recent_docs:
                    display_data.append({
                        "Filename": doc.get('filename', 'N/A'),
                        "Pages": doc.get('num_pages', 'N/A'),
                        "Uploaded": doc.get('upload_time', 'N/A')[:10],
                        "Stored": str(doc.get('created_at', 'N/A'))[:10]
                    })
                
                st.table(display_data)
            else:
                st.info("No documents in database yet.")
        
        except Exception as e:
            st.error(f"❌ Error loading statistics: {str(e)}")
            logger.exception("Error loading database statistics")
    else:
        st.warning("⚠️ Database not connected. Cannot load statistics.")

elif page == "💬 Chatbot":
    st.header("💬 Document-Aware Chatbot")
    
    if not st.session_state.get('chatbot_ready'):
        st.error(f"❌ Chatbot not available: {st.session_state.get('chatbot_error', 'Unknown error')}")
        st.info("Ensure Milvus and MongoDB are running and connected.")
    else:
        # Check Milvus collection status
        if st.session_state.get('milvus_connected'):
            try:
                collection_status = st.session_state.milvus_handler.get_collection_status()
                num_embeddings = collection_status.get('num_entities', 0)
                
                if num_embeddings == 0:
                    st.warning("⚠️ **No embeddings found in Milvus collection!**")
                    st.info("""
                    To use the chatbot, you need to:
                    1. Go to **"View Extracted Data"** page
                    2. For each document, click **"🧠 Generate Embedding for Document X"**
                    3. Return here and ask your questions
                    
                    This generates semantic embeddings that allow the chatbot to find relevant documents.
                    """)
                    st.markdown("---")
                else:
                    st.success(f"✅ Milvus collection has **{num_embeddings}** embeddings ready")
                    st.markdown("---")
            except Exception as e:
                logger.warning("Could not get collection status: %s", e)
        
        st.markdown("""
        Ask questions about your uploaded PDF documents. The chatbot will:
        1. Search for related documents using semantic similarity
        2. Generate an answer using NVIDIA Nemotron AI
        3. Provide citations to the source documents
        """)
        
        st.markdown("---")
        
        # Display chat history
        with st.container():
            if st.session_state.chat_messages:
                for msg in st.session_state.chat_messages:
                    if msg["role"] == "user":
                        st.chat_message("user").write(msg["content"])
                    else:
                        st.chat_message("assistant").write(msg["content"])
        
        # Input for new query
        st.markdown("---")
        query = st.text_input(
            "Ask a question about your documents:",
            placeholder="E.g., What are the eligibility criteria mentioned in the documents?",
            key="chat_input"
        )
        
        col1, col2 = st.columns([4, 1])
        with col1:
            search_button = st.button("🔍 Search & Answer", use_container_width=True, type="primary")
        with col2:
            clear_button = st.button("🗑️ Clear Chat", use_container_width=True)
        
        if clear_button:
            st.session_state.chat_messages = []
            st.rerun()
        
        if search_button and query.strip():
            # Add user message to history
            st.session_state.chat_messages.append({
                "role": "user",
                "content": query
            })
            
            # Show thinking state
            with st.spinner("🔍 Searching documents and generating answer..."):
                try:
                    # Get answer from RAG chatbot
                    result = st.session_state.rag_chatbot.chat(query, top_k=5)
                    
                    # Format response with citations
                    answer_text = result.get("answer", "No answer generated")
                    citations = result.get("citations", [])
                    related_docs = result.get("related_documents", [])
                    
                    # Build formatted response
                    formatted_response = f"{answer_text}\n"
                    
                    if citations:
                        formatted_response += "\n---\n**📚 Citations:**\n"
                        for citation in citations:
                            doc_num = citation.get("document_number", "?")
                            filename = citation.get("filename", "Unknown")
                            doc_id = citation.get("doc_id", "Unknown")
                            formatted_response += f"\n[Document {doc_num}] {filename}"
                    
                    if related_docs and not citations:
                        formatted_response += "\n---\n**📚 Related Documents:**\n"
                        for i, doc in enumerate(related_docs, 1):
                            filename = doc.get("filename", "Unknown")
                            score = doc.get("similarity_score", 0)
                            formatted_response += f"\n- {filename} (relevance: {score:.1%})"
                    
                    # Add assistant response to history
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": formatted_response
                    })
                    
                    # Display the response
                    st.chat_message("assistant").markdown(formatted_response)
                    
                except Exception as e:
                    error_msg = f"❌ Error: {str(e)}"
                    st.error(error_msg)
                    logger.exception("Error in chatbot query: %s", e)
                    
                    # Add error to history
                    st.session_state.chat_messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

# Footer
# st.markdown("---")
# st.markdown(
#     """
#     <div style='text-align: center; color: #888; font-size: 0.9rem;'>
#     <p>PDF Information Extractor v1.0 | Powered by ChatGPT & MongoDB</p>
#     </div>
#     """,
#     unsafe_allow_html=True
# )
