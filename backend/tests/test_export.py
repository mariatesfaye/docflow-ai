from datetime import date
from decimal import Decimal

from app.schemas.invoice import InvoiceData, LineItem
from app.services.export_service import export_csv, export_json


def test_export_json_and_csv():
    invoice = InvoiceData(
        supplier_name="Acme",
        invoice_number="INV-1",
        invoice_date=date(2024, 1, 1),
        currency="USD",
        subtotal=Decimal("10.00"),
        tax_amount=Decimal("1.00"),
        total_amount=Decimal("11.00"),
        line_items=[
            LineItem(description="Paper", quantity=Decimal("1"), unit_price=Decimal("10.00"), line_total=Decimal("10.00"))
        ],
    )
    json_payload = export_json(invoice)
    assert '"invoice_number": "INV-1"' in json_payload
    csv_payload = export_csv(invoice)
    assert "supplier_name" in csv_payload.splitlines()[0]
    assert "Paper" in csv_payload
