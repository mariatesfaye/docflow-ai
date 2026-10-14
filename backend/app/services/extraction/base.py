from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.schemas.invoice import InvoiceData


@dataclass
class ExtractionResult:
    invoice: InvoiceData
    provider_name: str
    model_id: str | None
    field_confidence: dict[str, str | float | None] | None
    duration_ms: int


class ExtractionProvider(ABC):
    @abstractmethod
    def extract(self, document_text: str, filename: str | None = None) -> ExtractionResult:
        raise NotImplementedError
