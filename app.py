import streamlit as st
import os
from pdf_handler import save_uploaded_pdf, extract_text_from_pdf, get_pdf_info, delete_pdf_file
from chatgpt_extractor import extract_information_from_pdf, validate_extracted_data
from mongodb_handler import MongoDBHandler
import json
from datetime import datetime

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

# Sidebar
st.sidebar.title("📋 Navigation")
page = st.sidebar.radio(
    "Select a page:",
    ["Upload & Extract", "View Extracted Data", "Database Statistics"]
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
                            st.success(f"✓ Data saved to database! Document ID: {doc_id}")
                    except Exception as e:
                        st.error(f"❌ Error saving to database: {str(e)}")
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
                        
                        # Delete button
                        if st.button(f"🗑️ Delete Document {idx}", key=f"delete_{doc['_id']}"):
                            try:
                                if st.session_state.db_handler.delete_document(doc['_id']):
                                    st.success("✓ Document deleted successfully!")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"❌ Error deleting document: {str(e)}")
            else:
                st.info("No documents found in database.")
        
        except Exception as e:
            st.error(f"❌ Error loading data: {str(e)}")
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
    else:
        st.warning("⚠️ Database not connected. Cannot load statistics.")

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
