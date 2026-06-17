"""Simplify repair status workflow.

Revision ID: 0012_simplify_repair_status_flow
Revises: 0011_roles_delivery_fields
Create Date: 2026-06-17 00:00:00.000000
"""

from alembic import op


revision = "0012_simplify_repair_status_flow"
down_revision = "0011_roles_delivery_fields"
branch_labels = None
depends_on = None


NEW_STATUSES = "'submitted', 'pending', 'in_process', 'ready', 'delivered', 'cancelled'"
OLD_STATUSES = "'received', 'diagnosis', 'in_repair', 'waiting_parts', 'ready', 'delivered', 'cancelled'"
UPGRADE_STATUS_MAP = {
    "received": "pending",
    "diagnosis": "pending",
    "in_repair": "in_process",
    "waiting_parts": "in_process",
    "ready": "ready",
    "delivered": "delivered",
    "cancelled": "cancelled",
}
DOWNGRADE_STATUS_MAP = {
    "submitted": "received",
    "pending": "diagnosis",
    "in_process": "in_repair",
    "ready": "ready",
    "delivered": "delivered",
    "cancelled": "cancelled",
}


def _case_statement(status_map: dict[str, str]) -> str:
    cases = " ".join(f"WHEN '{source}' THEN '{target}'" for source, target in status_map.items())
    return f"CASE status {cases} ELSE status END"


def upgrade() -> None:
    op.drop_constraint("ck_repairs_status_allowed", "repairs", type_="check")
    op.execute(f"UPDATE repairs SET status = {_case_statement(UPGRADE_STATUS_MAP)}")
    op.create_check_constraint("ck_repairs_status_allowed", "repairs", f"status IN ({NEW_STATUSES})")


def downgrade() -> None:
    op.drop_constraint("ck_repairs_status_allowed", "repairs", type_="check")
    op.execute(f"UPDATE repairs SET status = {_case_statement(DOWNGRADE_STATUS_MAP)}")
    op.create_check_constraint("ck_repairs_status_allowed", "repairs", f"status IN ({OLD_STATUSES})")
