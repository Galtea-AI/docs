"""
SDK API: Session Update - Additional Examples
Demonstrates use cases for the update method.
"""

from datetime import datetime

from galtea import Galtea

from _test_helpers import create_test_product

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea = Galtea(api_key="YOUR_API_KEY")

# Register a product for this demo
product_id = create_test_product(galtea, name="Session Update Demo " + run_identifier)

version = galtea.versions.create(
    name="Version-" + run_identifier,
    product_id=product_id,
    description="Demo version for session update examples",
)
if version is None:
    raise ValueError("version is None")
version_id = version.id

session = galtea.sessions.create(version_id=version_id, is_production=True)
if session is None:
    raise ValueError("session is None")


# @start error_update
try:
    # Your agent logic that might fail
    raise Exception("Connection timeout")
except Exception as e:
    # Record the error in the session
    galtea.sessions.update(
        session_id=session.id,
        error=str(e),
    )
# @end error_update


# @start metadata_update
galtea.sessions.update(
    session_id=session.id,
    metadata={
        "user_tier": "premium",
        "source": "mobile_app",
        "language": "en",
    },
)
# @end metadata_update


# === Cleanup ===
galtea.products.delete(product_id=product_id)
