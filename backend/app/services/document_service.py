import uuid
from datetime import UTC, datetime
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.config import Settings
from app.models.document import Document, ProcessingStatus
from app.models.extraction import Extraction
from app.models.review import Review, ReviewStatus
from app.schemas.document import DashboardStats, DocumentListItem
from app.schemas.invoice import InvoiceData
from app.services.extraction.factory import get_extraction_provider
from app.services.pdf_text import extract_document_text
from app.services.storage import (
    ensure_storage_dirs,
    resolve_upload_path,
    sha256_file,
    unique_storage_name,
    validate_pdf_content,
)
from app.services.validation_engine import validate_invoice


class DocumentService:
    def __init__(self, db: Session, settings: Settings) -> None:
        self.db = db
        self.settings = settings
        ensure_storage_dirs(settings)

    async def create_document(self, upload: UploadFile) -> Document:
        if not upload.filename:
            raise ValueError("Filename is required.")
        if upload.content_type not in self.settings.allowed_mime_types:
            raise ValueError("Only PDF uploads are supported.")

        raw = await upload.read()
        if not raw:
            raise ValueError("Uploaded file is empty.")
        if len(raw) > self.settings.max_upload_bytes:
            raise ValueError("File exceeds maximum upload size.")

        storage_name = unique_storage_name(upload.filename)
        dest = self.settings.upload_dir / storage_name
        dest.write_bytes(raw)

        try:
            validate_pdf_content(dest)
        except ValueError:
            dest.unlink(missing_ok=True)
            raise

        checksum = sha256_file(dest)
        document = Document(
            original_filename=upload.filename,
            storage_path=storage_name,
            mime_type=upload.content_type or "application/pdf",
            file_size=len(raw),
            checksum_sha256=checksum,
            status=ProcessingStatus.uploaded,
        )
        self.db.add(document)
        self.db.flush()
        self.db.add(Review(document_id=document.id, status=ReviewStatus.pending))
        self.db.commit()
        self.db.refresh(document)
        return document

    def process_document(self, document_id: uuid.UUID) -> Document:
        document = self._get_document(document_id)
        if document.status == ProcessingStatus.processing:
            raise ValueError("Document is already processing.")

        document.status = ProcessingStatus.processing
        document.processing_started_at = datetime.now(UTC)
        document.processing_ended_at = None
        document.error_message = None
        self.db.commit()

        try:
            pdf_path = resolve_upload_path(self.settings, document.storage_path)
            text, _used_ocr = extract_document_text(pdf_path, self.settings)
            if not text.strip():
                raise ValueError("Could not extract text from PDF (OCR may be unavailable).")

            text_name = f"{document.id.hex}.txt"
            text_path = self.settings.text_dir / text_name
            text_path.write_text(text, encoding="utf-8")

            provider = get_extraction_provider(self.settings)
            result = provider.extract(text, filename=document.original_filename)
            validation = validate_invoice(result.invoice)

            extraction = Extraction(
                document_id=document.id,
                provider_name=result.provider_name,
                model_id=result.model_id,
                extracted_data=result.invoice.model_dump(mode="json"),
                field_confidence=result.field_confidence,
                raw_text_path=text_name,
                validation_results=[issue.model_dump(mode="json") for issue in validation],
                duration_ms=result.duration_ms,
            )
            self.db.add(extraction)
            self.db.flush()

            review = document.review
            if review:
                review.extraction_id = extraction.id
                if review.status == ReviewStatus.pending:
                    review.status = ReviewStatus.in_review

            document.status = ProcessingStatus.completed
            document.processing_ended_at = datetime.now(UTC)
            self.db.commit()
        except Exception as exc:
            document.status = ProcessingStatus.failed
            document.processing_ended_at = datetime.now(UTC)
            document.error_message = str(exc)
            self.db.commit()
            raise ValueError(str(exc)) from exc

        self.db.refresh(document)
        return document

    def list_documents(
        self, page: int = 1, page_size: int = 20, search: str | None = None, status: str | None = None
    ) -> tuple[list[DocumentListItem], int]:
        query = select(Document).options(selectinload(Document.review), selectinload(Document.extractions))
        if status:
            query = query.where(Document.status == ProcessingStatus(status))
        if search:
            like = f"%{search.lower()}%"
            query = query.where(func.lower(Document.original_filename).like(like))

        count_query = select(func.count(Document.id))
        if status:
            count_query = count_query.where(Document.status == ProcessingStatus(status))
        if search:
            like = f"%{search.lower()}%"
            count_query = count_query.where(func.lower(Document.original_filename).like(like))
        total = self.db.scalar(count_query) or 0
        rows = self.db.scalars(
            query.order_by(Document.uploaded_at.desc()).offset((page - 1) * page_size).limit(page_size)
        ).all()

        items: list[DocumentListItem] = []
        for doc in rows:
            supplier = None
            invoice_number = None
            if doc.extractions:
                latest = sorted(doc.extractions, key=lambda e: e.created_at, reverse=True)[0]
                supplier = latest.extracted_data.get("supplier_name")
                invoice_number = latest.extracted_data.get("invoice_number")
            items.append(
                DocumentListItem(
                    id=doc.id,
                    original_filename=doc.original_filename,
                    status=doc.status,
                    uploaded_at=doc.uploaded_at,
                    supplier_name=supplier,
                    invoice_number=invoice_number,
                    review_status=doc.review.status if doc.review else None,
                )
            )
        return items, total

    def dashboard_stats(self) -> DashboardStats:
        total = self.db.scalar(select(func.count()).select_from(Document)) or 0
        processed = (
            self.db.scalar(select(func.count()).select_from(Document).where(Document.status == ProcessingStatus.completed))
            or 0
        )
        failed = (
            self.db.scalar(select(func.count()).select_from(Document).where(Document.status == ProcessingStatus.failed))
            or 0
        )
        awaiting = (
            self.db.scalar(
                select(func.count())
                .select_from(Review)
                .join(Document)
                .where(
                    Review.status.in_([ReviewStatus.pending, ReviewStatus.in_review]),
                    Document.status == ProcessingStatus.completed,
                )
            )
            or 0
        )
        avg_ms = self.db.scalar(select(func.avg(Extraction.duration_ms)))
        error_extractions = self.db.scalars(select(Extraction)).all()
        error_rate = None
        if error_extractions:
            with_errors = sum(
                1
                for ext in error_extractions
                if any(item.get("severity") == "error" for item in ext.validation_results)
            )
            error_rate = with_errors / len(error_extractions)

        return DashboardStats(
            total_documents=total,
            processed_documents=processed,
            awaiting_review=awaiting,
            failed_documents=failed,
            average_processing_ms=float(avg_ms) if avg_ms is not None else None,
            validation_error_rate=error_rate,
        )

    def get_file_path(self, document_id: uuid.UUID) -> Path:
        document = self._get_document(document_id)
        return resolve_upload_path(self.settings, document.storage_path)

    def _get_document(self, document_id: uuid.UUID) -> Document:
        document = self.db.scalar(
            select(Document)
            .where(Document.id == document_id)
            .options(
                selectinload(Document.extractions),
                selectinload(Document.review),
            )
        )
        if not document:
            raise LookupError("Document not found.")
        return document

    def get_export_invoice(self, document_id: uuid.UUID) -> InvoiceData:
        document = self._get_document(document_id)
        if document.review and document.review.corrected_data:
            return InvoiceData.model_validate(document.review.corrected_data)
        if not document.extractions:
            raise ValueError("No extraction available for export.")
        latest = sorted(document.extractions, key=lambda e: e.created_at, reverse=True)[0]
        return InvoiceData.model_validate(latest.extracted_data)
