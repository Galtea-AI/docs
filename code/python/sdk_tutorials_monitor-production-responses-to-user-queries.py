"""
Tutorial: Monitor Production Responses
Demonstrates how to log and evaluate user queries from your production environment.
"""

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
        "name": "Production Monitor Demo " + run_identifier,
        "description": "Demo product for production monitoring tutorial",
        "capabilities": "Demo capabilities",
        "inabilities": "Demo inabilities",
        "securityBoundaries": "Demo security boundaries",
    },
)
product_id = response.json()["id"]

version = galtea.versions.create(
    name="Version-" + run_identifier,
    product_id=product_id,
    description="Demo version for production monitoring",
    model_id="ru45tcu3bnqibuswhla4omyt",
)
if version is None:
    raise ValueError("version is None")
VERSION_ID = version.id


def your_product_function(user_query: str, retrieval_context: str | None = None) -> str:
    """Simulated product function."""
    return f"Simulated response to: {user_query}"


# @start single_turn
# In your application's request handler...
def handle_user_query(user_query: str, retrieval_context: str | None = None) -> str:
    # Your logic to get a response from your model
    model_response = your_product_function(user_query, retrieval_context)

    # Log and evaluate the interaction in Galtea
    galtea.evaluations.create_single_turn(
        version_id=VERSION_ID,
        is_production=True,
        metrics=[
            {"name": "Role Adherence"},
            {"name": "Answer Relevancy"},
            {"name": "Faithfulness"},
        ],
        input=user_query,
        actual_output=model_response,
        retrieval_context=retrieval_context,
    )

    return model_response


# Test the handler
handle_user_query(
    "What are your business hours?", "Business hours: 9am-5pm Monday-Friday"
)
# @end single_turn


METRICS_TO_EVALUATE = [
    {"name": "Conversation Relevancy"},
    {"name": "Knowledge Retention"},
]


# @start create_session
# Use is_production=True for real user interactions
session = galtea.sessions.create(
    custom_id="CLIENT_PROVIDED_SESSION_ID",  # Optional: a custom ID to associate this session in Galtea Platform to the one in your real application.
    version_id=VERSION_ID,
    is_production=True,
)
# @end create_session

if session is None:
    raise ValueError("session is None")


# @start log_turns_individually
def get_model_response(user_input: str) -> str:
    # Replace this with your actual model call
    model_output = f"This is a simulated response to '{user_input}'"
    return model_output


# This would happen dynamically in your application.
user_questions = [
    "What are some lower-risk investment strategies?",
    "With age, should the investment strategy change?",
    "Great, thanks!",
]

for question in user_questions:
    model_response = get_model_response(question)
    # Log the turn to Galtea right after it happens
    inference_result = galtea.inference_results.create(
        session_id=session.id, input=question, output=model_response
    )
# @end log_turns_individually


# Create a new session for batch logging
session_batch = galtea.sessions.create(
    version_id=VERSION_ID,
    is_production=True,
)
if session_batch is None:
    raise ValueError("session_batch is None")


# @start log_turns_batch
# The conversation must be in the standard format: a list of role/content dictionaries
conversation_turns = [
    {"role": "user", "content": "What are some lower-risk investment strategies?"},
    {
        "role": "assistant",
        "content": "For lower-risk investments, consider diversified index funds, bonds, or Treasury securities.",
    },
    {"role": "user", "content": "With age, should the investment strategy change?"},
    {
        "role": "assistant",
        "content": "Yes, many advisors recommend shifting to more conservative investments as you approach retirement.",
    },
    {"role": "user", "content": "Great, thanks!"},
    {"role": "assistant", "content": "You're welcome!"},
]

galtea.inference_results.create_batch(
    session_id=session_batch.id, conversation_turns=conversation_turns
)
# @end log_turns_batch


# @start evaluate_session
galtea.evaluations.create(session_id=session.id, metrics=METRICS_TO_EVALUATE)

print(f"Logged and evaluated production session {session.id}")
# @end evaluate_session


# === Cleanup ===
galtea.products.delete(product_id=product_id)
