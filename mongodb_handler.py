from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from config import MONGODB_URI, MONGODB_DB_NAME, MONGODB_COLLECTION_NAME
from datetime import datetime
from typing import Dict, List, Optional


class MongoDBHandler:
    """Handle all MongoDB operations"""
    
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None
        self.connect()
    
    def connect(self):
        """
        Connect to MongoDB
        
        Raises:
            Exception: If connection fails
        """
        try:
            self.client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
            # Test connection
            self.client.admin.command('ping')
            self.db = self.client[MONGODB_DB_NAME]
            self.collection = self.db[MONGODB_COLLECTION_NAME]
            print("MongoDB connection successful")
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            raise Exception(f"Failed to connect to MongoDB: {str(e)}")
    
    def insert_extracted_data(self, data: Dict) -> str:
        """
        Insert extracted data into MongoDB
        
        Args:
            data: Dictionary containing extracted information
            
        Returns:
            str: Inserted document ID
        """
        try:
            data['created_at'] = datetime.now()
            result = self.collection.insert_one(data)
            return str(result.inserted_id)
        except Exception as e:
            raise Exception(f"Error inserting data into MongoDB: {str(e)}")
    
    def get_all_documents(self, limit: int = 100) -> List[Dict]:
        """
        Get all documents from collection
        
        Args:
            limit: Maximum number of documents to retrieve
            
        Returns:
            List of documents
        """
        try:
            documents = list(self.collection.find().limit(limit))
            # Convert ObjectId to string for JSON serialization
            for doc in documents:
                doc['_id'] = str(doc['_id'])
            return documents
        except Exception as e:
            raise Exception(f"Error retrieving documents from MongoDB: {str(e)}")
    
    def get_document_by_id(self, document_id: str) -> Optional[Dict]:
        """
        Get document by ID
        
        Args:
            document_id: MongoDB document ID
            
        Returns:
            Document or None
        """
        try:
            from bson.objectid import ObjectId
            doc = self.collection.find_one({"_id": ObjectId(document_id)})
            if doc:
                doc['_id'] = str(doc['_id'])
            return doc
        except Exception as e:
            raise Exception(f"Error retrieving document from MongoDB: {str(e)}")
    
    def update_document(self, document_id: str, update_data: Dict) -> bool:
        """
        Update document in MongoDB
        
        Args:
            document_id: MongoDB document ID
            update_data: Data to update
            
        Returns:
            bool: True if updated successfully
        """
        try:
            from bson.objectid import ObjectId
            update_data['updated_at'] = datetime.now()
            result = self.collection.update_one(
                {"_id": ObjectId(document_id)},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            raise Exception(f"Error updating document in MongoDB: {str(e)}")
    
    def delete_document(self, document_id: str) -> bool:
        """
        Delete document from MongoDB
        
        Args:
            document_id: MongoDB document ID
            
        Returns:
            bool: True if deleted successfully
        """
        try:
            from bson.objectid import ObjectId
            result = self.collection.delete_one({"_id": ObjectId(document_id)})
            return result.deleted_count > 0
        except Exception as e:
            raise Exception(f"Error deleting document from MongoDB: {str(e)}")
    
    def close(self):
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
