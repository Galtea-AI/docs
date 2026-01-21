import time
from datetime import datetime

from galtea import (
    Agent,
    AgentInput,
    AgentResponse,
    Galtea,
)

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea = Galtea(api_key="YOUR_API_KEY")

# === Start with cleanup code to ensure a fresh environment ===
products = galtea.products.list(limit=100)
for product in products:
    galtea.products.delete(product_id=product.id)
# === End cleanup code ===

# Create a product for this demo
client = getattr(galtea, "_Galtea__client", None)
if client is None:
    raise ValueError("Could not access Galtea client for direct API call")
response = client.post(
    "products",
    json={
        "name": "Financial Assistant " + run_identifier,
        "description": "A conversational AI assistant designed to provide financial guidance to individuals with limited financial literacy. It empowers users to make informed investment decisions and manage their wealth effectively through accessible, easy-to-understand information.",
        "securityBoundaries": "* Must refuse to provide specific stock picks or investment strategies tailored to an individual\n* Should not ask for or store personally identifiable financial information (e.g., account numbers, social security numbers)\n* Must reject requests for illegal financial activities\n* Cannot offer advice that could be construed as fiduciary responsibility\n* Must refuse to share information about other users or general market data that is not publicly available\n",
        "capabilities": "* Explain basic investment concepts (e.g., stocks, bonds, mutual funds)\n* Provide information on different types of savings and investment accounts\n* Guide users on creating a simple personal budget\n* Offer general strategies for wealth management\n* Define financial terms and jargon\n",
        "inabilities": "* Cannot provide personalized investment recommendations or financial advice\n* Does not execute trades or manage user investment portfolios\n* Cannot access user's bank accounts or financial information\n* Does not offer tax advice\n* Cannot assist with loan applications or debt management\n",
        "policies": "",
    },
)
products = galtea.products.list(limit=10)
versions = galtea.versions.list(product_id=products[0].id)
if versions is None or len(versions) == 0:
    galtea.versions.create(
        product_id=products[0].id,
        name="quickstart-version-" + run_identifier,
        description="Created via the Galtea SDK quickstart example",
    )

# @start version_your_product
products = galtea.products.list()
for p in products:
    print(p.id, p.name)

versions = galtea.versions.list(product_id=products[0].id)
for v in versions:
    print(v.id, v.name)
# @end version_your_product

# @start set_ids
product_id = "your_product_id"
version_id = "your_version_id"
# @end set_ids

product_id = products[0].id
if product_id is None:
    raise ValueError("No product ID found")
version_id = versions[0].id
if version_id is None:
    raise ValueError("No version ID found")

# @start create_quality_test
test = galtea.tests.create(
    name="rag-quality-test",
    type="QUALITY",
    product_id=product_id,
    ground_truth_file_path="path/to/knowledge.md",
    language="english",
    max_test_cases=20,
)
# @end create_quality_test
if test is None:
    raise ValueError("Failed to create quality test")
quality_test = test

# @start create_red_teaming_test
test = galtea.tests.create(
    name="misuse-red-team-test",
    type="RED_TEAMING",
    product_id=product_id,
    variants=["Misuse"],
    strategies=["Original"],  # Original must always be included
    max_test_cases=20,
)
# @end create_red_teaming_test
if test is None:
    raise ValueError("Failed to create red teaming test")
red_teaming_test = test

# @start create_scenarios_test
test = galtea.tests.create(
    name="conversation-scenarios-test",
    type="SCENARIOS",
    product_id=product_id,
    language="english",
    max_test_cases=20,
    strategies=["written"],
)
# @end create_scenarios_test
if test is None:
    raise ValueError("Failed to create scenarios test")
scenarios_test = test

max_wait_iterations = 120  # e.g., wait up to 2 minutes
for _ in range(max_wait_iterations):
    # Pick the first test that has a URI
    test = galtea.tests.get(test_id=quality_test.id)
    if test.uri:
        break
    print("Waiting for quality test file to be ready...")
    time.sleep(1)
else:
    raise ValueError("Test file URI is still None after waiting. Test id: " + test.id)

max_wait_iterations = 120  # e.g., wait up to 2 minutes
for _ in range(max_wait_iterations):
    test = galtea.tests.get(test_id=red_teaming_test.id)
    if test.uri:
        break
    print("Waiting for red teaming test file to be ready...")
    time.sleep(1)
else:
    raise ValueError("Test file URI is still None after waiting. Test id: " + test.id)

max_wait_iterations = 120  # e.g., wait up to 2 minutes
for _ in range(max_wait_iterations):
    test = galtea.tests.get(test_id=scenarios_test.id)
    if test.uri:
        break
    print("Waiting for scenarios test file to be ready...")
    time.sleep(1)
else:
    raise ValueError("Test file URI is still None after waiting. Test id: " + test.id)

# Ensure it works with all test types, then do the actual demo code
test_cases = galtea.test_cases.list(test_id=quality_test.id)
if len(test_cases) == 0:
    raise ValueError("No test cases found for quality test")
quality_test_cases = test_cases
test_cases = galtea.test_cases.list(test_id=red_teaming_test.id)
if len(test_cases) == 0:
    raise ValueError("No test cases found for red teaming test")
red_teaming_test_cases = test_cases
test_cases = galtea.test_cases.list(test_id=scenarios_test.id)
if len(test_cases) == 0:
    raise ValueError("No test cases found for scenarios test")
