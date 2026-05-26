"""Update repair workflow statuses.

Revision ID: 0010_repair_workflow_statuses
Revises: 0009_inventory_items
Create Date: 2026-05-25 00:00:00.000000
"""

from alembic import op


revision = "0010_repair_workflow_statuses"
down_revision = "0009_inventory_items"
branch_labels = None
depends_on = None


NEW_STATUSES = "'diagnosis', 'in_repair', 'waiting_parts', 'ready', 'delivered', 'cancelled'"
OLD_STATUSES = "'pending', 'in_progress', 'delivered', 'cancelled'"


def upgrade() -> None:
    op.drop_constraint("ck_repairs_status_allowed", "repairs", type_="check")
    op.execute(
        """
        UPDATE repairs
        SET status = CASE status
            WHEN 'pending' THEN 'diagnosis'
            WHEN 'in_progress' THEN 'in_repair'
            WHEN 'completed' THEN 'in_repair'
            ELSE status
        END
        """
    )
    op.create_check_constraint(
        "ck_repairs_status_allowed",
        "repairs",
        f"status IN ({NEW_STATUSES})",
    )


def downgrade() -> None:
    op.drop_constraint("ck_repairs_status_allowed", "repairs", type_="check")
    op.execute(
        """
        UPDATE repairs
        SET status = CASE status
            WHEN 'diagnosis' THEN 'pending'
            WHEN 'in_repair' THEN 'in_progress'
            WHEN 'waiting_parts' THEN 'in_progress'
            WHEN 'ready' THEN 'in_progress'
            ELSE status
        END
        """
    )
    op.create_check_constraint(
        "ck_repairs_status_allowed",
        "repairs",
        f"status IN ({OLD_STATUSES})",
    )
