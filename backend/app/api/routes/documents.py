import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse, PlainTextResponse
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.mappers import to_document_detail, to_extraction_summary, to_review_summary
from app.config import Settings, get_settings
from app.db.session import get_db
from app.models.document import Document
from app.schemas.document import (
    DashboardStats,
    DocumentCreateResponse,
    DocumentDetail,
    DocumentListResponse,
    RejectRequest,
    ReviewSummary,
    ReviewUpdateRequest,
)
from app.services.document_service import DocumentService
from app.services.export_service import export_csv, export_json
from app.services.review_service import ReviewService

router = APIRouter(prefix="/documents", tags=["documents"])


def _service(db: Session, settings: Settings) -> DocumentService:
    return DocumentService(db, settings)


@router.post("", response_model=DocumentCreateResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> DocumentCreateResponse:
    service = _service(db, settings)
    try:
        document = await service.create_document(file)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return DocumentCreateResponse(
        id=document.id,
        original_filename=document.original_filename,
        status=document.status,
        document_type=document.document_type,
        uploaded_at=document.uploaded_at,
    )


@router.get("", response_model=DocumentListResponse)
def list_documents(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    search: str | None = None,
    status: str | None = None,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> DocumentListResponse:
    service = _service(db, settings)
    items, total = service.list_documents(page=page, page_size=page_size, search=search, status=status)
    return DocumentListResponse(items=items, total=total, page=page, page_size=page_size)


@router.get("/stats/dashboard", response_model=DashboardStats)
def dashboard_stats(
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> DashboardStats:
    return _service(db, settings).dashboard_stats()


@router.get("/{document_id}", response_model=DocumentDetail)
def get_document(document_id: uuid.UUID, db: Session = Depends(get_db)) -> DocumentDetail:
    document = db.scalar(
        select(Document)
        .where(Document.id == document_id)
        .options(selectinload(Document.extractions), selectinload(Document.review))
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    return to_document_detail(document)


@router.get("/{document_id}/file")
def get_document_file(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> FileResponse:
    service = _service(db, settings)
    try:
        path = service.get_file_path(document_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    meta = db.scalar(select(Document).where(Document.id == document_id))
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(
        path,
        media_type="application/pdf",
        filename=meta.original_filename if meta else path.name,
        content_disposition_type="inline",
    )


@router.post("/{document_id}/process", response_model=DocumentDetail)
def process_document(
    document_id: uuid.UUID,
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> DocumentDetail:
    service = _service(db, settings)
    try:
        document = service.process_document(document_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        document = db.scalar(
            select(Document)
            .where(Document.id == document_id)
            .options(selectinload(Document.extractions), selectinload(Document.review))
        )
        if document:
            return to_document_detail(document)
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return to_document_detail(document)


@router.get("/{document_id}/extractions")
def list_extractions(document_id: uuid.UUID, db: Session = Depends(get_db)) -> list[dict]:
    document = db.scalar(
        select(Document).where(Document.id == document_id).options(selectinload(Document.extractions))
    )
    if not document:
        raise HTTPException(status_code=404, detail="Document not found.")
    extractions = sorted(document.extractions, key=lambda e: e.created_at, reverse=True)
    return [to_extraction_summary(item).model_dump(mode="json") for item in extractions]


@router.put("/{document_id}/review", response_model=ReviewSummary)
def update_review(
    document_id: uuid.UUID,
    payload: ReviewUpdateRequest,
    db: Session = Depends(get_db),
) -> ReviewSummary:
    service = ReviewService(db)
    try:
        review = service.update_review(document_id, payload.corrected_data, payload.mark_in_review)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    summary = to_review_summary(review)
    assert summary is not None
    return summary


@router.post("/{document_id}/approve", response_model=ReviewSummary)
def approve_document(document_id: uuid.UUID, db: Session = Depends(get_db)) -> ReviewSummary:
    service = ReviewService(db)
    try:
        review = service.approve(document_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    summary = to_review_summary(review)
    assert summary is not None
    return summary


@router.post("/{document_id}/reject", response_model=ReviewSummary)
def reject_document(
    document_id: uuid.UUID,
    payload: RejectRequest,
    db: Session = Depends(get_db),
) -> ReviewSummary:
    service = ReviewService(db)
    try:
        review = service.reject(document_id, payload.reason)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    summary = to_review_summary(review)
    assert summary is not None
    return summary


@router.get("/{document_id}/export")
def export_document(
    document_id: uuid.UUID,
    format: str = Query("json", pattern="^(json|csv)$"),
    db: Session = Depends(get_db),
    settings: Settings = Depends(get_settings),
) -> PlainTextResponse:
    service = _service(db, settings)
    try:
        invoice = service.get_export_invoice(document_id)
    except LookupError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    if format == "csv":
        content = export_csv(invoice)
        media_type = "text/csv"
    else:
        content = export_json(invoice)
        media_type = "application/json"
    return PlainTextResponse(content, media_type=media_type)
