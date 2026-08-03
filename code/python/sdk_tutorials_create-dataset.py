"""
Tutorial: Create a Custom Dataset
Demonstrates how to create and upload custom datasets using the SDK.
"""

from datetime import datetime

from galtea import Galtea

from _test_helpers import create_test_product

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea = Galtea(api_key="YOUR_API_KEY")

# Register a product for this demo
product_id = create_test_product(galtea, name="Test Creation Demo " + run_identifier)


# @start upload_existing_dataset
# Upload a pre-existing dataset file to the Galtea Platform
dataset = galtea.datasets.create(
    name="financial-qa-test-" + run_identifier,
    type="ACCURACY",
    product_id=product_id,
    dataset_file_path="path/to/accuracy_dataset.csv",
)
# @end upload_existing_dataset

if dataset is None:
    raise ValueError("dataset is None")

print(f"Dataset created with ID: {dataset.id}")


# @start generate_from_knowledge
# Generate a dataset from a knowledge base file (PDF, TXT, etc.)
generated_dataset = galtea.datasets.create(
    name="generated-financial-qa-test-" + run_identifier,
    type="ACCURACY",
    product_id=product_id,
    ground_truth_file_path="path/to/knowledge.md",
    language="english",
    max_test_cases=50,  # Limit the number of generated test cases
)
# @end generate_from_knowledge

if generated_dataset is None:
    raise ValueError("generated_dataset is None")

print(f"Dataset generated from knowledge base with ID: {generated_dataset.id}")

# === Cleanup ===
galtea.products.delete(product_id=product_id)
