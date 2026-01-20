"""
SDK API: Inference Result Generate - Additional Examples
Demonstrates usage/cost info and error handling for the generate method.
"""

from datetime import datetime

import galtea
from galtea import Agent, AgentInput, AgentResponse, Galtea
from galtea.domain.models.trace import TraceType

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea_client = Galtea(api_key="YOUR_API_KEY")

# Create a product for this demo
client = getattr(galtea_client, "_Galtea__client", None)
if client is None:
    raise ValueError("Could not access Galtea client for direct API call")
response = client.post(
    "products",
    json={
        "name": "Generate Demo " + run_identifier,
        "description": "Demo product for inference result generate API",
        "capabilities": "Demo capabilities",
        "inabilities": "Demo inabilities",
        "securityBoundaries": "Demo security boundaries",
    },
)
product_id = response.json()["id"]

version = galtea_client.versions.create(
    name="Version-" + run_identifier,
    product_id=product_id,
    description="Demo version for generate examples",
    model_id="ru45tcu3bnqibuswhla4omyt",
)
if version is None:
    raise ValueError("version is None")
version_id = version.id

session = galtea_client.sessions.create(version_id=version_id, is_production=True)
if session is None:
    raise ValueError("session is None")


# @start usage_and_cost_info
class MyAgentWithUsage(Agent):
    @galtea.trace(name="main", type=TraceType.AGENT)
    def call(self, input: AgentInput) -> AgentResponse:
        # Your agent logic...

        return AgentResponse(
            content="Response content",
            usage_info={
                "input_tokens": 150,
                "output_tokens": 75,
                "cache_read_input_tokens": 50,
            },
            cost_info={
                "cost_per_input_token": 0.00001,
                "cost_per_output_token": 0.00003,
                "cost_per_cache_read_input_token": 0.000001,
            },
        )


# @end usage_and_cost_info


agent = MyAgentWithUsage()

result = galtea_client.inference_results.generate(
    agent=agent,
    session=session,
    user_input="test input",
)
if result is None:
    raise ValueError("result is None")

# Create a new session for error handling example
session_error = galtea_client.sessions.create(version_id=version_id, is_production=True)
if session_error is None:
    raise ValueError("session_error is None")


# @start error_handling
class FailingAgent(Agent):
    def call(self, input: AgentInput) -> AgentResponse:
        raise ValueError("Agent failed intentionally")


failing_agent = FailingAgent()

try:
    result = galtea_client.inference_results.generate(
        agent=failing_agent, session=session_error, user_input="test"
    )
except Exception as e:
    # Trace context is automatically cleaned up
    print(f"Agent failed: {e}")
# @end error_handling


# === Cleanup ===
galtea_client.products.delete(product_id=product_id)
