from fastapi import APIRouter, HTTPException, Query
from app.services.token_metrics import token_metrics_service

router = APIRouter(prefix="/tokens", tags=["Token Metrics"])

@router.get("/info")
async def token_info(symbol: str):
    result = await token_metrics_service.get_token_info(symbol)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/trader-grades")
async def trader_grades(
    symbol: str,
    start_date: str = Query(None, alias="startDate"),
    end_date: str = Query(None, alias="endDate")
):
    result = await token_metrics_service.get_trader_grades(symbol, start_date, end_date)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/market-sentiment")
async def market_sentiment():
    result = await token_metrics_service.get_market_sentiment()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result
