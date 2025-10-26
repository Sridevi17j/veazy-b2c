# LLM-driven workflow executor using complete JSON context
# Purpose: Let LLM intelligently handle workflow using complete JSON blueprint

import sys
sys.path.append('../..')

import json
from typing import Any, Dict, Optional
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from config.settings import invoke_llm_safe


@tool
async def workflow_executor_tool(user_message: str, current_stage: str = "start") -> str:
    """
    Execute visa workflow using LLM intelligence with complete JSON context.
    
    Use this tool when:
    - After recommending visa_type to user and the user says yes to proceed for visa application
    - User confirms after visa recommendation ("yes", "proceed", "start")
    - User is in workflow execution phase
    
    Args:
        user_message: User's message/response
    
    Returns:
        String response guiding user through workflow stages
    """
    
    try:
        # Step 1: Detect visa type from conversation context
        visa_type = await _detect_visa_type(user_message)
        
        # Step 2: Get complete workflow JSON for this visa type
        workflow_json = await _get_workflow_json(visa_type)
        
        if not workflow_json:
            return "I need to know which visa type you'd like to proceed with. Could you specify the visa type (e.g., Vietnam Tourism Single Entry)?"
        
        # Step 3: Execute workflow by reading JSON structure exactly
        workflow_prompt = f"""You are executing a visa application workflow. You MUST read and follow the JSON structure exactly.

WORKFLOW JSON:
{json.dumps(workflow_json, indent=2)}

USER MESSAGE: "{user_message}"

HOW TO READ THIS JSON:
1. "collection_sequence" has 7 stages in order
2. Each stage has either:
   - "required_documents" array = ASK USER TO UPLOAD THESE DOCUMENTS
   - "fields" object = CHECK EACH FIELD'S "extraction_method"

EXTRACTION METHOD RULES:
- "user_input" = ASK USER TO TYPE THIS INFORMATION
- "ai_derive_from_name" = DON'T ASK, EXTRACTED AUTOMATICALLY  
- "user_account" = DON'T ASK, TAKEN FROM ACCOUNT
- "passport_bio_page" = DON'T ASK, EXTRACTED FROM PASSPORT
- "visa_type_selected" = DON'T ASK, ALREADY KNOWN
- "flight_tickets_or_user_input" = ASK USER (no tickets uploaded yet)
- "hotel_reservation_or_user_input" = ASK USER (no reservation uploaded yet)

YOUR TASK:
1. Start with FIRST stage: "documents" 
2. This stage has "required_documents" = Ask to upload passport_bio_page and passport_photo
3. Explain what gets extracted from passport_bio_page
4. DO NOT ask for name, date of birth, etc. - these come from the passport automatically

EXACT RESPONSE NEEDED:
Perfect! Let's start your Vietnam Tourism Single Entry visa application.

**STAGE 1: Document Collection**

Please upload these 2 documents:

1. **Passport Bio Page** - Clear scan/photo of your passport bio page
   - This will automatically extract: surname, given name, date of birth, gender, nationality, place of birth, passport number, passport type, issuing country, issue date, expiry date

2. **Passport Size Photo** - Recent passport-sized photograph with white background

Please upload your passport bio page first so I can extract your personal details automatically."""

        response = invoke_llm_safe([HumanMessage(content=workflow_prompt)])
        return response.content.strip()
        
    except Exception as e:
        return "I'm having difficulty processing your visa application request. Could you please let me know which visa type you'd like to apply for and what you'd like to do next?"


async def _detect_visa_type(user_message: str) -> str:
    """Detect visa type from conversation context using LLM"""
    try:
        detection_prompt = f"""Analyze this message to detect the visa type being discussed: "{user_message}"

Look for context clues about:
- Country: Vietnam, Thailand, etc.
- Purpose: Tourism, Business, Work, etc. 
- Entry type: Single Entry, Multiple Entry

Common visa types:
- Vietnam Tourism Single Entry
- Vietnam Tourism Multiple Entry  
- Vietnam Business Single Entry
- Vietnam Business Multiple Entry

Return only the exact visa type name, or "Vietnam Tourism Single Entry" as default if unclear."""

        response = invoke_llm_safe([HumanMessage(content=detection_prompt)])
        return response.content.strip()
        
    except Exception as e:
        return "Vietnam Tourism Single Entry"  # Default fallback


async def _get_workflow_json(visa_type: str) -> Optional[dict]:
    """Get workflow JSON based on visa type"""
    try:
        # Map visa type to workflow file
        workflow_mapping = {
            "Vietnam Tourism Single Entry": "VNM_tourism_single_entry_workflow.json",
            "Vietnam Tourism Multiple Entry": "VNM_tourism_multiple_entry_workflow.json", 
            "Vietnam Business Single Entry": "VNM_business_single_entry_workflow.json",
            "Vietnam Business Multiple Entry": "VNM_business_multiple_entry_workflow.json"
        }
        
        # Get exact match or find closest match
        workflow_file = workflow_mapping.get(visa_type)
        
        if not workflow_file:
            # Fallback matching for partial matches
            visa_lower = visa_type.lower()
            if "vietnam" in visa_lower:
                if "business" in visa_lower:
                    if "multiple" in visa_lower:
                        workflow_file = "VNM_business_multiple_entry_workflow.json"
                    else:
                        workflow_file = "VNM_business_single_entry_workflow.json"
                else:  # tourism default
                    if "multiple" in visa_lower:
                        workflow_file = "VNM_tourism_multiple_entry_workflow.json"
                    else:
                        workflow_file = "VNM_tourism_single_entry_workflow.json"
            else:
                # Ultimate fallback
                workflow_file = "VNM_tourism_single_entry_workflow.json"
        
        # Load workflow JSON
        workflow_path = f"/mnt/c/Users/dev/github/veazy_b2c/backend/{workflow_file}"
        with open(workflow_path, 'r') as f:
            return json.load(f)
    
    except Exception as e:
        print(f"Error loading workflow JSON: {e}")
        return None


# Export the tool for agent use
__all__ = ["workflow_executor_tool"]