from datetime import date
from typing import Dict
from fastapi import FastAPI, HTTPException, Request

from .models import Invoice, Payment, InvoiceCreate, PaymentCreate

app = FastAPI()

# In-memory storage
invoices: Dict[str, Invoice] = {}
payments: Dict[str, Payment] = {}


@app.post("/invoice", response_model=Invoice)
def generate_invoice(data: InvoiceCreate) -> Invoice:
    invoice = Invoice(**data.dict())
    invoices[invoice.id] = invoice
    return invoice


@app.post("/payment", response_model=Payment)
def mark_payment(data: PaymentCreate) -> Payment:
    invoice = invoices.get(data.invoice_id)
    if not invoice:
        raise HTTPException(status_code=404, detail="Invoice not found")
    invoice.status = "paid"
    payment = Payment(**data.dict())
    payments[payment.id] = payment
    return payment


@app.get("/revenue")
def total_revenue() -> Dict[str, float]:
    total = sum(inv.amount for inv in invoices.values() if inv.status == "paid")
    return {"revenue": total}


@app.post("/webhook/stripe")
async def stripe_webhook(request: Request) -> Dict[str, str]:
    event = await request.json()
    if event.get("type") == "invoice.paid":
        invoice_id = event.get("data", {}).get("object", {}).get("id")
        invoice = invoices.get(invoice_id)
        if invoice:
            invoice.status = "paid"
    return {"status": "success"}


@app.get("/report")
def report(start: date, end: date) -> Dict[str, float]:
    total = 0.0
    for payment in payments.values():
        if start <= payment.timestamp.date() <= end:
            inv = invoices.get(payment.invoice_id)
            if inv:
                total += inv.amount
    return {"start": start, "end": end, "revenue": total}
