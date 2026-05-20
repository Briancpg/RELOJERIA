from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import base64
import json
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from app.core.config import settings
from app.core.exceptions import AppError


@dataclass(frozen=True)
class ExtractedRepairData:
    repair_date: date | None = None
    brand: str | None = None
    model: str | None = None
    description: str | None = None
    repair_cost: Decimal | None = None
    watchmaker_percentage: Decimal | None = None
    customer_name: str | None = None
    notes: str | None = None


@dataclass(frozen=True)
class ExtractionResult:
    data: ExtractedRepairData
    extracted: bool
    message: str
    confidence: float | None = None
    raw_text: str | None = None


EXTRACTION_SCHEMA: dict[str, Any] = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "repair_date": {
            "type": ["string", "null"],
            "description": "Fecha en formato YYYY-MM-DD si aparece claramente en el sobre.",
        },
        "brand": {"type": ["string", "null"], "description": "Marca del reloj."},
        "model": {"type": ["string", "null"], "description": "Modelo o referencia del reloj."},
        "description": {"type": ["string", "null"], "description": "Descripcion breve de la reparacion solicitada."},
        "repair_cost": {
            "type": ["string", "null"],
            "description": "Costo de reparacion como numero decimal sin moneda ni separadores de miles.",
        },
        "watchmaker_percentage": {
            "type": ["string", "null"],
            "description": "Porcentaje del relojero como numero decimal sin simbolo de porcentaje.",
        },
        "customer_name": {"type": ["string", "null"], "description": "Nombre del cliente si aparece."},
        "notes": {"type": ["string", "null"], "description": "Notas utiles no cubiertas por otros campos."},
        "raw_text": {"type": ["string", "null"], "description": "Texto visible leido del sobre."},
        "confidence": {
            "type": ["number", "null"],
            "description": "Confianza general entre 0 y 1 basada en legibilidad y claridad.",
        },
    },
    "required": [
        "repair_date",
        "brand",
        "model",
        "description",
        "repair_cost",
        "watchmaker_percentage",
        "customer_name",
        "notes",
        "raw_text",
        "confidence",
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

        payload = self._build_payload(content=content, content_type=content_type)
        response = self._call_openai(payload)
        parsed = self._parse_response(response)
        data = self._to_extracted_data(parsed)
        has_fields = any(
            value is not None
            for value in [
                data.repair_date,
                data.brand,
                data.model,
                data.description,
                data.repair_cost,
                data.watchmaker_percentage,
                data.customer_name,
                data.notes,
            ]
        )
        return ExtractionResult(
            data=data,
            extracted=has_fields,
            message="Campos sugeridos por Vision AI. Revisa y corrige antes de guardar."
            if has_fields
            else "Vision AI no encontro datos claros en el sobre. Puedes completar los campos manualmente.",
            confidence=self._parse_confidence(parsed.get("confidence")),
            raw_text=self._clean_text(parsed.get("raw_text")),
        )

    def _build_payload(self, *, content: bytes, content_type: str) -> dict[str, Any]:
        image_base64 = base64.b64encode(content).decode("ascii")
        return {
            "model": settings.openai_vision_model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "input_text",
                            "text": (
                                "Lee esta foto de un sobre de reparacion de reloj. "
                                "Extrae solo informacion visible. Si un dato no esta claro, usa null. "
                                "No inventes marca, modelo, costo, porcentaje, cliente ni fecha."
                            ),
                        },
                        {
                            "type": "input_image",
                            "image_url": f"data:{content_type};base64,{image_base64}",
                            "detail": "high",
                        },
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
            "max_output_tokens": 900,
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

    def _to_extracted_data(self, parsed: dict[str, Any]) -> ExtractedRepairData:
        return ExtractedRepairData(
            repair_date=self._parse_date(parsed.get("repair_date")),
            brand=self._clean_text(parsed.get("brand")),
            model=self._clean_text(parsed.get("model")),
            description=self._clean_text(parsed.get("description")),
            repair_cost=self._parse_decimal(parsed.get("repair_cost")),
            watchmaker_percentage=self._parse_decimal(parsed.get("watchmaker_percentage")),
            customer_name=self._clean_text(parsed.get("customer_name")),
            notes=self._clean_text(parsed.get("notes")),
        )

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

    def _parse_confidence(self, value: Any) -> float | None:
        if value is None:
            return None
        try:
            confidence = float(value)
        except (TypeError, ValueError):
            return None
        return max(0.0, min(1.0, confidence))

    def _read_error_detail(self, exc: HTTPError) -> str:
        try:
            body = json.loads(exc.read().decode("utf-8"))
        except Exception:
            return exc.reason or "error desconocido"
        message = body.get("error", {}).get("message")
        return message if isinstance(message, str) else "error desconocido"
