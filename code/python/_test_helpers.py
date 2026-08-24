"""
Shared test helpers for documentation code examples.

Centralizes the private `_Galtea__client` workaround for API calls that the
SDK does not yet expose publicly. When the SDK adds these methods, update
only this file. Also holds the polling waits the snippets share, so a
generation failure reports the same way everywhere.
"""

import time

from galtea import Dataset, DatasetStatus, Galtea

# A generation job in one of these states will never write a file URI.
_TERMINAL_DATASET_FAILURES = frozenset({DatasetStatus.FAILED.value, DatasetStatus.CANCELLED.value})


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
            "capabilities": capabilities,
            "inabilities": inabilities,
            "policies": policies,
        },
    )
    return response.json()["id"]


def wait_for_dataset_ready(
    galtea: Galtea,
    dataset_id: str,
    *,
    label: str = "dataset",
    timeout_seconds: int = 120,
    poll_seconds: int = 1,
) -> Dataset:
    """Poll a dataset until its generation job publishes the file URI.

    Stops on the first terminal failure status and reports the reason the API
    recorded. Polling only ``uri`` cannot tell a failed job from a slow one, so a
    broken job would otherwise burn the whole timeout and then blame the wait.

    ``timeout_seconds`` is wall clock, not a poll count: request latency eats into
    the budget rather than extending it, so a slow API yields fewer polls over the
    same ceiling.
    """
    deadline = time.monotonic() + timeout_seconds
    dataset = galtea.datasets.get(dataset_id=dataset_id)
    while True:
        if dataset.uri:
            return dataset

        status = str(getattr(dataset.status, "value", dataset.status) or "UNKNOWN").upper()
        if status in _TERMINAL_DATASET_FAILURES:
            raise ValueError(
                f"Generation of {label} {dataset_id} ended as {status}: {dataset.error or 'no reason reported'}"
            )
        if time.monotonic() >= deadline:
            raise ValueError(
                f"Generation of {label} {dataset_id} produced no file URI within {timeout_seconds}s. "
                f"Last status: {status}. Error: {dataset.error or 'none'}"
            )

        print(f"Waiting for {label} file to be ready (status: {status})...")
        time.sleep(poll_seconds)
        dataset = galtea.datasets.get(dataset_id=dataset_id)


def list_users(galtea: Galtea, organization_id: str, limit: int = 1) -> list[dict]:
    """Fetch users by organization via direct API call.

    The SDK does not expose a ``users.list()`` method.
    """
    client = _get_client(galtea)
    response = client.get("users", params={"organizationIds": organization_id, "limit": limit})
    return response.json()
