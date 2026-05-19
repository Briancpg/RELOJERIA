from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass(frozen=True)
class ExtractedRepairData:
    repair_date: date | None = None
    brand: str | None = None
    model: str | None = None
    description: str | None = None
    repair_cost: Decimal | None = None
    watchmaker_percentage: Decimal | None = None


class ExtractionService:
    def extract_from_image(self, _: bytes) -> ExtractedRepairData:
        raise NotImplementedError("OCR/AI extraction is intentionally not implemented in v1.")

