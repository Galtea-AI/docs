"""
Tutorial: Create a Custom Test
Demonstrates how to create and upload custom tests using the SDK.
"""

from datetime import datetime

from galtea import Galtea

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea = Galtea(api_key="YOUR_API_KEY")

# Create a product for this demo
client = getattr(galtea, "_Galtea__client", None)
if client is None:
    raise ValueError("Could not access Galtea client for direct API call")
response = client.post(
    "products",
    json={
        "name": "Test Creation Demo " + run_identifier,
        "description": "Demo product for test creation tutorial",
        "capabilities": "Demo capabilities",
        "inabilities": "Demo inabilities",
        "securityBoundaries": "Demo security boundaries",
    },
)
product_id = response.json()["id"]


# @start upload_existing_test
# Upload a pre-existing test file to the Galtea Platform
test = galtea.tests.create(
    name="financial-qa-test-" + run_identifier,
    type="QUALITY",
    product_id=product_id,
    test_file_path="path/to/quality_test.csv",
)
# @end upload_existing_test

if test is None:
    raise ValueError("test is None")

print(f"Test created with ID: {test.id}")


# @start generate_from_knowledge
# Generate a test from a knowledge base file (PDF, TXT, etc.)
generated_test = galtea.tests.create(
    name="generated-financial-qa-test-" + run_identifier,
    type="QUALITY",
    product_id=product_id,
    ground_truth_file_path="path/to/knowledge.md",
    language="english",
    max_test_cases=50,  # Limit the number of generated test cases
)
# @end generate_from_knowledge

if generated_test is None:
    raise ValueError("generated_test is None")

print(f"Test generated from knowledge base with ID: {generated_test.id}")

# === Cleanup ===
galtea.products.delete(product_id=product_id)
