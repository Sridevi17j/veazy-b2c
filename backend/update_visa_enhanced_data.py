import asyncio
import os
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from database.models.visa_type_selection import VisaTypeSelection, VisaDetails, DocumentRequirement, ProcessStep

async def update_visa_enhanced_data():
    """Update existing visa type selection data with enhanced information"""
    
    # Connect to MongoDB
    mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    database_name = os.getenv("DATABASE_NAME", "veazy_db")
    
    client = AsyncIOMotorClient(mongodb_url)
    db = client[database_name]
    
    # Initialize Beanie
    await init_beanie(database=db, document_models=[VisaTypeSelection])
    
    print("🔄 Starting enhanced data update...")
    
    # Get all existing visa type selections
    selections = await VisaTypeSelection.find_all().to_list()
    
    for selection in selections:
        print(f"\n📍 Updating {selection.country_name} ({selection.country_code})")
        
        # Update each rule with enhanced data
        for rule in selection.rules:
            print(f"  - Updating {rule.visa_type} ({rule.visa_code})")
            
            # Add visa details based on visa type
            if "tourist" in rule.visa_type.lower() or "leisure" in str(rule.criteria.purpose).lower():
                rule.visa_details = VisaDetails(
                    stay_duration=f"Up to {rule.criteria.max_days} days",
                    validity_period=f"{rule.criteria.max_days} days",
                    entry_type="Single Entry Only" if rule.criteria.max_days <= 90 else "Multiple Entry",
                    processing_time="3-5 business days",
                    fee_range="$25-75",
                    description=f"Perfect for {', '.join(rule.criteria.purpose[:3])} purposes"
                )
                
                rule.document_requirements = [
                    DocumentRequirement(
                        name="Passport",
                        description="A valid passport with minimum of 6 months validity from the date of return. Ensure at least 2 blank pages for visa stamping.",
                        required=True,
                        category="identity"
                    ),
                    DocumentRequirement(
                        name="Flight Tickets",
                        description="Round-trip flight tickets showing entry and exit from the country. Dummy tickets are accepted in some cases.",
                        required=True,
                        category="travel"
                    ),
                    DocumentRequirement(
                        name="Hotel Booking",
                        description="Confirmed hotel reservations or accommodation proof for the duration of stay.",
                        required=True,
                        category="accommodation"
                    ),
                    DocumentRequirement(
                        name="Passport Photos",
                        description="2 recent passport-sized photographs with white background.",
                        required=True,
                        category="identity"
                    )
                ]
                
            elif "business" in rule.visa_type.lower():
                rule.visa_details = VisaDetails(
                    stay_duration=f"Up to {rule.criteria.max_days} days",
                    validity_period=f"{rule.criteria.max_days} days",
                    entry_type="Multiple Entry" if rule.criteria.max_days > 90 else "Single Entry",
                    processing_time="5-7 business days",
                    fee_range="$50-150",
                    description=f"Ideal for {', '.join(rule.criteria.purpose[:3])} activities"
                )
                
                rule.document_requirements = [
                    DocumentRequirement(
                        name="Passport",
                        description="A valid passport with minimum of 6 months validity from the date of return. Ensure at least 2 blank pages for visa stamping.",
                        required=True,
                        category="identity"
                    ),
                    DocumentRequirement(
                        name="Business Invitation Letter",
                        description="Official invitation letter from the host company detailing purpose, duration and financial responsibility.",
                        required=True,
                        category="business"
                    ),
                    DocumentRequirement(
                        name="Company Registration",
                        description="Certificate of incorporation or business registration of your company.",
                        required=True,
                        category="business"
                    ),
                    DocumentRequirement(
                        name="Flight Tickets",
                        description="Round-trip flight tickets showing entry and exit from the country.",
                        required=True,
                        category="travel"
                    ),
                    DocumentRequirement(
                        name="Bank Statements",
                        description="Last 3 months bank statements showing sufficient funds.",
                        required=True,
                        category="financial"
                    )
                ]
                
            elif "investment" in rule.visa_type.lower() or "golden" in rule.visa_type.lower():
                rule.visa_details = VisaDetails(
                    stay_duration=f"Up to {rule.criteria.max_days} days",
                    validity_period=f"{rule.criteria.max_days} days",
                    entry_type="Multiple Entry",
                    processing_time="15-30 business days",
                    fee_range="$500-2000",
                    description=f"Long-term visa for {', '.join(rule.criteria.purpose[:2])} purposes"
                )
                
                rule.document_requirements = [
                    DocumentRequirement(
                        name="Passport",
                        description="A valid passport with minimum of 6 months validity from the date of return.",
                        required=True,
                        category="identity"
                    ),
                    DocumentRequirement(
                        name="Investment Proof",
                        description="Documentation proving investment amount and legitimacy of funds.",
                        required=True,
                        category="financial"
                    ),
                    DocumentRequirement(
                        name="Financial Statements",
                        description="Comprehensive financial statements and bank certificates.",
                        required=True,
                        category="financial"
                    ),
                    DocumentRequirement(
                        name="Background Check",
                        description="Police clearance certificate from country of residence.",
                        required=True,
                        category="verification"
                    )
                ]
                
            else:
                # Default for other visa types
                rule.visa_details = VisaDetails(
                    stay_duration=f"Up to {rule.criteria.max_days} days",
                    validity_period=f"{rule.criteria.max_days} days",
                    entry_type="Single Entry",
                    processing_time="5-7 business days",
                    fee_range="$30-100",
                    description=f"Suitable for {', '.join(rule.criteria.purpose[:2])} purposes"
                )
                
                rule.document_requirements = [
                    DocumentRequirement(
                        name="Passport",
                        description="A valid passport with minimum of 6 months validity from the date of return.",
                        required=True,
                        category="identity"
                    ),
                    DocumentRequirement(
                        name="Application Form",
                        description="Completed visa application form with all required information.",
                        required=True,
                        category="application"
                    ),
                    DocumentRequirement(
                        name="Supporting Documents",
                        description="Additional documents based on purpose of visit.",
                        required=True,
                        category="supporting"
                    )
                ]
            
            # Add approval process (same for all visa types with variations)
            processing_days = 3 if "tourist" in rule.visa_type.lower() else 5 if "business" in rule.visa_type.lower() else 10
            
            rule.approval_process = [
                ProcessStep(
                    step_number=1,
                    title="Application Processing",
                    description="Application review and document verification",
                    estimated_time=f"{processing_days-2}-{processing_days} days"
                ),
                ProcessStep(
                    step_number=2,
                    title="Approval Letter Issued",
                    description="Visa approval notification sent via email",
                    estimated_time="1 day"
                ),
                ProcessStep(
                    step_number=3,
                    title="Visa Stamping & Entry",
                    description="Visa stamping at embassy or on arrival",
                    estimated_time="Same day"
                )
            ]
        
        # Save updated document
        await selection.save()
        print(f"  ✅ Updated {selection.country_name} with enhanced data")
    
    print(f"\n🎉 Successfully updated {len(selections)} visa type selections with enhanced data!")
    client.close()

if __name__ == "__main__":
    asyncio.run(update_visa_enhanced_data())