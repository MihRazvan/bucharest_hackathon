# app/api/trading_routes.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.services.trading_agent_service import trading_agent_service

router = APIRouter(prefix="/trading", tags=["Idle Funds Trading"])

class TradingPlanRequest(BaseModel):
    idle_funds_amount: float = Field(1.0, description="Amount of idle funds to trade (default: 1.0 ETH)")

@router.post("/plan")
async def generate_trading_plan(request: TradingPlanRequest):
    """Generate a trading plan for idle funds"""
    result = await trading_agent_service.generate_trading_plan(request.idle_funds_amount)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.post("/execute/{plan_id}")
async def execute_trading_plan(plan_id: str):
    """Execute a trading plan (mocked)"""
    result = await trading_agent_service.execute_trade(plan_id)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/positions")
async def get_active_positions():
    """Get all active trading positions"""
    result = await trading_agent_service.get_active_positions()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/history")
async def get_trade_history():
    """Get trading history"""
    result = await trading_agent_service.get_trade_history()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/market-data")
async def get_market_data():
    """Get current market data for trading decisions"""
    result = await trading_agent_service.get_market_data()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/performance")
async def get_performance_stats():
    """Get performance statistics for trading operations (mocked)"""
    result = await trading_agent_service.get_performance_stats()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result