"""
Tutorial: Evaluating Conversations
Demonstrates how to evaluate multi-turn conversations using Galtea's session-based workflow.
"""

from datetime import datetime

from galtea import Galtea

from _test_helpers import create_test_product

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea_client = Galtea(api_key="YOUR_API_KEY")

# Register a product for this demo
product_id = create_test_product(
    galtea_client,
    name="Conversation Eval Demo " + run_identifier,
    description="Demo product for conversation evaluation tutorial",
    capabilities="Demo capabilities",
    inabilities="Demo inabilities",
)

version = galtea_client.versions.create(
    name="Version-" + run_identifier,
    product_id=product_id,
    description="Demo version for conversation evaluation",
)
if version is None:
    raise ValueError("version is None")
version_id = version.id

# Create a behavior test for test-based evaluation
behavior_dataset = galtea_client.datasets.create(
    product_id=product_id,
    name="behavior-test-" + run_identifier,
    type="BEHAVIOR",
    dataset_file_path="path/to/behavior_dataset.csv",
)
if behavior_dataset is None:
    raise ValueError("behavior_dataset is None")


# Create a specification with linked metrics so the specification-based evaluation
# examples below work. Reused by every `specification_ids=` snippet in this tutorial.
role_adherence = galtea_client.metrics.get_by_name(name="Role Adherence")
conversation_relevancy = galtea_client.metrics.get_by_name(name="Conversation Relevancy")
knowledge_retention = galtea_client.metrics.get_by_name(name="Knowledge Retention")
if role_adherence is None or conversation_relevancy is None or knowledge_retention is None:
    raise ValueError("Could not find the conversational metrics to link")

conversation_spec = galtea_client.specifications.create(
    product_id=product_id,
    name="Consistent in-role conversation",
    description="The assistant stays in role and gives relevant, consistent answers across the conversation.",
    type="CAPABILITY",
    metric_ids=[role_adherence.id, conversation_relevancy.id, knowledge_retention.id],
)


# Agent function used by the Conversation Simulator. In the docs this is shown via the
# "Agent Integration Options" snippet, so it is defined here (to keep the script
# runnable) but is not embedded into the page.
def my_agent(user_message: str) -> str:
    return f"Response to: {user_message}"


# @start capture_test_based
# Fetch your test cases (created from a CSV of behavior test cases)
test_cases = galtea_client.test_cases.list(dataset_id=behavior_dataset.id)
if not test_cases:
    raise ValueError("No test cases found")

# Take one test case (loop over `test_cases` to evaluate them all)
test_case = test_cases[0]

# Create a session for the test case, then let the simulator drive the
# conversation between a synthetic user and your agent function (`my_agent`)
session = galtea_client.sessions.create(version_id=version_id, test_case_id=test_case.id)
galtea_client.simulator.simulate(
    session_id=session.id,
    agent=my_agent,
    max_turns=test_case.max_iterations or 10,
)
# @end capture_test_based


# @start capture_past_conversations
# The conversation already happened: create a session (no test_case_id) and log every turn
session = galtea_client.sessions.create(
    version_id=version_id,
    custom_id="EXTERNAL_CONVERSATION_ID",  # optional: map to your own conversation ID
    is_production=True,  # set to True when these are real users
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
galtea_client.traces.create_batch(session_id=session.id, conversation_turns=conversation_turns)
# @end capture_past_conversations


# @start capture_monitoring_individual
# Create a production session and log each turn as it happens in your live app
session = galtea_client.sessions.create(version_id=version_id, is_production=True)


def your_product(user_input: str) -> str:
    return f"This is a simulated response to '{user_input}'"


def handle_turn(user_input: str) -> str:
    model_output = your_product(user_input)
    galtea_client.traces.create(session_id=session.id, input=user_input, output=model_output)
    return model_output


# Simulate production interactions
handle_turn("Hello!")
handle_turn("What services do you offer?")
# @end capture_monitoring_individual


# @start capture_monitoring_batch
# Or, if you already have the full transcript, create the session and log all turns at once
session = galtea_client.sessions.create(version_id=version_id, is_production=True)

conversation_turns = [
    {"role": "user", "content": "What are some lower-risk investment strategies?"},
    {
        "role": "assistant",
        "content": "For lower-risk investments, consider diversified index funds, bonds, or Treasury securities.",
    },
]

galtea_client.traces.create_batch(session_id=session.id, conversation_turns=conversation_turns)
# @end capture_monitoring_batch


# @start finish_session
# When the live conversation is over, finish the session. This closes it (status COMPLETED)
# so it accepts no more turns. Under a default-config product this is how a session completes,
# and a Monitor scores only closed sessions, so finishing gets it picked up on the next scan.
galtea_client.sessions.finish(session_id=session.id)
# @end finish_session


# @start evaluate_specifications
# Evaluate the whole conversation; metrics are resolved from the specifications automatically
galtea_client.evaluations.create(
    session_id=session.id,
    specification_ids=[conversation_spec.id],
)
# @end evaluate_specifications


# @start evaluate_metrics
# Evaluate the whole conversation by listing metrics explicitly
galtea_client.evaluations.create(
    session_id=session.id,
    metrics=[
        {"name": "Conversation Relevancy"},
        {"name": "Role Adherence"},
        {"name": "Knowledge Retention"},
    ],
)
# @end evaluate_metrics


metric_name = "conversation-consistency"
metric_created = None
try:
    metric_created = galtea_client.metrics.get_by_name(metric_name)
except Exception:
    pass
if metric_created is None:
    metric_created = galtea_client.metrics.create(
        name=metric_name,
        source="self_hosted",
    )
print(f"Custom metric created: {metric_created}")


# @start custom_metric_multi_turn
from galtea import CustomScoreEvaluationMetric, Trace


class ConversationConsistency(CustomScoreEvaluationMetric):
    """Scores how consistently the assistant responds across all turns."""

    def __init__(self):
        super().__init__(name=metric_name)

    def measure(self, *args, traces: list[Trace] | None = None, **kwargs) -> float:
        if not traces:
            return 0.0
        # Access the full conversation for cross-turn analysis
        assistant_outputs = [trace.actual_output for trace in traces if trace.actual_output]
        if len(assistant_outputs) < 2:
            return 1.0
        # Your custom logic here (e.g., check for contradictions across turns)
        return 0.9


galtea_client.evaluations.create(
    session_id=session.id,
    metrics=[
        {"name": "Role Adherence"},
        {"score": ConversationConsistency()},  # Custom multi-turn metric
    ],
)
# @end custom_metric_multi_turn


# === Cleanup ===
galtea_client.products.delete(product_id=product_id)
if metric_created:
    galtea_client.metrics.delete(metric_id=metric_created.id)
