"""
Database connection and configuration for MongoDB Atlas
"""
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
import os
from dotenv import load_dotenv

load_dotenv()

# MongoDB Atlas connection URI (will be provided by user)
MONGODB_URI = os.getenv("MONGODB_URI", "")

# Database and collection names
DB_NAME = "ats_scanner"
USERS_COLLECTION = "users"
SCANS_COLLECTION = "scans"

# Global database connection
_client = None
_db = None


def get_database():
    """Get database connection instance (singleton pattern)"""
    global _client, _db
    
    if _db is not None:
        return _db
    
    if not MONGODB_URI:
        raise ValueError("MONGODB_URI environment variable is not set. Please set it in your .env file.")
    
    try:
        _client = MongoClient(MONGODB_URI, serverSelectionTimeoutMS=5000)
        # Test the connection
        _client.admin.command('ping')
        _db = _client[DB_NAME]
        print(f"Successfully connected to MongoDB database: {DB_NAME}")
        return _db
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        raise ConnectionError(f"Failed to connect to MongoDB: {str(e)}")


def get_users_collection():
    """Get users collection"""
    db = get_database()
    return db[USERS_COLLECTION]


def get_scans_collection():
    """Get scans collection"""
    db = get_database()
    return db[SCANS_COLLECTION]


def close_connection():
    """Close MongoDB connection"""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        print("MongoDB connection closed")

