from app.services.extraction.demo import DemoExtractionProvider


def test_demo_provider_reads_fixture_marker():
    text = "DOCFLOW-FIXTURE-ID: acme_001\nSupplier: ignored"
    provider = DemoExtractionProvider()
    result = provider.extract(text)
    assert result.provider_name == "demo"
    assert result.invoice.invoice_number == "INV-2024-1001"


def test_demo_provider_unknown_document_fails():
    provider = DemoExtractionProvider()
    try:
        provider.extract("random text")
        raised = False
    except ValueError:
        raised = True
    assert raised
