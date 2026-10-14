from pathlib import Path

import pytest

FIXTURE_PDF = Path(__file__).resolve().parents[1] / "evaluation" / "fixtures" / "pdfs" / "acme_001.pdf"


@pytest.mark.skipif(not FIXTURE_PDF.exists(), reason="Fixtures not generated")
def test_upload_process_review_approve_export(client):
    with FIXTURE_PDF.open("rb") as handle:
        upload = client.post("/api/documents", files={"file": ("acme_001.pdf", handle, "application/pdf")})
    assert upload.status_code == 201
    document_id = upload.json()["id"]

    processed = client.post(f"/api/documents/{document_id}/process")
    assert processed.status_code == 200
    body = processed.json()
    assert body["status"] == "completed"
    assert body["latest_extraction"]["provider_name"] == "demo"

    invoice = body["latest_extraction"]["extracted_data"]
    invoice["supplier_name"] = "Acme Office Supplies Ltd. (Reviewed)"
    review = client.put(f"/api/documents/{document_id}/review", json={"corrected_data": invoice})
    assert review.status_code == 200

    approved = client.post(f"/api/documents/{document_id}/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    exported = client.get(f"/api/documents/{document_id}/export?format=json")
    assert exported.status_code == 200
    assert "Acme Office Supplies Ltd. (Reviewed)" in exported.text
