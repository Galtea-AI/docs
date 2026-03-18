from datetime import datetime

from _test_helpers import create_test_product
from galtea import Galtea

# Initialize Galtea SDK
galtea = Galtea(api_key="YOUR_API_KEY")

run_identifier: str = datetime.now().strftime("%Y%m%d%H%M%S%f")

# Create product via helper (SDK doesn't expose products.create)
product_id: str = create_test_product(
    galtea,
    name=f"docs-human-eval-product-{run_identifier}",
    description="Product for human evaluation tutorial",
)

# Create a version
version = galtea.versions.create(product_id=product_id, name=f"v-{run_identifier}")
version_id: str = version.id

# Create a test with test cases
test = galtea.tests.create(
    product_id=product_id,
    name=f"human-eval-tutorial-test-{run_identifier}",
    type="ACCURACY",
    test_file_path="path/to/accuracy_test.csv",
)
test_id: str = test.id

# Setup: create a user group for the human evaluation metric
user_group = galtea.user_groups.create(
    name="quality-reviewers-" + run_identifier,
    description="Quality reviewers for human evaluation",
)
if user_group is None:
    raise ValueError("Failed to create user group")
user_group_id: str = user_group.id

# @start create_human_metric
# Create a human evaluation metric with user groups
metric = galtea.metrics.create(
    name="human_helpfulness_" + run_identifier,
    source="human_evaluation",
    judge_prompt=(
        "Review the actual output and score it based on helpfulness and accuracy. "
        "Score 1 if the response is helpful and accurate. "
        "Score 0 if it is unhelpful or incorrect."
    ),
    evaluation_params=["input", "actual_output"],
    user_group_ids=[user_group_id],
    tags=["human", "helpfulness"],
    description="A human evaluation metric scored by quality reviewers.",
)

if metric is None:
    raise ValueError("Failed to create metric")
print(f"Created metric: {metric.name} (ID: {metric.id})")
# @end create_human_metric


# @start run_evaluations
# Simulate your product's response
def your_product_function(input_prompt: str) -> str:
    return f"Model response to: {input_prompt}"


# Fetch test cases and run evaluations
test_cases = galtea.test_cases.list(test_id=test_id)
print(f"Found {len(test_cases)} test cases")

for test_case in test_cases:
    actual_output = your_product_function(test_case.input)

    # Create session and evaluate — since the metric source is human_evaluation,
    # the evaluation status will be PENDING_HUMAN instead of running an LLM judge
    session = galtea.sessions.create(version_id=version_id, test_case_id=test_case.id)
    galtea.inference_results.create_and_evaluate(
        session_id=session.id,
        output=actual_output,
        metrics=[{"name": metric.name}],
    )

print("All evaluations submitted!")
# @end run_evaluations


# @start list_pending_evaluations
# List evaluations to confirm they are PENDING_HUMAN
sessions = galtea.sessions.list(version_id=version_id, test_id=test_id)
if sessions:
    evaluations = galtea.evaluations.list(session_id=sessions[0].id)
    for evaluation in evaluations:
        print(f"Evaluation {evaluation.id}: status={evaluation.status}")
# @end list_pending_evaluations
