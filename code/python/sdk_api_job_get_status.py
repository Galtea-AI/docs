import time
from datetime import datetime

import requests
from _test_helpers import create_test_product, wait_for_dataset_ready
from galtea import EndpointConnectionType, Galtea

galtea = Galtea(api_key="YOUR_API_KEY")

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S%f")

# Register a product for the demo
product_id = create_test_product(
    galtea,
    name=f"docs-job-status-{run_identifier}",
    description="A financial assistant that provides general guidance on investments, savings, and budgeting.",
    capabilities="Explain basic investment concepts, provide budgeting tips",
)

try:
    # A conversation endpoint connection makes evaluations.run() use the server-side
    # pipeline, which returns a real jobId we can poll. Since #2608, run() pre-flight
    # health-checks the endpoint before queuing, so the placeholder URL below is rejected
    # in the validation environment and the run+status demo self-skips (see handler below);
    # a real deployment points this at a reachable agent and runs the demo end to end.
    endpoint_connection = galtea.endpoint_connections.create(
        name=f"job-status-endpoint-{run_identifier}",
        product_id=product_id,
        url="https://api.example.com/v1/chat",
        type=EndpointConnectionType.CONVERSATION,
        http_method="POST",
        auth_type="BEARER",
        auth_token="YOUR_AUTH_TOKEN",
        input_template='{"message": "{{ input.user_message }}"}',
        output_mapping={"output": "$.response"},
        timeout=30,
    )

    # Link the endpoint connection to the version so evaluations.run() returns a jobId
    version = galtea.versions.create(
        product_id=product_id,
        name=f"v-job-status-{run_identifier}",
        conversation_endpoint_connection_id=endpoint_connection.id,
    )
    version_id = version.id

    # Create a specification with a linked metric so evaluations.run() has something to evaluate
    _metric = galtea.metrics.get_by_name(name="Role Adherence")
    _spec = galtea.specifications.create(
        product_id=product_id,
        name="Helpful financial information",
        description="The assistant provides helpful financial information.",
        type="POLICY",
        dataset_type="BEHAVIOR",
    )
    galtea.specifications.link_metrics(
        specification_id=_spec.id,
        metric_ids=[_metric.id],
    )

    # Create a behavior test linked to the specification, then wait for test cases
    _dataset = galtea.datasets.create(
        product_id=product_id,
        name=f"job-status-test-{run_identifier}",
        type="BEHAVIOR",
        language="english",
        max_test_cases=5,
        strategies=["written"],
        specification_id=_spec.id,
    )
    wait_for_dataset_ready(galtea, _dataset.id)
    for _ in range(120):
        _test_cases = galtea.test_cases.list(dataset_id=_dataset.id)
        if len(_test_cases) > 0:
            break
        print("Waiting for test cases to be generated...")
        time.sleep(1)
    else:
        raise ValueError("Test cases were not generated in time. Test id: " + _dataset.id)

    # job_id is the value returned as result["jobId"] from evaluations.run()
    job_id = galtea.evaluations.run(version_id=version_id)["jobId"]

    # @start get_status
    status = galtea.jobs.get_status(job_id=job_id)
    print(f"State:    {status.state}")
    print(f"Progress: {status.progress}")
    if status.error:
        print(f"Error:    {status.error}")
    if status.result:
        print(f"Result:   {status.result}")
    # @end get_status
except requests.exceptions.HTTPError as e:
    # The pre-flight health check (#2608) rejects the unreachable placeholder endpoint
    # before any job is queued; skip the demo here. A reachable endpoint returns a jobId.
    if e.response.status_code == 400 and (
        "unresponsive or unhealthy endpoint connection" in e.response.text.lower()
        or "does not have a conversation target" in e.response.text.lower()
    ):
        print("Skipped (expected: polling a queued job requires a reachable endpoint connection)")
    else:
        raise
finally:
    # Cleanup
    galtea.products.delete(product_id=product_id)
