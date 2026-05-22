from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal
import base64
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings
from app.core.exceptions import AppError
from app.services.image_preprocessing_service import ImagePreprocessingService, PreprocessedImage


@dataclass(frozen=True)
class ExtractedRepairData:
    repair_date: date | None = None
    brand: str | None = None
    model: str | None = None
    watch_color: str | None = None
    watch_specifications: str | None = None
    description: str | None = None
    repair_cost: Decimal | None = None
    deposit_amount: Decimal | None = None
    watchmaker_percentage: Decimal | None = None
    customer_name: str | None = None
    customer_phone: str | None = None
    customer_document_id: str | None = None
    invoice_number: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class ExtractionResult:
    data: ExtractedRepairData
    extracted: bool
    message: str
    confidence: float | None = None
    raw_text: str | None = None
    raw_text_candidates: list[str] = field(default_factory=list)
    envelope_number: str | None = None
    phone_numbers: list[str] = field(default_factory=list)
    field_confidences: dict[str, float] = field(default_factory=dict)
    warnings: list[str] = field(default_factory=list)


FIELD_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "value": {"type": ["string", "null"]},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
    },
    "required": ["value", "confidence"],
}

TRANSCRIPTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "raw_transcription": {
            "type": "string",
            "description": "Transcripcion en espanol, linea por linea, preservando el texto visible.",
        },
        "raw_text_candidates": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Lecturas posibles de texto dudoso.",
        },
        "warnings": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Problemas visibles de imagen, letra, angulo, brillo o blur.",
        },
    },
    "required": ["raw_transcription", "raw_text_candidates", "warnings"],
}

EXTRACTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "raw_transcription": {
            "type": "string",
            "description": "Misma transcripcion en espanol usada para extraer los campos.",
        },
        "raw_text_candidates": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Lecturas posibles cuando el texto sea incierto.",
        },
        "envelope_number": FIELD_SCHEMA,
        "repair_date": FIELD_SCHEMA,
        "customer_name": FIELD_SCHEMA,
        "customer_phone": FIELD_SCHEMA,
        "customer_document_id": FIELD_SCHEMA,
        "phone_numbers": {"type": "array", "items": {"type": "string"}},
        "watch_brand": FIELD_SCHEMA,
        "watch_model": FIELD_SCHEMA,
        "watch_color": FIELD_SCHEMA,
        "watch_specifications": FIELD_SCHEMA,
        "repair_description": FIELD_SCHEMA,
        "repair_cost": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "value": {
                    "type": ["number", "null"],
                    "description": "Monto sin moneda ni separadores cuando sea claramente visible.",
                },
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            },
            "required": ["value", "confidence"],
        },
        "deposit_amount": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "value": {
                    "type": ["number", "null"],
                    "description": "Abono, deposito, adelanto o anticipo sin moneda ni separadores cuando sea claramente visible.",
                },
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            },
            "required": ["value", "confidence"],
        },
        "invoice_number": FIELD_SCHEMA,
        "status": {
            "type": "object",
            "additionalProperties": False,
            "properties": {
                "value": {"type": "string", "enum": ["pending", "in_progress", "delivered", "cancelled"]},
                "confidence": {"type": "number", "minimum": 0, "maximum": 1},
            },
            "required": ["value", "confidence"],
        },
        "notes": FIELD_SCHEMA,
        "warnings": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Problemas de calidad de imagen, letra, brillo, angulo, blur o datos ambiguos.",
        },
    },
    "required": [
        "raw_transcription",
        "raw_text_candidates",
        "envelope_number",
        "repair_date",
        "customer_name",
        "customer_phone",
        "customer_document_id",
        "phone_numbers",
        "watch_brand",
        "watch_model",
        "watch_color",
        "watch_specifications",
        "repair_description",
        "repair_cost",
        "deposit_amount",
        "invoice_number",
        "status",
        "notes",
        "warnings",
    ],
}


