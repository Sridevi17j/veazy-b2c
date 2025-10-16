# migrations/add_profile_fields.py
import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def migrate_user_profile_fields():
    """
    Migration script to add profile fields to existing User documents
    This script adds the following fields:
    - first_name: Optional[str] = None
    - last_name: Optional[str] = None
    Note: email, phone, preferred_name already exist
    """
    
    # Get MongoDB connection details
    mongodb_url = os.getenv('MONGODB_URL')
    database_name = os.getenv('DATABASE_NAME', 'veazy_db')
    
    if not mongodb_url:
        print("Error: MONGODB_URL not found in environment variables")
        return
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient(mongodb_url)
        db = client[database_name]
        users_collection = db.users
        
        print(f"Connected to MongoDB database: {database_name}")
        
        # Find all existing users
        existing_users = await users_collection.find({}).to_list(length=None)
        total_users = len(existing_users)
        
        print(f"Found {total_users} existing users to migrate")
        
        if total_users == 0:
            print("No users found in the collection")
            return
        
        # Update fields for existing users
        update_operations = []
        
        for user in existing_users:
            user_id = user['_id']
            
            # Prepare update fields (only add if they don't exist)
            update_fields = {}
            
            if 'first_name' not in user:
                update_fields['first_name'] = None
                
            if 'last_name' not in user:
                update_fields['last_name'] = None
                
            # Ensure updated_at exists
            if 'updated_at' not in user:
                update_fields['updated_at'] = datetime.utcnow()
            
            # Only update if there are fields to add
            if update_fields:
                update_operations.append({
                    'filter': {'_id': user_id},
                    'update': {'$set': update_fields}
                })
        
        # Execute bulk update if there are operations
        if update_operations:
            print(f"Updating {len(update_operations)} users with new profile fields...")
            
            updated_count = 0
            
            for operation in update_operations:
                result = await users_collection.update_one(
                    operation['filter'], 
                    operation['update']
                )
                if result.modified_count > 0:
                    updated_count += 1
            
            print(f"Successfully updated {updated_count} users")
        else:
            print("All users already have the required profile fields")
        
        # Verify the migration by checking a few documents
        print("\nVerifying migration...")
        sample_users = await users_collection.find({}).limit(3).to_list(length=3)
        
        for user in sample_users:
            print(f"User {user.get('_id')}:")
            print(f"  - first_name: {user.get('first_name', 'MISSING')}")
            print(f"  - last_name: {user.get('last_name', 'MISSING')}")
            print(f"  - email: {user.get('email', 'MISSING')}")
            print(f"  - phone: {user.get('phone', 'MISSING')}")
            print(f"  - preferred_name: {user.get('preferred_name', 'MISSING')}")
            print()
        
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        raise
    finally:
        # Close the connection
        client.close()
        print("Database connection closed")

async def rollback_profile_migration():
    """
    Rollback script to remove profile fields from User documents
    Use this if you need to undo the migration
    """
    
    mongodb_url = os.getenv('MONGODB_URL')
    database_name = os.getenv('DATABASE_NAME', 'veazy_db')
    
    if not mongodb_url:
        print("Error: MONGODB_URL not found in environment variables")
        return
    
    try:
        client = AsyncIOMotorClient(mongodb_url)
        db = client[database_name]
        users_collection = db.users
        
        print("Rolling back profile fields migration...")
        
        # Remove profile fields
        result = await users_collection.update_many(
            {},
            {
                '$unset': {
                    'first_name': '',
                    'last_name': ''
                }
            }
        )
        
        print(f"Rollback completed. Modified {result.modified_count} documents")
        
    except Exception as e:
        print(f"Error during rollback: {e}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        print("Running rollback migration...")
        asyncio.run(rollback_profile_migration())
    else:
        print("Running forward migration...")
        asyncio.run(migrate_user_profile_fields())