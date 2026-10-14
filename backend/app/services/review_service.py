import uuid
from datetime import UTC, datetime

from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.document import Document, ProcessingStatus
from app.models.review import Review, ReviewStatus
from app.schemas.invoice import InvoiceData
from app.services.validation_engine import validate_invoice

ALLOWED_TRANSITIONS: dict[ReviewStatus, set[ReviewStatus]] = {
    ReviewStatus.pending: {ReviewStatus.in_review, ReviewStatus.approved, ReviewStatus.rejected},
    ReviewStatus.in_review: {ReviewStatus.in_review, ReviewStatus.approved, ReviewStatus.rejected},
    ReviewStatus.approved: {ReviewStatus.in_review, ReviewStatus.rejected},
    ReviewStatus.rejected: {ReviewStatus.in_review},
}


class ReviewService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def update_review(self, document_id: uuid.UUID, corrected: InvoiceData, mark_in_review: bool) -> Review:
        document, review = self._get_document_and_review(document_id)
        if document.status != ProcessingStatus.completed:
            raise ValueError("Document must be processed before review.")

        original = self._original_extraction_data(document)
        changes = self._diff_fields(original, corrected)
        review.corrected_data = corrected.model_dump(mode="json")
        review.field_changes = changes
        if mark_in_review:
            self._transition(review, ReviewStatus.in_review)
        review.updated_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(review)
        return review

    def approve(self, document_id: uuid.UUID) -> Review:
        document, review = self._get_document_and_review(document_id)
        data = review.corrected_data
        if not data and document.extractions:
            latest = sorted(document.extractions, key=lambda e: e.created_at, reverse=True)[0]
            data = latest.extracted_data
        if not data:
            raise ValueError("No data available to approve.")

        invoice = InvoiceData.model_validate(data)
        errors = [issue for issue in validate_invoice(invoice) if issue.severity.value == "error"]
        if errors:
            raise ValueError("Cannot approve while validation errors remain.")

        self._transition(review, ReviewStatus.approved)
        review.reviewed_at = datetime.now(UTC)
        review.rejection_reason = None
        self.db.commit()
        self.db.refresh(review)
        return review

    def reject(self, document_id: uuid.UUID, reason: str | None) -> Review:
        _, review = self._get_document_and_review(document_id)
        self._transition(review, ReviewStatus.rejected)
        review.rejection_reason = reason
        review.reviewed_at = datetime.now(UTC)
        self.db.commit()
        self.db.refresh(review)
        return review

    def _get_document_and_review(self, document_id: uuid.UUID) -> tuple[Document, Review]:
        document = self.db.scalar(
            select(Document)
            .where(Document.id == document_id)
            .options(selectinload(Document.extractions), selectinload(Document.review))
        )
        if not document or not document.review:
            raise LookupError("Document not found.")
        return document, document.review

    def _original_extraction_data(self, document: Document) -> dict:
        if not document.extractions:
            raise ValueError("No extraction available.")
        latest = sorted(document.extractions, key=lambda e: e.created_at, reverse=True)[0]
        return latest.extracted_data

    def _transition(self, review: Review, new_status: ReviewStatus) -> None:
        allowed = ALLOWED_TRANSITIONS.get(review.status, set())
        if new_status not in allowed and review.status != new_status:
            raise ValueError(f"Invalid review transition from {review.status.value} to {new_status.value}.")
        review.status = new_status

    def _diff_fields(self, before: dict, after: InvoiceData) -> list[dict]:
        after_dict = after.model_dump(mode="json")
        changes: list[dict] = []
        for key, after_value in after_dict.items():
            before_value = before.get(key)
            if before_value != after_value:
                changes.append({"field": key, "before": before_value, "after": after_value})
        return changes
