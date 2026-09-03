"""add organization roles and permissions

Revision ID: 0dc9f4f2a125
Revises: c5f0057e127f
Create Date: 2026-09-03 14:05:55.450391

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "0dc9f4f2a125"
down_revision: Union[str, Sequence[str], None] = "c5f0057e127f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Create organization_roles table
    op.create_table(
        "organization_roles",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "organization_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "name",
            sa.String(length=100),
            nullable=False,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["organization_id"],
            ["organizations.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "organization_id",
            "name",
            name="uq_organization_role_name",
        ),
    )

    op.create_index(
        "ix_organization_roles_organization_id",
        "organization_roles",
        ["organization_id"],
        unique=False,
    )

    # 2. Create organization_role_permissions table
    op.create_table(
        "organization_role_permissions",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("gen_random_uuid()"),
            nullable=False,
        ),
        sa.Column(
            "role_id",
            sa.UUID(),
            nullable=False,
        ),
        sa.Column(
            "permission",
            sa.String(length=150),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["role_id"],
            ["organization_roles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "role_id",
            "permission",
            name="uq_role_permission",
        ),
    )

    op.create_index(
        "ix_organization_role_permissions_role_id",
        "organization_role_permissions",
        ["role_id"],
        unique=False,
    )

    # 3. Add role_id temporarily as nullable
    op.add_column(
        "organization_members",
        sa.Column(
            "role_id",
            sa.UUID(),
            nullable=True,
        ),
    )

    # 4. Create ADMIN role for every existing organization
    op.execute(
        """
        INSERT INTO organization_roles (
            id,
            organization_id,
            name,
            description,
            is_active
        )
        SELECT
            gen_random_uuid(),
            id,
            'ADMIN',
            'Default organization administrator role',
            true
        FROM organizations
        """
    )

    # 5. Assign ADMIN role to existing organization members
    op.execute(
        """
        UPDATE organization_members AS members
        SET role_id = roles.id
        FROM organization_roles AS roles
        WHERE roles.organization_id = members.organization_id
          AND roles.name = 'ADMIN'
        """
    )

    # 6. Ensure every existing member received a role
    op.execute(
        """
        DO $$
        BEGIN
            IF EXISTS (
                SELECT 1
                FROM organization_members
                WHERE role_id IS NULL
            ) THEN
                RAISE EXCEPTION
                    'RBAC migration failed: some organization members have no role';
            END IF;
        END
        $$
        """
    )

    # 7. Make role_id NOT NULL
    op.alter_column(
        "organization_members",
        "role_id",
        existing_type=sa.UUID(),
        nullable=False,
    )

    # 8. Add index
    op.create_index(
        "ix_organization_members_role_id",
        "organization_members",
        ["role_id"],
        unique=False,
    )

    # 9. Add foreign key
    op.create_foreign_key(
        "fk_organization_members_role_id",
        "organization_members",
        "organization_roles",
        ["role_id"],
        ["id"],
        ondelete="RESTRICT",
    )


def downgrade() -> None:
    # Remove foreign key
    op.drop_constraint(
        "fk_organization_members_role_id",
        "organization_members",
        type_="foreignkey",
    )

    # Remove index
    op.drop_index(
        "ix_organization_members_role_id",
        table_name="organization_members",
    )

    # Remove role_id
    op.drop_column(
        "organization_members",
        "role_id",
    )

    # Remove permission table
    op.drop_index(
        "ix_organization_role_permissions_role_id",
        table_name="organization_role_permissions",
    )

    op.drop_table("organization_role_permissions")

    # Remove role table
    op.drop_index(
        "ix_organization_roles_organization_id",
        table_name="organization_roles",
    )

    op.drop_table("organization_roles")