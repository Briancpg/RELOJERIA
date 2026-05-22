"""add repair envelope raw transcription

Revision ID: 0005_repair_raw_transcription
Revises: 0004_repair_envelope_date
Create Date: 2026-05-21
"""
from alembic import op
import sqlalchemy as sa

revision = "0005_repair_raw_transcription"
down_revision = "0004_repair_envelope_date"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("repairs", sa.Column("envelope_raw_transcription", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("repairs", "envelope_raw_transcription")
