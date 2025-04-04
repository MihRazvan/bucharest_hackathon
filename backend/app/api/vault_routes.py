# app/api/vault_routes.py
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional

from app.services.vault_service import vault_service

router = APIRouter(prefix="/vault", tags=["Vault"])

class DepositRequest(BaseModel):
    amount: float  # ETH amount
    private_key: str  # Private key for executing the transaction

class WithdrawRequest(BaseModel):
    shares: float  # Number of shares to withdraw
    private_key: str  # Private key for executing the transaction

@router.get("/stats")
async def get_vault_stats():
    """Get stats about the vault"""
    result = await vault_service.get_vault_stats()
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.post("/deposit")
async def deposit_to_vault(request: DepositRequest):
    """Deposit ETH to the vault"""
    # Convert ETH amount to wei
    amount_wei = int(request.amount * 10**18)
    
    result = await vault_service.deposit(amount_wei, request.private_key)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.post("/withdraw")
async def withdraw_from_vault(request: WithdrawRequest):
    """Withdraw ETH from the vault by redeeming shares"""
    # Convert shares to wei format (18 decimals)
    shares_wei = int(request.shares * 10**18)
    
    result = await vault_service.withdraw(shares_wei, request.private_key)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/balance/{address}")
async def get_vault_balance(address: str):
    """Get the vault balance (shares) for an address"""
    result = await vault_service.get_balance(address)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result

@router.get("/asset-balance/{address}")
async def get_asset_balance(address: str):
    """Get the asset balance (ETH equivalent) for an address based on shares"""
    result = await vault_service.get_asset_balance(address)
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
    return result