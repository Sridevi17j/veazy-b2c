from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from pydantic import BaseModel
from typing import List, Dict, Any
import os
import uuid
import json
from langchain_core.messages import HumanMessage

# Import agent-based system
from agent.agent import stream_agent, invoke_agent
from agent.state import AgentState

# Import database and API routes
import sys
sys.path.append('..')  # Add parent directory to path for imports
from database.mongodb import init_db
from api.countries import router as countries_router
from api.auth import router as auth_router, get_current_user
from database.models.user import User

# Global state management for threads
thread_states = {}

def _extract_clean_content(content) -> str:
    """Extract clean text content from potentially complex message content"""
    if isinstance(content, str):
        return content
    elif isinstance(content, list):
        # Handle list format like [{'text': 'Hello!', 'type': 'text'}]
        text_parts = []
        for item in content:
            if isinstance(item, dict):
                if 'text' in item:
                    text_parts.append(str(item['text']))
                elif 'content' in item:
                    text_parts.append(str(item['content']))
                else:
                    # Fallback to string representation
                    text_parts.append(str(item))
            else:
                text_parts.append(str(item))
        return ' '.join(text_parts)
    elif isinstance(content, dict):
        # Handle dict format like {'text': 'Hello!', 'type': 'text'}
        if 'text' in content:
            return str(content['text'])
        elif 'content' in content:
            return str(content['content'])
        else:
            # Fallback to string representation
            return str(content)
    else:
        # Fallback for any other type
        return str(content)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    print("Initializing database connection...")
    await init_db()
    print("Agent-based Visa Assistant Production Server initialized")
    yield
    # Shutdown
    print("Server shutdown")

app = FastAPI(
    title="Agent-based Visa Agent API",
    description="Production Agent-based Visa Assistant using LangGraph React Agent",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://veazy-frontend.onrender.com", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(countries_router)
app.include_router(auth_router)

# Import and include document upload router
try:
    from api.document_upload import router as document_router
    app.include_router(document_router)
except ImportError:
    print("Document upload router not available")

# Pydantic models
class MessageRequest(BaseModel):
    messages: List[Dict[str, Any]]

class ThreadResponse(BaseModel):
    thread_id: str

class RunResponse(BaseModel):
    messages: List[Dict[str, Any]]

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "agent-based-visa-agent"}

# LangGraph React SDK compatible endpoints
@app.get("/assistants/{assistant_id}")
async def get_assistant(assistant_id: str):
    if assistant_id == "visa_agent":
        return {
            "assistant_id": "visa_agent",
            "graph_id": "visa_agent", 
            "config": {},
            "metadata": {"type": "agent_based"}
        }
    raise HTTPException(status_code=404, detail="Assistant not found")

@app.post("/threads", response_model=ThreadResponse)
async def create_thread(current_user: User = Depends(get_current_user)):
    thread_id = str(uuid.uuid4())
    # Initialize thread state with user_id
    thread_states[thread_id] = {
        "messages": [],
        "session_id": thread_id,
        "user_id": str(current_user.id),  # Store user_id in thread state
        "tool_call_count": 0,
        "state_version": 1
    }
    return ThreadResponse(thread_id=thread_id)

@app.post("/threads/{thread_id}/runs/wait", response_model=RunResponse)
async def run_thread(thread_id: str, request: MessageRequest):
    try:
        # Get the latest user message
        user_message = request.messages[-1]["content"]
        
        # Get current thread state or create new one (this endpoint doesn't have current_user, but shouldn't be used anyway)
        if thread_id not in thread_states:
            thread_states[thread_id] = {
                "messages": [],
                "session_id": thread_id,
                "tool_call_count": 0,
                "state_version": 1
            }
        
        current_state = thread_states[thread_id]
        
        # Add user message to state
        user_msg = HumanMessage(content=user_message)
        current_state["messages"].append(user_msg)
        
        # DEBUG: Check what messages the agent will see
        print(f"DEBUG: Agent will see {len(current_state['messages'])} messages:")
        for i, msg in enumerate(current_state['messages']):
            msg_type = getattr(msg, 'type', 'unknown')
            content_preview = str(getattr(msg, 'content', ''))[:50]
            print(f"  {i}: {msg_type} - {content_preview}...")
        
        # Prepare input for agent
        agent_input = {
            "messages": current_state["messages"],
            "session_id": thread_id,
            "tool_call_count": current_state.get("tool_call_count", 0),
            "state_version": current_state.get("state_version", 1)
        }
        
        # Add any existing state fields
        for key, value in current_state.items():
            if key not in ["messages", "session_id", "tool_call_count", "state_version"] and value is not None:
                agent_input[key] = value
        
        # Run the agent with config containing thread_id
        config = {"configurable": {"thread_id": thread_id}}
        result = invoke_agent(agent_input, config)
        
        # DEBUG: Check what tools were called
        if "messages" in result and result["messages"]:
            ai_messages = [msg for msg in result["messages"] if hasattr(msg, 'type') and msg.type == 'ai']
            for ai_msg in ai_messages:
                if hasattr(ai_msg, 'tool_calls') and ai_msg.tool_calls:
                    for tool_call in ai_msg.tool_calls:
                        print(f"DEBUG: Agent called tool: {tool_call['name']}")
        
        # Update thread state with result
        thread_states[thread_id].update(result)
        
        # Extract response messages - handle both message objects and direct responses
        response_messages = []
        
        if "messages" in result and result["messages"]:
            # Get the last AI message
            for msg in reversed(result["messages"]):
                if hasattr(msg, 'type') and msg.type == 'ai':
                    # Extract clean text content from potentially complex message structure
                    content = _extract_clean_content(msg.content)
                    response_messages.append({
                        "role": "assistant", 
                        "content": content
                    })
                    break  # Only take the latest AI response
        
        # If no messages in result, check for direct response
        elif "response" in result:
            content = _extract_clean_content(result["response"])
            response_messages.append({
                "role": "assistant",
                "content": content
            })
        
        # Fallback: If no proper response found, provide error message
        if not response_messages:
            response_messages.append({
                "role": "assistant",
                "content": "I processed your request but couldn't generate a proper response. Please try again."
            })
        
        return RunResponse(messages=response_messages)
        
    except Exception as e:
        print(f"Error in run_thread: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/threads/{thread_id}/state")
