import time
from datetime import datetime

from galtea import (
    Agent,
    AgentInput,
    AgentResponse,
    Galtea,
    TraceType,
    clear_context,
    set_context,
    start_trace,
    trace,
)
from galtea.domain.models.trace import TraceBase

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

# @start galtea_client
galtea = Galtea(api_key="YOUR_API_KEY")
# @end galtea_client


# @start product_list
products = galtea.products.list(limit=10)
# @end product_list

# If none exist, Create a product with direct API call since SDK does not have create product method
if products is None or len(products) == 0:
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

product_id = products[0].id
product_name = products[0].name

# @start product_get
product = galtea.products.get(product_id=product_id)
# @end product_get

if product is None:
    raise ValueError("product from get is None")

# @start product_get_by_name
product = galtea.products.get_by_name(name=product_name)
# @end product_get_by_name
if product is None:
    raise ValueError("product from get_by_name is None")

version_name = "Version-docs-" + run_identifier

# @start version_create
version = galtea.versions.create(
    name=version_name,
    product_id=product_id,
    description="Demo version created via SDK",
)
# @end version_create
if version is None:
    raise ValueError("version from create is None")

version_id = version.id

# @start version_list
versions = galtea.versions.list(product_id=product_id, limit=5)
# @end version_list
if versions is None or len(versions) == 0:
    raise ValueError("versions from list is None or empty")

# @start version_get
version = galtea.versions.get(version_id=version_id)
# @end version_get
if version is None:
    raise ValueError("version from get is None")

# @start version_get_by_name
version = galtea.versions.get_by_name(product_id=product_id, version_name=version_name)
# @end version_get_by_name
if version is None:
    raise ValueError("version from get_by_name is None")

test_name = "quality-test-docs-" + run_identifier

# @start test_create
test = galtea.tests.create(
    name=test_name,
    type="QUALITY",
    product_id=product_id,
    ground_truth_file_path="path/to/knowledge.md",
    language="english",
    max_test_cases=5,
)
# @end test_create
if test is None:
    raise ValueError("test from create is None")

test_id = test.id

# @start test_list
tests = galtea.tests.list(product_id=product_id, limit=10)
# @end test_list
if tests is None or len(tests) == 0:
    raise ValueError("tests from list is None or empty")

# @start test_get
test = galtea.tests.get(test_id=test_id)
# @end test_get
if test is None:
    raise ValueError("test from get is None")

# @start test_get_by_name
test = galtea.tests.get_by_name(product_id=product_id, test_name=test_name)
# @end test_get_by_name
if test is None:
    raise ValueError("test from get_by_name is None")


# @start test_case_create
test_case = galtea.test_cases.create(
    test_id=test_id,
    input="What is the capital of France?",
    expected_output="Paris",
    context="Geography facts",
    variant="original",
)
# @end test_case_create
if test_case is None:
    raise ValueError("test_case from create is None")

test_case_id = test_case.id

# @start test_case_list
test_cases = galtea.test_cases.list(test_id=test_id, limit=20)
# @end test_case_list
if test_cases is None or len(test_cases) == 0:
    raise ValueError("test_cases from list is None or empty")

# @start test_case_get
test_case = galtea.test_cases.get(test_case_id=test_case_id)
# @end test_case_get
if test_case is None:
    raise ValueError("test_case from get is None")

metric_name = "metric-docs-" + run_identifier

# @start metric_create
metric = galtea.metrics.create(
    name=metric_name,
    test_type="QUALITY",
    evaluator_model_name="GPT-4.1",
    source="partial_prompt",
    judge_prompt="Evaluate if the actual_output is polite.",
    evaluation_params=["actual_output"],
    description="Checks politeness",
)
# @end metric_create
if metric is None:
    raise ValueError("metric from create is None")

metric_name = metric.name
metric_id = metric.id

# @start metric_list
metrics = galtea.metrics.list(limit=20)
# @end metric_list
if metrics is None or len(metrics) == 0:
    raise ValueError("metrics from list is None or empty")

# @start metric_get
metric = galtea.metrics.get(metric_id=metric_id)
# @end metric_get
if metric is None:
    raise ValueError("metric from get is None")

# @start metric_get_by_name
metric = galtea.metrics.get_by_name(name=metric_name)
# @end metric_get_by_name
if metric is None:
    raise ValueError("metric from get_by_name is None")


# @start session_create
session = galtea.sessions.create(
    version_id=version_id, test_case_id=test_case_id, is_production=False
)
# @end session_create
if session is None:
    raise ValueError("session from create is None")

session_id = session.id
custom_session_id = "custom-session-" + run_identifier

# @start session_get_or_create
session = galtea.sessions.get_or_create(
    custom_id=custom_session_id,
    version_id=version_id,
    test_case_id=test_case_id,
)
# @end session_get_or_create
if session is None:
    raise ValueError("session from get_or_create is None")

