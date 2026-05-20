"""Remove completed repair status.

Revision ID: 0003_remove_completed_status
Revises: 0002_repair_image_type
Create Date: 2026-05-19 00:00:00.000000
"""

from alembic import op


revision = "0003_remove_completed_status"
down_revision = "0002_repair_image_type"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("UPDATE repairs SET status = 'in_progress' WHERE status = 'completed'")
    op.create_check_constraint(
        "ck_repairs_status_allowed",
        "repairs",
        "status IN ('pending', 'in_progress', 'delivered', 'cancelled')",
    )


def downgrade() -> None:
    op.drop_constraint("ck_repairs_status_allowed", "repairs", type_="check")
