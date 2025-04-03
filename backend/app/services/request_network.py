import os
import requests

REQUEST_API_KEY = os.getenv("REQUEST_API_KEY")
BASE_URL = "https://api.request.network/v1"

headers = {
    "x-api-key": REQUEST_API_KEY,
    "Content-Type": "application/json"
}

def create_invoice(payee: str, amount: str, invoice_currency: str, payment_currency: str):
    url = f"{BASE_URL}/request"  # ✅ Not hardcoded in BASE_URL
    payload = {
        "payee": payee,
        "amount": amount,
        "invoiceCurrency": invoice_currency,
        "paymentCurrency": payment_currency
    }

    response = requests.post(url, headers=headers, json=payload)
    response.raise_for_status()
    return response.json()

def get_invoice_status(payment_reference: str):
    url = f"{BASE_URL}/request/{payment_reference}"  # ✅ No double /request
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()
