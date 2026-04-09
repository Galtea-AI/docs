
from datetime import datetime

import requests
from _test_helpers import create_test_product
from galtea import Galtea, SpecificationType, TestType

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S")

galtea = Galtea(api_key="YOUR_API_KEY")

# Create a product for this demo
product_id = create_test_product(galtea, name="Trace Examples Demo " + run_identifier)

version = galtea.versions.create(
    name="Version-" + run_identifier,
    product_id=product_id,
    description="Demo version for trace examples",
)
if version is None:
    raise ValueError("version is None")
version_id = version.id

session = galtea.sessions.create(version_id=version_id, is_production=True)
if session is None:
    raise ValueError("session is None")

galtea.inference_results.create(
    session.id,
    "Dummy Input",
    "Dummy Output",
)


# @start wait_for_basic
# Create evaluations and wait for them to complete
evaluations = galtea.evaluations.create(
    session_id=session.id,
    metrics=[{"name": "Non-Toxic"}, {"name": "Unbiased"}],
)

# Wait for all evaluations to leave PENDING status
completed = galtea.evaluations.wait_for(
    evaluation_ids=[e.id for e in evaluations],
)

for evaluation in completed:
    print(f"{evaluation.id}: {evaluation.status} — score: {evaluation.score}")
# @end wait_for_basic

# @start wait_for_custom_timeout
# Wait with a custom timeout and poll interval
completed = galtea.evaluations.wait_for(
    evaluation_ids=[e.id for e in evaluations],
    timeout=600,       # wait up to 10 minutes
    poll_interval=10,  # check every 10 seconds
)
# @end wait_for_custom_timeout

specification = galtea.specifications.create(
    product_id,
    "The user should always salute the user with a greeting before providing an answer.",
    SpecificationType.POLICY,
    TestType.BEHAVIOR,
)

if specification is None:
    raise ValueError("specification is None")

metric = galtea.metrics.create(
    name="accuracy_v1_" + run_identifier,
    evaluator_model_name="GPT-4.1",
    source="partial_prompt",
    judge_prompt="Determine whether the actual output contains a greeting before the answer.",
    evaluation_params=["input", "actual_output"],
    tags=["custom", "accuracy"],
    description="A custom accuracy metric.",
)
if metric is None:
    raise ValueError("metric is None")
metric_id: str = metric.id

galtea.specifications.link_metrics(
    specification_id=specification.id,
    metric_ids=[metric_id],
)

behavior_test = galtea.tests.create(
    product_id=product_id,
    name="behavior-test-from-file-docs-" + run_identifier,
    type="BEHAVIOR",
    test_file_path="path/to/behavior_test.csv",
)

if behavior_test is None:
    raise ValueError("behavior_test is None")

galtea.specifications.link_tests(
    specification_id=specification.id,
    test_ids=[behavior_test.id],
)

def my_agent(messages: list[dict]) -> str:
    return f"Your model output"

# @start wait_for_run_lifecycle
# Full async evaluation lifecycle: run, then wait for results
result = galtea.evaluations.run(
    version_id=version_id,
    agent=my_agent,
)

# Collect evaluation IDs from the run result
evaluation_ids = [e.id for e in result["evaluations"]]

# Wait for all evaluations to complete
completed = galtea.evaluations.wait_for(evaluation_ids=evaluation_ids)

for evaluation in completed:
    print(f"Metric {evaluation.metric_id}: {evaluation.status} — {evaluation.score}")
# @end wait_for_run_lifecycle

# Endpoint-connection mode requires a deployed endpoint; skip when not configured
try:
    # @start wait_for_job_id
    # Endpoint-connection mode: run() returns a jobId instead of evaluations
    result = galtea.evaluations.run(version_id=version_id)
    job_id = result["jobId"]

    # Wait for the job to complete and all evaluations to finish
    completed = galtea.evaluations.wait_for(job_id=job_id, timeout=600)

    for evaluation in completed:
        print(f"Metric {evaluation.metric_id}: {evaluation.status} — {evaluation.score}")
    # @end wait_for_job_id
except requests.exceptions.HTTPError as e:
    if e.response.status_code == 400 and "version does not have a conversation endpoint connection" in e.response.text.lower():
        print("Skipped (expected: endpoint-connection mode requires a deployed endpoint)")
    else:
        raise
