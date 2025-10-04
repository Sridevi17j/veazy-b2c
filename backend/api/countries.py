from fastapi import APIRouter, HTTPException
from typing import List, Optional
import time
from database.models.country import Country
from database.models.visa_type_selection import VisaTypeSelection

router = APIRouter(prefix="/api/countries", tags=["countries"])

# Global cache variables
_countries_cache: Optional[List[dict]] = None
_cache_timestamp: Optional[float] = None
CACHE_TTL = 3600  # 1 hour in seconds

async def _fetch_countries_with_purposes() -> List[dict]:
    """
    Fetch countries with their supported purposes from database.
    This is the expensive operation we want to cache.
    """
    try:
        countries = await Country.find_all().to_list()
        result = []
        
        for country in countries:
            # Get visa type selection rules for this country
            visa_selection = await VisaTypeSelection.find_one({"country_code": country.code})
            
            # Extract unique purposes from all visa rules
            purposes = set()
            if visa_selection and visa_selection.rules:
                for rule in visa_selection.rules:
                    if rule.criteria and rule.criteria.purpose:
                        purposes.update(rule.criteria.purpose)
            
            # Only include countries that have supported visas
            if purposes:
                result.append({
                    "id": str(country.id),
                    "code": country.code,
                    "name": country.name,
                    "official_name": country.official_name,
                    "purposes": sorted(list(purposes))  # Sort for consistency
                })
        
        return result
        
    except Exception as e:
        print(f"Error fetching countries with purposes: {e}")
        # Return fallback data
        return [
            {
                "id": "1",
                "code": "VNM", 
                "name": "Vietnam",
                "official_name": "Socialist Republic of Vietnam",
                "purposes": ["tourism", "business", "social", "cultural"]
            },
            {
                "id": "2",
                "code": "THA",
                "name": "Thailand", 
                "official_name": "Kingdom of Thailand",
                "purposes": ["tourism", "business", "investment", "family visit"]
            },
            {
                "id": "3",
                "code": "IDN",
                "name": "Indonesia",
                "official_name": "Republic of Indonesia", 
                "purposes": ["tourism", "business", "social"]
            },
            {
                "id": "4",
                "code": "ARE",
                "name": "United Arab Emirates",
                "official_name": "United Arab Emirates",
                "purposes": ["tourism", "business", "investment", "medical"]
            }
        ]

def clear_countries_cache():
    """Clear the countries cache - useful when data is updated"""
    global _countries_cache, _cache_timestamp
    _countries_cache = None
    _cache_timestamp = None


@router.get("/", response_model=List[dict])
async def get_countries():
    """
    Get all countries with their basic information
    """
    try:
        countries = await Country.find_all().to_list()
        
        # Return only essential fields for dropdown
        return [
            {
                "id": str(country.id),
                "code": country.code,
                "name": country.name,
                "official_name": country.official_name
            }
            for country in countries
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching countries: {str(e)}")

@router.get("/supported", response_model=List[dict])  
async def get_supported_countries():
    """
    Get countries with their supported purposes (with caching)
    """
    global _countries_cache, _cache_timestamp
    
    try:
        # Check if cache is valid
        current_time = time.time()
        if (_countries_cache is not None and 
            _cache_timestamp is not None and 
            current_time - _cache_timestamp < CACHE_TTL):
            print("Serving countries from cache")
            return _countries_cache
        
        print("Cache miss - fetching countries from database")
        
        # Cache miss - fetch from database
        countries = await _fetch_countries_with_purposes()
        
        # Update cache
        _countries_cache = countries
        _cache_timestamp = current_time
        
        print(f"Cached {len(countries)} countries with purposes")
        return countries
        
    except Exception as e:
        print(f"Error in get_supported_countries: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching supported countries: {str(e)}")

@router.get("/{country_code}/purposes/{purpose}/visa-details")
async def get_visa_details_by_purpose(country_code: str, purpose: str):
    """
    Get detailed visa information based on country and purpose selection
    """
    try:
        # Find visa selection for the country
        visa_selection = await VisaTypeSelection.find_one({"country_code": country_code.upper()})
        
        if not visa_selection:
            raise HTTPException(status_code=404, detail=f"Country {country_code} not found")
        
        # Find the best matching visa rule based on purpose
        best_match = None
        highest_score = 0
        
        for rule in visa_selection.rules:
            if rule.criteria and rule.criteria.purpose:
                # Calculate match score
                score = 0
                purpose_lower = purpose.lower()
                
                for rule_purpose in rule.criteria.purpose:
                    if purpose_lower == rule_purpose.lower():
                        score += 10  # Exact match
                    elif purpose_lower in rule_purpose.lower() or rule_purpose.lower() in purpose_lower:
                        score += 5   # Partial match
                
                # Consider priority (lower number = higher priority)
                if rule.priority:
                    score += (10 - rule.priority)
                
                if score > highest_score:
                    highest_score = score
                    best_match = rule
        
        if not best_match:
            raise HTTPException(status_code=404, detail=f"No visa found for purpose: {purpose}")
        
        # Return complete visa information
        result = {
            "country_name": visa_selection.country_name,
            "country_code": visa_selection.country_code,
            "matched_purpose": purpose,
            "visa_type": best_match.visa_type,
            "visa_code": best_match.visa_code,
            "priority": best_match.priority,
            "criteria": {
                "purpose": best_match.criteria.purpose,
                "max_days": best_match.criteria.max_days,
                "min_travellers": best_match.criteria.min_travellers,
                "max_travellers": best_match.criteria.max_travellers
            }
        }
        
        # Add enhanced information if available
        if best_match.visa_details:
            result["visa_details"] = {
                "stay_duration": best_match.visa_details.stay_duration,
                "validity_period": best_match.visa_details.validity_period,
                "entry_type": best_match.visa_details.entry_type,
                "processing_time": best_match.visa_details.processing_time,
                "fee_range": best_match.visa_details.fee_range,
                "description": best_match.visa_details.description
            }
        
        if best_match.document_requirements:
            result["document_requirements"] = [
                {
                    "name": doc.name,
                    "description": doc.description,
                    "required": doc.required,
                    "category": doc.category,
                    "notes": doc.notes
                }
                for doc in best_match.document_requirements
            ]
        
        if best_match.approval_process:
            result["approval_process"] = [
                {
                    "step_number": step.step_number,
                    "title": step.title,
                    "description": step.description,
                    "estimated_time": step.estimated_time
                }
                for step in best_match.approval_process
            ]
        
        return result
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_visa_details_by_purpose: {e}")
        raise HTTPException(status_code=500, detail=f"Error fetching visa details: {str(e)}")