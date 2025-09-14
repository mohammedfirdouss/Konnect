"""Agent tools for the ADK (Agent Development Kit) integration"""

from typing import Dict, List, Callable, Any
from dataclasses import dataclass
from sqlalchemy.orm import Session

from . import crud, schemas
from .database import get_db


@dataclass
class AgentTool:
    """Agent tool definition"""
    name: str
    description: str
    function: Callable
    parameters: Dict[str, Any]


class AgentToolRegistry:
    """Registry for agent tools"""
    
    def __init__(self):
        self.tools: Dict[str, AgentTool] = {}
    
    def register_tool(self, tool: AgentTool):
        """Register a new tool"""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> AgentTool:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def get_all_tools(self) -> List[AgentTool]:
        """Get all registered tools"""
        return list(self.tools.values())
    
    def execute_tool(self, name: str, **kwargs) -> Any:
        """Execute a tool by name with arguments"""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool '{name}' not found")
        return tool.function(**kwargs)


# Global tool registry
tool_registry = AgentToolRegistry()


def get_user_activity_tool(user_id: int, limit: int = 50) -> Dict[str, Any]:
    """
    Agent tool function to get user purchase and browsing history.
    
    Args:
        user_id: The ID of the user to get activity for
        limit: Maximum number of records to return (default: 50)
        
    Returns:
        Dictionary containing user activity data
    """
    # Get database session
    db = next(get_db())
    
    try:
        # Get user activity using CRUD function
        activity = crud.get_user_activity(db, user_id, limit)
        
        # Convert to dictionary for easier consumption by the agent
        return {
            "user_id": activity.user_id,
            "purchases": [
                {
                    "id": purchase.id,
                    "listing_id": purchase.listing_id,
                    "amount": purchase.amount,
                    "status": purchase.status,
                    "transaction_hash": purchase.transaction_hash,
                    "created_at": purchase.created_at.isoformat(),
                    "updated_at": purchase.updated_at.isoformat(),
                }
                for purchase in activity.purchases
            ],
            "browsing_history": [
                {
                    "id": history.id,
                    "listing_id": history.listing_id,
                    "action": history.action,
                    "created_at": history.created_at.isoformat(),
                }
                for history in activity.browsing_history
            ],
            "summary": {
                "total_purchases": len(activity.purchases),
                "total_browsing_actions": len(activity.browsing_history),
                "purchase_amount_total": sum(p.amount for p in activity.purchases),
            }
        }
    finally:
        db.close()


# Register the user activity tool
user_activity_tool = AgentTool(
    name="get_user_activity",
    description="Get user purchase history and browsing activity for personalized recommendations",
    function=get_user_activity_tool,
    parameters={
        "user_id": {
            "type": "integer",
            "description": "The ID of the user to get activity for",
            "required": True
        },
        "limit": {
            "type": "integer", 
            "description": "Maximum number of records to return",
            "required": False,
            "default": 50
        }
    }
)

tool_registry.register_tool(user_activity_tool)


def get_agent_prompt() -> str:
    """Get the updated agent prompt that includes instructions for using tools"""
    return """
You are Konnect AI, an intelligent assistant for the Konnect campus marketplace platform.

Your primary goal is to help users find relevant products and services, provide personalized recommendations, and assist with marketplace interactions.

## Available Tools:

1. **get_user_activity**: Use this tool to fetch a user's purchase history and browsing behavior
   - Parameters: user_id (required), limit (optional, default=50)
   - Use this to understand user preferences and provide personalized recommendations
   - Example: When a user asks for recommendations, first call get_user_activity(user_id=123) to understand their history

## Instructions:

- Always use the get_user_activity tool when users ask for recommendations or when you need to understand their preferences
- Analyze purchase patterns and browsing behavior to suggest relevant items
- Consider the user's previous purchases and interests when making recommendations
- Be helpful, friendly, and focused on the campus community
- Prioritize student-to-student commerce and campus-specific needs

## Example Usage:

User: "Can you recommend some items for me?"
1. First call: get_user_activity(user_id=user_id)
2. Analyze the returned data for patterns (categories, price ranges, etc.)
3. Provide personalized recommendations based on their history

Remember to always use tools when they can provide relevant information to better assist the user.
"""


def format_tool_for_agent(tool: AgentTool) -> Dict[str, Any]:
    """Format a tool definition for agent consumption"""
    return {
        "name": tool.name,
        "description": tool.description,
        "parameters": tool.parameters
    }


def get_available_tools() -> List[Dict[str, Any]]:
    """Get all available tools formatted for agent consumption"""
    return [format_tool_for_agent(tool) for tool in tool_registry.get_all_tools()]