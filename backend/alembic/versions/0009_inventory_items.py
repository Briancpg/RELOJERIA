"""add inventory items

Revision ID: 0009_inventory_items
Revises: 0008_repair_customer_phone
Create Date: 2026-05-25
"""
from alembic import op
import sqlalchemy as sa

revision = "0009_inventory_items"
down_revision = "0008_repair_customer_phone"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "inventory_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("reference", sa.String(length=80), nullable=False),
        sa.Column("name", sa.String(length=160), nullable=False),
        sa.Column("category", sa.String(length=80), nullable=False),
        sa.Column("brand", sa.String(length=120), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("stock_quantity", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("minimum_stock", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("unit_price", sa.Numeric(12, 2), nullable=False, server_default="0"),
        sa.Column("location", sa.String(length=120), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("stock_quantity >= 0", name=op.f("ck_inventory_items_inventory_stock_non_negative")),
        sa.CheckConstraint("minimum_stock >= 0", name=op.f("ck_inventory_items_inventory_minimum_stock_non_negative")),
        sa.CheckConstraint("unit_price >= 0", name=op.f("ck_inventory_items_inventory_unit_price_non_negative")),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_inventory_items")),
    )
    op.create_index(op.f("ix_inventory_items_id"), "inventory_items", ["id"], unique=False)
    op.create_index("ix_inventory_items_reference", "inventory_items", ["reference"], unique=True)
    op.create_index(op.f("ix_inventory_items_name"), "inventory_items", ["name"], unique=False)
    op.create_index(op.f("ix_inventory_items_category"), "inventory_items", ["category"], unique=False)
    op.create_index(op.f("ix_inventory_items_brand"), "inventory_items", ["brand"], unique=False)
    op.create_index("ix_inventory_items_category_brand", "inventory_items", ["category", "brand"], unique=False)
    op.create_index(op.f("ix_inventory_items_deleted_at"), "inventory_items", ["deleted_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_inventory_items_deleted_at"), table_name="inventory_items")
    op.drop_index("ix_inventory_items_category_brand", table_name="inventory_items")
    op.drop_index(op.f("ix_inventory_items_brand"), table_name="inventory_items")
    op.drop_index(op.f("ix_inventory_items_category"), table_name="inventory_items")
    op.drop_index(op.f("ix_inventory_items_name"), table_name="inventory_items")
    op.drop_index("ix_inventory_items_reference", table_name="inventory_items")
    op.drop_index(op.f("ix_inventory_items_id"), table_name="inventory_items")
    op.drop_table("inventory_items")
