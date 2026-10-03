"""
MongoDB data-access module for the Grazioso Salvare application.

CS 499 Database Enhancement
"""

from pymongo import ASCENDING, MongoClient
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

class AnimalShelter:
    """Provides validated CRUD operations for the animal collection."""

    def __init__(self):
        """Initialize and verify the MongoDB connection."""
    
        # Validate required configuration before attempting a connection.
        validate_config()
    
        try:
            self.client = MongoClient(
                host=MONGO_HOST,
                port=MONGO_PORT,
                username=MONGO_USER,
                password=MONGO_PASSWORD,
                authSource=MONGO_DB,
                serverSelectionTimeoutMS=5000
            )
            
            self.database = self.client[MONGO_DB]
            self.collection = self.database[MONGO_COLLECTION]

            # Verify that MongoDB is reachable when the object is created.
            self.client.admin.command("ping")

            # Create indexes used by the application's rescue queries.
            self.ensure_indexes()

        except PyMongoError as error:
            raise ConnectionError(
                f"Unable to connect to MongoDB: {error}"
            ) from error

    @staticmethod
    def _validate_dictionary(value, name, allow_empty=False):
        """Validate dictionary input before it is sent to MongoDB."""
        if not isinstance(value, dict):
            raise TypeError(f"{name} must be a dictionary.")

        if not allow_empty and not value:
            raise ValueError(f"{name} cannot be empty.")

    def ensure_indexes(self):
        """
        Create indexes for fields commonly used by rescue-candidate queries.
        """
        try:
            self.collection.create_index(
                [
                    ("animal_type", ASCENDING),
                    ("breed", ASCENDING),
                    ("sex_upon_outcome", ASCENDING),
                    ("age_upon_outcome_in_weeks", ASCENDING)
                ],
                name="rescue_candidate_idx"
            )

        except PyMongoError as error:
            raise RuntimeError(
                f"Unable to create MongoDB indexes: {error}"
            ) from error

    def create(self, data):
        """Insert one animal document and return its inserted ID."""
        self._validate_dictionary(data, "data")

        try:
            result = self.collection.insert_one(data)

            if result.acknowledged:
                return result.inserted_id

            return None

        except PyMongoError as error:
            raise RuntimeError(
                f"Unable to create animal record: {error}"
            ) from error

    def read(self, query=None, projection=None, limit=0):
        """
        Retrieve animal documents matching a query.

        projection can be used to request only fields needed by the
        application instead of retrieving every field in each document.
        """
        if query is None:
            query = {}

        self._validate_dictionary(query, "query", allow_empty=True)

        if projection is not None:
            self._validate_dictionary(
                projection,
                "projection",
                allow_empty=True
            )

        if not isinstance(limit, int) or limit < 0:
            raise ValueError("limit must be a non-negative integer.")

        try:
            cursor = self.collection.find(query, projection)

            if limit > 0:
                cursor = cursor.limit(limit)

            return list(cursor)

        except PyMongoError as error:
            raise RuntimeError(
                f"Unable to read animal records: {error}"
            ) from error

    def update(self, query, new_values, many=False):
        """
        Update matching animal records.

        Returns information about both matched and modified documents.
        """
        self._validate_dictionary(query, "query")
        self._validate_dictionary(new_values, "new_values")

        if not isinstance(many, bool):
            raise TypeError("many must be True or False.")

        # Allow MongoDB update operators or automatically use $set
        # for a normal dictionary of field/value pairs.
        if any(str(key).startswith("$") for key in new_values):
            payload = new_values
        else:
            payload = {"$set": new_values}

        try:
            if many:
                result = self.collection.update_many(query, payload)
            else:
                result = self.collection.update_one(query, payload)

            return {
                "matched_count": result.matched_count,
                "modified_count": result.modified_count,
                "acknowledged": result.acknowledged
            }

        except PyMongoError as error:
            raise RuntimeError(
                f"Unable to update animal record: {error}"
            ) from error

    def delete(self, query, many=False):
        """
        Delete matching animal records and return the number deleted.
        """
        self._validate_dictionary(query, "query")

        if not isinstance(many, bool):
            raise TypeError("many must be True or False.")

        try:
            if many:
                result = self.collection.delete_many(query)
            else:
                result = self.collection.delete_one(query)

            return {
                "deleted_count": result.deleted_count,
                "acknowledged": result.acknowledged
            }

        except PyMongoError as error:
            raise RuntimeError(
                f"Unable to delete animal record: {error}"
            ) from error

    def close(self):
        """Close the MongoDB client connection."""
        self.client.close()
