import os
from datetime import datetime

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

# The settings your agent runs with. The workflow sets them in its `env:` block, and the
# defaults apply when you run this script on your own machine.
AGENT_MODEL = os.environ.get("AGENT_MODEL", "gpt-4o-mini")
AGENT_TEMPERATURE = os.environ.get("AGENT_TEMPERATURE", "0.7")

# One version per agent state. The facts come from the same settings the agent uses, so they
# always describe what was tested. `auto_detect_commit_hash` adds the commit: GITHUB_SHA in CI,
# `git rev-parse HEAD` on your machine. A re-run of the same state gets the same version back.
version = galtea.versions.get_or_create(
    product_id=PRODUCT_ID,
    facts={"model": AGENT_MODEL, "temperature": AGENT_TEMPERATURE},
    auto_detect_commit_hash=True,
)


# Your product under test. Galtea calls it once per test case.
def my_agent(user_message: str) -> str:
    # In a real scenario, this would call your model with AGENT_MODEL and AGENT_TEMPERATURE
    return "This is a placeholder model answer."


# Open a run named after the workflow run, so every result of this CI job is grouped under one
# entry you can find again from the build number. The label must be unique per product, and
# "Re-run all jobs" keeps the run id and only bumps the attempt, so both go in the label.
# Leaving the block closes the run.
with galtea.runs.start(
    product_id=PRODUCT_ID,
    version_id=version.id,
    custom_id=f"{os.environ['GITHUB_RUN_ID']}-{os.environ['GITHUB_RUN_ATTEMPT']}",
):
    # One call runs the whole evaluation: it finds the product's specifications, resolves their
    # linked datasets and metrics, runs the agent on every test case, and submits the results.
    # It joins the open run, so you pass no run id here.
    result = galtea.evaluations.run(version_id=version.id, agent=my_agent)

print(f"Evaluated {result['testCaseCount']} test cases against version {version.name}")
print(f"Results are grouped under run {result['runId']}")
# @end github_actions_workflow

# Guard the gate itself: `run()` returns testCaseCount 0 and raises nothing when the
# specification resolves no datasets, so without this the snippet would stay green while
# demonstrating a flow that evaluates nothing.
if result["testCaseCount"] == 0:
    raise ValueError("evaluations.run() resolved no test cases — specification linking is broken")

# Cleanup
galtea_fixture.products.delete(product_id=PRODUCT_ID)
if previous_product_id is None:
    os.environ.pop("GALTEA_PRODUCT_ID", None)
else:
    os.environ["GALTEA_PRODUCT_ID"] = previous_product_id
