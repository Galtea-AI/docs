import time
from datetime import datetime

from _test_helpers import create_test_product
from galtea import Galtea

galtea = Galtea(api_key="YOUR_API_KEY")

run_identifier = datetime.now().strftime("%Y%m%d%H%M%S%f")

# Create product, version, test, and specification for the demo
product_id = create_test_product(
    galtea,
    name=f"docs-eval-run-{run_identifier}",
    description="A financial assistant that provides general guidance on investments, savings, and budgeting.",
    capabilities="Explain basic investment concepts, provide budgeting tips",
)

version = galtea.versions.create(
    product_id=product_id,
    name=f"v-eval-run-{run_identifier}",
)
version_id = version.id

# Create specification with linked metric
_metric = galtea.metrics.get_by_name(name="Role Adherence")
_spec = galtea.specifications.create(
    product_id=product_id,
    description="The assistant provides helpful financial information.",
    type="POLICY",
    test_type="BEHAVIOR",
)
galtea.specifications.link_metrics(
    specification_id=_spec.id,
    metric_ids=[_metric.id],
)

# Create a behavior test linked to the specification, then wait for test cases
_test = galtea.tests.create(
    product_id=product_id,
    name=f"eval-run-test-{run_identifier}",
    type="BEHAVIOR",
    language="english",
    max_test_cases=5,
    strategies=["written"],
    specification_id=_spec.id,
)
for _ in range(120):
    _t = galtea.tests.get(test_id=_test.id)
    if _t.uri:
        break
    print("Waiting for test file to be ready...")
    time.sleep(1)
for _ in range(120):
    _test_cases = galtea.test_cases.list(test_id=_test.id)
    if len(_test_cases) > 0:
        break
    print("Waiting for test cases to be generated...")
    time.sleep(1)

specification_ids = [_spec.id]

# Endpoint connection mode requires a deployed endpoint; skip gracefully in CI
try:
    # @start run_endpoint_connection
    # Run evaluation using your deployed endpoint connection
    result = galtea.evaluations.run(version_id=version_id)
    print(f"Job {result['jobId']} queued {result['testCaseCount']} test cases")
    for spec in result["specifications"]:
        print(f"  Spec {spec['specificationId']}: {spec['testCount']} tests, {spec['metricCount']} metrics")
    # @end run_endpoint_connection
except Exception:
    pass

try:
    # @start run_with_specification_ids
    # Evaluate only specific specifications
    result = galtea.evaluations.run(
        version_id=version_id,
        specification_ids=specification_ids,
    )
    # @end run_with_specification_ids
except Exception:
    pass

# @start run_with_agent
# Run evaluation with a local agent (SDK-side loop)
def my_agent(user_message: str) -> str:
    # Replace with your actual agent logic
    return "Agent response"

result = galtea.evaluations.run(
    version_id=version_id,
    agent=my_agent,
    specification_ids=specification_ids[:1],
)
print(f"Processed {result['testCaseCount']} test cases")
print(f"Created {len(result['evaluations'])} evaluations")
# @end run_with_agent

# Cleanup
galtea.products.delete(product_id=product_id)