# @start session_list
sessions = galtea.sessions.list(version_id=version_id, limit=10)
# @end session_list
if sessions is None or len(sessions) == 0:
    raise ValueError("sessions from list is None or empty")

# @start session_get
session = galtea.sessions.get(session_id=session_id)
# @end session_get
if session is None:
    raise ValueError("session from get is None")

# @start session_get_by_custom_id
session_by_custom = galtea.sessions.get_by_custom_id(custom_id=custom_session_id)
# @end session_get_by_custom_id
if session_by_custom is None:
    raise ValueError("session from get_by_custom_id is None")


# @start inference_result_create
inference_result = galtea.inference_results.create(
    session_id=session_id,
    input="What is the capital of France?",
    output="Paris",
    latency=150.5,
)
# @end inference_result_create
if inference_result is None:
    raise ValueError("inference_result from create is None")

inference_result_id = inference_result.id

# @start inference_result_create_batch
inference_result = galtea.inference_results.create_batch(
    session_id=session_id,
    conversation_turns=[
        {"role": "user", "content": "Hi"},
        {"role": "assistant", "content": "Hello!"},
    ],
)
# @end inference_result_create_batch
if inference_result is None or len(inference_result) == 0:
    raise ValueError("inference_results from create_batch is None or empty")

# @start inference_result_update
inference_result = galtea.inference_results.update(
    inference_result_id=inference_result_id,
    output="Paris is the capital.",
    cost=0.0001,
)
# @end inference_result_update
if inference_result is None:
    raise ValueError("inference_result from update is None")

# @start inference_result_list
inference_result = galtea.inference_results.list(session_id=session_id)
# @end inference_result_list
if inference_result is None or len(inference_result) == 0:
    raise ValueError("inference_results from list is None or empty")

# @start inference_result_get
inference_result = galtea.inference_results.get(inference_result_id=inference_result_id)
# @end inference_result_get
if inference_result is None:
    raise ValueError("inference_result from get is None")


# @start inference_result_create_and_evaluate_basic
# Create inference result and evaluate in a single call
inference_result, evaluations = galtea.inference_results.create_and_evaluate(
    session_id=session_id,
    input="What is the capital of France?",
    output="The capital of France is Paris.",
    metrics=["Factual Accuracy", "Answer Relevancy"],
)
# @end inference_result_create_and_evaluate_basic
if inference_result is None:
    raise ValueError("inference_result from create_and_evaluate is None")
if evaluations is None or len(evaluations) == 0:
    raise ValueError("evaluations from create_and_evaluate is None or empty")


# @start inference_result_generate
# Define an Agent to be used for generation
class MyAgent(Agent):
    def call(self, input_data: AgentInput) -> AgentResponse:
        # Implement your agent logic here, using input_data content
        return AgentResponse(content="Generated response")


inference_result = galtea.inference_results.generate(
    agent=MyAgent(), session=session, user_input="Generate something"
)
# @end inference_result_generate
if inference_result is None:
    raise ValueError("inference_result from generate is None")


# @start trace_decorator
@trace(type=TraceType.TOOL, name="calculate_sum")
def calculate(a, b):
    return a + b


class MyMathsAgent(Agent):
    def call(self, input_data: AgentInput) -> AgentResponse:
        message = input_data.last_user_message_str() or ""
        a, b = map(int, message.split(","))
        return AgentResponse(content=f"Result: {calculate(a, b)}")


inference_result = galtea.inference_results.generate(
    agent=MyMathsAgent(),
    session=session,
    user_input="5,3",
)
# @end trace_decorator

# @start trace_set_context
trace_context = set_context(inference_result_id=inference_result_id)
# @end trace_set_context

# @start trace_clear_context
clear_context(trace_context)
# @end trace_clear_context

# @start trace_start_trace
with start_trace("manual_span", type="SPAN") as span:
    # Do work
    span.update(metadata={"status": "done"})
# @end trace_start_trace


# @start trace_create
manual_trace = galtea.traces.create(
    inference_result_id=inference_result_id,
    name="manual_db_call",
    type=TraceType.TOOL,
    start_time="2023-01-01T12:00:00Z",
    end_time="2023-01-01T12:00:01Z",
)
# @end trace_create

trace_id = manual_trace.id if manual_trace else "YOUR_TRACE_ID"

# @start trace_create_batch
galtea.traces.create_batch(
    [
        TraceBase(
            inference_result_id=inference_result_id,
            name="batch_trace_1",
            type=TraceType.SPAN,
        )
    ]
)
# @end trace_create_batch

