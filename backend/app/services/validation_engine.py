from decimal import Decimal

from app.config import get_settings
from app.schemas.invoice import InvoiceData
from app.schemas.validation import ValidationIssue, ValidationSeverity


def _dec(value: Decimal | str | float | int) -> Decimal:
    return value if isinstance(value, Decimal) else Decimal(str(value))


def validate_invoice(data: InvoiceData) -> list[ValidationIssue]:
    settings = get_settings()
    tolerance = Decimal(settings.rounding_tolerance)
    issues: list[ValidationIssue] = []

    if data.due_date and data.due_date < data.invoice_date:
        issues.append(
            ValidationIssue(
                rule_id="date_due_before_invoice",
                severity=ValidationSeverity.error,
                message="Due date cannot be before invoice date.",
                field="due_date",
            )
        )

    line_sum = Decimal("0")
    for index, item in enumerate(data.line_items):
        expected = (_dec(item.quantity) * _dec(item.unit_price)).quantize(Decimal("0.01"))
        actual = _dec(item.line_total).quantize(Decimal("0.01"))
        if abs(expected - actual) > tolerance:
            issues.append(
                ValidationIssue(
                    rule_id="line_total_mismatch",
                    severity=ValidationSeverity.error,
                    message=f"Line {index + 1} total does not match quantity × unit price.",
                    field=f"line_items[{index}].line_total",
                )
            )
        if _dec(item.quantity) < 0 or _dec(item.unit_price) < 0:
            issues.append(
                ValidationIssue(
                    rule_id="negative_line_value",
                    severity=ValidationSeverity.error,
                    message=f"Line {index + 1} has negative quantity or unit price.",
                    field=f"line_items[{index}]",
                )
            )
        line_sum += actual

    subtotal = _dec(data.subtotal).quantize(Decimal("0.01"))
    if abs(line_sum - subtotal) > tolerance:
        issues.append(
            ValidationIssue(
                rule_id="subtotal_mismatch",
                severity=ValidationSeverity.warning,
                message="Subtotal differs from the sum of line item totals beyond rounding tolerance.",
                field="subtotal",
            )
        )

    expected_total = (subtotal + _dec(data.tax_amount)).quantize(Decimal("0.01"))
    total = _dec(data.total_amount).quantize(Decimal("0.01"))
    if abs(expected_total - total) > tolerance:
        issues.append(
            ValidationIssue(
                rule_id="total_mismatch",
                severity=ValidationSeverity.warning,
                message="Total amount differs from subtotal + tax beyond rounding tolerance.",
                field="total_amount",
            )
        )

    if _dec(data.tax_amount) < 0:
        issues.append(
            ValidationIssue(
                rule_id="negative_tax",
                severity=ValidationSeverity.error,
                message="Tax amount cannot be negative.",
                field="tax_amount",
            )
        )

    if not data.currency.isalpha():
        issues.append(
            ValidationIssue(
                rule_id="invalid_currency",
                severity=ValidationSeverity.error,
                message="Currency must be a 3-letter code.",
                field="currency",
            )
        )

    return issues
