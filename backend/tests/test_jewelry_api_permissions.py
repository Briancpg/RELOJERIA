from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from typing import Iterator

import pytest
from fastapi import Depends, FastAPI, Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.deps import get_current_user
from app.api.v1.router import api_router
from app.core.exceptions import register_exception_handlers
from app.db.base import Base
from app.db.session import get_db
from app.models import InventoryItem, Repair, RepairImage, User
from app.models.repair import RepairStatus
from app.models.repair_image import RepairImageType
from app.models.user import UserRole
from app.services.extraction_service import ExtractedRepairData, ExtractionResult, ExtractionService
from app.storage.r2 import R2Storage, StoredObject


SENSITIVE_REPAIR_FIELDS = {
    "internal_cost",
    "watchmaker_percentage",
    "profit_amount",
    "notes",
    "envelope_raw_transcription",
}

PNG_1X1 = bytes.fromhex(
    "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
    "0000000d49444154789c6360000002000150a0f5190000000049454e44ae426082"
)


@dataclass(frozen=True)
class ApiContext:
    client: TestClient
    jewelry_id: int
    other_jewelry_id: int
    owned_repair_id: int
    other_repair_id: int
    owned_image_id: int
    other_image_id: int
    inventory_item_id: int


def _repair(*, created_by_user_id: int, brand: str) -> Repair:
    return Repair(
        created_by_user_id=created_by_user_id,
        repair_date=date(2026, 6, 17),
        brand=brand,
        model="RoleCheck",
        description="Chequeo de permisos",
        repair_cost=Decimal("1200.00"),
        internal_cost=Decimal("450.00"),
        deposit_amount=Decimal("100.00"),
        watchmaker_percentage=Decimal("50.00"),
        profit_amount=Decimal("600.00"),
        status=RepairStatus.submitted,
        customer_name="Cliente prueba",
        customer_phone="809-555-0000",
        customer_document_id="001-0000000-1",
        invoice_number="FAC-001",
        notes="nota interna privada",
        envelope_raw_transcription="transcripcion privada del sobre",
    )


@pytest.fixture()
def api_context(monkeypatch: pytest.MonkeyPatch) -> Iterator[ApiContext]:
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
    Base.metadata.create_all(bind=engine)

    with TestingSessionLocal() as db:
        admin = User(email="admin@example.com", hashed_password="x", role=UserRole.admin, is_admin=True)
        jewelry = User(email="joyeria@example.com", hashed_password="x", role=UserRole.joyeria, is_admin=False)
        other_jewelry = User(email="otra@example.com", hashed_password="x", role=UserRole.joyeria, is_admin=False)
        db.add_all([admin, jewelry, other_jewelry])
        db.flush()

        owned_repair = _repair(created_by_user_id=jewelry.id, brand="Owned")
        other_repair = _repair(created_by_user_id=other_jewelry.id, brand="Other")
        db.add_all([owned_repair, other_repair])
        db.flush()

        owned_image = RepairImage(
            repair_id=owned_repair.id,
            image_type=RepairImageType.watch,
            r2_key="repairs/owned/watch.png",
            file_name="watch.png",
            content_type="image/png",
            file_size=len(PNG_1X1),
            public_url=None,
        )
        other_image = RepairImage(
            repair_id=other_repair.id,
            image_type=RepairImageType.envelope,
            r2_key="repairs/other/envelope.png",
            file_name="envelope.png",
            content_type="image/png",
            file_size=len(PNG_1X1),
            public_url=None,
        )
        inventory_item = InventoryItem(
            reference="PRV-001",
            name="Pieza privada",
            category="Movimiento",
            stock_quantity=2,
            minimum_stock=1,
            unit_price=Decimal("100.00"),
        )
        db.add_all([owned_image, other_image, inventory_item])
        db.flush()
        db.commit()

        user_by_email = {
            admin.email: admin,
            jewelry.email: jewelry,
            other_jewelry.email: other_jewelry,
        }
        context_ids = {
            "jewelry_id": jewelry.id,
            "other_jewelry_id": other_jewelry.id,
            "owned_repair_id": owned_repair.id,
            "other_repair_id": other_repair.id,
            "owned_image_id": owned_image.id,
            "other_image_id": other_image.id,
            "inventory_item_id": inventory_item.id,
        }

    def override_get_db() -> Iterator[Session]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    def override_get_current_user(request: Request) -> User:
        email = request.headers.get("x-test-user", "joyeria@example.com")
        return user_by_email[email]

    def fake_r2_init(self: R2Storage) -> None:
        return None

    def fake_download_image(self: R2Storage, *, key: str) -> bytes:
        return b"private-image-bytes"

    def fake_upload_image(self: R2Storage, *, repair_id: int, file_name: str, content_type: str, content: bytes):
        return StoredObject(key=f"repairs/{repair_id}/{file_name}", public_url=None)

    monkeypatch.setattr(R2Storage, "__init__", fake_r2_init)
    monkeypatch.setattr(R2Storage, "download_image", fake_download_image)
    monkeypatch.setattr(R2Storage, "upload_image", fake_upload_image)

    app = FastAPI()
    register_exception_handlers(app)
    app.include_router(api_router, prefix="/api/v1")
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    with TestClient(app) as client:
        yield ApiContext(client=client, **context_ids)

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def _jewelry_headers() -> dict[str, str]:
    return {"x-test-user": "joyeria@example.com"}


