"""
Tutorial: Simulating User Conversations
Demonstrates how to use Galtea's Conversation Simulator to test your AI with a synthetic user.
"""

import time
from datetime import datetime

import galtea
from galtea import Galtea

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea_client = Galtea(api_key="YOUR_API_KEY")

# Create a product for this demo
client = getattr(galtea_client, "_Galtea__client", None)
if client is None:
    raise ValueError("Could not access Galtea client for direct API call")
response = client.post(
    "products",
    json={
        "name": "Simulation Demo " + run_identifier,
        "description": "Demo product for conversation simulation tutorial",
        "capabilities": "Demo capabilities",
        "inabilities": "Demo inabilities",
        "securityBoundaries": "Demo security boundaries",
    },
)
product_id = response.json()["id"]
version = galtea_client.versions.create(
    name="v1.0-" + run_identifier,
    product_id=product_id,
    description="Version created from the tutorial",
)
if version is None:
    raise ValueError("version is None")
version_id = version.id
test = galtea_client.tests.create(
    name="behavior-test-docs-" + run_identifier,
    type="BEHAVIOR",
    strategies=["written"],
    product_id=product_id,
    ground_truth_file_path="path/to/knowledge.md",
    language="english",
    max_test_cases=1,
)
test_cases = []
tries = 0
while len(test_cases) == 0:
    test_cases = galtea_client.test_cases.list(test_id=test.id)
    tries += 1
    time.sleep(1)
    print("Waiting for test cases to be generated...")
    if tries > 30:
        raise ValueError("No test cases found after multiple tries")
test_case_id = test_cases[0].id
session_id = galtea_client.sessions.create(
    version_id=version_id, test_case_id=test_case_id
).id


# @start agent_options_simulate
# Simple: receives just the last user message
def my_agent(user_message: str) -> str:
    return f"Response to: {user_message}"


# Chat History: receives the full conversation history (OpenAI message format)
def my_agent(messages: list[dict]) -> str:
    return f"Response to: {messages[-1]['content']}"


# Structured: structured input/output (with usage/cost tracking and retrieval context)
def my_agent(input_data: galtea.AgentInput) -> galtea.AgentResponse:
    user_msg = input_data.last_user_message_str()
    return galtea.AgentResponse(
        content=f"Response to: {user_msg}",
        usage_info={"input_tokens": 100, "output_tokens": 50},
    )


# Async functions work too
async def my_async_agent(user_message: str) -> str:
    return f"Async response to: {user_message}"


result = galtea_client.simulator.simulate(
    session_id=session_id,
    agent=my_agent,
    max_turns=10,
)
# @end agent_options_simulate


# @start implement_agent_function
# Simple: receives just the last user message
def my_agent(user_message: str) -> str:
    """Simplest agent function signature."""
    # Your LLM call here
    return f"Response to: {user_message}"


# Chat History: receives full conversation history (OpenAI message format)
def my_agent(messages: list[dict]) -> str:
    """Agent function with access to the full conversation history."""
    user_message = messages[-1]["content"]
    # Your LLM call here
    return f"Response to: {user_message}"


# Structured: structured input/output
def my_agent(input_data: galtea.AgentInput) -> galtea.AgentResponse:
    """Structured agent function with access to session context and rich responses."""
    user_message = input_data.last_user_message_str()
    return galtea.AgentResponse(
        content=f"Response to: {user_message}",
        usage_info={"input_tokens": 100, "output_tokens": 50},
    )


# @end implement_agent_function


# @start implement_agent
# Structured function (for advanced features like usage/cost tracking)
@galtea.trace(name="main_agent")
def call_my_llm(user_message: str) -> str:
    """Your main agent logic"""
    return "useful_response"


def my_structured_agent(input_data: galtea.AgentInput) -> galtea.AgentResponse:
    # Access the latest user message
    user_message = input_data.last_user_message_str()

    # Generate a response using your own logic/model
    response = call_my_llm(user_message)

    # Return a structured response (optionally with metadata and retrieval context)
    return galtea.AgentResponse(
        content=response,
        retrieval_context=None,  # Optional: context retrieved by the agent (e.g., for RAG)
        metadata=None,  # Optional: additional metadata
    )


# @end implement_agent


# Call the product and version you want to evaluate
product = galtea_client.products.get(product_id=product_id)
if product is None:
    raise ValueError("product is None")

test_name = f"Multi-turn Conversation Test-{run_identifier}"

# @start create_test_and_sessions
# Create a test suite using the behavior test options
# This can be done via the Dashboard or programmatically as shown here
test = galtea_client.tests.create(
    product_id=product.id,
    name=test_name,
    type="BEHAVIOR",
    # This time we provide a path to a CSV file with behavior tests, but you can also have Galtea generate them if you do not provide a CSV file
    test_file_path="path/to/behavior_test.csv",
)

# Get your test cases
# If Galtea is generating the test for you, it might take a few moments to be ready
test_cases = galtea_client.test_cases.list(test_id=test.id)
# @end create_test_and_sessions

if test_cases is None or len(test_cases) == 0:
    raise ValueError("No test cases found")


# @start run_simulator
# Define your agent function (see Agent Integration Options for all signatures)
def my_agent(user_message: str) -> str:
    return f"Response to: {user_message}"


# Run simulations with your agent function
for test_case in test_cases:
    session = galtea_client.sessions.create(
        version_id=version.id, test_case_id=test_case.id
    )

    result = galtea_client.simulator.simulate(
        session_id=session.id, agent=my_agent, max_turns=10
    )

    # Analyze results
    print(f"Scenario: {test_case.scenario}")
    print(f"Completed {result.total_turns} turns")
    print(f"Success: {result.finished}")
    if result.stopping_reason:
        print(f"Ended because: {result.stopping_reason}")
    # @end run_simulator

    # @start evaluate_session
    # After each simulation, you can create an evaluation
    evaluations = galtea_client.evaluations.create(
        session_id=session.id,
        metrics=[{"name": "Role Adherence"}],  # Replace with your metrics
    )
    for evaluation in evaluations:
        print(f"Evaluation created: {evaluation.id}")
# @end evaluate_session


# @start rag_agent
def my_rag_agent(input_data: galtea.AgentInput) -> galtea.AgentResponse:
    user_message = input_data.last_user_message_str()

    # Your RAG logic to retrieve context and generate a response
    retrieved_docs = vector_store.search(user_message)
    response_content = llm.generate(prompt=user_message, context=retrieved_docs)

    return galtea.AgentResponse(
        content=response_content,
        retrieval_context=retrieved_docs,
        metadata={"docs_retrieved": len(retrieved_docs)},
    )


# @end rag_agent


# === Cleanup ===
galtea_client.products.delete(product_id=product_id)
