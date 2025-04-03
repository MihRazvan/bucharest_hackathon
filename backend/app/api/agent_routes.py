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

@router.get("/status")
async def get_agent_status():
    """Get the status of the agent service"""
    return {
        "status": "success",
        "agent_initialized": agent_service.agent_kit is not None,
        "network_id": agent_service.network_id,
        "wallet_provider": agent_service.wallet_provider is not None,
        "wallet_address": agent_service.wallet_provider.get_address() if agent_service.wallet_provider else None
    }

# Add this to your agent_routes.py
@router.post("/faucet")
async def request_faucet_funds():
    """Request testnet funds from the CDP faucet"""
    result = agent_service.request_faucet_funds()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result