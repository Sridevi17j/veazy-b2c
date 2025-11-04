# Intelligent Workflow Agent - Dynamic workflow executor and JS file generator
# Purpose: Generic agent that can execute any workflow.json and prepare automation files

import sys
sys.path.append('../..')

import json
import asyncio
from typing import Dict, List, Optional, Any, Annotated
from datetime import datetime, timedelta
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.prebuilt import create_react_agent, InjectedState
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command
from config.settings import invoke_llm_safe, llm
from database.models.comprehensive_visa_application import ComprehensiveVisaApplication

# Global state store for workflow sessions
workflow_sessions: Dict[str, Dict[str, Any]] = {}

@tool
async def initialize_workflow_session(
    thread_id: Annotated[str, "Thread ID for this workflow session"],
    handoff_data: Annotated[dict, "Data received from handoff including country, visa_type, travel_dates"],
    state: Annotated[dict, InjectedState] = None
) -> str:
    """Initialize a new workflow session with handoff data from main agent"""
    
    print(f"DEBUG: initialize_workflow_session called with thread_id={thread_id}")
    print(f"DEBUG: handoff_data={handoff_data}")
    
    try:
        # Store session data
        workflow_sessions[thread_id] = {
            "handoff_data": handoff_data,
            "workflow_json": None,
            "current_stage_index": 0,
            "collected_data": {},
            "uploaded_documents": {},
            "stage_completion": {},
            "session_start": datetime.now().isoformat(),
            "status": "initialized"
        }
        
        print(f"DEBUG: Workflow session stored successfully")
        
        return f"Workflow session initialized for thread {thread_id}. Received handoff data: {handoff_data}. Ready to load workflow JSON."
        
    except Exception as e:
        print(f"DEBUG: Error in initialize_workflow_session: {e}")
        raise e

@tool
async def load_workflow_dynamically(
    thread_id: Annotated[str, "Thread ID for this workflow session"], 
    visa_type: Annotated[str, "Visa type to determine which workflow to load"],
    state: Annotated[dict, InjectedState] = None
) -> str:
    """Dynamically load and analyze any workflow JSON structure"""
    
    print(f"DEBUG: load_workflow_dynamically called with thread_id={thread_id}, visa_type={visa_type}")
    
    if thread_id not in workflow_sessions:
        print(f"DEBUG: Thread {thread_id} not found in workflow_sessions")
        return "Error: Workflow session not found. Please initialize first."
    
    session = workflow_sessions[thread_id]
    print(f"DEBUG: Found session: {session}")
    
    try:
        # Dynamic workflow file mapping - completely extensible
        import os
        # Use absolute path to avoid any path resolution issues
        backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
        workflow_files = {
            "Vietnam Tourism Single Entry": os.path.abspath(os.path.join(backend_dir, "VNM_tourism_single_entry_workflow_optimized.json")),
        }
        
        print(f"DEBUG: Available workflows: {list(workflow_files.keys())}")
        print(f"DEBUG: Backend directory resolved to: {backend_dir}")
        
        workflow_file = workflow_files.get(visa_type)
        print(f"DEBUG: Resolved workflow file path: {workflow_file}")
        if not workflow_file:
            print(f"DEBUG: No workflow found for visa type: {visa_type}")
            return f"No workflow found for visa type: {visa_type}. Available workflows: {list(workflow_files.keys())}"
        
        print(f"DEBUG: Loading workflow file: {workflow_file}")
        
        # Load and parse workflow JSON
        with open(workflow_file, 'r') as f:
            workflow_json = json.load(f)
        
        print(f"DEBUG: Workflow JSON loaded successfully")
        
        session["workflow_json"] = workflow_json
        session["status"] = "workflow_loaded"
        
        # Analyze workflow structure dynamically
        stages = workflow_json.get("collection_sequence", [])
        total_stages = len(stages)
        
        print(f"DEBUG: Found {total_stages} stages in workflow")
        
        analysis = f"**Workflow Analysis for {visa_type}**\n\n"
        analysis += f"**Total Stages:** {total_stages}\n"
        analysis += f"**Description:** {workflow_json.get('workflow_description', 'No description available')}\n\n"
        analysis += "**Stage Overview:**\n"
        
        for i, stage in enumerate(stages, 1):
            stage_title = stage.get("stage_title", f"Stage {i}")
            stage_desc = stage.get("stage_description", "No description")
            
            # Count requirements dynamically
            doc_count = len(stage.get("required_documents", []))
            field_count = len(stage.get("fields", {}))
            
            analysis += f"{i}. **{stage_title}**\n"
            analysis += f"   - {stage_desc}\n"
            analysis += f"   - Documents: {doc_count}, Fields: {field_count}\n"
        
        analysis += f"\nReady to begin stage 1: {stages[0].get('stage_title', 'First Stage')}"
        
        print(f"DEBUG: Analysis complete: {analysis[:200]}...")
        
        return analysis
        
    except Exception as e:
        print(f"DEBUG: Error in load_workflow_dynamically: {e}")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        return f"Error loading workflow: {str(e)}"

