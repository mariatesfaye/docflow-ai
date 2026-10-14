from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.document import DocumentType, ProcessingStatus
from app.models.review import ReviewStatus
from app.schemas.invoice import InvoiceData
from app.schemas.validation import ValidationIssue


class DocumentCreateResponse(BaseModel):
    id: UUID
    original_filename: str
    status: ProcessingStatus
    document_type: DocumentType
    uploaded_at: datetime


class ExtractionSummary(BaseModel):
    id: UUID
    provider_name: str
    model_id: str | None
    extracted_data: InvoiceData
    field_confidence: dict[str, str | float | None] | None
    validation_results: list[ValidationIssue]
    duration_ms: int | None
    created_at: datetime


class ReviewSummary(BaseModel):
    id: UUID
    status: ReviewStatus
    corrected_data: InvoiceData | None
    field_changes: list[dict]
    rejection_reason: str | None
    reviewed_at: datetime | None
    updated_at: datetime


class DocumentDetail(BaseModel):
    id: UUID
    original_filename: str
    status: ProcessingStatus
    document_type: DocumentType
    mime_type: str
    file_size: int
    uploaded_at: datetime
    processing_started_at: datetime | None
    processing_ended_at: datetime | None
    error_message: str | None
    latest_extraction: ExtractionSummary | None
    review: ReviewSummary | None


class DocumentListItem(BaseModel):
    id: UUID
    original_filename: str
    status: ProcessingStatus
    uploaded_at: datetime
    supplier_name: str | None = None
    invoice_number: str | None = None
    review_status: ReviewStatus | None = None


class DocumentListResponse(BaseModel):
    items: list[DocumentListItem]
    total: int
    page: int
    page_size: int


class DashboardStats(BaseModel):
    total_documents: int
    processed_documents: int
    awaiting_review: int
    failed_documents: int
    average_processing_ms: float | None
    validation_error_rate: float | None


class ReviewUpdateRequest(BaseModel):
    corrected_data: InvoiceData
    mark_in_review: bool = True


class RejectRequest(BaseModel):
    reason: str | None = Field(default=None, max_length=2000)


class ErrorResponse(BaseModel):
    detail: str
