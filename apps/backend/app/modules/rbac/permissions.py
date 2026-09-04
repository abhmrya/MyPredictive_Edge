class Permissions:
    # Organization
    ORGANIZATION_VIEW = "organization.view"
    ORGANIZATION_MANAGE = "organization.manage"

    # Inventory
    INVENTORY_VIEW = "inventory.view"
    INVENTORY_MANAGE = "inventory.manage"

    # Alerts
    ALERTS_VIEW = "alerts.view"
    ALERTS_MANAGE = "alerts.manage"

    # Decisions
    DECISIONS_VIEW = "decisions.view"
    DECISIONS_APPROVE = "decisions.approve"
    DECISIONS_REJECT = "decisions.reject"
    DECISIONS_OVERRIDE = "decisions.override"


# System-controlled permission catalog.
# Roles are dynamic, but permissions are predefined by the system.
VALID_PERMISSIONS = frozenset(
    {
        Permissions.ORGANIZATION_VIEW,
        Permissions.ORGANIZATION_MANAGE,
        Permissions.INVENTORY_VIEW,
        Permissions.INVENTORY_MANAGE,
        Permissions.ALERTS_VIEW,
        Permissions.ALERTS_MANAGE,
        Permissions.DECISIONS_VIEW,
        Permissions.DECISIONS_APPROVE,
        Permissions.DECISIONS_REJECT,
        Permissions.DECISIONS_OVERRIDE,
    }
)