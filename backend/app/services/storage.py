import hashlib
import re
import uuid
from pathlib import Path

import fitz

from app.config import Settings


def ensure_storage_dirs(settings: Settings) -> None:
    settings.upload_dir.mkdir(parents=True, exist_ok=True)
    settings.text_dir.mkdir(parents=True, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    name = Path(filename).name
    name = re.sub(r"[^\w.\- ]+", "_", name).strip()
    return name or "document.pdf"


def unique_storage_name(original_filename: str) -> str:
    safe = sanitize_filename(original_filename)
    return f"{uuid.uuid4().hex}_{safe}"


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def validate_pdf_content(path: Path) -> None:
    try:
        with fitz.open(path) as doc:
            if doc.page_count < 1:
                raise ValueError("PDF has no pages")
    except Exception as exc:
        raise ValueError("Invalid or corrupted PDF file") from exc


def resolve_upload_path(settings: Settings, storage_path: str) -> Path:
    base = settings.upload_dir.resolve()
    full = (settings.upload_dir / storage_path).resolve()
    if not str(full).startswith(str(base)):
        raise ValueError("Invalid storage path")
    return full


def resolve_text_path(settings: Settings, text_path: str) -> Path:
    base = settings.text_dir.resolve()
    full = (settings.text_dir / text_path).resolve()
    if not str(full).startswith(str(base)):
        raise ValueError("Invalid text path")
    return full
