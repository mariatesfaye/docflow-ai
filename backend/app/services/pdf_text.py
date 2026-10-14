from pathlib import Path

import fitz
import pytesseract
from PIL import Image

from app.config import Settings


def extract_embedded_text(pdf_path: Path) -> str:
    parts: list[str] = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            parts.append(page.get_text("text"))
    return "\n".join(parts).strip()


def ocr_pdf(pdf_path: Path) -> str:
    parts: list[str] = []
    with fitz.open(pdf_path) as doc:
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            image = Image.frombytes("RGB", (pix.width, pix.height), pix.samples)
            parts.append(pytesseract.image_to_string(image))
    return "\n".join(parts).strip()


def extract_document_text(pdf_path: Path, settings: Settings) -> tuple[str, bool]:
    text = extract_embedded_text(pdf_path)
    used_ocr = False
    if len(text.replace("\n", "").strip()) < 40 and settings.ocr_enabled:
        ocr_text = ocr_pdf(pdf_path)
        if len(ocr_text.strip()) > len(text.strip()):
            text = ocr_text
            used_ocr = True
    return text, used_ocr
