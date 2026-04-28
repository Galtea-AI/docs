"""
Tutorial: Evaluate with Custom Metrics
Demonstrates how to run evaluations with your own custom, self-hosted metrics.
"""

from datetime import datetime

from _test_helpers import create_test_product
from galtea import CustomScoreEvaluationMetric, Galtea

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea = Galtea(api_key="YOUR_API_KEY")

# Register a product for this demo
product_id = create_test_product(
    galtea,
    name="Custom Metrics Demo " + run_identifier,
    description="Demo product for custom metrics tutorial",
    capabilities="Demo capabilities",
    inabilities="Demo inabilities",
    security_boundaries="Demo security boundaries",
)

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
)

# Run evaluation with your pre-computed score
session = galtea.sessions.create(version_id=version_id, test_case_id=test_case_id)
galtea.inference_results.create_and_evaluate(
    session_id=session.id,
    output=actual_output,
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
)

# Your product's response
actual_output_2 = "This response is relevant and helpful."

# Run evaluation with your custom metric class
# Important: Do NOT provide 'id' or 'name' in the dict when using CustomScoreEvaluationMetric
session_2 = galtea.sessions.create(version_id=version_id, test_case_id=test_case_id)
galtea.inference_results.create_and_evaluate(
    session_id=session_2.id,
    output=actual_output_2,
    metrics=[
        {"name": "Role Adherence"},  # Standard Galtea metric
        {"score": accuracy_metric},  # Self-hosted with dynamic scoring
    ],
)
# @end option_2_custom_class


# @start multi_turn_custom_metric
from galtea import InferenceResult


class AllOutputsContainKeyword(CustomScoreEvaluationMetric):
    """Checks if a keyword appears in every assistant response across the conversation."""

    def __init__(self, keyword: str):
        self.keyword = keyword.lower()
        super().__init__(name=f"all-outputs-contain-{self.keyword}")

    def measure(self, *args, actual_output: str | None = None, inference_results: list[InferenceResult] | None = None, **kwargs) -> float:
        """
        Uses inference_results to check every turn in the conversation.
        Falls back to actual_output when inference_results is not available.
        """
        if inference_results:
            outputs = [ir.actual_output for ir in inference_results if ir.actual_output]
            if not outputs:
                return 0.0
            matches = sum(1 for output in outputs if self.keyword in output.lower())
            return matches / len(outputs)
        # Fallback for when inference_results is not provided
        if not actual_output:
            return 0.0
        return 1.0 if self.keyword in actual_output.lower() else 0.0


# Use with session-based evaluation for multi-turn scoring
# galtea.evaluations.create(
#     session_id="your_session_id",
#     metrics=[{"score": AllOutputsContainKeyword(keyword="helpful")}],
# )
# @end multi_turn_custom_metric


# === Cleanup ===
galtea.products.delete(product_id=product_id)
metric = galtea.metrics.get_by_name(name=CUSTOM_METRIC_NAME)
if metric:
    galtea.metrics.delete(metric_id=metric.id)
accuracy_metric_to_delete = galtea.metrics.get_by_name(name=accuracy_metric.name)
if accuracy_metric_to_delete:
    galtea.metrics.delete(metric_id=accuracy_metric_to_delete.id)
