"""MongoDB database connection and configuration"""
import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

load_dotenv()

# MongoDB connection string
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
DATABASE_NAME = os.getenv("DATABASE_NAME", "visioncore_db")

# Global database instance
mongodb_client: AsyncIOMotorClient = None
mongodb_db: AsyncIOMotorDatabase = None


async def connect_to_mongo():
    """Create MongoDB connection"""
    global mongodb_client, mongodb_db
    
    try:
        mongodb_client = AsyncIOMotorClient(MONGODB_URL)
        mongodb_db = mongodb_client[DATABASE_NAME]
        
        # Verify connection
        await mongodb_db.command("ping")
        print("✓ Connected to MongoDB")
        
        # Create collections and indexes
        await _create_indexes()
    except Exception as e:
        print(f"✗ Error connecting to MongoDB: {e}")
        raise


async def close_mongo_connection():
    """Close MongoDB connection"""
    global mongodb_client
    
    if mongodb_client:
        mongodb_client.close()
        print("✓ MongoDB connection closed")


async def _create_indexes():
    """Create necessary database indexes"""
    users_collection = mongodb_db["users"]
    
    # Create unique index on email
    await users_collection.create_index("email", unique=True)
    await users_collection.create_index("username", unique=True)
    
    print("✓ Database indexes created")


def get_database() -> AsyncIOMotorDatabase:
    """Get database instance"""
    if mongodb_db is None:
        raise RuntimeError("Database not connected. Call connect_to_mongo() first")
    return mongodb_db
