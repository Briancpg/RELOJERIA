"""add repair envelope date

Revision ID: 0004_repair_envelope_date
Revises: 0003_remove_completed_status
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa

revision = "0004_repair_envelope_date"
down_revision = "0003_remove_completed_status"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("repairs", sa.Column("envelope_date", sa.Date(), nullable=True))
    op.create_index(op.f("ix_repairs_envelope_date"), "repairs", ["envelope_date"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_repairs_envelope_date"), table_name="repairs")
    op.drop_column("repairs", "envelope_date")
