"""
Tutorial: Evaluating Conversations
Demonstrates how to evaluate multi-turn conversations using Galtea's session-based workflow.
"""

from datetime import datetime

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
        "name": "Conversation Eval Demo " + run_identifier,
        "description": "Demo product for conversation evaluation tutorial",
        "capabilities": "Demo capabilities",
        "inabilities": "Demo inabilities",
        "securityBoundaries": "Demo security boundaries",
    },
)
product_id = response.json()["id"]

version = galtea_client.versions.create(
    name="Version-" + run_identifier,
    product_id=product_id,
    description="Demo version for conversation evaluation",
)
if version is None:
    raise ValueError("version is None")
version_id = version.id

# Create a behavior test for test-based evaluation
behavior_test = galtea_client.tests.create(
    product_id=product_id,
    name="behavior-test-" + run_identifier,
    type="BEHAVIOR",
    test_file_path="path/to/behavior_test.csv",
)
if behavior_test is None:
    raise ValueError("behavior_test is None")


# @start test_based_evaluation
# Fetch your test cases (created from a CSV of behavior tests)
test_cases = galtea_client.test_cases.list(test_id=behavior_test.id)
if test_cases is None or len(test_cases) == 0:
    raise ValueError("No test cases found")


# Define your agent function (connect your product/model)
def my_agent(user_message: str) -> str:
    return f"Response to: {user_message}"


for test_case in test_cases:
    # Create a session linked to the test case
    session = galtea_client.sessions.create(
        version_id=version_id,
        test_case_id=test_case.id,
    )

    # Run the simulator (synthetic user) with your agent function
    galtea_client.simulator.simulate(
        session_id=session.id,
        agent=my_agent,
        max_turns=test_case.max_iterations or 20,
    )

    # Evaluate the full conversation
    galtea_client.evaluations.create(
        session_id=session.id,
        metrics=[
            {"name": "Conversation Relevancy"},
            {"name": "Role Adherence"},
            {"name": "Knowledge Retention"},
        ],
    )
# @end test_based_evaluation


# @start past_conversations
# Optional: map to your own conversation ID and mark as production if these are real users
session = galtea_client.sessions.create(
    version_id=version_id,
    custom_id="EXTERNAL_CONVERSATION_ID",
    is_production=True,
)

conversation_turns = [
    {"role": "user", "content": "What are some lower-risk investment strategies?"},
    {
        "role": "assistant",
        "content": "For lower-risk investments, consider diversified index funds, bonds, or Treasury securities.",
        "retrieval_context": "Low-risk investment options include index funds, government bonds, and Treasury securities.",
    },
    {"role": "user", "content": "With age, should the investment strategy change?"},
    {
        "role": "assistant",
        "content": "Yes, many advisors recommend shifting to more conservative investments as you approach retirement.",
        "retrieval_context": "Financial advisors typically recommend a more conservative asset allocation as investors near retirement age.",
    },
]

# Log all turns at once
galtea_client.inference_results.create_batch(
    session_id=session.id, conversation_turns=conversation_turns
)

# Evaluate the full session
galtea_client.evaluations.create(
    session_id=session.id,
    metrics=[
        {"name": "Role Adherence"},
        {"name": "Knowledge Retention"},
        {"name": "Conversation Relevancy"},
    ],
)
# @end past_conversations


# @start monitoring_individual
session = galtea_client.sessions.create(
    version_id=version_id,
    is_production=True,
)


def your_product(user_input: str) -> str:
    return f"This is a simulated response to '{user_input}'"


def handle_turn(user_input: str) -> str:
    model_output = your_product(user_input)
    galtea_client.inference_results.create(
        session_id=session.id, input=user_input, output=model_output
    )
    return model_output


# Simulate production interactions
handle_turn("Hello!")
handle_turn("What services do you offer?")
# @end monitoring_individual


# @start monitoring_batch
session_batch = galtea_client.sessions.create(
    version_id=version_id,
    is_production=True,
)

conversation_turns = [
    {"role": "user", "content": "What are some lower-risk investment strategies?"},
    {
        "role": "assistant",
        "content": "For lower-risk investments, consider diversified index funds, bonds, or Treasury securities.",
    },
]

galtea_client.inference_results.create_batch(
    session_id=session_batch.id, conversation_turns=conversation_turns
)
# @end monitoring_batch


# @start monitoring_evaluate
# Evaluate when the conversation is complete
galtea_client.evaluations.create(
    session_id=session.id,
    metrics=[{"name": "Conversation Relevancy"}, {"name": "Knowledge Retention"}],
)
# @end monitoring_evaluate


# === Cleanup ===
galtea_client.products.delete(product_id=product_id)
