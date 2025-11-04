# Start Workflow Tool - For existing agent to call workflow agent
# Purpose: Simple tool for existing agent to start workflow agent after visa type confirmation

import sys
sys.path.append('../..')

from typing import Annotated
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

@tool
async def start_detailed_application_process(
    confirmed_visa_type: Annotated[str, "Visa type confirmed by user"],
    country: Annotated[str, "Country for visa application"],
    purpose: Annotated[str, "Purpose of travel"],
    travel_dates: Annotated[dict, "Travel dates from user"] = None,
    state: Annotated[dict, InjectedState] = None
) -> str:
    """Start detailed workflow process after user confirms suggested visa type"""

    print("=" * 80)
    print("🔧 START_DETAILED_APPLICATION_PROCESS CALLED!")
    print(f"📝 Confirmed visa type: {confirmed_visa_type}")
    print(f"📝 Country: {country}")
    print(f"📝 Purpose: {purpose}")
    print(f"📝 Travel dates: {travel_dates}")
    print("=" * 80)

    try:
        print(f"DEBUG: start_detailed_application_process called!")
        print(f"DEBUG: confirmed_visa_type={confirmed_visa_type}")
        print(f"DEBUG: country={country}")
        print(f"DEBUG: purpose={purpose}")
        print(f"DEBUG: travel_dates={travel_dates}")
        print(f"DEBUG: state={state}")
        
        # Import workflow agent functions
        print(f"DEBUG: Importing workflow agent functions...")
        from agent.agents.intelligent_workflow_agent import (
            workflow_sessions, 
            initialize_workflow_session, 
            load_workflow_dynamically,
            execute_current_stage
        )
        print(f"DEBUG: Import successful!")
        
        # Generate simple session ID from state or create one
        session_id = state.get("session_id", "default_session") if state else "default_session"
        print(f"DEBUG: session_id={session_id}")
        
        # Prepare handoff data
        handoff_data = {
            "visa_type": confirmed_visa_type,
            "country": country,
            "purpose": purpose,
            "travel_dates": travel_dates or {}
        }
        print(f"DEBUG: handoff_data={handoff_data}")
        
        # Initialize workflow session
        print(f"DEBUG: Initializing workflow session...")
        init_result = await initialize_workflow_session.ainvoke({"thread_id": session_id, "handoff_data": handoff_data, "state": state})
        print(f"DEBUG: Initialize result: {init_result}")
        
        # Load workflow for confirmed visa type
        print(f"DEBUG: Loading workflow for {confirmed_visa_type}...")
        workflow_analysis = await load_workflow_dynamically.ainvoke({"thread_id": session_id, "visa_type": confirmed_visa_type, "state": state})
        print(f"DEBUG: Workflow analysis: {workflow_analysis}")
        
        # Get first stage requirements
        print(f"DEBUG: Getting stage requirements...")
        stage_requirements = await execute_current_stage.ainvoke({"thread_id": session_id, "state": state})
        print(f"DEBUG: Stage requirements: {stage_requirements}")
        
        print(f"DEBUG: Workflow agent successfully executed!")
        
        return f"""Perfect! Let's start your detailed {confirmed_visa_type} application process.

{workflow_analysis}

---

{stage_requirements}

I'll guide you through each step systematically. When you're ready to upload documents or provide information, just let me know!"""
        
    except Exception as e:
        print(f"DEBUG: Exception in start_detailed_application_process: {e}")
        print(f"DEBUG: Exception type: {type(e)}")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        # Fallback response if workflow agent not available
        return f"""Great! Your {confirmed_visa_type} application is confirmed.

**Your Details:**
- Country: {country}
- Purpose: {purpose}
- Visa Type: {confirmed_visa_type}

I'll now guide you through the detailed application process step by step. We'll need:

1. **Documents Required:**
   - Passport bio page (clear scan, 6+ months validity)
   - Recent passport photo (white background, formal)
   - Flight tickets (optional - for automatic date extraction)

2. **Information Needed:**
   - Contact details (email, phone)
   - Travel information (dates, accommodation in {country})
   - Personal details (address, occupation)
   - Financial information
   - Emergency contact

Let's start with the first requirement: Please upload your passport bio page."""