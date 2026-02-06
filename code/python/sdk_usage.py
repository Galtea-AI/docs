"""
SDK Usage Examples
Demonstrates common SDK usage patterns.
"""

from datetime import datetime

# @start importing_the_sdk
from galtea import Galtea

# Initialize client (replace with your real API key)
galtea = Galtea(api_key="YOUR_API_KEY")
# @end importing_the_sdk

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S%f")

# Create a product for this demo via direct API call
client = getattr(galtea, "_Galtea__client", None)
if client is None:
    raise ValueError("Could not access Galtea client for direct API call")
response = client.post(
    "products",
    json={
        "name": "SDK Usage Demo " + run_identifier,
        "description": "Demo product for SDK usage tutorial",
        "capabilities": "Demo capabilities",
        "inabilities": "Demo inabilities",
        "securityBoundaries": "Demo security boundaries",
    },
)
product_id = response.json()["id"]

# Get the product for use in examples
product = galtea.products.get(product_id=product_id)

# @start creating_a_version
# 1) Create a version
version = galtea.versions.create(
    name="v1.0-" + run_identifier,
    product_id=product.id,
    description="Initial version with basic summarization capabilities",
)
# @end creating_a_version

# @start creating_a_test
# 2) Create a test
test = galtea.tests.create(
    name="example-test-tutorial-" + run_identifier,
    type="ACCURACY",
    product_id=product.id,
    ground_truth_file_path="path/to/knowledge.md",  # The ground truth is the knowledge base
    language="english",
)
# @end creating_a_test

# @start creating_a_metric
# 3) Create a standard metric via API
metric_from_api = galtea.metrics.create(
    name="accuracy-" + run_identifier,
    test_type="ACCURACY",
    evaluator_model_name="GPT-4.1",
    source="full_prompt",
    judge_prompt=(
        "Determine whether the output is equivalent to the expected output. "
        'Output: "{actual_output}". Expected Output: "{expected_output}."'
    ),
)


# 4) Create a custom metric entry in the platform, then define local evaluator
metric_from_api_custom = galtea.metrics.create(
    name="keyword-check-" + run_identifier,
    test_type="ACCURACY",
    source="self_hosted",
    description="Checks if the 'actual output' contains the keyword 'expected'.",
)

from galtea import CustomScoreEvaluationMetric  # noqa: E402


class MyKeywordMetric(CustomScoreEvaluationMetric):
    def __init__(self) -> None:
        super().__init__(name="keyword-check-" + run_identifier)

    def measure(self, *args, actual_output: str | None = None, **kwargs) -> float:
        """
        Returns 1.0 if 'expected' is in actual_output, else 0.0.
        """
        if actual_output is None:
            return 0.0
        # @end creating_a_metric
        return 1.0 if "expected" in actual_output else 0.0


# @start launching_evaluations

keyword_metric = MyKeywordMetric()

# 5) Retrieve test cases for the test
test_cases = galtea.test_cases.list(test_id=test.id)

# 6) Run evaluations for each test case (placeholders used for retriever & product)
for test_case in test_cases:
    # Replace the following with your retrieval and product inference functions
    retrieval_context = None  # your_retriever_function(test_case.input)
    actual_output = (
        "This is the expected output"  # your_product_function(test_case.input, ...)
    )

    galtea.evaluations.create_single_turn(
        version_id=version.id,
        test_case_id=test_case.id,
        metrics=[
            {"name": metric_from_api.name},
            {"score": keyword_metric},
        ],
        actual_output=actual_output,
        retrieval_context=retrieval_context,
        # @end launching_evaluations
    )
# @start retrieving_evaluation_results

# 7) List sessions for the version and print evaluations
sessions = galtea.sessions.list(version_id=version.id, sort_by_created_at="desc")
for session in sessions:
    evaluations = galtea.evaluations.list(session_id=session.id)
    for evaluation in evaluations:
        # @end retrieving_evaluation_results
        print(f"Evaluation ID: {evaluation.id}, Score: {evaluation.score}")

# @start working_with_pagination_basic


# 8) Pagination examples
def fetch_all_test_cases(test_id: str, limit: int = 100) -> list:
    all_test_cases = []
    offset = 0
    while True:
        batch = galtea.test_cases.list(test_id=test_id, offset=offset, limit=limit)
        if not batch:
            break
        all_test_cases.extend(batch)
        if len(batch) < limit:
            break
        offset += limit
    # @end working_with_pagination_basic
    return all_test_cases


# @start working_with_pagination_understanding

# Products/pages examples
first_page_products = galtea.products.list(offset=0, limit=10)
second_page_products = galtea.products.list(offset=10, limit=10)
# @end working_with_pagination_understanding
default_products = galtea.products.list()  # up to default limit (e.g., 1000)
# @start working_with_pagination_pagination

# Generic pagination examples
products_page = galtea.products.list(offset=0, limit=50)
versions_page = galtea.versions.list(product_id=product.id, offset=0, limit=50)
sessions_page = galtea.sessions.list(version_id=version.id, offset=0, limit=50)
if sessions:
    evaluations_page = galtea.evaluations.list(
        session_id=sessions[0].id,
        offset=0,
        limit=50,
        # @end working_with_pagination_pagination
    )

# === Cleanup ===
galtea.metrics.delete(metric_id=metric_from_api.id)
galtea.metrics.delete(metric_id=metric_from_api_custom.id)
galtea.products.delete(product_id=product_id)
