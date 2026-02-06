"""
Tutorial: Evaluate with Custom Metrics
Demonstrates how to run evaluations with your own custom, self-hosted metrics.
"""

from datetime import datetime

from galtea import CustomScoreEvaluationMetric, Galtea

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea = Galtea(api_key="YOUR_API_KEY")

# Create a product for this demo
client = getattr(galtea, "_Galtea__client", None)
if client is None:
    raise ValueError("Could not access Galtea client for direct API call")
response = client.post(
    "products",
    json={
        "name": "Custom Metrics Demo " + run_identifier,
        "description": "Demo product for custom metrics tutorial",
        "capabilities": "Demo capabilities",
        "inabilities": "Demo inabilities",
        "securityBoundaries": "Demo security boundaries",
    },
)
product_id = response.json()["id"]

version = galtea.versions.create(
    name="Version-" + run_identifier,
    product_id=product_id,
    description="Demo version for custom metrics",
)
if version is None:
    raise ValueError("version is None")
version_id = version.id

test = galtea.tests.create(
    name="test-custom-metrics-" + run_identifier,
    type="ACCURACY",
    product_id=product_id,
    test_file_path="path/to/accuracy_test.csv",
)
if test is None:
    raise ValueError("test is None")

test_cases = galtea.test_cases.list(test_id=test.id, limit=1)
if test_cases is None or len(test_cases) == 0:
    raise ValueError("test_cases is None or empty")
test_case_id = test_cases[0].id


# @start option_1_pre_compute
# Your product's response
actual_output = "This response contains the correct keyword."


# Define your custom scoring logic
def contains_keyword(text: str, keyword: str) -> float:
    """Returns 1.0 if the keyword is in text (case-insensitive), 0.0 otherwise."""
    return 1.0 if keyword.lower() in text.lower() else 0.0


# Compute the score
custom_score = contains_keyword(actual_output, "correct")

# Create the metric if it doesn't exist yet
CUSTOM_METRIC_NAME = "contains-correct"
galtea.metrics.create(
    name=CUSTOM_METRIC_NAME,
    source="self_hosted",
    description='Checks for the presence of the keyword "correct" in the output',
    test_type="ACCURACY",
)

# Run evaluation with your pre-computed score
galtea.evaluations.create_single_turn(
    version_id=version_id,
    test_case_id=test_case_id,
    actual_output=actual_output,
    metrics=[
        {"name": "Role Adherence"},  # Standard Galtea metric
        {
            "name": CUSTOM_METRIC_NAME,
            "score": custom_score,
        },  # Self-hosted with pre-computed score
    ],
)
# @end option_1_pre_compute


# @start option_2_custom_class
# Define your custom metric class
class ContainsKeyword(CustomScoreEvaluationMetric):
    def __init__(self, keyword: str):
        self.keyword = keyword.lower()
        # Initialize with the metric name or ID
        super().__init__(name=f"contains-{self.keyword}")

    def measure(self, *args, actual_output: str | None = None, **kwargs) -> float:
        """
        Returns 1.0 if the keyword is in actual_output (case-insensitive), 0.0 otherwise.
        All other args/kwargs are accepted but ignored.
        """
        if actual_output is None:
            return 0.0
        return 1.0 if self.keyword in actual_output.lower() else 0.0


# Instantiate your metric
accuracy_metric = ContainsKeyword(keyword="relevant")

# Create the metric in the platform if it doesn't exist yet
galtea.metrics.create(
    name=accuracy_metric.name,
    source="self_hosted",
    description='Checks for the presence of the keyword "relevant" in the output',
    test_type="ACCURACY",
)

# Your product's response
actual_output_2 = "This response is relevant and helpful."

# Run evaluation with your custom metric class
# Important: Do NOT provide 'id' or 'name' in the dict when using CustomScoreEvaluationMetric
galtea.evaluations.create_single_turn(
    version_id=version_id,
    test_case_id=test_case_id,
    actual_output=actual_output_2,
    metrics=[
        {"name": "Role Adherence"},  # Standard Galtea metric
        {"score": accuracy_metric},  # Self-hosted with dynamic scoring
    ],
)
# @end option_2_custom_class


# === Cleanup ===
galtea.products.delete(product_id=product_id)
metric = galtea.metrics.get_by_name(name=CUSTOM_METRIC_NAME)
if metric:
    galtea.metrics.delete(metric_id=metric.id)
accuracy_metric_to_delete = galtea.metrics.get_by_name(name=accuracy_metric.name)
if accuracy_metric_to_delete:
    galtea.metrics.delete(metric_id=accuracy_metric_to_delete.id)
