"""
SDK API: Evaluation Create
Demonstrates how to create evaluations for all inference results within a session.
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
        "name": "Evaluation Create Demo " + run_identifier,
        "description": "Demo product for evaluation create API",
        "capabilities": "Demo capabilities",
        "inabilities": "Demo inabilities",
        "securityBoundaries": "Demo security boundaries",
    },
)
product_id = response.json()["id"]

version = galtea.versions.create(
    name="Version-" + run_identifier,
    product_id=product_id,
    description="Demo version for evaluation create",
    model_id="ru45tcu3bnqibuswhla4omyt",
)
if version is None:
    raise ValueError("version is None")
version_id = version.id


# @start usage_example_using_the_metricinput_1
# First, create a session and log inference results
session = galtea.sessions.create(version_id=version_id, is_production=True)
galtea.inference_results.create_batch(
    session_id=session.id,
    conversation_turns=[
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello!"},
        {"role": "user", "content": "How are you?"},
        {"role": "assistant", "content": "I am fine, thank you."},
    ],
)


# Define scoring logic as a class
class PolitenessCheck(CustomScoreEvaluationMetric):
    def __init__(self):
        super().__init__(name="politeness-check")

    def measure(self, *args, actual_output: str | None = None, **kwargs) -> float:
        if actual_output is None:
            return 0.0
        polite_words = ["please", "thank you", "you're welcome"]
        return (
            1.0 if any(word in actual_output.lower() for word in polite_words) else 0.0
        )


# Create the metric in the platform if it doesn't exist yet
galtea.metrics.create(
    name="politeness-check",
    source="self_hosted",
    description="Checks if polite words appear in the output",
    test_type="QUALITY",
)

# Now, evaluate the entire session
evaluations = galtea.evaluations.create(
    session_id=session.id,
    metrics=[
        {"name": "Role Adherence"},  # Galtea-hosted metric
        {"name": "Conversation Relevancy"},  # Galtea-hosted metric
        {"score": PolitenessCheck()},  # Self-hosted with dynamic scoring
        # Note: No 'name' or 'id' in dict - it comes from PolitenessCheck(name="...")
    ],
)
# @end usage_example_using_the_metricinput_1


# @start usage_example_legacy_format_not
# First, create a session and log inference results
session_legacy = galtea.sessions.create(version_id=version_id, is_production=True)
galtea.inference_results.create_batch(
    session_id=session_legacy.id,
    conversation_turns=[
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello!"},
        {"role": "user", "content": "How are you?"},
        {"role": "assistant", "content": "I am fine, thank you."},
    ],
)


# Define your custom metric
class LegacyPolitenessCheck(CustomScoreEvaluationMetric):
    def __init__(self):
        super().__init__(name="legacy-politeness-check")

    def measure(self, *args, actual_output: str | None = None, **kwargs) -> float:
        if actual_output is None:
            return 0.0
        polite_words = ["please", "thank you", "you're welcome"]
        return (
            1.0 if any(word in actual_output.lower() for word in polite_words) else 0.0
        )


# Create the metric in the platform if it doesn't exist yet
galtea.metrics.create(
    name="legacy-politeness-check",
    source="self_hosted",
    description="Legacy polite check",
    test_type="QUALITY",
)

custom_score_politeness = LegacyPolitenessCheck()

# Legacy format - passing directly without MetricInput dict wrapper
evaluations = galtea.evaluations.create(
    session_id=session_legacy.id,
    metrics=[
        "Role Adherence",  # Legacy: string format
        "Conversation Relevancy",  # Legacy: string format
        custom_score_politeness,  # Legacy: CustomScoreEvaluationMetric directly
    ],
)
# @end usage_example_legacy_format_not


# @start parameters
metrics = [
    {"name": "Role Adherence"},  # By name (Galtea-hosted)
    {"id": "metric_abc123"},  # By ID
    {"name": "my-custom-metric", "score": 0.85},  # Pre-computed score (self-hosted)
    {"score": PolitenessCheck()},  # Dynamic scoring (self-hosted)
]
# @end parameters


# === Cleanup ===
galtea.products.delete(product_id=product_id)
metric = galtea.metrics.get_by_name(name="politeness-check")
if metric:
    galtea.metrics.delete(metric_id=metric.id)
metric = galtea.metrics.get_by_name(name="legacy-politeness-check")
if metric:
    galtea.metrics.delete(metric_id=metric.id)
