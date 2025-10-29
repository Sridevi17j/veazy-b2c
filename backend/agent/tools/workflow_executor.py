# Advanced Workflow Executor with State Management
# Purpose: Stateful workflow execution with context switching, interruption handling, and recovery

import sys
sys.path.append('../..')

import json
from typing import Dict, List, Optional, Any, Literal
from typing_extensions import Annotated
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import InjectedState
from config.settings import invoke_llm_safe
from database.models.comprehensive_visa_application import ComprehensiveVisaApplication, DocumentInfo

# Workflow state management
workflow_states = {}  # In-memory state store (can be moved to database later)

WorkflowStage = Literal[
    "start", "documents", "personal_info", "contact_info", 
    "occupation_info", "travel_info", "emergency_contact", "financial_info", "complete"
]

class WorkflowState:
    """Manages workflow state across multiple interactions"""
    
    def __init__(self, thread_id: str, visa_type: str):
        self.thread_id = thread_id
        self.visa_type = visa_type
        self.current_stage: WorkflowStage = "start"
        self.stage_progress = {}  # Tracks completion within each stage
        self.collected_data = {}  # Stores all collected information
        self.workflow_json = None
        self.interrupted = False
        self.deviation_context = None
        
    def to_dict(self) -> Dict[str, Any]:
        """Serialize state for persistence"""
        return {
            "thread_id": self.thread_id,
            "visa_type": self.visa_type,
            "current_stage": self.current_stage,
            "stage_progress": self.stage_progress,
            "collected_data": self.collected_data,
            "interrupted": self.interrupted,
            "deviation_context": self.deviation_context
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'WorkflowState':
        """Deserialize state from persistence"""
        state = cls(data["thread_id"], data["visa_type"])
        state.current_stage = data["current_stage"]
        state.stage_progress = data["stage_progress"]
        state.collected_data = data["collected_data"]
        state.interrupted = data.get("interrupted", False)
        state.deviation_context = data.get("deviation_context")
        return state


@tool
async def workflow_executor_tool(
    user_message: str, 
    intent_type: str = "workflow_progress",
    state: Annotated[dict, InjectedState] = None
) -> str:
    """
    Advanced workflow executor with state management and deviation handling.
    
    Args:
        user_message: User's input message
        thread_id: Unique thread identifier for state persistence
        intent_type: Type of interaction (workflow_progress, deviation, modification, etc.)
    
    Returns:
        Appropriate response based on workflow state and user intent
    """
    
    try:
        # Extract session_id from injected state
        thread_id = "default_thread"  # fallback
        if state:
            thread_id = state.get("session_id", "default_thread")
            print(f"DEBUG: State injected successfully: session_id={thread_id}")
        else:
            print(f"DEBUG: No state injected, using fallback: {thread_id}")
            
        print(f"DEBUG: workflow_executor_tool called with thread_id: {thread_id}, user_message: {user_message[:50]}...")
        
        # Get or create workflow state and database application
        state = _get_workflow_state(thread_id)
        
        # Get user_id from thread state (if available)
        user_id = _get_user_id_from_thread(thread_id)
        print(f"DEBUG: Got user_id: {user_id} from thread: {thread_id}")
        
        # Direct database access - ensure application exists
        db_application = await ComprehensiveVisaApplication.find_one({"thread_id": thread_id})
        if not db_application:
            # Create new application linked to both user_id and thread_id
            unique_app_id = f"{user_id}_{thread_id}" if user_id else thread_id
            db_application = ComprehensiveVisaApplication(
                application_id=unique_app_id,
                thread_id=thread_id,
                user_id=user_id,  # Link to user
                visa_type=state.visa_type
            )
            print(f"DEBUG: Creating new visa application with data: {db_application.dict()}")
            await db_application.insert()
            print(f"SUCCESS: Created new visa application: {unique_app_id} for user: {user_id}, thread: {thread_id}")
        else:
            print(f"DEBUG: Found existing application: {db_application.application_id}")
        
        # Load workflow JSON if not already loaded
        if not state.workflow_json:
            state.workflow_json = await _get_workflow_json(state.visa_type)
        
        # Route based on intent type
        print(f"DEBUG: Routing based on intent_type: {intent_type}")
        if intent_type == "deviation":
            print("DEBUG: Handling deviation")
            return await _handle_deviation(state, user_message)
        elif intent_type == "modification":
            print("DEBUG: Handling modification")
            return await _handle_data_modification(state, user_message)
        elif intent_type == "resume":
            print("DEBUG: Handling resume")
            return await _resume_workflow(state)
        elif intent_type == "document_processed":
            print("DEBUG: Handling document_processed")
            return await _handle_document_processed(state, user_message, thread_id)
        else:
            print("DEBUG: Default - calling _progress_workflow")
            return await _progress_workflow(state, user_message)
            
    except Exception as e:
        return f"I encountered an issue with your visa application. Let me help you continue from where we left off. What would you like to do next?"


def _get_workflow_state(thread_id: str) -> WorkflowState:
    """Get or create workflow state for thread"""
    if thread_id not in workflow_states:
        # Create new state - this should be called after visa type is confirmed
        visa_type = "Vietnam Tourism Single Entry"  # Default, should be passed from context
        workflow_states[thread_id] = WorkflowState(thread_id, visa_type)
    
    return workflow_states[thread_id]


def _get_user_id_from_thread(thread_id: str) -> Optional[str]:
    """Get user_id from thread state (from production_app.py thread_states)"""
    try:
        # Import here to avoid circular imports
        import sys
        sys.path.append('..')
        from agent.production_app import thread_states
        
        thread_state = thread_states.get(thread_id, {})
        return thread_state.get("user_id")
    except Exception as e:
        print(f"Could not get user_id from thread {thread_id}: {e}")
        return None


async def _progress_workflow(state: WorkflowState, user_message: str) -> str:
    """Progress through workflow stages based on current state"""
    
    print(f"DEBUG: _progress_workflow called with current_stage: {state.current_stage}")
    
    if state.current_stage == "start":
        print("DEBUG: Current stage is 'start', calling _start_workflow")
        return await _start_workflow(state)
    else:
        print(f"DEBUG: Current stage is '{state.current_stage}', not 'start' - continuing with stage processing")
    
    # Check if user provided required information for current stage
    stage_complete = await _process_stage_input(state, user_message)
    
    if stage_complete:
        # Move to next stage
        next_stage = _get_next_stage(state.current_stage)
        state.current_stage = next_stage
        
        # Mark current stage as complete in database
        await _mark_stage_complete(thread_id, state.current_stage)
        
        if next_stage == "complete":
            return await _complete_workflow(state)
        else:
            return await _start_stage(state, next_stage)
    else:
        # Continue current stage
        return await _continue_current_stage(state, user_message)


async def _start_workflow(state: WorkflowState) -> str:
    """Start the workflow with Stage 1: Documents"""
    print("DEBUG: _start_workflow called - setting current_stage to 'documents'")
    state.current_stage = "documents"
    print(f"DEBUG: About to call _start_stage with stage: documents")
    result = await _start_stage(state, "documents")
    print(f"DEBUG: _start_stage returned: {result[:100]}...")
    return result


async def _start_stage(state: WorkflowState, stage: WorkflowStage) -> str:
    """Start a specific workflow stage"""
    
    print(f"DEBUG: _start_stage called with stage: {stage}")
    
    if not state.workflow_json:
        print("DEBUG: No workflow_json found!")
        return "Unable to load workflow configuration. Please try again."
    
    print(f"DEBUG: Workflow JSON loaded, has {len(state.workflow_json.get('collection_sequence', []))} stages")
    
    # Find the stage in workflow JSON
    collection_sequence = state.workflow_json.get("collection_sequence", [])
    stage_config = next((s for s in collection_sequence if s["stage"] == stage), None)
    
    if not stage_config:
        print(f"DEBUG: Stage config for '{stage}' NOT FOUND!")
        available_stages = [s.get("stage") for s in collection_sequence]
        print(f"DEBUG: Available stages: {available_stages}")
        return f"Configuration for stage '{stage}' not found. Please contact support."
    
    print(f"DEBUG: Found stage config for '{stage}': {stage_config.get('stage_title', 'No title')}")
    
    # Generate stage-specific prompt
    stage_prompt = await _generate_stage_prompt(state, stage_config)
    print(f"DEBUG: Generated stage prompt: {stage_prompt[:100]}...")
    return stage_prompt


async def _generate_stage_prompt(state: WorkflowState, stage_config: Dict[str, Any]) -> str:
    """Generate appropriate prompt for a workflow stage"""
    
    stage_title = stage_config.get("stage_title", "")
    stage_name = stage_config.get("stage", "")
    
    print(f"DEBUG: _generate_stage_prompt for stage: {stage_name}, title: {stage_title}")
    print(f"DEBUG: Stage config keys: {list(stage_config.keys())}")
    
    # Handle document collection stages
    if "required_documents" in stage_config:
        print("DEBUG: This is a DOCUMENTS stage - generating document upload prompt")
        documents = stage_config["required_documents"]
        doc_list = []
        
        for i, doc in enumerate(documents, 1):
            doc_name = doc.get("name", "")
            doc_desc = doc.get("description", "")
            extracts = doc.get("extracts", [])
            
            doc_entry = f"{i}. **{doc_name}** - {doc_desc}"
            if extracts:
                doc_entry += f"\n   - Will automatically extract: {', '.join(extracts)}"
            doc_list.append(doc_entry)
        
        return f"""**{stage_title}**

Please upload these documents:

{chr(10).join(doc_list)}

Upload your documents one by one. I'll process each document and extract the required information automatically."""
    
    # Handle information collection stages
    elif "fields" in stage_config:
        print("DEBUG: This is a FIELDS stage - generating manual input prompt")
        fields = stage_config["fields"]
        user_input_fields = []
        
        for field_name, field_config in fields.items():
            if field_config.get("extraction_method") == "user_input":
                field_type = field_config.get("field_type", "text")
                required = field_config.get("required", False)
                options = field_config.get("options", [])
                
                field_prompt = f"• **{field_name.replace('_', ' ').title()}**"
                if required:
                    field_prompt += " (required)"
                
                if options:
                    field_prompt += f" - Choose from: {', '.join(options)}"
                
                user_input_fields.append(field_prompt)
        
        if user_input_fields:
            return f"""**{stage_title}**

Please provide the following information:

{chr(10).join(user_input_fields)}

You can provide them one by one or all together."""
        else:
            # All fields are auto-extracted, move to next stage
            next_stage = _get_next_stage(stage_name)
            state.current_stage = next_stage
            return await _start_stage(state, next_stage)
    
    return f"Processing {stage_title}..."


async def _process_stage_input(state: WorkflowState, user_message: str) -> bool:
    """Process user input for current stage and determine if stage is complete"""
    
    # Use LLM to analyze if the user provided the required information
    analysis_prompt = f"""Analyze if the user has provided the required information for the current workflow stage.

CURRENT STAGE: {state.current_stage}
WORKFLOW JSON: {json.dumps(state.workflow_json, indent=2) if state.workflow_json else 'Not loaded'}
USER MESSAGE: "{user_message}"
ALREADY COLLECTED: {json.dumps(state.collected_data, indent=2)}

Determine:
1. Has the user provided the required information for this stage?
2. What specific information was provided?
3. Is this stage now complete?

Respond with JSON:
{{"stage_complete": true/false, "extracted_info": {{}}, "missing_items": []}}"""

    response = invoke_llm_safe([HumanMessage(content=analysis_prompt)])
    
    try:
        analysis = json.loads(response.content.strip())
        
        # Update collected data in memory state
        if analysis.get("extracted_info"):
            state.collected_data.update(analysis["extracted_info"])
            
            # Update database with extracted info
            await _update_stage_data(thread_id, state.current_stage, analysis["extracted_info"])
        
        return analysis.get("stage_complete", False)
        
    except:
        # Fallback: assume not complete
        return False


async def _continue_current_stage(state: WorkflowState, user_message: str) -> str:
    """Continue with current stage, asking for missing information"""
    
    prompt = f"""The user is in the middle of completing a workflow stage. Generate a helpful response to continue the process.

CURRENT STAGE: {state.current_stage}
USER MESSAGE: "{user_message}"
COLLECTED SO FAR: {json.dumps(state.collected_data, indent=2)}

Provide a helpful response that:
1. Acknowledges what they provided
2. Asks for any missing required information
3. Guides them to complete the current stage"""

    response = invoke_llm_safe([HumanMessage(content=prompt)])
    return response.content.strip()


async def _handle_deviation(state: WorkflowState, user_message: str) -> str:
    """Handle user deviation from workflow (questions, off-topic, etc.)"""
    
    state.interrupted = True
    state.deviation_context = {
        "stage_when_interrupted": state.current_stage,
        "user_question": user_message
    }
    
    # Generate response to deviation then offer to resume
    deviation_prompt = f"""The user deviated from the visa application workflow to ask a question or make a comment.

USER MESSAGE: "{user_message}"
CURRENT WORKFLOW STAGE: {state.current_stage}

Provide:
1. A helpful answer to their question/comment
2. Then offer to resume the visa application where they left off

Be conversational and helpful."""

    response = invoke_llm_safe([HumanMessage(content=deviation_prompt)])
    return response.content.strip() + "\n\nWould you like to continue with your visa application where we left off?"


async def _handle_data_modification(state: WorkflowState, user_message: str) -> str:
    """Handle user request to modify previously collected data"""
    
    modification_prompt = f"""The user wants to modify some information in their visa application.

USER REQUEST: "{user_message}"
CURRENT DATA: {json.dumps(state.collected_data, indent=2)}

Determine:
1. What information they want to change
2. Update the data accordingly
3. Confirm the changes

Respond with the updated information and ask if they want to continue."""

    response = invoke_llm_safe([HumanMessage(content=modification_prompt)])
    return response.content.strip()


async def _resume_workflow(state: WorkflowState) -> str:
    """Resume workflow after interruption"""
    
    state.interrupted = False
    state.deviation_context = None
    
    return f"Great! Let's continue with your {state.visa_type} application. " + await _start_stage(state, state.current_stage)


async def _handle_document_processed(state: WorkflowState, user_message: str, thread_id: str) -> str:
    """Handle processed document data from document processing tool"""
    
    try:
        # Extract JSON data from document processing tool response
        extracted_data = _parse_extracted_data_json(user_message)
        
        if extracted_data:
            # Save extracted data to database
            await _update_stage_data(thread_id, state.current_stage, extracted_data)
            
            # Mark current stage as complete
            await _mark_stage_complete(thread_id, state.current_stage)
            
            # Move to next stage
            next_stage = _get_next_stage(state.current_stage)
            state.current_stage = next_stage
            
            if next_stage == "complete":
                return await _complete_workflow(state)
            else:
                return await _start_stage(state, next_stage)
        else:
            return "I couldn't process the extracted document data. Please try uploading your documents again."
            
    except Exception as e:
        print(f"Error handling document processed: {e}")
        return "There was an issue processing your document data. Please try uploading again or continue with manual information entry."


def _parse_extracted_data_json(user_message: str) -> Optional[Dict[str, Any]]:
    """Parse extracted data JSON from document processing tool response"""
    
    try:
        # Look for EXTRACTED_DATA_JSON: pattern in the message
        import re
        json_pattern = r'EXTRACTED_DATA_JSON:\s*(\{.*?\})'
        match = re.search(json_pattern, user_message, re.DOTALL)
        
        if match:
            json_str = match.group(1)
            return json.loads(json_str)
        else:
            # Try to find any JSON in the message
            json_match = re.search(r'\{.*\}', user_message, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
                
        return None
        
    except Exception as e:
        print(f"Error parsing extracted data JSON: {e}")
        return None


def _get_next_stage(current_stage: WorkflowStage) -> WorkflowStage:
    """Get the next stage in workflow sequence"""
    
    stage_sequence = [
        "start", "documents", "personal_info", "contact_info", 
        "occupation_info", "travel_info", "emergency_contact", "financial_info", "complete"
    ]
    
    try:
        current_index = stage_sequence.index(current_stage)
        if current_index < len(stage_sequence) - 1:
            return stage_sequence[current_index + 1]
    except ValueError:
        pass
    
    return "complete"


async def _complete_workflow(state: WorkflowState) -> str:
    """Complete the workflow and generate final response"""
    
    return f"""🎉 **Congratulations!** Your {state.visa_type} application is now complete!

**Application Summary:**
- All required information collected
- Documents processed and verified
- Application ready for submission

**Next Steps:**
1. Review your application details
2. Make payment for visa processing
3. Submit your application
4. Track your application status

Your application will be processed within 3-5 business days. You'll receive updates via email.

Is there anything else you'd like to know about your visa application?"""


async def _get_workflow_json(visa_type: str) -> Optional[dict]:
    """Get workflow JSON based on visa type"""
    try:
        # Map visa type to workflow file
        workflow_mapping = {
            "Vietnam Tourism Single Entry": "VNM_tourism_single_entry_workflow.json",
        }
        
        workflow_file = workflow_mapping.get(visa_type, "VNM_tourism_single_entry_workflow.json")
        # Get absolute path to backend directory
        import os
        backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        workflow_path = os.path.join(backend_dir, workflow_file)
        
        with open(workflow_path, 'r') as f:
            return json.load(f)
    
    except Exception as e:
        print(f"Error loading workflow JSON: {e}")
        return None


async def _update_stage_data(thread_id: str, stage: str, stage_data: Dict[str, Any]) -> None:
    """Update stage-specific data in database using direct model access"""
    try:
        # Single fetch
        application = await ComprehensiveVisaApplication.find_one({"thread_id": thread_id})
        if not application:
            return
        
        # Update stage-specific fields
        if stage == "documents":
            # Handle document data
            for field, value in stage_data.items():
                if hasattr(application.documents, field):
                    setattr(application.documents, field, value)
                    
        elif stage == "personal_info":
            for field, value in stage_data.items():
                if hasattr(application.personal_info, field) and value is not None:
                    setattr(application.personal_info, field, value)
                    
        elif stage == "contact_info":
            for field, value in stage_data.items():
                if hasattr(application.contact_info, field) and value is not None:
                    setattr(application.contact_info, field, value)
                    
        elif stage == "occupation_info":
            for field, value in stage_data.items():
                if hasattr(application.occupation_info, field) and value is not None:
                    setattr(application.occupation_info, field, value)
                    
        elif stage == "travel_info":
            for field, value in stage_data.items():
                if hasattr(application.travel_info, field) and value is not None:
                    setattr(application.travel_info, field, value)
                    
        elif stage == "emergency_contact":
            for field, value in stage_data.items():
                if hasattr(application.emergency_contact, field) and value is not None:
                    setattr(application.emergency_contact, field, value)
                    
        elif stage == "financial_info":
            for field, value in stage_data.items():
                if hasattr(application.financial_info, field) and value is not None:
                    setattr(application.financial_info, field, value)
        
        # Update raw collected data for flexibility
        application.raw_collected_data[stage] = stage_data
        
        # Update timestamp
        application.update_timestamp()
        
        # Single save
        await application.save()
        
    except Exception as e:
        print(f"Error updating stage data: {e}")


async def _mark_stage_complete(thread_id: str, completed_stage: str) -> None:
    """Mark a stage as complete in database"""
    try:
        # Single fetch
        application = await ComprehensiveVisaApplication.find_one({"thread_id": thread_id})
        if not application:
            return
        
        # Mark stage complete
        if completed_stage not in application.workflow_progress.completed_stages:
            application.workflow_progress.completed_stages.append(completed_stage)
        
        # Update current stage
        application.workflow_progress.current_stage = completed_stage
        
        # Update timestamp
        application.update_timestamp()
        
        # Single save
        await application.save()
        
    except Exception as e:
        print(f"Error marking stage complete: {e}")


async def _get_application_data(thread_id: str) -> Optional[Dict[str, Any]]:
    """Get complete application data from database"""
    try:
        application = await ComprehensiveVisaApplication.find_one({"thread_id": thread_id})
        if not application:
            return None
            
        return {
            "application_id": application.application_id,
            "thread_id": application.thread_id,
            "visa_type": application.visa_type,
            "status": application.status,
            "completion_percentage": application.get_completion_percentage(),
            "current_stage": application.workflow_progress.current_stage,
            "completed_stages": application.workflow_progress.completed_stages,
            "personal_info": application.personal_info.dict(),
            "contact_info": application.contact_info.dict(),
            "travel_info": application.travel_info.dict(),
            "documents": application.documents.dict(),
            "created_at": application.created_at,
            "updated_at": application.updated_at
        }
        
    except Exception as e:
        print(f"Error getting application data: {e}")
        return None


# Export the tool
__all__ = ["workflow_executor_tool"]