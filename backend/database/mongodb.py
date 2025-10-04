from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import os
from typing import Optional

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

# Database instance
db = Database()

# Alias for backward compatibility
async def init_db():
    """Initialize database connection and models"""
    await connect_to_mongo()

async def connect_to_mongo():
    """Create database connection"""
    # Get MongoDB URL from environment or use default
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "veazy_db")
    
    # Create MongoDB client
    db.client = AsyncIOMotorClient(mongodb_url)
    db.database = db.client[database_name]
    
    # Import all models we need
    from database.models.user import User
    from database.models.country import Country
    from database.models.visa_type_selection import VisaTypeSelection
    
    # Initialize Beanie with all models
    await init_beanie(
        database=db.database,
        document_models=[User, Country, VisaTypeSelection]
    )
    
    print(f"Connected to MongoDB database: {database_name}")

async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()
        print("Disconnected from MongoDB")

def get_database():
    """Get database instance"""
    return db.database