from mongoengine import connect, disconnect
from .config import settings
import logging

logger = logging.getLogger(__name__)

def connect_to_mongo():
    """Connect to MongoDB database."""
    try:
        connect(db=settings.MONGODB_DATABASE, host=settings.MONGODB_URI)
        logger.info(f"Connected to MongoDB database: {settings.MONGODB_DATABASE}")
    except Exception as e:
        logger.error(f"Failed to connect to MongoDB: {str(e)}")
        raise

def disconnect_from_mongo():
    """Disconnect from MongoDB database."""
    try:
        disconnect()
        logger.info("Disconnected from MongoDB")
    except Exception as e:
        logger.error(f"Error disconnecting from MongoDB: {str(e)}") 