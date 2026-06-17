"""
AgentInput reference page code examples.
Demonstrates accessing structured input fields via AgentInput.
"""

from datetime import datetime

import galtea
from galtea import AgentInput, AgentResponse, Galtea

from _test_helpers import create_test_product

run_identifier: str = datetime.now().strftime("%Y%m%d%H%M%S%f")

galtea_client = Galtea(api_key="YOUR_API_KEY")

# Setup: create a product, version, test, test case (with structured input),
# session, and inference result so the snippets below can call get() against
# real IDs.
product_id: str = create_test_product(
    galtea_client,
    name=f"docs-agent-input-{run_identifier}",
    description="Product for AgentInput documentation example",
)

version = galtea_client.versions.create(
    name=f"agent-input-version-{run_identifier}",
    product_id=product_id,
    description="Version for AgentInput documentation example",
)
if version is None:
    raise ValueError("version is None")

test = galtea_client.tests.create(
    name=f"agent-input-test-{run_identifier}",
    type="ACCURACY",
    product_id=product_id,
    ground_truth_file_path="path/to/knowledge.md",
    language="english",
    max_test_cases=1,
)
if test is None:
    raise ValueError("test is None")

test_case = galtea_client.test_cases.create(
    test_id=test.id,
    input={"user_message": "hello", "chat_type": "support"},
    expected_output="Hi there!",
)
if test_case is None:
    raise ValueError("test_case is None")
test_case_id: str = test_case.id

session = galtea_client.sessions.create(version_id=version.id, test_case_id=test_case_id, is_production=False)
if session is None:
    raise ValueError("session is None")

inference_result = galtea_client.inference_results.create(
    session_id=session.id,
    input={"user_message": "hello", "chat_type": "support"},
    output="Hi there!",
)
if inference_result is None:
    raise ValueError("inference_result is None")
inference_result_id: str = inference_result.id


# @start basic_usage
def my_basic_agent(input_data: galtea.AgentInput) -> galtea.AgentResponse:
    # Get the last user message content
    user_message = input_data.last_user_message_str()

    # Access session and context
    session_id = input_data.session_id
    context = input_data.context_data  # e.g. {"customer_tier": "premium"}

    return galtea.AgentResponse(content=f"Response to: {user_message}")


# @end basic_usage


# @start structured_input_access
def my_structured_agent(input_data: AgentInput) -> AgentResponse:
    # Get the last user message as a ConversationMessage object
    last_msg = input_data.last_user_message()
    if last_msg is None:
        return AgentResponse(content="No user message received.")

    # The message content (the user_message field from structured input)
    user_message = last_msg.content  # e.g. "hello"

    # Structured fields from the test case are in the first user message's metadata
    first_user_msg = input_data.messages[0] if input_data.messages else None
    if first_user_msg and first_user_msg.metadata:
        chat_type = first_user_msg.metadata.get("chat_type")  # e.g. "support"
        priority = first_user_msg.metadata.get("priority")  # e.g. "high"
    else:
        chat_type = None
        priority = None

    # Use structured fields to customize behavior
    if chat_type == "support":
        response = f"Support response (priority={priority}): {user_message}"
    else:
        response = f"General response: {user_message}"

    return AgentResponse(content=response)


# @end structured_input_access


# @start context_data_access
def my_context_agent(input_data: AgentInput) -> AgentResponse:
    user_message = input_data.last_user_message_str()

    # context_data comes from the test case's context field
    if input_data.context_data:
        customer_tier = input_data.context_data.get("customer_tier", "standard")
    else:
        customer_tier = "standard"

    return AgentResponse(content=f"[{customer_tier}] Response to: {user_message}")


# @end context_data_access


# @start test_case_input_data
# After running generate() or in a test loop, access the full structured input:
galtea_client = Galtea(api_key="YOUR_API_KEY")
test_case = galtea_client.test_cases.get(test_case_id=test_case_id)

# .input gives the user_message as a plain string
print(test_case.input)  # "hello"

# .input_data gives the full structured dict
print(test_case.input_data)  # {"user_message": "hello", "chat_type": "support"}

# Same pattern for inference results (input side):
inference_result = galtea_client.inference_results.get(inference_result_id=inference_result_id)
print(inference_result.input)  # "hello"
print(inference_result.input_data)  # {"user_message": "hello", "chat_type": "support"}

# Output side — symmetric pair:
print(inference_result.actual_output)  # "the answer is 42" (plain string for text; transcript for voice)
print(
    inference_result.actual_output_data
)  # None for plain text; {"assistant_message": "...", "content": [...]} for voice
# @end test_case_input_data

# Cleanup
galtea_client.products.delete(product_id=product_id)
