# Placeholder for detailed application tool
from typing import Any, Dict
from langchain_core.tools import tool
from agent.state import AgentState

@tool
def application_detailed_tool(user_message: str) -> Dict[str, Any]:
    """Placeholder tool for detailed application collection"""

    print("=" * 80)
    print("🔧 APPLICATION_DETAILED_TOOL CALLED!")
    print(f"📝 User message: {user_message}")
    print("=" * 80)

    return {
        "response": "Detailed application tool is not implemented yet.",
        "last_tool_used": "application_detailed"
    }

__all__ = ["application_detailed_tool"]