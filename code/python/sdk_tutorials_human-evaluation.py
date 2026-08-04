from datetime import datetime

from requests.exceptions import HTTPError

from _test_helpers import create_test_product
from galtea import Galtea

# Initialize Galtea SDK
galtea = Galtea(api_key="YOUR_API_KEY")

run_identifier: str = datetime.now().strftime("%Y%m%d%H%M%S%f")

# Register product via helper (SDK doesn't expose products.create)
product_id: str = create_test_product(
    galtea,
    name=f"docs-human-eval-product-{run_identifier}",
    description="Product for human evaluation tutorial",
)

# Create a version
version = galtea.versions.create(product_id=product_id, name=f"v-{run_identifier}")
version_id: str = version.id

# Create a dataset with test cases
dataset = galtea.datasets.create(
    product_id=product_id,
    name=f"human-eval-tutorial-test-{run_identifier}",
    type="ACCURACY",
    dataset_file_path="path/to/accuracy_dataset.csv",
)
dataset_id: str = dataset.id

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


# Link the human evaluation metric and the dataset to a specification, so that
# `evaluations.run()` below can discover both. This setup is done once per product.
specification = galtea.specifications.create(
    product_id=product_id,
    name="Answers must be helpful and accurate",
    description="The assistant answers helpfully and accurately, as judged by a human reviewer.",
    type="POLICY",
    dataset_type="ACCURACY",
    test_variant="other",
    metric_ids=[metric.id],
)
if specification is None:
    raise ValueError("Failed to create specification")
galtea.specifications.link_datasets(specification_id=specification.id, dataset_ids=[dataset_id])


# @start run_evaluations
# Simulate your product's response
def your_product_function(user_message: str) -> str:
    return f"Model response to: {user_message}"


# One call resolves the specifications, their datasets and metrics, runs your product on
# every test case, and submits the results. Since the metric source is human_evaluation,
# each evaluation lands in PENDING_HUMAN instead of running an LLM judge.
result = galtea.evaluations.run(version_id=version_id, agent=your_product_function)

print(f"Submitted evaluations for {result['testCaseCount']} test cases")
# @end run_evaluations

# Guard the gate itself: `run()` returns testCaseCount 0 and raises nothing when the
# specification resolves no datasets, so without this the snippet would stay green while
# the PENDING_HUMAN check below silently degrades into a no-op.
if result["testCaseCount"] == 0:
    raise ValueError("evaluations.run() resolved no test cases — specification linking is broken")


# @start list_pending_evaluations
# List evaluations to confirm they are PENDING_HUMAN
sessions = galtea.sessions.list(version_id=version_id, dataset_id=dataset_id)
if sessions:
    evaluations = galtea.evaluations.list(session_id=sessions[0].id)
    for evaluation in evaluations:
        print(f"Evaluation {evaluation.id}: status={evaluation.status}")
# @end list_pending_evaluations

# Cleanup. The product now owns a specification, so guard the delete: an unguarded 500 here
# would abort before the metric and the user group are removed, leaking both in the real org
# on every nightly live run.
try:
    galtea.products.delete(product_id=product_id)
except HTTPError as e:
    # Known API issue: cascade soft-delete may hit unique constraint on specifications
    if e.response.status_code != 500:
        raise
galtea.metrics.delete(metric_id=metric.id)
galtea.user_groups.delete(user_group_id=user_group_id)
