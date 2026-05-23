"""
Quick debugging script to diagnose search issues
Run: python debug_search.py
"""
import logging
from embedding_utils import get_embedding
from milvus_handler import MilvusHandler
from mongodb_handler import MongoDBHandler
from logger_config import get_logger

logger = get_logger(__name__)
logging.basicConfig(level=logging.DEBUG)

def debug_search():
    """Debug the search pipeline"""
    print("\n" + "="*60)
    print("🔍 SEARCH DEBUG UTILITY")
    print("="*60 + "\n")
    
    try:
        # 1. Test embedding generation
        print("1️⃣ Testing Embedding Generation...")
        test_text = "What are the benefits of this program?"
        embedding = get_embedding(test_text)
        print(f"   ✓ Embedding dimension: {len(embedding)}")
        print(f"   ✓ First 5 values: {embedding[:5]}")
        
        # 2. Test Milvus connection
        print("\n2️⃣ Testing Milvus Collection...")
        milvus = MilvusHandler()
        print(f"   ✓ Connected to Milvus")
        print(f"   ✓ Collection name: pdf_embeddings")
        
        entity_count = milvus.collection.num_entities
        print(f"   ✓ Total entities in collection: {entity_count}")
        
        if entity_count == 0:
            print("   ⚠️ WARNING: No embeddings in collection!")
            print("   → Solution: Generate embeddings for documents first")
        
        # 3. Test Milvus search
        print("\n3️⃣ Testing Milvus Search...")
        search_results = milvus.search(embedding, top_k=5)
        print(f"   ✓ Search completed")
        print(f"   ✓ Result type: {type(search_results)}")
        
        if search_results and len(search_results) > 0:
            hits = search_results[0]
            print(f"   ✓ Number of hits: {len(hits)}")
            
            for i, hit in enumerate(hits):
                try:
                    if hasattr(hit.entity, 'get'):
                        doc_id = hit.entity.get('doc_id') or 'N/A'
                        summary = hit.entity.get('summary') or 'N/A'
                    else:
                        doc_id = hit.entity["doc_id"] if "doc_id" in hit.entity else "N/A"
                        summary = hit.entity["summary"] if "summary" in hit.entity else "N/A"
                except (KeyError, TypeError):
                    doc_id = 'N/A'
                    summary = 'N/A'
                
                print(f"\n   Hit {i+1}:")
                print(f"      Distance (similarity): {hit.distance:.4f}")
                print(f"      Doc ID: {doc_id}")
                summary_text = summary[:100] if isinstance(summary, str) else str(summary)[:100]
                print(f"      Summary (first 100 chars): {summary_text}")
        else:
            print("   ⚠️ WARNING: No search results returned!")
        
        # 4. Test MongoDB connection
        print("\n4️⃣ Testing MongoDB...")
        mongo = MongoDBHandler()
        doc_count = mongo.collection.count_documents({})
        print(f"   ✓ Connected to MongoDB")
        print(f"   ✓ Total documents: {doc_count}")
        
        if doc_count > 0:
            sample_doc = mongo.collection.find_one()
            if sample_doc:
                print(f"   ✓ Sample document ID: {sample_doc.get('_id')}")
                print(f"   ✓ Sample filename: {sample_doc.get('filename')}")
                summary = sample_doc.get('extracted_info', {}).get('summary', '')
                print(f"   ✓ Sample summary length: {len(summary)} chars")
        
        print("\n" + "="*60)
        print("✅ DEBUG COMPLETED")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        logger.exception("Debug error")

if __name__ == "__main__":
    debug_search()
