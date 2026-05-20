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
            if utility.has_collection(self.collection_name):
                self.collection = Collection(self.collection_name)
                return

            fields = [
                FieldSchema(name='pk', dtype=DataType.INT64, is_primary=True, auto_id=True),
                FieldSchema(name='doc_id', dtype=DataType.VARCHAR, max_length=256),
                FieldSchema(name='summary', dtype=DataType.VARCHAR, max_length=4096),
                FieldSchema(name='embedding', dtype=DataType.FLOAT_VECTOR, dim=self.dim)
            ]
            schema = CollectionSchema(fields, description='PDF summary embeddings')
            self.collection = Collection(self.collection_name, schema)

            # create index on embedding
            index_params = {
                'index_type': 'IVF_FLAT',
                'metric_type': 'COSINE',
                'params': {'nlist': 1024}
            }
            self.collection.create_index(field_name='embedding', index_params=index_params)
            # load into memory
            self.collection.load()
            logger.info("Created Milvus collection '%s' with dim=%s", self.collection_name, self.dim)
        except Exception as e:
            logger.exception("Failed to ensure Milvus collection: %s", e)
            raise

    def insert_embedding(self, doc_id: str, summary: str, embedding: List[float]):
        """Insert a single embedding record. Returns the Milvus assigned primary key id."""
        try:
            # Milvus expects list of column-wise lists
            entities = [
                [doc_id],
                [summary],
                [embedding]
            ]
            res = self.collection.insert(entities)
            # flush to make sure persisted
            self.collection.flush()
            # return the generated primary keys
            pk = res.primary_keys[0] if hasattr(res, 'primary_keys') and res.primary_keys else None
            logger.info("Inserted embedding for doc_id=%s pk=%s", doc_id, pk)
            return pk
        except Exception as e:
            logger.exception("Failed to insert embedding into Milvus: %s", e)
            raise

    def search(self, query_embedding: List[float], top_k: int = 5):
        try:
            self.collection.load()
            result = self.collection.search([query_embedding], 'embedding', params={"metric_type": "COSINE", "params": {"nprobe": 10}}, limit=top_k, output_fields=['doc_id', 'summary'])
            return result
        except Exception as e:
            logger.exception("Milvus search failed: %s", e)
            raise