@tool
async def execute_current_stage(
    thread_id: Annotated[str, "Thread ID for this workflow session"],
    state: Annotated[dict, InjectedState] = None
) -> str:
    """Dynamically execute current stage based on workflow JSON structure"""
    
    if thread_id not in workflow_sessions:
        return "Workflow session not found."
    
    session = workflow_sessions[thread_id]
    workflow_json = session.get("workflow_json")
    
    if not workflow_json:
        return "No workflow loaded. Please load workflow first."
    
    stages = workflow_json.get("collection_sequence", [])
    current_index = session["current_stage_index"]
    
    if current_index >= len(stages):
        return "All stages completed! Ready to generate final output."
    
    current_stage = stages[current_index]
    stage_title = current_stage.get("stage_title", f"Stage {current_index + 1}")
    stage_desc = current_stage.get("stage_description", "")
    
    requirements = f"**Current Stage: {stage_title}**\n{stage_desc}\n\n**Requirements:**\n\n"
    
    # Process document requirements dynamically
    docs = current_stage.get("required_documents", [])
    if docs:
        requirements += "**Documents Needed:**\n"
        for doc in docs:
            status = "UPLOADED" if doc["type"] in session["uploaded_documents"] else "PENDING"
            required_text = "REQUIRED" if doc.get("required", True) else "OPTIONAL"
            requirements += f"- **{doc['name']}** ({required_text}) - {status}\n"
            requirements += f"  {doc['description']}\n"
            
            # Show extraction capabilities
            if doc.get("extracts"):
                extracts = ", ".join(doc["extracts"])
                requirements += f"  Will extract: {extracts}\n"
            requirements += "\n"
    
    # Process field requirements dynamically
    fields = current_stage.get("fields", {})
    if fields:
        requirements += "**Information Needed:**\n"
        for field_name, field_info in fields.items():
            status = "COLLECTED" if field_name in session["collected_data"] else "PENDING"
            required_text = "REQUIRED" if field_info.get("required", True) else "OPTIONAL"
            field_type = field_info.get("field_type", "text")
            
            # Determine extraction method dynamically
            extraction = field_info.get("extraction_method", "user_input")
            if extraction == "passport_bio_page":
                extraction_text = "(Will be extracted from passport)"
            elif extraction == "flight_tickets_or_user_input":
                extraction_text = "(From flight tickets or manual input)"
            elif extraction == "calculated_from_dates":
                extraction_text = "(Auto-calculated)"
            elif extraction == "handoff_data":
                extraction_text = "(From initial handoff)"
            else:
                extraction_text = "(Manual input required)"
            
            requirements += f"- **{field_name.replace('_', ' ').title()}** ({required_text}) - {status}\n"
            requirements += f"  Type: {field_type} {extraction_text}\n"
            
            # Add prompt if available
            if field_info.get("prompt"):
                requirements += f"  Prompt: {field_info['prompt']}\n"
            
            # Add options for select fields
            if field_info.get("options"):
                options = ", ".join(field_info["options"][:5])
                if len(field_info["options"]) > 5:
                    options += "..."
                requirements += f"  Options: {options}\n"
            
            requirements += "\n"
    
    return requirements

