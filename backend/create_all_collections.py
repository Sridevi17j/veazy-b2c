import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from database.models.user import User, UserProfile
from database.models.visa_application import VisaApplication
from database.models.document import DocumentModel
from database.models.country import Country

async def create_all_collections():
    print("Creating all MongoDB collections...")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        database = client["veazy_db"]
        
        # Initialize Beanie with all models
        await init_beanie(
            database=database, 
            document_models=[User, VisaApplication, DocumentModel, Country]
        )
        
        print("Connected to MongoDB successfully")
        
        # Create sample countries
        countries_data = [
            {"code": "THA", "name": "Thailand", "official_name": "Kingdom of Thailand", "currency": "THB", "supported_visas": ["tourist", "business", "transit"]},
            {"code": "VNM", "name": "Vietnam", "official_name": "Socialist Republic of Vietnam", "currency": "VND", "supported_visas": ["tourist", "business"]},
            {"code": "SGP", "name": "Singapore", "official_name": "Republic of Singapore", "currency": "SGD", "supported_visas": ["tourist", "business", "transit"]}
        ]
        
        for country_data in countries_data:
            country = Country(**country_data)
            await country.save()
            print(f"Created country: {country.name}")
        
        # Get a user to link visa application
        user = await User.find_one()
        if user:
            # Create sample visa application
            visa_app = VisaApplication(
                user_id=str(user.id),
                reference_number="VA001"
            )
            await visa_app.save()
            print(f"Created visa application: {visa_app.reference_number}")
        
        print("All collections created successfully!")
        
        # List all collections
        collections = await database.list_collection_names()
        print(f"Available collections: {collections}")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_all_collections())