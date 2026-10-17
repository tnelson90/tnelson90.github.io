# Example Python Code to Insert a Document 

from pymongo import MongoClient 
from bson.objectid import ObjectId 

class AnimalShelter(object): 
    """ CRUD operations for Animal collection in MongoDB """ 

    def __init__(self): 
        # Initializing the MongoClient. This helps to access the MongoDB 
        # databases and collections. This is hard-wired to use the aac 
        # database, the animals collection, and the aac user. 
        # 
        # You must edit the password below for your environment. 
        # 
        # Connection Variables 
        # 
        USER = 'aacuser' 
        PASS = 'aacuserCS340password' 
        HOST = 'localhost' 
        PORT = 27017 
        DB = 'aac' 
        COL = 'animals' 
        # 
        # Initialize Connection 
        # 
        self.client = MongoClient('mongodb://%s:%s@%s:%d' % (USER,PASS,HOST,PORT)) 
        self.database = self.client['%s' % (DB)] 
        self.collection = self.database['%s' % (COL)] 

    # Create a method to return the next available record number for use in the create method
            
    # Complete this create method to implement the C in CRUD. 
    def create(self, data):
        if data is not None:
            try:
                result = self.database.animals.insert_one(data)  # data should be dictionary
                return True if result.acknowledged else False # shows insert was succesful
            except:
                return False
        else: 
            raise Exception("Nothing to save, because data parameter is empty") 

    # Create method to implement the R in CRUD.
    def read(self, query):
        if query is not None:
            try:
                cursor = self.database.animals.find(query) # find() returns a cursor
                return list(cursor) # converts cursor to list
            except:
                return []
        else:
            raise Exception("Nothing to read, becasue query parameter is empty")
            
    # Update document(s) that match query; returns number modified
    def update(self, query, new_values, many=False):
        if query and new_values:
            # allow plain dicts or Mongo-style operators
            payload = (new_values if any(str(k).startswith('$') for k in new_values)
                       else {"$set": new_values})
            try:
                result = (self.database.animals.update_many(query, payload)
                          if many else
                          self.database.animals.update_one(query, payload))
                return result.modified_count
            except:
                return 0
        else:
            raise Exception("Nothing to update, because query or new_values parameter is empty")
            
    # Delete document(s) that match query; returns number removed
    def delete(self, query, many=False):
        if query:
            try:
                result = (self.database.animals.delete_many(query)
                          if many else
                          self.database.animals.delete_one(query))
                return result.deleted_count
            except:
                return 0
        else:
            raise Exception("Nothing to delete, because query parameter is empty")

