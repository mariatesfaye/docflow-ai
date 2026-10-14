import csv
import io
import json

from app.schemas.invoice import InvoiceData


def export_json(invoice: InvoiceData) -> str:
    return json.dumps(invoice.model_dump(mode="json"), indent=2)


def export_csv(invoice: InvoiceData) -> str:
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow(
        [
            "supplier_name",
            "supplier_tax_id",
            "invoice_number",
            "invoice_date",
            "due_date",
            "currency",
            "subtotal",
            "tax_amount",
            "total_amount",
            "purchase_order_reference",
            "line_description",
            "line_quantity",
            "line_unit_price",
            "line_total",
        ]
    )
    for item in invoice.line_items:
        writer.writerow(
            [
                invoice.supplier_name,
                invoice.supplier_tax_id or "",
                invoice.invoice_number,
                invoice.invoice_date.isoformat(),
                invoice.due_date.isoformat() if invoice.due_date else "",
                invoice.currency,
                str(invoice.subtotal),
                str(invoice.tax_amount),
                str(invoice.total_amount),
                invoice.purchase_order_reference or "",
                item.description,
                str(item.quantity),
                str(item.unit_price),
                str(item.line_total),
            ]
        )
    return buffer.getvalue()
