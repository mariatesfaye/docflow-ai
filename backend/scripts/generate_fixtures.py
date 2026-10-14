"""Generate synthetic invoice PDF fixtures and ground-truth JSON."""

from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "evaluation" / "fixtures"
PDF_DIR = FIXTURES / "pdfs"
TEXT_DIR = FIXTURES / "text"
TRUTH_DIR = FIXTURES / "ground_truth"


def invoice_to_text(fixture_id: str, data: dict) -> str:
    lines = [
        f"DOCFLOW-FIXTURE-ID: {fixture_id}",
        f"Supplier: {data['supplier_name']}",
        f"Tax ID: {data.get('supplier_tax_id') or ''}",
        f"Invoice Number: {data['invoice_number']}",
        f"Invoice Date: {data['invoice_date']}",
        f"Due Date: {data.get('due_date') or ''}",
        f"Currency: {data['currency']}",
        f"PO Reference: {data.get('purchase_order_reference') or ''}",
        "Line Items:",
    ]
    for item in data["line_items"]:
        lines.append(
            f"LINE: {item['description']} | qty {item['quantity']} | unit {item['unit_price']} | total {item['line_total']}"
        )
    lines.extend(
        [
            f"Subtotal: {data['subtotal']}",
            f"Tax: {data['tax_amount']}",
            f"Total: {data['total_amount']}",
        ]
    )
    return "\n".join(lines)


def write_pdf(path: Path, text: str) -> None:
    doc = fitz.open()
    page = doc.new_page(width=595, height=842)
    page.insert_text((50, 60), text, fontsize=10, fontname="helv")
    doc.save(path)
    doc.close()


def dec(value: str | float) -> str:
    return str(Decimal(str(value)))


