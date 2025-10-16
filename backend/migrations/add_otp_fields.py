# migrations/add_otp_fields.py
import asyncio
import os
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()

async def migrate_user_collection():
    """
    Migration script to add OTP-related fields to existing User documents
    This script adds the following fields:
    - otp_code: Optional[str] = None
    - otp_expires_at: Optional[datetime] = None  
    - otp_attempts: int = 0
    - verified_at: Optional[datetime] = None
    - session_token: Optional[str] = None
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
            
            if 'otp_code' not in user:
                update_fields['otp_code'] = None
                
            if 'otp_expires_at' not in user:
                update_fields['otp_expires_at'] = None
                
            if 'otp_attempts' not in user:
                update_fields['otp_attempts'] = 0
                
            if 'verified_at' not in user:
                update_fields['verified_at'] = None
                
            if 'session_token' not in user:
                update_fields['session_token'] = None
                
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
            print(f"Updating {len(update_operations)} users with new OTP fields...")
            
            # Execute updates in batches of 100
            batch_size = 100
            updated_count = 0
            
            for i in range(0, len(update_operations), batch_size):
                batch = update_operations[i:i + batch_size]
                
                for operation in batch:
                    result = await users_collection.update_one(
                        operation['filter'], 
                        operation['update']
                    )
                    if result.modified_count > 0:
                        updated_count += 1
                
                print(f"Processed batch {i//batch_size + 1}/{(len(update_operations) + batch_size - 1)//batch_size}")
            
            print(f"Successfully updated {updated_count} users")
        else:
            print("All users already have the required OTP fields")
        
        # Verify the migration by checking a few documents
        print("\nVerifying migration...")
        sample_users = await users_collection.find({}).limit(3).to_list(length=3)
        
        for user in sample_users:
            print(f"User {user.get('_id')}:")
            print(f"  - otp_code: {user.get('otp_code', 'MISSING')}")
            print(f"  - otp_expires_at: {user.get('otp_expires_at', 'MISSING')}")
            print(f"  - otp_attempts: {user.get('otp_attempts', 'MISSING')}")
            print(f"  - verified_at: {user.get('verified_at', 'MISSING')}")
            print(f"  - session_token: {user.get('session_token', 'MISSING')}")
            print()
        
        print("Migration completed successfully!")
        
    except Exception as e:
        print(f"Error during migration: {e}")
        raise
    finally:
        # Close the connection
        client.close()
        print("Database connection closed")

async def rollback_migration():
    """
    Rollback script to remove OTP-related fields from User documents
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
        
        print("Rolling back OTP fields migration...")
        
        # Remove OTP-related fields
        result = await users_collection.update_many(
            {},
            {
                '$unset': {
                    'otp_code': '',
                    'otp_expires_at': '',
                    'otp_attempts': '',
                    'verified_at': '',
                    'session_token': ''
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
        asyncio.run(rollback_migration())
    else:
        print("Running forward migration...")
        asyncio.run(migrate_user_collection())