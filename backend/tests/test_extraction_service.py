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
    responses = [
        {
            "output_text": (
                '{"raw_transcription":"Sobre 102\\nFecha 2026-05-20\\nJuan Perez\\nSeiko 5 Sports\\nCambio de cristal\\nRD$2500",'
                '"raw_text_candidates":["Sobre 102","Sobre 107"],'
                '"warnings":["La esquina inferior esta borrosa."]}'
            )
        },
        {
            "output_text": (
                '{"raw_transcription":"Sobre 102\\nFecha 2026-05-20\\nJuan Perez\\nSeiko 5 Sports\\nCambio de cristal\\nRD$2500",'
                '"raw_text_candidates":["Sobre 102"],'
                '"envelope_number":{"value":"102","confidence":0.82},'
                '"repair_date":{"value":"2026-05-20","confidence":0.91},'
                '"customer_name":{"value":"Juan Perez","confidence":0.88},'
                '"customer_phone":{"value":"809-555-1234","confidence":0.9},'
                '"customer_document_id":{"value":"001-1234567-8","confidence":0.92},'
                '"phone_numbers":["809-555-1234"],'
                '"watch_brand":{"value":"Seiko","confidence":0.93},'
                '"watch_model":{"value":"5 Sports","confidence":0.89},'
                '"watch_color":{"value":"Azul","confidence":0.83},'
                '"watch_specifications":{"value":"Correa metalica, esfera azul","confidence":0.81},'
                '"repair_description":{"value":"Cambio de cristal","confidence":0.86},'
                '"repair_cost":{"value":2500,"confidence":0.9},'
                '"deposit_amount":{"value":500,"confidence":0.78},'
                '"invoice_number":{"value":"F-102","confidence":0.84},'
                '"status":{"value":"pending","confidence":0.7},'
                '"notes":{"value":"Cristal rayado","confidence":0.8},'
                '"warnings":[]}'
            )
        },
    ]

    def fake_call_openai(_):
        return responses.pop(0)

    monkeypatch.setattr(service, "_call_openai", fake_call_openai)
    monkeypatch.setattr(service, "_prepare_vision_images", lambda **_: [])

    result = service.extract_from_envelope_image(b"image-bytes", "image/png")

    assert responses == []
    assert result.extracted is True
    assert result.data.brand == "Seiko"
    assert result.data.model == "5 Sports"
    assert result.data.watch_color == "Azul"
    assert result.data.watch_specifications == "Correa metalica, esfera azul"
    assert result.data.repair_cost == Decimal("2500")
    assert result.data.deposit_amount == Decimal("500")
    assert result.data.watchmaker_percentage is None
    assert result.data.customer_phone == "809-555-1234"
    assert result.data.customer_document_id == "001-1234567-8"
    assert result.data.invoice_number == "F-102"
    assert result.confidence == 0.8621
    assert result.raw_text == "Sobre 102\nFecha 2026-05-20\nJuan Perez\nSeiko 5 Sports\nCambio de cristal\nRD$2500"
    assert result.raw_text_candidates == ["Sobre 102", "Sobre 107"]
    assert result.envelope_number == "102"
    assert result.phone_numbers == ["809-555-1234"]
    assert result.field_confidences["watch_brand"] == 0.93
    assert result.warnings == ["La esquina inferior esta borrosa."]
