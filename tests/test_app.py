from fastapi.testclient import TestClient
from app.main import app, invoices, payments

client = TestClient(app)


def setup_function():
    invoices.clear()
    payments.clear()


def test_invoice_payment_flow():
    inv_resp = client.post(
        "/invoice", json={"customer": "Alice", "amount": 100.0, "due_date": "2024-01-01"}
    )
    assert inv_resp.status_code == 200
    invoice = inv_resp.json()

    pay_resp = client.post(
        "/payment",
        json={"invoice_id": invoice["id"], "transaction_reference": "TX123"},
    )
    assert pay_resp.status_code == 200

    rev_resp = client.get("/revenue")
    assert rev_resp.json()["revenue"] == 100.0

    report_resp = client.get(
        "/report", params={"start": "2023-12-01", "end": "2024-12-31"}
    )
    assert report_resp.json()["revenue"] == 100.0


def test_stripe_webhook_marks_invoice_paid():
    inv_resp = client.post(
        "/invoice", json={"customer": "Bob", "amount": 50.0, "due_date": "2024-01-10"}
    )
    invoice_id = inv_resp.json()["id"]

    event = {"type": "invoice.paid", "data": {"object": {"id": invoice_id}}}
    wh_resp = client.post("/webhook/stripe", json=event)
    assert wh_resp.status_code == 200

    rev_resp = client.get("/revenue")
    assert rev_resp.json()["revenue"] == 50.0
