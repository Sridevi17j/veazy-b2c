import asyncio
from database.mongodb import connect_to_mongo, close_mongo_connection
from database.models.user import User, UserProfile

async def create_sample_users():
    print("Creating sample users in MongoDB...")
    
    try:
        # Connect to MongoDB
        await connect_to_mongo()
        
        # Create multiple sample users
        users_data = [
            {
                "email": "john.doe@example.com",
                "phone": "+1234567890",
                "preferred_name": "John Doe",
                "profile": UserProfile(nationality="US", preferredLanguage="en", frequentFlyer="AA123")
            },
            {
                "email": "jane.smith@example.com", 
                "phone": "+1987654321",
                "preferred_name": "Jane Smith",
                "profile": UserProfile(nationality="UK", preferredLanguage="en", frequentFlyer="BA456")
            },
            {
                "email": "carlos.rodriguez@example.com",
                "phone": "+1555666777",
                "preferred_name": "Carlos Rodriguez", 
                "profile": UserProfile(nationality="ES", preferredLanguage="es", frequentFlyer="IB789")
            }
        ]
        
        # Create and save users
        for user_data in users_data:
            user = User(**user_data)
            await user.save()
            print(f"Created user: {user.preferred_name} (ID: {user.id})")
        
        # Count total users
        total_users = await User.count()
        print(f"Total users in database: {total_users}")
        
        print("Sample data created successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
    
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(create_sample_users())