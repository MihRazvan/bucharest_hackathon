# app/api/agent_routes.py
from fastapi import APIRouter, HTTPException

from app.services.agent_service import agent_service

router = APIRouter(prefix="/agent", tags=["AI Agent"])

@router.get("/wallet")
async def get_wallet_details():
    """Get the agent's wallet details"""
    result = agent_service.get_wallet_details()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/balance")
async def get_wallet_balance():
    """Get the agent's wallet balance"""
    result = agent_service.get_wallet_balance()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result