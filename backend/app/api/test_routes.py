from fastapi import APIRouter, HTTPException
from app.services.token_metrics import token_metrics

router = APIRouter(prefix="/test", tags=["test"])

@router.get("/tokenmetrics")
async def test_token_metrics():
    """Test endpoint for Token Metrics API integration"""
    result = await token_metrics.get_market_sentiment()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/tokenmetrics/stablecoins")
async def test_stablecoin_health():
    """Test endpoint for Token Metrics stablecoin health"""
    result = await token_metrics.get_stablecoin_health()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result