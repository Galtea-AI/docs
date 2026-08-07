"""
Tutorial: Tracing Agent Operations
Demonstrates how to trace agent operations using the SDK.
"""

from datetime import datetime

from galtea import (
    AgentInput,
    AgentResponse,
    Galtea,
    SpanType,
    clear_context,
    set_context,
    start_span,
    traced,
)

from _test_helpers import create_test_product

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S%f")

galtea = Galtea(api_key="YOUR_API_KEY")

# Register a product for this demo
product_id = create_test_product(
    galtea,
    name="Tracing Demo " + run_identifier,
    description="Demo product for tracing tutorial",
    capabilities="Demo capabilities",
    inabilities="Demo inabilities",
)

# Create version
version = galtea.versions.create(
    product_id=product_id,
    name="v1.0-" + run_identifier,
)

# Create a behavior test for simulation
behavior_dataset = galtea.datasets.create(
    name="tracing-behavior-" + run_identifier,
    type="BEHAVIOR",
    product_id=product_id,
    dataset_file_path="path/to/behavior_dataset.csv",
)


# Mock database for demos
class MockDB:
    def query(self, query: str) -> str:
        return "Mock result for: " + query


db = MockDB()


# @start 1_the_decorator
@traced(name="db_call", type=SpanType.TOOL)
def my_function(query: str) -> str:
    result = db.query(query)
    return result


# @end 1_the_decorator


# @start 2_the_context_manager
def get_user(user_id: str) -> str:
    with start_span("database_query", type=SpanType.TOOL, input={"user_id": user_id}) as span:
        query = f"SELECT * FROM users WHERE id = {user_id}"
        result = db.query(query)
        span.update(output=result, metadata={"query": query})
    return result


# @end 2_the_context_manager


# @start automatic_collection_agent_setup
@traced(type=SpanType.RETRIEVER)
def search(query: str) -> list[dict]:
    return [{"id": "doc_1", "content": "..."}]


@traced(type=SpanType.GENERATION)
def generate_response(context: list, query: str) -> str:
    return "Based on the context..."


@traced(type=SpanType.AGENT)
def my_agent(input_data: AgentInput) -> AgentResponse:
    query = input_data.last_user_message_str()

    # For structured inputs, access extra fields via first message metadata
    # first_msg = input_data.messages[0] if input_data.messages else None
    # chat_type = first_msg.metadata.get("chat_type") if first_msg and first_msg.metadata else None

    docs = search(query)
    response = generate_response(docs, query)
    return AgentResponse(content=response, retrieval_context=str(docs))


# Setup
session = galtea.sessions.create(version_id=version.id, is_production=True)
# @end automatic_collection_agent_setup

# @start automatic_collection_single_turn_with
inference_result = galtea.inference_results.generate(agent=my_agent, session=session, input="What's the price?")
# Spans are collected, associated with inference_result.id, and flushed automatically
# @end automatic_collection_single_turn_with


# Create a session for multi-turn simulation (requires test case)
test_cases = galtea.test_cases.list(dataset_id=behavior_dataset.id, limit=1)
if test_cases:
    simulation_session = galtea.sessions.create(version_id=version.id, test_case_id=test_cases[0].id)

    # @start automatic_collection_multi_turn_with
    result = galtea.simulator.simulate(session_id=simulation_session.id, agent=my_agent, max_turns=5)
    # Spans are saved automatically for each turn
    # @end automatic_collection_multi_turn_with


# @start 3_collect_and_send_traces_to_galtea
# Define traced functions
@traced(type=SpanType.RETRIEVER)
def search(query: str) -> list[dict]:
    return [{"id": "doc_1", "content": "..."}]


@traced(type=SpanType.GENERATION)
def generate(context: list, query: str) -> str:
    return "Based on the context..."


@traced(type=SpanType.AGENT)
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

# 2. Set Galtea context with the inference result ID
token = set_context(inference_result_id=manual_inference_result.id)

try:
    # 3. Run your logic - all @traced calls will be associated with this inference result
    response = run_agent(user_input)

    # 4. Update inference result with the output
    galtea.inference_results.update(inference_result_id=manual_inference_result.id, output=response)
finally:
    # 5. Clear context and flush spans to Galtea
    clear_context(token)  # flush=True by default
# @end 3_collect_and_send_traces_to_galtea

# @start remote_agent_tracing
import httpx

from galtea import AgentInput, AgentResponse, traced, SpanType

REMOTE_URL = "https://my-remote-agent.example.com/invoke"


@traced(type=SpanType.AGENT)
def remote_agent(input_data: AgentInput) -> AgentResponse:
    """Forward execution to a remote server, passing the inference_result_id for span correlation."""
    response = httpx.post(
        REMOTE_URL,
        json={
            "message": input_data.last_user_message_str(),
            "session_id": input_data.session_id,
            "inference_result_id": input_data.inference_result_id,
        },
    )
    return AgentResponse(content=response.json()["content"])


# @end remote_agent_tracing


# @start remote_server_handler
# On the remote server (e.g. FastAPI endpoint):
from galtea import set_context, clear_context


def handle_request(message: str, session_id: str, inference_result_id: str) -> str:
    # Attach spans to the same inference result
    token = set_context(inference_result_id=inference_result_id)
    try:
        # All @traced calls here will be associated with the inference result
        response = run_agent_logic(message)
        return response
    finally:
        clear_context(token)


# @end remote_server_handler


def run_agent_logic(message: str) -> str:
    return "Response to: " + message


# === Cleanup ===
galtea.products.delete(product_id=product_id)
