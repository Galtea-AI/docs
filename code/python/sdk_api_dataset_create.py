from datetime import datetime

from galtea import Galtea

from _test_helpers import create_test_product

galtea = Galtea(api_key="YOUR_API_KEY")

run_identifier: str = datetime.now().strftime("%Y%m%d%H%M%S%f")

product_id: str = create_test_product(
    galtea,
    name=f"docs-test-create-product-{run_identifier}",
    description="Product for test creation documentation",
    security_boundaries="Do not reveal sensitive data",
    capabilities="Answer questions about products",
    inabilities="Cannot process payments",
)

# @start accuracy_dataset
dataset = galtea.datasets.create(
    name=f"accuracy-test-{run_identifier}",
    type="ACCURACY",
    product_id=product_id,
    ground_truth_file_path="path/to/knowledge.md",
    language="english",
    max_test_cases=100,
)
# @end accuracy_dataset
print(f"Created accuracy test: {dataset.id}")

# @start security_dataset
security_dataset = galtea.datasets.create(
    name=f"security-test-{run_identifier}",
    type="SECURITY",
    product_id=product_id,
    variants=["toxicity"],
    strategies=["original", "role_play", "base64"],
    max_test_cases=50,
)
# @end security_dataset
print(f"Created security test: {security_dataset.id}")

# @start behavior_dataset
behavior_dataset = galtea.datasets.create(
    name=f"behavior-test-{run_identifier}",
    type="BEHAVIOR",
    product_id=product_id,
    custom_user_focus="A medical professional specialized in dementia with more than 15 years in the field",
    language="english",
    max_test_cases=25,
    max_iterations=10,
    strategies=["written"],
)
# @end behavior_dataset
print(f"Created behavior test: {behavior_dataset.id}")

# @start quality_custom_dataset_from_csv
csv_dataset = galtea.datasets.create(
    name=f"csv-accuracy-test-{run_identifier}",
    type="ACCURACY",
    product_id=product_id,
    dataset_file_path="path/to/accuracy_dataset.csv",
)
# @end quality_custom_dataset_from_csv
print(f"Created CSV accuracy test: {csv_dataset.id}")

# Cleanup
galtea.products.delete(product_id=product_id)