def _admin_headers() -> dict[str, str]:
    return {"x-test-user": "admin@example.com"}


def assert_repair_sensitive_fields_are_redacted(payload: dict) -> None:
    for field in SENSITIVE_REPAIR_FIELDS:
        assert field in payload
        assert payload[field] is None


def assert_no_sensitive_keys(payload) -> None:
    if isinstance(payload, dict):
        assert not (SENSITIVE_REPAIR_FIELDS & set(payload.keys()))
        for value in payload.values():
            assert_no_sensitive_keys(value)
    elif isinstance(payload, list):
        for item in payload:
            assert_no_sensitive_keys(item)


def test_jewelry_repair_list_and_detail_redact_sensitive_fields_and_filter_ownership(api_context: ApiContext):
    response = api_context.client.get("/api/v1/repairs", headers=_jewelry_headers())

    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 1
    assert [item["id"] for item in body["items"]] == [api_context.owned_repair_id]
    assert_repair_sensitive_fields_are_redacted(body["items"][0])

    own_detail = api_context.client.get(f"/api/v1/repairs/{api_context.owned_repair_id}", headers=_jewelry_headers())
    assert own_detail.status_code == 200
    assert_repair_sensitive_fields_are_redacted(own_detail.json())

    other_detail = api_context.client.get(f"/api/v1/repairs/{api_context.other_repair_id}", headers=_jewelry_headers())
    assert other_detail.status_code == 404
    assert_no_sensitive_keys(other_detail.json())


def test_jewelry_create_repair_forces_safe_defaults_and_redacts_sensitive_response(api_context: ApiContext):
    payload = {
        "repair_date": "2026-06-17",
        "brand": "New",
        "model": "Safe",
        "description": "Creada por joyeria",
        "repair_cost": "2000.00",
        "internal_cost": "999.00",
        "watchmaker_percentage": "90.00",
        "status": "delivered",
        "customer_name": "Cliente joyeria",
        "customer_phone": "809-555-2222",
        "notes": "nota privada que no debe persistir para joyeria",
        "envelope_raw_transcription": "texto privado",
    }

    response = api_context.client.post("/api/v1/repairs", json=payload, headers=_jewelry_headers())

    assert response.status_code == 201
    body = response.json()
    assert body["created_by_user_id"] == api_context.jewelry_id
    assert body["status"] == "submitted"
    assert body["exit_date"] is None
    assert_repair_sensitive_fields_are_redacted(body)

    admin_detail = api_context.client.get(f"/api/v1/repairs/{body['id']}", headers=_admin_headers())
    assert admin_detail.status_code == 200
    persisted = admin_detail.json()
    assert persisted["internal_cost"] == "0.00"
    assert persisted["watchmaker_percentage"] == "0.00"
    assert persisted["profit_amount"] == "0.00"
    assert persisted["notes"] is None
    assert persisted["envelope_raw_transcription"] is None


