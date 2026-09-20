"""Configuration settings for the Grazioso Salvare application."""

import os


MONGO_USER = os.getenv("MONGO_USER")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD")
MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
MONGO_PORT = int(os.getenv("MONGO_PORT", "27017"))
MONGO_DB = os.getenv("MONGO_DB", "aac")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "animals")


def validate_config():
    """Verify that required MongoDB configuration values are available."""

    if not MONGO_USER or not MONGO_PASSWORD:
        raise ValueError(
            "MongoDB username and password must be set as environment variables."
        )
