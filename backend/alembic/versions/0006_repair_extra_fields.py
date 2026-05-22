"""add repair extra operational fields

Revision ID: 0006_repair_extra_fields
Revises: 0005_repair_raw_transcription
Create Date: 2026-05-22
"""
from alembic import op
import sqlalchemy as sa

revision = "0006_repair_extra_fields"
down_revision = "0005_repair_raw_transcription"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("repairs", sa.Column("customer_document_id", sa.String(length=40), nullable=True))
    op.add_column("repairs", sa.Column("watch_specifications", sa.Text(), nullable=True))
    op.add_column("repairs", sa.Column("invoice_number", sa.String(length=80), nullable=True))
    op.add_column("repairs", sa.Column("deposit_amount", sa.Numeric(precision=12, scale=2), nullable=True))
    op.create_check_constraint(
        op.f("ck_repairs_deposit_amount_non_negative"),
        "repairs",
        "deposit_amount IS NULL OR deposit_amount >= 0",
    )


def downgrade() -> None:
    op.drop_constraint(op.f("ck_repairs_deposit_amount_non_negative"), "repairs", type_="check")
    op.drop_column("repairs", "deposit_amount")
    op.drop_column("repairs", "invoice_number")
    op.drop_column("repairs", "watch_specifications")
    op.drop_column("repairs", "customer_document_id")
