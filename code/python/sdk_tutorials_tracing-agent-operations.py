"""
Tutorial: Tracing Agent Operations
Demonstrates how to trace agent operations using the SDK.
"""

from datetime import datetime

from galtea import (
    Agent,
    AgentInput,
    AgentResponse,
    Galtea,
    TraceType,
    clear_context,
    set_context,
    start_trace,
    trace,
)

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S%f")

galtea = Galtea(api_key="YOUR_API_KEY")

# Create a product for this demo
client = getattr(galtea, "_Galtea__client", None)
if client is None:
    raise ValueError("Could not access Galtea client for direct API call")
response = client.post(
    "products",
    json={
        "name": "Tracing Demo " + run_identifier,
        "description": "Demo product for tracing tutorial",
        "capabilities": "Demo capabilities",
        "inabilities": "Demo inabilities",
        "securityBoundaries": "Demo security boundaries",
    },
)
product_id = response.json()["id"]

# Create version
version = galtea.versions.create(
    product_id=product_id,
    name="v1.0-" + run_identifier,
)

# Create a behavior test for simulation
behavior_test = galtea.tests.create(
    name="tracing-behavior-" + run_identifier,
    type="BEHAVIOR",
    product_id=product_id,
    test_file_path="path/to/behavior_test.csv",
)


# Mock database for demos
class MockDB:
    def query(self, query: str) -> str:
        return "Mock result for: " + query


db = MockDB()


# @start 1_the_decorator
@trace(name="db_call", type=TraceType.TOOL)
def my_function(query: str) -> str:
    result = db.query(query)
    return result


# @end 1_the_decorator


# @start 2_the_context_manager
def get_user(user_id: str) -> str:
    with start_trace(
        "database_query", type=TraceType.TOOL, input={"user_id": user_id}
    ) as span:
        query = f"SELECT * FROM users WHERE id = {user_id}"
        result = db.query(query)
        span.update(output=result, metadata={"query": query})
    return result


# @end 2_the_context_manager


# @start automatic_collection_agent_setup
class MyAgent(Agent):
    @trace(type=TraceType.RETRIEVER)
    def search(self, query: str) -> list[dict]:
        return [{"id": "doc_1", "content": "..."}]

    @trace(type=TraceType.GENERATION)
    def generate(self, context: list, query: str) -> str:
        return "Based on the context..."

    @trace(type=TraceType.AGENT)
    def call(self, input: AgentInput) -> AgentResponse:
        query = input.last_user_message_str()
        docs = self.search(query)
        response = self.generate(docs, query)
        return AgentResponse(content=response, retrieval_context=str(docs))


# Setup
session = galtea.sessions.create(version_id=version.id, is_production=True)
agent = MyAgent()
# @end automatic_collection_agent_setup

# @start automatic_collection_single_turn_with
inference_result = galtea.inference_results.generate(
    agent=agent, session=session, user_input="What's the price?"
)
# Traces are collected, associated with inference_result.id, and flushed automatically
# @end automatic_collection_single_turn_with


# Create a session for multi-turn simulation (requires test case)
test_cases = galtea.test_cases.list(test_id=behavior_test.id, limit=1)
if test_cases:
    simulation_session = galtea.sessions.create(
        version_id=version.id, test_case_id=test_cases[0].id
    )

    # @start automatic_collection_multi_turn_with
    result = galtea.simulator.simulate(
        session_id=simulation_session.id, agent=agent, max_turns=5
    )
    # Traces are saved automatically for each turn
    # @end automatic_collection_multi_turn_with


# @start 3_collect_and_send_traces_to_galtea
# Define traced functions
@trace(type=TraceType.RETRIEVER)
def search(query: str) -> list[dict]:
    return [{"id": "doc_1", "content": "..."}]


@trace(type=TraceType.GENERATION)
def generate(context: list, query: str) -> str:
    return "Based on the context..."


@trace(type=TraceType.AGENT)
def run_agent(query: str) -> str:
    docs = search(query)
    return generate(docs, query)


# Setup
manual_session = galtea.sessions.create(version_id=version.id, is_production=True)
user_input = "What's the price?"

# 1. Create inference result first (to get the ID)
manual_inference_result = galtea.inference_results.create(
    session_id=manual_session.id,
    input=user_input,
    output=None,  # Will update later
)

# 2. Set trace context with the inference result ID
token = set_context(inference_result_id=manual_inference_result.id)

try:
    # 3. Run your logic - all @trace calls will be associated with this inference result
    response = run_agent(user_input)

    # 4. Update inference result with the output
    galtea.inference_results.update(
        inference_result_id=manual_inference_result.id, output=response
    )
finally:
    # 5. Clear context and flush traces to Galtea
    clear_context(token)  # flush=True by default
# @end 3_collect_and_send_traces_to_galtea

# === Cleanup ===
galtea.products.delete(product_id=product_id)