# @start trace_list
traces = galtea.traces.list(inference_result_id=inference_result_id)
# @end trace_list
if traces is None or len(traces) == 0:
    raise ValueError("traces from list is None or empty")

trace_id = traces[0].id
if trace_id is None:
    raise ValueError("trace_id is None")

# @start trace_get
trace = galtea.traces.get(trace_id=trace_id)
# @end trace_get
if trace is None:
    raise ValueError("trace from get is None")

scenarios_test = galtea.tests.create(
    product_id=product_id,
    name="scenario-test-from-file-docs-" + run_identifier,
    type="SCENARIOS",
    test_file_path="path/to/scenarios_test.csv",
)

red_teaming_test = galtea.tests.create(
    product_id=product_id,
    name="red-teaming-test-from-file-docs-" + run_identifier,
    type="RED_TEAMING",
    test_file_path="path/to/red_teaming_test.csv",
)

quality_test = galtea.tests.create(
    product_id=product_id,
    name="quality-test-from-file-docs-" + run_identifier,
    type="QUALITY",
    test_file_path="path/to/quality_test.csv",
)

scenarios_test_case = galtea.test_cases.list(test_id=scenarios_test.id, limit=1)[0]

scenarios_session = galtea.sessions.create(
    version_id=version_id,
    is_production=False,
    test_case_id=scenarios_test_case.id,
)


# @start simulator_simulate
class MyCustomAgent(Agent):
    def call(self, input_data: AgentInput) -> AgentResponse:
        # Implement your agent logic here, using input_data content
        return AgentResponse(
            content=f"Generated response for {input_data.last_user_message_str()}"
        )


simulation_result = galtea.simulator.simulate(
    session_id=scenarios_session.id,
    agent=MyCustomAgent(),
    max_turns=3,
    log_inference_results=True,
)
# @end simulator_simulate
if simulation_result is None:
    raise ValueError("simulation_result from simulate is None")

# @start evaluation_create_single_turn
evaluations = galtea.evaluations.create_single_turn(
    version_id=version_id,
    test_case_id=test_case_id,
    actual_output="Paris",
    metrics=[{"name": "Factual Accuracy"}],
)
# @end evaluation_create_single_turn
if evaluations is None or len(evaluations) == 0:
    raise ValueError("evaluations from create_single_turn is None or empty")

self_hosted_metric_name = "self-hosted-metric-docs"
try:
    self_hosted_metric = galtea.metrics.get_by_name(name=self_hosted_metric_name)
except Exception:
    self_hosted_metric = None
if self_hosted_metric is not None:
    galtea.metrics.delete(metric_id=self_hosted_metric.id)
self_hosted_metric = galtea.metrics.create(
    name=self_hosted_metric_name,
    test_type="QUALITY",
    source="self_hosted",
    description="A self-hosted metric for demonstration",
)
if self_hosted_metric is None:
    raise ValueError("self_hosted_metric from create is None")

# @start evaluation_create_single_turn_self_hosted
evaluations = galtea.evaluations.create_single_turn(
    version_id=version_id,
    test_case_id=test_case_id,
    actual_output="Paris",
    metrics=[{"name": self_hosted_metric.name, "score": 0.75}],
)
# @end evaluation_create_single_turn_self_hosted
if evaluations is None or len(evaluations) == 0:
    raise ValueError("evaluations from create_single_turn is None or empty")

# @start inference_result_create_and_evaluate_precomputed
# With pre-computed scores for self-hosted metrics
inference_result, evaluations = galtea.inference_results.create_and_evaluate(
    session_id=session_id,
    output="Model response...",
    metrics=[
        {"name": "Factual Accuracy"},
        {"name": self_hosted_metric.name, "score": 0.95},  # Pre-computed score
    ],
)
# @end inference_result_create_and_evaluate_precomputed
if inference_result is None or evaluations is None:
    raise ValueError("inference_result or evaluations from create_and_evaluate is None")

# @start inference_result_create_and_evaluate_custom
# With dynamic score calculation using CustomScoreEvaluationMetric
from galtea.utils.custom_score_metric import CustomScoreEvaluationMetric


class MyMetric(CustomScoreEvaluationMetric):
    def measure(self, *args, actual_output: str | None = None, **kwargs) -> float:
        # Your custom scoring logic
        return 0.95


custom_metric = MyMetric(name=self_hosted_metric.name)

inference_result, evaluations = galtea.inference_results.create_and_evaluate(
    session_id=session_id,
    output="Model response...",
    metrics=[
        {"name": "Factual Accuracy"},
        {"score": custom_metric},  # Dynamic score calculation
    ],
)
# @end inference_result_create_and_evaluate_custom
if inference_result is None or evaluations is None:
    raise ValueError("inference_result or evaluations from create_and_evaluate is None")

