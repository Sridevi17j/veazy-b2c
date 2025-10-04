import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from database.models.user import User, UserProfile

async def test_simple():
    print("Testing simple MongoDB connection...")
    
    try:
        # Simple MongoDB connection
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        database = client["veazy_db"]
        
        # Initialize Beanie with just User model
        await init_beanie(database=database, document_models=[User])
        
        print("Connected to MongoDB successfully")
        
        # Create a test user
        test_user = User(
            email="test@example.com",
            phone="+1234567890",
            preferred_name="Test User",
            profile=UserProfile(
                nationality="US",
                preferredLanguage="en"
            )
        )
        
        # Save user
        await test_user.save()
        print(f"User created with ID: {test_user.id}")
        
        # Find user
        found_user = await User.find_one({"email": "test@example.com"})
        if found_user:
            print(f"Found user: {found_user.preferred_name}")
            print(f"Nationality: {found_user.profile.nationality}")
        
        print("Test completed successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(test_simple())