import os
from datetime import datetime

from requests.exceptions import HTTPError

from _test_helpers import create_test_product
from galtea import Galtea

# Fixture setup for the snippet test. Only the `github_actions_workflow` section below is
# embedded in the docs, and it rebinds `galtea`, so the fixture keeps its own client under a
# separate name — otherwise the cleanup at the bottom would silently depend on the snippet.
galtea_fixture = Galtea(api_key="YOUR_API_KEY")

run_identifier: str = datetime.now().strftime("%Y%m%d%H%M%S%f")

# Register product via helper (SDK doesn't expose products.create)
PRODUCT_ID: str = create_test_product(
    galtea_fixture,
    name=f"docs-github-actions-product-{run_identifier}",
    description="Product for GitHub Actions integration documentation",
)

# Create a dataset with test cases
dataset = galtea_fixture.datasets.create(
    product_id=PRODUCT_ID,
    name=f"github-actions-test-{run_identifier}",
    type="ACCURACY",
    dataset_file_path="path/to/accuracy_dataset.csv",
)

# `evaluations.run()` discovers work through specifications, so the specification needs both
# its metrics and its datasets linked, or the run finds nothing to evaluate. A real product
# does this once (from the dashboard or a setup script), never from the CI script.
factual_accuracy = galtea_fixture.metrics.get_by_name(name="Factual Accuracy")
if factual_accuracy is None:
    raise ValueError("Could not find 'Factual Accuracy' metric")

specification = galtea_fixture.specifications.create(
    product_id=PRODUCT_ID,
    name="Answers must be factually correct",
    description="The assistant answers only from its knowledge base, and never invents details.",
    type="POLICY",
    dataset_type="ACCURACY",
    test_variant="rag",
    metric_ids=[factual_accuracy.id],
)
if specification is None:
    raise ValueError("Failed to create specification")
galtea_fixture.specifications.link_datasets(specification_id=specification.id, dataset_ids=[dataset.id])

# The snippet below reads these from the environment, as a real workflow does. GitHub Actions
# already sets the GITHUB_* ones; the product ID is this fixture's, restored after the snippet
# so no later snippet in the same validator process is pointed at the product deleted below.
previous_product_id = os.environ.get("GALTEA_PRODUCT_ID")
os.environ["GALTEA_PRODUCT_ID"] = PRODUCT_ID
os.environ.setdefault("GITHUB_SHA", run_identifier)
os.environ.setdefault("GITHUB_RUN_ID", run_identifier)
os.environ.setdefault("GITHUB_RUN_ATTEMPT", "1")

# @start github_actions_workflow
import os

from galtea import Galtea

# GALTEA_API_KEY and GALTEA_PRODUCT_ID come from the workflow's `env:` block above.
# The GITHUB_* ones are provided by GitHub Actions itself, so you never declare them.
galtea = Galtea(api_key=os.environ["GALTEA_API_KEY"])

PRODUCT_ID = os.environ["GALTEA_PRODUCT_ID"]
COMMIT_SHA = os.environ["GITHUB_SHA"]

# One version per workflow run, named after the commit so every result is traceable to the
# code that produced it. Version names are unique per product, and the same commit is built
# again on `pull_request` and on every job re-run, so the run id and attempt keep it unique.
version = galtea.versions.create(
    name=f"ci-{COMMIT_SHA[:7]}-{os.environ['GITHUB_RUN_ID']}.{os.environ['GITHUB_RUN_ATTEMPT']}",
    product_id=PRODUCT_ID,
)
if version is None:
    raise RuntimeError("Could not create the version — check GALTEA_API_KEY and GALTEA_PRODUCT_ID")


# Your product under test. Galtea calls it once per test case.
def my_agent(user_message: str) -> str:
    # In a real scenario, this would call your actual AI model or API
    return "This is a placeholder model answer."


# One call runs the whole evaluation: it finds the product's specifications, resolves their
# linked datasets and metrics, runs the agent on every test case, and submits the results.
result = galtea.evaluations.run(version_id=version.id, agent=my_agent)

print(f"Evaluated {result['testCaseCount']} test cases against version {version.name}")
# @end github_actions_workflow

# Guard the gate itself: `run()` returns testCaseCount 0 and raises nothing when the
# specification resolves no datasets, so without this the snippet would stay green while
# demonstrating a flow that evaluates nothing.
if result["testCaseCount"] == 0:
    raise ValueError("evaluations.run() resolved no test cases — specification linking is broken")

# Cleanup. Guarded because the product owns a specification, and the cascade soft-delete can
# 500 on the specifications unique constraint — a failure unrelated to what this file documents.
try:
    galtea_fixture.products.delete(product_id=PRODUCT_ID)
except HTTPError as e:
    if e.response.status_code != 500:
        raise
if previous_product_id is None:
    os.environ.pop("GALTEA_PRODUCT_ID", None)
else:
    os.environ["GALTEA_PRODUCT_ID"] = previous_product_id
