from decimal import Decimal

from app.core.config import settings
from app.services.extraction_service import ExtractionService


def test_extraction_without_openai_key_returns_actionable_message(monkeypatch):
    monkeypatch.setattr(settings, "openai_api_key", "")

    result = ExtractionService().extract_from_envelope_image(b"image-bytes", "image/png")

    assert result.extracted is False
    assert "OPENAI_API_KEY" in result.message
    assert result.data.brand is None


def test_extraction_maps_structured_openai_json(monkeypatch):
    monkeypatch.setattr(settings, "openai_api_key", "test-key")
    service = ExtractionService()

    def fake_call_openai(_):
        return {
            "output_text": (
                '{"repair_date":"2026-05-20","brand":"Seiko","model":"5 Sports",'
                '"description":"Cambio de cristal","repair_cost":"2500.00",'
                '"watchmaker_percentage":"50","customer_name":"Juan Perez",'
                '"notes":"Cristal rayado","raw_text":"Marca: Seiko","confidence":0.86}'
            )
        }

    monkeypatch.setattr(service, "_call_openai", fake_call_openai)

    result = service.extract_from_envelope_image(b"image-bytes", "image/png")

    assert result.extracted is True
    assert result.data.brand == "Seiko"
    assert result.data.model == "5 Sports"
    assert result.data.repair_cost == Decimal("2500.00")
    assert result.data.watchmaker_percentage == Decimal("50")
    assert result.confidence == 0.86
    assert result.raw_text == "Marca: Seiko"
