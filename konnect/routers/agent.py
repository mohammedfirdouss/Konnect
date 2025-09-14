"""Agent router for ADK integration"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..database import get_db
from ..dependencies import get_current_user
from ..models import User
from ..agent_tools import tool_registry, get_agent_prompt, get_available_tools
from .. import crud

router = APIRouter(prefix="/agent", tags=["agent"])


@router.get("/tools", response_model=List[Dict[str, Any]])
async def list_available_tools():
    """Get list of available agent tools"""
    return get_available_tools()


@router.get("/prompt")
async def get_prompt():
    """Get the agent prompt with tool instructions"""
    return {"prompt": get_agent_prompt()}


@router.post("/tools/{tool_name}")
async def execute_tool(
    tool_name: str,
    parameters: Dict[str, Any],
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Execute an agent tool"""
    try:
        # For security, ensure user can only access their own data
        if tool_name == "get_user_activity":
            user_id = parameters.get("user_id")
            if user_id != current_user.id:
                raise HTTPException(status_code=403, detail="Access denied")
            
            # Execute the tool using CRUD function directly (safer than tool registry for API)
            limit = parameters.get("limit", 50)
            activity = crud.get_user_activity(db, user_id, limit)
            
            return {
                "tool": tool_name,
                "result": {
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
            }
        else:
            raise HTTPException(status_code=404, detail=f"Tool '{tool_name}' not found")
            
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tool execution failed: {str(e)}")


@router.get("/user-activity")
async def get_user_activity_endpoint(
    limit: int = 50,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get user activity (purchases and browsing history) - convenience endpoint"""
    activity = crud.get_user_activity(db, current_user.id, limit)
    
    return {
        "user_id": activity.user_id,
        "purchases": activity.purchases,
        "browsing_history": activity.browsing_history,
        "summary": {
            "total_purchases": len(activity.purchases),
            "total_browsing_actions": len(activity.browsing_history),
            "purchase_amount_total": sum(p.amount for p in activity.purchases),
        }
    }