# @start evaluation_create_single_turn_production
evaluations = galtea.evaluations.create_single_turn(
    version_id=version_id,
    is_production=True,
    input="What is the capital of France?",
    actual_output="Paris",
    metrics=[{"name": "Answer Relevancy"}],
)
# @end evaluation_create_single_turn_production

# @start evaluation_create
evaluations = galtea.evaluations.create(
    session_id=session_id,
    metrics=[{"name": "Role Adherence"}, {"name": "Conversation Relevancy"}],
)
# @end evaluation_create
if evaluations is None or len(evaluations) == 0:
    raise ValueError("evaluations from create is None or empty")

# @start evaluation_create_self_hosted
evaluations = galtea.evaluations.create(
    session_id=session_id,
    metrics=[{"name": self_hosted_metric.name, "score": 0.85}],
)
# @end evaluation_create_self_hosted
if evaluations is None or len(evaluations) == 0:
    raise ValueError("evaluations from create is None or empty")

evaluation_id = evaluations[0].id

# @start evaluation_create_from_inference_result
# Evaluate a specific inference result by providing its ID
evaluations = galtea.evaluations.create(
    inference_result_id=inference_result_id,
    metrics=["Factual Accuracy", "Answer Relevancy"],
)
# @end evaluation_create_from_inference_result
if evaluations is None or len(evaluations) == 0:
    raise ValueError(
        "evaluations from create with inference_result_id is None or empty"
    )

# @start evaluation_create_production
production_session = galtea.sessions.create(version_id=version_id, is_production=True)

# Create an inference result for the production session first
production_inference_result = galtea.inference_results.create(
    session_id=production_session.id,
    input="Production user query",
    output="Production response",
)

evaluations = galtea.evaluations.create(
    session_id=production_session.id,
    metrics=[{"name": self_hosted_metric.name, "score": 0.85}],
)
# @end evaluation_create_production
if evaluations is None or len(evaluations) == 0:
    raise ValueError("evaluations from create is None or empty")

# @start evaluation_list
evaluations = galtea.evaluations.list(session_id=session_id)
# @end evaluation_list
if evaluations is None or len(evaluations) == 0:
    raise ValueError("evaluations_list from list is None or empty")

# @start evaluation_display_results
print(f"Total evaluations: {len(evaluations)}")
scores = [ev.score for ev in evaluations if ev.score is not None]
if len(scores) > 0:
    average_score = sum(scores) / len(scores)
    print(f"Average Score: {average_score}")
else:
    print("No scores available yet")

print("Detailed Results:")
for evaluation in evaluations:
    metric = galtea.metrics.get(metric_id=evaluation.metric_id)
    print(f"Metric: {metric}")
    print(f"    Score: {evaluation.score}")
    print(f"    Reason: {evaluation.reason}")
# @end evaluation_display_results

# @start evaluation_get
evaluation = galtea.evaluations.get(evaluation_id=evaluation_id)
# @end evaluation_get
if evaluation is None:
    raise ValueError("evaluation from get is None")


# Check if test has finished generating before downloading, if not, await

max_wait_iterations = 120  # e.g., wait up to 2 minutes
for _ in range(max_wait_iterations):
    test = galtea.tests.get(test_id=test.id)
    if test.uri:
        break
    print("Waiting for test file to be ready...")
    time.sleep(1)
else:
    raise ValueError("Test file URI is still None after waiting. Test id: " + test.id)

# @start test_download
downloaded_path = galtea.tests.download(test=test, output_directory="./.temp")
# @end test_download
if downloaded_path is None:
    raise ValueError("downloaded_path from download is None")

# =============================================================================
# CLEANUP RESOURCES in reverse order
# =============================================================================

# @start evaluation_delete
galtea.evaluations.delete(evaluation_id=evaluation_id)
# @end evaluation_delete

# @start trace_delete
galtea.traces.delete(trace_id=trace_id)
# @end trace_delete

# @start inference_result_delete
galtea.inference_results.delete(inference_result_id=inference_result_id)
# @end inference_result_delete

# @start session_delete
galtea.sessions.delete(session_id=session_id)
# @end session_delete

# @start version_delete
galtea.versions.delete(version_id=version_id)
# @end version_delete

# @start test_case_delete
galtea.test_cases.delete(test_case_id=test_case_id)
# @end test_case_delete

# @start test_delete
galtea.tests.delete(test_id=test_id)
# @end test_delete

# Deleting the product ensures complete cleanup of all associated resources
# @start product_delete
galtea.products.delete(product_id=product_id)
# @end product_delete

# Since metrics are organization-level, we delete the created metric as well
# @start metric_delete
galtea.metrics.delete(metric_id=metric_id)
# @end metric_delete

# === Ensure no Leftovers ===
galtea.metrics.delete(metric_id=self_hosted_metric.id)
