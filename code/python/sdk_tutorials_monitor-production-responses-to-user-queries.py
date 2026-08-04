"""
Tutorial: Monitor Production Responses
Demonstrates how to log and evaluate user queries from your production environment.
"""

from datetime import datetime

from _test_helpers import create_test_product
from galtea import Galtea
from requests.exceptions import HTTPError

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea = Galtea(api_key="YOUR_API_KEY")

# Register a product for this demo
product_id = create_test_product(
    galtea,
    name="Production Monitor Demo " + run_identifier,
    description="Demo product for production monitoring tutorial",
    capabilities="Demo capabilities",
    inabilities="Demo inabilities",
)

version = galtea.versions.create(
    name="Version-" + run_identifier,
    product_id=product_id,
    description="Demo version for production monitoring",
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
    session = galtea.sessions.create(version_id=VERSION_ID, is_production=True)
    galtea.inference_results.create_and_evaluate(
        session_id=session.id,
        input=user_query,
        output=model_response,
        retrieval_context=retrieval_context,
        metrics=[
            {"name": "Role Adherence"},
            {"name": "Answer Relevancy"},
            {"name": "Faithfulness"},
        ],
    )

    return model_response


# Test the handler
handle_user_query("What are your business hours?", "Business hours: 9am-5pm Monday-Friday")
# @end single_turn


# Create a specification with linked metrics so specification-based evaluation works
answer_relevancy = galtea.metrics.get_by_name(name="Answer Relevancy")
role_adherence = galtea.metrics.get_by_name(name="Role Adherence")
if answer_relevancy is None or role_adherence is None:
    raise ValueError("Could not find the metrics to link to the specification")

production_spec = galtea.specifications.create(
    product_id=product_id,
    name="Stays relevant and in role",
    description="The assistant gives relevant answers and stays within its defined role.",
    type="CAPABILITY",
    metric_ids=[answer_relevancy.id, role_adherence.id],
)
if production_spec is None:
    raise ValueError("Failed to create specification")
specification_ids = [production_spec.id]


# @start single_turn_specification_ids
# In your application's request handler...
def handle_user_query_with_specifications(user_query: str, retrieval_context: str | None = None) -> str:
    # Your logic to get a response from your model
    model_response = your_product_function(user_query, retrieval_context)

    # Log and evaluate the interaction, resolving metrics from your specifications
    session = galtea.sessions.create(version_id=VERSION_ID, is_production=True)
    galtea.inference_results.create_and_evaluate(
        session_id=session.id,
        input=user_query,
        output=model_response,
        retrieval_context=retrieval_context,
        specification_ids=specification_ids,
    )

    return model_response


# Test the handler
handle_user_query_with_specifications("What are your business hours?", "Business hours: 9am-5pm Monday-Friday")
# @end single_turn_specification_ids


# @start single_turn_custom_id
# At the start of the conversation, create the session ONCE with YOUR own id.
galtea.sessions.create(
    custom_id="conversation-42",  # your own conversation id
    version_id=VERSION_ID,
    is_production=True,
)


# In your application's request handler...
def handle_user_query_with_custom_id(conversation_id: str, user_query: str) -> str:
    # Your logic to get a response from your model
    model_response = your_product_function(user_query)

    # Log and evaluate in one call, using YOUR conversation id as the handle.
    # Galtea finds the existing session by that id and appends the turn to it.
    galtea.inference_results.create_and_evaluate(
        session_custom_id=conversation_id,  # the id you created the session with
        version_id=VERSION_ID,  # or product_id=product_id to find it under the product
        input=user_query,
        output=model_response,
        metrics=[
            {"name": "Role Adherence"},
            {"name": "Answer Relevancy"},
        ],
    )

    return model_response


# Test the handler: both calls land in the same session
handle_user_query_with_custom_id("conversation-42", "What are your business hours?")
handle_user_query_with_custom_id("conversation-42", "Are you open on weekends?")
# @end single_turn_custom_id


# @start log_turns_custom_id
# Create the session once, up front, with your own conversation id.
galtea.sessions.create(
    custom_id="conversation-1234",
    version_id=VERSION_ID,
    is_production=True,
)


def handle_conversation_turn(conversation_id: str, user_input: str) -> str:
    # Replace this with your actual model call
    model_output = f"This is a simulated response to '{user_input}'"

    # Log each turn under your own conversation id. Galtea finds the existing
    # session by that id and appends the turn to it.
    galtea.inference_results.create(
        session_custom_id=conversation_id,
        version_id=VERSION_ID,  # or product_id=product_id
        input=user_input,
        output=model_output,
    )
    return model_output


# This would happen dynamically in your application.
for question in [
    "What are some lower-risk investment strategies?",
    "With age, should the investment strategy change?",
    "Great, thanks!",
]:
    handle_conversation_turn("conversation-1234", question)
# @end log_turns_custom_id


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
    inference_result = galtea.inference_results.create(session_id=session.id, input=question, output=model_response)
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

galtea.inference_results.create_batch(session_id=session_batch.id, conversation_turns=conversation_turns)
# @end log_turns_batch


# @start evaluate_session_metrics
galtea.evaluations.create(session_id=session.id, metrics=METRICS_TO_EVALUATE)
# @end evaluate_session_metrics

# @start evaluate_session_specifications
# Or resolve metrics from your product's specifications instead of listing them
galtea.evaluations.create(session_id=session.id, specification_ids=specification_ids)
# @end evaluate_session_specifications

# @start finish_session
# When the user's conversation ends, finish the session. This closes it, so a monitor
# can score it on the next scan instead of waiting for the product's auto-close window.
galtea.sessions.finish(session.id)
# @end finish_session


print(f"Logged and evaluated production session {session.id}")


# === Cleanup ===
# Deleting the product cascades to the sessions and specification created above.
try:
    galtea.products.delete(product_id=product_id)
except HTTPError as e:
    # Known API issue: cascade soft-delete may hit unique constraint on specifications
    if e.response.status_code != 500:
        raise
