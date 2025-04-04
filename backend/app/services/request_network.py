import os
import requests
from typing import Dict, Optional, Any

REQUEST_API_KEY = os.getenv("REQUEST_API_KEY")
BASE_URL = "https://api.request.network/v1"

headers = {
    "x-api-key": REQUEST_API_KEY,
    "Content-Type": "application/json"
}

def create_invoice(payee, amount, invoice_currency, payment_currency, payer=None, due_date=None):
    """Create a new invoice using Request Network API"""
    url = f"{BASE_URL}/request"
    
    # Start with the basic required fields
    payload = {
        "payee": payee,
        "amount": amount,
        "invoiceCurrency": invoice_currency,
        "paymentCurrency": payment_currency
    }
    
    # Add optional payer if provided
    if payer:
        payload["payer"] = payer
    
    # Add due date in the correct format if provided
    if due_date:
        # Ensure date is in ISO 8601 format (YYYY-MM-DDTHH:MM:SS.sssZ)
        # For now, skip the recurrence as it might be causing issues
        pass
    
    print(f"Sending request to {url} with payload: {payload}")
    response = requests.post(url, headers=headers, json=payload)
    
    # Print the response for debugging
    print(f"Response status: {response.status_code}")
    print(f"Response body: {response.text}")
    
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

def calculate_factoring_offer(
    invoice_amount: float, 
    due_date: Optional[str] = None, 
    advance_percentage: float = 70.0, 
    factoring_fee: float = 3.0
) -> Dict[str, Any]:
    """Calculate a factoring offer based on the invoice amount
    
    Args:
        invoice_amount: The total invoice amount
        due_date: Optional due date for the invoice
        advance_percentage: Percentage of the invoice to advance immediately (default: 70%)
        factoring_fee: Fee percentage for the factoring service (default: 3%)
    
    Returns:
        Dict with offer details
    """
    from datetime import datetime
    
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

def mock_payment_status(payment_reference: str, status: str = "pending") -> Dict[str, Any]:
    """Mock payment status for testing the factoring workflow
    
    Args:
        payment_reference: The payment reference of the request
        status: Payment status (pending, paid, failed)
    
    Returns:
        Mock payment status response
    """
    statuses = {
        "pending": {
            "hasBeenPaid": False,
            "paymentReference": payment_reference,
            "requestId": f"01e273ecc29d4b526df3a0f1f05ffc59372af8752c2b678096e49ac270416a7{payment_reference[-2:]}",
            "isListening": True,
            "txHash": None
        },
        "paid": {
            "hasBeenPaid": True,
            "paymentReference": payment_reference,
            "requestId": f"01e273ecc29d4b526df3a0f1f05ffc59372af8752c2b678096e49ac270416a7{payment_reference[-2:]}",
            "isListening": False,
            "txHash": f"0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcd{payment_reference[-2:]}"
        },
        "failed": {
            "hasBeenPaid": False,
            "paymentReference": payment_reference,
            "requestId": f"01e273ecc29d4b526df3a0f1f05ffc59372af8752c2b678096e49ac270416a7{payment_reference[-2:]}",
            "isListening": False,
            "txHash": None,
            "error": "Payment failed"
        }
    }
    
    return statuses.get(status, statuses["pending"])

def get_network_info() -> Dict[str, Any]:
    """Get information about the invoice network (Base Mainnet)
    
    Returns:
        Network information
    """
    return {
        "name": "Base",
        "chainId": 8453,
        "currency": "ETH",
        "rpcUrl": "https://mainnet.base.org",
        "blockExplorer": "https://basescan.org"
    }

def get_invoice_status(payment_reference: str) -> Dict[str, Any]:
    """Get the status of an invoice"""
    url = f"{BASE_URL}/request/{payment_reference}"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()

def get_payment_calldata(payment_reference: str) -> Dict[str, Any]:
    """Get the calldata needed to pay a request"""
    url = f"{BASE_URL}/request/{payment_reference}/pay"
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()