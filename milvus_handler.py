from pymilvus import connections, FieldSchema, CollectionSchema, DataType, Collection, utility, Index
from typing import List
import logging

logger = logging.getLogger(__name__)

DEFAULT_ALIAS = 'default'

class MilvusHandler:
    def __init__(self, host: str = '127.0.0.1', port: str = '19530', collection_name: str = 'pdf_embeddings', dim: int = 768):
        self.host = host
        self.port = port
        self.collection_name = collection_name
        self.dim = dim
        self._connect()
        self._ensure_collection()

    def _connect(self):
        try:
            connections.connect(alias=DEFAULT_ALIAS, host=self.host, port=self.port)
            logger.info("Connected to Milvus at %s:%s", self.host, self.port)
        except Exception as e:
            logger.exception("Failed to connect to Milvus: %s", e)
            raise

    def _ensure_collection(self):
        try:
            # Define schema (needed if we need to create the collection)
            fields = [
                FieldSchema(name='pk', dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name='doc_id', dtype=DataType.VARCHAR, max_length=256),
                FieldSchema(name='summary', dtype=DataType.VARCHAR, max_length=4096),
                FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=self.dim)
            ]
            schema = CollectionSchema(fields, description='PDF summary embeddings')
            
            # Check if collection exists
            collection_exists = False
            try:
                collection_exists = utility.has_collection(self.collection_name)
                logger.info("Checked collection existence: %s", collection_exists)
            except Exception as check_error:
                logger.debug("has_collection check failed (likely doesn't exist): %s", str(check_error)[:100])
                collection_exists = False
            
            if collection_exists:
                # Collection exists, just load it
                logger.info("Collection '%s' already exists. Loading into memory...", self.collection_name)
                self.collection = Collection(name=self.collection_name)
                self.collection.load()
                entity_count = self.collection.num_entities
                logger.info("✓ Loaded existing collection '%s' with %d entities", self.collection_name, entity_count)
                return
            
            # Collection doesn't exist, create it fresh
            logger.info("Collection '%s' does not exist. Creating new collection...", self.collection_name)
            self.collection = Collection(name=self.collection_name, schema=schema)
            logger.info("✓ Collection '%s' created successfully", self.collection_name)

            # Create index on embedding field
            index_params = {
                'index_type': 'IVF_FLAT',
                'metric_type': 'COSINE',
                'params': {'nlist': 1024}
            }
            self.collection.create_index(field_name='embedding', index_params=index_params)
            logger.info("✓ Index created on embedding field")
            
            # Load collection into memory
            self.collection.load()
            logger.info("✓ Milvus collection '%s' initialized with dim=%d and loaded into memory", self.collection_name, self.dim)
        except Exception as e:
            logger.exception("Failed to ensure Milvus collection: %s", e)
            raise

    def get_collection_status(self) -> dict:
        """Get current collection status for debugging"""
        try:
            status = {
                "collection_name": self.collection_name,
                "num_entities": self.collection.num_entities,
                "collection_loaded": True,
                "embedding_dim": self.dim
            }
            logger.info("Collection Status: %s", status)
            return status
        except Exception as e:
            logger.exception("Failed to get collection status: %s", e)
            return {"error": str(e)}

    def insert_embedding(self, doc_id: str, summary: str, embedding: List[float]):
        """Insert a single embedding record. Returns the Milvus assigned primary key id."""
        try:
            logger.info("Inserting embedding for doc_id=%s, summary_length=%d, embedding_dim=%d", 
                       doc_id, len(summary), len(embedding))
            logger.debug("Embedding sample (first 5 values): %s", embedding[:5])
            
            # Milvus expects list of column-wise lists
            entities = [
                [doc_id],
                [summary],
                [embedding]
            ]
            logger.debug("Entities structure prepared for insertion")
            
            res = self.collection.insert(entities)
            logger.debug("Insert response: %s", res)
            
            # flush to make sure persisted
            self.collection.flush()
            logger.info("Collection flushed successfully")
            
            # return the generated primary keys
            pk = res.primary_keys[0] if hasattr(res, 'primary_keys') and res.primary_keys else None
            logger.info("Successfully inserted embedding for doc_id=%s with primary_key=%s", doc_id, pk)
            
            # Verify insertion
            collection_count = self.collection.num_entities
            logger.info("Collection now has %d entities", collection_count)
            
            return pk
        except Exception as e:
            logger.exception("Failed to insert embedding into Milvus: %s", e)
            raise

    def search(self, query_embedding: List[float], top_k: int = 5):
        try:
            logger.info("Loading collection '%s' into memory...", self.collection_name)
            self.collection.load()
            logger.info("Collection loaded. Embedding dimension: %d", len(query_embedding))
            logger.debug("Query embedding sample (first 5 values): %s", query_embedding[:5])
            
            # Get collection statistics before search
            try:
                collection_num = self.collection.num_entities
                logger.warning("⚠️ CRITICAL: Collection has %d entities before search", collection_num)
                if collection_num == 0:
                    logger.warning("🔴 COLLECTION IS EMPTY! No embeddings have been inserted.")
                    logger.warning("   → Please generate embeddings for documents in the app")
                    logger.warning("   → Go to 'View Extracted Data' page and click '🧠 Generate Embedding'")
            except Exception as e:
                logger.warning("Could not get collection entity count: %s", e)
            
            # Proper params for pymilvus 2.4.0
            search_params = {
                'metric_type': 'COSINE',
                'params': {'nprobe': 10}
            }
            logger.warning("🔵 Starting Milvus search with top_k=%d", top_k)
            
            result = self.collection.search(
                data=[query_embedding],
                anns_field='embedding',
                param=search_params,
                limit=top_k,
                output_fields=['doc_id', 'summary']
            )
            
            logger.warning("🟡 Search completed. Result type: %s", type(result))
            logger.warning("🟡 Result structure: %s", result)
            
            if result:
                for i, hits in enumerate(result):
                    logger.warning("🟡 Result group %d: %d hits", i, len(hits) if hits else 0)
                    if hits and len(hits) > 0:
                        for j, hit in enumerate(hits):
                            try:
                                # Access entity data properly
                                doc_id = hit.entity.get("doc_id") if hasattr(hit.entity, 'get') else hit.entity["doc_id"] if "doc_id" in hit.entity else "Unknown"
                                logger.info("  ✓ Hit %d: distance=%.4f, doc_id=%s", j, hit.distance, doc_id)
                            except Exception as entity_error:
                                logger.warning("  ⚠️ Hit %d: distance=%.4f, error reading doc_id: %s", j, hit.distance, entity_error)
                    else:
                        logger.warning("  ❌ No hits found in this group - Collection may be empty!")
            else:
                logger.warning("❌ Search returned None or empty result")
            
            return result
        except Exception as e:
            logger.exception("Milvus search failed: %s", e)
            raise
