from services.request_network import create_invoice
import os

def test_create_invoice():
    payee = "0x0a6A5Ba22da4e199bB5d8Cc04a84976C5930d049"
    amount = "1.00"
    invoice = create_invoice(payee, amount)
    assert "requestID" in invoice
    assert "paymentReference" in invoice
