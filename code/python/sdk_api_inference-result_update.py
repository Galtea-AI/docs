"""
SDK API: Inference Result Update - Additional Examples
Demonstrates use cases for the update method.
"""

import time
from datetime import datetime

from galtea import Galtea

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea = Galtea(api_key="YOUR_API_KEY")

# Create a product for this demo
client = getattr(galtea, "_Galtea__client", None)
if client is None:
    raise ValueError("Could not access Galtea client for direct API call")
response = client.post(
    "products",
    json={
        "name": "Update Demo " + run_identifier,
        "description": "Demo product for inference result update API",
        "capabilities": "Demo capabilities",
        "inabilities": "Demo inabilities",
        "securityBoundaries": "Demo security boundaries",
    },
)
product_id = response.json()["id"]

version = galtea.versions.create(
    name="Version-" + run_identifier,
    product_id=product_id,
    description="Demo version for update examples",
    model_id="ru45tcu3bnqibuswhla4omyt",
)
if version is None:
    raise ValueError("version is None")
version_id = version.id

session = galtea.sessions.create(version_id=version_id, is_production=True)
if session is None:
    raise ValueError("session is None")


def my_model_generate(user_input: str) -> str:
    """Simulated model call."""
    time.sleep(0.1)  # Simulate processing time
    return f"Response to: {user_input}"


# @start deferred_output
# Create inference result with just input
user_input = "What is the weather today?"
inference_result = galtea.inference_results.create(
    session_id=session.id, input=user_input
)
if inference_result is None:
    raise ValueError("inference_result is None")

# Process with your model
start_time = time.time()
response = my_model_generate(user_input)
latency_ms = (time.time() - start_time) * 1000

# Update with output and metrics
galtea.inference_results.update(
    inference_result_id=inference_result.id, output=response, latency=latency_ms
)
# @end deferred_output


# @start cost_info
galtea.inference_results.update(
    inference_result_id=inference_result.id,
    cost=0.0025,
    cost_per_input_token=0.00001,
    cost_per_output_token=0.00003,
)
# @end cost_info


# === Cleanup ===
galtea.products.delete(product_id=product_id)
