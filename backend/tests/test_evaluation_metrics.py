from datetime import date
from decimal import Decimal

from app.evaluation.metrics import compare_invoices, numeric_match
from app.schemas.invoice import InvoiceData, LineItem


def test_numeric_match_tolerance():
    assert numeric_match(Decimal("1.00"), Decimal("1.009"))


def test_compare_invoices_detects_differences():
    base = InvoiceData(
        supplier_name="A",
        invoice_number="1",
        invoice_date=date(2024, 1, 1),
        currency="USD",
        subtotal=Decimal("10"),
        tax_amount=Decimal("1"),
        total_amount=Decimal("11"),
        line_items=[LineItem(description="x", quantity=Decimal("1"), unit_price=Decimal("10"), line_total=Decimal("10"))],
    )
    changed = base.model_copy(update={"supplier_name": "B"})
    result = compare_invoices(base, changed)
    assert result["field_results"]["supplier_name"] is False
