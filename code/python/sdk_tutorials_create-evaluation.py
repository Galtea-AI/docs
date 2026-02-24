from datetime import datetime

from galtea import Galtea

# Initialize Galtea SDK
galtea = Galtea(api_key="YOUR_API_KEY")

run_identifier: str = datetime.now().strftime("%Y%m%d%H%M%S%f")

# Create product via direct API call (SDK doesn't expose products.create)
client = getattr(galtea, "_Galtea__client", None)
if client is None:
    raise ValueError("Could not access Galtea client for direct API call")
client.post(
    "products",
    json={
        "name": f"docs-create-eval-product-{run_identifier}",
        "description": "Product for create evaluation tutorial",
        "securityBoundaries": "none",
        "capabilities": "answer questions",
        "inabilities": "none",
    },
)
products = galtea.products.list(limit=1)
product = products[0]
product_id: str = product.id

# Create version and test
version = galtea.versions.create(product_id=product_id, name=f"v-{run_identifier}")
version_id: str = version.id

test = galtea.tests.create(
    product_id=product_id,
    name=f"create-eval-tutorial-test-{run_identifier}",
    type="ACCURACY",
    test_file_path="path/to/accuracy_test.csv",
)
test_id: str = test.id

# --- Configuration ---
METRICS_TO_EVALUATE = [
    {"name": "Factual Accuracy"},
    {"name": "Role Adherence"},
]


# @start product_function
# --- Your Product's Logic (Placeholder) ---
# In a real scenario, this would call your actual AI model or API
def your_product_function(input_prompt: str, context: str = None) -> str:
    # Your model's inference logic goes here
    # For this example, we'll return a simple placeholder response
    return f"Model response to: {input_prompt}"


# @end product_function

# @start create_evaluations
# 1. Fetch the test cases for the specified test
test_cases = galtea.test_cases.list(test_id=test_id)
print(f"Found {len(test_cases)} test cases for Test ID: {test_id}")

# 2. Loop through each test case and run an evaluation
for test_case in test_cases:
    # Get your product's actual response to the input
    actual_output = your_product_function(test_case.input)

    # Create the evaluation
    # An evaluation is created implicitly on the first call
    galtea.evaluations.create_single_turn(
        version_id=version_id,
        test_case_id=test_case.id,
        metrics=METRICS_TO_EVALUATE,
        actual_output=actual_output,
    )

print(f"\nAll evaluations submitted for Version ID: {version_id}")
# @end create_evaluations

# Create a specification with linked metrics so the specification-based evaluation works
factual_accuracy = galtea.metrics.get_by_name(name="Factual Accuracy")
if factual_accuracy is None:
    raise ValueError("Could not find 'Factual Accuracy' metric")

galtea.specifications.create(
    product_id=product_id,
    description="The assistant provides factually correct answers to user questions.",
    type="CAPABILITY",
    metric_ids=[factual_accuracy.id],
)

# @start specification_based_evaluation
# 1. List the specifications for your product
specifications = galtea.specifications.list(product_id=product_id)
spec_ids = [spec.id for spec in specifications]
print(f"Found {len(spec_ids)} specifications for product {product_id}")

# 2. Create a session and record an inference result
session = galtea.sessions.create(version_id=version_id, test_case_id=test_cases[0].id)
inference_result = galtea.inference_results.create(
    session_id=session.id,
    input=test_cases[0].input,
    output=your_product_function(test_cases[0].input),
)

# 3. Evaluate using specifications — the API resolves linked metrics automatically
evaluations = galtea.evaluations.create(
    inference_result_id=inference_result.id,
    specification_ids=spec_ids,
)
print(f"Created {len(evaluations)} evaluations from specifications")
# @end specification_based_evaluation

# Cleanup
galtea.products.delete(product_id=product_id)
