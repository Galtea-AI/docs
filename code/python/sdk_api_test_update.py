from datetime import datetime

from galtea import Galtea

from _test_helpers import create_test_product

galtea = Galtea(api_key="YOUR_API_KEY")

run_identifier: str = datetime.now().strftime("%Y%m%d%H%M%S%f")

product_id: str = create_test_product(
    galtea,
    name=f"docs-test-update-product-{run_identifier}",
    description="Product for test update documentation",
)

test = galtea.tests.create(
    name=f"original-test-{run_identifier}",
    type="SECURITY",
    product_id=product_id,
    variants=["toxicity"],
    strategies=["original"],
    max_test_cases=5,
    metadata={"owner": "qa-team", "ticket": "QA-100"},
)

# @start rename_test
renamed = galtea.tests.update(
    test_id=test.id,
    name=f"renamed-test-{run_identifier}",
)
# @end rename_test
print(f"Renamed test to: {renamed.name}")

# @start update_metadata
with_new_metadata = galtea.tests.update(
    test_id=test.id,
    metadata={"owner": "platform-team", "ticket": "QA-200", "priority": "high"},
)
# @end update_metadata
print(f"Updated metadata: {with_new_metadata.metadata}")

# @start update_both
updated = galtea.tests.update(
    test_id=test.id,
    name=f"final-test-{run_identifier}",
    metadata={"owner": "platform-team", "archived": True},
)
# @end update_both
print(f"Updated both fields: name={updated.name}, metadata={updated.metadata}")

# Cleanup
galtea.products.delete(product_id=product_id)