@tool
async def collect_data_item(
    thread_id: Annotated[str, "Thread ID for this workflow session"],
    field_name: Annotated[str, "Name of the field to collect"],
    field_value: Annotated[str, "Value provided by user or extracted"],
    state: Annotated[dict, InjectedState] = None
) -> str:
    """Collect and validate field data according to workflow specifications"""
    
    if thread_id not in workflow_sessions:
        return "Workflow session not found."
    
    session = workflow_sessions[thread_id]
    workflow_json = session.get("workflow_json")
    
    # Find field definition in current stage
    stages = workflow_json.get("collection_sequence", [])
    current_stage = stages[session["current_stage_index"]]
    field_definition = current_stage.get("fields", {}).get(field_name)
    
    # Apply validation if defined
    if field_definition:
        validation = field_definition.get("validation", {})
        
        # Basic validation examples
        if validation.get("required") and not field_value:
            return f"Error: {field_name} is required and cannot be empty."
        
        if validation.get("min_length") and len(field_value) < validation["min_length"]:
            return f"Error: {field_name} must be at least {validation['min_length']} characters."
        
        if validation.get("max_length") and len(field_value) > validation["max_length"]:
            return f"Error: {field_name} must be no more than {validation['max_length']} characters."
    
    # Store the data
    session["collected_data"][field_name] = field_value
    
    # Update database if available
    try:
        db_application = await ComprehensiveVisaApplication.find_one({"thread_id": thread_id})
        if db_application:
            if not db_application.collected_data:
                db_application.collected_data = {}
            db_application.collected_data[field_name] = field_value
            await db_application.save()
    except Exception as e:
        print(f"DEBUG: Database update error: {e}")
    
    return f"Collected **{field_name.replace('_', ' ').title()}**: {field_value}"

@tool
async def process_document_extraction(
    thread_id: Annotated[str, "Thread ID for this workflow session"],
    document_type: Annotated[str, "Type of document uploaded"],
    extraction_results: Annotated[dict, "Data extracted from the document"],
    state: Annotated[dict, InjectedState] = None
) -> str:
    """Process document upload and map extracted data according to workflow"""
    
    if thread_id not in workflow_sessions:
        return "Workflow session not found."
    
    session = workflow_sessions[thread_id]
    workflow_json = session.get("workflow_json")
    
    # Find document definition in current stage
    stages = workflow_json.get("collection_sequence", [])
    current_stage = stages[session["current_stage_index"]]
    
    # Find the document definition
    doc_definition = None
    for doc in current_stage.get("required_documents", []):
        if doc["type"] == document_type:
            doc_definition = doc
            break
    
    if not doc_definition:
        return f"Document type {document_type} not expected in current stage."
    
    # Store document info
    session["uploaded_documents"][document_type] = {
        "upload_time": datetime.now().isoformat(),
        "extraction_results": extraction_results
    }
    
    # Auto-populate extracted fields based on workflow definition
    expected_extracts = doc_definition.get("extracts", [])
    extracted_fields = []
    
    for field_name in expected_extracts:
        if field_name in extraction_results and extraction_results[field_name]:
            session["collected_data"][field_name] = extraction_results[field_name]
            extracted_fields.append(f"   - {field_name.replace('_', ' ').title()}: {extraction_results[field_name]}")
    
    result = f"**{document_type.replace('_', ' ').title()}** processed successfully!\n\n"
    if extracted_fields:
        result += "**Auto-extracted data:**\n" + "\n".join(extracted_fields)
    else:
        result += "Document uploaded but no data could be extracted."
    
    return result

