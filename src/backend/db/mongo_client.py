import os
from pymongo import MongoClient
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# Singleton client
_CLIENT = None

def get_mongo_client():
    global _CLIENT
    if _CLIENT is None:
        import urllib.parse
        
        mongo_uri = os.getenv("MONGO_URI")
        
        # Check for granular credentials to build safe URI
        username = os.getenv("MONGO_USERNAME")
        password = os.getenv("MONGO_PASSWORD")
        cluster = os.getenv("MONGO_CLUSTER")
        
        if username and password and cluster:
            # URL encode credentials
            user_safe = urllib.parse.quote_plus(username)
            pass_safe = urllib.parse.quote_plus(password)
            
            # Construct Atlas URI
            mongo_uri = f"mongodb+srv://{user_safe}:{pass_safe}@{cluster}/?appName=Cluster0"
            logger.info(f"Connecting to MongoDB Atlas Cluster: {cluster}")
        
        try:
            if not mongo_uri:
                # Fallback for local dev
                mongo_uri = "mongodb://localhost:27017"
                logger.warning("No MongoDB config found, using localhost default.")

            _CLIENT = MongoClient(mongo_uri)
            # Verify connection
            _CLIENT.admin.command('ping')
            logger.info("Successfully connected to MongoDB.")
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise e
    return _CLIENT

def get_database():
    client = get_mongo_client()
    return client.get_database("resume_matcher")

def get_jobs_collection():
    db = get_database()
    return db.get_collection("jobs")

def get_candidates_collection():
    db = get_database()
    return db.get_collection("candidates")
