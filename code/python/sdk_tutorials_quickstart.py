import time
from datetime import datetime

from _test_helpers import create_test_product
from requests.exceptions import HTTPError

from galtea import (
    AgentInput,
    AgentResponse,
    Galtea,
)

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea = Galtea(api_key="YOUR_API_KEY")

# === Start with cleanup code to ensure a fresh environment ===
products = galtea.products.list(limit=100)
print(f"Cleaning up {len(products)} products")
for product in products:
    try:
        # Delete specifications individually first to avoid batch soft-delete
        # constraint violations when duplicate specs exist on a product
        specs = galtea.specifications.list(product_id=product.id)
        for spec in specs:
            try:
                galtea.specifications.delete(specification_id=spec.id)
            except Exception:
                pass
        galtea.products.delete(product_id=product.id)
    except Exception:
        pass
products = galtea.products.list(limit=100)
print(f"Remaining products after cleanup: {len(products)}")
# === End cleanup code ===

# Register a product for this demo
_created_product_id = create_test_product(
    galtea,
    name="Financial Assistant",
    description="A conversational AI assistant designed to provide financial guidance to individuals with limited financial literacy. It empowers users to make informed investment decisions and manage their wealth effectively through accessible, easy-to-understand information.",
    capabilities="* Explain basic investment concepts (e.g., stocks, bonds, mutual funds)\n* Provide information on different types of savings and investment accounts\n* Guide users on creating a simple personal budget\n* Offer general strategies for wealth management\n* Define financial terms and jargon\n",
    inabilities="* Cannot provide personalized investment recommendations or financial advice\n* Does not execute trades or manage user investment portfolios\n* Cannot access user's bank accounts or financial information\n* Does not offer tax advice\n* Cannot assist with loan applications or debt management\n",
    policies="",
)
versions = galtea.versions.list(product_id=_created_product_id)
if versions is None or len(versions) == 0:
    galtea.versions.create(
        product_id=_created_product_id,
        name="v1",
        description="Created via the Galtea SDK quickstart example",
    )

# @start find_ids
# Look your product and version up by name — no need to copy IDs from the dashboard.
product = galtea.products.get_by_name(name="Financial Assistant")
version = galtea.versions.get_by_name(product_id=product.id, version_name="v1")

product_id = product.id
version_id = version.id
# @end find_ids

# @start create_accuracy_test
dataset = galtea.datasets.create(
    name="rag-accuracy-test",
    type="ACCURACY",
    product_id=product_id,
    ground_truth_file_path="knowledge.md",
    language="english",
    max_test_cases=20,
)
# @end create_accuracy_test
if dataset is None:
    raise ValueError("Failed to create accuracy test")
accuracy_dataset = dataset

# @start create_security_test
dataset = galtea.datasets.create(
    name="misuse-security-test",
    type="SECURITY",
    product_id=product_id,
    variants=["misuse"],
    strategies=["original"],  # original must always be included
    max_test_cases=20,
)
# @end create_security_test
if dataset is None:
    raise ValueError("Failed to create security test")
security_dataset = dataset

# @start create_behavior_test
dataset = galtea.datasets.create(
    name="conversation-behavior-test",
    type="BEHAVIOR",
    product_id=product_id,
    language="english",
    max_test_cases=20,
    strategies=["written"],
)
# @end create_behavior_test
if dataset is None:
    raise ValueError("Failed to create behavior test")
behavior_dataset = dataset

max_wait_iterations = 120  # e.g., wait up to 2 minutes
for _ in range(max_wait_iterations):
    # Pick the first test that has a URI
    dataset = galtea.datasets.get(dataset_id=accuracy_dataset.id)
    if dataset.uri:
        break
    print("Waiting for accuracy test file to be ready...")
    time.sleep(1)
else:
    raise ValueError("Test file URI is still None after waiting. Test id: " + dataset.id)

max_wait_iterations = 120  # e.g., wait up to 2 minutes
for _ in range(max_wait_iterations):
    dataset = galtea.datasets.get(dataset_id=security_dataset.id)
    if dataset.uri:
        break
    print("Waiting for security test file to be ready...")
    time.sleep(1)
else:
    raise ValueError("Test file URI is still None after waiting. Test id: " + dataset.id)

max_wait_iterations = 120  # e.g., wait up to 2 minutes
for _ in range(max_wait_iterations):
    dataset = galtea.datasets.get(dataset_id=behavior_dataset.id)
    if dataset.uri:
        break
    print("Waiting for behavior test file to be ready...")
    time.sleep(1)
else:
    raise ValueError("Test file URI is still None after waiting. Test id: " + dataset.id)

# Ensure it works with all test types, then do the actual demo code
test_cases = galtea.test_cases.list(dataset_id=accuracy_dataset.id)
if len(test_cases) == 0:
    raise ValueError("No test cases found for accuracy test")
