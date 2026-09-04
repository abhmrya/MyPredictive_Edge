"""create inventory table

Revision ID: 9c1e5e7d2a11
Revises: 0dc9f4f2a125
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9c1e5e7d2a11"
down_revision: Union[str, Sequence[str], None] = "0dc9f4f2a125"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "inventory",
        sa.Column("id", sa.UUID(), server_default=sa.text("gen_random_uuid()"), nullable=False),
        sa.Column("organization_id", sa.UUID(), nullable=False),
        sa.Column("location_id", sa.UUID(), nullable=False),
        sa.Column("sku", sa.String(length=150), nullable=False),
        sa.Column("stock_level", sa.Integer(), nullable=False),
        sa.Column("safety_stock_level", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["location_id"], ["locations.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("organization_id", "location_id", "sku", name="uq_inventory_org_location_sku"),
        sa.CheckConstraint("stock_level >= 0", name="ck_inventory_stock_nonnegative"),
        sa.CheckConstraint("safety_stock_level >= 0", name="ck_inventory_safety_stock_nonnegative"),
    )
    op.create_index("ix_inventory_organization_id", "inventory", ["organization_id"])
    op.create_index("ix_inventory_location_id", "inventory", ["location_id"])


def downgrade() -> None:
    op.drop_index("ix_inventory_location_id", table_name="inventory")
    op.drop_index("ix_inventory_organization_id", table_name="inventory")
    op.drop_table("inventory")