FIXTURES_DATA: list[tuple[str, dict]] = [
    (
        "acme_001",
        {
            "supplier_name": "Acme Office Supplies Ltd.",
            "supplier_tax_id": "US-ACME-001",
            "invoice_number": "INV-2024-1001",
            "invoice_date": "2024-03-15",
            "due_date": "2024-04-14",
            "currency": "USD",
            "subtotal": "250.00",
            "tax_amount": "20.00",
            "total_amount": "270.00",
            "purchase_order_reference": "PO-7781",
            "line_items": [
                {"description": "Printer paper (10 reams)", "quantity": "10", "unit_price": "15.00", "line_total": "150.00"},
                {"description": "Ink cartridges", "quantity": "4", "unit_price": "25.00", "line_total": "100.00"},
            ],
        },
    ),
    (
        "nordic_002",
        {
            "supplier_name": "Nordic Cloud Services AB",
            "supplier_tax_id": None,
            "invoice_number": "NC-8842",
            "invoice_date": "2024-05-01",
            "due_date": None,
            "currency": "EUR",
            "subtotal": "1200.50",
            "tax_amount": "300.13",
            "total_amount": "1500.63",
            "purchase_order_reference": None,
            "line_items": [
                {"description": "Platform subscription", "quantity": "1", "unit_price": "999.00", "line_total": "999.00"},
                {"description": "Support hours", "quantity": "3", "unit_price": "67.17", "line_total": "201.50"},
            ],
        },
    ),
    (
        "tokyo_003",
        {
            "supplier_name": "Tokyo Parts Trading Co.",
            "supplier_tax_id": "JP-TPT-993",
            "invoice_number": "TPT-2024-019",
            "invoice_date": "2024-01-20",
            "due_date": "2024-02-19",
            "currency": "JPY",
            "subtotal": "98000",
            "tax_amount": "9800",
            "total_amount": "107800",
            "purchase_order_reference": "PO-JP-12",
            "line_items": [
                {"description": "Sensor module A", "quantity": "2", "unit_price": "30000", "line_total": "60000"},
                {"description": "Sensor module B", "quantity": "1", "unit_price": "38000", "line_total": "38000"},
            ],
        },
    ),
    (
        "london_004",
        {
            "supplier_name": "Thames Consulting LLP",
            "supplier_tax_id": "GB-TC-441",
            "invoice_number": "TC-INV-004",
            "invoice_date": "2024-06-30",
            "due_date": "2024-07-30",
            "currency": "GBP",
            "subtotal": "875.00",
            "tax_amount": "175.00",
            "total_amount": "1050.00",
            "purchase_order_reference": "PO-UK-902",
            "line_items": [
                {"description": "Advisory day rate", "quantity": "3.5", "unit_price": "250.00", "line_total": "875.00"},
            ],
        },
    ),
    (
        "sydney_005",
        {
            "supplier_name": "Harbor Logistics Pty",
            "supplier_tax_id": "AU-HL-22",
            "invoice_number": "HL-5505",
            "invoice_date": "2024-02-10",
            "due_date": "2024-03-12",
            "currency": "AUD",
            "subtotal": "410.00",
            "tax_amount": "41.00",
            "total_amount": "451.00",
            "purchase_order_reference": None,
            "line_items": [
                {"description": "Freight handling", "quantity": "1", "unit_price": "260.00", "line_total": "260.00"},
                {"description": "Storage (days)", "quantity": "5", "unit_price": "30.00", "line_total": "150.00"},
            ],
        },
    ),
    (
        "montreal_006",
        {
            "supplier_name": "Montreal Media Studio",
            "supplier_tax_id": "CA-MMS-88",
            "invoice_number": "MMS-2024-06",
            "invoice_date": "2024-04-05",
            "due_date": "2024-05-05",
            "currency": "CAD",
            "subtotal": "1999.98",
            "tax_amount": "260.00",
            "total_amount": "2259.98",
            "purchase_order_reference": "PO-CA-661",
            "line_items": [
                {"description": "Video editing", "quantity": "12", "unit_price": "120.00", "line_total": "1440.00"},
                {"description": "Color grading", "quantity": "4", "unit_price": "139.995", "line_total": "559.98"},
            ],
        },
    ),
    (
        "berlin_007",
        {
            "supplier_name": "Berlin Hardware GmbH",
            "supplier_tax_id": "DE-BH-007",
            "invoice_number": "BH-77821",
            "invoice_date": "2024-07-01",
            "due_date": "2024-07-31",
            "currency": "EUR",
            "subtotal": "540.00",
            "tax_amount": "102.60",
            "total_amount": "642.60",
            "purchase_order_reference": "PO-DE-19",
            "line_items": [
                {"description": "SSD 1TB", "quantity": "6", "unit_price": "90.00", "line_total": "540.00"},
            ],
        },
    ),
    (
        "mumbai_008",
        {
            "supplier_name": "Mumbai Analytics Pvt Ltd",
            "supplier_tax_id": None,
            "invoice_number": "MA-240808",
            "invoice_date": "2024-08-08",
            "due_date": None,
            "currency": "INR",
            "subtotal": "15000.00",
            "tax_amount": "2700.00",
            "total_amount": "17700.00",
            "purchase_order_reference": "PO-IN-441",
            "line_items": [
                {"description": "Data pipeline setup", "quantity": "1", "unit_price": "10000.00", "line_total": "10000.00"},
                {"description": "Dashboard build", "quantity": "1", "unit_price": "5000.00", "line_total": "5000.00"},
            ],
        },
    ),
    (
        "rounding_009",
        {
            "supplier_name": "Rounding Test Vendor",
            "supplier_tax_id": "RT-009",
            "invoice_number": "ROUND-009",
            "invoice_date": "2024-09-01",
            "due_date": "2024-10-01",
            "currency": "USD",
            "subtotal": "100.02",
            "tax_amount": "8.00",
            "total_amount": "108.01",
            "purchase_order_reference": None,
            "line_items": [
                {"description": "Fractional units", "quantity": "3", "unit_price": "33.34", "line_total": "100.02"},
            ],
        },
    ),
    (
        "mismatch_010",
        {
            "supplier_name": "Inconsistent Totals Inc.",
            "supplier_tax_id": "IT-010",
            "invoice_number": "BAD-010",
            "invoice_date": "2024-10-15",
            "due_date": "2024-11-15",
            "currency": "USD",
            "subtotal": "200.00",
            "tax_amount": "16.00",
            "total_amount": "220.00",
            "purchase_order_reference": "PO-BAD",
            "line_items": [
                {"description": "Widget A", "quantity": "2", "unit_price": "50.00", "line_total": "100.00"},
                {"description": "Widget B", "quantity": "1", "unit_price": "100.00", "line_total": "100.00"},
            ],
        },
    ),
    (
        "sparse_011",
        {
            "supplier_name": "Sparse Fields Co.",
            "supplier_tax_id": None,
            "invoice_number": "SP-011",
            "invoice_date": "2024-11-01",
            "due_date": None,
            "currency": "USD",
            "subtotal": "45.00",
            "tax_amount": "0.00",
            "total_amount": "45.00",
            "purchase_order_reference": None,
            "line_items": [
                {"description": "Minimal service", "quantity": "1", "unit_price": "45.00", "line_total": "45.00"},
            ],
        },
    ),
    (
        "multi_012",
        {
            "supplier_name": "Multi Line Wholesale",
            "supplier_tax_id": "ML-012",
            "invoice_number": "ML-2024-12",
            "invoice_date": "2024-12-01",
            "due_date": "2025-01-01",
            "currency": "USD",
            "subtotal": "742.50",
            "tax_amount": "59.40",
            "total_amount": "801.90",
            "purchase_order_reference": "PO-ML-12",
            "line_items": [
                {"description": "Item 1", "quantity": "5", "unit_price": "40.00", "line_total": "200.00"},
                {"description": "Item 2", "quantity": "2", "unit_price": "75.00", "line_total": "150.00"},
                {"description": "Item 3", "quantity": "3", "unit_price": "60.50", "line_total": "181.50"},
                {"description": "Item 4", "quantity": "1", "unit_price": "211.00", "line_total": "211.00"},
            ],
        },
    ),
]


def main() -> None:
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    TEXT_DIR.mkdir(parents=True, exist_ok=True)
    TRUTH_DIR.mkdir(parents=True, exist_ok=True)

    for fixture_id, payload in FIXTURES_DATA:
        text = invoice_to_text(fixture_id, payload)
        (TEXT_DIR / f"{fixture_id}.txt").write_text(text, encoding="utf-8")
        write_pdf(PDF_DIR / f"{fixture_id}.pdf", text)
        (TRUTH_DIR / f"{fixture_id}.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(f"Generated {len(FIXTURES_DATA)} fixtures in {FIXTURES}")


if __name__ == "__main__":
    main()