accuracy_test_cases = test_cases
test_cases = galtea.test_cases.list(dataset_id=security_dataset.id)
if len(test_cases) == 0:
    raise ValueError("No test cases found for security test")
security_test_cases = test_cases
test_cases = galtea.test_cases.list(dataset_id=behavior_dataset.id)
if len(test_cases) == 0:
    raise ValueError("No test cases found for behavior test")
behavior_test_cases = test_cases

# @start list_test_cases
test_cases = galtea.test_cases.list(dataset_id=dataset.id)
print(f"Using dataset '{dataset.name}' with {len(test_cases)} test cases.")
# @end list_test_cases

# @start metric_pick_quality
metric = galtea.metrics.get_by_name(name="Factual Accuracy")
# @end metric_pick_quality
if metric is None:
    raise ValueError("Could not find metric by name 'Factual Accuracy'")
accuracy_metric = metric

# @start metric_pick_red_team
metric = galtea.metrics.get_by_name(name="Misuse Resilience")
# @end metric_pick_red_team
if metric is None:
    raise ValueError("Could not find metric by name 'Misuse Resilience'")
security_metric = metric

# @start metric_pick_scenarios
metric = galtea.metrics.get_by_name(name="Role Adherence")
# @end metric_pick_scenarios
if metric is None:
    raise ValueError("Could not find metric by name 'Role Adherence'")
behavior_metric = metric


# @start define_agent_simple
def my_agent(user_message: str) -> str:
    # In a real scenario, call your model here
    return f"Your model output to: {user_message}"


# @end define_agent_simple


# @start define_agent_chat
def my_agent(messages: list[dict]) -> str:
    # messages follows the standard chat format:
    # [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
    user_message = messages[-1]["content"]
    return f"Your model output to: {user_message}"


# @end define_agent_chat


# @start define_agent_structured_function
def my_agent(input_data: AgentInput) -> AgentResponse:
    user_message = input_data.last_user_message_str()

    # Access structured input fields from the first user message's metadata
    # (e.g. when test case input is {"user_message": "hello", "chat_type": "support"})
    first_msg = input_data.messages[0] if input_data.messages else None
    chat_type = first_msg.metadata.get("chat_type") if first_msg and first_msg.metadata else None

    # In a real scenario, call your model here
    model_output = f"Your model output to: {user_message}"
    # Return AgentResponse with optional usage/cost tracking
    return AgentResponse(
        content=model_output,
        usage_info={"input_tokens": 100, "output_tokens": 50},
    )


# @end define_agent_structured_function


# Setup: create a specification, then link a metric AND a test to it so
# evaluations.run() has something to discover and evaluate.
_spec = galtea.specifications.create(
    product_id=product_id,
    name="Stays in its financial-assistant role",
    description="The assistant must stay in its role and follow its guidelines when answering.",
    type="POLICY",
    dataset_type="BEHAVIOR",
)
if _spec is None:
    raise ValueError("Failed to create specification")
galtea.specifications.link_metrics(
    specification_id=_spec.id,
    metric_ids=[behavior_metric.id],
)
galtea.specifications.link_datasets(
    specification_id=_spec.id,
    dataset_ids=[behavior_dataset.id],
)

# @start run_evaluation_run
# One call resolves your specifications, their datasets and metrics, runs your agent
# on every test case, and submits the results for scoring.
result = galtea.evaluations.run(
    version_id=version_id,
    agent=my_agent,
)
print(f"Launched {result['testCaseCount']} test cases across {len(result['specifications'])} specifications")
# @end run_evaluation_run

# @start see_results
# Block until every evaluation leaves PENDING (defaults: up to 300s, polling every 5s).
completed = galtea.evaluations.wait_for(
    evaluation_ids=[e.id for e in result["evaluations"]],
)

# A readable pass/fail summary. Each metric defines its own passing threshold;
# 0.5 is used here as a simple example — adjust it to your metrics.
pass_threshold = 0.5
scored = [e for e in completed if e.score is not None]
passed = [e for e in scored if e.score >= pass_threshold]
print(f"{len(passed)}/{len(scored)} evaluations scored >= {pass_threshold}")

# Triage: list sessions whose agent run failed and produced no output to score.
failed_sessions = galtea.sessions.list(version_id=version_id, status="FAILED")
if failed_sessions:
    print(f"{len(failed_sessions)} sessions failed to run — inspect them:")
    for session in failed_sessions:
        print(f"  session {session.id}")

print(f"View full results at: https://platform.galtea.ai/product/{product_id}")
# @end see_results

# === Cleanup: delete the product created for this demo ===
galtea.products.delete(product_id=_created_product_id)