async def get_thread_state(thread_id: str):
    try:
        if thread_id in thread_states:
            # Return clean state without internal message objects
            state = thread_states[thread_id].copy()
            # Convert messages to serializable format
            if "messages" in state:
                serializable_messages = []
                for msg in state["messages"]:
                    if hasattr(msg, 'type') and hasattr(msg, 'content'):
                        serializable_messages.append({
                            "type": msg.type,
                            "content": msg.content
                        })
                state["messages"] = serializable_messages
            return {"state": state}
        else:
            return {"state": {}}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Streaming endpoint that LangGraph React SDK expects
@app.post("/threads/{thread_id}/runs/stream")
async def stream_run(thread_id: str, request: dict, current_user: User = Depends(get_current_user)):
    from fastapi.responses import StreamingResponse
    
    try:
        # Get the input messages
        input_data = request.get("input", {})
        messages = input_data.get("messages", [])
        
        if not messages:
            raise HTTPException(status_code=400, detail="No messages provided")
        
        user_message = messages[-1]["content"]
        
        # Get current thread state or create new one
        if thread_id not in thread_states:
            thread_states[thread_id] = {
                "messages": [],
                "session_id": thread_id,
                "user_id": str(current_user.id),  # Add user_id to thread state
                "tool_call_count": 0,
                "state_version": 1
            }
        
        current_state = thread_states[thread_id]
        
        # Add user message to state
        user_msg = HumanMessage(content=user_message)
        current_state["messages"].append(user_msg)
        
        # DEBUG: Check what messages the agent will see (STREAMING)
        print(f"DEBUG STREAM: Agent will see {len(current_state['messages'])} messages:")
        for i, msg in enumerate(current_state['messages']):
            msg_type = getattr(msg, 'type', 'unknown')
            content_preview = str(getattr(msg, 'content', ''))[:50]
            print(f"  {i}: {msg_type} - {content_preview}...")
        
        async def generate_stream():
            print(f"Starting agent stream for thread {thread_id}, message: {user_message}")
            
            # First, yield the user message in LangGraph format
            user_message_obj = {
                "id": f"user_{thread_id}",
                "type": "human", 
                "content": user_message,
                "created_at": "2025-01-01T00:00:00Z"
            }
            yield f"data: {json.dumps(user_message_obj)}\n\n"
            
            # Prepare input for agent streaming
            agent_input = {
                "messages": current_state["messages"],
                "session_id": thread_id,
                "tool_call_count": current_state.get("tool_call_count", 0),
                "state_version": current_state.get("state_version", 1)
            }
            
            # Add any existing state fields
            for key, value in current_state.items():
                if key not in ["messages", "session_id", "tool_call_count", "state_version"] and value is not None:
                    agent_input[key] = value
            
            # Stream the AI response using agent streaming
            full_ai_response = ""
            config = {"configurable": {"thread_id": thread_id}}
            try:
                async for chunk in stream_agent(agent_input, config):
                    if chunk and chunk.get("type") == "token":
                        token_content = chunk.get("token", "")
                        full_ai_response += token_content
                        ai_message_obj = {
                            "id": f"ai_{thread_id}_{token_content[:10]}",
                            "type": "ai",
                            "content": token_content,
                            "created_at": "2025-01-01T00:00:00Z"
                        }
                        yield f"data: {json.dumps(ai_message_obj)}\n\n"
                
                # CRITICAL FIX: Save the complete AI response to thread state
                if full_ai_response.strip():
                    from langchain_core.messages import AIMessage
                    ai_msg = AIMessage(content=full_ai_response.strip())
                    current_state["messages"].append(ai_msg)
                    print(f"DEBUG: Saved AI response to thread state: {full_ai_response[:50]}...")
                        
            except Exception as stream_error:
                print(f"Streaming error: {stream_error}")
                error_message = {
                    "id": f"error_{thread_id}",
                    "type": "ai",
                    "content": "I encountered an issue processing your request. Please try again.",
                    "created_at": "2025-01-01T00:00:00Z"
                }
                yield f"data: {json.dumps(error_message)}\n\n"
            
            print("Agent stream completed")
        
        return StreamingResponse(
            generate_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive"
            }
        )
        
    except Exception as e:
        print(f"Error in stream_run: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# For local development
if __name__ == "__main__":
    import uvicorn
    import asyncio
    import sys
    
    # Fix for Windows asyncio event loop issue
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    port = int(os.environ.get("PORT", 8000))
    print(f"Starting Agent-based Visa Assistant on port {port}")
    
    # Enable auto-reload in development mode
    is_development = os.environ.get("ENVIRONMENT", "development") == "development"
    
    if is_development:
        print("Development mode: Auto-reload enabled")
        uvicorn.run(
            "production_app:app",  # Import string format required for reload
            host="0.0.0.0", 
            port=port,
            reload=True,
            reload_dirs=["./"]
        )
    else:
        uvicorn.run(
            app, 
            host="0.0.0.0", 
            port=port
        )