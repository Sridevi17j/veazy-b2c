import asyncio
from database.mongodb import connect_to_mongo, close_mongo_connection
from database.models.user import User, UserProfile

async def test_create_user():
    print("Testing MongoDB user creation...")
    
    try:
        # Connect to MongoDB
        await connect_to_mongo()
        
        # Create a test user
        test_profile = UserProfile(
            nationality="US",
            preferredLanguage="en", 
            frequentFlyer="AA123"
        )
        
        test_user = User(
            email="john@example.com",
            phone="+1234567890",
            preferred_name="John Doe",
            profile=test_profile
        )
        
        # Save user to MongoDB
        await test_user.save()
        print(f"User created with ID: {test_user.id}")
        
        # Find the user back
        found_user = await User.find_one({"email": "john@example.com"})
        if found_user:
            print(f"Found user: {found_user.preferred_name}")
            print(f"Email: {found_user.email}")
            print(f"Phone: {found_user.phone}")
            print(f"Nationality: {found_user.profile.nationality}")
            print(f"Language: {found_user.profile.preferredLanguage}")
        
        print("User creation test successful!")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        # Close connection
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(test_create_user())