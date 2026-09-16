"""
SDK API: Galtea client errors
Demonstrates catching EntityNotFoundException, which every read raises when the
platform holds nothing under the id or name passed.
"""

from datetime import datetime

from _test_helpers import create_test_product
from galtea import EntityNotFoundException, Galtea

galtea = Galtea(api_key="YOUR_API_KEY")

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S%f")

product_id: str = create_test_product(
    galtea,
    name=f"docs-errors-product-{run_identifier}",
    description="Product for the error handling documentation",
    capabilities="Answer questions about geography",
    inabilities="Cannot process payments",
)

version_name = f"v-{run_identifier}"

# @start entity_not_found
try:
    version = galtea.versions.get_by_name(product_id=product_id, version_name=version_name)
except EntityNotFoundException:
    version = galtea.versions.create(product_id=product_id, name=version_name)
# @end entity_not_found

assert version is not None, "the fallback did not produce a version"
assert version.name == version_name, f"expected version {version_name}, got {version.name}"

# The same call now finds it, so the fallback does not run twice.
found = galtea.versions.get_by_name(product_id=product_id, version_name=version_name)
assert found.id == version.id, "get_by_name returned another version"

# === Cleanup ===
galtea.products.delete(product_id=product_id)
