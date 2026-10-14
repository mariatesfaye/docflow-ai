from __future__ import annotations

import json
from datetime import date
from decimal import Decimal
from pathlib import Path

from app.schemas.invoice import InvoiceData
from app.services.extraction.demo import DemoExtractionProvider
from app.services.validation_engine import validate_invoice

FIXTURES_DIR = Path(__file__).resolve().parents[2] / "evaluation" / "fixtures"
GROUND_TRUTH_DIR = FIXTURES_DIR / "ground_truth"
REPORT_PATH = FIXTURES_DIR / "reports" / "latest_evaluation.json"

NUMERIC_TOLERANCE = Decimal("0.01")


def normalize_date(value: str | date | None) -> str | None:
    if value is None:
        return None
    if isinstance(value, date):
        return value.isoformat()
    return date.fromisoformat(str(value)).isoformat()


def numeric_match(expected: Decimal, actual: Decimal) -> bool:
    return abs(expected - actual) <= NUMERIC_TOLERANCE


def compare_invoices(expected: InvoiceData, actual: InvoiceData) -> dict:
    field_results: dict[str, bool] = {}
    expected_dump = expected.model_dump()
    actual_dump = actual.model_dump()

    for field in [
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
    ]:
        exp = expected_dump[field]
        act = actual_dump[field]
        if field in {"invoice_date", "due_date"}:
            field_results[field] = normalize_date(exp) == normalize_date(act)
        elif field in {"subtotal", "tax_amount", "total_amount"}:
            field_results[field] = numeric_match(Decimal(str(exp)), Decimal(str(act)))
        else:
            field_results[field] = (exp or None) == (act or None)

    line_ok = len(expected.line_items) == len(actual.line_items)
    if line_ok:
        for idx, (exp_item, act_item) in enumerate(zip(expected.line_items, actual.line_items, strict=True)):
            line_ok = line_ok and exp_item.description == act_item.description
            line_ok = line_ok and numeric_match(exp_item.quantity, act_item.quantity)
            line_ok = line_ok and numeric_match(exp_item.unit_price, act_item.unit_price)
            line_ok = line_ok and numeric_match(exp_item.line_total, act_item.line_total)
    field_results["line_items"] = line_ok

    exact_matches = sum(1 for key, ok in field_results.items() if ok and key not in {"invoice_date", "due_date", "subtotal", "tax_amount", "total_amount", "line_items"})
    normalized_matches = sum(1 for ok in field_results.values() if ok)
    total_fields = len(field_results)

    return {
        "field_results": field_results,
        "exact_match_rate": exact_matches / max(total_fields - 4, 1),
        "normalized_match_rate": normalized_matches / total_fields,
    }


def run_fixture_evaluation() -> dict:
    provider = DemoExtractionProvider()
    results: list[dict] = []
    for truth_path in sorted(GROUND_TRUTH_DIR.glob("*.json")):
        fixture_id = truth_path.stem
        pdf_path = FIXTURES_DIR / "pdfs" / f"{fixture_id}.pdf"
        text_path = FIXTURES_DIR / "text" / f"{fixture_id}.txt"
        text = text_path.read_text(encoding="utf-8") if text_path.exists() else ""
        if not text and pdf_path.exists():
            import fitz

            with fitz.open(pdf_path) as doc:
                text = doc[0].get_text("text")

        expected = InvoiceData.model_validate(json.loads(truth_path.read_text(encoding="utf-8")))
        extraction = provider.extract(text, filename=f"{fixture_id}.pdf")
        comparison = compare_invoices(expected, extraction.invoice)
        validation = validate_invoice(extraction.invoice)
        results.append(
            {
                "fixture_id": fixture_id,
                "provider": extraction.provider_name,
                "duration_ms": extraction.duration_ms,
                "comparison": comparison,
                "validation_issues": [issue.model_dump() for issue in validation],
            }
        )

    if not results:
        return {
            "document_count": 0,
            "field_exact_match_accuracy": None,
            "normalized_field_accuracy": None,
            "per_field_accuracy": {},
            "validation_failure_rate": None,
            "average_processing_ms": None,
            "notes": "No fixtures found.",
        }

    per_field: dict[str, list[bool]] = {}
    for item in results:
        for field, ok in item["comparison"]["field_results"].items():
            per_field.setdefault(field, []).append(ok)

    per_field_accuracy = {field: sum(vals) / len(vals) for field, vals in per_field.items()}
    validation_failures = sum(
        1 for item in results if any(v.get("severity") == "error" for v in item["validation_issues"])
    )

    report = {
        "document_count": len(results),
        "field_exact_match_accuracy": sum(item["comparison"]["exact_match_rate"] for item in results) / len(results),
        "normalized_field_accuracy": sum(item["comparison"]["normalized_match_rate"] for item in results) / len(results),
        "per_field_accuracy": per_field_accuracy,
        "validation_failure_rate": validation_failures / len(results),
        "average_processing_ms": sum(item["duration_ms"] or 0 for item in results) / len(results),
        "metric_definitions": {
            "field_exact_match_accuracy": "Share of string/categorical fields with exact matches (excludes normalized dates/amounts).",
            "normalized_field_accuracy": "Share of all tracked fields matching with date normalization and numeric tolerance.",
            "validation_failure_rate": "Share of fixtures whose extracted data triggers at least one validation error.",
        },
        "limitations": "Ten synthetic fixtures are a portfolio benchmark, not evidence of real-world LLM accuracy.",
        "results": results,
    }
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    REPORT_PATH.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def load_evaluation_summary() -> dict:
    if REPORT_PATH.exists():
        return json.loads(REPORT_PATH.read_text(encoding="utf-8"))
    return run_fixture_evaluation()
