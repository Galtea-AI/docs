from datetime import datetime

from galtea import Galtea

from _test_helpers import create_test_product

galtea = Galtea(api_key="YOUR_API_KEY")

run_identifier: str = datetime.now().strftime("%Y%m%d%H%M%S%f")

product_id: str = create_test_product(
    galtea,
    name=f"docs-test-conversation-history-{run_identifier}",
    description="Analytics workspace that answers questions about dashboards and reports",
    capabilities="Explain dashboards, reports and data sources",
    inabilities="Cannot process orders or payments",
)

# A predefined conversation is stored on a version of the product, so the product needs one.
version = galtea.versions.create(product_id=product_id, description="Seeded conversation demo")
if version is None:
    raise ValueError("version from create is None")

dataset = galtea.datasets.create(
    name=f"behavior-dataset-{run_identifier}",
    type="BEHAVIOR",
    product_id=product_id,
    dataset_file_path="path/to/behavior_dataset.csv",
)
if dataset is None:
    raise ValueError("dataset from create is None")

# @start test_case_from_written_conversation
conversation_history = [
    {"role": "user", "content": "Hi, I am checking what this analytics workspace can do."},
    {"role": "assistant", "content": "I can help with dashboards, reports and data sources."},
    {"role": "user", "content": "Does it handle orders and payments too?"},
    {"role": "assistant", "content": "No. It reports on your data, it does not process payments."},
]

test_case = galtea.test_cases.create(
    dataset_id=dataset.id,
    user_persona="A team lead evaluating the product",
    goal="Get a clear answer about what the product does and does not cover",
    scenario="The user asks about an unrelated service",
    conversation_history=conversation_history,
    # Turns the simulator runs after the predefined conversation.
    max_iterations=2,
)
# @end test_case_from_written_conversation
if test_case.seed_session_id is None:
    raise ValueError("the created test case holds no predefined conversation")
print(f"Test case {test_case.id} starts from session {test_case.seed_session_id}")

# @start test_case_from_existing_session
reused = galtea.test_cases.create(
    dataset_id=dataset.id,
    user_persona="A team lead evaluating the product",
    goal="Ask for a feature the product does not have",
    scenario="The user asks about an unrelated service",
    seed_session_id=test_case.seed_session_id,
    max_iterations=2,
)
# @end test_case_from_existing_session
if reused.seed_session_id is None:
    raise ValueError("the second test case holds no predefined conversation")
# Galtea copies the conversation, so the two test cases never share one session.
if reused.seed_session_id == test_case.seed_session_id:
    raise ValueError("the second test case reuses the session instead of a copy of it")
print(f"Test case {reused.id} starts from a copy: {reused.seed_session_id}")
