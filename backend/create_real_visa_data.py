import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from database.models.visa_type_selection import (
    VisaTypeSelection, 
    VisaTypeRule, 
    SelectionCriteria, 
    MatchWeights
)
from database.models.country import Country

async def create_real_visa_data():
    """Create real visa type data for Vietnam, Indonesia, and UAE based on 2025 research"""
    print("Creating real visa type selection data for Vietnam, Indonesia, and UAE...")
    
    try:
        # Connect to MongoDB
        client = AsyncIOMotorClient("mongodb://localhost:27017")
        database = client["veazy_db"]
        
        # Initialize Beanie
        await init_beanie(
            database=database, 
            document_models=[VisaTypeSelection, Country]
        )
        
        print("Connected to MongoDB successfully")
        
        # === VIETNAM VISA TYPES (2025) ===
        vietnam_rules = [
            VisaTypeRule(
                visa_type="Tourist Visa",
                visa_code="DL",
                priority=1,
                criteria=SelectionCriteria(
                    purpose=["tourism", "leisure", "vacation", "sightseeing", "holiday"],
                    max_days=30,
                    min_travellers=1,
                    max_travellers=10
                ),
                match_weights=MatchWeights(purpose_exact=1.0, purpose_partial=0.8, traveller_count=0.9)
            ),
            VisaTypeRule(
                visa_type="Business Visa DN1",
                visa_code="DN1", 
                priority=2,
                criteria=SelectionCriteria(
                    purpose=["business", "work", "meeting", "conference", "trade"],
                    max_days=365,
                    min_travellers=1,
                    max_travellers=5
                ),
                match_weights=MatchWeights(purpose_exact=1.0, purpose_partial=0.7, traveller_count=0.8)
            ),
            VisaTypeRule(
                visa_type="Business Visa DN2",
                visa_code="DN2",
                priority=3, 
                criteria=SelectionCriteria(
                    purpose=["services", "commercial", "investment", "establishment"],
                    max_days=365,
                    min_travellers=1,
                    max_travellers=3
                ),
                match_weights=MatchWeights(purpose_exact=1.0, purpose_partial=0.7, traveller_count=0.8)
            ),
            VisaTypeRule(
                visa_type="Investment Visa DT1",
                visa_code="DT1",
                priority=4,
                criteria=SelectionCriteria(
                    purpose=["investment", "investor", "capital", "major investment"],
                    max_days=1825,  # 5 years
                    min_travellers=1,
                    max_travellers=2
                ),
                match_weights=MatchWeights(purpose_exact=1.0, purpose_partial=0.6, traveller_count=0.7)
            ),
            VisaTypeRule(
                visa_type="Investment Visa DT2",
                visa_code="DT2", 
                priority=5,
                criteria=SelectionCriteria(
                    purpose=["investment", "investor", "medium investment"],
                    max_days=1825,  # 5 years
                    min_travellers=1,
                    max_travellers=2
                )
            ),
            VisaTypeRule(
                visa_type="E-Visa Tourist",
                visa_code="E-DL",
                priority=6,
                criteria=SelectionCriteria(
                    purpose=["tourism", "short visit", "quick trip"],
                    max_days=90,
                    min_travellers=1,
                    max_travellers=8
                )
            )
        ]
        
        vietnam_selection = VisaTypeSelection(
            country_code="VNM",
            country_name="Vietnam",
            rules=vietnam_rules,
            default_suggestion="Tourist Visa",
            version="2025.1"
        )
        
        await vietnam_selection.save()
        print(f"Created Vietnam visa types (ID: {vietnam_selection.id})")
        
        # === INDONESIA VISA TYPES (2025) ===
        indonesia_rules = [
            VisaTypeRule(
                visa_type="Visa-Free Entry",
                visa_code="VF",
                priority=1,
                criteria=SelectionCriteria(
                    purpose=["tourism", "family visit", "short business", "transit"],
                    max_days=30,
                    min_travellers=1,
                    max_travellers=15
                ),
                match_weights=MatchWeights(purpose_exact=1.0, purpose_partial=0.9, traveller_count=0.9)
            ),
            VisaTypeRule(
                visa_type="Visa on Arrival (VOA)",
                visa_code="B211A",
                priority=2,
                criteria=SelectionCriteria(
                    purpose=["tourism", "business meeting", "government visit", "goods purchasing"],
                    max_days=30,
                    min_travellers=1,
                    max_travellers=10
                ),
                match_weights=MatchWeights(purpose_exact=1.0, purpose_partial=0.8, traveller_count=0.9)
            ),
            VisaTypeRule(
                visa_type="Social Cultural Visa",
                visa_code="C6",
                priority=3,
                criteria=SelectionCriteria(
                    purpose=["social", "cultural", "family visit", "education", "training"],
                    max_days=60,
                    min_travellers=1,
                    max_travellers=5
                ),
                match_weights=MatchWeights(purpose_exact=1.0, purpose_partial=0.7, traveller_count=0.8)
            ),
            VisaTypeRule(
                visa_type="Business Visa",
                visa_code="C7",
                priority=4,
                criteria=SelectionCriteria(
                    purpose=["business", "conference", "meeting", "trade", "negotiation"],
                    max_days=60,
                    min_travellers=1,
                    max_travellers=5
                ),
                match_weights=MatchWeights(purpose_exact=1.0, purpose_partial=0.7, traveller_count=0.8)
            ),
            VisaTypeRule(
                visa_type="Multiple Entry Visitor",
                visa_code="C8",
                priority=5,
                criteria=SelectionCriteria(
                    purpose=["frequent visits", "multiple trips", "long-term business"],
                    max_days=180,
                    min_travellers=1,
                    max_travellers=3
                )
            )
        ]
        
        indonesia_selection = VisaTypeSelection(
            country_code="IDN",
            country_name="Indonesia",
            rules=indonesia_rules,
            default_suggestion="Visa on Arrival (VOA)",
            version="2025.1"
        )
        
        await indonesia_selection.save()
        print(f"Created Indonesia visa types (ID: {indonesia_selection.id})")
        
        # === UAE VISA TYPES (2025) ===
        uae_rules = [
            VisaTypeRule(
                visa_type="Tourist Visa 30 Days",
                visa_code="TV30",
                priority=1,
                criteria=SelectionCriteria(
                    purpose=["tourism", "leisure", "vacation", "sightseeing", "short visit"],
                    max_days=30,
                    min_travellers=1,
                    max_travellers=10
                ),
                match_weights=MatchWeights(purpose_exact=1.0, purpose_partial=0.9, traveller_count=0.9)
            ),
            VisaTypeRule(
                visa_type="Tourist Visa 90 Days",
                visa_code="TV90",
                priority=2,
                criteria=SelectionCriteria(
                    purpose=["extended tourism", "long vacation", "extended stay"],
                    max_days=90,
                    min_travellers=1,
                    max_travellers=8
                )
            ),
            VisaTypeRule(
                visa_type="Visit Visa",
                visa_code="VV",
                priority=3,
                criteria=SelectionCriteria(
                    purpose=["family visit", "friend visit", "personal visit"],
                    max_days=60,
                    min_travellers=1,
                    max_travellers=6
                )
            ),
            VisaTypeRule(
                visa_type="Business Visa",
                visa_code="BV",
                priority=4,
                criteria=SelectionCriteria(
                    purpose=["business", "meeting", "conference", "trade", "commercial"],
                    max_days=90,
                    min_travellers=1,
                    max_travellers=5
                ),
                match_weights=MatchWeights(purpose_exact=1.0, purpose_partial=0.8, traveller_count=0.8)
            ),
            VisaTypeRule(
                visa_type="Golden Visa (Investment)",
                visa_code="GV10",
                priority=5,
                criteria=SelectionCriteria(
                    purpose=["investment", "real estate", "major investor", "long-term residence"],
                    max_days=3650,  # 10 years
                    min_travellers=1,
                    max_travellers=2
                ),
                match_weights=MatchWeights(purpose_exact=1.0, purpose_partial=0.6, traveller_count=0.7)
            ),
            VisaTypeRule(
                visa_type="Golden Visa (Entrepreneur)",
                visa_code="GV5",
                priority=6,
                criteria=SelectionCriteria(
                    purpose=["entrepreneur", "startup", "business establishment"],
                    max_days=1825,  # 5 years
                    min_travellers=1,
                    max_travellers=2
                )
            ),
            VisaTypeRule(
                visa_type="Green Visa",
                visa_code="GRV",
                priority=7,
                criteria=SelectionCriteria(
                    purpose=["skilled professional", "freelancer", "self-sponsored"],
                    max_days=1825,  # 5 years
                    min_travellers=1,
                    max_travellers=1
                )
            )
        ]
        
        uae_selection = VisaTypeSelection(
            country_code="ARE",
            country_name="United Arab Emirates",
            rules=uae_rules,
            default_suggestion="Tourist Visa 30 Days",
            version="2025.1"
        )
        
        await uae_selection.save()
        print(f"Created UAE visa types (ID: {uae_selection.id})")
        
        # Create/Update country records
        countries_data = [
            {
                "code": "VNM",
                "name": "Vietnam", 
                "official_name": "Socialist Republic of Vietnam",
                "currency": "VND",
                "supported_visas": ["DL", "DN1", "DN2", "DT1", "DT2", "E-DL"]
            },
            {
                "code": "IDN", 
                "name": "Indonesia",
                "official_name": "Republic of Indonesia", 
                "currency": "IDR",
                "supported_visas": ["VF", "B211A", "C6", "C7", "C8"]
            },
            {
                "code": "ARE",
                "name": "United Arab Emirates",
                "official_name": "United Arab Emirates",
                "currency": "AED", 
                "supported_visas": ["TV30", "TV90", "VV", "BV", "GV10", "GV5", "GRV"]
            }
        ]
        
        for country_data in countries_data:
            # Check if country exists, update or create
            existing_country = await Country.find_one({"code": country_data["code"]})
            if existing_country:
                existing_country.supported_visas = country_data["supported_visas"]
                await existing_country.save()
                print(f"Updated {country_data['name']} country record")
            else:
                country = Country(**country_data)
                await country.save()
                print(f"Created {country_data['name']} country record")
        
        # Count totals
        total_selections = await VisaTypeSelection.count()
        total_countries = await Country.count()
        
        print(f"Total visa type selections: {total_selections}")
        print(f"Total countries: {total_countries}")
        print("Real visa type data created successfully!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(create_real_visa_data())