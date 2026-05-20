"""Add image type to repair images.

Revision ID: 0002_repair_image_type
Revises: 0001_initial_schema
Create Date: 2026-05-19 00:00:00.000000
"""

from alembic import op
import sqlalchemy as sa


revision = "0002_repair_image_type"
down_revision = "0001_initial_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "repair_images",
        sa.Column("image_type", sa.String(length=30), nullable=False, server_default="watch"),
    )
    op.create_index(op.f("ix_repair_images_image_type"), "repair_images", ["image_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_repair_images_image_type"), table_name="repair_images")
    op.drop_column("repair_images", "image_type")
