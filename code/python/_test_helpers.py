"""
Shared test helpers for documentation code examples.

Centralizes the private `_Galtea__client` workaround for API calls that the
SDK does not yet expose publicly. When the SDK adds these methods, update
only this file.
"""

from galtea import Galtea


def _get_client(galtea: Galtea):
    """Return the internal HTTP client, raising if unavailable."""
    client = getattr(galtea, "_Galtea__client", None)
    if client is None:
        raise ValueError("Could not access Galtea client for direct API call")
    return client


def create_test_product(
    galtea: Galtea,
    name: str,
    description: str = "Test product created for documentation examples",
    *,
    security_boundaries: str = "none",
    capabilities: str = "answer questions",
    inabilities: str = "none",
    policies: str = "",
) -> str:
    """Create a test product via direct API call and return its ID.

    The SDK does not expose ``products.create()``, so this helper uses the
    internal HTTP client.  All doc-example scripts should call this function
    instead of accessing ``_Galtea__client`` directly.
    """
    client = _get_client(galtea)
    response = client.post(
        "products",
        json={
            "name": name,
            "description": description,
            "securityBoundaries": security_boundaries,
            "capabilities": capabilities,
            "inabilities": inabilities,
            "policies": policies,
        },
    )
    return response.json()["id"]


def list_users(galtea: Galtea, organization_id: str, limit: int = 1) -> list[dict]:
    """Fetch users by organization via direct API call.

    The SDK does not expose a ``users.list()`` method.
    """
    client = _get_client(galtea)
    response = client.get(
        "users", params={"organizationIds": organization_id, "limit": limit}
    )
    return response.json()
