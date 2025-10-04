#!/usr/bin/env python3
"""
Export local MongoDB data to MongoDB Atlas
"""
import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from database.models.visa_type_selection import VisaTypeSelection
from database.models.country import Country

async def export_local_data():
    """Export data from local MongoDB"""
    print("🔄 Connecting to local MongoDB...")
    
    # Connect to local MongoDB
    local_client = AsyncIOMotorClient("mongodb://localhost:27017")
    local_db = local_client["veazy_db"]
    
    # Initialize Beanie with local connection
    await init_beanie(database=local_db, document_models=[VisaTypeSelection, Country])
    
    # Export VisaTypeSelection data
    print("📤 Exporting VisaTypeSelection data...")
    visa_selections = await VisaTypeSelection.find_all().to_list()
    visa_data = []
    for selection in visa_selections:
        visa_data.append(selection.dict())
    
    # Export Country data
    print("📤 Exporting Country data...")
    countries = await Country.find_all().to_list()
    country_data = []
    for country in countries:
        country_data.append(country.dict())
    
    # Save to JSON files
    os.makedirs("./data_export", exist_ok=True)
    
    with open("./data_export/visa_type_selections.json", "w", encoding="utf-8") as f:
        json.dump(visa_data, f, indent=2, default=str)
    
    with open("./data_export/countries.json", "w", encoding="utf-8") as f:
        json.dump(country_data, f, indent=2, default=str)
    
    print(f"✅ Exported {len(visa_data)} visa selections and {len(country_data)} countries")
    print("📁 Data saved to ./data_export/ folder")
    
    local_client.close()

async def import_to_atlas(atlas_connection_string):
    """Import data to MongoDB Atlas"""
    print("🔄 Connecting to MongoDB Atlas...")
    
    # Connect to Atlas
    atlas_client = AsyncIOMotorClient(atlas_connection_string)
    atlas_db = atlas_client["veazy_db"]
    
    # Initialize Beanie with Atlas connection
    await init_beanie(database=atlas_db, document_models=[VisaTypeSelection, Country])
    
    # Load JSON data
    with open("./data_export/visa_type_selections.json", "r", encoding="utf-8") as f:
        visa_data = json.load(f)
    
    with open("./data_export/countries.json", "r", encoding="utf-8") as f:
        country_data = json.load(f)
    
    # Clear existing data (optional)
    print("🗑️ Clearing existing data in Atlas...")
    await VisaTypeSelection.delete_all()
    await Country.delete_all()
    
    # Import visa selections
    print("📥 Importing VisaTypeSelection data...")
    for item in visa_data:
        # Remove _id field to avoid conflicts
        if '_id' in item:
            del item['_id']
        visa_selection = VisaTypeSelection(**item)
        await visa_selection.save()
    
    # Import countries
    print("📥 Importing Country data...")
    for item in country_data:
        # Remove _id field to avoid conflicts
        if '_id' in item:
            del item['_id']
        country = Country(**item)
        await country.save()
    
    print(f"✅ Imported {len(visa_data)} visa selections and {len(country_data)} countries to Atlas")
    
    atlas_client.close()

async def main():
    print("🚀 MongoDB Data Migration Tool")
    print("=" * 50)
    
    # Step 1: Export from local
    try:
        await export_local_data()
    except Exception as e:
        print(f"❌ Error exporting local data: {e}")
        return
    
    # Step 2: Get Atlas connection string
    print("\n📋 Please provide your MongoDB Atlas connection string:")
    print("Example: mongodb+srv://username:password@cluster.mongodb.net/veazy_db?retryWrites=true&w=majority")
    atlas_url = input("Atlas Connection String: ").strip()
    
    if not atlas_url:
        print("❌ No connection string provided. Exiting...")
        return
    
    # Step 3: Import to Atlas
    try:
        await import_to_atlas(atlas_url)
        print("\n🎉 Migration completed successfully!")
        print("💡 Your data is now available in MongoDB Atlas")
    except Exception as e:
        print(f"❌ Error importing to Atlas: {e}")
        print("💡 Check your connection string and try again")

if __name__ == "__main__":
    asyncio.run(main())