@tool
async def validate_stage_completion(
    thread_id: Annotated[str, "Thread ID for this workflow session"],
    state: Annotated[dict, InjectedState] = None
) -> str:
    """Check if current stage is complete according to workflow requirements"""
    
    if thread_id not in workflow_sessions:
        return "Workflow session not found."
    
    session = workflow_sessions[thread_id]
    workflow_json = session.get("workflow_json")
    
    if not workflow_json:
        return "No workflow loaded."
    
    stages = workflow_json.get("collection_sequence", [])
    current_index = session["current_stage_index"]
    
    if current_index >= len(stages):
        return "All stages already completed!"
    
    current_stage = stages[current_index]
    missing_items = []
    
    # Check required documents
    for doc in current_stage.get("required_documents", []):
        if doc.get("required", True) and doc["type"] not in session["uploaded_documents"]:
            missing_items.append(f"Document: {doc['name']}")
    
    # Check required fields
    for field_name, field_info in current_stage.get("fields", {}).items():
        if field_info.get("required", True) and field_name not in session["collected_data"]:
            missing_items.append(f"Field: {field_name.replace('_', ' ').title()}")
    
    if missing_items:
        return f"**Stage not complete.** Missing:\n" + "\n".join([f"- {item}" for item in missing_items])
    
    return "Stage is complete! Ready to advance to next stage."

@tool
async def advance_to_next_stage(
    thread_id: Annotated[str, "Thread ID for this workflow session"],
    state: Annotated[dict, InjectedState] = None
) -> str:
    """Advance to the next stage in the workflow"""
    
    if thread_id not in workflow_sessions:
        return "Workflow session not found."
    
    session = workflow_sessions[thread_id]
    workflow_json = session.get("workflow_json")
    
    stages = workflow_json.get("collection_sequence", [])
    current_index = session["current_stage_index"]
    
    # Mark current stage as complete
    current_stage = stages[current_index]
    stage_name = current_stage.get("stage", f"stage_{current_index}")
    session["stage_completion"][stage_name] = True
    
    # Advance to next stage
    session["current_stage_index"] += 1
    
    # Check if workflow is complete
    if session["current_stage_index"] >= len(stages):
        session["status"] = "complete"
        return "**All stages completed!** Ready to generate final JS file for automation."
    
    # Move to next stage
    next_stage = stages[session["current_stage_index"]]
    next_title = next_stage.get("stage_title", f"Stage {session['current_stage_index'] + 1}")
    
    return f"**Stage completed!** Advanced to next stage: **{next_title}**"

@tool
async def generate_automation_js_file(
    thread_id: Annotated[str, "Thread ID for this workflow session"],
    state: Annotated[dict, InjectedState] = None
) -> str:
    """Generate the final JS file for automation using workflow mapping rules"""
    
    if thread_id not in workflow_sessions:
        return "Workflow session not found."
    
    session = workflow_sessions[thread_id]
    workflow_json = session.get("workflow_json")
    
    if session["status"] != "complete":
        return "Cannot generate JS file - workflow not complete."
    
    # Get automation output mapping from workflow
    output_mapping = workflow_json.get("automation_output_mapping", {})
    target_format = output_mapping.get("target_format", "personal-info.properties.js")
    
    # Prepare the JS data structure
    collected_data = session["collected_data"]
    handoff_data = session["handoff_data"]
    
    # Build the final automation data according to mapping
    automation_data = {}
    
    # Add handoff data
    automation_data.update(handoff_data)
    
    # Add all collected data
    automation_data.update(collected_data)
    
    # Apply any default values from workflow
    default_values = workflow_json.get("default_values", {})
    for key, value in default_values.items():
        if key not in automation_data:
            automation_data[key] = value
    
    # Generate JS file content in exact format needed
    js_content = f"""// Auto-generated automation data for {handoff_data.get('visa_type', 'Unknown Visa')}
// Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
// Thread ID: {thread_id}

export const personalInfoConfig = {{
  dummyData: {json.dumps(automation_data, indent=4, ensure_ascii=False)},
  
  mandatoryFields: [
    {', '.join([f'"{field}"' for field in collected_data.keys() if collected_data[field]])}
  ],
  
  // Auto-generated validation rules
  validationRules: {{
    // Basic validation rules can be added here
  }},
  
  // Auto-generated field mappings
  fieldMappings: {{
    {','.join([f'"{k}": "{v}"' for k, v in collected_data.items() if v])}
  }}
}};
"""
    
    # Save to file
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    output_filename = f"/mnt/c/Users/dev/github/veazy_b2c/backend/generated_automation_{thread_id}_{timestamp}.js"
    
    try:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(js_content)
        
        # Update session status
        session["status"] = "js_generated"
        session["output_file"] = output_filename
        
        # Update database
        try:
            db_application = await ComprehensiveVisaApplication.find_one({"thread_id": thread_id})
            if db_application:
                db_application.automation_ready_data = automation_data
                db_application.js_file_path = output_filename
                db_application.status = "ready_for_automation"
                await db_application.save()
        except Exception as e:
            print(f"DEBUG: Database update error: {e}")
        
        return f"""**Automation JS file generated successfully!**

**File:** `{output_filename}`
**Data Fields:** {len(collected_data)} fields collected
**Status:** Ready for automation agent

The file contains all collected data in the proper format for automation scripts."""
        
    except Exception as e:
        return f"Error generating JS file: {str(e)}"