def test_jewelry_cannot_update_or_delete_repairs(api_context: ApiContext):
    update_response = api_context.client.patch(
        f"/api/v1/repairs/{api_context.owned_repair_id}",
        json={
            "internal_cost": "1.00",
            "watchmaker_percentage": "100.00",
            "notes": "intento de ver nota",
            "envelope_raw_transcription": "intento de transcripcion",
        },
        headers=_jewelry_headers(),
    )
    assert update_response.status_code == 403
    assert_no_sensitive_keys(update_response.json())

    delete_response = api_context.client.delete(
        f"/api/v1/repairs/{api_context.owned_repair_id}",
        headers=_jewelry_headers(),
    )
    assert delete_response.status_code == 403
    assert_no_sensitive_keys(delete_response.json())


def test_jewelry_image_routes_are_scoped_and_do_not_expose_repair_sensitive_fields(api_context: ApiContext):
    images = api_context.client.get(
        f"/api/v1/repairs/{api_context.owned_repair_id}/images",
        headers=_jewelry_headers(),
    )
    assert images.status_code == 200
    assert images.json()[0]["id"] == api_context.owned_image_id
    assert_no_sensitive_keys(images.json())

    content = api_context.client.get(
        f"/api/v1/repairs/{api_context.owned_repair_id}/images/{api_context.owned_image_id}/content",
        headers=_jewelry_headers(),
    )
    assert content.status_code == 200
    assert content.content == b"private-image-bytes"
    assert not any(field.encode() in content.content for field in SENSITIVE_REPAIR_FIELDS)

    other_images = api_context.client.get(
        f"/api/v1/repairs/{api_context.other_repair_id}/images",
        headers=_jewelry_headers(),
    )
    assert other_images.status_code == 404
    assert_no_sensitive_keys(other_images.json())

    other_content = api_context.client.get(
        f"/api/v1/repairs/{api_context.other_repair_id}/images/{api_context.other_image_id}/content",
        headers=_jewelry_headers(),
    )
    assert other_content.status_code == 404
    assert_no_sensitive_keys(other_content.json())

    own_delete = api_context.client.delete(
        f"/api/v1/repairs/{api_context.owned_repair_id}/images/{api_context.owned_image_id}",
        headers=_jewelry_headers(),
    )
    assert own_delete.status_code == 204

    other_delete = api_context.client.delete(
        f"/api/v1/repairs/{api_context.other_repair_id}/images/{api_context.other_image_id}",
        headers=_jewelry_headers(),
    )
    assert other_delete.status_code == 404
    assert_no_sensitive_keys(other_delete.json())


def test_jewelry_upload_image_response_does_not_expose_repair_sensitive_fields(api_context: ApiContext):
    response = api_context.client.post(
        f"/api/v1/repairs/{api_context.owned_repair_id}/images",
        data={"image_type": "watch"},
        files={"file": ("watch.png", PNG_1X1, "image/png")},
        headers=_jewelry_headers(),
    )

    assert response.status_code == 201
    body = response.json()
    assert body["repair_id"] == api_context.owned_repair_id
    assert body["image_type"] == "watch"
    assert_no_sensitive_keys(body)


