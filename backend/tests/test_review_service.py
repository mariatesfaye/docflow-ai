from datetime import date
from decimal import Decimal

from app.schemas.invoice import InvoiceData, LineItem
from app.services.validation_engine import validate_invoice


def test_approve_blocked_on_validation_errors():
    invoice = InvoiceData(
        supplier_name="Acme",
        invoice_number="1",
        invoice_date=date(2024, 1, 1),
        currency="USD",
        subtotal=Decimal("100"),
        tax_amount=Decimal("10"),
        total_amount=Decimal("50"),
        line_items=[
            LineItem(description="Item", quantity=Decimal("2"), unit_price=Decimal("50"), line_total=Decimal("90"))
        ],
    )
    errors = [issue for issue in validate_invoice(invoice) if issue.severity.value == "error"]
    assert errors
