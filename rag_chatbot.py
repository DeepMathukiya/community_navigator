"""
RAG-based chatbot using Milvus for document retrieval and NVIDIA Nemotron for answer generation.
"""
from milvus_handler import MilvusHandler
from embedding_utils import get_embedding
from chatgpt_extractor import validate_extracted_data
from mongodb_handler import MongoDBHandler
from openai import OpenAI
from config import NVIDIA_API_KEY, NVIDIA_MODEL
import json
from logger_config import get_logger

logger = get_logger(__name__)


class RAGChatbot:
    def __init__(self, milvus_handler: MilvusHandler = None, mongo_handler: MongoDBHandler = None):
        """Initialize RAG chatbot with Milvus and MongoDB handlers."""
        logger.info("Initializing RAGChatbot...")
        try:
            self.milvus_handler = milvus_handler or MilvusHandler()
            logger.debug("Milvus handler initialized")
            
            self.mongo_handler = mongo_handler or MongoDBHandler()
            logger.debug("MongoDB handler initialized")
            
            self.client = OpenAI(
                base_url="https://integrate.api.nvidia.com/v1",
                api_key=NVIDIA_API_KEY
            )
            logger.debug("NVIDIA Nemotron API client initialized")
            logger.info("RAGChatbot initialization successful")
        except Exception as e:
            logger.exception("Failed to initialize RAGChatbot: %s", e)
            raise

    def search_related_documents(self, query: str, top_k: int = 5) -> list:
        """
        Search Milvus for documents related to the query.
        
        Args:
            query: User query string
            top_k: Number of top results to return
            
        Returns:
            list: List of dicts with doc_id, summary, score
        """
        logger.debug("Starting document search for query: %s (top_k=%d)", query[:100], top_k)
        try:
            # Generate embedding for the query
            logger.debug("Generating embedding for query...")
            query_embedding = get_embedding(query)
            logger.info("Query embedding generated with dimension: %d", len(query_embedding))
            logger.debug("Query embedding sample (first 5): %s", query_embedding[:5])
            
            # Search Milvus
            logger.info("Searching Milvus collection for similar documents...")
            try:
                search_results = self.milvus_handler.search(query_embedding, top_k=top_k)
                logger.info("Milvus search completed. Checking results...")
                logger.debug("Search results type: %s", type(search_results))
                logger.debug("Search results: %s", search_results)
            except Exception as milvus_error:
                error_msg = str(milvus_error).lower()
                if "collection not loaded" in error_msg or "bloom_filter" in error_msg:
                    logger.warning("Milvus collection not properly loaded. Attempting recovery...")
                    logger.info("Please ensure:")
                    logger.info("1. Milvus service is running on localhost:19530")
                    logger.info("2. At least one PDF has been uploaded and embedded")
                    logger.info("3. Run: docker restart milvus (if using Docker) or restart the service")
                    raise Exception("Milvus collection not available. Please upload and embed PDF documents first, then restart the app.")
                else:
                    logger.exception("Milvus search error: %s", milvus_error)
                    raise
            
            results = []
            if search_results:
                logger.info("Processing %d search result groups", len(search_results))
                for group_idx, hits in enumerate(search_results):
                    logger.debug("Group %d has %d hits", group_idx, len(hits))
                    for hit_idx, hit in enumerate(hits):
                        logger.debug("Processing hit %d: %s", hit_idx, hit)
                        
                        # Safely access entity data
                        try:
                            if hasattr(hit.entity, 'get'):
                                doc_id = hit.entity.get("doc_id") or "Unknown"
                                summary = hit.entity.get("summary") or ""
                            elif isinstance(hit.entity, dict):
                                doc_id = hit.entity.get("doc_id", "Unknown")
                                summary = hit.entity.get("summary", "")
                            else:
                                # Try direct access
                                doc_id = hit.entity["doc_id"] if "doc_id" in hit.entity else "Unknown"
                                summary = hit.entity["summary"] if "summary" in hit.entity else ""
                        except (KeyError, TypeError) as e:
                            logger.warning("Could not access entity data: %s", e)
                            doc_id = "Unknown"
                            summary = ""
                        
                        result = {
                            "doc_id": doc_id,
                            "summary": summary,
                            "similarity_score": hit.distance
                        }
                        logger.info("Found document: doc_id=%s, score=%.4f, summary_length=%d", 
                                   result["doc_id"], result["similarity_score"], len(result["summary"]))
                        
                        # Retrieve full document from MongoDB if needed
                        if result["doc_id"] != "Unknown":
                            try:
                                logger.debug("Retrieving full document from MongoDB for doc_id: %s", result["doc_id"])
                                mongo_doc = self.mongo_handler.get_document_by_id(result["doc_id"])
                                if mongo_doc:
                                    result["filename"] = mongo_doc.get("filename", "Unknown")
                                    result["full_info"] = mongo_doc.get("extracted_info", {})
                                    logger.info("Retrieved full document: %s", result["filename"])
                                else:
                                    logger.warning("MongoDB document not found for doc_id: %s", result["doc_id"])
                            except Exception as e:
                                logger.warning("Could not retrieve full doc from MongoDB for %s: %s", result["doc_id"], e)
                        results.append(result)

            else:
                logger.warning("No documents found in Milvus for query: %s", query)
            
            
            logger.info("Document search completed. Found %d related documents", len(results))
            return results
        
        except Exception as e:
            logger.exception("Error searching related documents: %s", e)
            raise

    def generate_answer(self, query: str, related_docs: list) -> dict:
        """
        Generate answer using NVIDIA Nemotron with retrieved documents and citations.
        
        Args:
            query: User query
            related_docs: List of related documents from search
            
        Returns:
            dict: Contains 'answer' and 'citations'
        """
        logger.debug("Generating answer for query with %d related documents", len(related_docs))
        try:
            if not NVIDIA_API_KEY:
                logger.error("NVIDIA_API_KEY not configured")
                raise Exception("NVIDIA_API_KEY not configured")
            
            # Build context from related documents with full extracted information
            doc_context = ""
            for i, doc in enumerate(related_docs, 1):
                doc_id = doc.get("doc_id", "Unknown")
                score = doc.get("similarity_score", 0)
                filename = doc.get("filename", "Unknown file")
                
                # Get full extracted information from MongoDB
                full_info = doc.get("full_info", {})
                
                # Build comprehensive document context
                doc_context += f"\n[{filename}] \n"
                doc_context += f"Document ID: {doc_id} | Relevance Score: {score:.2%}\n"
                doc_context += "-" * 60 + "\n"
                
                # Add all extracted information
                if full_info:
                    if full_info.get("summary"):
                        doc_context += f"Summary: {full_info.get('summary')}\n\n"
                    
                    if full_info.get("eligibility"):
                        eligibility = full_info.get("eligibility")
                        if isinstance(eligibility, list):
                            doc_context += f"Eligibility:\n"
                            for item in eligibility:
                                doc_context += f"  - {item}\n"
                        else:
                            doc_context += f"Eligibility: {eligibility}\n"
                        doc_context += "\n"
                    
                    if full_info.get("benefits"):
                        benefits = full_info.get("benefits")
                        if isinstance(benefits, list):
                            doc_context += f"Benefits:\n"
                            for item in benefits:
                                doc_context += f"  - {item}\n"
                        else:
                            doc_context += f"Benefits: {benefits}\n"
                        doc_context += "\n"
                    
                    if full_info.get("apply_date"):
                        doc_context += f"Application Date: {full_info.get('apply_date')}\n\n"
                    
                    if full_info.get("application_process"):
                        process = full_info.get("application_process")
                        if isinstance(process, list):
                            doc_context += f"Application Process:\n"
                            for idx, step in enumerate(process, 1):
                                doc_context += f"  {idx}. {step}\n"
                        else:
                            doc_context += f"Application Process: {process}\n"
                        doc_context += "\n"
                else:
                    # Fallback to summary if full_info not available
                    summary = doc.get("summary", "No summary available")
                    doc_context += f"Summary: {summary}\n\n"
                
                logger.info("Added document %d to context: %s (score: %.4f, info_size: %d)", 
                           i, filename, score, len(str(full_info)))
            
            # Check if we have any documents
            has_documents = bool(doc_context.strip())
            if not has_documents:
                logger.warning("No document context available for answer generation. Will provide general answer.")
                doc_context = "No related documents found in the knowledge base."
                
                # Prompt for when no documents are available
                prompt = f"""You are a helpful assistant. A user has asked a question, but there are no relevant documents in the knowledge base to answer it directly.

User Query: {query}

Since no related documents are available, please provide a helpful general answer to the user's query based on your general knowledge. Be honest about the limitations and suggest that the user might want to upload relevant documents if they need domain-specific information.

Please provide a helpful response:"""
            else:
                # Prompt for when documents are available
                prompt = f"""You are a helpful assistant answering user queries based on detailed document information.

User Query: {query}

Related Documents:
{doc_context}

Instructions:
1. Answer the user's query based ONLY on the information from the related documents above
2. Use the document sections (Summary, Eligibility, Benefits, Application Date, Application Process) to provide comprehensive answers
3. If the answer is found in the documents, cite the specific document(s) by their number [Document X]
4. If information is not available in the documents, clearly state "Based on the provided documents, this information is not available"
5. Keep your answer concise and well-structured
6. Always include citations in format: [Document X] for each claim
7. When discussing eligibility or benefits, use the specific items from the documents

Please provide your answer with proper citations:"""
            
            logger.debug("Calling NVIDIA Nemotron API with prompt length: %d", len(prompt))
            
            # Call NVIDIA Nemotron API
            completion = self.client.chat.completions.create(
                model=NVIDIA_MODEL,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
            )
            
            answer = completion.choices[0].message.content.strip()
            logger.debug("Received answer from NVIDIA Nemotron (length: %d)", len(answer))
            
            # Extract citations from answer (only if we had documents)
            citations = self._extract_citations(answer, related_docs) if has_documents else []
            logger.info("Extracted %d citations from answer", len(citations))
            
            result = {
                "answer": answer,
                "citations": citations,
                "related_documents": related_docs,
                "has_documents": has_documents
            }
            
            logger.info("Answer generation successful with %d citations", len(citations))
            return result
        
        except Exception as e:
            logger.exception("Error generating answer: %s", e)
            raise

    def _extract_citations(self, answer: str, related_docs: list) -> list:
        """
        Extract document citations from the answer.
        
        Args:
            answer: Generated answer with citations
            related_docs: List of related documents
            
        Returns:
            list: List of citation dicts
        """
        logger.debug("Extracting citations from answer (length: %d)", len(answer))
        citations = []
        try:
            # Find all [Document X] patterns in the answer
            import re
            pattern = r'\[Document (\d+)\]'
            matches = re.findall(pattern, answer)
            logger.debug("Found %d citation patterns in answer", len(matches))
            
            for match in matches:
                doc_num = int(match)
                if 0 < doc_num <= len(related_docs):
                    doc = related_docs[doc_num - 1]
                    citation = {
                        "document_number": doc_num,
                        "doc_id": doc.get("doc_id", "Unknown"),
                        "filename": doc.get("filename", "Unknown"),
                        "summary": doc.get("summary", "")[:200] + "..." if len(doc.get("summary", "")) > 200 else doc.get("summary", "")
                    }
                    if citation not in citations:  # Avoid duplicates
                        citations.append(citation)
                        logger.debug("Added citation: Document %d - %s", doc_num, citation["filename"])
                    else:
                        logger.debug("Skipped duplicate citation for Document %d", doc_num)
                else:
                    logger.warning("Invalid document number in citation: %d (available: %d)", doc_num, len(related_docs))
            
            logger.info("Citation extraction complete: %d unique citations", len(citations))
        except Exception as e:
            logger.warning("Error extracting citations: %s", e)
        
        return citations

    def chat(self, query: str, top_k: int = 5) -> dict:
        """
        End-to-end chat: search documents and generate answer with citations.
        
        Args:
            query: User query
            top_k: Number of top related documents to retrieve
            
        Returns:
            dict: Contains answer, citations, and related documents
        """
        logger.info("Starting chat session with query: %s", query[:100])
        try:
            # Step 1: Search for related documents
            logger.debug("Step 1/2: Searching for related documents...")
            related_docs = self.search_related_documents(query, top_k=top_k)
            logger.info("Step 1/2 complete: Found %d related documents", len(related_docs))
            
            # Step 2: Generate answer using NVIDIA Nemotron
            logger.debug("Step 2/2: Generating answer with NVIDIA Nemotron...")
            result = self.generate_answer(query, related_docs)
            logger.info("Step 2/2 complete: Answer generated with %d citations", len(result.get("citations", [])))
            
            logger.info("Chat session successful for query: %s", query[:100])
            return result
        
        except Exception as e:
            logger.exception("Error in chat session: %s", e)
            return {
                "answer": f"I encountered an error processing your query: {str(e)}",
                "citations": [],
                "related_documents": [],
                "error": str(e)
            }
