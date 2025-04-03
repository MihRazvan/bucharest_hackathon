from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.services import request_network

router = APIRouter()

class InvoiceRequest(BaseModel):
    payee: str
    amount: str
    invoice_currency: str = "USD"
    payment_currency: str = "ETH-base-base"

@router.post("/invoices")
def create_invoice_endpoint(invoice: InvoiceRequest):
    try:
        data = request_network.create_invoice(
            payee=invoice.payee,
            amount=invoice.amount,
            invoice_currency=invoice.invoice_currency,
            payment_currency=invoice.payment_currency
        )
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/invoices/{payment_reference}")
def get_invoice_status(payment_reference: str):
    try:
        data = request_network.get_invoice_status(payment_reference)
        return {"status": "success", "data": data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
