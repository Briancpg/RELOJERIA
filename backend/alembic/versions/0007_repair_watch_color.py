"""add repair watch color

Revision ID: 0007_repair_watch_color
Revises: 0006_repair_extra_fields
Create Date: 2026-05-22
"""
from alembic import op
import sqlalchemy as sa

revision = "0007_repair_watch_color"
down_revision = "0006_repair_extra_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("repairs", sa.Column("watch_color", sa.String(length=80), nullable=True))


def downgrade() -> None:
    op.drop_column("repairs", "watch_color")
