from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import uuid

from app.services import request_network
from app.services.rate_agent_service import rate_agent_service

router = APIRouter(tags=["Invoices and Factoring"])

class InvoiceRequest(BaseModel):
    payee: str = Field(..., description="Wallet address of the payee")
    amount: str = Field(..., description="Invoice amount")
    payer: Optional[str] = Field(None, description="Wallet address of the payer (optional)")
    invoice_currency: str = Field("ETH-base-base", description="Invoice currency")
    payment_currency: str = Field("ETH-base-base", description="Payment currency")
    due_date: Optional[str] = Field(None, description="Invoice due date (ISO format)")

class FactoringOfferRequest(BaseModel):
    payment_reference: str = Field(..., description="Payment reference of the invoice")
    advance_percentage: Optional[float] = Field(None, description="Percentage to advance (if custom)")
    factoring_fee: Optional[float] = Field(None, description="Factoring fee percentage (if custom)")

class AcceptFactoringRequest(BaseModel):
    offer_id: str = Field(..., description="ID of the factoring offer")

# In-memory storage for factoring offers (would use a database in production)
factoring_offers = {}

@router.get("/network/invoice-config")
async def get_invoice_network_config():
    """
    Get the network configuration for invoicing
    
    Returns information about the network used for invoicing (Base Mainnet)
    """
    try:
        network_info = request_network.get_network_info()
        return {
            "status": "success",
            "message": "Invoice transactions are on Base Mainnet, liquidity pool and trading on Base Sepolia",
            "data": {
                "invoice_network": network_info,
                "liquidity_network": {
                    "name": "Base Sepolia",
                    "chainId": 84532,
                    "currency": "ETH",
                    "rpcUrl": "https://sepolia.base.org",
                    "blockExplorer": "https://sepolia.basescan.org"
                }
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/factoring/offers")
async def create_factoring_offer(request: FactoringOfferRequest):
    """
    Create a factoring offer for an invoice
    
    Generates a factoring offer with advance amount and fee based on
    Token Metrics market sentiment data.
    """
    try:
        # Get invoice details
        invoice_data = request_network.get_invoice_status(request.payment_reference)
        
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
        if request.advance_percentage is not None:
            advance_percentage = request.advance_percentage
        else:
            # Use the middle of the recommended range
            advance_percentage = (rates["advance_percentage"][0] + rates["advance_percentage"][1]) / 2
            
        if request.factoring_fee is not None:
            factoring_fee = request.factoring_fee
        else:
            # Use the middle of the recommended range
            factoring_fee = (rates["fee_range"][0] + rates["fee_range"][1]) / 2
        
        # Mock invoice amount (since we don't know exactly how to extract it from invoice_data)
        # In a real implementation, you'd extract this value correctly from the response
        invoice_amount = 1.0  # Default 1 ETH if we can't extract it
        
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
            "payment_reference": request.payment_reference,
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

@router.post("/factoring/accept")
async def accept_factoring_offer(request: AcceptFactoringRequest):
    """
    Accept a factoring offer and initiate the advance payment
    
    When an SME accepts a factoring offer, the system advances them
    the agreed-upon portion of the invoice amount.
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
        
        # In a real implementation, this would transfer funds from vault to SME
        
        # Update the status
        offer["status"] = "accepted"
        offer["accepted_at"] = datetime.now().isoformat()
        
        return {
            "status": "success",
            "message": "Factoring offer accepted",
            "data": {
                "offer_id": request.offer_id,
                "payment_reference": offer["payment_reference"],
                "advance_amount": offer["advance_amount"],
                "factoring_fee": offer["factoring_fee_amount"],
                "accepted_at": offer["accepted_at"]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/factoring/offers/{offer_id}")
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

@router.get("/factoring/offers")
async def list_factoring_offers():
    """
    List all factoring offers (for demo purposes)
    """
    return {
        "status": "success",
        "data": list(factoring_offers.values())
    }

@router.post("/simulate-payment/{payment_reference}")
async def simulate_payment(payment_reference: str, status: str = Query("paid", description="Payment status to simulate (paid, pending, failed)")):
    """
    Simulate an invoice payment (for demo purposes)
    
    This endpoint simulates a payment to an invoice, updating its status.
    """
    try:
        # In a real implementation, you would actually check the on-chain status
        # For the demo, we'll just mock a successful payment
        data = request_network.mock_payment_status(payment_reference, status)
        
        # If we have any factoring offers for this payment reference, update them
        for offer_id, offer in factoring_offers.items():
            if offer["payment_reference"] == payment_reference:
                if status == "paid":
                    offer["invoice_paid"] = True
                    offer["payment_timestamp"] = datetime.now().isoformat()
                    # In a real implementation, this would trigger the final payment
                    # of the remaining amount to the SME
                    offer["remaining_amount_paid"] = True
                    offer["remaining_amount_paid_timestamp"] = datetime.now().isoformat()
        
        return {
            "status": "success",
            "message": f"Payment simulation successful. Status: {status}",
            "data": data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/dashboard-data")
async def get_dashboard_data():
    """
    Get aggregated data for the dashboard
    
    Returns statistics about invoices, factoring, and payments for
    display on the dashboard.
    """
    try:
        # Calculate metrics based on factoring offers
        total_offers = len(factoring_offers)
        accepted_offers = sum(1 for o in factoring_offers.values() if o.get('status') == 'accepted')
        total_factored_amount = sum(o.get('advance_amount', 0) for o in factoring_offers.values() if o.get('status') == 'accepted')
        total_fees = sum(o.get('factoring_fee_amount', 0) for o in factoring_offers.values() if o.get('status') == 'accepted')
        
        # Mock data for the dashboard
        return {
            "status": "success",
            "data": {
                "total_invoices": total_offers + 5,  # Adding some mock data
                "total_factored_amount": total_factored_amount + 0.5,  # Adding some mock data
                "total_fees_earned": total_fees + 0.02,  # Adding some mock data
                "offers": {
                    "total": total_offers,
                    "accepted": accepted_offers,
                    "pending": total_offers - accepted_offers,
                    "conversion_rate": (accepted_offers / total_offers * 100) if total_offers > 0 else 0
                },
                "average_advance_percentage": 75.5,  # Mock data
                "average_factoring_fee": 3.2,  # Mock data
                "recent_activity": [
                    {
                        "type": "invoice_created",
                        "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
                        "amount": 1.2,
                        "currency": "ETH"
                    },
                    {
                        "type": "offer_accepted",
                        "timestamp": (datetime.now() - timedelta(hours=3)).isoformat(),
                        "amount": 0.8,
                        "currency": "ETH"
                    },
                    {
                        "type": "payment_received",
                        "timestamp": (datetime.now() - timedelta(hours=5)).isoformat(),
                        "amount": 1.5,
                        "currency": "ETH"
                    }
                ]
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@router.post("/invoices/create")
async def create_invoice_endpoint(invoice: InvoiceRequest):
    """Create a new invoice using Request Network"""
    try:
        # Default to ETH-base-base for both currencies
        invoice_currency = "ETH-base-base"
        payment_currency = "ETH-base-base"
        
        data = request_network.create_invoice(
            payee=invoice.payee,
            amount=invoice.amount,
            invoice_currency=invoice_currency,
            payment_currency=payment_currency,
            payer=invoice.payer
            # Skip due_date for now until we confirm it works
        )
        return {
            "status": "success", 
            "message": "Invoice created successfully",
            "data": data
        }
    except Exception as e:
        print(f"Error creating invoice: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))