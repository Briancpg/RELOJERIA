"""add repair customer phone

Revision ID: 0008_repair_customer_phone
Revises: 0007_repair_watch_color
Create Date: 2026-05-22
"""
from alembic import op
import sqlalchemy as sa

revision = "0008_repair_customer_phone"
down_revision = "0007_repair_watch_color"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("repairs", sa.Column("customer_phone", sa.String(length=40), nullable=True))


def downgrade() -> None:
    op.drop_column("repairs", "customer_phone")
