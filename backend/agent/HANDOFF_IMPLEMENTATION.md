# Agent Handoff Implementation

## Overview
Multi-agent system with LangGraph handoff from Main Agent → Workflow Agent

## Architecture

```
User Request
    ↓
Main Agent (Consultation & Recommendation)
    ├─ Collects basic info (country, purpose, dates, travelers)
    ├─ Calls database_visa_lookup_tool
    ├─ Recommends visa type
    ├─ Waits for user confirmation
    └─ User says "yes"
        ↓
    Calls transfer_to_workflow_agent (handoff tool)
        ↓
Workflow Agent (Document Collection & Processing)
    ├─ Loads workflow JSON (10 stages)
    ├─ Stage 1: Document Collection
    ├─ Stage 2: Contact Information
    ├─ Stage 3: Travel Details
    ├─ ... (continues through all stages)
    └─ Stage 10: Generate JS automation file
```

## Key Files

### 1. `tools/workflow_handoff_tool.py`
- Creates `transfer_to_workflow_agent` tool
- Uses LangGraph `Command(goto="workflow_agent")` for handoff
- Passes handoff_data (visa_type, country, purpose, travel_dates)

### 2. `multi_agent_graph.py`
- Combines main_agent + workflow_agent in StateGraph
- Simple 3-line graph setup
- Compiled multi_agent_system

### 3. `agent/state.py`
- Added `handoff_data` field for agent communication
- Added `workflow_mode` field to track active agent

### 4. `production_app.py`
- Uses `multi_agent_system` instead of single agent
- Handles LangGraph streaming format
- Extracts messages from node outputs

### 5. `agents/intelligent_workflow_agent.py`
- Pre-built workflow agent with 8 tools
- Dynamically executes workflow JSON
- Handles document processing, data collection, JS generation

## Flow Example

```
User: "I want to apply for Vietnam visa"
Main Agent: "What is your purpose of travel? How many travelers? Travel dates?"

User: "Tourism, 1 traveler, 20-25 March 2026"
Main Agent: *calls database_visa_lookup_tool*
Main Agent: "I recommend Vietnam Tourism Single Entry. Can we proceed?"

User: "yes"
Main Agent: *calls transfer_to_workflow_agent*
                ↓ HANDOFF ↓
Workflow Agent: "Let's start with document collection. Please upload:"
                 - Passport Bio Page (REQUIRED)
                 - Passport Photograph (REQUIRED)
                 - Flight Tickets (OPTIONAL)

User: "I uploaded my passport"
Workflow Agent: *processes document, extracts data, continues to next stage*
```

## Testing

To test the handoff:
1. Start conversation with main agent
2. Provide basic info (country, purpose, dates)
3. Confirm visa recommendation with "yes"
4. Verify handoff occurs (check logs for "transfer_to_workflow_agent")
5. Continue interaction - should be handled by workflow agent

## Debug Logs

Look for these in console:
```
DEBUG: workflow_handoff_tool called!
DEBUG: confirmed_visa_type=Vietnam Tourism Single Entry
✓ Main agent initialized
✓ Workflow agent initialized
✓ Multi-agent system compiled successfully!
```
