# Advanced Workflow Executor with State Management
# Purpose: Stateful workflow execution with context switching, interruption handling, and recovery

import sys
sys.path.append('../..')

import json
from typing import Dict, List, Optional, Any, Literal
from typing_extensions import Annotated
from datetime import datetime
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage
from langgraph.prebuilt import InjectedState
from config.settings import invoke_llm_safe
from database.models.visa_application import VisaApplication, DocumentInfo

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
    Now delegates to intelligent workflow agent when workflow session is active.

    Args:
        user_message: User's input message
        intent_type: Type of interaction (workflow_progress, deviation, modification, etc.)
        state: Injected agent state containing session_id and user_id

    Returns:
        Appropriate response based on workflow state and user intent
    """

    print("=" * 80)
    print("🔧 WORKFLOW_EXECUTOR_TOOL CALLED!")
    print(f"📝 User message: {user_message}")
    print(f"📝 Intent type: {intent_type}")
    print("=" * 80)

    try:
        # Extract session_id from injected state
        thread_id = "default_thread"  # fallback
        if state:
            thread_id = state.get("session_id", "default_thread")
            print(f"DEBUG: State injected successfully: session_id={thread_id}")
        else:
            print(f"DEBUG: No state injected, using fallback: {thread_id}")

        print(f"DEBUG: workflow_executor_tool called with thread_id: {thread_id}, user_message: {user_message[:50]}...")

        # Get user_id from injected agent state
        user_id = state.get("user_id") if state else None
        print(f"DEBUG: Got user_id: {user_id} from injected agent state")

        # CRITICAL: Check if intelligent workflow agent session exists
        try:
            from agent.agents.intelligent_workflow_agent import (
                workflow_sessions,
                collect_data_item,
                process_document_extraction,
                execute_current_stage,
                advance_to_next_stage
            )

            if thread_id in workflow_sessions:
                print(f"DEBUG: Found active workflow session for {thread_id} - delegating to intelligent workflow agent")

                # Delegate to intelligent workflow agent based on intent_type
                if intent_type == "document_processed" or "upload" in user_message.lower():
                    # User uploaded a document - need to process it first with document_processing_tool
                    print(f"DEBUG: User uploaded document - calling document_processing_tool first")

                    # Import document processing tool and workflow agent tools
                    from agent.tools.document_processing import document_processing_tool
                    from agent.agents.intelligent_workflow_agent import (
                        validate_stage_completion,
                        advance_to_next_stage
                    )

                    # Process document with GPT-4 Vision extraction
                    doc_result = await document_processing_tool.ainvoke({
                        "user_message": user_message,
                        "document_type": "passport_bio_page",  # Can be made smarter with LLM analysis
                        "session_id": thread_id,
                        "user_id": user_id  # Pass user_id directly
                    })

                    print(f"DEBUG: Document processing result: {doc_result[:200]}...")

                    # Check if current stage is now complete
                    try:
                        is_complete = await validate_stage_completion.ainvoke({
                            "thread_id": thread_id,
                            "state": state
                        })

                        print(f"DEBUG: Stage completion check: {is_complete}")

                        # If stage complete, advance to next stage
                        if "complete" in is_complete.lower() or "yes" in is_complete.lower():
                            advance_result = await advance_to_next_stage.ainvoke({
                                "thread_id": thread_id,
                                "state": state
                            })
                            return f"{doc_result}\n\n---\n\n{advance_result}"
                        else:
                            return doc_result

                    except Exception as e:
                        print(f"DEBUG: Could not check stage completion: {e}")
                        # Fallback: just return document result
                        return doc_result

                elif intent_type == "deviation":
                    # User asked a question during workflow
                    print(f"DEBUG: Handling deviation - calling execute_current_stage to maintain context")
                    # For deviations, we answer the question then remind them of current stage
                    deviation_response = f"Let me help with that: {user_message}\n\n"
                    stage_reminder = await execute_current_stage.ainvoke({
                        "thread_id": thread_id,
                        "state": state
                    })
                    return deviation_response + "\n\n" + stage_reminder

                elif intent_type == "modification":
                    # User wants to modify previously provided data
                    print(f"DEBUG: Handling modification via collect_data_item")
                    result = await collect_data_item.ainvoke({
                        "thread_id": thread_id,
                        "field_name": "modification_request",
                        "field_value": user_message,
                        "state": state
                    })
                    return result

                else:
                    # Default: user providing data for current stage
                    print(f"DEBUG: Default workflow progress - calling collect_data_item")

                    # First, try to collect the data
                    result = await collect_data_item.ainvoke({
                        "thread_id": thread_id,
                        "field_name": "user_input",
                        "field_value": user_message,
                        "state": state
                    })

                    return result

            else:
                print(f"DEBUG: No active workflow session found - using fallback OLD workflow logic")
                # Fall through to old workflow logic below

        except ImportError as e:
            print(f"DEBUG: Could not import intelligent workflow agent: {e}")
            # Fall through to old workflow logic

        # === OLD WORKFLOW LOGIC (FALLBACK) ===
        # This should rarely be used now, but kept for backward compatibility

        # Fallback: try thread state if not in agent state
        if not user_id:
            user_id = _get_user_id_from_thread(thread_id)
            print(f"DEBUG: Fallback - Got user_id: {user_id} from thread: {thread_id}")

        # Get or create workflow state and database application
        workflow_state = _get_workflow_state(thread_id)

        # Direct database access - ensure application exists (find by user_id)
        db_application = await VisaApplication.find_one({"user_id": user_id, "status": "in_progress"})
        if not db_application:
            # Create new application linked to user_id
            unique_app_id = f"VA_{user_id}_{datetime.now().strftime('%Y%m%d')}_{thread_id[:8]}"
            db_application = VisaApplication(
                visa_application_id=unique_app_id,
                user_id=user_id,
                status="in_progress"
            )
            print(f"DEBUG: Creating new visa application with data: {db_application.dict()}")
            await db_application.insert()
            print(f"SUCCESS: Created new visa application: {unique_app_id} for user: {user_id}")
        else:
            print(f"DEBUG: Found existing application: {db_application.visa_application_id}")

        # Load workflow JSON if not already loaded
        if not workflow_state.workflow_json:
            workflow_state.workflow_json = await _get_workflow_json(workflow_state.visa_type)

        # Route based on intent type
        print(f"DEBUG: Routing based on intent_type: {intent_type}")
        if intent_type == "deviation":
            print("DEBUG: Handling deviation")
            return await _handle_deviation(workflow_state, user_message)
        elif intent_type == "modification":
            print("DEBUG: Handling modification")
            return await _handle_data_modification(workflow_state, user_message)
        elif intent_type == "resume":
            print("DEBUG: Handling resume")
            return await _resume_workflow(workflow_state)
        elif intent_type == "document_processed":
            print("DEBUG: Handling document_processed")
            return await _handle_document_processed(workflow_state, user_message, thread_id)
        else:
            print("DEBUG: Default - calling _progress_workflow")
            return await _progress_workflow(workflow_state, user_message)

    except Exception as e:
        print(f"ERROR in workflow_executor_tool: {e}")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
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
        
        print(f"DEBUG: Available thread_ids in thread_states: {list(thread_states.keys())}")
        thread_state = thread_states.get(thread_id, {})
        print(f"DEBUG: Thread state for {thread_id}: {thread_state}")
        user_id = thread_state.get("user_id")
        print(f"DEBUG: Extracted user_id: {user_id}")
        return user_id
    except Exception as e:
        print(f"Could not get user_id from thread {thread_id}: {e}")
        import traceback
        print(f"DEBUG: Full traceback: {traceback.format_exc()}")
        return None

def _extract_user_id_from_jwt_token(authorization_header: Optional[str]) -> Optional[str]:
    """Extract user_id directly from JWT token in Authorization header"""
    if not authorization_header:
        return None
    
    try:
        # Extract token from "Bearer <token>" format
        if not authorization_header.startswith("Bearer "):
            return None
        
        token = authorization_header.replace("Bearer ", "")
        
        # Import JWT service
        from services.jwt_service import jwt_service
        
        # Verify and decode token
        result = jwt_service.verify_token(token)
        if result['success']:
            return result['data']['user_id']
        else:
            print(f"JWT token verification failed: {result.get('error')}")
            return None
            
    except Exception as e:
        print(f"Error extracting user_id from JWT token: {e}")
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
        # Get user_id from thread
        user_id = _get_user_id_from_thread(thread_id)
        if not user_id:
            return

        # Single fetch by user_id
        application = await VisaApplication.find_one({"user_id": user_id, "status": "in_progress"})
        if not application:
            return
        
        # Get or create primary traveler
        primary_traveler = application.get_primary_traveler()
        if not primary_traveler:
            from database.models.visa_application import TravelerData
            primary_traveler = TravelerData(traveler_id=1, is_primary_applicant=True)
            application.travelers.append(primary_traveler)

        # Store data dynamically in collected_data
        if stage not in primary_traveler.collected_data:
            primary_traveler.collected_data[stage] = {}

        primary_traveler.collected_data[stage].update(stage_data)

        # Update timestamp
        application.update_timestamp()

        # Single save
        await application.save()
        
    except Exception as e:
        print(f"Error updating stage data: {e}")


async def _mark_stage_complete(thread_id: str, completed_stage: str) -> None:
    """Mark a stage as complete in database"""
    try:
        # Get user_id from thread
        user_id = _get_user_id_from_thread(thread_id)
        if not user_id:
            return

        # Single fetch by user_id
        application = await VisaApplication.find_one({"user_id": user_id, "status": "in_progress"})
        if not application:
            return

        # Mark stage complete
        if completed_stage not in application.workflow_info.completed_stages:
            application.workflow_info.completed_stages.append(completed_stage)

        # Update current stage
        application.workflow_info.current_stage = completed_stage

        # Update timestamp
        application.update_timestamp()

        # Single save
        await application.save()
        
    except Exception as e:
        print(f"Error marking stage complete: {e}")


async def _get_application_data(thread_id: str) -> Optional[Dict[str, Any]]:
    """Get complete application data from database"""
    try:
        # Get user_id from thread
        user_id = _get_user_id_from_thread(thread_id)
        if not user_id:
            return None

        application = await VisaApplication.find_one({"user_id": user_id, "status": "in_progress"})
        if not application:
            return None

        return {
            "visa_application_id": application.visa_application_id,
            "user_id": application.user_id,
            "status": application.status,
            "basic_info": application.basic_info.dict(),
            "workflow_info": application.workflow_info.dict(),
            "completion_percentage": application.completion_percentage,
            "travelers": [t.dict() for t in application.travelers],
            "created_at": application.created_at,
            "updated_at": application.updated_at
        }

    except Exception as e:
        print(f"Error getting application data: {e}")
        return None


# Export the tool
__all__ = ["workflow_executor_tool"]