from fastapi import APIRouter, HTTPException
from app.services.token_metrics import token_metrics_service

router = APIRouter(prefix="/tokens", tags=["Token Metrics"])

@router.get("/market-sentiment")
async def market_sentiment():
    result = await token_metrics_service.get_market_sentiment()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/stablecoin-health")
async def stablecoin_health(symbols: str = "USDC,USDT,DAI"):
    symbols_list = symbols.split(",")
    result = await token_metrics_service.get_stablecoin_health(symbols=symbols_list)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result