@tool
async def get_workflow_status(
    thread_id: Annotated[str, "Thread ID for this workflow session"],
    state: Annotated[dict, InjectedState] = None
) -> str:
    """Get current workflow status and progress summary"""
    
    if thread_id not in workflow_sessions:
        return "No workflow session found."
    
    session = workflow_sessions[thread_id]
    workflow_json = session.get("workflow_json")
    
    if not workflow_json:
        return "No workflow loaded."
    
    stages = workflow_json.get("collection_sequence", [])
    current_index = session["current_stage_index"]
    
    status = f"""**Workflow Status Report**

**Visa Type:** {session['handoff_data'].get('visa_type', 'Unknown')}
**Current Stage:** {current_index + 1} of {len(stages)}
**Started:** {session['session_start']}
**Status:** {session['status'].replace('_', ' ').title()}

**Progress:**
"""
    
    for i, stage in enumerate(stages):
        if i < current_index:
            status_icon = "COMPLETED"
        elif i == current_index:
            status_icon = "IN_PROGRESS"
        else:
            status_icon = "PENDING"
        
        status += f"{status_icon} - {stage.get('stage_title', f'Stage {i+1}')}\n"
    
    status += f"\n**Data Collected:** {len(session['collected_data'])} fields"
    status += f"\n**Documents Uploaded:** {len(session['uploaded_documents'])} documents"
    
    return status

def create_intelligent_workflow_agent():
    """Create the intelligent workflow agent that can handle any workflow.json"""
    
    tools = [
        initialize_workflow_session,
        load_workflow_dynamically,
        execute_current_stage,
        collect_data_item,
        process_document_extraction,
        validate_stage_completion,
        advance_to_next_stage,
        generate_automation_js_file,
        get_workflow_status
    ]
    
    workflow_agent_prompt = """You are an Intelligent Workflow Agent designed to execute any workflow.json dynamically.

**Your Core Capabilities:**
1. Load and analyze any workflow JSON structure
2. Execute workflow stages systematically 
3. Process document uploads and extract data
4. Collect user information intelligently
5. Validate completion at each stage
6. Generate final JS files for automation

**Your Working Principles:**
- NEVER hardcode workflows - be completely dynamic
- Follow the workflow.json structure exactly
- Be systematic: complete each stage before moving to next
- Provide clear, helpful instructions to users
- Extract maximum data from documents before asking users
- Validate all requirements before advancing stages
- Generate accurate automation files

**Your Workflow Process:**
1. Initialize session with handoff data
2. Load and analyze the workflow JSON
3. Execute each stage systematically:
   - Present requirements clearly
   - Collect documents/data
   - Validate completion
   - Advance to next stage
4. Generate final JS file when complete

**Communication Style:**
- Be professional and systematic
- Provide helpful prompts and explanations
- Show progress and what's remaining
- Celebrate completions

**Important:** You work with ANY workflow.json structure. Adapt to whatever workflow is loaded. Be intelligent about field types, validation rules, and requirements specified in the JSON.

When you receive a handoff, immediately initialize the session and load the appropriate workflow. Guide the user through each stage until completion."""
    
    return create_react_agent(
        model=llm,
        tools=tools,
        prompt=workflow_agent_prompt,
        checkpointer=InMemorySaver()
    )

# Initialize the intelligent workflow agent
intelligent_workflow_agent = create_intelligent_workflow_agent()