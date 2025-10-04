import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from database.models.country import Country

async def update_countries():
    """Update countries to have exactly 4: Thailand, Vietnam, UAE, Indonesia"""
    print("Updating countries to have exactly Thailand, Vietnam, UAE, Indonesia...")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        database = client["veazy_db"]
        
        # Initialize Beanie
        await init_beanie(database=database, document_models=[Country])
        
        print("Connected to MongoDB successfully")
        
        # Delete all existing countries
        await Country.delete_all()
        print("Deleted all existing countries")
        
        # Create the 4 required countries
        countries_data = [
            {
                "code": "THA",
                "name": "Thailand", 
                "official_name": "Kingdom of Thailand",
                "currency": "THB",
                "supported_visas": ["TR", "B", "TS", "NON-B", "NON-O"]
            },
            {
                "code": "VNM",
                "name": "Vietnam", 
                "official_name": "Socialist Republic of Vietnam",
                "currency": "VND",
                "supported_visas": ["DL", "DN1", "DN2", "DT1", "DT2", "E-DL"]
            },
            {
                "code": "ARE",
                "name": "United Arab Emirates",
                "official_name": "United Arab Emirates",
                "currency": "AED", 
                "supported_visas": ["TV30", "TV90", "VV", "BV", "GV10", "GV5", "GRV"]
            },
            {
                "code": "IDN", 
                "name": "Indonesia",
                "official_name": "Republic of Indonesia", 
                "currency": "IDR",
                "supported_visas": ["VF", "B211A", "C6", "C7", "C8"]
            }
        ]
        
        # Create countries
        for country_data in countries_data:
            country = Country(**country_data)
            await country.save()
            print(f"Created: {country.code} - {country.name}")
        
        # Verify final count
        total_countries = await Country.count()
        print(f"\nFinal count: {total_countries} countries")
        
        # List all countries
        print("\n=== FINAL COUNTRIES LIST ===")
        all_countries = await Country.find_all().to_list()
        for country in all_countries:
            print(f"{country.code} - {country.name} ({country.official_name})")
            print(f"  Currency: {country.currency}")
            print(f"  Supported visas: {country.supported_visas}")
            print()
        
        print("Countries updated successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(update_countries())