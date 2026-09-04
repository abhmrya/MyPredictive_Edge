from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID

from app.database.core import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class OrganizationRole(Base):
    __tablename__ = "organization_roles"

    __table_args__ = (
        UniqueConstraint(
            "organization_id",
            "name",
            name="uq_organization_role_name",
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )

    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "organizations.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    name = Column(
        String(100),
        nullable=False,
    )

    description = Column(
        Text,
        nullable=True,
    )

    is_active = Column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        server_default=text("now()"),
    )

    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        onupdate=utc_now,
        server_default=text("now()"),
    )


class OrganizationRolePermission(Base):
    __tablename__ = "organization_role_permissions"

    __table_args__ = (
        UniqueConstraint(
            "role_id",
            "permission",
            name="uq_role_permission",
        ),
    )

    id = Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
        server_default=text("gen_random_uuid()"),
    )

    role_id = Column(
        UUID(as_uuid=True),
        ForeignKey(
            "organization_roles.id",
            ondelete="CASCADE",
        ),
        nullable=False,
        index=True,
    )

    permission = Column(
        String(150),
        nullable=False,
    )

    created_at = Column(
        DateTime(timezone=True),
        nullable=False,
        default=utc_now,
        server_default=text("now()"),
    )