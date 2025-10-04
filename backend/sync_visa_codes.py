import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from database.models.country import Country
from database.models.visa_type_selection import VisaTypeSelection

async def sync_visa_codes():
    """Synchronize visa codes between Country and VisaTypeSelection collections"""
    print("Synchronizing visa codes between collections...")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        database = client["veazy_db"]
        
        # Initialize Beanie
        await init_beanie(
            database=database, 
            document_models=[Country, VisaTypeSelection]
        )
        
        print("Connected to MongoDB successfully")
        
        # Get all countries and visa selections
        countries = await Country.find_all().to_list()
        visa_selections = await VisaTypeSelection.find_all().to_list()
        
        print("\n=== CURRENT MISMATCHES ===")
        
        for country in countries:
            # Find corresponding visa selection
            visa_selection = next((vs for vs in visa_selections if vs.country_code == country.code), None)
            
            if visa_selection:
                # Get visa codes from rules
                selection_codes = [rule.visa_code for rule in visa_selection.rules]
                country_codes = country.supported_visas
                
                print(f"\n{country.code} - {country.name}:")
                print(f"  Country codes: {country_codes}")
                print(f"  Selection codes: {selection_codes}")
                
                # Check for mismatches
                missing_in_selection = set(country_codes) - set(selection_codes)
                missing_in_country = set(selection_codes) - set(country_codes)
                
                if missing_in_selection:
                    print(f"  Missing in VisaTypeSelection: {list(missing_in_selection)}")
                if missing_in_country:
                    print(f"  Missing in Country: {list(missing_in_country)}")
                
                # Fix: Update country to match visa selection (visa selection is the source of truth)
                if missing_in_country or missing_in_selection:
                    print(f"  Updating {country.code} to match VisaTypeSelection...")
                    country.supported_visas = selection_codes
                    await country.save()
                    print(f"  Updated {country.code} supported_visas to: {selection_codes}")
            else:
                print(f"\n{country.code} - NO VISA SELECTION FOUND!")
        
        print(f"\n=== VERIFICATION ===")
        
        # Verify sync
        countries = await Country.find_all().to_list()
        visa_selections = await VisaTypeSelection.find_all().to_list()
        
        for country in countries:
            visa_selection = next((vs for vs in visa_selections if vs.country_code == country.code), None)
            if visa_selection:
                selection_codes = [rule.visa_code for rule in visa_selection.rules]
                country_codes = country.supported_visas
                
                if set(country_codes) == set(selection_codes):
                    print(f"{country.code}: SYNCED ✓")
                else:
                    print(f"{country.code}: STILL MISMATCHED ✗")
                    print(f"  Country: {country_codes}")
                    print(f"  Selection: {selection_codes}")
        
        print("\nVisa codes synchronization completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(sync_visa_codes())