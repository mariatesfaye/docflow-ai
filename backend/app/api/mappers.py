from app.models.document import Document
from app.models.extraction import Extraction
from app.models.review import Review
from app.schemas.document import DocumentDetail, ExtractionSummary, ReviewSummary
from app.schemas.invoice import InvoiceData
from app.schemas.validation import ValidationIssue


def to_extraction_summary(extraction: Extraction) -> ExtractionSummary:
    return ExtractionSummary(
        id=extraction.id,
        provider_name=extraction.provider_name,
        model_id=extraction.model_id,
        extracted_data=InvoiceData.model_validate(extraction.extracted_data),
        field_confidence=extraction.field_confidence,
        validation_results=[ValidationIssue.model_validate(item) for item in extraction.validation_results],
        duration_ms=extraction.duration_ms,
        created_at=extraction.created_at,
    )


def to_review_summary(review: Review | None) -> ReviewSummary | None:
    if not review:
        return None
    corrected = InvoiceData.model_validate(review.corrected_data) if review.corrected_data else None
    return ReviewSummary(
        id=review.id,
        status=review.status,
        corrected_data=corrected,
        field_changes=review.field_changes,
        rejection_reason=review.rejection_reason,
        reviewed_at=review.reviewed_at,
        updated_at=review.updated_at,
    )


def to_document_detail(document: Document) -> DocumentDetail:
    latest = None
    if document.extractions:
        latest_ext = sorted(document.extractions, key=lambda e: e.created_at, reverse=True)[0]
        latest = to_extraction_summary(latest_ext)
    return DocumentDetail(
        id=document.id,
        original_filename=document.original_filename,
        status=document.status,
        document_type=document.document_type,
        mime_type=document.mime_type,
        file_size=document.file_size,
        uploaded_at=document.uploaded_at,
        processing_started_at=document.processing_started_at,
        processing_ended_at=document.processing_ended_at,
        error_message=document.error_message,
        latest_extraction=latest,
        review=to_review_summary(document.review),
    )
