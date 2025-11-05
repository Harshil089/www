from fastapi import APIRouter
from pydantic import BaseModel
from agents.dashboard_agent import dashboard_agent
import json

router = APIRouter()

class UIEvent(BaseModel):
    event: str
    target_id: str
    params: dict = {}

@router.post("/agent")
async def handle_ui_event(event: UIEvent):
    """Handle UI events and return execution plan"""
    try:
        result = dashboard_agent(event.dict())
        return result
    except Exception as e:
        return {
            "navigate": None,
            "http": [],
            "render": [],
            "toasts": [f"Error: {str(e)}"],
            "state": {}
        }