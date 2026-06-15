"""Add user roles and repair delivery ownership fields.

Revision ID: 0011_roles_delivery_fields
Revises: 0010_repair_workflow_statuses
Create Date: 2026-06-15 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0011_roles_delivery_fields"
down_revision = "0010_repair_workflow_statuses"
branch_labels = None
depends_on = None


NEW_STATUSES = "'received', 'diagnosis', 'in_repair', 'waiting_parts', 'ready', 'delivered', 'cancelled'"
OLD_STATUSES = "'diagnosis', 'in_repair', 'waiting_parts', 'ready', 'delivered', 'cancelled'"


def upgrade() -> None:
    op.add_column("users", sa.Column("role", sa.String(length=20), nullable=False, server_default="admin"))
    op.create_check_constraint("ck_users_user_role_allowed", "users", "role IN ('admin', 'maestro', 'joyeria')")

    op.add_column("repairs", sa.Column("created_by_user_id", sa.Integer(), nullable=True))
    op.add_column("repairs", sa.Column("exit_date", sa.Date(), nullable=True))
    op.add_column(
        "repairs",
        sa.Column("internal_cost", sa.Numeric(precision=12, scale=2), nullable=False, server_default="0"),
    )
    op.create_index(op.f("ix_repairs_created_by_user_id"), "repairs", ["created_by_user_id"], unique=False)
    op.create_index(op.f("ix_repairs_exit_date"), "repairs", ["exit_date"], unique=False)
    op.create_foreign_key(
        op.f("fk_repairs_created_by_user_id_users"),
        "repairs",
        "users",
        ["created_by_user_id"],
        ["id"],
        ondelete="SET NULL",
    )
    op.create_check_constraint("ck_repairs_internal_cost_non_negative", "repairs", "internal_cost >= 0")

    op.drop_constraint("ck_repairs_status_allowed", "repairs", type_="check")
    op.create_check_constraint("ck_repairs_status_allowed", "repairs", f"status IN ({NEW_STATUSES})")


def downgrade() -> None:
    op.drop_constraint("ck_repairs_status_allowed", "repairs", type_="check")
    op.execute("UPDATE repairs SET status = 'diagnosis' WHERE status = 'received'")
    op.create_check_constraint("ck_repairs_status_allowed", "repairs", f"status IN ({OLD_STATUSES})")

    op.drop_constraint("ck_repairs_internal_cost_non_negative", "repairs", type_="check")
    op.drop_constraint(op.f("fk_repairs_created_by_user_id_users"), "repairs", type_="foreignkey")
    op.drop_index(op.f("ix_repairs_exit_date"), table_name="repairs")
    op.drop_index(op.f("ix_repairs_created_by_user_id"), table_name="repairs")
    op.drop_column("repairs", "internal_cost")
    op.drop_column("repairs", "exit_date")
    op.drop_column("repairs", "created_by_user_id")
    op.drop_constraint("ck_users_user_role_allowed", "users", type_="check")
    op.drop_column("users", "role")
