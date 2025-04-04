from fastapi import APIRouter, HTTPException, Body
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import uuid

from app.services import request_network
from app.services.rate_agent_service import rate_agent_service

router = APIRouter(prefix="/invoices", tags=["Invoices and Factoring"])

class InvoiceRequest(BaseModel):
    payee: str = Field(..., description="Wallet address of the payee")
    amount: str = Field(..., description="Invoice amount")
    payer: Optional[str] = Field(None, description="Wallet address of the payer (optional)")
    invoice_currency: str = Field("USD", description="Invoice currency")
    payment_currency: str = Field("ETH-sepolia-sepolia", description="Payment currency")
    due_date: Optional[str] = Field(None, description="Invoice due date (ISO format)")

class FactoringOfferRequest(BaseModel):
    payment_reference: str = Field(..., description="Payment reference of the invoice")
    advance_percentage: Optional[float] = Field(None, description="Percentage to advance (if custom)")
    factoring_fee: Optional[float] = Field(None, description="Factoring fee percentage (if custom)")

class AcceptFactoringRequest(BaseModel):
    offer_id: str = Field(..., description="ID of the factoring offer")

# In-memory storage for factoring offers (would use a database in production)
factoring_offers = {}

@router.post("/create")
async def create_invoice_endpoint(invoice: InvoiceRequest):
    """
    Create a new invoice using Request Network
    """
    try:
        data = request_network.create_invoice(
            payee=invoice.payee,
            amount=invoice.amount,
            invoice_currency=invoice.invoice_currency,
            payment_currency=invoice.payment_currency,
            payer=invoice.payer
        )
        return {
            "status": "success", 
            "message": "Invoice created successfully",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{payment_reference}")
async def get_invoice_status(payment_reference: str):
    """
    Get the status of an invoice
    """
    try:
        data = request_network.get_invoice_status(payment_reference)
        return {
            "status": "success", 
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{payment_reference}/payment-data")
async def get_payment_data(payment_reference: str):
    """
    Get the payment calldata for an invoice
    """
    try:
        data = request_network.get_payment_calldata(payment_reference)
        return {
            "status": "success", 
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{payment_reference}/factoring-offer")
async def create_factoring_offer(payment_reference: str, request: Optional[FactoringOfferRequest] = None):
    """
    Create a factoring offer for an invoice
    """
    try:
        # Get invoice details
        invoice_data = request_network.get_invoice_status(payment_reference)
        
        if invoice_data.get("hasBeenPaid", False):
            return {
                "status": "error",
                "message": "Invoice has already been paid"
            }
        
        # Get recommended rates from the AI agent
        rates_response = await rate_agent_service.get_recommended_rates()
        if rates_response["status"] != "success":
            return rates_response
        
        rates = rates_response["rates"]
        
        # Use custom rates if provided, otherwise use AI recommended rates
        if request and request.advance_percentage is not None:
            advance_percentage = request.advance_percentage
        else:
            # Use the middle of the recommended range
            advance_percentage = (rates["advance_percentage"][0] + rates["advance_percentage"][1]) / 2
            
        if request and request.factoring_fee is not None:
            factoring_fee = request.factoring_fee
        else:
            # Use the middle of the recommended range
            factoring_fee = (rates["fee_range"][0] + rates["fee_range"][1]) / 2
        
        # Extract invoice amount (assuming it's in the invoice_data)
        # This would need to be adapted based on actual Request Network response format
        # For now, we'll mock it
        
        # Mock invoice amount calculation
        # In a real implementation, we would extract this from invoice_data
        invoice_amount = float(100)  # Default mock value
        
        # Generate offer
        offer = request_network.calculate_factoring_offer(
            invoice_amount=invoice_amount,
            due_date=None,  # Could be extracted from invoice_data if available
            advance_percentage=advance_percentage,
            factoring_fee=factoring_fee
        )
        
        # Add offer ID and additional metadata
        offer_id = str(uuid.uuid4())
        full_offer = {
            "offer_id": offer_id,
            "payment_reference": payment_reference,
            "status": "pending",
            "created_at": datetime.now().isoformat(),
            "expires_at": (datetime.now() + timedelta(hours=24)).isoformat(),
            **offer,
            "market_data": rates_response.get("market_data", {})
        }
        
        # Store offer in memory (would be in database in production)
        factoring_offers[offer_id] = full_offer
        
        return {
            "status": "success",
            "message": "Factoring offer created",
            "data": full_offer
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/accept-factoring")
async def accept_factoring_offer(request: AcceptFactoringRequest):
    """
    Accept a factoring offer and initiate the advance payment
    """
    try:
        # Get the offer
        offer = factoring_offers.get(request.offer_id)
        if not offer:
            return {
                "status": "error",
                "message": "Factoring offer not found"
            }
        
        if offer["status"] != "pending":
            return {
                "status": "error",
                "message": f"Offer is no longer pending, current status: {offer['status']}"
            }
        
        # In a real implementation, this would:
        # 1. Transfer the advance amount to the SME
        # 2. Record the factoring agreement on-chain
        # 3. Update the status of the offer
        
        # For now, we'll just update the status
        offer["status"] = "accepted"
        offer["accepted_at"] = datetime.now().isoformat()
        
        return {
            "status": "success",
            "message": "Factoring offer accepted",
            "data": {
                "offer_id": request.offer_id,
                "advance_amount": offer["advance_amount"],
                "factoring_fee": offer["factoring_fee_amount"],
                "accepted_at": offer["accepted_at"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/offers/{offer_id}")
async def get_factoring_offer(offer_id: str):
    """
    Get details of a specific factoring offer
    """
    offer = factoring_offers.get(offer_id)
    if not offer:
        raise HTTPException(status_code=404, detail="Factoring offer not found")
    
    return {
        "status": "success",
        "data": offer
    }

@router.get("/offers")
async def list_factoring_offers():
    """
    List all factoring offers (for demo purposes)
    """
    return {
        "status": "success",
        "data": list(factoring_offers.values())
    }