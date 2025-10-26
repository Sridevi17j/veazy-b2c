# Database visa lookup tool
# Purpose: Fetch visa document from database and let LLM analyze and recommend

import sys
sys.path.append('../..')

from typing import Any, Dict, Optional
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from config.settings import invoke_llm_safe
from database.models.visa_type_selection import VisaTypeSelection


@tool
async def database_visa_lookup_tool(country_code: str, user_details: str) -> str:
    """
    Fetch visa options from database and recommend best type using LLM.
    
    Use this tool when:
    - Basic information is complete and country_code is available
    - Need to suggest visa type from database options  
    - User needs recommendation based on their travel purpose
    - IMPORTANT: Do NOT use if user has already received a recommendation and said "yes"
    
    Args:
        country_code: ISO country code (e.g., "VNM" for Vietnam)
        user_details: User's travel details and purpose
    
    Returns:
        String response with visa recommendation
    """
    
    try:
        # Fetch visa document from database
        visa_document = await VisaTypeSelection.find_one({"country_code": country_code})
        
        if not visa_document:
            return f"I don't have visa information available for this destination yet. Please contact our support team for assistance."
        
        # Let LLM analyze user details and document to recommend visa type
        recommendation = _get_llm_recommendation(user_details, visa_document.dict())
        
        return recommendation
        
    except Exception as e:
        return "I'm having difficulty accessing visa information right now. Let me connect you with our support team for assistance."


def _get_llm_recommendation(user_details: str, visa_document: dict) -> str:
    """Let LLM analyze user details and visa document to recommend best visa type"""
    try:
        recommendation_prompt = f"""You are a professional visa consultant. Analyze the user's travel details and the visa document to recommend the best visa type.

USER TRAVEL DETAILS:
{user_details}

VISA DOCUMENT FROM DATABASE:
{visa_document}

TASK:
1. Analyze the user's travel needs
2. Match them with the best visa type from the document
3. Recommend the specific visa type
4. Ask if we can proceed with the application

RESPONSE FORMAT:
Based on your [purpose] trip to [country], I recommend the **[EXACT VISA TYPE NAME]**.

[Brief explanation why this visa type suits their needs]

Can we proceed with applying for the [EXACT VISA TYPE NAME] for [number] traveler(s)?

Keep the response conversational and end with asking if we can proceed with the visa application."""

        response = invoke_llm_safe([HumanMessage(content=recommendation_prompt)])
        return response.content.strip()
        
    except Exception as e:
        return "I'm having trouble analyzing the visa options right now. Let me connect you with our support team for assistance."


# Export the tool for agent use
__all__ = ["database_visa_lookup_tool"]