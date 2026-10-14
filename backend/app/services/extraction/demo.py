import json
import re
import time
from datetime import date
from decimal import Decimal
from pathlib import Path

from app.schemas.invoice import InvoiceData, LineItem
from app.services.extraction.base import ExtractionProvider, ExtractionResult

FIXTURES_DIR = Path(__file__).resolve().parents[3] / "evaluation" / "fixtures" / "ground_truth"


class DemoExtractionProvider(ExtractionProvider):
    """Deterministic extractor for local demo — not an LLM."""

    def extract(self, document_text: str, filename: str | None = None) -> ExtractionResult:
        started = time.perf_counter()
        invoice = self._extract_from_text(document_text, filename)
        duration_ms = int((time.perf_counter() - started) * 1000)
        confidence = {key: "demo_heuristic" for key in invoice.model_dump().keys()}
        confidence["line_items"] = "demo_heuristic"
        return ExtractionResult(
            invoice=invoice,
            provider_name="demo",
            model_id="deterministic-v1",
            field_confidence=confidence,
            duration_ms=duration_ms,
        )

    def _extract_from_text(self, document_text: str, filename: str | None) -> InvoiceData:
        marker = self._find_marker(document_text)
        if marker:
            fixture_path = FIXTURES_DIR / f"{marker}.json"
            if fixture_path.exists():
                payload = json.loads(fixture_path.read_text(encoding="utf-8"))
                return InvoiceData.model_validate(payload)

        parsed = self._parse_labeled_text(document_text)
        if parsed:
            return parsed

        raise ValueError(
            "Demo extractor could not map this document. Upload a bundled synthetic invoice or switch to LLM mode."
        )

    def _find_marker(self, text: str) -> str | None:
        match = re.search(r"DOCFLOW-FIXTURE-ID:\s*([a-z0-9_\-]+)", text, re.IGNORECASE)
        if match:
            return match.group(1).lower()
        return None

    def _parse_labeled_text(self, text: str) -> InvoiceData | None:
        def field(label: str) -> str | None:
            pattern = rf"{re.escape(label)}:\s*(.+)"
            match = re.search(pattern, text, re.IGNORECASE)
            return match.group(1).strip() if match else None

        supplier = field("Supplier")
        invoice_number = field("Invoice Number")
        invoice_date = field("Invoice Date")
        if not (supplier and invoice_number and invoice_date):
            return None

        line_items: list[LineItem] = []
        for line in text.splitlines():
            item_match = re.match(
                r"LINE:\s*(.+?)\s*\|\s*qty\s*([\d.]+)\s*\|\s*unit\s*([\d.]+)\s*\|\s*total\s*([\d.]+)",
                line.strip(),
                re.IGNORECASE,
            )
            if item_match:
                line_items.append(
                    LineItem(
                        description=item_match.group(1).strip(),
                        quantity=Decimal(item_match.group(2)),
                        unit_price=Decimal(item_match.group(3)),
                        line_total=Decimal(item_match.group(4)),
                    )
                )

        if not line_items:
            return None

        subtotal = field("Subtotal")
        tax = field("Tax")
        total = field("Total")
        currency = field("Currency") or "USD"
        if not (subtotal and tax and total):
            return None

        due = field("Due Date")
        po = field("PO Reference")
        tax_id = field("Tax ID")

        return InvoiceData(
            supplier_name=supplier,
            supplier_tax_id=tax_id,
            invoice_number=invoice_number,
            invoice_date=date.fromisoformat(invoice_date),
            due_date=date.fromisoformat(due) if due else None,
            currency=currency,
            subtotal=Decimal(subtotal),
            tax_amount=Decimal(tax),
            total_amount=Decimal(total),
            purchase_order_reference=po,
            line_items=line_items,
        )
