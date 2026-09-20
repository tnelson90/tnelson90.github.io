

from pymongo import MongoClient
from pymongo.errors import PyMongoError

from config import (
    MONGO_USER,
    MONGO_PASSWORD,
    MONGO_HOST,
    MONGO_PORT,
    MONGO_DB,
    MONGO_COLLECTION,
    validate_config
) 

class AnimalShelter(object): 
    """ CRUD operations for Animal collection in MongoDB """ 

    def __init__(self):
        """Initialize the MongoDB connection and animal collection."""
    
        validate_config()
    
        try:
            self.client = MongoClient(
                MONGO_HOST,
                MONGO_PORT,
                username=MONGO_USER,
                password=MONGO_PASSWORD
            )
    
            self.database = self.client[MONGO_DB]
            self.collection = self.database[MONGO_COLLECTION]
    
            self.client.admin.command("ping")
    
        except PyMongoError as error:
            raise ConnectionError(
                f"Unable to connect to MongoDB: {error}"
            ) from error 

    # Create a method to return the next available record number for use in the create method
            
    # Complete this create method to implement the C in CRUD. 
    def create(self, data):
        """Create a new animal record."""
    
        if not isinstance(data, dict) or not data:
            raise ValueError("Data must be provided as a non-empty dictionary.")
    
        try:
            result = self.collection.insert_one(data)
            return result.acknowledged
    
        except PyMongoError as error:
            print(f"Error creating animal record: {error}")
            return False 

    # Create method to implement the R in CRUD.
    def read(self, query=None):
        """Read animal records matching the supplied query."""
    
        if query is None:
            query = {}
    
        if not isinstance(query, dict):
            raise ValueError("Query must be a dictionary.")
    
        try:
            return list(self.collection.find(query))
    
        except PyMongoError as error:
            print(f"Error reading animal records: {error}")
            return []
            
    # Update document(s) that match query; returns number modified
    def update(self, query, new_values, many=False):
        """Update one or more animal records."""
    
        if not isinstance(query, dict) or not query:
            raise ValueError("Query must be a non-empty dictionary.")
    
        if not isinstance(new_values, dict) or not new_values:
            raise ValueError("New values must be a non-empty dictionary.")
    
        payload = (
            new_values
            if any(str(key).startswith("$") for key in new_values)
            else {"$set": new_values}
        )
    
        try:
            if many:
                result = self.collection.update_many(query, payload)
            else:
                result = self.collection.update_one(query, payload)
    
            return result.modified_count
    
        except PyMongoError as error:
            print(f"Error updating animal record: {error}")
            return 0
            
    # Delete document(s) that match query; returns number removed
    def delete(self, query, many=False):
        """Delete one or more animal records."""
    
        if not isinstance(query, dict) or not query:
            raise ValueError("Query must be a non-empty dictionary.")
    
        try:
            if many:
                result = self.collection.delete_many(query)
            else:
                result = self.collection.delete_one(query)
    
            return result.deleted_count
    
        except PyMongoError as error:
            print(f"Error deleting animal record: {error}")
            return 0

