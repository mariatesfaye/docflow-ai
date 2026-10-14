from datetime import date
from decimal import Decimal

from app.schemas.invoice import InvoiceData, LineItem
from app.services.validation_engine import validate_invoice


def sample_invoice(**overrides) -> InvoiceData:
    payload = {
        "supplier_name": "Acme",
        "invoice_number": "INV-1",
        "invoice_date": date(2024, 1, 1),
        "currency": "USD",
        "subtotal": Decimal("100.00"),
        "tax_amount": Decimal("10.00"),
        "total_amount": Decimal("110.00"),
        "line_items": [
            LineItem(description="Item", quantity=Decimal("2"), unit_price=Decimal("50.00"), line_total=Decimal("100.00"))
        ],
    }
    payload.update(overrides)
    return InvoiceData(**payload)


def test_line_total_mismatch_is_error():
    invoice = sample_invoice(
        line_items=[
            LineItem(description="Item", quantity=Decimal("2"), unit_price=Decimal("50.00"), line_total=Decimal("90.00"))
        ]
    )
    issues = validate_invoice(invoice)
    assert any(issue.rule_id == "line_total_mismatch" and issue.severity.value == "error" for issue in issues)


def test_total_mismatch_is_warning():
    invoice = sample_invoice(total_amount=Decimal("120.00"))
    issues = validate_invoice(invoice)
    assert any(issue.rule_id == "total_mismatch" and issue.severity.value == "warning" for issue in issues)
