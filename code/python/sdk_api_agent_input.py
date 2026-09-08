"""
AgentInput reference page code examples.
Demonstrates accessing structured input fields via AgentInput.
"""

import base64
from datetime import datetime

import galtea
from galtea import AgentInput, AgentResponse, Galtea

from _test_helpers import create_test_product

run_identifier: str = datetime.now().strftime("%Y%m%d%H%M%S%f")

galtea_client = Galtea(api_key="YOUR_API_KEY")

# Setup: create a product, version, test, test case (with structured input),
# session, and trace so the snippets below can call get() against
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

dataset = galtea_client.datasets.create(
    name=f"agent-input-test-{run_identifier}",
    type="ACCURACY",
    product_id=product_id,
    ground_truth_file_path="path/to/knowledge.md",
    language="english",
    max_test_cases=1,
)
if dataset is None:
    raise ValueError("dataset is None")

test_case = galtea_client.test_cases.create(
    dataset_id=dataset.id,
    input={"user_message": "hello", "chat_type": "support"},
    expected_output="Hi there!",
)
if test_case is None:
    raise ValueError("test_case is None")
test_case_id: str = test_case.id

session = galtea_client.sessions.create(version_id=version.id, test_case_id=test_case_id, is_production=False)
if session is None:
    raise ValueError("session is None")

trace = galtea_client.traces.create(
    session_id=session.id,
    input={"user_message": "hello", "chat_type": "support"},
    output="Hi there!",
)
if trace is None:
    raise ValueError("trace is None")
trace_id: str = trace.id


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


# @start reading_attached_files
def my_document_agent(input_data: AgentInput) -> AgentResponse:
    # Each InputFile has the same uri, filename and mime_type as test_case.input_files.
    document_paths = [
        galtea_client.storage.download(attached, output_directory="./.temp/agent-inputs")
        for attached in input_data.input_files
    ]

    # Empty string for a test case that carries only a document and no text.
    question = input_data.last_user_message_str() or ""

    return AgentResponse(content=f"Answer to {question!r} from {len(document_paths)} file(s)")


# @end reading_attached_files


# @start reading_attached_files_bytes
def my_multimodal_agent(input_data: AgentInput) -> AgentResponse:
    # read() keeps the bytes in memory, for a model that takes the document inline.
    parts = [
        {
            "type": "document",
            "media_type": attached.mime_type,
            "data": base64.b64encode(galtea_client.storage.read(attached)).decode(),
        }
        for attached in input_data.input_files
    ]

    question = input_data.last_user_message_str() or ""

    return AgentResponse(content=f"Answer to {question!r} from {len(parts)} inline document(s)")


# @end reading_attached_files_bytes


# @start test_case_input_data
# After running generate() or in a test loop, access the full structured input:
galtea_client = Galtea(api_key="YOUR_API_KEY")
test_case = galtea_client.test_cases.get(test_case_id=test_case_id)

# .input gives the user_message as a plain string
print(test_case.input)  # "hello"

# .input_data gives the full structured dict
print(test_case.input_data)  # {"user_message": "hello", "chat_type": "support"}

# Same pattern for traces (input side):
trace = galtea_client.traces.get(trace_id=trace_id)
print(trace.input)  # "hello"
print(trace.input_data)  # {"user_message": "hello", "chat_type": "support"}

# Output side — symmetric pair:
print(trace.actual_output)  # "the answer is 42" (plain string for text; transcript for voice)
print(trace.actual_output_data)  # None for plain text; {"assistant_message": "...", "content": [...]} for voice
# @end test_case_input_data

# Cleanup
galtea_client.products.delete(product_id=product_id)
