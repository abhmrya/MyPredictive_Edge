from typing import Any
from uuid import UUID, uuid4

from app.core.exceptions import BadRequestError, AppError
from app.modules.organizations.schemas import OrganizationCreate
from app.services.supabase_client import async_supabase


def generate_slug(name: str) -> str:
    """
    Convert organization name into a URL-friendly slug.

    Example:
        "Bluethink Technologies" -> "bluethink-technologies"
    """

    slug = name.strip().lower()

    # Replace spaces with hyphens
    slug = "-".join(slug.split())

    # Keep only safe characters
    slug = "".join(
        character
        for character in slug
        if character.isalnum() or character == "-"
    )

    # Remove duplicate hyphens
    while "--" in slug:
        slug = slug.replace("--", "-")

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    if not slug:
        raise BadRequestError(
            "Organization name cannot produce a valid slug."
        )

    return slug


async def create_organization(
    organization: OrganizationCreate,
    current_user: dict[str, Any],
) -> dict[str, Any]:

    # ---------------------------------------------------------
    # 1. Get authenticated user from JWT
    # ---------------------------------------------------------

    user_id = current_user.get("user_id")

    if not user_id:
        raise BadRequestError(
            "Authenticated user ID is missing."
        )

    try:
        user_uuid = UUID(user_id)
    except (ValueError, TypeError):
        raise BadRequestError(
            "Invalid authenticated user ID."
        )

    # ---------------------------------------------------------
    # 2. Generate organization slug
    # ---------------------------------------------------------

    slug = generate_slug(organization.name)

    # ---------------------------------------------------------
    # 3. Check whether slug already exists
    # ---------------------------------------------------------

    try:
        existing = (
            await async_supabase
            .table("organizations")
            .select("id")
            .eq("slug", slug)
            .limit(1)
            .execute()
        )

        if existing.data:
            raise BadRequestError(
                "An organization with this name already exists."
            )

        # -----------------------------------------------------
        # 4. Create organization
        # -----------------------------------------------------

        organization_id = uuid4()

        organization_payload = {
            "id": str(organization_id),
            "name": organization.name.strip(),
            "slug": slug,
            "created_by_user_id": str(user_uuid),
            "is_active": True,
        }

        organization_result = (
            await async_supabase
            .table("organizations")
            .insert(organization_payload)
            .execute()
        )

        if not organization_result.data:
            raise AppError(
                "Failed to create organization."
            )

        created_organization = organization_result.data[0]

        # -----------------------------------------------------
        # 5. Add creator as organization member
        # -----------------------------------------------------

        member_payload = {
            "organization_id": str(organization_id),
            "user_id": str(user_uuid),
        }

        member_result = (
            await async_supabase
            .table("organization_members")
            .insert(member_payload)
            .execute()
        )

        if not member_result.data:
            # Important:
            # Organization was created but membership failed.
            #
            # With the current Supabase client approach, these
            # two requests are not automatically one transaction.
            # We will improve transactional behavior separately.
            raise AppError(
                "Organization created, but membership setup failed."
            )

        # -----------------------------------------------------
        # 6. Return created organization
        # -----------------------------------------------------

        return created_organization

    except (BadRequestError, AppError):
        raise

    except Exception as e:
        print(
            "ORGANIZATION CREATE ERROR:",
            type(e).__name__,
            str(e),
        )
        raise AppError(
            "Failed to create organization."
        )