def test_jewelry_extraction_response_redacts_financial_notes_and_raw_transcription(
    api_context: ApiContext,
    monkeypatch: pytest.MonkeyPatch,
):
    def fake_extract(self: ExtractionService, content: bytes, content_type: str) -> ExtractionResult:
        return ExtractionResult(
            data=ExtractedRepairData(
                repair_date=date(2026, 6, 17),
                brand="Seiko",
                model="5",
                description="Cambio de cristal",
                repair_cost=Decimal("1500.00"),
                deposit_amount=Decimal("500.00"),
                watchmaker_percentage=Decimal("50.00"),
                customer_name="Cliente",
                customer_phone="809-555-3333",
                notes="nota privada detectada",
            ),
            extracted=True,
            message="Campos sugeridos",
            confidence=0.9,
            raw_text="transcripcion privada completa",
            raw_text_candidates=["lectura privada dudosa"],
            envelope_number="A-1",
            phone_numbers=["809-555-3333"],
            field_confidences={
                "repair_cost": 0.9,
                "deposit_amount": 0.9,
                "watchmaker_percentage": 0.9,
                "notes": 0.9,
                "brand": 0.9,
            },
            warnings=["texto borroso"],
        )

    monkeypatch.setattr(ExtractionService, "extract_from_envelope_image", fake_extract)

    response = api_context.client.post(
        "/api/v1/repairs/extract-envelope",
        files={"file": ("sobre.png", PNG_1X1, "image/png")},
        headers=_jewelry_headers(),
    )

    assert response.status_code == 200
    body = response.json()
    assert body["fields"]["brand"] == "Seiko"
    assert body["fields"]["repair_cost"] is None
    assert body["fields"]["deposit_amount"] is None
    assert body["fields"]["watchmaker_percentage"] is None
    assert body["fields"]["notes"] is None
    assert body["raw_text"] is None
    assert body["raw_transcription"] is None
    assert body["raw_text_candidates"] == []
    assert "repair_cost" not in body["field_confidences"]
    assert "deposit_amount" not in body["field_confidences"]
    assert "watchmaker_percentage" not in body["field_confidences"]
    assert "notes" not in body["field_confidences"]
    assert "envelope_raw_transcription" not in body


@pytest.mark.parametrize(
    "path",
    [
        "/api/v1/dashboard/summary",
        "/api/v1/dashboard/repairs-by-status",
        "/api/v1/dashboard/profit-by-week",
        "/api/v1/reports/summary",
        "/api/v1/clients",
        "/api/v1/inventory",
        "/api/v1/inventory/summary",
    ],
)
def test_jewelry_cannot_access_admin_financial_or_operational_modules(api_context: ApiContext, path: str):
    response = api_context.client.get(path, headers=_jewelry_headers())

    assert response.status_code == 403
    assert_no_sensitive_keys(response.json())


def test_jewelry_cannot_access_any_inventory_endpoint(api_context: ApiContext):
    create_payload = {
        "reference": "NEW-001",
        "name": "Pieza nueva",
        "category": "Movimiento",
        "stock_quantity": 1,
        "minimum_stock": 1,
        "unit_price": "10.00",
    }
    requests = [
        ("get", "/api/v1/inventory", None),
        ("get", "/api/v1/inventory/summary", None),
        ("get", f"/api/v1/inventory/{api_context.inventory_item_id}", None),
        ("post", "/api/v1/inventory", create_payload),
        ("patch", f"/api/v1/inventory/{api_context.inventory_item_id}", {"unit_price": "99.00"}),
        ("delete", f"/api/v1/inventory/{api_context.inventory_item_id}", None),
    ]

    for method, path, payload in requests:
        response = api_context.client.request(method, path, json=payload, headers=_jewelry_headers())
        assert response.status_code == 403
        assert_no_sensitive_keys(response.json())


def test_admin_dashboard_and_reports_work_with_simplified_statuses(api_context: ApiContext):
    summary = api_context.client.get("/api/v1/dashboard/summary", headers=_admin_headers())
    assert summary.status_code == 200
    summary_body = summary.json()
    assert summary_body["submitted_repairs"] == 2
    assert summary_body["pending_repairs"] == 0
    assert summary_body["active_repairs"] == 2
    assert summary_body["ready_repairs"] == 0
    assert summary_body["delivered_repairs"] == 0

    by_status = api_context.client.get("/api/v1/dashboard/repairs-by-status", headers=_admin_headers())
    assert by_status.status_code == 200
    assert by_status.json() == [{"status": "submitted", "count": 2}]

    reports = api_context.client.get("/api/v1/reports/summary", headers=_admin_headers())
    assert reports.status_code == 200
    report_body = reports.json()
    assert report_body["total_repairs"] == 2
    assert report_body["status_counts"] == [{"name": "submitted", "count": 2}]


def test_jewelry_limited_dashboard_has_no_financial_or_sensitive_fields(api_context: ApiContext):
    response = api_context.client.get("/api/v1/dashboard/my-summary", headers=_jewelry_headers())

    assert response.status_code == 200
    body = response.json()
    assert set(body.keys()) == {"sent_repairs", "in_process_repairs", "ready_repairs", "delivered_repairs"}
    assert_no_sensitive_keys(body)