scenarios_test_cases = test_cases

# @start list_test_cases
test_cases = galtea.test_cases.list(test_id=test.id)
print(f"Using test '{test.name}' with {len(test_cases)} test cases.")
# @end list_test_cases

# @start metric_pick_quality
metric = galtea.metrics.get_by_name(name="Factual Accuracy")
# @end metric_pick_quality
if metric is None:
    raise ValueError("Could not find metric by name 'Factual Accuracy'")
quality_metric = metric

# @start metric_pick_red_team
metric = galtea.metrics.get_by_name(name="Misuse Resilience")
# @end metric_pick_red_team
if metric is None:
    raise ValueError("Could not find metric by name 'Misuse Resilience'")
red_teaming_metric = metric

# @start metric_pick_scenarios
metric = galtea.metrics.get_by_name(name="Role Adherence")
# @end metric_pick_scenarios
if metric is None:
    raise ValueError("Could not find metric by name 'Role Adherence'")
scenarios_metric = metric


# @start define_your_agent
class MyAgent(Agent):
    def call(self, input_data: AgentInput) -> AgentResponse:
        user_message = input_data.last_user_message_str()
        # In a real scenario, you woyuld call your agent here, e.g., your_model_output = your_product_function(user_message)
        model_output = f"Your model output to the {user_message}"
        return AgentResponse(content=model_output)


# @end define_your_agent

# Ensure it works with all test types, then do the actual demo code
quality_test_case = galtea.test_cases.list(test_id=quality_test.id)[0]
red_teaming_test_case = galtea.test_cases.list(test_id=red_teaming_test.id)[0]
scenarios_test_case = galtea.test_cases.list(test_id=scenarios_test.id)[0]
if (
    quality_test_case is None
    or red_teaming_test_case is None
    or scenarios_test_case is None
):
    raise ValueError("No test cases found for one or more tests")

quality_session = galtea.sessions.create(
    version_id=version_id, test_case_id=quality_test_case.id
)
red_teaming_session = galtea.sessions.create(
    version_id=version_id, test_case_id=red_teaming_test_case.id
)
scenarios_session = galtea.sessions.create(
    version_id=version_id, test_case_id=scenarios_test_case.id
)
if quality_session is None or red_teaming_session is None or scenarios_session is None:
    raise ValueError("Failed to create one or more sessions")
# galtea.simulator.simulate(
#     session_id=quality_session.id,
#     agent=MyAgent(),
#     max_turns=quality_test_case.max_iterations or 10,
# )
quality_inference_result = galtea.inference_results.generate(
    session=quality_session,
    agent=MyAgent(),
    user_input=quality_test_case.input,
)
# galtea.simulator.simulate(
#     session_id=red_teaming_session.id,
#     agent=MyAgent(),
#     max_turns=red_teaming_test_case.max_iterations or 10,
# )
red_teaming_inference_result = galtea.inference_results.generate(
    session=red_teaming_session,
    agent=MyAgent(),
    user_input=red_teaming_test_case.input,
)
conversational_simulation_result = galtea.simulator.simulate(
    session_id=scenarios_session.id,
    agent=MyAgent(),
    max_turns=scenarios_test_case.max_iterations or 10,
)
if (
    quality_inference_result is None
    or red_teaming_inference_result is None
    or conversational_simulation_result is None
):
    raise ValueError("Failed to generate one or more inference results")
galtea.evaluations.create(
    session_id=quality_session.id,
    metrics=[{"name": quality_metric.name}],
)
galtea.evaluations.create(
    session_id=red_teaming_session.id,
    metrics=[{"name": red_teaming_metric.name}],
)
galtea.evaluations.create(
    session_id=scenarios_session.id,
    metrics=[{"name": scenarios_metric.name}],
)

test_cases = quality_test_cases
metric = quality_metric
# @start run_evaluation
for test_case in test_cases:
    # Create a session linked to the test case and version
    session = galtea.sessions.create(
        version_id=version_id,
        test_case_id=test_case.id,
    )

    # Run a synthetic user conversation against your agent
    inference_result = galtea.inference_results.generate(
        session=session,
        agent=MyAgent(),
        user_input=test_case.input,
    )

    # Evaluate the full conversation (session)
    galtea.evaluations.create(
        session_id=session.id,
        metrics=[{"name": metric.name}],
    )

print(f"Submitted evaluations for version {version_id} using test '{test.name}'.")

# @end run_evaluation

# Only run the first scenarios test case
test_cases = scenarios_test_cases[:1]
metric = scenarios_metric
# @start run_evaluation_conversational
for test_case in test_cases:
    # Create a session linked to the test case and version
    session = galtea.sessions.create(
        version_id=version_id,
        test_case_id=test_case.id,
    )

    # Run a synthetic user conversation against your agent
    galtea.simulator.simulate(
        session_id=session.id,
        agent=MyAgent(),
        max_turns=test_case.max_iterations or 10,
    )

    # Evaluate the full conversation (session)
    galtea.evaluations.create(
        session_id=session.id,
        metrics=[{"name": metric.name}],
    )

print(f"Submitted evaluations for version {version_id} using test '{test.name}'.")

# @end run_evaluation_conversational

# @start see_results
print(f"View results at: https://platform.galtea.ai/product/{product_id}")
# @end see_results
