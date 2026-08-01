from datetime import datetime

from _test_helpers import create_test_product
from galtea import Galtea

galtea = Galtea(api_key="YOUR_API_KEY")

run_identifier: str = datetime.now().strftime("%Y%m%d%H%M%S%f")

# Register product via helper (SDK doesn't expose products.create)
PRODUCT_ID: str = create_test_product(
    galtea,
    name=f"docs-github-actions-product-{run_identifier}",
    description="Product for GitHub Actions integration documentation",
)

# Create a test with test cases
test = galtea.tests.create(
    product_id=PRODUCT_ID,
    name=f"github-actions-test-{run_identifier}",
    type="ACCURACY",
    test_file_path="path/to/accuracy_test.csv",
)

# @start github_actions_workflow
# GitHub Actions workflow environment variables would be:
# GALTEA_API_KEY, GALTEA_PRODUCT_ID, GALTEA_TEST_NAME

version = galtea.versions.create(name=f"v1.X-{run_identifier}", product_id=PRODUCT_ID)

test_cases = galtea.test_cases.list(test_id=test.id)

metrics = [{"name": "Factual Accuracy"}]

# Placeholder for where the model's answer would be generated
# In a real scenario, this would involve calling your model with test_case.input
model_answer = "This is a placeholder model answer."

for test_case in test_cases:
    session = galtea.sessions.create(version_id=version.id, test_case_id=test_case.id)
    galtea.inference_results.create_and_evaluate(
        session_id=session.id,
        output=model_answer,
        metrics=metrics,
    )
# @end github_actions_workflow

print(f"Evaluated {len(test_cases)} test cases against version {version.name}")

# Cleanup
galtea.products.delete(product_id=PRODUCT_ID)
