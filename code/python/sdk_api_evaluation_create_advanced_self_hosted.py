from datetime import datetime

from galtea import (
    CustomScoreEvaluationMetric,
    Galtea,
)

galtea = Galtea(api_key="YOUR_API_KEY")
client = getattr(galtea, "_Galtea__client", None)
run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")
if client is None:
    raise ValueError("Could not access Galtea client for direct API call")
response = client.post(
    "products",
    json={
        "name": "Financial Assistant " + run_identifier,
        "description": "A conversational AI assistant designed to provide financial guidance to individuals with limited financial literacy. It empowers users to make informed investment decisions and manage their wealth effectively through accessible, easy-to-understand information.",
        "securityBoundaries": "* Must refuse to provide specific stock picks or investment strategies tailored to an individual\n* Should not ask for or store personally identifiable financial information (e.g., account numbers, social security numbers)\n* Must reject requests for illegal financial activities\n* Cannot offer advice that could be construed as fiduciary responsibility\n* Must refuse to share information about other users or general market data that is not publicly available\n",
        "capabilities": "* Explain basic investment concepts (e.g., stocks, bonds, mutual funds)\n* Provide information on different types of savings and investment accounts\n* Guide users on creating a simple personal budget\n* Offer general strategies for wealth management\n* Define financial terms and jargon\n",
        "inabilities": "* Cannot provide personalized investment recommendations or financial advice\n* Does not execute trades or manage user investment portfolios\n* Cannot access user's bank accounts or financial information\n* Does not offer tax advice\n* Cannot assist with loan applications or debt management\n",
        "policies": "",
    },
)
product_id = response.json()["id"]
version = galtea.versions.create(
    name="Version-docs-" + run_identifier,
    product_id=product_id,
    description="Demo version created via SDK",
)
if version is None:
    raise ValueError("version is None")
version_id = version.id

# @start tutorial
# First, create a session, in this case it is a production session, so we do not need a test case
session = galtea.sessions.create(version_id=version_id, is_production=True)

# Then, add some inference results to the session
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
# Note: This can be done via the Dashboard too
try:
    metric = galtea.metrics.get_by_name(name="politeness-check")
except Exception:
    metric = None
if metric is None:
    galtea.metrics.create(
        name="politeness-check",
        source="self_hosted",
        description="Checks if polite words appear in the output",
        test_type="ACCURACY",
    )

# Now, evaluate the entire session
evaluations = galtea.evaluations.create(
    session_id=session.id,
    metrics=[
        {"name": "Role Adherence"},  # You can use galtea-hosted metrics simultaneously
        {"score": PolitenessCheck()},  # Self-hosted with dynamic scoring
        # Note: No 'name' or 'id' in dict - it comes from PolitenessCheck(name="...")
    ],
)
# @end tutorial

# === Ensure no Leftovers ===
galtea.products.delete(product_id=product_id)
metric = galtea.metrics.get_by_name(name="politeness-check")
galtea.metrics.delete(metric_id=metric.id)
