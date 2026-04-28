"""
Tutorial: Create a Custom Test
Demonstrates how to create and upload custom tests using the SDK.
"""

from datetime import datetime

from galtea import Galtea

from _test_helpers import create_test_product

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea = Galtea(api_key="YOUR_API_KEY")

# Register a product for this demo
product_id = create_test_product(galtea, name="Test Creation Demo " + run_identifier)


# @start upload_existing_test
# Upload a pre-existing test file to the Galtea Platform
test = galtea.tests.create(
    name="financial-qa-test-" + run_identifier,
    type="ACCURACY",
    product_id=product_id,
    test_file_path="path/to/accuracy_test.csv",
)
# @end upload_existing_test

if test is None:
    raise ValueError("test is None")

print(f"Test created with ID: {test.id}")


# @start generate_from_knowledge
# Generate a test from a knowledge base file (PDF, TXT, etc.)
generated_test = galtea.tests.create(
    name="generated-financial-qa-test-" + run_identifier,
    type="ACCURACY",
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
