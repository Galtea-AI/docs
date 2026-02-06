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
        "name": f"docs-github-actions-product-{run_identifier}",
        "description": "Product for GitHub Actions integration documentation",
        "securityBoundaries": "none",
        "capabilities": "answer questions",
        "inabilities": "none",
    },
)
products = galtea.products.list(limit=1)
product = products[0]
PRODUCT_ID: str = product.id

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

metrics = ["Factual Accuracy"]

# Placeholder for where the model's answer would be generated
# In a real scenario, this would involve calling your model with test_case.input
model_answer = "This is a placeholder model answer."

for test_case in test_cases:
    galtea.evaluations.create_single_turn(
        version_id=version.id,
        test_case_id=test_case.id,
        metrics=metrics,
        actual_output=model_answer,
    )
# @end github_actions_workflow

print(f"Evaluated {len(test_cases)} test cases against version {version.name}")

# Cleanup
galtea.products.delete(product_id=PRODUCT_ID)
