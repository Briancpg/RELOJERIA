"""initial schema

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-05-18
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_initial_schema"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("is_admin", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
    )
    op.create_index(op.f("ix_users_deleted_at"), "users", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=False)

    op.create_table(
        "repairs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("repair_date", sa.Date(), nullable=False),
        sa.Column("brand", sa.String(length=120), nullable=False),
        sa.Column("model", sa.String(length=120), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("repair_cost", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("watchmaker_percentage", sa.Numeric(precision=5, scale=2), nullable=False),
        sa.Column("profit_amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column(
            "status",
            sa.Enum("pending", "in_progress", "completed", "delivered", "cancelled", name="repair_status", native_enum=False),
            nullable=False,
        ),
        sa.Column("customer_name", sa.String(length=160), nullable=True),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint("profit_amount >= 0", name=op.f("ck_repairs_profit_amount_non_negative")),
        sa.CheckConstraint("repair_cost >= 0", name=op.f("ck_repairs_repair_cost_non_negative")),
        sa.CheckConstraint(
            "watchmaker_percentage >= 0 AND watchmaker_percentage <= 100",
            name=op.f("ck_repairs_percentage_range"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_repairs")),
    )
    op.create_index(op.f("ix_repairs_brand"), "repairs", ["brand"], unique=False)
    op.create_index(op.f("ix_repairs_deleted_at"), "repairs", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_repairs_id"), "repairs", ["id"], unique=False)
    op.create_index(op.f("ix_repairs_model"), "repairs", ["model"], unique=False)
    op.create_index(op.f("ix_repairs_repair_date"), "repairs", ["repair_date"], unique=False)
    op.create_index("ix_repairs_repair_date_status", "repairs", ["repair_date", "status"], unique=False)
    op.create_index(op.f("ix_repairs_status"), "repairs", ["status"], unique=False)

    op.create_table(
        "repair_images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("repair_id", sa.Integer(), nullable=False),
        sa.Column("r2_key", sa.String(length=500), nullable=False),
        sa.Column("file_name", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=100), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("public_url", sa.String(length=700), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["repair_id"], ["repairs.id"], name=op.f("fk_repair_images_repair_id_repairs"), ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_repair_images")),
        sa.UniqueConstraint("r2_key", name=op.f("uq_repair_images_r2_key")),
    )
    op.create_index(op.f("ix_repair_images_deleted_at"), "repair_images", ["deleted_at"], unique=False)
    op.create_index(op.f("ix_repair_images_id"), "repair_images", ["id"], unique=False)
    op.create_index(op.f("ix_repair_images_repair_id"), "repair_images", ["repair_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_repair_images_repair_id"), table_name="repair_images")
    op.drop_index(op.f("ix_repair_images_id"), table_name="repair_images")
    op.drop_index(op.f("ix_repair_images_deleted_at"), table_name="repair_images")
    op.drop_table("repair_images")
    op.drop_index(op.f("ix_repairs_status"), table_name="repairs")
    op.drop_index("ix_repairs_repair_date_status", table_name="repairs")
    op.drop_index(op.f("ix_repairs_repair_date"), table_name="repairs")
    op.drop_index(op.f("ix_repairs_model"), table_name="repairs")
    op.drop_index(op.f("ix_repairs_id"), table_name="repairs")
    op.drop_index(op.f("ix_repairs_deleted_at"), table_name="repairs")
    op.drop_index(op.f("ix_repairs_brand"), table_name="repairs")
    op.drop_table("repairs")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_index(op.f("ix_users_deleted_at"), table_name="users")
    op.drop_table("users")

