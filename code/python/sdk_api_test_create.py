from datetime import datetime

from galtea import Galtea

galtea = Galtea(api_key="YOUR_API_KEY")

run_identifier: str = datetime.now().strftime("%Y%m%d%H%M%S%f")

# Create product via direct API call (SDK doesn't expose products.create)
client = getattr(galtea, "_Galtea__client", None)
if client is None:
    raise ValueError("Could not access Galtea client for direct API call")
client.post(
    "products",
    json={
        "name": f"docs-test-create-product-{run_identifier}",
        "description": "Product for test creation documentation",
        "securityBoundaries": "Do not reveal sensitive data",
        "capabilities": "Answer questions about products",
        "inabilities": "Cannot process payments",
    },
)
products = galtea.products.list(limit=1)
product = products[0]
product_id: str = product.id

# @start quality_test
test = galtea.tests.create(
    name=f"accuracy-test-{run_identifier}",
    type="ACCURACY",
    product_id=product_id,
    ground_truth_file_path="path/to/knowledge.md",
    language="english",
    max_test_cases=100,
)
# @end quality_test
print(f"Created accuracy test: {test.id}")

# @start red_teaming
security_test = galtea.tests.create(
    name=f"security-test-{run_identifier}",
    type="SECURITY",
    product_id=product_id,
    variants=["Toxicity"],
    strategies=["Original", "Roleplay", "Base64"],
    max_test_cases=50,
)
# @end red_teaming
print(f"Created security test: {security_test.id}")

# @start scenario_test
behavior_test = galtea.tests.create(
    name=f"behavior-test-{run_identifier}",
    type="BEHAVIOR",
    product_id=product_id,
    custom_user_focus="A medical professional specialized in dementia with more than 15 years in the field",
    language="english",
    max_test_cases=25,
    strategies=["written"],
)
# @end scenario_test
print(f"Created behavior test: {behavior_test.id}")

# @start quality_custom_test_from_csv
csv_test = galtea.tests.create(
    name=f"csv-accuracy-test-{run_identifier}",
    type="ACCURACY",
    product_id=product_id,
    test_file_path="path/to/accuracy_test.csv",
)
# @end quality_custom_test_from_csv
print(f"Created CSV accuracy test: {csv_test.id}")

# Cleanup
galtea.products.delete(product_id=product_id)
