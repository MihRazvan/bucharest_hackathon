# app/api/rate_routes.py
from fastapi import APIRouter, HTTPException
from app.services.rate_agent_service import rate_agent_service

router = APIRouter(prefix="/rates", tags=["Factoring Rates"])

@router.get("/recommend")
async def get_recommended_rates():
    """Get recommended factoring rates based on market conditions"""
    result = await rate_agent_service.get_recommended_rates()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result