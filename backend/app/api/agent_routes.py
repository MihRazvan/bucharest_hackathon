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

def request_faucet_funds(self):
    """Request testnet funds from the CDP faucet"""
    try:
        if not self.agent_kit:
            # Try to initialize again if it failed before
            if not self.initialize_agent():
                return {"status": "error", "message": "Agent initialization failed"}
        
        # Check if we're on a testnet
        if "sepolia" not in self.network_id.lower() and "testnet" not in self.network_id.lower():
            return {"status": "error", "message": "Faucet is only available on testnets"}
        
        try:
            # Request funds
            result = self.agent_kit.execute_action(
                "cdp_api", "request_faucet_funds", 
                {"asset_id": None}  # Default to ETH
            )
            return {"status": "success", "data": result}
        except Exception as faucet_error:
            # If the action fails, provide a helpful message
            return {
                "status": "error", 
                "message": f"Faucet request failed: {str(faucet_error)}",
                "wallet_address": self.wallet_provider.get_address() if self.wallet_provider else None,
                "network": self.network_id
            }
    except Exception as e:
        return {"status": "error", "message": str(e)}