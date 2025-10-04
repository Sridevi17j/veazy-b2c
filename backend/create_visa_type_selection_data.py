import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from database.models.visa_type_selection import (
    VisaTypeSelection, 
    VisaTypeRule, 
    SelectionCriteria, 
    MatchWeights
)

async def create_visa_type_selection_data():
    """Create sample visa type selection rules following Beanie documentation patterns"""
    print("Creating visa type selection data...")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        database = client["veazy_db"]
        
        # Initialize Beanie with visa type selection model
        await init_beanie(
            database=database, 
            document_models=[VisaTypeSelection]
        )
        
        print("Connected to MongoDB successfully")
        
        # Create Thailand visa type selection rules
        thailand_rules = [
            VisaTypeRule(
                visa_type="Tourist Visa",
                visa_code="TR",
                priority=1,
                criteria=SelectionCriteria(
                    purpose=["tourism", "leisure", "vacation", "sightseeing"],
                    max_days=60,
                    min_travellers=1,
                    max_travellers=10
                ),
                match_weights=MatchWeights(
                    purpose_exact=1.0,
                    purpose_partial=0.8,
                    traveller_count=0.9
                )
            ),
            VisaTypeRule(
                visa_type="Business Visa",
                visa_code="B",
                priority=2,
                criteria=SelectionCriteria(
                    purpose=["business", "work", "meeting", "conference"],
                    max_days=90,
                    min_travellers=1,
                    max_travellers=5
                ),
                match_weights=MatchWeights(
                    purpose_exact=1.0,
                    purpose_partial=0.7,
                    traveller_count=0.8
                )
            ),
            VisaTypeRule(
                visa_type="Transit Visa",
                visa_code="TS",
                priority=3,
                criteria=SelectionCriteria(
                    purpose=["transit", "stopover", "connection"],
                    max_days=30,
                    min_travellers=1,
                    max_travellers=15
                ),
                match_weights=MatchWeights(
                    purpose_exact=1.0,
                    purpose_partial=0.6,
                    traveller_count=0.5
                )
            )
        ]
        
        thailand_selection = VisaTypeSelection(
            country_code="THA",
            country_name="Thailand",
            rules=thailand_rules,
            default_suggestion="Tourist Visa",
            version="1.0"
        )
        
        await thailand_selection.save()
        print(f"Created Thailand visa type selection (ID: {thailand_selection.id})")
        
        # Create Vietnam visa type selection rules
        vietnam_rules = [
            VisaTypeRule(
                visa_type="Tourist Visa",
                visa_code="DL",
                priority=1,
                criteria=SelectionCriteria(
                    purpose=["tourism", "leisure", "vacation"],
                    max_days=30,
                    min_travellers=1,
                    max_travellers=8
                )
            ),
            VisaTypeRule(
                visa_type="Business Visa",
                visa_code="DN",
                priority=2,
                criteria=SelectionCriteria(
                    purpose=["business", "work", "investment"],
                    max_days=90,
                    min_travellers=1,
                    max_travellers=3
                )
            )
        ]
        
        vietnam_selection = VisaTypeSelection(
            country_code="VNM",
            country_name="Vietnam",
            rules=vietnam_rules,
            default_suggestion="Tourist Visa",
            version="1.0"
        )
        
        await vietnam_selection.save()
        print(f"Created Vietnam visa type selection (ID: {vietnam_selection.id})")
        
        # Count total visa type selections
        total_selections = await VisaTypeSelection.count()
        print(f"Total visa type selections in database: {total_selections}")
        
        print("Visa type selection data created successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_visa_type_selection_data())