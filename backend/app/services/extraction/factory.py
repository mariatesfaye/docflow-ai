from app.config import Settings
from app.services.extraction.base import ExtractionProvider
from app.services.extraction.demo import DemoExtractionProvider
from app.services.extraction.openai_provider import OpenAIExtractionProvider


def get_extraction_provider(settings: Settings) -> ExtractionProvider:
    mode = settings.extraction_provider.lower().strip()
    if mode == "demo":
        return DemoExtractionProvider()
    if mode in {"openai", "llm"}:
        return OpenAIExtractionProvider(settings)
    raise ValueError(f"Unsupported extraction provider: {settings.extraction_provider}")