class ExtractionService:
    def extract_from_envelope_image(self, content: bytes, content_type: str) -> ExtractionResult:
        if not settings.openai_api_key:
            return ExtractionResult(
                data=ExtractedRepairData(),
                extracted=False,
                message="Configura OPENAI_API_KEY para activar la lectura automatica del sobre con Vision AI.",
            )

        images = self._prepare_vision_images(content=content, content_type=content_type)
        transcription_payload = self._build_transcription_payload(images)
        transcription = self._parse_response(self._call_openai(transcription_payload))

        structured_payload = self._build_structured_payload(transcription)
        parsed = self._parse_response(self._call_openai(structured_payload))
        parsed = self._merge_transcription(parsed, transcription)

        if self._field_score(parsed) == 0:
            direct_payload = self._build_direct_structured_payload(images, transcription)
            direct_parsed = self._merge_transcription(self._parse_response(self._call_openai(direct_payload)), transcription)
            if self._field_score(direct_parsed) > self._field_score(parsed):
                parsed = direct_parsed

        data = self._to_extracted_data(parsed)
        has_fields = any(
            value is not None
            for value in [
                data.repair_date,
                data.brand,
                data.model,
                data.watch_color,
                data.watch_specifications,
                data.description,
                data.repair_cost,
                data.deposit_amount,
                data.customer_name,
                data.customer_phone,
                data.customer_document_id,
                data.invoice_number,
                data.notes,
            ]
        )
        return ExtractionResult(
            data=data,
            extracted=has_fields,
            message="Campos sugeridos por Vision AI. Revisa y corrige antes de guardar."
            if has_fields
            else "Vision AI no encontro datos claros en el sobre. Puedes completar los campos manualmente.",
            confidence=self._overall_confidence(parsed),
            raw_text=self._clean_text(parsed.get("raw_transcription")),
            raw_text_candidates=self._clean_string_list(parsed.get("raw_text_candidates")),
            envelope_number=self._clean_text(self._field_value(parsed, "envelope_number")),
            phone_numbers=self._clean_string_list(parsed.get("phone_numbers")),
            field_confidences=self._field_confidences(parsed),
            warnings=self._clean_string_list(parsed.get("warnings")),
        )

    def _prepare_vision_images(self, *, content: bytes, content_type: str) -> list[PreprocessedImage]:
        return ImagePreprocessingService().prepare_for_vision(content, max_width=1800)

    def _build_transcription_payload(self, images: list[PreprocessedImage]) -> dict[str, Any]:
        content_items: list[dict[str, Any]] = [
            {
                "type": "input_text",
                "text": (
                    "Transcribe esta imagen de un sobre de reparacion de reloj escrito en espanol.\n"
                    "Usa la imagen original y la version mejorada. Devuelve la transcripcion en espanol, linea por linea.\n"
                    "No traduzcas marcas, modelos, telefonos ni precios. No inventes informacion.\n"
                    "Si una palabra o numero es dudoso, dejalo en raw_text_candidates y marca una advertencia."
                ),
            }
        ]
        for image in images:
            content_items.append(
                {
                    "type": "input_text",
                    "text": f"Imagen {image.label}:",
                }
            )
            content_items.append(self._image_input(image))
        return {
            "model": settings.openai_vision_model,
            "input": [{"role": "user", "content": content_items}],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "watch_repair_envelope_transcription",
                    "strict": True,
                    "schema": TRANSCRIPTION_SCHEMA,
                }
            },
            "max_output_tokens": 1200,
        }

    def _build_structured_payload(self, transcription: dict[str, Any]) -> dict[str, Any]:
        raw_transcription = self._clean_text(transcription.get("raw_transcription")) or ""
        candidates = self._clean_string_list(transcription.get("raw_text_candidates"))
        warnings = self._clean_string_list(transcription.get("warnings"))
        return {
            "model": settings.openai_vision_model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "You are a document extraction assistant specialized in handwritten watch repair envelopes.\n\n"
                                "Extract structured fields ONLY from this Spanish transcription. Do not use outside knowledge.\n"
                                "Return JSON in the provided schema.\n\n"
                                "Rules:\n"
                                "- Do not invent missing information.\n"
                                "- If a field is uncertain, return null or low confidence.\n"
                                "- Dates must be YYYY-MM-DD only when the date is clear.\n"
                                "- Money must be a number only when clearly visible.\n"
                                "- If a visible amount is labeled abono, anticipo, deposito or adelanto, put it in deposit_amount, not repair_cost.\n"
                                "- Extract cedula or customer document into customer_document_id.\n"
                                "- Put the main customer phone number in customer_phone and include every visible phone in phone_numbers.\n"
                                "- Extract numero de factura, factura, recibo or referencia into invoice_number.\n"
                                "- Extract visible watch color into watch_color.\n"
                                "- Watch specifications can include color, size, gender, strap, crystal, movement, water resistance, or other visible watch details.\n"
                                "- Phone numbers must be extracted separately.\n"
                                "- Watch brand and model must not be invented.\n"
                                "- Repair description and notes must remain in Spanish.\n"
                                "- Use status.value='pending' unless another status is clearly written.\n\n"
                                f"Raw transcription in Spanish:\n{raw_transcription}\n\n"
                                f"Raw text candidates:\n{json.dumps(candidates, ensure_ascii=False)}\n\n"
                                f"Transcription warnings:\n{json.dumps(warnings, ensure_ascii=False)}"
                            ),
                        }
                    ],
                }
            ],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "watch_repair_envelope_extraction",
                    "strict": True,
                    "schema": EXTRACTION_SCHEMA,
                }
            },
            "max_output_tokens": 1400,
        }

    def _build_direct_structured_payload(self, images: list[PreprocessedImage], transcription: dict[str, Any]) -> dict[str, Any]:
        raw_transcription = self._clean_text(transcription.get("raw_transcription")) or ""
        candidates = self._clean_string_list(transcription.get("raw_text_candidates"))
        warnings = self._clean_string_list(transcription.get("warnings"))
        content_items: list[dict[str, Any]] = [
            {
                "type": "input_text",
                "text": (
                    "La extraccion desde la transcripcion no encontro campos utiles. "
                    "Revisa nuevamente las imagenes original y mejorada junto con la transcripcion.\n\n"
                    "Extrae SOLO informacion visible del sobre de reparacion de reloj. "
                    "La transcripcion y los campos deben quedar en espanol. No inventes datos.\n"
                    "Si un campo no esta claro, usa null o baja confianza. "
                    "Si un precio, telefono, marca o fecha se ve en la imagen, incluyelo con su confianza real.\n\n"
                    "Si aparece telefono, cedula, factura, abono, color o especificaciones del reloj, extraelos en sus campos dedicados.\n\n"
                    f"Transcripcion previa:\n{raw_transcription}\n\n"
                    f"Lecturas dudosas:\n{json.dumps(candidates, ensure_ascii=False)}\n\n"
                    f"Advertencias previas:\n{json.dumps(warnings, ensure_ascii=False)}"
                ),
            }
        ]
        for image in images:
            content_items.append({"type": "input_text", "text": f"Imagen {image.label}:"})
            content_items.append(self._image_input(image))
        return {
            "model": settings.openai_vision_model,
            "input": [{"role": "user", "content": content_items}],
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "watch_repair_envelope_direct_extraction",
                    "strict": True,
                    "schema": EXTRACTION_SCHEMA,
                }
            },
            "max_output_tokens": 1600,
        }

    def _image_input(self, image: PreprocessedImage) -> dict[str, Any]:
        image_base64 = base64.b64encode(image.content).decode("ascii")
        return {
            "type": "input_image",
            "image_url": f"data:{image.content_type};base64,{image_base64}",
            "detail": "high",
        }

    def _call_openai(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = Request(
            "https://api.openai.com/v1/responses",
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"Bearer {settings.openai_api_key}",
                "Content-Type": "application/json",
            },
            method="POST",
        )
        try:
            with urlopen(request, timeout=settings.openai_vision_timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except HTTPError as exc:
            detail = self._read_error_detail(exc)
            raise AppError(f"No se pudo leer el sobre con Vision AI: {detail}") from exc
        except (TimeoutError, URLError) as exc:
            raise AppError("No se pudo conectar con OpenAI Vision AI") from exc
        except json.JSONDecodeError as exc:
            raise AppError("OpenAI Vision AI devolvio una respuesta invalida") from exc

    def _parse_response(self, response: dict[str, Any]) -> dict[str, Any]:
        output_text = response.get("output_text")
        if not output_text:
            output_text = self._find_output_text(response.get("output", []))
        if not output_text:
            raise AppError("OpenAI Vision AI no devolvio texto estructurado")
        try:
            parsed = json.loads(output_text)
        except json.JSONDecodeError as exc:
            raise AppError("OpenAI Vision AI no devolvio JSON valido") from exc
        if not isinstance(parsed, dict):
            raise AppError("OpenAI Vision AI devolvio un JSON inesperado")
        return parsed

    def _find_output_text(self, output: list[Any]) -> str | None:
        for item in output:
            if not isinstance(item, dict):
                continue
            for content_item in item.get("content", []):
                if isinstance(content_item, dict) and content_item.get("type") == "output_text":
                    text = content_item.get("text")
                    if isinstance(text, str):
                        return text
        return None

    def _merge_transcription(self, parsed: dict[str, Any], transcription: dict[str, Any]) -> dict[str, Any]:
        merged = dict(parsed)
        raw_transcription = self._clean_text(transcription.get("raw_transcription"))
        if raw_transcription:
            merged["raw_transcription"] = raw_transcription
        merged["raw_text_candidates"] = self._dedupe_strings(
            self._clean_string_list(transcription.get("raw_text_candidates"))
            + self._clean_string_list(parsed.get("raw_text_candidates"))
        )
        merged["warnings"] = self._dedupe_strings(
            self._clean_string_list(transcription.get("warnings")) + self._clean_string_list(parsed.get("warnings"))
        )
        return merged

    def _to_extracted_data(self, parsed: dict[str, Any]) -> ExtractedRepairData:
        return ExtractedRepairData(
            repair_date=self._parse_date(self._field_value(parsed, "repair_date")),
            brand=self._clean_text(self._field_value(parsed, "watch_brand")),
            model=self._clean_text(self._field_value(parsed, "watch_model")),
            watch_color=self._clean_text(self._field_value(parsed, "watch_color")),
            watch_specifications=self._clean_text(self._field_value(parsed, "watch_specifications")),
            description=self._clean_text(self._field_value(parsed, "repair_description")),
            repair_cost=self._parse_decimal(self._field_value(parsed, "repair_cost")),
            deposit_amount=self._parse_decimal(self._field_value(parsed, "deposit_amount")),
            customer_name=self._clean_text(self._field_value(parsed, "customer_name")),
            customer_phone=self._clean_text(self._field_value(parsed, "customer_phone")),
            customer_document_id=self._clean_text(self._field_value(parsed, "customer_document_id")),
            invoice_number=self._clean_text(self._field_value(parsed, "invoice_number")),
            notes=self._clean_text(self._field_value(parsed, "notes")),
        )

    def _field_value(self, parsed: dict[str, Any], field_name: str) -> Any:
        field_data = parsed.get(field_name)
        if not isinstance(field_data, dict):
            return None
        return field_data.get("value")

    def _field_confidences(self, parsed: dict[str, Any]) -> dict[str, float]:
        confidences: dict[str, float] = {}
        for field_name in [
            "envelope_number",
            "repair_date",
            "customer_name",
            "customer_phone",
            "customer_document_id",
            "watch_brand",
            "watch_model",
            "watch_color",
            "watch_specifications",
            "repair_description",
            "repair_cost",
            "deposit_amount",
            "invoice_number",
            "status",
            "notes",
        ]:
            field_data = parsed.get(field_name)
            if not isinstance(field_data, dict):
                continue
            confidence = self._parse_confidence(field_data.get("confidence"))
            if confidence is not None:
                confidences[field_name] = confidence
        return confidences

    def _field_score(self, parsed: dict[str, Any]) -> int:
        score = 0
        for field_name in [
            "envelope_number",
            "repair_date",
            "customer_name",
            "customer_phone",
            "customer_document_id",
            "watch_brand",
            "watch_model",
            "watch_color",
            "watch_specifications",
            "repair_description",
            "repair_cost",
            "deposit_amount",
            "invoice_number",
            "notes",
        ]:
            if self._field_value(parsed, field_name) is not None:
                score += 1
        if self._clean_string_list(parsed.get("phone_numbers")):
            score += 1
        return score

    def _clean_text(self, value: Any) -> str | None:
        if not isinstance(value, str):
            return None
        value = value.strip()
        return value or None

    def _parse_date(self, value: Any) -> date | None:
        value = self._clean_text(value)
        if not value:
            return None
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None

    def _parse_decimal(self, value: Any) -> Decimal | None:
        if value is None:
            return None
        clean_value = str(value).strip().replace(",", "")
        if not clean_value:
            return None
        try:
            decimal_value = Decimal(clean_value)
        except Exception:
            return None
        return decimal_value if decimal_value >= Decimal("0") else None

    def _clean_string_list(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        cleaned: list[str] = []
        for item in value:
            item_text = self._clean_text(item)
            if item_text:
                cleaned.append(item_text)
        return cleaned

    def _dedupe_strings(self, values: list[str]) -> list[str]:
        seen = set()
        deduped = []
        for value in values:
            key = value.casefold()
            if key not in seen:
                deduped.append(value)
                seen.add(key)
        return deduped

    def _parse_confidence(self, value: Any) -> float | None:
        if value is None:
            return None
        try:
            confidence = float(value)
        except (TypeError, ValueError):
            return None
        return max(0.0, min(1.0, confidence))

    def _overall_confidence(self, parsed: dict[str, Any]) -> float | None:
        values = []
        for field_name, confidence in self._field_confidences(parsed).items():
            if field_name == "status":
                continue
            if self._field_value(parsed, field_name) is not None:
                values.append(confidence)
        if not values:
            return None
        return round(sum(values) / len(values), 4)

    def _read_error_detail(self, exc: HTTPError) -> str:
        try:
            body = json.loads(exc.read().decode("utf-8"))
        except Exception:
            return exc.reason or "error desconocido"
        message = body.get("error", {}).get("message")
        return message if isinstance(message, str) else "error desconocido"
