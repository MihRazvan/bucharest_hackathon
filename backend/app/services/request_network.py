import os
import requests
from typing import Dict, Optional, Any, Union
from datetime import datetime

REQUEST_API_KEY = os.getenv("REQUEST_API_KEY")
BASE_URL = "https://api.request.network/v1"

headers = {
    "x-api-key": REQUEST_API_KEY,
    "Content-Type": "application/json"
}

def create_invoice(payee: str, amount: str, invoice_currency: str, payment_currency: str, payer: Optional[str] = None):
    """Create a new invoice using Request Network API
    
    Args:
        payee: The wallet address of the payee
        amount: The invoice amount as a string
        invoice_currency: Currency ID from Request Network Token List
        payment_currency: Payment currency ID from Request Network Token List
        payer: Optional wallet address of the payer
    
    Returns:
        Dict with requestID and paymentReference
    """
    url = f"{BASE_URL}/request"
    
    payload = {
        "payee": payee,
        "amount": amount,
        "invoiceCurrency": invoice_currency,
        "paymentCurrency": payment_currency
    }
    
    # Add payer if provided
    if payer:
        payload["payer"] = payer
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def get_invoice_status(payment_reference: str) -> Dict[str, Any]:
    """Get the status of an invoice
    
    Args:
        payment_reference: The payment reference of the request
    
    Returns:
        Dict with invoice status details
    """
    url = f"{BASE_URL}/request/{payment_reference}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_payment_calldata(payment_reference: str) -> Dict[str, Any]:
    """Get the calldata needed to pay a request
    
    Args:
        payment_reference: The payment reference of the request
    
    Returns:
        Dict with transaction data for payment
    """
    url = f"{BASE_URL}/request/{payment_reference}/pay"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def initiate_payment(payee: str, amount: str, invoice_currency: str, payment_currency: str) -> Dict[str, Any]:
    """Initiate a payment without creating a request first
    
    Args:
        payee: The wallet address of the payee
        amount: The invoice amount as a string
        invoice_currency: Currency ID from Request Network Token List
        payment_currency: Payment currency ID from Request Network Token List
    
    Returns:
        Dict with payment information including transactions
    """
    url = f"{BASE_URL}/pay"
    
    payload = {
        "payee": payee,
        "amount": amount,
        "invoiceCurrency": invoice_currency,
        "paymentCurrency": payment_currency
    }
    
    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

# Additional helper functions for the factoring process

def calculate_factoring_offer(invoice_amount: float, due_date: Optional[str] = None, 
                              advance_percentage: float = 70.0, factoring_fee: float = 3.0) -> Dict[str, Any]:
    """Calculate a factoring offer based on the invoice amount
    
    Args:
        invoice_amount: The total invoice amount
        due_date: Optional due date for the invoice
        advance_percentage: Percentage of the invoice to advance immediately (default: 70%)
        factoring_fee: Fee percentage for the factoring service (default: 3%)
    
    Returns:
        Dict with offer details
    """
    advance_amount = invoice_amount * (advance_percentage / 100)
    fee_amount = invoice_amount * (factoring_fee / 100)
    remaining_amount = invoice_amount - advance_amount - fee_amount
    
    return {
        "invoice_amount": invoice_amount,
        "advance_percentage": advance_percentage,
        "advance_amount": advance_amount,
        "factoring_fee_percentage": factoring_fee,
        "factoring_fee_amount": fee_amount,
        "remaining_amount": remaining_amount,
        "due_date": due_date,
        "offer_timestamp": datetime.now().isoformat()
    }